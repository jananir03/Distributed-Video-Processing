"""FastAPI application for the video upload service."""
import json
import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from shared.database import Base, check_database, get_db, get_engine
from shared.logging_config import configure_logging
from shared.settings import get_settings
from . import models  # Ensure service-owned models are registered with Base.
from .models import OutboxEvent, Video
from .outbox import outbox_publisher_loop
from .schemas import (
    HealthResponse,
    VideoDetailResponse,
    VideoListItem,
    VideoListResponse,
    VideoUploadResponse,
)
from .storage import save_upload

settings = get_settings()
configure_logging(settings.service_name or "video-upload")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize service-owned tables and start the outbox publisher."""
    stop_event = threading.Event()
    publisher_thread = None
    try:
        Path(settings.media_root).expanduser().mkdir(parents=True, exist_ok=True)
        # For this assignment phase, create_all bootstraps the service-owned schema.
        # For a production deployment, replace this with an Alembic migration step.
        Base.metadata.create_all(bind=get_engine())
        publisher_thread = threading.Thread(
            target=outbox_publisher_loop,
            args=(stop_event,),
            name="upload-outbox-publisher",
            daemon=True,
        )
        publisher_thread.start()
        logger.info("Video upload service started")
        yield
    finally:
        stop_event.set()
        if publisher_thread is not None:
            publisher_thread.join(timeout=5)
        logger.info("Video upload service stopped")


app = FastAPI(
    title="Video Upload Service",
    description="Validates and stores source videos and emits video.uploaded events.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health/live", tags=["health"])
def liveness() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/health/ready", response_model=HealthResponse, tags=["health"])
def readiness() -> HealthResponse:
    try:
        check_database()
    except Exception as exc:
        logger.exception("Readiness check failed")
        raise HTTPException(status_code=503, detail="Database is not ready.") from exc
    return HealthResponse(status="ready", service=settings.service_name, database="connected")


@app.post(
    "/videos/upload",
    response_model=VideoUploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["videos"],
)
async def upload_video(
    file: UploadFile = File(..., description="A supported source video file"),
    db: Session = Depends(get_db),
) -> VideoUploadResponse:
    """Save an upload and atomically create its video row and outbox event."""
    saved = await save_upload(file)

    # Avoid storing duplicate content twice. The DB constraint is a final guard
    # against concurrent uploads with the same SHA-256 digest.
    existing = db.scalar(select(Video).where(Video.sha256 == saved["sha256"]))
    if existing is not None:
        Path(saved["storage_path"]).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "An identical video has already been uploaded.", "video_id": existing.id},
        )

    video_id = str(uuid4())
    video = Video(
        id=video_id,
        original_filename=saved["original_filename"],
        stored_filename=saved["stored_filename"],
        storage_path=saved["storage_path"],
        content_type=saved["content_type"],
        file_extension=saved["file_extension"],
        file_size_bytes=saved["file_size_bytes"],
        sha256=saved["sha256"],
        status="uploaded",
    )
    event_id = str(uuid4())
    event_payload = {
        "event_id": event_id,
        "event_type": "video.uploaded",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "video": {
            "id": video_id,
            "original_filename": video.original_filename,
            "storage_path": video.storage_path,
            "content_type": video.content_type,
            "file_extension": video.file_extension,
            "file_size_bytes": video.file_size_bytes,
            "sha256": video.sha256,
        },
    }
    outbox = OutboxEvent(
        id=event_id,
        aggregate_id=video_id,
        event_type="video.uploaded",
        payload_json=json.dumps(event_payload, separators=(",", ":")),
    )

    try:
        db.add(video)
        db.add(outbox)
        db.commit()
        db.refresh(video)
    except IntegrityError as exc:
        db.rollback()
        Path(saved["storage_path"]).unlink(missing_ok=True)
        duplicate = db.scalar(select(Video).where(Video.sha256 == saved["sha256"]))
        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "An identical video has already been uploaded.", "video_id": duplicate.id},
            ) from exc
        logger.exception("Database integrity error while saving upload")
        raise HTTPException(status_code=500, detail="Could not save video metadata.") from exc
    except SQLAlchemyError as exc:
        db.rollback()
        Path(saved["storage_path"]).unlink(missing_ok=True)
        logger.exception("Database error while saving upload")
        raise HTTPException(status_code=503, detail="Video metadata storage is temporarily unavailable.") from exc
    except Exception:
        db.rollback()
        Path(saved["storage_path"]).unlink(missing_ok=True)
        raise

    logger.info("Uploaded video id=%s size=%s sha256=%s", video.id, video.file_size_bytes, video.sha256)
    return VideoUploadResponse(
        id=video.id,
        original_filename=video.original_filename,
        content_type=video.content_type,
        file_extension=video.file_extension,
        file_size_bytes=video.file_size_bytes,
        sha256=video.sha256,
        status=video.status,
        created_at=video.created_at,
    )


@app.get("/videos", response_model=VideoListResponse, tags=["videos"])
def list_videos(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> VideoListResponse:
    total = db.scalar(select(func.count()).select_from(Video)) or 0
    rows = db.scalars(
        select(Video).order_by(Video.created_at.desc()).offset(offset).limit(limit)
    ).all()
    return VideoListResponse(
        items=[VideoListItem.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@app.get("/videos/{video_id}", response_model=VideoDetailResponse, tags=["videos"])
def get_video(video_id: str, db: Session = Depends(get_db)) -> VideoDetailResponse:
    video = db.get(Video, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found.")
    return VideoDetailResponse(
        id=video.id,
        original_filename=video.original_filename,
        content_type=video.content_type,
        file_extension=video.file_extension,
        file_size_bytes=video.file_size_bytes,
        sha256=video.sha256,
        status=video.status,
        created_at=video.created_at,
        updated_at=video.updated_at,
    )
