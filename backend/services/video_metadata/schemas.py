"""API response schemas for the Video Metadata Service."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    video_id: str
    original_filename: str
    storage_path: str
    content_type: str
    file_extension: str
    file_size_bytes: int
    sha256: str
    source_event_id: str
    created_at: datetime
    updated_at: datetime


class MetadataListResponse(BaseModel):
    items: list[MetadataResponse]
    total: int
    limit: int
    offset: int


class HealthResponse(BaseModel):
    status: str
    service: str
    database: str
    rabbitmq_consumer: str
    details: dict[str, str] = Field(default_factory=dict)