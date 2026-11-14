from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.dependencies.auth import AdminUser, DbSession
from app.schemas.crypto import (
    AttackExperimentRead,
    AvalancheRequest,
    AvalancheResponse,
    BruteForceAttackRequest,
    CryptoOperationRead,
    DecryptRequest,
    DecryptResponse,
    DifferentialAttackRequest,
    EncryptRequest,
    EncryptResponse,
    KeyGenerateRequest,
    KeyMaterialRead,
    StatisticalAttackRequest,
    StatisticalRequest,
    StatisticalResponse,
)
from app.services.crypto.attack_lab_service import AttackLabService
from app.services.crypto.crypto_lab_service import CryptoLabService
from app.utils.request import get_client_ip, get_user_agent


router = APIRouter(prefix="/crypto", tags=["crypto-lab"])


@router.post("/keys/generate", response_model=KeyMaterialRead)
def generate_key(
    payload: KeyGenerateRequest,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> KeyMaterialRead:
    material = CryptoLabService(db).generate_key(
        owner=admin,
        algorithm=payload.algorithm.value,
        label=payload.label,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return KeyMaterialRead.model_validate(material)


@router.post("/encrypt", response_model=EncryptResponse)
def encrypt(
    payload: EncryptRequest,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> EncryptResponse:
    operation, ciphertext_b64, fingerprint = CryptoLabService(db).encrypt(
        user=admin,
        algorithm=payload.algorithm.value,
        plaintext=payload.plaintext.encode("utf-8"),
        input_kind=payload.input_kind.value,
        key_id=payload.key_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return EncryptResponse(
        operation_id=operation.id,
        algorithm=operation.algorithm,
        ciphertext_b64=ciphertext_b64,
        key_id=operation.key_material_id,
        key_fingerprint=fingerprint,
        input_size=operation.input_size,
        output_size=operation.output_size,
        duration_ms=operation.duration_ms,
    )


@router.post("/decrypt", response_model=DecryptResponse)
def decrypt(
    payload: DecryptRequest,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> DecryptResponse:
    operation, plaintext = CryptoLabService(db).decrypt(
        user=admin,
        algorithm=payload.algorithm.value,
        ciphertext_b64=payload.ciphertext_b64,
        key_id=payload.key_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return DecryptResponse(
        operation_id=operation.id,
        algorithm=operation.algorithm,
        plaintext=plaintext.decode("utf-8"),
        key_id=operation.key_material_id,
        input_size=operation.input_size,
        output_size=operation.output_size,
        duration_ms=operation.duration_ms,
    )


@router.get("/operations", response_model=list[CryptoOperationRead])
def list_operations(
    _: AdminUser,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[CryptoOperationRead]:
    ops = CryptoLabService(db).list_operations(limit=limit)
    return [CryptoOperationRead.model_validate(op) for op in ops]


@router.get("/operations/{operation_id}", response_model=CryptoOperationRead)
def get_operation(operation_id: UUID, _: AdminUser, db: DbSession) -> CryptoOperationRead:
    op = CryptoLabService(db).get_operation(operation_id)
    return CryptoOperationRead.model_validate(op)


@router.post("/metrics/avalanche", response_model=AvalancheResponse)
def avalanche(
    payload: AvalancheRequest,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> AvalancheResponse:
    operation, report = CryptoLabService(db).avalanche(
        user=admin,
        algorithm=payload.algorithm.value,
        plaintext=payload.plaintext.encode("utf-8"),
        key_id=payload.key_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return AvalancheResponse(
        operation_id=operation.id,
        algorithm=operation.algorithm,
        report=report,
    )


@router.post("/metrics/statistical", response_model=StatisticalResponse)
def statistical(
    payload: StatisticalRequest,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> StatisticalResponse:
    operation, report = CryptoLabService(db).statistical(
        user=admin,
        ciphertext_b64=payload.ciphertext_b64,
        algorithm=payload.algorithm.value,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return StatisticalResponse(
        operation_id=operation.id,
        algorithm=operation.algorithm,
        report=report,
    )


@router.post("/attacks/brute-force", response_model=AttackExperimentRead)
def attack_brute_force(
    payload: BruteForceAttackRequest,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> AttackExperimentRead:
    experiment = AttackLabService(db).brute_force(
        user=admin,
        plaintext=payload.plaintext,
        searchable_bits=payload.searchable_bits,
        key_id=payload.key_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return AttackExperimentRead.model_validate(experiment)


@router.post("/attacks/differential", response_model=AttackExperimentRead)
def attack_differential(
    payload: DifferentialAttackRequest,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> AttackExperimentRead:
    experiment = AttackLabService(db).differential(
        user=admin,
        plaintext=payload.plaintext,
        key_id=payload.key_id,
        flip_byte_index=payload.flip_byte_index,
        flip_bit_mask=payload.flip_bit_mask,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return AttackExperimentRead.model_validate(experiment)


@router.post("/attacks/statistical", response_model=AttackExperimentRead)
def attack_statistical(
    payload: StatisticalAttackRequest,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> AttackExperimentRead:
    experiment = AttackLabService(db).statistical(
        user=admin,
        ciphertext_b64=payload.ciphertext_b64,
        plaintext=payload.plaintext,
        key_id=payload.key_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return AttackExperimentRead.model_validate(experiment)


@router.get("/attacks/experiments", response_model=list[AttackExperimentRead])
def list_attack_experiments(
    _: AdminUser,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AttackExperimentRead]:
    items = AttackLabService(db).list_experiments(limit=limit)
    return [AttackExperimentRead.model_validate(e) for e in items]


@router.get("/attacks/experiments/{experiment_id}", response_model=AttackExperimentRead)
def get_attack_experiment(
    experiment_id: UUID, _: AdminUser, db: DbSession
) -> AttackExperimentRead:
    experiment = AttackLabService(db).get_experiment(experiment_id)
    return AttackExperimentRead.model_validate(experiment)
