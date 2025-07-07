# backend/app/schemas/ferrageamento.py
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_serializer, field_validator


class TipoFerrageamentoEnum(str, Enum):
    FERRAGEAMENTO = "FERRAGEAMENTO"
    CASQUEAMENTO = "CASQUEAMENTO"
    FERRAGEAMENTO_CORRETIVO = "FERRAGEAMENTO_CORRETIVO"
    CASQUEAMENTO_TERAPEUTICO = "CASQUEAMENTO_TERAPEUTICO"


class TipoFerraduraEnum(str, Enum):
    NORMAL = "NORMAL"
    CORRETIVA = "CORRETIVA"
    TERAPEUTICA = "TERAPEUTICA"
    ESPECIAL = "ESPECIAL"


class MembroTratadoEnum(str, Enum):
    AD = "AD"  # Anterior Direito
    AE = "AE"  # Anterior Esquerdo
    PD = "PD"  # Posterior Direito
    PE = "PE"  # Posterior Esquerdo
    TODOS = "TODOS"


class StatusCascoEnum(str, Enum):
    BOM = "BOM"
    REGULAR = "REGULAR"
    RUIM = "RUIM"
    PROBLEMA = "PROBLEMA"


# Base schema para ferrageamento
class FerrageamentoBase(BaseModel):
    ID_ANIMAL: int
    TIPO_FERRAGEAMENTO: TipoFerrageamentoEnum
    DATA_OCORRENCIA: datetime
    DESCRICAO: Optional[str] = Field(None, max_length=1000)

    # Campos específicos de ferrageamento
    TIPO_FERRADURA: Optional[TipoFerraduraEnum] = None
    MEMBRO_TRATADO: MembroTratadoEnum
    PROBLEMA_DETECTADO: Optional[str] = Field(None, max_length=500)
    TECNICA_APLICADA: Optional[str] = Field(None, max_length=200)
    FERRADOR_RESPONSAVEL: Optional[str] = Field(None, max_length=200)
    STATUS_CASCO: Optional[StatusCascoEnum] = None
    PROXIMA_AVALIACAO: Optional[datetime] = None

    # Financeiro
    CUSTO: Optional[float] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = None


class FerrageamentoCreate(FerrageamentoBase):
    @field_validator("DATA_OCORRENCIA")
    @classmethod
    def validate_data_ocorrencia(cls, v):
        if v > datetime.now():
            raise ValueError("Data de ocorrência não pode ser no futuro")
        return v

    @field_validator("PROXIMA_AVALIACAO")
    @classmethod
    def validate_proxima_avaliacao(cls, v, info):
        if v and hasattr(info, "data") and "DATA_OCORRENCIA" in info.data:
            if v <= info.data["DATA_OCORRENCIA"]:
                raise ValueError("Próxima avaliação deve ser após a data de ocorrência")
        return v


class FerrageamentoUpdate(BaseModel):
    TIPO_FERRAGEAMENTO: Optional[TipoFerrageamentoEnum] = None
    DATA_OCORRENCIA: Optional[datetime] = None
    DESCRICAO: Optional[str] = Field(None, max_length=1000)
    TIPO_FERRADURA: Optional[TipoFerraduraEnum] = None
    MEMBRO_TRATADO: Optional[MembroTratadoEnum] = None
    PROBLEMA_DETECTADO: Optional[str] = Field(None, max_length=500)
    TECNICA_APLICADA: Optional[str] = Field(None, max_length=200)
    FERRADOR_RESPONSAVEL: Optional[str] = Field(None, max_length=200)
    STATUS_CASCO: Optional[StatusCascoEnum] = None
    PROXIMA_AVALIACAO: Optional[datetime] = None
    CUSTO: Optional[float] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = None


class FerrageamentoResponse(FerrageamentoBase):
    ID: int
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    # Campos relacionados calculados
    animal_nome: Optional[str] = None
    dias_proxima_avaliacao: Optional[int] = None
    status_vencimento: Optional[str] = None  # EM_DIA, PROXIMO_VENCIMENTO, VENCIDO

    @field_serializer("DATA_OCORRENCIA", "PROXIMA_AVALIACAO", "DATA_REGISTRO")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None

    class Config:
        from_attributes = True


# Schema para aplicação rápida (mobile)
class FerrageamentoRapido(BaseModel):
    ID_ANIMAL: int
    TIPO_FERRAGEAMENTO: TipoFerrageamentoEnum
    MEMBRO_TRATADO: MembroTratadoEnum
    FERRADOR_RESPONSAVEL: Optional[str] = Field(None, max_length=200)
    STATUS_CASCO: Optional[StatusCascoEnum] = None
    CUSTO: Optional[float] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = None


# Schema para alertas de vencimento
class AlertaVencimento(BaseModel):
    animal_id: int
    animal_nome: str
    tipo_ferrageamento: str
    data_ultima: datetime
    proxima_avaliacao: datetime
    dias_vencimento: int
    ferrador_anterior: Optional[str] = None
    custo_estimado: Optional[float] = None

    @field_serializer("data_ultima", "proxima_avaliacao")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None


# Schema para estatísticas
class EstatisticasFerrageamento(BaseModel):
    total_registros: int
    registros_mes_atual: int
    custo_total_mes: float
    ferradores_ativos: int
    proximas_avaliacoes: int
    animais_atrasados: int

    # Breakdown por tipo
    total_ferrageamento: int
    total_casqueamento: int
    total_corretivo: int
    total_terapeutico: int


# Schema para relatórios
class RelatorioFerrageamento(BaseModel):
    animal_nome: str
    tipo_ferrageamento: str
    data_ocorrencia: datetime
    ferrador_responsavel: Optional[str] = None
    status_casco: Optional[str] = None
    proxima_avaliacao: Optional[datetime] = None
    custo: Optional[float] = None

    @field_serializer("data_ocorrencia", "proxima_avaliacao")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None


# Schema para estatísticas por ferrador
class FerradorEstatisticas(BaseModel):
    ferrador_nome: str
    total_atendimentos: int
    custo_total: float
    ultima_atividade: Optional[datetime] = None

    @field_serializer("ultima_atividade")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None
