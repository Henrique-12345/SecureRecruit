import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import SecurityEventType, UserRole
from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.models.resume import Resume
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.hash_service import calculate_file_hash, verify_file_integrity


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class ResumeService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)
        self.upload_dir = Path(settings.UPLOAD_DIRECTORY)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _validate_file(self, file: UploadFile, content: bytes) -> None:
        if file.content_type not in settings.allowed_file_types_list:
            raise AppError("Unsupported file type", status_code=400)

        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise AppError("Unsupported file extension", status_code=400)

        if len(content) == 0:
            raise AppError("Empty file", status_code=400)

        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise AppError("File exceeds maximum upload size", status_code=400)

    def upload(
        self,
        *,
        candidate: User,
        file: UploadFile,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Resume:
        if candidate.role != UserRole.CANDIDATE.value:
            raise ForbiddenError("Only candidates can upload resumes")

        content = file.file.read()
        self._validate_file(file, content)

        original = Path(file.filename or "resume").name
        suffix = Path(original).suffix.lower()
        stored_name = f"{uuid.uuid4().hex}{suffix}"
        destination = self.upload_dir / stored_name
        destination.write_bytes(content)

        file_hash = calculate_file_hash(content)

        resume = Resume(
            candidate_id=candidate.id,
            original_filename=original,
            stored_filename=stored_name,
            file_path=str(destination),
            content_type=file.content_type or "application/octet-stream",
            file_size=len(content),
            sha256_hash=file_hash,
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)

        self.audit.log_event(
            event_type=SecurityEventType.RESUME,
            action="resume_upload",
            success=True,
            user_id=candidate.id,
            resource="resume",
            resource_id=resume.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"Uploaded {original} size={len(content)} hash={file_hash[:12]}...",
        )
        return resume

    def list_for_user(self, user: User) -> list[Resume]:
        if user.role == UserRole.ADMIN.value:
            return self.db.query(Resume).order_by(Resume.uploaded_at.desc()).all()
        return (
            self.db.query(Resume)
            .filter(Resume.candidate_id == user.id)
            .order_by(Resume.uploaded_at.desc())
            .all()
        )

    def get_authorized(self, resume_id: uuid.UUID, user: User) -> Resume:
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise NotFoundError("Resume not found")

        if user.role == UserRole.ADMIN.value:
            return resume
        if user.role == UserRole.CANDIDATE.value and resume.candidate_id == user.id:
            return resume
        if user.role == UserRole.RECRUITER.value:
            from app.models.application import Application
            from app.models.job import Job

            linked = (
                self.db.query(Application)
                .join(Job, Job.id == Application.job_id)
                .filter(
                    Application.resume_id == resume.id,
                    Job.recruiter_id == user.id,
                )
                .first()
            )
            if linked:
                return resume

        raise ForbiddenError("Not authorized to access this resume")

    def delete(
        self,
        resume_id: uuid.UUID,
        user: User,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        resume = self.get_authorized(resume_id, user)
        if user.role != UserRole.ADMIN.value and resume.candidate_id != user.id:
            raise ForbiddenError("Only the owner can delete this resume")

        path = Path(resume.file_path)
        self.db.delete(resume)
        self.db.commit()
        if path.exists():
            path.unlink()

        self.audit.log_event(
            event_type=SecurityEventType.RESUME,
            action="resume_delete",
            success=True,
            user_id=user.id,
            resource="resume",
            resource_id=resume_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details="Resume deleted",
        )

    def check_integrity(self, resume_id: uuid.UUID) -> dict:
        resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise NotFoundError("Resume not found")

        path = Path(resume.file_path)
        if not path.exists():
            return {
                "resume_id": resume.id,
                "stored_hash": resume.sha256_hash,
                "current_hash": "",
                "integrity_ok": False,
                "message": "File missing on disk",
            }

        current_hash, ok = verify_file_integrity(path, resume.sha256_hash)
        return {
            "resume_id": resume.id,
            "stored_hash": resume.sha256_hash,
            "current_hash": current_hash,
            "integrity_ok": ok,
            "message": "Integrity verified" if ok else "Hash mismatch detected",
        }
