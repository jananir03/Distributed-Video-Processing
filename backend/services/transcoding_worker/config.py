from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
    service_name: str = "video-transcoding-worker"
    log_level: str = "INFO"
    rabbitmq_url: str = "amqp://video_app:change_me@rabbitmq:5672/%2F"
    input_exchange: str = "video.transcoding"
    input_queue: str = "video.transcoding.worker.queue"
    input_routing_key: str = "transcoding.requested"
    dead_letter_exchange: str = "video.dlx"
    dead_letter_queue: str = "video.transcoding.worker.dlq"
    dead_letter_routing_key: str = "video.transcoding.worker.dead"
    prefetch_count: int = Field(default=1, ge=1, le=100)
    database_url: str = "mysql+pymysql://video_app:change_me@mysql:3306/transcoding_worker_db"
    orchestrator_database_url: str = "mysql+pymysql://video_app:change_me@mysql:3306/transcoding_orchestrator_db"
    media_root: str = "/app/media"
    output_subdirectory: str = "transcoded"
    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"
    max_attempts: int = Field(default=3, ge=1, le=10)
    retry_delay_seconds: float = Field(default=2.0, ge=0, le=60)
    job_timeout_seconds: int = Field(default=3600, ge=60, le=86400)
    default_video_codec: str = "libx264"
    default_audio_codec: str = "aac"

@lru_cache
def get_settings() -> Settings:
    return Settings()
