from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_serializer, field_validator


class TipoRegistroEnum(str, Enum):
    """Enum apenas para tipos de saúde - removidos os tipos de ferrageamento"""

    VACINA = "VACINA"
    VERMIFUGO = "VERMIFUGO"
    MEDICAMENTO = "MEDICAMENTO"
    EXAME = "EXAME"
    CONSULTA = "CONSULTA"
    CIRURGIA = "CIRURGIA"
    TRATAMENTO = "TRATAMENTO"


class SaudeBase(BaseModel):
    ID_ANIMAL: int
    TIPO_REGISTRO: TipoRegistroEnum
    DATA_OCORRENCIA: datetime
    DESCRICAO: Optional[str] = Field(None, max_length=1000)
    VETERINARIO_RESPONSAVEL: Optional[str] = Field(None, max_length=200)
    MEDICAMENTO_APLICADO: Optional[str] = Field(None, max_length=500)
    DOSE_APLICADA: Optional[str] = Field(None, max_length=100)
    PROXIMA_APLICACAO: Optional[datetime] = None
    CUSTO: Optional[float] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = None

    # Campos para medicamentos do estoque
    ID_MEDICAMENTO: Optional[int] = None
    QUANTIDADE_APLICADA: Optional[float] = Field(None, gt=0)
    UNIDADE_APLICADA: Optional[str] = Field(None, max_length=20)


class SaudeCreate(SaudeBase):
    @field_validator("DATA_OCORRENCIA")
    @classmethod
    def validate_data_ocorrencia(cls, v):
        if v > datetime.now():
            raise ValueError("Data de ocorrência não pode ser no futuro")
        return v

    @field_validator("PROXIMA_APLICACAO")
    @classmethod
    def validate_proxima_aplicacao(cls, v, info):
        if v and hasattr(info, "data") and "DATA_OCORRENCIA" in info.data:
            if v <= info.data["DATA_OCORRENCIA"]:
                raise ValueError("Próxima aplicação deve ser após a data de ocorrência")
        return v

    @field_validator("QUANTIDADE_APLICADA")
    @classmethod
    def validate_quantidade_medicamento(cls, v, info):
        # Se informou medicamento do estoque, deve informar quantidade
        if hasattr(info, "data") and "ID_MEDICAMENTO" in info.data:
            if info.data["ID_MEDICAMENTO"] and not v:
                raise ValueError(
                    "Quantidade deve ser informada quando medicamento do estoque "
                    "é selecionado"
                )
        return v


class SaudeUpdate(BaseModel):
    TIPO_REGISTRO: Optional[TipoRegistroEnum] = None
    DATA_OCORRENCIA: Optional[datetime] = None
    DESCRICAO: Optional[str] = Field(None, max_length=1000)
    VETERINARIO_RESPONSAVEL: Optional[str] = Field(None, max_length=200)
    MEDICAMENTO_APLICADO: Optional[str] = Field(None, max_length=500)
    DOSE_APLICADA: Optional[str] = Field(None, max_length=100)
    PROXIMA_APLICACAO: Optional[datetime] = None
    CUSTO: Optional[float] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = None
    ID_MEDICAMENTO: Optional[int] = None
    QUANTIDADE_APLICADA: Optional[float] = Field(None, gt=0)
    UNIDADE_APLICADA: Optional[str] = Field(None, max_length=20)


class SaudeResponse(SaudeBase):
    ID: int
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    # Campos relacionados calculados
    animal_nome: Optional[str] = None
    medicamento_nome: Optional[str] = None
    estoque_suficiente: Optional[bool] = None
    dias_proxima_aplicacao: Optional[int] = None
    status_aplicacao: Optional[str] = None  # PENDENTE, APLICADO, ATRASADO

    @field_serializer("DATA_OCORRENCIA", "PROXIMA_APLICACAO", "DATA_REGISTRO")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None

    class Config:
        from_attributes = True


# Schemas para aplicação rápida (mantém compatibilidade)
class AplicacaoRapida(BaseModel):
    ID_ANIMAL: int
    TIPO_REGISTRO: TipoRegistroEnum
    ID_MEDICAMENTO: Optional[int] = None
    QUANTIDADE_APLICADA: Optional[float] = Field(None, gt=0)
    MEDICAMENTO_APLICADO: Optional[str] = Field(None, max_length=500)
    DOSE_APLICADA: Optional[str] = Field(None, max_length=100)
    CUSTO: Optional[float] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = None


# Schema para histórico de saúde
class HistoricoSaude(BaseModel):
    animal_id: int
    animal_nome: str
    registros: list


# Schema para próximas aplicações
class ProximasAplicacoes(BaseModel):
    animal_id: int
    animal_nome: str
    tipo_registro: str
    proxima_aplicacao: datetime
    descricao: str
    dias_vencimento: int
    medicamento_nome: Optional[str] = None
    veterinario_responsavel: Optional[str] = None
    prioridade: str  # URGENTE, NORMAL, BAIXA

    @field_serializer("proxima_aplicacao")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None


# Schema para calendário de saúde
class CalendarioSaude(BaseModel):
    data: datetime
    eventos: list

    @field_serializer("data")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None


# Schema para estatísticas
class EstatisticasSaude(BaseModel):
    total_registros: int
    registros_mes_atual: int
    custo_total_mes: float
    proximas_aplicacoes: int
    animais_em_tratamento: int

    # Breakdown por tipo
    total_vacinas: int
    total_vermifugos: int
    total_medicamentos: int
    total_exames: int
    total_consultas: int


# Schema para consumo por tipo
class ConsumoPorTipo(BaseModel):
    tipo_registro: str
    total_registros: int
    custo_total: float


# Schema para autocomplete de medicamentos
class MedicamentoAutocomplete(BaseModel):
    id: int
    nome: str
    unidade_medida: str
    estoque_atual: float
