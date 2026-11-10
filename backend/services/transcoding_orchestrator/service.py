import logging, uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .config import settings
from .database import SessionLocal
from .models import ConsumedEvent, OutboxEvent, TranscodingJob
from .rabbitmq import Publisher
log = logging.getLogger(__name__)
publisher = Publisher()

def process_event(payload, event_id):
    # Upload service puts video details inside payload["video"].
    video_data = payload.get("video")
    if not isinstance(video_data, dict):
        video_data = payload

    video_id = str(
        video_data.get("id")
        or video_data.get("video_id")
        or payload.get("video_id")
        or ""
    )

    source_path = (
        video_data.get("storage_path")
        or video_data.get("file_path")
        or video_data.get("media_path")
        or video_data.get("stored_filename")
        or payload.get("storage_path")
        or payload.get("file_path")
        or payload.get("media_path")
        or payload.get("stored_filename")
    )
    
    if not video_id or not source_path:
        raise ValueError("Upload event must include video_id and a source path")
    profiles = list(dict.fromkeys(p.strip().lower() for p in settings.default_profiles.split(",") if p.strip()))
    allowed = {"144p","240p","360p","480p","720p","1080p","1440p","2160p"}
    profiles = [p for p in profiles if p in allowed]
    if not profiles: raise ValueError("No valid DEFAULT_PROFILES configured")
    with SessionLocal() as db:
        try:
            if db.get(ConsumedEvent, event_id):
                log.info("Duplicate event ignored: %s", event_id)
                return
            db.add(ConsumedEvent(event_id=event_id, event_type=str(payload.get("event_type") or "video.uploaded")))
            for profile in profiles:
                job = db.scalar(select(TranscodingJob).where(
                    TranscodingJob.video_id == video_id, TranscodingJob.profile == profile))
                if job: continue
                job = TranscodingJob(video_id=video_id, source_event_id=event_id,
                    source_path=str(source_path), profile=profile, status="queued",
                    priority=5, attempt_count=0, max_attempts=settings.job_max_attempts)
                db.add(job)
                db.flush()
                request = {"event_id": str(uuid.uuid4()), "event_type": "transcoding.requested",
                    "job_id": job.id, "video_id": video_id, "source_event_id": event_id,
                    "source_path": str(source_path), "profile": profile, "priority": 5,
                    "attempt": 0, "created_at": datetime.now(timezone.utc).isoformat()}
                db.add(OutboxEvent(dedupe_key=f"{job.id}:transcoding.requested",
                    exchange_name=settings.output_exchange, routing_key=settings.output_routing_key,
                    payload=request))
            db.commit()
            log.info("Created/verified jobs for video=%s from event=%s", video_id, event_id)
        except IntegrityError:
            db.rollback()
            if db.get(ConsumedEvent, event_id): return
            raise
        except Exception:
            db.rollback()
            raise

def publish_outbox_once(batch_size=50):
    with SessionLocal() as db:
        rows = list(db.scalars(select(OutboxEvent).where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at).limit(batch_size)))
        for row in rows:
            rid, exchange, routing, payload = row.id, row.exchange_name, row.routing_key, row.payload
            try:
                publisher.publish(exchange, routing, payload, rid)
                row.published_at = datetime.now(timezone.utc).replace(tzinfo=None)
                row.last_error = None
                db.commit()
            except Exception as exc:
                db.rollback()
                failed = db.get(OutboxEvent, rid)
                if failed:
                    failed.attempts += 1
                    failed.last_error = str(exc)[:4000]
                    db.commit()
                log.exception("Outbox publish failed for %s", rid)
                break
