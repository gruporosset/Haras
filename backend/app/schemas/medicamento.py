# backend/app/schemas/medicamento.py
from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional
from datetime import datetime
from enum import Enum


class FormaFarmaceuticaEnum(str, Enum):
    INJETAVEL = "INJETAVEL"
    ORAL = "ORAL"
    TOPICO = "TOPICO"


class TipoMovimentacaoEnum(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE = "AJUSTE"


class StatusEstoqueEnum(str, Enum):
    OK = "OK"
    ESTOQUE_BAIXO = "ESTOQUE_BAIXO"
    VENCENDO = "VENCENDO"
    VENCIDO = "VENCIDO"

# === MEDICAMENTO ===


class MedicamentoBase(BaseModel):
    NOME: str = Field(..., max_length=200)
    PRINCIPIO_ATIVO: Optional[str] = Field(None, max_length=200)
    CONCENTRACAO: Optional[str] = Field(None, max_length=100)
    FORMA_FARMACEUTICA: Optional[FormaFarmaceuticaEnum] = None
    FABRICANTE: Optional[str] = Field(None, max_length=100)
    REGISTRO_MAPA: Optional[str] = Field(None, max_length=50)

    # Estoque
    ESTOQUE_ATUAL: float = Field(default=0, ge=0)
    ESTOQUE_MINIMO: float = Field(default=0, ge=0)
    UNIDADE_MEDIDA: str = Field(..., max_length=20)

    # Validade
    LOTE_ATUAL: Optional[str] = Field(None, max_length=50)
    DATA_VALIDADE: Optional[datetime] = None
    DATA_FABRICACAO: Optional[datetime] = None

    # Custos
    PRECO_UNITARIO: Optional[float] = Field(None, ge=0)
    FORNECEDOR: Optional[str] = Field(None, max_length=100)

    # Prescrição
    REQUER_RECEITA: str = Field(default='N', pattern=r'^[SN]$')
    PERIODO_CARENCIA: Optional[int] = Field(None, ge=0, le=365)

    OBSERVACOES: Optional[str] = None


class MedicamentoCreate(MedicamentoBase):
    ID_USUARIO_CADASTRO: int

    @field_validator('DATA_VALIDADE', 'DATA_FABRICACAO')
    @classmethod
    def validate_datas(cls, v):
        if v and v < datetime.now():
            raise ValueError(
                'Data não pode ser no passado para novos registros')
        return v


class MedicamentoUpdate(BaseModel):
    NOME: Optional[str] = Field(None, max_length=200)
    PRINCIPIO_ATIVO: Optional[str] = Field(None, max_length=200)
    CONCENTRACAO: Optional[str] = Field(None, max_length=100)
    FORMA_FARMACEUTICA: Optional[FormaFarmaceuticaEnum] = None
    FABRICANTE: Optional[str] = Field(None, max_length=100)
    REGISTRO_MAPA: Optional[str] = Field(None, max_length=50)
    ESTOQUE_MINIMO: Optional[float] = Field(None, ge=0)
    PRECO_UNITARIO: Optional[float] = Field(None, ge=0)
    FORNECEDOR: Optional[str] = Field(None, max_length=100)
    REQUER_RECEITA: Optional[str] = Field(None, pattern=r'^[SN]$')
    PERIODO_CARENCIA: Optional[int] = Field(None, ge=0, le=365)
    OBSERVACOES: Optional[str] = None
    ATIVO: Optional[str] = Field(None, pattern=r'^[SN]$')


class MedicamentoResponse(MedicamentoBase):
    ID: int
    ATIVO: str
    ID_USUARIO_CADASTRO: int
    DATA_CADASTRO: Optional[datetime] = None

    # Campos calculados
    status_estoque: Optional[str] = None
    dias_vencimento: Optional[int] = None
    valor_estoque: Optional[float] = None

    @field_serializer('DATA_VALIDADE', 'DATA_FABRICACAO', 'DATA_CADASTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None

    class Config:
        from_attributes = True

# === MOVIMENTAÇÃO ===


class MovimentacaoMedicamentoBase(BaseModel):
    ID_MEDICAMENTO: int
    TIPO_MOVIMENTACAO: TipoMovimentacaoEnum
    QUANTIDADE: float = Field(..., gt=0)

    # Para saída
    ID_ANIMAL: Optional[int] = None
    ID_SAUDE_ANIMAL: Optional[int] = None

    # Para entrada
    NOTA_FISCAL: Optional[str] = Field(None, max_length=100)
    FORNECEDOR: Optional[str] = Field(None, max_length=100)
    PRECO_UNITARIO: Optional[float] = Field(None, ge=0)
    LOTE: Optional[str] = Field(None, max_length=50)
    DATA_VALIDADE: Optional[datetime] = None

    MOTIVO: Optional[str] = Field(None, max_length=200)
    OBSERVACOES: Optional[str] = None


class MovimentacaoMedicamentoCreate(MovimentacaoMedicamentoBase):
    ID_USUARIO_REGISTRO: int

    @field_validator('QUANTIDADE')
    @classmethod
    def validate_quantidade(cls, v, values):
        if v <= 0:
            raise ValueError('Quantidade deve ser maior que zero')
        return v


class MovimentacaoMedicamentoUpdate(BaseModel):
    MOTIVO: Optional[str] = Field(None, max_length=200)
    OBSERVACOES: Optional[str] = None


class MovimentacaoMedicamentoResponse(MovimentacaoMedicamentoBase):
    ID: int
    QUANTIDADE_ANTERIOR: Optional[float] = None
    QUANTIDADE_ATUAL: Optional[float] = None
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    # Campos relacionados
    medicamento_nome: Optional[str] = None
    animal_nome: Optional[str] = None

    @field_serializer('DATA_VALIDADE', 'DATA_REGISTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None

    class Config:
        from_attributes = True

# === ENTRADA ESTOQUE ===


class EntradaEstoque(BaseModel):
    ID_MEDICAMENTO: int
    QUANTIDADE: float = Field(..., gt=0)
    LOTE: str = Field(..., max_length=50)
    DATA_VALIDADE: datetime
    DATA_FABRICACAO: Optional[datetime] = None
    NOTA_FISCAL: Optional[str] = Field(None, max_length=100)
    FORNECEDOR: Optional[str] = Field(None, max_length=100)
    PRECO_UNITARIO: Optional[float] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = None

# === APLICAÇÃO MEDICAMENTO ===


class AplicacaoMedicamento(BaseModel):
    ID_MEDICAMENTO: int
    ID_ANIMAL: int
    QUANTIDADE: float = Field(..., gt=0)
    OBSERVACOES: Optional[str] = None

# === RELATÓRIOS ===


class EstoqueBaixo(BaseModel):
    medicamento_id: int
    nome: str
    estoque_atual: float
    estoque_minimo: float
    unidade_medida: str
    status_alerta: str
    dias_vencimento: Optional[int] = None


class MovimentacaoEstoque(BaseModel):
    medicamento_id: int
    medicamento_nome: str
    total_entradas: float
    total_saidas: float
    saldo_atual: float
    valor_total: float
    ultima_movimentacao: Optional[datetime] = None


class ConsumoPorAnimal(BaseModel):
    animal_id: int
    animal_nome: str
    medicamento_nome: str
    total_aplicado: float
    unidade_medida: str
    numero_aplicacoes: int
    ultima_aplicacao: Optional[datetime] = None
    custo_total: Optional[float] = None


class PrevisaoConsumo(BaseModel):
    medicamento_id: int
    medicamento_nome: str
    consumo_mensal_medio: float
    estoque_atual: float
    dias_restantes: int
    data_prevista_fim: datetime
    recomendacao: str  # COMPRAR_URGENTE, COMPRAR_BREVE, OK
