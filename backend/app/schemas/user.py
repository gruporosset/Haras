import re
from datetime import datetime
from pydantic import BaseModel, validator, field_serializer
from typing import Optional
from enum import Enum

class Perfil(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    READONLY = "READONLY"

class UserBase(BaseModel):
    NOME_COMPLETO: str
    EMAIL: str
    PERFIL: Perfil = Perfil.USER

    @validator("EMAIL")
    def validate_email(cls, v):
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("E-mail inválido")
        return v

class UserCreate(UserBase):
    SENHA: str

class UserLogin(BaseModel):
    EMAIL: str
    SENHA: str
    @validator("EMAIL")
    def validate_email(cls, v):
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", v):
            raise ValueError("E-mail inválido")
        return v    

class UserForgotPassword(BaseModel):
    EMAIL: str
    @validator("EMAIL")
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

    @field_serializer('DATA_CADASTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None

    class Config:
        from_attributes = True
