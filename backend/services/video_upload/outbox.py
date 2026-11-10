"""Reliable outbox publishing to RabbitMQ with persistent messages."""
import json
import logging
import time
from datetime import datetime, timezone

import pika
from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.database import get_db_session_factory
from shared.settings import get_settings
from .models import OutboxEvent

logger = logging.getLogger(__name__)
EXCHANGE_NAME = "video.events"
ROUTING_KEY = "video.uploaded"


def publish_one_event(payload_json: str, event_id: str) -> None:
    """Publish one durable message and wait for broker confirmation."""
    settings = get_settings()
    if not settings.rabbitmq_url:
        raise RuntimeError("RABBITMQ_URL is not configured.")
    parameters = pika.URLParameters(settings.rabbitmq_url)
    parameters.socket_timeout = 5
    parameters.blocked_connection_timeout = 5
    connection = pika.BlockingConnection(parameters)
    try:
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
        channel.confirm_delivery()
        accepted = channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            body=payload_json.encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
                message_id=event_id,
                timestamp=int(time.time()),
                headers={"event_id": event_id},
            ),
            mandatory=True,
        )
        if accepted is False:
            raise RuntimeError("RabbitMQ did not confirm the message.")
    finally:
        connection.close()


def publish_pending_once(batch_size: int = 20) -> int:
    """Publish pending events and mark them after broker confirmation.

    A crash between publish and DB update may cause a duplicate; consumers must
    deduplicate by event_id. This is the normal at-least-once outbox guarantee.
    """
    session_factory = get_db_session_factory()
    published_count = 0
    with session_factory() as db:
        events = db.scalars(
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at)
            .limit(batch_size)
        ).all()

        for event in events:
            try:
                publish_one_event(event.payload_json, event.id)
                event.published_at = datetime.now(timezone.utc)
                event.attempts += 1
                event.last_error = None
                db.commit()
                published_count += 1
            except Exception as exc:
                db.rollback()
                logger.warning("Outbox event %s publish failed: %s", event.id, exc)
                # Record the failure in a fresh transaction; keep the event pending.
                failed = db.get(OutboxEvent, event.id)
                if failed is not None:
                    failed.attempts += 1
                    failed.last_error = str(exc)[:4000]
                    db.commit()
                break
    return published_count


def outbox_publisher_loop(stop_event) -> None:
    """Blocking loop intended to run in a dedicated daemon thread."""
    while not stop_event.is_set():
        try:
            count = publish_pending_once()
            if count:
                logger.info("Published %s upload outbox event(s)", count)
        except Exception:
            logger.exception("Outbox publisher iteration failed")
        stop_event.wait(2.0)
