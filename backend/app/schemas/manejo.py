# backend/app/schemas/manejo.py
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, field_serializer


class TipoProdutoEnum(str, Enum):
    FERTILIZANTE = "FERTILIZANTE"
    DEFENSIVO = "DEFENSIVO"
    CORRETIVO = "CORRETIVO"
    SEMENTE = "SEMENTE"


class TipoManejoEnum(str, Enum):
    ADUBACAO = "ADUBACAO"
    CALAGEM = "CALAGEM"
    PLANTIO = "PLANTIO"
    APLICACAO_DEFENSIVO = "APLICACAO_DEFENSIVO"
    ROÇADA = "ROÇADA"
    IRRIGACAO = "IRRIGACAO"

# === PRODUTOS MANEJO ===


class ProdutoManejoBase(BaseModel):
    NOME: str = Field(..., max_length=100)
    TIPO_PRODUTO: TipoProdutoEnum
    PRINCIPIO_ATIVO: Optional[str] = Field(None, max_length=200)
    CONCENTRACAO: Optional[str] = Field(None, max_length=50)
    UNIDADE_MEDIDA: str = Field(..., max_length=20)  # KG, L, T, SC
    FABRICANTE: Optional[str] = Field(None, max_length=100)
    REGISTRO_MINISTERIO: Optional[str] = Field(None, max_length=50)
    OBSERVACOES: Optional[str] = None


class ProdutoManejoCreate(ProdutoManejoBase):
    ID_USUARIO_CADASTRO: int


class ProdutoManejoUpdate(BaseModel):
    NOME: Optional[str] = Field(None, max_length=100)
    TIPO_PRODUTO: Optional[TipoProdutoEnum] = None
    PRINCIPIO_ATIVO: Optional[str] = Field(None, max_length=200)
    CONCENTRACAO: Optional[str] = Field(None, max_length=50)
    UNIDADE_MEDIDA: Optional[str] = Field(None, max_length=20)
    FABRICANTE: Optional[str] = Field(None, max_length=100)
    REGISTRO_MINISTERIO: Optional[str] = Field(None, max_length=50)
    OBSERVACOES: Optional[str] = None
    ATIVO: Optional[str] = Field(None, pattern=r'^[SN]$')


