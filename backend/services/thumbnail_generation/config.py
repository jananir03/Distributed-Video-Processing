from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")
    service_name: str = "thumbnail-service"
    log_level: str = "INFO"
    database_url: str = "mysql+pymysql://video_app:change_me@mysql:3306/thumbnail_db"
    worker_database_url: str = "mysql+pymysql://video_app:change_me@mysql:3306/transcoding_worker_db"
    media_root: str = "/app/media"
    ffmpeg_binary: str = "ffmpeg"
    poll_interval_seconds: int = Field(default=10, ge=2, le=300)
    batch_size: int = Field(default=50, ge=1, le=500)
    max_attempts: int = Field(default=3, ge=1, le=10)
    command_timeout_seconds: int = Field(default=120, ge=10, le=900)
    thumbnail_seek_seconds: float = Field(default=1.0, ge=0, le=60)

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
