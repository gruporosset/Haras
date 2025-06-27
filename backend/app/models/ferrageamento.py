# backend/app/models/ferrageamento.py
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.types import CLOB
from .base import Base


class TipoFerrageamentoEnum(str, enum.Enum):
    FERRAGEAMENTO = "FERRAGEAMENTO"
    CASQUEAMENTO = "CASQUEAMENTO"
    FERRAGEAMENTO_CORRETIVO = "FERRAGEAMENTO_CORRETIVO"
    CASQUEAMENTO_TERAPEUTICO = "CASQUEAMENTO_TERAPEUTICO"


class TipoFerraduraEnum(str, enum.Enum):
    COMUM = "Comum"
    ORTOPEDICA = "Ortopédica"
    ALUMINIO = "Alumínio"
    BORRACHA = "Borracha"
    COLAGEM = "Colagem"
    DESCALCO = "Descalço"


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


class StatusVencimentoEnum(str, enum.Enum):
    SEM_AGENDAMENTO = "SEM_AGENDAMENTO"
    VENCIDO = "VENCIDO"
    VENCE_SEMANA = "VENCE_SEMANA"
    VENCE_QUINZENA = "VENCE_QUINZENA"
    EM_DIA = "EM_DIA"


# Extender o modelo SaudeAnimais existente com os novos campos
# Note: Esta é uma extensão conceitual - na prática, os campos já foram adicionados via ALTER TABLE

class FerrageamentoResumo(Base):
    """View para relatórios de ferrageamento"""
    __tablename__ = "VW_FERRAGEAMENTO_RESUMO"

    ANIMAL_ID = Column("ANIMAL_ID", Integer, primary_key=True)
    ANIMAL_NOME = Column("ANIMAL_NOME", String(100))
    NUMERO_REGISTRO = Column("NUMERO_REGISTRO", String(50))
    REGISTRO_ID = Column("REGISTRO_ID", Integer)
    TIPO_REGISTRO = Column("TIPO_REGISTRO", Enum(TipoFerrageamentoEnum))
    DATA_OCORRENCIA = Column("DATA_OCORRENCIA", DateTime)
    TIPO_FERRADURA = Column("TIPO_FERRADURA", String(100))
    MEMBRO_TRATADO = Column("MEMBRO_TRATADO", Enum(MembroTratadoEnum))
    PROBLEMA_DETECTADO = Column("PROBLEMA_DETECTADO", String(500))
    FERRADOR_RESPONSAVEL = Column("FERRADOR_RESPONSAVEL", String(200))
    STATUS_CASCO = Column("STATUS_CASCO", Enum(StatusCascoEnum))
    PROXIMA_AVALIACAO = Column("PROXIMA_AVALIACAO", DateTime)
    CUSTO = Column("CUSTO", Float)
    OBSERVACOES = Column("OBSERVACOES", CLOB)
    DIAS_PROXIMA_AVALIACAO = Column("DIAS_PROXIMA_AVALIACAO", Integer)
    STATUS_VENCIMENTO = Column("STATUS_VENCIMENTO", Enum(StatusVencimentoEnum))


# Mixin para adicionar aos campos de SaudeAnimais
class FerrageamentoMixin:
    """Mixin com campos específicos de ferrageamento para SaudeAnimais"""

    TIPO_FERRADURA = Column(String(100))
    MEMBRO_TRATADO = Column(Enum(MembroTratadoEnum))
    PROBLEMA_DETECTADO = Column(String(500))
    TECNICA_APLICADA = Column(String(200))
    FERRADOR_RESPONSAVEL = Column(String(200))
    STATUS_CASCO = Column(Enum(StatusCascoEnum))
    PROXIMA_AVALIACAO = Column(DateTime)

    def calcular_dias_vencimento(self):
        """Calcula dias até vencimento da próxima avaliação"""
        if not self.PROXIMA_AVALIACAO:
            return None

        from datetime import datetime
        delta = self.PROXIMA_AVALIACAO - datetime.now()
        return delta.days

    def get_status_vencimento(self):
        """Retorna status do vencimento"""
        if not self.PROXIMA_AVALIACAO:
            return StatusVencimentoEnum.SEM_AGENDAMENTO

        dias = self.calcular_dias_vencimento()

        if dias < 0:
            return StatusVencimentoEnum.VENCIDO
        elif dias <= 7:
            return StatusVencimentoEnum.VENCE_SEMANA
        elif dias <= 15:
            return StatusVencimentoEnum.VENCE_QUINZENA
        else:
            return StatusVencimentoEnum.EM_DIA

    def calcular_proxima_data(self, modalidade="GERAL"):
        """Calcula próxima data baseada no tipo e modalidade"""
        from datetime import datetime, timedelta

        intervalos = {
            "FERRAGEAMENTO": {
                "CCE": 30,
                "APARTACAO": 60,
                "CORRIDA": 35,
                "GERAL": 45
            },
            "CASQUEAMENTO": {
                "GERAL": 40
            },
            "FERRAGEAMENTO_CORRETIVO": {
                "GERAL": 21
            },
            "CASQUEAMENTO_TERAPEUTICO": {
                "GERAL": 21
            }
        }

        tipo_str = str(self.TIPO_REGISTRO) if hasattr(
            self, 'TIPO_REGISTRO') else "FERRAGEAMENTO"
        dias = intervalos.get(tipo_str, {}).get(modalidade, 45)

        data_base = self.DATA_OCORRENCIA if hasattr(
            self, 'DATA_OCORRENCIA') else datetime.now()
        return data_base + timedelta(days=dias)
