import enum
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.types import CLOB
from .base import Base


class TipoCoberturaEnum(str, enum.Enum):
    NATURAL = "NATURAL"
    IA = "IA"  # Inseminação Artificial
    TE = "TE"  # Transferência de Embrião


class ResultadoDiagnosticoEnum(str, enum.Enum):
    POSITIVO = "POSITIVO"
    NEGATIVO = "NEGATIVO"
    PENDENTE = "PENDENTE"


class StatusReproducaoEnum(str, enum.Enum):
    ATIVO = "ATIVO"      # Gestação ativa
    CONCLUIDO = "CONCLUIDO"  # Parto realizado
    FALHADO = "FALHADO"    # Perdeu a gestação


class Reproducao(Base):
    __tablename__ = "REPRODUCAO"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_EGUA = Column(Integer, ForeignKey('ANIMAIS.ID'), nullable=False)
    ID_PARCEIRO = Column(Integer, ForeignKey('ANIMAIS.ID')
                         )  # Pode ser null para IA/TE
    TIPO_COBERTURA = Column(Enum(TipoCoberturaEnum), nullable=False)
    DATA_COBERTURA = Column(DateTime, nullable=False)
    DATA_DIAGNOSTICO = Column(DateTime)
    RESULTADO_DIAGNOSTICO = Column(
        Enum(ResultadoDiagnosticoEnum), default=ResultadoDiagnosticoEnum.PENDENTE)
    DATA_PARTO_PREVISTA = Column(DateTime)
    DATA_PARTO_REAL = Column(DateTime)
    OBSERVACOES = Column(CLOB)
    STATUS_REPRODUCAO = Column(
        Enum(StatusReproducaoEnum), default=StatusReproducaoEnum.ATIVO)
    ID_USUARIO_REGISTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_REGISTRO = Column(DateTime(timezone=True), server_default=func.now())
