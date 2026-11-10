import json, logging, os, subprocess, tempfile
from pathlib import Path
from .config import Settings

logger = logging.getLogger(__name__)
PROFILE_DIMENSIONS = {"144p": (256,144), "240p": (426,240), "360p": (640,360),
                      "480p": (854,480), "720p": (1280,720), "1080p": (1920,1080)}

class TranscodingError(RuntimeError):
    pass

def run(command: list[str], timeout: int) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise TranscodingError(f"Command timed out after {timeout} seconds") from exc
    if result.returncode:
        raise TranscodingError((result.stderr or result.stdout or "Unknown FFmpeg error")[-4000:])
    return result

def resolve_source(source_path: str, media_root: str) -> Path:
    root = Path(media_root).resolve()
    candidate = Path(source_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    if candidate != root and root not in candidate.parents:
        raise TranscodingError("Source path is outside the media directory")
    if not candidate.is_file() or candidate.stat().st_size == 0:
        raise TranscodingError(f"Source file is missing or empty: {candidate.name}")
    return candidate

def probe(source: Path, settings: Settings) -> dict:
    result = run([settings.ffprobe_binary, "-v", "error", "-show_entries",
                  "format=duration,format_name:stream=codec_type,width,height",
                  "-of", "json", str(source)], settings.job_timeout_seconds)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise TranscodingError("ffprobe returned invalid JSON") from exc
    if not any(s.get("codec_type") == "video" for s in data.get("streams", [])):
        raise TranscodingError("Input contains no video stream")
    return data

def transcode(source_path: str, video_id: str, job_id: str, profile: str, settings: Settings) -> str:
    if profile not in PROFILE_DIMENSIONS:
        raise TranscodingError(f"Unsupported profile: {profile}")
    source = resolve_source(source_path, settings.media_root)
    probe(source, settings)
    width, height = PROFILE_DIMENSIONS[profile]
    root = Path(settings.media_root).resolve()
    output_dir = (root / settings.output_subdirectory / video_id).resolve()
    if root not in output_dir.parents:
        raise TranscodingError("Output directory is outside media root")
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{profile}.mp4"
    fd, temp_name = tempfile.mkstemp(prefix=f".{job_id}-", suffix=".mp4", dir=output_dir)
    os.close(fd)
    temp = Path(temp_name)
    try:
        run([settings.ffmpeg_binary, "-hide_banner", "-nostdin", "-y", "-i", str(source),
             "-map", "0:v:0", "-map", "0:a?", "-vf",
             f"scale=w={width}:h={height}:force_original_aspect_ratio=decrease:force_divisible_by=2",
             "-c:v", settings.default_video_codec, "-preset", "veryfast", "-crf", "23",
             "-c:a", settings.default_audio_codec, "-b:a", "128k", "-movflags", "+faststart",
             str(temp)], settings.job_timeout_seconds)
        if not temp.is_file() or temp.stat().st_size < 1024:
            raise TranscodingError("FFmpeg output is missing or unexpectedly small")
        probe(temp, settings)
        os.replace(temp, output)
    finally:
        temp.unlink(missing_ok=True)
    return str(output.relative_to(root)).replace("\\", "/")
