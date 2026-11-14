from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AnomalyRunRequest(BaseModel):
    hours: int = Field(default=24, ge=1, le=720)
    auth_burst_threshold: int = Field(default=20, ge=1, le=10000)
    decrypt_fail_rate_threshold: float = Field(default=0.25, ge=0.01, le=1.0)
    access_denied_threshold: int = Field(default=30, ge=1, le=10000)
    event_spike_z: float = Field(default=2.5, ge=0.5, le=10.0)


class AnomalyEventRead(BaseModel):
    id: UUID
    anomaly_type: str
    severity: str
    score: float
    source_user_id: UUID | None
    evidence: dict | None
    resolved: bool
    detected_at: datetime

    model_config = {"from_attributes": True}


class AnomalyRunResponse(BaseModel):
    created_count: int
    anomalies: list[AnomalyEventRead]


class AnomalyResolveResponse(BaseModel):
    anomaly: AnomalyEventRead
    message: str = "Anomaly marked as resolved"
