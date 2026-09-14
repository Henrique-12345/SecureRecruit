from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeResumeRequest(BaseModel):
    resume_id: UUID


class MatchResumeJobRequest(BaseModel):
    resume_id: UUID
    job_id: UUID


class AIAnalysisResult(BaseModel):
    summary: str
    key_skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    relevant_experience: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    compatibility_notes: Optional[str] = None
    compatibility_score: Optional[float] = Field(default=None, ge=0, le=100)


class AIAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resume_id: UUID
    job_id: Optional[UUID] = None
    analysis_text: str
    extracted_skills: Optional[str] = None
    compatibility_score: Optional[float] = None
    created_at: datetime
    result: Optional[AIAnalysisResult] = None