class ProdutoManejoResponse(ProdutoManejoBase):
    ID: int
    ATIVO: str
    ID_USUARIO_CADASTRO: int
    DATA_CADASTRO: Optional[datetime] = None

    @field_serializer('DATA_CADASTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else None

    class Config:
        from_attributes = True

# === ANÁLISES DE SOLO ===


class AnalisesSoloBase(BaseModel):
    ID_TERRENO: int
    DATA_COLETA: datetime
    DATA_RESULTADO: Optional[datetime] = None
    LABORATORIO: Optional[str] = Field(None, max_length=100)

    # Parâmetros químicos
    PH_AGUA: Optional[float] = Field(None, ge=0, le=14)
    PH_CACL2: Optional[float] = Field(None, ge=0, le=14)
    MATERIA_ORGANICA: Optional[float] = Field(None, ge=0, le=100)  # %
    FOSFORO: Optional[float] = Field(None, ge=0)  # mg/dm³
    POTASSIO: Optional[float] = Field(None, ge=0)  # cmolc/dm³
    CALCIO: Optional[float] = Field(None, ge=0)  # cmolc/dm³
    MAGNESIO: Optional[float] = Field(None, ge=0)  # cmolc/dm³
    ALUMINIO: Optional[float] = Field(None, ge=0)  # cmolc/dm³
    H_AL: Optional[float] = Field(None, ge=0)  # H+Al
    CTC: Optional[float] = Field(None, ge=0)  # Capacidade de Troca
    SATURACAO_BASES: Optional[float] = Field(None, ge=0, le=100)  # %
    SATURACAO_ALUMINIO: Optional[float] = Field(None, ge=0, le=100)  # %

    # Micronutrientes
    ENXOFRE: Optional[float] = Field(None, ge=0)
    BORO: Optional[float] = Field(None, ge=0)
    COBRE: Optional[float] = Field(None, ge=0)
    FERRO: Optional[float] = Field(None, ge=0)
    MANGANES: Optional[float] = Field(None, ge=0)
    ZINCO: Optional[float] = Field(None, ge=0)

    OBSERVACOES: Optional[str] = None
    RECOMENDACOES: Optional[str] = None


class AnalisesSoloCreate(AnalisesSoloBase):
    ID_USUARIO_CADASTRO: int

    @field_validator('DATA_COLETA')
    @classmethod
    def validate_data_coleta(cls, v):
        if v > datetime.now():
            raise ValueError('Data de coleta não pode ser no futuro')
        return v


class AnalisesSoloUpdate(BaseModel):
    DATA_RESULTADO: Optional[datetime] = None
    LABORATORIO: Optional[str] = Field(None, max_length=100)
    PH_AGUA: Optional[float] = Field(None, ge=0, le=14)
    PH_CACL2: Optional[float] = Field(None, ge=0, le=14)
    MATERIA_ORGANICA: Optional[float] = Field(None, ge=0, le=100)
    FOSFORO: Optional[float] = Field(None, ge=0)
    POTASSIO: Optional[float] = Field(None, ge=0)
    CALCIO: Optional[float] = Field(None, ge=0)
    MAGNESIO: Optional[float] = Field(None, ge=0)
    SATURACAO_BASES: Optional[float] = Field(None, ge=0, le=100)
    OBSERVACOES: Optional[str] = None
    RECOMENDACOES: Optional[str] = None


class AnalisesSoloResponse(AnalisesSoloBase):
    ID: int
    ID_USUARIO_CADASTRO: int
    DATA_CADASTRO: Optional[datetime] = None
    ARQUIVO_LAUDO: Optional[str] = None

    # Campos relacionados
    terreno_nome: Optional[str] = None

    @field_serializer('DATA_COLETA', 'DATA_RESULTADO', 'DATA_CADASTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None

    class Config:
        from_attributes = True

# === MANEJO TERRENOS ===


class ManejoTerrenosBase(BaseModel):
    ID_TERRENO: int
    ID_PRODUTO: int
    TIPO_MANEJO: TipoManejoEnum
    DATA_APLICACAO: datetime
    QUANTIDADE: float = Field(..., gt=0)
    UNIDADE_MEDIDA: str = Field(..., max_length=20)  # KG/HA, L/HA
    DOSE_HECTARE: Optional[float] = Field(None, gt=0)
    AREA_APLICADA: Optional[float] = Field(None, gt=0)
    CUSTO_TOTAL: Optional[float] = Field(None, ge=0)
    EQUIPAMENTO_UTILIZADO: Optional[str] = Field(None, max_length=100)
    CONDICOES_CLIMATICAS: Optional[str] = Field(None, max_length=200)
    PERIODO_CARENCIA: Optional[int] = Field(None, ge=0, le=365)  # dias
    OBSERVACOES: Optional[str] = None


class ManejoTerrenosCreate(ManejoTerrenosBase):
    ID_USUARIO_REGISTRO: int

    @field_validator('DATA_APLICACAO')
    @classmethod
    def validate_data_aplicacao(cls, v):
        if v > datetime.now():
            raise ValueError('Data de aplicação não pode ser no futuro')
        return v


class ManejoTerrenosUpdate(BaseModel):
    ID_PRODUTO: Optional[int] = None
    TIPO_MANEJO: Optional[TipoManejoEnum] = None
    DATA_APLICACAO: Optional[datetime] = None
    QUANTIDADE: Optional[float] = Field(None, gt=0)
    UNIDADE_MEDIDA: Optional[str] = Field(None, max_length=20)
    DOSE_HECTARE: Optional[float] = Field(None, gt=0)
    AREA_APLICADA: Optional[float] = Field(None, gt=0)
    CUSTO_TOTAL: Optional[float] = Field(None, ge=0)
    EQUIPAMENTO_UTILIZADO: Optional[str] = Field(None, max_length=100)
    CONDICOES_CLIMATICAS: Optional[str] = Field(None, max_length=200)
    PERIODO_CARENCIA: Optional[int] = Field(None, ge=0, le=365)
    OBSERVACOES: Optional[str] = None


class ManejoTerrenosResponse(ManejoTerrenosBase):
    ID: int
    DATA_LIBERACAO: Optional[datetime] = None  # Calculado automaticamente
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    # Campos relacionados
    terreno_nome: Optional[str] = None
    produto_nome: Optional[str] = None
    dias_para_liberacao: Optional[int] = None  # Calculado

    @field_serializer('DATA_APLICACAO', 'DATA_LIBERACAO', 'DATA_REGISTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None

    class Config:
        from_attributes = True

# === SCHEMAS PARA RELATÓRIOS ===


class CronogramaAplicacoes(BaseModel):
    terreno_id: int
    terreno_nome: str
    manejo_id: int
    tipo_manejo: str
    produto_nome: str
    data_aplicacao: datetime
    data_liberacao: Optional[datetime] = None
    dias_para_liberacao: Optional[int] = None
    status: str  # APLICADO, PENDENTE, LIBERADO


class CapacidadeOcupacao(BaseModel):
    terreno_id: int
    terreno_nome: str
    area_hectares: float
    capacidade_animais: Optional[int]
    animais_atuais: int
    taxa_ocupacao: float  # %
    status_lotacao: str  # ADEQUADA, SOBRELOTADO, SUBLOTADO


class HistoricoNutricional(BaseModel):
    terreno_id: int
    terreno_nome: str
    ultima_analise: Optional[datetime] = None
    ph_atual: Optional[float] = None
    saturacao_bases: Optional[float] = None
    materia_organica: Optional[float] = None
    total_aplicacoes: int
    custo_total_ano: Optional[float] = None
    status_solo: str  # BOM, REGULAR, RUIM
