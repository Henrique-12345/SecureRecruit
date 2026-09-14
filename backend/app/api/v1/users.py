from fastapi import APIRouter, Request

from app.core.enums import SecurityEventType
from app.dependencies.auth import CurrentUser, DbSession
from app.schemas.user import UserRead, UserUpdate
from app.services.audit_service import AuditService
from app.utils.request import get_client_ip, get_user_agent


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.put("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    request: Request,
    current_user: CurrentUser,
    db: DbSession,
) -> UserRead:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)

    AuditService(db).log_event(
        event_type=SecurityEventType.USER,
        action="profile_updated",
        success=True,
        user_id=current_user.id,
        resource="user",
        resource_id=current_user.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details="User profile fields updated",
    )
    return UserRead.model_validate(current_user)
