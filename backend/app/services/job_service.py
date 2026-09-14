from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import JobStatus, SecurityEventType, UserRole
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate
from app.services.audit_service import AuditService


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def list_jobs(self, user: User | None = None, *, mine: bool = False) -> list[Job]:
        query = self.db.query(Job)
        if mine and user and user.role == UserRole.RECRUITER.value:
            query = query.filter(Job.recruiter_id == user.id)
        elif user is None or user.role == UserRole.CANDIDATE.value:
            query = query.filter(Job.status == JobStatus.OPEN.value)
        return query.order_by(Job.created_at.desc()).all()

    def get_job(self, job_id: UUID, user: User | None = None) -> Job:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise NotFoundError("Job not found")

        if user is None or user.role == UserRole.CANDIDATE.value:
            if job.status != JobStatus.OPEN.value:
                # candidates can still see jobs they applied to via applications,
                # but public detail only shows open jobs
                if user is None:
                    raise NotFoundError("Job not found")
        return job

    def create(
        self,
        recruiter: User,
        payload: JobCreate,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Job:
        if recruiter.role != UserRole.RECRUITER.value and recruiter.role != UserRole.ADMIN.value:
            raise ForbiddenError("Only recruiters can create jobs")

        job = Job(
            recruiter_id=recruiter.id,
            title=payload.title,
            description=payload.description,
            requirements=payload.requirements,
            location=payload.location,
            employment_type=payload.employment_type.value,
            salary_range=payload.salary_range,
            status=JobStatus.OPEN.value,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        self.audit.log_event(
            event_type=SecurityEventType.JOB,
            action="job_created",
            success=True,
            user_id=recruiter.id,
            resource="job",
            resource_id=job.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"Created job '{job.title}'",
        )
        return job

    def update(
        self,
        job_id: UUID,
        user: User,
        payload: JobUpdate,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Job:
        job = self.get_job(job_id, user)
        if user.role != UserRole.ADMIN.value and job.recruiter_id != user.id:
            raise ForbiddenError("Not authorized to update this job")

        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            if hasattr(value, "value"):
                value = value.value
            setattr(job, key, value)

        self.db.commit()
        self.db.refresh(job)

        self.audit.log_event(
            event_type=SecurityEventType.JOB,
            action="job_updated",
            success=True,
            user_id=user.id,
            resource="job",
            resource_id=job.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details="Job updated",
        )
        return job

    def delete(
        self,
        job_id: UUID,
        user: User,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        job = self.get_job(job_id, user)
        if user.role != UserRole.ADMIN.value and job.recruiter_id != user.id:
            raise ForbiddenError("Not authorized to delete this job")

        self.db.delete(job)
        self.db.commit()
        self.audit.log_event(
            event_type=SecurityEventType.JOB,
            action="job_deleted",
            success=True,
            user_id=user.id,
            resource="job",
            resource_id=job_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details="Job deleted",
        )
