import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.types import CLOB
from .base import Base


class TipoRegistroEnum(str, enum.Enum):
    VACINA = "VACINA"
    VERMIFUGO = "VERMIFUGO"
    MEDICAMENTO = "MEDICAMENTO"
    EXAME = "EXAME"
    CONSULTA = "CONSULTA"
    CIRURGIA = "CIRURGIA"
    TRATAMENTO = "TRATAMENTO"


class SaudeAnimais(Base):
    __tablename__ = "SAUDE_ANIMAIS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_ANIMAL = Column(Integer, ForeignKey('ANIMAIS.ID'), nullable=False)
    TIPO_REGISTRO = Column(Enum(TipoRegistroEnum), nullable=False)
    DATA_OCORRENCIA = Column(DateTime, nullable=False)
    DESCRICAO = Column(String(1000))
    VETERINARIO_RESPONSAVEL = Column(String(200))
    MEDICAMENTO_APLICADO = Column(String(500))  # Mantido para compatibilidade
    DOSE_APLICADA = Column(String(100))  # Mantido para compatibilidade
    PROXIMA_APLICACAO = Column(DateTime)  # Para reforços
    CUSTO = Column(Float)
    OBSERVACOES = Column(CLOB)

    # Campos para integração com medicamentos (se estiver no estoque)
    ID_MEDICAMENTO = Column(Integer, ForeignKey('MEDICAMENTOS.ID'))
    QUANTIDADE_APLICADA = Column(Float)
    UNIDADE_APLICADA = Column(String(20))

    ID_USUARIO_REGISTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_REGISTRO = Column(DateTime(timezone=True), server_default=func.now())
