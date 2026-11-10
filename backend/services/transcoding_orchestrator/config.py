from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    service_name: str = "transcoding-orchestrator"
    app_env: str = "production"
    log_level: str = "INFO"
    database_url: str = "mysql+pymysql://user:password@mysql:3306/transcoding_orchestrator_db"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/%2F"
    input_exchange: str = "video.events"
    input_queue: str = "video.transcoding.orchestrator.queue"
    input_routing_key: str = "video.uploaded"
    dead_letter_exchange: str = "video.dlx"
    dead_letter_queue: str = "video.transcoding.orchestrator.dlq"
    dead_letter_routing_key: str = "video.transcoding.orchestrator.dead"
    output_exchange: str = "video.transcoding"
    output_routing_key: str = "transcoding.requested"
    default_profiles: str = "360p,480p,720p"
    job_max_attempts: int = 3
    outbox_poll_seconds: float = 2
    consumer_prefetch: int = 10
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

settings = Settings()
