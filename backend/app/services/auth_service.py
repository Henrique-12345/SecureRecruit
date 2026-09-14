from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import SecurityEventType, UserRole
from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.audit_service import AuditService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)

    def register(
        self,
        payload: RegisterRequest,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, str]:
        if payload.role == UserRole.ADMIN:
            raise ForbiddenError("Admin accounts cannot be self-registered")

        existing = self.db.query(User).filter(User.email == payload.email.lower()).first()
        if existing:
            raise ConflictError("Email already registered")

        if payload.cpf:
            cpf_exists = self.db.query(User).filter(User.cpf == payload.cpf).first()
            if cpf_exists:
                raise ConflictError("CPF already registered")

        user = User(
            name=payload.name,
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            role=payload.role.value,
            cpf=payload.cpf,
            phone=payload.phone,
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()

        if user.role == UserRole.CANDIDATE.value:
            profile = CandidateProfile(user_id=user.id)
            self.db.add(profile)

        self.db.commit()
        self.db.refresh(user)

        self.audit.log_event(
            event_type=SecurityEventType.AUTH,
            action="user_created",
            success=True,
            user_id=user.id,
            resource="user",
            resource_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"Registered role={user.role} email={user.email}",
        )

        token = create_access_token(subject=user.id, role=user.role)
        return user, token

    def login(
        self,
        payload: LoginRequest,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, str]:
        user = self.db.query(User).filter(User.email == payload.email.lower()).first()
        if not user or not verify_password(payload.password, user.password_hash):
            self.audit.log_event(
                event_type=SecurityEventType.AUTH,
                action="login_failed",
                success=False,
                resource="auth",
                ip_address=ip_address,
                user_agent=user_agent,
                details=f"Failed login for email={payload.email.lower()}",
            )
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            self.audit.log_event(
                event_type=SecurityEventType.AUTH,
                action="login_failed",
                success=False,
                user_id=user.id,
                resource="auth",
                ip_address=ip_address,
                user_agent=user_agent,
                details="Inactive account",
            )
            raise ForbiddenError("Account is inactive")

        self.audit.log_event(
            event_type=SecurityEventType.AUTH,
            action="login_success",
            success=True,
            user_id=user.id,
            resource="auth",
            resource_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details="Login successful",
        )
        token = create_access_token(subject=user.id, role=user.role)
        return user, token

    def logout(
        self,
        user: User,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        self.audit.log_event(
            event_type=SecurityEventType.AUTH,
            action="logout",
            success=True,
            user_id=user.id,
            resource="auth",
            resource_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details="Logout",
        )

    def get_user_by_id(self, user_id: UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
