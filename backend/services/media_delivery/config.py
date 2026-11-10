from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")
    service_name: str = "media-delivery"
    log_level: str = "INFO"
    worker_database_url: str = Field(..., min_length=1)
    media_root: Path = Path("/app/media")
    max_page_size: int = Field(default=100, ge=1, le=500)
    stream_cache_control: str = "private, no-cache"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
