from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from .base import Base

# Base = declarative_base()


class Sessao(Base):
    __tablename__ = "SESSOES"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_USUARIO = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    TOKEN_SESSAO = Column(String(500), unique=True, nullable=False)
    IP_ORIGEM = Column(String(45))
    USER_AGENT = Column(String(500))
    DATA_CRIACAO = Column(DateTime, server_default=func.now())
    DATA_EXPIRACAO = Column(DateTime, nullable=False)
    ATIVA = Column(String(1), default="S")
    DATA_ULTIMO_ACESSO = Column(DateTime, server_default=func.now())
