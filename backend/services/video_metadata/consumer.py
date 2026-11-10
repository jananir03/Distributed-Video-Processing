

import json
import logging
import os
import threading
import time
from typing import Any

import pika
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from shared.database import get_db_session_factory
from shared.settings import get_settings
from services.video_metadata.models import ConsumedEvent, VideoMetadata

settings = get_settings()
logger = logging.getLogger(__name__)

EXCHANGE_NAME = "video.events"
QUEUE_NAME = "video.metadata.uploaded.queue"
ROUTING_KEY = "video.uploaded"
DEAD_LETTER_EXCHANGE = "video.dlx"
DEAD_LETTER_QUEUE = "video.metadata.uploaded.dlq"
DEAD_LETTER_ROUTING_KEY = "video.uploaded.dead"


def _normalise_storage_path(value: str) -> str:
    """Resolve a stored filename safely inside the shared media directory."""
    normalised = value.replace("\\", "/").rstrip("/")
    filename = normalised.split("/")[-1]

    if not filename or filename in {".", ".."}:
        raise ValueError("Event contains an invalid storage_path")

    media_root = os.path.abspath(settings.media_root)
    result = os.path.abspath(os.path.join(media_root, filename))

    if os.path.commonpath([media_root, result]) != media_root:
        raise ValueError("Resolved media path escapes MEDIA_ROOT")

    return result


def _validate_event(
    payload: dict[str, Any],
) -> tuple[str, str, dict[str, Any]]:
    event_id = payload.get("event_id")
    event_type = payload.get("event_type")
    video = payload.get("video")

    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("Missing event_id")

    if event_type != "video.uploaded":
        raise ValueError(f"Unsupported event_type: {event_type!r}")

    if not isinstance(video, dict):
        raise ValueError("Missing or invalid video object")

    required = (
        "id",
        "original_filename",
        "storage_path",
        "content_type",
        "file_extension",
        "file_size_bytes",
        "sha256",
    )
    missing = [field for field in required if video.get(field) is None]
    if missing:
        raise ValueError(f"Event is missing video fields: {', '.join(missing)}")

    video_id = video["id"]
    if not isinstance(video_id, str) or not video_id.strip():
        raise ValueError("Invalid video.id")

    try:
        size = int(video["file_size_bytes"])
    except (TypeError, ValueError) as exc:
        raise ValueError("file_size_bytes must be an integer") from exc

    if size <= 0:
        raise ValueError("file_size_bytes must be positive")

    sha256 = str(video["sha256"]).lower()
    if len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256):
        raise ValueError("sha256 must be a valid 64-character hexadecimal digest")

    return event_id, video_id, video


def _persist_event(payload: dict[str, Any]) -> None:
    """Store metadata and the consumed-event record in one transaction."""
    event_id, video_id, video = _validate_event(payload)
    session_factory = get_db_session_factory()

    with session_factory() as session:
        already_consumed = session.scalar(
            select(ConsumedEvent.id).where(ConsumedEvent.event_id == event_id)
        )
        if already_consumed:
            logger.info("Ignoring already processed event_id=%s", event_id)
            return

        existing_metadata = session.scalar(
            select(VideoMetadata).where(VideoMetadata.video_id == video_id)
        )

        if existing_metadata is None:
            session.add(
                VideoMetadata(
                    video_id=video_id,
                    original_filename=os.path.basename(
                        str(video["original_filename"]).replace("\\", "/")
                    ),
                    storage_path=_normalise_storage_path(
                        str(video["storage_path"])
                    ),
                    content_type=str(video["content_type"]),
                    file_extension=str(video["file_extension"]).lower(),
                    file_size_bytes=int(video["file_size_bytes"]),
                    sha256=str(video["sha256"]).lower(),
                    source_event_id=event_id,
                )
            )
        else:
            logger.warning(
                "Metadata already exists for video_id=%s; recording event_id=%s",
                video_id,
                event_id,
            )

        session.add(
            ConsumedEvent(
                event_id=event_id,
                event_type="video.uploaded",
                video_id=video_id,
            )
        )

        try:
            session.commit()
        except IntegrityError:
            session.rollback()

            # Another delivery may have committed the same event concurrently.
            if session.scalar(
                select(ConsumedEvent.id).where(ConsumedEvent.event_id == event_id)
            ):
                return

            # Metadata may have been inserted by a different event for this video.
            if session.scalar(
                select(VideoMetadata.id).where(VideoMetadata.video_id == video_id)
            ):
                session.add(
                    ConsumedEvent(
                        event_id=event_id,
                        event_type="video.uploaded",
                        video_id=video_id,
                    )
                )
                session.commit()
                return

            raise

    logger.info(
        "Processed video.uploaded event: event_id=%s video_id=%s",
        event_id,
        video_id,
    )


