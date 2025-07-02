# backend/app/models/saude.py
import enum

from app.models.base import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.types import CLOB


class TipoRegistroEnum(str, enum.Enum):
    VACINA = "VACINA"
    VERMIFUGO = "VERMIFUGO"
    MEDICAMENTO = "MEDICAMENTO"
    EXAME = "EXAME"
    CONSULTA = "CONSULTA"
    CIRURGIA = "CIRURGIA"
    TRATAMENTO = "TRATAMENTO"
    # Tipos de ferrageamento
    FERRAGEAMENTO = "FERRAGEAMENTO"
    CASQUEAMENTO = "CASQUEAMENTO"
    FERRAGEAMENTO_CORRETIVO = "FERRAGEAMENTO_CORRETIVO"
    CASQUEAMENTO_TERAPEUTICO = "CASQUEAMENTO_TERAPEUTICO"


class SaudeAnimais(Base):
    __tablename__ = "SAUDE_ANIMAIS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_ANIMAL = Column(Integer, ForeignKey("ANIMAIS.ID"), nullable=False)
    # Mudado para String para suportar novos tipos
    TIPO_REGISTRO = Column(String(50), nullable=False)
    DATA_OCORRENCIA = Column(DateTime, nullable=False)
    DESCRICAO = Column(String(1000))
    VETERINARIO_RESPONSAVEL = Column(String(200))
    MEDICAMENTO_APLICADO = Column(String(500))  # Mantido para compatibilidade
    DOSE_APLICADA = Column(String(100))  # Mantido para compatibilidade
    PROXIMA_APLICACAO = Column(DateTime)  # Para reforços
    CUSTO = Column(Float)
    OBSERVACOES = Column(CLOB)

    # Campos para integração com medicamentos (se estiver no estoque)
    ID_MEDICAMENTO = Column(Integer, ForeignKey("MEDICAMENTOS.ID"))
    QUANTIDADE_APLICADA = Column(Float)
    UNIDADE_APLICADA = Column(String(20))

    # Campos específicos de ferrageamento (adicionados via ALTER TABLE)
    TIPO_FERRADURA = Column(String(100))
    MEMBRO_TRATADO = Column(String(50))
    PROBLEMA_DETECTADO = Column(String(500))
    TECNICA_APLICADA = Column(String(200))
    FERRADOR_RESPONSAVEL = Column(String(200))
    STATUS_CASCO = Column(String(100))
    PROXIMA_AVALIACAO = Column(DateTime)

    ID_USUARIO_REGISTRO = Column(Integer, ForeignKey("USUARIOS.ID"))
    DATA_REGISTRO = Column(DateTime(timezone=True), server_default=func.now())
