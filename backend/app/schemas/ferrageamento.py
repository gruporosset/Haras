from enum import Enum
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, field_serializer


class TipoFerrageamentoEnum(str, Enum):
    FERRAGEAMENTO = "FERRAGEAMENTO"
    CASQUEAMENTO = "CASQUEAMENTO"
    FERRAGEAMENTO_CORRETIVO = "FERRAGEAMENTO_CORRETIVO"
    CASQUEAMENTO_TERAPEUTICO = "CASQUEAMENTO_TERAPEUTICO"


class TipoFerraduraEnum(str, Enum):
    COMUM = "Comum"
    ORTOPEDICA = "Ortopédica"
    ALUMINIO = "Alumínio"
    BORRACHA = "Borracha"
    COLAGEM = "Colagem"
    DESCALCO = "Descalço"


class MembroTratadoEnum(str, Enum):
    AD = "AD"
    AE = "AE"
    PD = "PD"
    PE = "PE"
    TODOS = "TODOS"


class StatusCascoEnum(str, Enum):
    BOM = "BOM"
    REGULAR = "REGULAR"
    RUIM = "RUIM"
    PROBLEMA = "PROBLEMA"


class StatusVencimentoEnum(str, Enum):
    SEM_AGENDAMENTO = "SEM_AGENDAMENTO"
    VENCIDO = "VENCIDO"
    VENCE_SEMANA = "VENCE_SEMANA"
    VENCE_QUINZENA = "VENCE_QUINZENA"
    EM_DIA = "EM_DIA"


# Schemas para Request
class FerrageamentoCreate(BaseModel):
    ID_ANIMAL: int = Field(..., description="ID do animal")
    TIPO_REGISTRO: TipoFerrageamentoEnum = Field(
        ..., description="Tipo de registro")
    DATA_OCORRENCIA: datetime = Field(...,
                                      description="Data do ferrageamento/casqueamento")
    DESCRICAO: Optional[str] = Field(
        None, max_length=1000, description="Descrição do procedimento")

    # Campos específicos de ferrageamento
    TIPO_FERRADURA: Optional[TipoFerraduraEnum] = Field(
        None, description="Tipo de ferradura")
    MEMBRO_TRATADO: MembroTratadoEnum = Field(
        default=MembroTratadoEnum.TODOS, description="Membro(s) tratado(s)")
    PROBLEMA_DETECTADO: Optional[str] = Field(
        None, max_length=500, description="Problemas detectados")
    TECNICA_APLICADA: Optional[str] = Field(
        None, max_length=200, description="Técnica aplicada")
    FERRADOR_RESPONSAVEL: Optional[str] = Field(
        None, max_length=200, description="Nome do ferrador")
    STATUS_CASCO: Optional[StatusCascoEnum] = Field(
        None, description="Estado do casco")
    PROXIMA_AVALIACAO: Optional[datetime] = Field(
        None, description="Data da próxima avaliação")

    # Campos gerais
    CUSTO: Optional[float] = Field(None, ge=0, description="Custo do serviço")
    OBSERVACOES: Optional[str] = Field(None, description="Observações gerais")

    @field_validator('DATA_OCORRENCIA')
    @classmethod
    def validar_data_ocorrencia(cls, v):
        if v > datetime.now():
            raise ValueError('Data de ocorrência não pode ser futura')
        return v

    @field_validator('PROXIMA_AVALIACAO')
    @classmethod
    def validar_proxima_avaliacao(cls, v, info):
        if v and hasattr(info, 'data') and 'DATA_OCORRENCIA' in info.data:
            if v <= info.data['DATA_OCORRENCIA']:
                raise ValueError(
                    'Próxima avaliação deve ser posterior à data de ocorrência')
        return v


class FerrageamentoUpdate(BaseModel):
    TIPO_REGISTRO: Optional[TipoFerrageamentoEnum] = None
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


