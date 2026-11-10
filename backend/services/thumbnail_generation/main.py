import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .config import get_settings
from .database import Base, SessionLocal, WorkerSessionLocal, engine, worker_engine
from .models import ThumbnailRecord
from .processor import ThumbnailProcessor, generate_existing_path

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO),
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
processor = ThumbnailProcessor(settings)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Fail fast on DB configuration errors; the readiness endpoint also checks both DBs.
    with SessionLocal() as db: db.execute(text("SELECT 1"))
    with WorkerSessionLocal() as db: db.execute(text("SELECT 1"))
    processor.start()
    try:
        yield
    finally:
        processor.stop()

app = FastAPI(title="Video Thumbnail Service", version="1.0.0",
              description="Generates and serves JPEG thumbnails for successfully transcoded video profiles.", lifespan=lifespan)

@app.get("/health/live", tags=["health"])
def health_live():
    return {"status": "ok", "service": settings.service_name}

@app.get("/health/ready", tags=["health"])
def health_ready():
    try:
        with SessionLocal() as db: db.execute(text("SELECT 1"))
        with WorkerSessionLocal() as db: db.execute(text("SELECT 1"))
        return {"status": "ready", "service": settings.service_name,
                "thumbnail_database": "connected", "worker_database": "connected",
                "processor_running": processor.running, "last_error": processor.last_error}
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="A required database is unavailable.") from exc

@app.get("/internal/processor", tags=["internal"])
def processor_status():
    return {"running": processor.running, "poll_interval_seconds": settings.poll_interval_seconds,
            "batch_size": settings.batch_size, "last_error": processor.last_error}

@app.post("/internal/process-now", tags=["internal"])
def process_now():
    """Trigger a bounded scan for manual verification; processing remains idempotent."""
    try:
        count = processor.process_batch()
        return {"status": "ok", "new_thumbnails_processed": count}
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Unable to query thumbnail or worker database.") from exc

@app.get("/thumbnails", tags=["thumbnails"])
def list_thumbnails(limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0),
                    status: str | None = Query(default=None, pattern="^(pending|processing|completed|failed)$")):
    with SessionLocal() as db:
        query = db.query(ThumbnailRecord)
        if status:
            query = query.filter(ThumbnailRecord.status == status)
        total = query.count()
        rows = query.order_by(ThumbnailRecord.created_at.desc()).offset(offset).limit(limit).all()
        return {"items": [{"job_id": r.job_id, "video_id": r.video_id, "profile": r.profile,
                            "status": r.status, "thumbnail_path": r.thumbnail_path,
                            "error_message": r.error_message, "attempts": r.attempts,
                            "created_at": r.created_at, "updated_at": r.updated_at}
                           for r in rows], "total": total, "limit": limit, "offset": offset}

@app.get("/thumbnails/{video_id}", tags=["thumbnails"])
def thumbnails_for_video(video_id: str):
    with SessionLocal() as db:
        rows = db.query(ThumbnailRecord).filter_by(video_id=video_id).order_by(ThumbnailRecord.profile.asc()).all()
        if not rows:
            raise HTTPException(status_code=404, detail="No thumbnail records found for this video yet.")
        return {"video_id": video_id, "items": [{"job_id": r.job_id, "profile": r.profile,
                "status": r.status, "thumbnail_path": r.thumbnail_path,
                "url": f"/thumbnails/{video_id}/{r.profile}" if r.status == "completed" else None,
                "error_message": r.error_message} for r in rows]}

@app.get("/thumbnails/{video_id}/{profile}", tags=["thumbnails"], response_class=FileResponse)
def get_thumbnail(video_id: str, profile: str):
    # Profile and video ID are restricted to safe path-segment characters.
    if not video_id or any(not (c.isalnum() or c in "-_") for c in video_id):
        raise HTTPException(status_code=400, detail="Invalid video_id.")
    if not profile or any(not (c.isalnum() or c in "-_") for c in profile):
        raise HTTPException(status_code=400, detail="Invalid profile.")
    with SessionLocal() as db:
        record = db.query(ThumbnailRecord).filter_by(video_id=video_id, profile=profile, status="completed").order_by(ThumbnailRecord.updated_at.desc()).first()
        if not record or not record.thumbnail_path:
            raise HTTPException(status_code=404, detail="Thumbnail not found or not ready.")
        path = generate_existing_path(record.thumbnail_path, settings.media_root)
        if not path or not path.is_file():
            raise HTTPException(status_code=404, detail="Thumbnail file is missing.")
        return FileResponse(path, media_type="image/jpeg", filename=f"{video_id}-{profile}.jpg")
