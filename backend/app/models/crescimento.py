from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from .base import Base

Base = declarative_base()

class HistoricoCrescimento(Base):
    __tablename__ = "HISTORICO_CRESCIMENTO"
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_ANIMAL = Column(Integer, ForeignKey('ANIMAIS.ID'), nullable=False)
    DATA_MEDICAO = Column(DateTime, nullable=False)
    PESO = Column(Float)  # kg
    ALTURA = Column(Float)  # cm
    PERIMETRO_TORACICO = Column(Float)  # cm
    COMPRIMENTO_CORPO = Column(Float)  # cm
    DIAMETRO_CANELA = Column(Float)  # cm
    OBSERVACOES = Column(String(500))
    ID_USUARIO_REGISTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_REGISTRO = Column(DateTime(timezone=True), server_default=func.now())