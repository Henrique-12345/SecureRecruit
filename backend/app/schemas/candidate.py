from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CandidateProfileBase(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    professional_summary: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    linkedin_url: Optional[str] = None


class CandidateProfileUpdate(CandidateProfileBase):
    pass


class CandidateProfileRead(CandidateProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class CandidatePublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    name: str
    email: str
    professional_summary: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    linkedin_url: Optional[str] = None
