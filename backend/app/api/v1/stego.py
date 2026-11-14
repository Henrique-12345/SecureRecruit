from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, File, Form, Query, Request, UploadFile
from fastapi.responses import FileResponse

from app.core.enums import CryptoAlgorithm, SecurityEventType
from app.core.exceptions import AppError
from app.dependencies.auth import AdminUser, DbSession
from app.schemas.stego import StegoArtifactRead, StegoEmbedResponse, StegoExtractResponse
from app.services.audit_service import AuditService
from app.services.stego.stego_lab_service import StegoLabService
from app.utils.request import get_client_ip, get_user_agent


router = APIRouter(prefix="/stego", tags=["stego-lab"])


@router.post("/embed", response_model=StegoEmbedResponse, status_code=201)
async def embed_payload(
    request: Request,
    admin: AdminUser,
    db: DbSession,
    cover: UploadFile = File(...),
    plaintext: str = Form(..., min_length=1, max_length=100_000),
    algorithm: CryptoAlgorithm = Form(default=CryptoAlgorithm.CUSTOM_SPN),
    key_id: UUID | None = Form(default=None),
) -> StegoEmbedResponse:
    artifact = StegoLabService(db).embed(
        user=admin,
        cover=cover,
        plaintext=plaintext,
        algorithm=algorithm.value,
        key_id=key_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return StegoEmbedResponse(artifact=StegoArtifactRead.model_validate(artifact))


@router.post("/extract", response_model=StegoExtractResponse)
async def extract_payload(
    request: Request,
    admin: AdminUser,
    db: DbSession,
    stego: UploadFile | None = File(default=None),
    artifact_id: UUID | None = Form(default=None),
    algorithm: CryptoAlgorithm | None = Form(default=None),
    key_id: UUID | None = Form(default=None),
) -> StegoExtractResponse:
    if stego is None and artifact_id is None:
        raise AppError("Provide stego file or artifact_id", status_code=400)

    artifact, plaintext = StegoLabService(db).extract(
        user=admin,
        stego_file=stego,
        artifact_id=artifact_id,
        algorithm=algorithm.value if algorithm else None,
        key_id=key_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return StegoExtractResponse(
        artifact_id=artifact.id if artifact else artifact_id,
        plaintext=plaintext,
    )


@router.get("/artifacts", response_model=list[StegoArtifactRead])
def list_artifacts(
    _: AdminUser,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[StegoArtifactRead]:
    items = StegoLabService(db).list_artifacts(limit=limit)
    return [StegoArtifactRead.model_validate(a) for a in items]


@router.get("/artifacts/{artifact_id}", response_model=StegoArtifactRead)
def get_artifact(artifact_id: UUID, _: AdminUser, db: DbSession) -> StegoArtifactRead:
    artifact = StegoLabService(db).get_artifact(artifact_id)
    return StegoArtifactRead.model_validate(artifact)


@router.get("/artifacts/{artifact_id}/download")
def download_stego(
    artifact_id: UUID,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> FileResponse:
    artifact = StegoLabService(db).get_artifact(artifact_id)
    path = Path(artifact.stego_file_path)
    AuditService(db).log_event(
        event_type=SecurityEventType.STEGO,
        action="stego_download",
        success=True,
        user_id=admin.id,
        resource="stego_artifact",
        resource_id=artifact.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details=f"Downloaded {artifact.stego_stored_filename}",
    )
    return FileResponse(
        path=path,
        media_type="image/png",
        filename=artifact.stego_stored_filename,
    )
