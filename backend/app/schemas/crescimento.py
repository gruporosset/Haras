# backend/app/schemas/crescimento.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, field_serializer


class CrescimentoBase(BaseModel):
    ID_ANIMAL: int
    DATA_MEDICAO: datetime
    PESO: Optional[float] = Field(None, gt=0, le=2000, description="Peso em kg")
    ALTURA: Optional[float] = Field(None, gt=0, le=300, description="Altura em cm")
    CIRCUNFERENCIA_CANELA: Optional[float] = Field(
        None, gt=0, le=100, description="Circunferência da canela em cm"
    )
    CIRCUNFERENCIA_TORACICA: Optional[float] = Field(
        None, gt=0, le=500, description="Circunferência torácica em cm"
    )
    COMPRIMENTO_CORPO: Optional[float] = Field(
        None, gt=0, le=500, description="Comprimento do corpo em cm"
    )
    OBSERVACOES: Optional[str] = None


class CrescimentoCreate(CrescimentoBase):
    ID_USUARIO_REGISTRO: int

    @field_validator("DATA_MEDICAO")
    @classmethod
    def validate_data_medicao(cls, v):
        if v > datetime.now():
            raise ValueError("Data de medição não pode ser no futuro")
        return v

    @field_validator(
        "PESO",
        "ALTURA",
        "CIRCUNFERENCIA_CANELA",
        "CIRCUNFERENCIA_TORACICA",
        "COMPRIMENTO_CORPO",
    )
    @classmethod
    def validate_medidas(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Medidas devem ser maiores que zero")
        return v


class CrescimentoUpdate(BaseModel):
    DATA_MEDICAO: Optional[datetime] = None
    PESO: Optional[float] = Field(None, gt=0, le=2000)
    ALTURA: Optional[float] = Field(None, gt=0, le=300)
    CIRCUNFERENCIA_CANELA: Optional[float] = Field(None, gt=0, le=100)
    CIRCUNFERENCIA_TORACICA: Optional[float] = Field(None, gt=0, le=500)
    COMPRIMENTO_CORPO: Optional[float] = Field(None, gt=0, le=500)
    OBSERVACOES: Optional[str] = None


class CrescimentoResponse(CrescimentoBase):
    ID: int
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    # Campos calculados
    animal_nome: Optional[str] = None
    ganho_peso: Optional[float] = None  # Comparado com medição anterior
    dias_desde_ultima: Optional[int] = None

    @field_serializer("DATA_MEDICAO", "DATA_REGISTRO")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None

    class Config:
        from_attributes = True


# Schemas para relatórios e estatísticas


class EstatisticasCrescimento(BaseModel):
    animal_id: int
    animal_nome: str
    total_medicoes: int
    peso_inicial: Optional[float]
    peso_atual: Optional[float]
    ganho_peso_total: Optional[float]
    ganho_peso_medio_mes: Optional[float]
    altura_inicial: Optional[float]
    altura_atual: Optional[float]
    primeira_medicao: Optional[datetime]
    ultima_medicao: Optional[datetime]


class CrescimentoDetalhado(BaseModel):
    medicao: CrescimentoResponse
    variacao_peso: Optional[float] = None
    variacao_altura: Optional[float] = None
    dias_crescimento: Optional[int] = None
    taxa_crescimento_dia: Optional[float] = None  # kg/dia


class ComparacaoMedidas(BaseModel):
    animal_id: int
    animal_nome: str
    idade_meses: Optional[int]
    peso_atual: Optional[float]
    peso_ideal_raca: Optional[float]  # Para futuro
    altura_atual: Optional[float]
    classificacao: str  # ABAIXO, IDEAL, ACIMA
