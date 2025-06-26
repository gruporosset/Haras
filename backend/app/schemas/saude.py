# backend/app/schemas/saude.py
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, field_serializer


class TipoRegistroEnum(str, Enum):
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
    # ID_USUARIO_REGISTRO: int

    @field_validator('DATA_OCORRENCIA')
    @classmethod
    def validate_data_ocorrencia(cls, v):
        if v > datetime.now():
            raise ValueError('Data de ocorrência não pode ser no futuro')
        return v

    @field_validator('PROXIMA_APLICACAO')
    @classmethod
    def validate_proxima_aplicacao(cls, v, info):
        if v and hasattr(info, 'data') and 'DATA_OCORRENCIA' in info.data:
            if v <= info.data['DATA_OCORRENCIA']:
                raise ValueError(
                    'Próxima aplicação deve ser após a data de ocorrência')
        return v

    @field_validator('QUANTIDADE_APLICADA')
    @classmethod
    def validate_quantidade_medicamento(cls, v, info):
        # Se informou medicamento do estoque, deve informar quantidade
        if hasattr(info, 'data') and 'ID_MEDICAMENTO' in info.data:
            if info.data['ID_MEDICAMENTO'] and not v:
                raise ValueError(
                    'Quantidade deve ser informada quando medicamento do estoque é selecionado')
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

    @field_serializer('DATA_OCORRENCIA', 'PROXIMA_APLICACAO', 'DATA_REGISTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None

    class Config:
        from_attributes = True

# Schemas para aplicação rápida


class AplicacaoRapida(BaseModel):
    ID_ANIMAL: int
    TIPO_REGISTRO: TipoRegistroEnum
    ID_MEDICAMENTO: Optional[int] = None
    QUANTIDADE_APLICADA: Optional[float] = Field(None, gt=0)
    MEDICAMENTO_APLICADO: Optional[str] = Field(None, max_length=500)
    DOSE_APLICADA: Optional[str] = Field(None, max_length=100)
    VETERINARIO_RESPONSAVEL: Optional[str] = Field(None, max_length=200)
    OBSERVACOES: Optional[str] = None

# Schemas para relatórios e estatísticas


class EstatisticasSaude(BaseModel):
    animal_id: int
    animal_nome: str
    total_registros: int
    tipos_aplicados: dict  # {"VACINA": 5, "MEDICAMENTO": 3}
    ultima_aplicacao: Optional[datetime] = None
    proximas_aplicacoes: int
    custo_total: Optional[float] = None
    veterinario_principal: Optional[str] = None


class VeterinarioEstatisticas(BaseModel):
    veterinario: str
    total_aplicacoes: int
    animais_atendidos: int
    tipos_diferentes: int
    ultimo_atendimento: Optional[str] = None


class ProximasAplicacoes(BaseModel):
    animal_id: int
    animal_nome: str
    tipo_registro: str
    data_aplicacao: datetime
    descricao: str
    dias_restantes: int
    medicamento_nome: Optional[str] = None
    veterinario_responsavel: Optional[str] = None
    prioridade: str  # URGENTE, NORMAL, BAIXA


class HistoricoSaude(BaseModel):
    animal_id: int
    animal_nome: str
    registros: list[SaudeResponse]
    resumo_tipos: dict
    periodo_analise: str
    total_custo: Optional[float] = None


class CalendarioSaude(BaseModel):
    data: datetime
    eventos: list[dict]  # Lista de aplicações para o dia
    total_eventos: int
    tipos_eventos: list[str]


class ConsumoPorTipo(BaseModel):
    tipo_registro: str
    total_aplicacoes: int
    medicamentos_utilizados: int
    custo_total: Optional[float] = None
    periodo_analise: str
    animais_atendidos: int

# Schema para autocomplete de medicamentos


class MedicamentoAutocomplete(BaseModel):
    value: int
    label: str
    nome: str
    estoque: float
    unidade: str
    forma: Optional[str] = None
    carencia: Optional[int] = None
    principio_ativo: Optional[str] = None
