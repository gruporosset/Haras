from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base  

# Base = declarative_base()

class MFAConfig(Base):
    __tablename__ = "CONFIG_MFA"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_USUARIO = Column(Integer, ForeignKey('USUARIOS.ID'), nullable=False)
    SEGREDO_TOTP = Column(String(100), nullable=False)
    ATIVO = Column(String, default='S')
    DATA_CADASTRO = Column(DateTime, server_default=func.now())