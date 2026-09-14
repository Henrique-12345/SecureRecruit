from uuid import UUID

from fastapi import APIRouter, Request

from app.dependencies.auth import CandidateUser, CurrentUser, DbSession, RecruiterUser
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationDetail,
    ApplicationRead,
    ApplicationStatusUpdate,
)
from app.services.application_service import ApplicationService
from app.utils.request import get_client_ip, get_user_agent


router = APIRouter(tags=["applications"])


def _to_detail(db, application) -> ApplicationDetail:
    candidate = db.query(User).filter(User.id == application.candidate_id).first()
    job = db.query(Job).filter(Job.id == application.job_id).first()
    resume = db.query(Resume).filter(Resume.id == application.resume_id).first()
    base = ApplicationRead.model_validate(application)
    return ApplicationDetail(
        **base.model_dump(),
        candidate_name=candidate.name if candidate else None,
        job_title=job.title if job else None,
        resume_filename=resume.original_filename if resume else None,
    )


@router.post(
    "/jobs/{job_id}/applications",
    response_model=ApplicationRead,
    status_code=201,
)
def apply_to_job(
    job_id: UUID,
    payload: ApplicationCreate,
    request: Request,
    current_user: CandidateUser,
    db: DbSession,
) -> ApplicationRead:
    application = ApplicationService(db).apply(
        candidate=current_user,
        job_id=job_id,
        payload=payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return ApplicationRead.model_validate(application)


@router.get("/applications/me", response_model=list[ApplicationDetail])
def my_applications(current_user: CurrentUser, db: DbSession) -> list[ApplicationDetail]:
    apps = ApplicationService(db).list_mine(current_user)
    return [_to_detail(db, a) for a in apps]


@router.get("/applications/{application_id}", response_model=ApplicationDetail)
def get_application(
    application_id: UUID, current_user: CurrentUser, db: DbSession
) -> ApplicationDetail:
    application = ApplicationService(db).get_authorized(application_id, current_user)
    return _to_detail(db, application)


@router.get("/jobs/{job_id}/applications", response_model=list[ApplicationDetail])
def job_applications(
    job_id: UUID, current_user: RecruiterUser, db: DbSession
) -> list[ApplicationDetail]:
    apps = ApplicationService(db).list_for_job(job_id, current_user)
    return [_to_detail(db, a) for a in apps]


@router.patch(
    "/applications/{application_id}/status",
    response_model=ApplicationRead,
)
def update_status(
    application_id: UUID,
    payload: ApplicationStatusUpdate,
    request: Request,
    current_user: RecruiterUser,
    db: DbSession,
) -> ApplicationRead:
    application = ApplicationService(db).update_status(
        application_id,
        current_user,
        payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return ApplicationRead.model_validate(application)
