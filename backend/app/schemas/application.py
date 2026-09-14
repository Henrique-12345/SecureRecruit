from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ApplicationStatus


class ApplicationCreate(BaseModel):
    resume_id: UUID


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID
    job_id: UUID
    resume_id: UUID
    status: ApplicationStatus
    applied_at: datetime
    updated_at: datetime


class ApplicationDetail(ApplicationRead):
    candidate_name: str | None = None
    job_title: str | None = None
    resume_filename: str | None = None
