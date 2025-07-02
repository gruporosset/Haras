import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from .base import Base


class Perfil(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    READONLY = "READONLY"


class User(Base):
    __tablename__ = "USUARIOS"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOME_COMPLETO = Column(String(200), nullable=False)
    EMAIL = Column(String(100), unique=True, nullable=False)
    SENHA_HASH = Column(String(500))
    SALT = Column(String(100))
    DATA_CADASTRO = Column(DateTime(timezone=True), server_default=func.now())
    DATA_ULTIMO_LOGIN = Column(DateTime)
    TOKEN_CADASTRO = Column(String(500))
    TOKEN_CADASTRO_EXPIRA = Column(DateTime)
    RESET_PASSWORD_TOKEN = Column(String(500))
    RESET_TOKEN_EXPIRA = Column(DateTime)
    TENTATIVAS_LOGIN = Column(Integer, default=0)
    BLOQUEADO_ATE = Column(DateTime)
    PERFIL = Column(Enum(Perfil), default=Perfil.USER)
    PRIMEIRO_ACESSO = Column(String, default="N")
    ATIVO = Column(String, default="S")
    MFA_ATIVO = Column(String, default="N")
