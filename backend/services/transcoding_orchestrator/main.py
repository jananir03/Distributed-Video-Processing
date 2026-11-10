import logging, threading
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db, wait_for_database
from .models import ConsumedEvent, OutboxEvent, TranscodingJob
from .rabbitmq import Consumer
from .schemas import JobListResponse, JobResponse
from .service import process_event, publish_outbox_once
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger(__name__)
consumer = None
publisher_stop = threading.Event()
publisher_thread = None

def publisher_loop():
    while not publisher_stop.is_set():
        try: publish_outbox_once()
        except Exception: log.exception("Outbox publisher pass failed")
        publisher_stop.wait(max(.5, settings.outbox_poll_seconds))

@asynccontextmanager
async def lifespan(app: FastAPI):
    global consumer, publisher_thread
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    consumer = Consumer(process_event)
    consumer.start()
    publisher_stop.clear()
    publisher_thread = threading.Thread(target=publisher_loop, daemon=True, name="outbox-publisher")
    publisher_thread.start()
    try: yield
    finally:
        if consumer: consumer.stop()
        publisher_stop.set()
        engine.dispose()

app = FastAPI(title="Video Transcoding Orchestrator", version="1.0.0", lifespan=lifespan,
    description="Consumes upload events, creates idempotent profile jobs, and publishes requests via a transactional outbox.")

@app.get("/health/live", tags=["health"])
def live():
    return {"status":"ok","service":settings.service_name}

@app.get("/health/ready", tags=["health"])
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    consumer_status = "connected" if consumer and consumer.connected.is_set() else "disconnected"
    result = {"status":"ok" if db_status == "connected" and consumer_status == "connected" else "degraded",
        "service":settings.service_name,"database":db_status,"consumer":consumer_status}
    if result["status"] != "ok": raise HTTPException(503, detail=result)
    return result

@app.get("/jobs", response_model=JobListResponse, tags=["jobs"])
def jobs(video_id: str | None = None, job_status: str | None = Query(None, alias="status",
        pattern="^(queued|processing|completed|failed|cancelled)$"),
        profile: str | None = None, limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    q, cq = select(TranscodingJob), select(func.count()).select_from(TranscodingJob)
    if video_id: q=q.where(TranscodingJob.video_id==video_id); cq=cq.where(TranscodingJob.video_id==video_id)
    if job_status: q=q.where(TranscodingJob.status==job_status); cq=cq.where(TranscodingJob.status==job_status)
    if profile: q=q.where(TranscodingJob.profile==profile.lower()); cq=cq.where(TranscodingJob.profile==profile.lower())
    return JobListResponse(items=list(db.scalars(q.order_by(TranscodingJob.created_at.desc()).limit(limit).offset(offset))),
        limit=limit, offset=offset, total=db.scalar(cq) or 0)

@app.get("/jobs/{job_id}", response_model=JobResponse, tags=["jobs"])
def job(job_id: str, db: Session = Depends(get_db)):
    found=db.get(TranscodingJob, job_id)
    if not found: raise HTTPException(404, "Transcoding job not found")
    return found

@app.get("/internal/consumer", tags=["internal"])
def consumer_status():
    return {"connected":bool(consumer and consumer.connected.is_set()),"queue":settings.input_queue,
        "exchange":settings.input_exchange,"routing_key":settings.input_routing_key,
        "output_exchange":settings.output_exchange,"output_routing_key":settings.output_routing_key}

@app.get("/internal/events/{event_id}", tags=["internal"])
def consumed_event(event_id: str, db: Session = Depends(get_db)):
    found=db.get(ConsumedEvent,event_id)
    if not found: raise HTTPException(404, "Event has not been consumed")
    return {"event_id":found.event_id,"event_type":found.event_type,"processed_at":found.processed_at}

@app.get("/internal/outbox", tags=["internal"])
def outbox(db: Session = Depends(get_db)):
    total=db.scalar(select(func.count()).select_from(OutboxEvent)) or 0
    pending=db.scalar(select(func.count()).select_from(OutboxEvent).where(OutboxEvent.published_at.is_(None))) or 0
    return {"total":total,"pending":pending,"published":total-pending}
