from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class StegoArtifactRead(BaseModel):
    id: UUID
    user_id: UUID
    payload_operation_id: UUID | None
    cover_original_filename: str
    stego_stored_filename: str
    capacity_bits: int
    payload_bits: int
    created_at: datetime

    model_config = {"from_attributes": True}


class StegoExtractResponse(BaseModel):
    artifact_id: UUID | None = None
    plaintext: str
    message: str = "Payload recovered"


class StegoEmbedResponse(BaseModel):
    artifact: StegoArtifactRead
    message: str = Field(default="Payload encrypted and embedded via LSB")
