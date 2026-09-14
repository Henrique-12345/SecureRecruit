from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import SecurityEventType, UserRole
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User
from app.services.audit_service import AuditService
from app.utils.request import get_client_ip, get_user_agent


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Authentication required")

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError, TypeError):
        AuditService(db).log_event(
            event_type=SecurityEventType.ACCESS,
            action="invalid_token",
            success=False,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details="Invalid JWT presented",
        )
        raise UnauthorizedError("Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise ForbiddenError("Account is inactive")
    return user


def get_optional_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User | None:
    if credentials is None:
        return None
    try:
        return get_current_user(request, credentials, db)
    except (UnauthorizedError, ForbiddenError):
        return None


def require_roles(*roles: UserRole) -> Callable:
    allowed = {role.value for role in roles}

    def dependency(
        request: Request,
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)],
    ) -> User:
        if user.role not in allowed:
            AuditService(db).log_event(
                event_type=SecurityEventType.ACCESS,
                action="access_denied",
                success=False,
                user_id=user.id,
                resource=str(request.url.path),
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                details=f"Required roles={sorted(allowed)} actual={user.role}",
            )
            raise ForbiddenError("Insufficient permissions")
        return user

    return dependency


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
DbSession = Annotated[Session, Depends(get_db)]
CandidateUser = Annotated[User, Depends(require_roles(UserRole.CANDIDATE))]
RecruiterUser = Annotated[User, Depends(require_roles(UserRole.RECRUITER, UserRole.ADMIN))]
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
