from fastapi import APIRouter, Request

from app.dependencies.auth import CurrentUser, DbSession
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserRead
from app.services.auth_service import AuthService
from app.utils.request import get_client_ip, get_user_agent


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, request: Request, db: DbSession) -> TokenResponse:
    user, token = AuthService(db).register(
        payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: DbSession) -> TokenResponse:
    user, token = AuthService(db).login(
        payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)


@router.post("/logout", response_model=MessageResponse)
def logout(request: Request, current_user: CurrentUser, db: DbSession) -> MessageResponse:
    AuthService(db).logout(
        current_user,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return MessageResponse(message="Logged out")
