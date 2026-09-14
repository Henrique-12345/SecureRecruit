from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.core.enums import SecurityEventType
from app.core.exceptions import NotFoundError
from app.dependencies.auth import AdminUser, DbSession
from app.models.application import Application
from app.models.job import Job
from app.models.resume import Resume
from app.models.security_log import SecurityLog
from app.models.user import User
from app.schemas.application import ApplicationDetail, ApplicationRead
from app.schemas.security_log import SecurityLogRead
from app.schemas.user import UserAdminRead, UserStatusUpdate
from app.services.audit_service import AuditService
from app.utils.request import get_client_ip, get_user_agent


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserAdminRead])
def list_users(_: AdminUser, db: DbSession) -> list[UserAdminRead]:
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserAdminRead.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=UserAdminRead)
def get_user(user_id: UUID, _: AdminUser, db: DbSession) -> UserAdminRead:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User not found")
    return UserAdminRead.model_validate(user)


@router.patch("/users/{user_id}/status", response_model=UserAdminRead)
def update_user_status(
    user_id: UUID,
    payload: UserStatusUpdate,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> UserAdminRead:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User not found")

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)

    AuditService(db).log_event(
        event_type=SecurityEventType.ADMIN,
        action="user_status_updated",
        success=True,
        user_id=admin.id,
        resource="user",
        resource_id=user.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details=f"is_active={user.is_active}",
    )
    return UserAdminRead.model_validate(user)


@router.get("/logs", response_model=list[SecurityLogRead])
def list_admin_logs(
    _: AdminUser,
    db: DbSession,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[SecurityLogRead]:
    logs = (
        db.query(SecurityLog)
        .order_by(SecurityLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [SecurityLogRead.model_validate(log) for log in logs]


@router.get("/applications", response_model=list[ApplicationDetail])
def list_applications(_: AdminUser, db: DbSession) -> list[ApplicationDetail]:
    apps = db.query(Application).order_by(Application.applied_at.desc()).all()
    details: list[ApplicationDetail] = []
    for application in apps:
        candidate = db.query(User).filter(User.id == application.candidate_id).first()
        job = db.query(Job).filter(Job.id == application.job_id).first()
        resume = db.query(Resume).filter(Resume.id == application.resume_id).first()
        base = ApplicationRead.model_validate(application)
        details.append(
            ApplicationDetail(
                **base.model_dump(),
                candidate_name=candidate.name if candidate else None,
                job_title=job.title if job else None,
                resume_filename=resume.original_filename if resume else None,
            )
        )
    return details
