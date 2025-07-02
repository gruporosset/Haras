from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.types import CLOB

from .base import Base


class Terreno(Base):
    __tablename__ = "TERRENOS"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOME = Column(String(100), nullable=False)
    AREA_HECTARES = Column(Float, nullable=False)  # NUMBER(8,4)
    TIPO_SOLO = Column(String(50))
    TOPOGRAFIA = Column(String(50))
    TIPO_PASTAGEM = Column(String(100))
    CAPACIDADE_ANIMAIS = Column(Integer)  # NUMBER(3)
    LATITUDE = Column(Float, nullable=False)  # NUMBER(9,6)
    LONGITUDE = Column(Float, nullable=False)  # NUMBER(9,6)
    STATUS_TERRENO = Column(String(20), default="DISPONIVEL")
    OBSERVACOES = Column(CLOB)
    ID_USUARIO_CADASTRO = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    DATA_CADASTRO = Column(DateTime(timezone=True), server_default=func.now())
