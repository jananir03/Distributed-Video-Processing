import logging
import os
import subprocess
import tempfile
from pathlib import Path
from .config import Settings

logger = logging.getLogger(__name__)

class ThumbnailError(RuntimeError):
    pass

def resolve_media_path(value: str, media_root: str) -> Path:
    root = Path(media_root).resolve()
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    if candidate != root and root not in candidate.parents:
        raise ThumbnailError("Media path resolves outside MEDIA_ROOT")
    if not candidate.is_file() or candidate.stat().st_size == 0:
        raise ThumbnailError(f"Input file is missing or empty: {candidate.name}")
    return candidate

def _extract(source: Path, target: Path, settings: Settings, seek: float) -> None:
    cmd = [settings.ffmpeg_binary, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
           "-ss", str(seek), "-i", str(source), "-map", "0:v:0", "-frames:v", "1",
           "-vf", "scale=w=640:h=360:force_original_aspect_ratio=decrease:force_divisible_by=2",
           "-q:v", "2", str(target)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=settings.command_timeout_seconds, check=False)
    except subprocess.TimeoutExpired as exc:
        raise ThumbnailError(f"FFmpeg timed out after {settings.command_timeout_seconds} seconds") from exc
    if result.returncode != 0 or not target.is_file() or target.stat().st_size < 256:
        target.unlink(missing_ok=True)
        raise ThumbnailError((result.stderr or result.stdout or "FFmpeg did not produce a valid thumbnail")[-2000:])

def generate_thumbnail(source_path: str, video_id: str, profile: str, settings: Settings) -> str:
    source = resolve_media_path(source_path, settings.media_root)
    root = Path(settings.media_root).resolve()
    # IDs are validated before being used as path segments.
    safe_video_id = "".join(c for c in video_id if c.isalnum() or c in "-_")
    safe_profile = "".join(c for c in profile if c.isalnum() or c in "-_")
    if not safe_video_id or safe_video_id != video_id or not safe_profile or safe_profile != profile:
        raise ThumbnailError("Invalid video_id or profile path segment")
    output_dir = (root / "thumbnails" / safe_video_id).resolve()
    if root not in output_dir.parents:
        raise ThumbnailError("Thumbnail output path resolves outside MEDIA_ROOT")
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{safe_profile}.jpg"
    fd, temp_name = tempfile.mkstemp(prefix=f".{safe_profile}-", suffix=".jpg", dir=output_dir)
    os.close(fd)
    temp = Path(temp_name)
    try:
        try:
            _extract(source, temp, settings, settings.thumbnail_seek_seconds)
        except ThumbnailError:
            # Short videos may have no frame at the configured seek point.
            if settings.thumbnail_seek_seconds <= 0:
                raise
            _extract(source, temp, settings, 0)
        os.replace(temp, output)
    finally:
        temp.unlink(missing_ok=True)
    return str(output.relative_to(root)).replace("\\", "/")
