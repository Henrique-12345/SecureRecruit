from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import ApplicationStatus, JobStatus, SecurityEventType, UserRole
from app.core.exceptions import AppError, ConflictError, ForbiddenError, NotFoundError
from app.models.application import Application
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationStatusUpdate
from app.services.audit_service import AuditService


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def apply(
        self,
        *,
        candidate: User,
        job_id: UUID,
        payload: ApplicationCreate,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Application:
        if candidate.role != UserRole.CANDIDATE.value:
            raise ForbiddenError("Only candidates can apply to jobs")

        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise NotFoundError("Job not found")
        if job.status != JobStatus.OPEN.value:
            raise AppError("Job is not open for applications", status_code=400)

        resume = (
            self.db.query(Resume)
            .filter(Resume.id == payload.resume_id, Resume.candidate_id == candidate.id)
            .first()
        )
        if not resume:
            raise NotFoundError("Resume not found for this candidate")

        existing = (
            self.db.query(Application)
            .filter(Application.candidate_id == candidate.id, Application.job_id == job_id)
            .first()
        )
        if existing:
            raise ConflictError("Already applied to this job")

        application = Application(
            candidate_id=candidate.id,
            job_id=job_id,
            resume_id=resume.id,
            status=ApplicationStatus.SUBMITTED.value,
        )
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)

        self.audit.log_event(
            event_type=SecurityEventType.APPLICATION,
            action="application_created",
            success=True,
            user_id=candidate.id,
            resource="application",
            resource_id=application.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"Applied to job={job_id}",
        )
        return application

    def list_mine(self, user: User) -> list[Application]:
        return (
            self.db.query(Application)
            .filter(Application.candidate_id == user.id)
            .order_by(Application.applied_at.desc())
            .all()
        )

    def list_for_job(self, job_id: UUID, user: User) -> list[Application]:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise NotFoundError("Job not found")

        if user.role == UserRole.ADMIN.value:
            pass
        elif user.role == UserRole.RECRUITER.value and job.recruiter_id == user.id:
            pass
        else:
            raise ForbiddenError("Not authorized to view applications for this job")

        return (
            self.db.query(Application)
            .filter(Application.job_id == job_id)
            .order_by(Application.applied_at.desc())
            .all()
        )

    def get_authorized(self, application_id: UUID, user: User) -> Application:
        application = (
            self.db.query(Application).filter(Application.id == application_id).first()
        )
        if not application:
            raise NotFoundError("Application not found")

        if user.role == UserRole.ADMIN.value:
            return application
        if user.role == UserRole.CANDIDATE.value and application.candidate_id == user.id:
            return application
        if user.role == UserRole.RECRUITER.value:
            job = self.db.query(Job).filter(Job.id == application.job_id).first()
            if job and job.recruiter_id == user.id:
                return application

        raise ForbiddenError("Not authorized to access this application")

    def update_status(
        self,
        application_id: UUID,
        user: User,
        payload: ApplicationStatusUpdate,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Application:
        application = self.get_authorized(application_id, user)
        if user.role == UserRole.CANDIDATE.value:
            raise ForbiddenError("Candidates cannot change application status")

        if user.role == UserRole.RECRUITER.value:
            job = self.db.query(Job).filter(Job.id == application.job_id).first()
            if not job or job.recruiter_id != user.id:
                raise ForbiddenError("Not authorized to update this application")

        application.status = payload.status.value
        self.db.commit()
        self.db.refresh(application)

        self.audit.log_event(
            event_type=SecurityEventType.APPLICATION,
            action="application_status_updated",
            success=True,
            user_id=user.id,
            resource="application",
            resource_id=application.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"Status changed to {application.status}",
        )
        return application

    def list_all(self) -> list[Application]:
        return self.db.query(Application).order_by(Application.applied_at.desc()).all()
