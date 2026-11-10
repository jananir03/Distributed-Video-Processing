import logging
import time
from datetime import datetime, timedelta
from threading import Event
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .config import Settings
from .database import SessionLocal, WorkerSessionLocal
from .generator import generate_thumbnail
from .models import ThumbnailRecord

logger = logging.getLogger(__name__)

class ThumbnailProcessor:
    """Poll completed transcoding results and idempotently generate thumbnails."""
    def __init__(self, settings: Settings):
        self.settings = settings
        self.stop_event = Event()
        self.thread = None
        self.last_error = None
        self.running = False

    def start(self):
        import threading
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, name="thumbnail-poller", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=10)

    def _run(self):
        self.running = True
        try:
            while not self.stop_event.is_set():
                try:
                    self.process_batch()
                    self.last_error = None
                except Exception as exc:
                    self.last_error = str(exc)[:1000]
                    logger.exception("Thumbnail polling cycle failed")
                self.stop_event.wait(self.settings.poll_interval_seconds)
        finally:
            self.running = False

    def process_batch(self) -> int:
        # Page through old completed results as well as new ones. A fixed first-page
        # query would repeatedly see the same already-processed jobs and starve newer rows.
        processed = 0
        offset = 0
        page_size = self.settings.batch_size
        while not self.stop_event.is_set():
            with WorkerSessionLocal() as source_db:
                rows = source_db.execute(text("""
                    SELECT job_id, video_id, profile, output_path
                    FROM transcoding_worker_job_results
                    WHERE status = 'completed' AND output_path IS NOT NULL AND output_path <> ''
                    ORDER BY COALESCE(finished_at, created_at) ASC, job_id ASC
                    LIMIT :batch_size OFFSET :offset
                """), {"batch_size": page_size, "offset": offset}).mappings().all()
            if not rows:
                break
            for row in rows:
                if self.stop_event.is_set():
                    break
                if self._process_one(dict(row)):
                    processed += 1
                    if processed >= self.settings.batch_size:
                        return processed
            offset += len(rows)
            if len(rows) < page_size:
                break
        return processed

    def _process_one(self, item: dict) -> bool:
        job_id = str(item["job_id"])
        video_id = str(item["video_id"])
        profile = str(item["profile"])
        source_path = str(item["output_path"])
        now = datetime.utcnow()
        with SessionLocal() as db:
            record = db.query(ThumbnailRecord).filter_by(job_id=job_id).one_or_none()
            if record and record.status == "completed":
                # Repair a missing artifact without regenerating healthy thumbnails.
                try:
                    existing = generate_existing_path(record.thumbnail_path, self.settings.media_root)
                    if existing and existing.is_file() and existing.stat().st_size > 0:
                        return False
                except Exception:
                    pass
            if record and record.status == "processing" and record.updated_at and record.updated_at > now - timedelta(minutes=10):
                return False
            if record and record.attempts >= self.settings.max_attempts and record.status == "failed":
                return False
            if record and record.status == "failed" and record.next_retry_at and record.next_retry_at > now:
                return False
            if record is None:
                record = ThumbnailRecord(job_id=job_id, video_id=video_id, profile=profile,
                    source_path=source_path, status="processing", attempts=1)
                db.add(record)
            else:
                record.video_id, record.profile, record.source_path = video_id, profile, source_path
                record.status, record.attempts, record.error_message = "processing", record.attempts + 1, None
                record.next_retry_at = None
            db.commit()
            record_id = record.id
        try:
            output = generate_thumbnail(source_path, video_id, profile, self.settings)
            with SessionLocal() as db:
                record = db.get(ThumbnailRecord, record_id)
                if record:
                    record.status, record.thumbnail_path, record.error_message = "completed", output, None
                    record.next_retry_at = None
                    db.commit()
            logger.info("Thumbnail generated video_id=%s profile=%s path=%s", video_id, profile, output)
            return True
        except Exception as exc:
            message = str(exc)[:2000]
            with SessionLocal() as db:
                record = db.get(ThumbnailRecord, record_id)
                if record:
                    record.status, record.error_message = "failed", message
                    record.next_retry_at = datetime.utcnow() + timedelta(seconds=min(30 * (2 ** max(record.attempts - 1, 0)), 900))
                    db.commit()
            logger.warning("Thumbnail generation failed job_id=%s: %s", job_id, message)
            return False

def generate_existing_path(value: str | None, media_root: str):
    if not value:
        return None
    from pathlib import Path
    root = Path(media_root).resolve()
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if path != root and root not in path.parents:
        return None
    return path
