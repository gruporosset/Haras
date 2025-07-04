import enum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.types import CLOB

from .base import Base


class TipoFerrageamentoEnum(str, enum.Enum):
    FERRAGEAMENTO = "FERRAGEAMENTO"
    CASQUEAMENTO = "CASQUEAMENTO"
    FERRAGEAMENTO_CORRETIVO = "FERRAGEAMENTO_CORRETIVO"
    CASQUEAMENTO_TERAPEUTICO = "CASQUEAMENTO_TERAPEUTICO"


class MembroTratadoEnum(str, enum.Enum):
    AD = "AD"  # Anterior Direito
    AE = "AE"  # Anterior Esquerdo
    PD = "PD"  # Posterior Direito
    PE = "PE"  # Posterior Esquerdo
    TODOS = "TODOS"


class StatusCascoEnum(str, enum.Enum):
    BOM = "BOM"
    REGULAR = "REGULAR"
    RUIM = "RUIM"
    PROBLEMA = "PROBLEMA"


class FerrageamentoAnimais(Base):
    __tablename__ = "FERRAGEAMENTO_ANIMAIS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_ANIMAL = Column(Integer, ForeignKey("ANIMAIS.ID"), nullable=False)
    TIPO_FERRAGEAMENTO = Column(String(30), nullable=False)
    DATA_OCORRENCIA = Column(DateTime, nullable=False)
    DESCRICAO = Column(String(1000))

    # Campos específicos de ferrageamento
    TIPO_FERRADURA = Column(String(100))
    MEMBRO_TRATADO = Column(String(50))
    PROBLEMA_DETECTADO = Column(String(500))
    TECNICA_APLICADA = Column(String(200))
    FERRADOR_RESPONSAVEL = Column(String(200))
    STATUS_CASCO = Column(String(100))
    PROXIMA_AVALIACAO = Column(DateTime)

    # Campos financeiros e administrativos
    CUSTO = Column(Float)
    OBSERVACOES = Column(CLOB)
    ID_USUARIO_REGISTRO = Column(Integer, ForeignKey("USUARIOS.ID"))
    DATA_REGISTRO = Column(DateTime(timezone=True), server_default=func.now())


# Classe para compatibilidade com o código existente
# Mantém as mesmas funcionalidades que estavam no modelo SaudeAnimais
class FerrageamentoMixin:
    """Mixin para manter funcionalidades específicas de ferrageamento"""

    @property
    def dias_proxima_avaliacao(self):
        """Calcula dias até próxima avaliação"""
        if not self.PROXIMA_AVALIACAO:
            return None

        from datetime import datetime

        delta = self.PROXIMA_AVALIACAO.date() - datetime.now().date()
        return delta.days

    @property
    def status_avaliacao(self):
        """Status da avaliação baseado na proximidade da data"""
        if not self.PROXIMA_AVALIACAO:
            return "SEM_AGENDAMENTO"

        dias = self.dias_proxima_avaliacao
        if dias is None:
            return "SEM_AGENDAMENTO"
        elif dias < 0:
            return "ATRASADO"
        elif dias <= 7:
            return "URGENTE"
        elif dias <= 15:
            return "PROXIMO"
        else:
            return "OK"


# Classe de resumo para relatórios (mantém compatibilidade)
class FerrageamentoResumo:
    """Classe para resumos e estatísticas de ferrageamento"""

    def __init__(self, tipo_ferrageamento, total_registros, custo_total=None):
        self.tipo_ferrageamento = tipo_ferrageamento
        self.total_registros = total_registros
        self.custo_total = custo_total or 0.0

    def to_dict(self):
        return {
            "tipo_ferrageamento": self.tipo_ferrageamento,
            "total_registros": self.total_registros,
            "custo_total": self.custo_total,
        }