class VideoMetadataConsumer:
    """Runs a reconnecting RabbitMQ consumer in a background thread."""

    def __init__(self) -> None:
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._running = threading.Event()

    @property
    def is_running(self) -> bool:
        return self._running.is_set()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run_forever,
            name="video-metadata-rabbitmq-consumer",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=10)

    def _run_forever(self) -> None:
        while not self._stop.is_set():
            connection = None

            try:
                parameters = pika.URLParameters(settings.rabbitmq_url)
                parameters.heartbeat = 30
                parameters.blocked_connection_timeout = 60

                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                channel.basic_qos(prefetch_count=10)

                channel.exchange_declare(
                    exchange=EXCHANGE_NAME,
                    exchange_type="topic",
                    durable=True,
                )
                channel.exchange_declare(
                    exchange=DEAD_LETTER_EXCHANGE,
                    exchange_type="direct",
                    durable=True,
                )
                channel.queue_declare(
                    queue=DEAD_LETTER_QUEUE,
                    durable=True,
                )
                channel.queue_bind(
                    queue=DEAD_LETTER_QUEUE,
                    exchange=DEAD_LETTER_EXCHANGE,
                    routing_key=DEAD_LETTER_ROUTING_KEY,
                )
                channel.queue_declare(
                    queue=QUEUE_NAME,
                    durable=True,
                    arguments={
                        "x-dead-letter-exchange": DEAD_LETTER_EXCHANGE,
                        "x-dead-letter-routing-key": DEAD_LETTER_ROUTING_KEY,
                    },
                )
                channel.queue_bind(
                    queue=QUEUE_NAME,
                    exchange=EXCHANGE_NAME,
                    routing_key=ROUTING_KEY,
                )

                def on_message(ch, method, properties, body) -> None:
                    try:
                        payload = json.loads(body.decode("utf-8"))
                        if not isinstance(payload, dict):
                            raise ValueError("Message body must be a JSON object")

                        _persist_event(payload)

                    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
                        logger.exception(
                            "Invalid upload event; sending it to the dead-letter queue"
                        )
                        ch.basic_nack(
                            delivery_tag=method.delivery_tag,
                            requeue=False,
                        )

                    except Exception:
                        logger.exception(
                            "Failed to process upload event; requeueing for retry"
                        )
                        ch.basic_nack(
                            delivery_tag=method.delivery_tag,
                            requeue=True,
                        )

                    else:
                        ch.basic_ack(delivery_tag=method.delivery_tag)

                channel.basic_consume(
                    queue=QUEUE_NAME,
                    on_message_callback=on_message,
                    auto_ack=False,
                )

                self._running.set()
                logger.info(
                    "RabbitMQ consumer connected; queue=%s routing_key=%s",
                    QUEUE_NAME,
                    ROUTING_KEY,
                )

                while not self._stop.is_set() and connection.is_open:
                    connection.process_data_events(time_limit=1)

            except Exception:
                if not self._stop.is_set():
                    logger.exception(
                        "RabbitMQ consumer unavailable; retrying in 5 seconds"
                    )
                    self._stop.wait(5)

            finally:
                self._running.clear()
                if connection is not None:
                    try:
                        if connection.is_open:
                            connection.close()
                    except Exception:
                        logger.exception("Error closing RabbitMQ connection")


consumer = VideoMetadataConsumer()
