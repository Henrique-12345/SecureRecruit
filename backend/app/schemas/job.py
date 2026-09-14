from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import EmploymentType, JobStatus


class JobBase(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    requirements: str = Field(min_length=5)
    location: str = Field(min_length=2, max_length=150)
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    salary_range: Optional[str] = Field(default=None, max_length=100)


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=200)
    description: Optional[str] = Field(default=None, min_length=10)
    requirements: Optional[str] = Field(default=None, min_length=5)
    location: Optional[str] = Field(default=None, min_length=2, max_length=150)
    employment_type: Optional[EmploymentType] = None
    salary_range: Optional[str] = Field(default=None, max_length=100)
    status: Optional[JobStatus] = None


class JobRead(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recruiter_id: UUID
    status: JobStatus
    created_at: datetime
    updated_at: datetime
