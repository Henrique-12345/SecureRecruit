from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import UserRole


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


class UserAdminRead(UserRead):
    pass


class UserStatusUpdate(BaseModel):
    is_active: bool
