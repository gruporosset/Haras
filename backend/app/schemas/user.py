import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_serializer, field_validator


class Perfil(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    READONLY = "READONLY"


class UserBase(BaseModel):
    NOME_COMPLETO: str
    EMAIL: str
    PERFIL: Perfil = Perfil.USER

    @field_validator("EMAIL")
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("E-mail inválido")
        return v


class UserCreate(UserBase):
    SENHA: str


class UserLogin(BaseModel):
    EMAIL: str
    SENHA: str

    @field_validator("EMAIL")
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("E-mail inválido")
        return v


class UserForgotPassword(BaseModel):
    EMAIL: str

    @field_validator("EMAIL")
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("E-mail inválido")
        return v


class UserResetPassword(BaseModel):
    TOKEN: str
    SENHA: str


class UserResponse(UserBase):
    ID: int
    DATA_CADASTRO: Optional[datetime] = None
    ATIVO: str
    DATA_ULTIMO_LOGIN: Optional[datetime] = None
    MFA_ATIVO: str

    @field_serializer("DATA_CADASTRO", "DATA_ULTIMO_LOGIN")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
    requires_mfa: bool
    user_id: int
