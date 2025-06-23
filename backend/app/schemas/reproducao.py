from typing import Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, field_validator, field_serializer


class TipoCoberturaEnum(str, Enum):
    NATURAL = "NATURAL"
    IA = "IA"
    TE = "TE"


class ResultadoDiagnosticoEnum(str, Enum):
    POSITIVO = "POSITIVO"
    NEGATIVO = "NEGATIVO"
    PENDENTE = "PENDENTE"


class StatusReproducaoEnum(str, Enum):
    ATIVO = "A"
    CONCLUIDO = "C"
    FALHADO = "F"


class ReproducaoBase(BaseModel):
    ID_EGUA: int
    ID_PARCEIRO: Optional[int] = None
    TIPO_COBERTURA: TipoCoberturaEnum
    DATA_COBERTURA: datetime
    DATA_DIAGNOSTICO: Optional[datetime] = None
    RESULTADO_DIAGNOSTICO: ResultadoDiagnosticoEnum = ResultadoDiagnosticoEnum.PENDENTE
    DATA_PARTO_PREVISTA: Optional[datetime] = None
    DATA_PARTO_REAL: Optional[datetime] = None
    OBSERVACOES: Optional[str] = None
    STATUS_REPRODUCAO: StatusReproducaoEnum = StatusReproducaoEnum.ATIVO

    class Config:
        use_enum_values = True


class ReproducaoCreate(ReproducaoBase):
    ID_USUARIO_REGISTRO: int

    @field_validator('DATA_COBERTURA')
    @classmethod
    def validate_data_cobertura(cls, v):
        if v > datetime.now():
            raise ValueError('Data de cobertura não pode ser no futuro')
        return v

    @field_validator('DATA_DIAGNOSTICO')
    @classmethod
    def validate_data_diagnostico(cls, v, info):
        if v and info.data.get('DATA_COBERTURA'):
            if v < info.data['DATA_COBERTURA']:
                raise ValueError(
                    'Data de diagnóstico deve ser após a cobertura')
        return v

    @field_validator('DATA_PARTO_PREVISTA')
    @classmethod
    def validate_data_parto_prevista(cls, v, info):
        if v and info.data.get('DATA_COBERTURA'):
            # Gestação equina: aproximadamente 340 dias (11 meses)
            data_minima = info.data['DATA_COBERTURA'] + timedelta(days=300)
            data_maxima = info.data['DATA_COBERTURA'] + timedelta(days=380)

            if v < data_minima or v > data_maxima:
                raise ValueError(
                    'Data prevista deve estar entre 300-380 dias após a cobertura')
        return v

    @field_validator('DATA_PARTO_REAL')
    @classmethod
    def validate_data_parto_real(cls, v, info):
        if v and info.data.get('DATA_COBERTURA'):
            if v < info.data['DATA_COBERTURA']:
                raise ValueError('Data de parto deve ser após a cobertura')
        return v


class ReproducaoUpdate(BaseModel):
    ID_PARCEIRO: Optional[int] = None
    TIPO_COBERTURA: Optional[TipoCoberturaEnum] = None
    DATA_COBERTURA: Optional[datetime] = None
    DATA_DIAGNOSTICO: Optional[datetime] = None
    RESULTADO_DIAGNOSTICO: Optional[ResultadoDiagnosticoEnum] = None
    DATA_PARTO_PREVISTA: Optional[datetime] = None
    DATA_PARTO_REAL: Optional[datetime] = None
    OBSERVACOES: Optional[str] = None
    STATUS_REPRODUCAO: Optional[StatusReproducaoEnum] = None
    ID_USUARIO_REGISTRO: Optional[int] = None


class ReproducaoResponse(ReproducaoBase):
    ID: int
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    # Campos relacionados
    egua_nome: Optional[str] = None
    parceiro_nome: Optional[str] = None
    dias_gestacao: Optional[int] = None

    @field_serializer('DATA_COBERTURA', 'DATA_DIAGNOSTICO', 'DATA_PARTO_PREVISTA', 'DATA_PARTO_REAL', 'DATA_REGISTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None

    class Config:
        from_attributes = True

# Schemas para relatórios


class EstatisticasReproducao(BaseModel):
    total_coberturas: int
    coberturas_positivas: int
    coberturas_negativas: int
    coberturas_pendentes: int
    taxa_sucesso: float
    partos_realizados: int
    gestacoes_ativas: int


class CalendarioReproducao(BaseModel):
    egua_id: int
    egua_nome: str
    evento_tipo: str  # DIAGNOSTICO, PARTO_PREVISTO
    data_evento: datetime
    dias_restantes: int
    observacoes: Optional[str] = None


class HistoricoEgua(BaseModel):
    reproducoes: list[ReproducaoResponse]
    total_coberturas: int
    partos_realizados: int
    taxa_sucesso: float
