from datetime import datetime
from pydantic import BaseModel, ConfigDict

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    video_id: str
    source_event_id: str
    source_path: str
    profile: str
    status: str
    priority: int
    attempt_count: int
    max_attempts: int
    error_message: str | None
    output_path: str | None
    created_at: datetime
    updated_at: datetime

class JobListResponse(BaseModel):
    items: list[JobResponse]
    limit: int
    offset: int
    total: int
