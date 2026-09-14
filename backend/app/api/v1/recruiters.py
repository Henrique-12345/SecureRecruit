from fastapi import APIRouter

from app.dependencies.auth import CurrentUser, DbSession
from app.models.job import Job
from app.schemas.job import JobRead
from app.schemas.user import UserRead


router = APIRouter(prefix="/recruiters", tags=["recruiters"])


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.get("/me/jobs", response_model=list[JobRead])
def my_jobs(current_user: CurrentUser, db: DbSession) -> list[JobRead]:
    jobs = (
        db.query(Job)
        .filter(Job.recruiter_id == current_user.id)
        .order_by(Job.created_at.desc())
        .all()
    )
    return [JobRead.model_validate(j) for j in jobs]
