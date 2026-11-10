"""Validated API request and response schemas."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class VideoUploadResponse(BaseModel):
    id: str
    original_filename: str
    content_type: str
    file_extension: str
    file_size_bytes: int
    sha256: str
    status: str
    created_at: datetime


class VideoListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    content_type: str
    file_extension: str
    file_size_bytes: int
    sha256: str
    status: str
    created_at: datetime


class VideoListResponse(BaseModel):
    items: list[VideoListItem]
    total: int
    limit: int
    offset: int


class VideoDetailResponse(VideoListItem):
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str = Field(description="Service health status")
    service: str
    database: str
