import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.types import CLOB
from .base import Base


class SexoEnum(str, enum.Enum):
    M = "M"
    F = "F"


class StatusAnimalEnum(str, enum.Enum):
    ATIVO = "ATIVO"
    VENDIDO = "VENDIDO"
    MORTO = "MORTO"
    EMPRESTADO = "EMPRESTADO"


class Animal(Base):
    __tablename__ = "ANIMAIS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOME = Column(String(100), nullable=False)
    NUMERO_REGISTRO = Column(String(50), unique=True)
    CHIP_IDENTIFICACAO = Column(String(50), unique=True)
    SEXO = Column(Enum(SexoEnum))
    DATA_NASCIMENTO = Column(DateTime)
    PELAGEM = Column(String(50))
    STATUS_ANIMAL = Column(Enum(StatusAnimalEnum),
                           default=StatusAnimalEnum.ATIVO)
    ID_PAI = Column(Integer, ForeignKey('ANIMAIS.ID'))
    ID_MAE = Column(Integer, ForeignKey('ANIMAIS.ID'))
    ORIGEM = Column(String(100))
    PROPRIETARIO = Column(String(200))
    CONTATO_PROPRIETARIO = Column(String(200))
    CPF_CNPJ_PROPRIETARIO = Column(String(20))
    ID_USUARIO_CADASTRO = Column(
        Integer, ForeignKey('USUARIOS.ID'), nullable=False)
    DATA_CADASTRO = Column(DateTime(timezone=True), server_default=func.now())
    ID_USUARIO_ALTERACAO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_ALTERACAO = Column(DateTime(timezone=True), onupdate=func.now())
    OBSERVACOES = Column(CLOB)
    PESO_ATUAL = Column(Float)
    FOTO_PRINCIPAL = Column(String(500))