# Schemas para Response
class FerrageamentoResponse(BaseModel):
    ID: int
    ID_ANIMAL: int
    TIPO_REGISTRO: str
    DATA_OCORRENCIA: datetime
    DESCRICAO: Optional[str] = None

    # Campos específicos
    TIPO_FERRADURA: Optional[str] = None
    MEMBRO_TRATADO: Optional[str] = None
    PROBLEMA_DETECTADO: Optional[str] = None
    TECNICA_APLICADA: Optional[str] = None
    FERRADOR_RESPONSAVEL: Optional[str] = None
    STATUS_CASCO: Optional[str] = None
    PROXIMA_AVALIACAO: Optional[datetime] = None

    # Campos gerais
    CUSTO: Optional[float] = None
    OBSERVACOES: Optional[str] = None
    DATA_REGISTRO: Optional[datetime] = None

    # Campos calculados
    animal_nome: Optional[str] = None
    dias_proxima_avaliacao: Optional[int] = None
    status_vencimento: Optional[str] = None

    @field_serializer('DATA_OCORRENCIA', 'PROXIMA_AVALIACAO', 'DATA_REGISTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else None

    class Config:
        from_attributes = True


class FerrageamentoResumoResponse(BaseModel):
    ANIMAL_ID: int
    ANIMAL_NOME: str
    NUMERO_REGISTRO: Optional[str] = None
    REGISTRO_ID: int
    TIPO_REGISTRO: str
    DATA_OCORRENCIA: datetime
    TIPO_FERRADURA: Optional[str] = None
    MEMBRO_TRATADO: Optional[str] = None
    PROBLEMA_DETECTADO: Optional[str] = None
    FERRADOR_RESPONSAVEL: Optional[str] = None
    STATUS_CASCO: Optional[str] = None
    PROXIMA_AVALIACAO: Optional[datetime] = None
    CUSTO: Optional[float] = None
    OBSERVACOES: Optional[str] = None
    DIAS_PROXIMA_AVALIACAO: Optional[int] = None
    STATUS_VENCIMENTO: Optional[str] = None

    class Config:
        from_attributes = True


# Schemas para relatórios e estatísticas
class EstatisticasFerrageamento(BaseModel):
    animal_id: int
    animal_nome: str
    total_ferrageamentos: int
    total_casqueamentos: int
    custo_total: Optional[float] = None
    ultimo_ferrageamento: Optional[datetime] = None
    ultimo_casqueamento: Optional[datetime] = None
    status_atual_casco: Optional[str] = None
    ferrador_principal: Optional[str] = None
    proxima_data: Optional[datetime] = None
    status_vencimento: Optional[str] = None


class FerradorEstatisticas(BaseModel):
    ferrador: str
    total_atendimentos: int
    animais_atendidos: int
    custo_total: Optional[float] = None
    ultimo_atendimento: Optional[datetime] = None
    especialidades: List[str] = []  # Tipos de ferrageamento que mais faz


class AlertaVencimento(BaseModel):
    animal_id: int
    animal_nome: str
    tipo_registro: str
    data_vencimento: datetime
    dias_vencimento: int
    status_vencimento: str
    ferrador_anterior: Optional[str] = None
    custo_estimado: Optional[float] = None


class RelatorioFerrageamento(BaseModel):
    periodo_inicio: date
    periodo_fim: date
    total_registros: int
    custo_total: Optional[float] = None
    animais_atendidos: int
    ferradores_utilizados: int
    tipos_mais_realizados: dict
    problemas_mais_comuns: List[str] = []
    registros: List[FerrageamentoResponse] = []


# Schema para aplicação rápida (mobile)
class FerrageamentoRapido(BaseModel):
    ID_ANIMAL: int
    TIPO_REGISTRO: TipoFerrageamentoEnum
    MEMBRO_TRATADO: MembroTratadoEnum = MembroTratadoEnum.TODOS
    FERRADOR_RESPONSAVEL: str = Field(..., max_length=200)
    STATUS_CASCO: StatusCascoEnum = StatusCascoEnum.BOM
    CUSTO: Optional[float] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "ID_ANIMAL": 1,
                "TIPO_REGISTRO": "FERRAGEAMENTO",
                "MEMBRO_TRATADO": "TODOS",
                "FERRADOR_RESPONSAVEL": "João Silva",
                "STATUS_CASCO": "BOM",
                "CUSTO": 120.0,
                "OBSERVACOES": "Ferrageamento padrão, cascos em bom estado"
            }
        }
