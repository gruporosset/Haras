# backend/app/models/crescimento.py
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.types import CLOB

from .base import Base


class HistoricoCrescimento(Base):
    __tablename__ = "HISTORICO_CRESCIMENTO"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_ANIMAL = Column(Integer, ForeignKey("ANIMAIS.ID"), nullable=False)
    DATA_MEDICAO = Column(DateTime, nullable=False)
    PESO = Column(Float)  # kg
    ALTURA = Column(Float)  # cm
    CIRCUNFERENCIA_CANELA = Column(Float)  # cm
    CIRCUNFERENCIA_TORACICA = Column(Float)  # cm
    COMPRIMENTO_CORPO = Column(Float)  # cm
    OBSERVACOES = Column(CLOB)
    ID_USUARIO_REGISTRO = Column(Integer, ForeignKey("USUARIOS.ID"))
    DATA_REGISTRO = Column(DateTime(timezone=True), server_default=func.now())
