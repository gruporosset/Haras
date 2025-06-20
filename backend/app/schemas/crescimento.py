from pydantic import BaseModel, Field, field_serializer, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class TipoRegistroEnum(str, Enum):
    VACINA = "VACINA"
    VERMIFUGO = "VERMIFUGO"
    MEDICAMENTO = "MEDICAMENTO"
    EXAME = "EXAME"
    CONSULTA = "CONSULTA"
    CIRURGIA = "CIRURGIA"
    TRATAMENTO = "TRATAMENTO"

# Schemas Crescimento
class CrescimentoBase(BaseModel):
    ID_ANIMAL: int
    DATA_MEDICAO: datetime
    PESO: Optional[float] = Field(None, ge=0)
    ALTURA: Optional[float] = Field(None, ge=0)
    PERIMETRO_TORACICO: Optional[float] = Field(None, ge=0)
    COMPRIMENTO_CORPO: Optional[float] = Field(None, ge=0)
    DIAMETRO_CANELA: Optional[float] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = Field(None, max_length=500)

class CrescimentoCreate(CrescimentoBase):
    ID_USUARIO_REGISTRO: int

    @field_validator('DATA_MEDICAO')
    @classmethod
    def validate_data_medicao(cls, v):
        if v > datetime.now():
            raise ValueError('Data de medição não pode ser no futuro')
        return v

class CrescimentoUpdate(BaseModel):
    DATA_MEDICAO: Optional[datetime] = None
    PESO: Optional[float] = Field(None, ge=0)
    ALTURA: Optional[float] = Field(None, ge=0)
    PERIMETRO_TORACICO: Optional[float] = Field(None, ge=0)
    COMPRIMENTO_CORPO: Optional[float] = Field(None, ge=0)
    DIAMETRO_CANELA: Optional[float] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = Field(None, max_length=500)
    ID_USUARIO_REGISTRO: Optional[int] = None

class CrescimentoResponse(CrescimentoBase):
    ID: int
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    @field_serializer('DATA_MEDICAO', 'DATA_REGISTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else None

    class Config:
        from_attributes = True

# Schemas Saúde
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

class SaudeCreate(SaudeBase):
    ID_USUARIO_REGISTRO: int

    @field_validator('DATA_OCORRENCIA')
    @classmethod
    def validate_data_ocorrencia(cls, v):
        if v > datetime.now():
            raise ValueError('Data de ocorrência não pode ser no futuro')
        return v

    @field_validator('PROXIMA_APLICACAO')
    @classmethod
    def validate_proxima_aplicacao(cls, v, info):
        if v and info.data.get('DATA_OCORRENCIA'):
            if v <= info.data['DATA_OCORRENCIA']:
                raise ValueError('Próxima aplicação deve ser após a data de ocorrência')
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
    ID_USUARIO_REGISTRO: Optional[int] = None

class SaudeResponse(SaudeBase):
    ID: int
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    @field_serializer('DATA_OCORRENCIA', 'PROXIMA_APLICACAO', 'DATA_REGISTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else None

    class Config:
        from_attributes = True

# Schemas para Relatórios
class EstatisticasCrescimento(BaseModel):
    animal_id: int
    animal_nome: str
    total_medicoes: int
    peso_inicial: Optional[float]
    peso_atual: Optional[float]
    ganho_peso: Optional[float]
    media_peso: Optional[float]

class ProximasAplicacoes(BaseModel):
    animal_id: int
    animal_nome: str
    tipo_registro: str
    data_aplicacao: datetime
    descricao: str
    dias_restantes: int