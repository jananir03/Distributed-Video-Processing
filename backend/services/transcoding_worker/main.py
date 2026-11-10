import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .config import get_settings
from .database import WorkerSessionLocal, OrchestratorSessionLocal, worker_engine
from .models import Base, WorkerJobResult
from .worker import RabbitWorker

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO),
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
worker = RabbitWorker(settings)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=worker_engine)
    worker.start()
    yield
    worker.stop()

app = FastAPI(title="Video Transcoding Worker", version="1.0.0",
              description="Consumes transcoding requests and generates FFmpeg outputs.", lifespan=lifespan)

@app.get("/health/live")
def health_live():
    return {"status": "ok", "service": settings.service_name}

@app.get("/health/ready")
def health_ready():
    try:
        with WorkerSessionLocal() as db: db.execute(text("SELECT 1"))
        with OrchestratorSessionLocal() as db: db.execute(text("SELECT 1"))
        if not worker.connected:
            return {"status": "not_ready", "database": "connected", "consumer": "disconnected",
                    "last_error": worker.last_error}
        return {"status": "ok", "database": "connected", "consumer": "connected"}
    except SQLAlchemyError as exc:
        return {"status": "not_ready", "database": "disconnected", "consumer": worker.connected,
                "error": str(exc)[:500]}

@app.get("/internal/worker")
def worker_status():
    return {"connected": worker.connected, "queue": settings.input_queue, "exchange": settings.input_exchange,
            "routing_key": settings.input_routing_key, "last_error": worker.last_error}

@app.get("/internal/results")
def results(limit: int = 50, offset: int = 0):
    limit, offset = max(1, min(limit, 200)), max(0, offset)
    with WorkerSessionLocal() as db:
        rows = db.query(WorkerJobResult).order_by(WorkerJobResult.created_at.desc()).offset(offset).limit(limit).all()
        total = db.query(WorkerJobResult).count()
        return {"items": [{"job_id": r.job_id, "video_id": r.video_id, "profile": r.profile,
                           "status": r.status, "output_path": r.output_path, "error_message": r.error_message,
                           "started_at": r.started_at, "finished_at": r.finished_at} for r in rows],
                "total": total, "limit": limit, "offset": offset}
