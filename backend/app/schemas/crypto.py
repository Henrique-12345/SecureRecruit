from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import CryptoAlgorithm, CryptoInputKind


class KeyGenerateRequest(BaseModel):
    algorithm: CryptoAlgorithm = CryptoAlgorithm.CUSTOM_SPN
    label: str | None = Field(default=None, max_length=120)


class KeyMaterialRead(BaseModel):
    id: UUID
    algorithm: str
    key_fingerprint: str
    label: str | None
    is_active: bool
    created_at: datetime
    derivation_info: dict | None = None

    model_config = {"from_attributes": True}


class EncryptRequest(BaseModel):
    algorithm: CryptoAlgorithm = CryptoAlgorithm.CUSTOM_SPN
    plaintext: str = Field(..., min_length=1, max_length=100_000)
    key_id: UUID | None = None
    input_kind: CryptoInputKind = CryptoInputKind.TEXT


class EncryptResponse(BaseModel):
    operation_id: UUID
    algorithm: str
    ciphertext_b64: str
    key_id: UUID | None
    key_fingerprint: str
    input_size: int
    output_size: int
    duration_ms: int | None


class DecryptRequest(BaseModel):
    algorithm: CryptoAlgorithm = CryptoAlgorithm.CUSTOM_SPN
    ciphertext_b64: str = Field(..., min_length=1)
    key_id: UUID | None = None


class DecryptResponse(BaseModel):
    operation_id: UUID
    algorithm: str
    plaintext: str
    key_id: UUID | None
    input_size: int
    output_size: int
    duration_ms: int | None


class AvalancheRequest(BaseModel):
    algorithm: CryptoAlgorithm = CryptoAlgorithm.CUSTOM_SPN
    plaintext: str = Field(..., min_length=1, max_length=100_000)
    key_id: UUID | None = None


class AvalancheResponse(BaseModel):
    operation_id: UUID
    algorithm: str
    report: dict


class StatisticalRequest(BaseModel):
    algorithm: CryptoAlgorithm = CryptoAlgorithm.CUSTOM_SPN
    ciphertext_b64: str = Field(..., min_length=1)


class StatisticalResponse(BaseModel):
    operation_id: UUID
    algorithm: str
    report: dict


class CryptoOperationRead(BaseModel):
    id: UUID
    user_id: UUID | None
    key_material_id: UUID | None
    operation_type: str
    algorithm: str
    input_kind: str
    input_size: int
    output_size: int
    success: bool
    error_code: str | None
    avalanche_score: float | None
    duration_ms: int | None
    details: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
