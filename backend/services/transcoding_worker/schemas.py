from pydantic import BaseModel, Field
class TranscodingRequest(BaseModel):
    job_id: str = Field(min_length=1, max_length=36)
    video_id: str = Field(min_length=1, max_length=36)
    profile: str = Field(min_length=1, max_length=32)
    source_path: str = Field(min_length=1)
    source_event_id: str | None = None
    max_attempts: int | None = Field(default=None, ge=1, le=10)
    priority: int | None = None
