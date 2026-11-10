import logging
from pathlib import Path
from typing import Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .config import get_settings
from .database import engine

logger = logging.getLogger(__name__)
settings = get_settings()

class AssetNotFound(Exception):
    pass

class AssetUnavailable(Exception):
    pass

def media_root() -> Path:
    return settings.media_root.resolve()

def safe_file(value: str | None) -> Path | None:
    if not value:
        return None
    root = media_root()
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if resolved == root or root not in resolved.parents or not resolved.is_file():
        return None
    return resolved

def list_outputs(video_id: str, limit: int, offset: int) -> dict[str, Any]:
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT job_id, video_id, profile, status, output_path, error_message,
                       started_at, finished_at, created_at, updated_at
                FROM transcoding_worker_job_results
                WHERE video_id = :video_id
                ORDER BY profile
                LIMIT :limit OFFSET :offset
            """), {"video_id": video_id, "limit": limit, "offset": offset}).mappings().all()
            total = conn.execute(
                text("SELECT COUNT(*) FROM transcoding_worker_job_results WHERE video_id=:video_id"),
                {"video_id": video_id}
            ).scalar_one()
    except SQLAlchemyError as exc:
        logger.exception("Unable to query transcoding results")
        raise AssetUnavailable("Media catalog is temporarily unavailable") from exc
    items = []
    for row in rows:
        item = dict(row)
        path = safe_file(item.get("output_path")) if item.get("status") == "completed" else None
        item["available"] = path is not None
        item["size_bytes"] = path.stat().st_size if path else None
        item["stream_url"] = f"/api/v1/videos/{video_id}/stream?profile={item['profile']}" if path else None
        item["download_url"] = f"/api/v1/videos/{video_id}/download?profile={item['profile']}" if path else None
        item["output_path"] = str(path.relative_to(media_root())).replace("\\", "/") if path else None
        items.append(item)
    return {"video_id": video_id, "items": items, "total": int(total), "limit": limit, "offset": offset}

def resolve_output(video_id: str, profile: str) -> Path:
    try:
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT status, output_path FROM transcoding_worker_job_results
                WHERE video_id=:video_id AND profile=:profile
                ORDER BY updated_at DESC LIMIT 1
            """), {"video_id": video_id, "profile": profile}).mappings().first()
    except SQLAlchemyError as exc:
        logger.exception("Unable to query media output")
        raise AssetUnavailable("Media catalog is temporarily unavailable") from exc
    if not row or row["status"] != "completed":
        raise AssetNotFound("No completed output exists for this video and profile")
    path = safe_file(row["output_path"])
    if path is None or path.stat().st_size == 0:
        raise AssetNotFound("The media output is not available on disk")
    return path

def list_thumbnails(video_id: str) -> dict[str, Any]:
    root = media_root()
    directory = (root / "thumbnails" / video_id).resolve()
    if root not in directory.parents or not directory.is_dir():
        return {"video_id": video_id, "items": [], "total": 0}
    items = []
    for candidate in sorted(directory.glob("*.jpg")):
        path = safe_file(str(candidate))
        if path:
            items.append({"profile": path.stem, "content_type": "image/jpeg",
                          "size_bytes": path.stat().st_size,
                          "url": f"/api/v1/videos/{video_id}/thumbnails/{path.stem}"})
    return {"video_id": video_id, "items": items, "total": len(items)}

def resolve_thumbnail(video_id: str, profile: str) -> Path:
    if not profile or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in profile):
        raise AssetNotFound("Invalid thumbnail profile")
    path = safe_file(str(media_root() / "thumbnails" / video_id / f"{profile}.jpg"))
    if path is None or path.suffix.lower() != ".jpg" or path.stat().st_size == 0:
        raise AssetNotFound("Thumbnail not found")
    return path
