from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import UserRole
from app.utils.masking import mask_cpf, mask_phone


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    cpf: Optional[str] = Field(default=None, max_length=14)
    phone: Optional[str] = Field(default=None, max_length=20)
    birth_date: Optional[date] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.CANDIDATE


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    birth_date: Optional[date] = None
    cpf: Optional[str] = Field(default=None, max_length=14)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserAdminRead(BaseModel):
    """Visão administrativa de usuário com PII minimizada (R5 / LGPD art. 6º, III).

    O admin gerencia contas (ativar/desativar) e não precisa do CPF, telefone ou
    data de nascimento completos. Construir sempre via `from_user`, que aplica o
    mascaramento na origem: `mask_phone` não é idempotente, então mascarar em um
    serializer quebraria quando o FastAPI revalida o `response_model`.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    cpf: Optional[str] = None
    phone: Optional[str] = None
    # Data de nascimento reduzida ao ano: suficiente para contexto administrativo
    # (ex.: conferir maioridade aproximada) sem expor o dado completo, que combinado
    # com nome/CPF facilita identificação e fraude.
    birth_year: Optional[int] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_user(cls, user: Any) -> "UserAdminRead":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            cpf=mask_cpf(user.cpf),
            phone=mask_phone(user.phone),
            birth_year=user.birth_date.year if user.birth_date else None,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UserStatusUpdate(BaseModel):
    is_active: bool
