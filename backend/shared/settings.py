"""Environment-backed configuration shared by backend services."""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings are supplied through environment variables in Docker Compose."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    service_name: str = "video-service"
    environment: str = "development"
    log_level: str = "INFO"

    # Each service receives a URL for its own database schema.
    database_url: str = ""

    rabbitmq_url: str = ""
    redis_url: str = ""

    media_root: str = "/app/media"
    max_upload_size_mb: int = Field(default=500, ge=1, le=4096)
    allowed_video_extensions: str = ".mp4,.mov,.mkv,.webm,.avi"
    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"
    ffmpeg_timeout_seconds: int = Field(default=1800, ge=30, le=14400)

    @property
    def allowed_extensions(self) -> set[str]:
        return {
            extension.strip().lower()
            for extension in self.allowed_video_extensions.split(",")
            if extension.strip()
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return one cached settings object per service process."""
    return Settings()
