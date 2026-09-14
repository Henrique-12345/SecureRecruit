from uuid import UUID

from fastapi import APIRouter, Request

from app.core.enums import SecurityEventType, UserRole
from app.core.exceptions import ForbiddenError, NotFoundError
from app.dependencies.auth import CurrentUser, DbSession
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.schemas.candidate import (
    CandidateProfileRead,
    CandidateProfileUpdate,
    CandidatePublicRead,
)
from app.services.audit_service import AuditService
from app.utils.request import get_client_ip, get_user_agent


router = APIRouter(prefix="/candidates", tags=["candidates"])


def _get_or_create_profile(db, user: User) -> CandidateProfile:
    profile = (
        db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    )
    if not profile:
        profile = CandidateProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/me", response_model=CandidateProfileRead)
def get_my_profile(current_user: CurrentUser, db: DbSession) -> CandidateProfileRead:
    if current_user.role != UserRole.CANDIDATE.value:
        raise ForbiddenError("Only candidates have candidate profiles")
    profile = _get_or_create_profile(db, current_user)
    return CandidateProfileRead.model_validate(profile)


@router.put("/me", response_model=CandidateProfileRead)
def update_my_profile(
    payload: CandidateProfileUpdate,
    request: Request,
    current_user: CurrentUser,
    db: DbSession,
) -> CandidateProfileRead:
    if current_user.role != UserRole.CANDIDATE.value:
        raise ForbiddenError("Only candidates can update candidate profiles")

    profile = _get_or_create_profile(db, current_user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)

    AuditService(db).log_event(
        event_type=SecurityEventType.PROFILE,
        action="candidate_profile_updated",
        success=True,
        user_id=current_user.id,
        resource="candidate_profile",
        resource_id=profile.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details="Candidate profile updated",
    )
    return CandidateProfileRead.model_validate(profile)


@router.get("/{candidate_id}", response_model=CandidatePublicRead)
def get_candidate(
    candidate_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> CandidatePublicRead:
    user = db.query(User).filter(User.id == candidate_id).first()
    if not user or user.role != UserRole.CANDIDATE.value:
        raise NotFoundError("Candidate not found")

    if current_user.role == UserRole.CANDIDATE.value and current_user.id != user.id:
        raise ForbiddenError("Not authorized to view this candidate")

    if current_user.role == UserRole.RECRUITER.value:
        from app.models.application import Application
        from app.models.job import Job

        linked = (
            db.query(Application)
            .join(Job, Job.id == Application.job_id)
            .filter(
                Application.candidate_id == user.id,
                Job.recruiter_id == current_user.id,
            )
            .first()
        )
        if not linked:
            raise ForbiddenError("Not authorized to view this candidate")

    profile = _get_or_create_profile(db, user)
    return CandidatePublicRead(
        user_id=user.id,
        name=user.name,
        email=user.email,
        professional_summary=profile.professional_summary,
        education=profile.education,
        skills=profile.skills,
        experience=profile.experience,
        city=profile.city,
        state=profile.state,
        linkedin_url=profile.linkedin_url,
    )
