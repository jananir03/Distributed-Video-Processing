
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import func, select

from shared.database import (
    Base,
    check_database,
    get_db_session_factory,
    get_engine,
)
from shared.logging_config import configure_logging
from services.video_metadata.consumer import consumer
from services.video_metadata.models import ConsumedEvent, VideoMetadata
from services.video_metadata.schemas import (
    HealthResponse,
    MetadataListResponse,
    MetadataResponse,
)

SERVICE_NAME = "video-metadata"
configure_logging(SERVICE_NAME)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize this service's tables and start its RabbitMQ consumer."""
    Base.metadata.create_all(bind=get_engine())
    consumer.start()

    try:
        yield
    finally:
        consumer.stop()


app = FastAPI(
    title="Video Metadata Service",
    description=(
        "Stores metadata for uploaded videos and consumes video.uploaded "
        "events from RabbitMQ."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health/live")
def liveness() -> dict[str, str]:
    return {"status": "alive", "service": SERVICE_NAME}


@app.get("/health/ready", response_model=HealthResponse)
def readiness() -> HealthResponse:
    try:
        check_database()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Metadata database is unavailable",
        ) from exc

    consumer_status = "connected" if consumer.is_running else "disconnected"

    return HealthResponse(
        status="ready" if consumer.is_running else "degraded",
        service=SERVICE_NAME,
        database="connected",
        rabbitmq_consumer=consumer_status,
        details={
            "queue": "video.metadata.uploaded.queue",
            "routing_key": "video.uploaded",
            "database_schema": "configured by DATABASE_URL",
        },
    )


@app.get("/metadata/videos", response_model=MetadataListResponse)
def list_metadata(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> MetadataListResponse:
    session_factory = get_db_session_factory()

    with session_factory() as session:
        total = session.scalar(
            select(func.count()).select_from(VideoMetadata)
        ) or 0

        rows = session.scalars(
            select(VideoMetadata)
            .order_by(VideoMetadata.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()

        return MetadataListResponse(
            items=list(rows),
            total=total,
            limit=limit,
            offset=offset,
        )


@app.get(
    "/metadata/videos/{video_id}",
    response_model=MetadataResponse,
)
def get_metadata(video_id: str) -> VideoMetadata:
    session_factory = get_db_session_factory()

    with session_factory() as session:
        record = session.scalar(
            select(VideoMetadata).where(VideoMetadata.video_id == video_id)
        )

        if record is None:
            raise HTTPException(
                status_code=404,
                detail=f"Metadata not found for video {video_id}",
            )

        return record


@app.get("/internal/consumer")
def consumer_status() -> dict[str, object]:
    """Expose the consumer's current connection status."""
    return {
        "service": SERVICE_NAME,
        "running": consumer.is_running,
        "queue": "video.metadata.uploaded.queue",
        "routing_key": "video.uploaded",
    }


@app.get("/internal/events/{event_id}")
def event_status(event_id: str) -> dict[str, object]:
    """Check whether an event has been committed to the idempotency ledger."""
    session_factory = get_db_session_factory()

    with session_factory() as session:
        event = session.scalar(
            select(ConsumedEvent).where(ConsumedEvent.event_id == event_id)
        )

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Event has not been processed",
            )

        return {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "video_id": event.video_id,
            "processed_at": event.processed_at,
        }
