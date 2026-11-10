from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "api-gateway"
    app_env: str = "development"
    log_level: str = "INFO"

    video_upload_url: str = "http://video_upload:8000"
    video_metadata_url: str = "http://video_metadata:8000"
    transcoding_orchestrator_url: str = "http://transcoding_orchestrator:8000"
    media_delivery_url: str = "http://media_delivery:8000"
    thumbnail_service_url: str = "http://thumbnail_service:8000"

    request_timeout_seconds: float = 120.0
    connect_timeout_seconds: float = 5.0
    openapi_timeout_seconds: float = 8.0
    max_connections: int = 200
    max_keepalive_connections: int = 40
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [value.strip() for value in self.cors_origins.split(",") if value.strip()]


settings = Settings()
