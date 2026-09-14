from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.dependencies.auth import CurrentUser, DbSession, OptionalUser, RecruiterUser
from app.schemas.job import JobCreate, JobRead, JobUpdate
from app.services.job_service import JobService
from app.utils.request import get_client_ip, get_user_agent


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
def list_jobs(
    db: DbSession,
    current_user: OptionalUser,
    mine: bool = Query(default=False),
) -> list[JobRead]:
    jobs = JobService(db).list_jobs(current_user, mine=mine)
    return [JobRead.model_validate(j) for j in jobs]


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: UUID, db: DbSession, current_user: OptionalUser) -> JobRead:
    job = JobService(db).get_job(job_id, current_user)
    return JobRead.model_validate(job)


@router.post("", response_model=JobRead, status_code=201)
def create_job(
    payload: JobCreate,
    request: Request,
    current_user: RecruiterUser,
    db: DbSession,
) -> JobRead:
    job = JobService(db).create(
        current_user,
        payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return JobRead.model_validate(job)


@router.put("/{job_id}", response_model=JobRead)
def update_job(
    job_id: UUID,
    payload: JobUpdate,
    request: Request,
    current_user: RecruiterUser,
    db: DbSession,
) -> JobRead:
    job = JobService(db).update(
        job_id,
        current_user,
        payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return JobRead.model_validate(job)


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: UUID,
    request: Request,
    current_user: RecruiterUser,
    db: DbSession,
) -> None:
    JobService(db).delete(
        job_id,
        current_user,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
