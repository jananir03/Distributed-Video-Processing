import hashlib, json, logging, threading, time
from datetime import datetime
import pika
from pika.exceptions import AMQPConnectionError, ConnectionClosedByBroker, StreamLostError
from sqlalchemy import text
from .config import Settings
from .database import WorkerSessionLocal, OrchestratorSessionLocal
from .models import ProcessedMessage, WorkerJobResult
from .schemas import TranscodingRequest
from .transcoder import TranscodingError, transcode

logger = logging.getLogger(__name__)

class RabbitWorker:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.connected = False
        self.last_error = None
        self.stop_event = threading.Event()

    def start(self):
        threading.Thread(target=self._run, name="transcoding-consumer", daemon=True).start()

    def stop(self):
        self.stop_event.set()

    def _run(self):
        delay = 1
        while not self.stop_event.is_set():
            conn = None
            try:
                params = pika.URLParameters(self.settings.rabbitmq_url)
                params.heartbeat = 60
                params.blocked_connection_timeout = 30
                conn = pika.BlockingConnection(params)
                ch = conn.channel()
                ch.exchange_declare(exchange=self.settings.input_exchange, exchange_type="topic", durable=True)
                # Do not change existing queue arguments: Phase 4 already created this queue.
                ch.queue_declare(queue=self.settings.input_queue, durable=True)
                ch.queue_bind(queue=self.settings.input_queue, exchange=self.settings.input_exchange,
                              routing_key=self.settings.input_routing_key)
                ch.exchange_declare(exchange=self.settings.dead_letter_exchange, exchange_type="direct", durable=True)
                ch.queue_declare(queue=self.settings.dead_letter_queue, durable=True)
                ch.queue_bind(queue=self.settings.dead_letter_queue, exchange=self.settings.dead_letter_exchange,
                              routing_key=self.settings.dead_letter_routing_key)
                ch.basic_qos(prefetch_count=self.settings.prefetch_count)
                self.connected, self.last_error = True, None
                ch.basic_consume(queue=self.settings.input_queue, on_message_callback=self._callback, auto_ack=False)
                logger.info("Consuming queue %s", self.settings.input_queue)
                delay = 1
                while not self.stop_event.is_set() and conn.is_open:
                    conn.process_data_events(time_limit=1)
                if conn.is_open:
                    conn.close()
            except (AMQPConnectionError, ConnectionClosedByBroker, StreamLostError, OSError) as exc:
                self.connected, self.last_error = False, str(exc)
                logger.exception("RabbitMQ connection failed")
                if conn and conn.is_open:
                    try: conn.close()
                    except Exception: pass
                self.stop_event.wait(delay)
                delay = min(delay * 2, 30)
            except Exception as exc:
                self.connected, self.last_error = False, str(exc)
                logger.exception("Worker loop failed")
                if conn and conn.is_open:
                    try: conn.close()
                    except Exception: pass
                self.stop_event.wait(delay)
                delay = min(delay * 2, 30)

    def _callback(self, ch, method, properties, body):
        message_id = (getattr(properties, "message_id", None) or hashlib.sha256(body).hexdigest())
        try:
            request = TranscodingRequest.model_validate(json.loads(body.decode("utf-8")))
        except Exception as exc:
            logger.error("Rejecting invalid message %s: %s", message_id, exc)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        try:
            result = self._process(request, message_id)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("Job %s result=%s", request.job_id, result)
        except Exception as exc:
            self.last_error = str(exc)
            logger.exception("Job failed: %s", request.job_id)
            # Bounded application retries happen inside _process; do not endlessly requeue.
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _process(self, req: TranscodingRequest, message_id: str) -> str:
        with WorkerSessionLocal() as db:
            record = db.query(ProcessedMessage).filter_by(message_id=message_id).one_or_none()
            if record and record.outcome == "completed":
                return "already_completed"
            if not record:
                record = ProcessedMessage(message_id=message_id, job_id=req.job_id, outcome="processing")
                db.add(record)
            record.outcome, record.error_message = "processing", None
            db.commit()

        self._update_job(req.job_id, "processing", None, None)
        started = datetime.utcnow()
        attempts = min(req.max_attempts or self.settings.max_attempts, self.settings.max_attempts)
        error = None
        for attempt in range(1, attempts + 1):
            try:
                output = transcode(req.source_path, req.video_id, req.job_id, req.profile, self.settings)
                self._update_job(req.job_id, "completed", output, None)
                self._save_result(req, "completed", output, None, started, datetime.utcnow())
                self._mark_message(message_id, "completed", None)
                return "completed"
            except Exception as exc:
                error = str(exc)[:4000]
                logger.warning("Attempt %d/%d for %s failed: %s", attempt, attempts, req.job_id, error)
                if attempt < attempts:
                    time.sleep(self.settings.retry_delay_seconds * attempt)
        self._update_job(req.job_id, "failed", None, error)
        self._save_result(req, "failed", None, error, started, datetime.utcnow())
        self._mark_message(message_id, "failed", error)
        return "failed"

    def _update_job(self, job_id, status, output, error):
        with OrchestratorSessionLocal() as db:
            result = db.execute(text("""UPDATE transcoding_jobs
                SET status=:status, output_path=:output, error_message=:error,
                    updated_at=CURRENT_TIMESTAMP WHERE id=:job_id"""),
                {"status": status, "output": output, "error": error, "job_id": job_id})
            if result.rowcount == 0:
                db.rollback()
                raise TranscodingError(f"Orchestrator job not found: {job_id}")
            db.commit()

    def _save_result(self, req, status, output, error, started, finished):
        with WorkerSessionLocal() as db:
            row = db.query(WorkerJobResult).filter_by(job_id=req.job_id).one_or_none()
            if row is None:
                row = WorkerJobResult(job_id=req.job_id, video_id=req.video_id, profile=req.profile,
                                      status=status, started_at=started)
                db.add(row)
            row.status, row.output_path, row.error_message, row.finished_at = status, output, error, finished
            db.commit()

    def _mark_message(self, message_id, outcome, error):
        with WorkerSessionLocal() as db:
            row = db.query(ProcessedMessage).filter_by(message_id=message_id).one()
            row.outcome, row.error_message, row.processed_at = outcome, error, datetime.utcnow()
            db.commit()
