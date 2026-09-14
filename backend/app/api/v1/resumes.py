from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import FileResponse

from app.core.enums import SecurityEventType
from app.dependencies.auth import AdminUser, CurrentUser, DbSession
from app.schemas.resume import IntegrityCheckResponse, ResumeRead
from app.services.audit_service import AuditService
from app.services.resume_service import ResumeService
from app.utils.request import get_client_ip, get_user_agent


router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeRead, status_code=201)
async def upload_resume(
    request: Request,
    current_user: CurrentUser,
    db: DbSession,
    file: UploadFile = File(...),
) -> ResumeRead:
    resume = ResumeService(db).upload(
        candidate=current_user,
        file=file,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return ResumeRead.model_validate(resume)


@router.get("", response_model=list[ResumeRead])
def list_resumes(current_user: CurrentUser, db: DbSession) -> list[ResumeRead]:
    resumes = ResumeService(db).list_for_user(current_user)
    return [ResumeRead.model_validate(r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeRead)
def get_resume(
    resume_id: UUID, current_user: CurrentUser, db: DbSession
) -> ResumeRead:
    resume = ResumeService(db).get_authorized(resume_id, current_user)
    return ResumeRead.model_validate(resume)


@router.get("/{resume_id}/download")
def download_resume(
    resume_id: UUID,
    request: Request,
    current_user: CurrentUser,
    db: DbSession,
) -> FileResponse:
    resume = ResumeService(db).get_authorized(resume_id, current_user)
    path = Path(resume.file_path)
    AuditService(db).log_event(
        event_type=SecurityEventType.RESUME,
        action="resume_download",
        success=True,
        user_id=current_user.id,
        resource="resume",
        resource_id=resume.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details=f"Downloaded {resume.original_filename}",
    )
    return FileResponse(
        path=path,
        media_type=resume.content_type,
        filename=resume.original_filename,
    )


@router.delete("/{resume_id}", status_code=204)
def delete_resume(
    resume_id: UUID,
    request: Request,
    current_user: CurrentUser,
    db: DbSession,
) -> None:
    ResumeService(db).delete(
        resume_id,
        current_user,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


@router.get("/{resume_id}/integrity", response_model=IntegrityCheckResponse)
def check_integrity(
    resume_id: UUID,
    _: AdminUser,
    db: DbSession,
) -> IntegrityCheckResponse:
    result = ResumeService(db).check_integrity(resume_id)
    return IntegrityCheckResponse(**result)
