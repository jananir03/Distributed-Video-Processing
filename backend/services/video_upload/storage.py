"""Safe, streaming file storage and lightweight media-signature validation."""
import hashlib
import os
import re
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from shared.settings import get_settings

CHUNK_SIZE = 1024 * 1024
SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def safe_original_filename(filename: str | None) -> str:
    """Keep a display-only basename; never use the client filename as a path."""
    name = Path((filename or "video").replace("\\", "/")).name.strip()
    name = SAFE_NAME_RE.sub("_", name).strip("._")
    if not name:
        name = "video"
    return name[:255]


def has_supported_signature(extension: str, header: bytes) -> bool:
    """Reject obvious extension/content mismatches without trusting MIME headers."""
    ext = extension.lower()
    if ext in {".mp4", ".mov", ".m4v"}:
        return len(header) >= 8 and header[4:8] == b"ftyp"
    if ext == ".webm":
        return header.startswith(bytes.fromhex("1A45DFA3"))
    if ext == ".mkv":
        return header.startswith(bytes.fromhex("1A45DFA3"))
    if ext == ".avi":
        return len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"AVI "
    return False


async def save_upload(upload: UploadFile) -> dict:
    """Stream an upload to a temporary file, enforcing size and hashing bytes."""
    settings = get_settings()
    original_name = safe_original_filename(upload.filename)
    extension = Path(original_name).suffix.lower()

    if extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported video extension. Allowed: {', '.join(sorted(settings.allowed_extensions))}",
        )

    media_root = Path(settings.media_root).expanduser().resolve()
    media_root.mkdir(parents=True, exist_ok=True)
    temp_path = media_root / f".upload-{uuid4().hex}.part"
    stored_filename = f"{uuid4().hex}{extension}"
    final_path = media_root / stored_filename
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    total = 0
    digest = hashlib.sha256()
    header = b""

    try:
        with temp_path.open("xb") as destination:
            while True:
                chunk = await upload.read(CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds the {settings.max_upload_size_mb} MB upload limit.",
                    )
                if len(header) < 32:
                    header += chunk[: 32 - len(header)]
                digest.update(chunk)
                destination.write(chunk)
            destination.flush()
            os.fsync(destination.fileno())

        if total == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded file is empty.")

        if not has_supported_signature(extension, header):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="The file content does not match a supported video format.",
            )

        os.replace(temp_path, final_path)
        return {
            "original_filename": original_name,
            "stored_filename": stored_filename,
            "storage_path": stored_filename,
            "content_type": upload.content_type or "application/octet-stream",
            "file_extension": extension,
            "file_size_bytes": total,
            "sha256": digest.hexdigest(),
        }
    except Exception:
        temp_path.unlink(missing_ok=True)
        final_path.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()
