from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID
    original_filename: str
    stored_filename: str
    content_type: str
    file_size: int
    sha256_hash: str
    uploaded_at: datetime


class IntegrityCheckResponse(BaseModel):
    resume_id: UUID
    stored_hash: str
    current_hash: str
    integrity_ok: bool
    message: str
