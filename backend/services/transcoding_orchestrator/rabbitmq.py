import json, logging, threading, time
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError
from .config import settings
log = logging.getLogger(__name__)

def params():
    p = pika.URLParameters(settings.rabbitmq_url)
    p.heartbeat = 60
    p.blocked_connection_timeout = 30
    return p

class Publisher:
    def publish(self, exchange, routing_key, payload, message_id):
        conn = pika.BlockingConnection(params())
        try:
            ch = conn.channel()
            ch.confirm_delivery()
            ch.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
            ok = ch.basic_publish(exchange, routing_key,
                json.dumps(payload, separators=(",", ":")).encode(),
                pika.BasicProperties(content_type="application/json", delivery_mode=2,
                    message_id=message_id, type=payload.get("event_type", "transcoding.requested")),
                mandatory=True)
            if ok is False: raise RuntimeError("Publisher confirmation rejected")
        finally:
            if conn.is_open: conn.close()

class Consumer:
    def __init__(self, handler):
        self.handler, self.stop_event = handler, threading.Event()
        self.connected = threading.Event()
        self.thread = None
    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True, name="upload-consumer")
        self.thread.start()
    def stop(self): self.stop_event.set()
    def run(self):
        while not self.stop_event.is_set():
            conn = None
            try:
                conn = pika.BlockingConnection(params())
                ch = conn.channel()
                ch.exchange_declare(settings.input_exchange, "topic", durable=True)
                ch.exchange_declare(
                    exchange=settings.dead_letter_exchange,
                    exchange_type="direct",
                    durable=True,
                )
                ch.queue_declare(settings.dead_letter_queue, durable=True)
                ch.queue_bind(settings.dead_letter_queue, settings.dead_letter_exchange, settings.dead_letter_routing_key)
                ch.queue_declare(settings.input_queue, durable=True, arguments={
                    "x-dead-letter-exchange": settings.dead_letter_exchange,
                    "x-dead-letter-routing-key": settings.dead_letter_routing_key})
                ch.queue_bind(settings.input_queue, settings.input_exchange, settings.input_routing_key)
                ch.basic_qos(prefetch_count=settings.consumer_prefetch)
                self.connected.set()
                def callback(channel, method, props, body):
                    try:
                        payload = json.loads(body.decode("utf-8"))
                        if not isinstance(payload, dict): raise ValueError("Expected JSON object")
                        event_id = (props.message_id if props else None) or payload.get("event_id") or payload.get("id")
                        if not event_id: raise ValueError("Missing event ID/message_id")
                        self.handler(payload, str(event_id))
                    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                        log.exception("Invalid event; sending to dead-letter queue")
                        channel.basic_nack(method.delivery_tag, requeue=False)
                    except Exception:
                        log.exception("Processing failed; requeueing")
                        channel.basic_nack(method.delivery_tag, requeue=True)
                    else: channel.basic_ack(method.delivery_tag)
                ch.basic_consume(settings.input_queue, callback, auto_ack=False)
                while not self.stop_event.is_set() and conn.is_open:
                    conn.process_data_events(time_limit=1)
            except (AMQPConnectionError, AMQPChannelError, OSError):
                log.exception("RabbitMQ disconnected; retrying")
            except Exception:
                log.exception("Consumer failure; retrying")
            finally:
                self.connected.clear()
                if conn and conn.is_open:
                    try: conn.close()
                    except Exception: log.exception("Connection close failed")
            self.stop_event.wait(3)
