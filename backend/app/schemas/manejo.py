# backend/app/schemas/manejo.py
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator


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
    GESSAGEM = "GESSAGEM"
    SULCAGEM = "SULCAGEM"


class TipoMovimentacaoManejoEnum(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE = "AJUSTE"


class StatusEstoqueEnum(str, Enum):
    SEM_ESTOQUE = "SEM_ESTOQUE"
    ESTOQUE_BAIXO = "ESTOQUE_BAIXO"
    VENCIMENTO_PROXIMO = "VENCIMENTO_PROXIMO"
    OK = "OK"


# === PRODUTO MANEJO SCHEMAS ===
class ProdutoManejoBase(BaseModel):
    NOME: str = Field(..., max_length=100)
    TIPO_PRODUTO: TipoProdutoEnum
    PRINCIPIO_ATIVO: Optional[str] = Field(None, max_length=200)
    CONCENTRACAO: Optional[str] = Field(None, max_length=50)
    UNIDADE_MEDIDA: str = Field(..., max_length=20)
    FABRICANTE: Optional[str] = Field(None, max_length=100)
    REGISTRO_MINISTERIO: Optional[str] = Field(None, max_length=50)

    # Controle de Estoque
    ESTOQUE_ATUAL: float = Field(default=0, ge=0)
    ESTOQUE_MINIMO: float = Field(default=0, ge=0)
    ESTOQUE_MAXIMO: Optional[float] = Field(None, ge=0)

    # Custos e Fornecimento
    PRECO_UNITARIO: Optional[float] = Field(None, ge=0)
    FORNECEDOR_PRINCIPAL: Optional[str] = Field(None, max_length=100)
    CODIGO_FORNECEDOR: Optional[str] = Field(None, max_length=50)

    # Validade e Lote
    LOTE_ATUAL: Optional[str] = Field(None, max_length=50)
    DATA_VALIDADE: Optional[datetime] = None
    DATA_ULTIMA_COMPRA: Optional[datetime] = None

    # Aplicação Técnica
    DOSE_RECOMENDADA: Optional[float] = Field(None, ge=0)
    PERIODO_CARENCIA: Optional[int] = Field(None, ge=0)
    REQUER_RECEITUARIO: str = Field(default='N', pattern='^[SN]$')

    # Armazenamento
    LOCAL_ARMAZENAMENTO: Optional[str] = Field(None, max_length=100)
    CONDICOES_ARMAZENAMENTO: Optional[str] = Field(None, max_length=200)

    OBSERVACOES: Optional[str] = None

    @model_validator(mode='after')
    def validar_estoques(self):
        if (self.ESTOQUE_MAXIMO is not None and
                self.ESTOQUE_MAXIMO <= self.ESTOQUE_MINIMO):
            raise ValueError('Estoque máximo deve ser maior que o mínimo')
        return self

    @field_validator('DATA_VALIDADE')
    @classmethod
    def validar_data_validade(cls, v):
        if v and v < datetime.now():
            raise ValueError('Data de validade não pode ser no passado')
        return v


class ProdutoManejoCreate(ProdutoManejoBase):
    pass


class ProdutoManejoUpdate(BaseModel):
    NOME: Optional[str] = Field(None, max_length=100)
    TIPO_PRODUTO: Optional[TipoProdutoEnum] = None
    PRINCIPIO_ATIVO: Optional[str] = Field(None, max_length=200)
    CONCENTRACAO: Optional[str] = Field(None, max_length=50)
    UNIDADE_MEDIDA: Optional[str] = Field(None, max_length=20)
    FABRICANTE: Optional[str] = Field(None, max_length=100)
    REGISTRO_MINISTERIO: Optional[str] = Field(None, max_length=50)
    ESTOQUE_MINIMO: Optional[float] = Field(None, ge=0)
    ESTOQUE_MAXIMO: Optional[float] = Field(None, ge=0)
    PRECO_UNITARIO: Optional[float] = Field(None, ge=0)
    FORNECEDOR_PRINCIPAL: Optional[str] = Field(None, max_length=100)
    CODIGO_FORNECEDOR: Optional[str] = Field(None, max_length=50)
    LOTE_ATUAL: Optional[str] = Field(None, max_length=50)
    DATA_VALIDADE: Optional[datetime] = None
    DOSE_RECOMENDADA: Optional[float] = Field(None, ge=0)
    PERIODO_CARENCIA: Optional[int] = Field(None, ge=0)
    REQUER_RECEITUARIO: Optional[str] = Field(None, pattern='^[SN]$')
    LOCAL_ARMAZENAMENTO: Optional[str] = Field(None, max_length=100)
    CONDICOES_ARMAZENAMENTO: Optional[str] = Field(None, max_length=200)
    OBSERVACOES: Optional[str] = None


class ProdutoManejoResponse(ProdutoManejoBase):
    ID: int
    ID_USUARIO_CADASTRO: int
    DATA_CADASTRO: Optional[datetime] = None
    ATIVO: str

    # Campos calculados
    status_estoque: Optional[StatusEstoqueEnum] = None
    dias_vencimento: Optional[int] = None
    valor_total_estoque: Optional[float] = None

    class Config:
        from_attributes = True


# === MOVIMENTAÇÃO ESTOQUE SCHEMAS ===
class MovimentacaoEstoqueBase(BaseModel):
    ID_PRODUTO: int
    TIPO_MOVIMENTACAO: TipoMovimentacaoManejoEnum
    QUANTIDADE: float = Field(..., gt=0)

    # Dados da Entrada (Compra)
    NOTA_FISCAL: Optional[str] = Field(None, max_length=100)
    FORNECEDOR: Optional[str] = Field(None, max_length=100)
    PRECO_UNITARIO: Optional[float] = Field(None, ge=0)
    LOTE: Optional[str] = Field(None, max_length=50)
    DATA_VALIDADE: Optional[datetime] = None
    DATA_FABRICACAO: Optional[datetime] = None

    MOTIVO: Optional[str] = Field(None, max_length=200)
    OBSERVACOES: Optional[str] = None

    @model_validator(mode='after')
    def validar_datas(self):
        if (self.DATA_FABRICACAO and self.DATA_VALIDADE and
                self.DATA_FABRICACAO >= self.DATA_VALIDADE):
            raise ValueError('Data de fabricação deve ser anterior à validade')
        return self


class EntradaEstoqueCreate(MovimentacaoEstoqueBase):
    TIPO_MOVIMENTACAO: TipoMovimentacaoManejoEnum = Field(
        default=TipoMovimentacaoManejoEnum.ENTRADA)
    NOTA_FISCAL: str = Field(..., max_length=100)
    FORNECEDOR: str = Field(..., max_length=100)
    PRECO_UNITARIO: float = Field(..., ge=0)
    LOTE: str = Field(..., max_length=50)
    DATA_VALIDADE: Optional[datetime] = None


class SaidaEstoqueCreate(BaseModel):
    ID_PRODUTO: int
    QUANTIDADE: float = Field(..., gt=0)
    ID_TERRENO: Optional[int] = None
    MOTIVO: str = Field(..., max_length=200)
    OBSERVACOES: Optional[str] = None


class AjusteEstoqueCreate(BaseModel):
    ID_PRODUTO: int
    QUANTIDADE_NOVA: float = Field(..., ge=0)
    MOTIVO: str = Field(..., max_length=200)
    OBSERVACOES: Optional[str] = None


class MovimentacaoEstoqueResponse(MovimentacaoEstoqueBase):
    ID: int
    QUANTIDADE_ANTERIOR: Optional[float] = None
    QUANTIDADE_ATUAL: Optional[float] = None
    ID_MANEJO_TERRENO: Optional[int] = None
    ID_TERRENO: Optional[int] = None
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    # Campos relacionados
    produto_nome: Optional[str] = None
    produto_unidade: Optional[str] = None
    terreno_nome: Optional[str] = None

    class Config:
        from_attributes = True


# === MANEJO TERRENOS SCHEMAS ===
class ManejoTerrenosBase(BaseModel):
    ID_TERRENO: int
    ID_PRODUTO: int
    TIPO_MANEJO: TipoManejoEnum
    DATA_APLICACAO: datetime
    QUANTIDADE: float = Field(..., gt=0)
    UNIDADE_MEDIDA: str = Field(..., max_length=20)
    DOSE_HECTARE: Optional[float] = Field(None, gt=0)
    AREA_APLICADA: Optional[float] = Field(None, gt=0)
    CUSTO_PRODUTO: Optional[float] = Field(None, ge=0)
    CUSTO_APLICACAO: Optional[float] = Field(None, ge=0)
    CUSTO_TOTAL: Optional[float] = Field(None, ge=0)
    EQUIPAMENTO_UTILIZADO: Optional[str] = Field(None, max_length=100)
    CONDICOES_CLIMATICAS: Optional[str] = Field(None, max_length=200)
    PERIODO_CARENCIA: Optional[int] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = None

    @model_validator(mode='after')
    def calcular_custo_total(self):
        if not self.CUSTO_TOTAL:
            custo_produto = self.CUSTO_PRODUTO or 0
            custo_aplicacao = self.CUSTO_APLICACAO or 0
            self.CUSTO_TOTAL = custo_produto + custo_aplicacao
        return self


class ManejoTerrenosCreate(ManejoTerrenosBase):
    pass


class ManejoTerrenosUpdate(BaseModel):
    ID_TERRENO: Optional[int] = None
    ID_PRODUTO: Optional[int] = None
    TIPO_MANEJO: Optional[TipoManejoEnum] = None
    DATA_APLICACAO: Optional[datetime] = None
    QUANTIDADE: Optional[float] = Field(None, gt=0)
    UNIDADE_MEDIDA: Optional[str] = Field(None, max_length=20)
    DOSE_HECTARE: Optional[float] = Field(None, gt=0)
    AREA_APLICADA: Optional[float] = Field(None, gt=0)
    CUSTO_PRODUTO: Optional[float] = Field(None, ge=0)
    CUSTO_APLICACAO: Optional[float] = Field(None, ge=0)
    CUSTO_TOTAL: Optional[float] = Field(None, ge=0)
    EQUIPAMENTO_UTILIZADO: Optional[str] = Field(None, max_length=100)
    CONDICOES_CLIMATICAS: Optional[str] = Field(None, max_length=200)
    PERIODO_CARENCIA: Optional[int] = Field(None, ge=0)
    DATA_LIBERACAO: Optional[datetime] = None
    OBSERVACOES: Optional[str] = None


class ManejoTerrenosResponse(ManejoTerrenosBase):
    ID: int
    DATA_LIBERACAO: Optional[datetime] = None
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    # Campos relacionados
    terreno_nome: Optional[str] = None
    produto_nome: Optional[str] = None
    produto_tipo: Optional[str] = None

    class Config:
        from_attributes = True


# === RELATÓRIOS E ANÁLISES ===
class EstoqueBaixo(BaseModel):
    produto_id: int
    nome: str
    tipo_produto: TipoProdutoEnum
    estoque_atual: float
    estoque_minimo: float
    unidade_medida: str
    status_alerta: StatusEstoqueEnum
    dias_vencimento: Optional[int] = None
    fornecedor_principal: Optional[str] = None


class MovimentacaoResumo(BaseModel):
    produto_id: int
    produto_nome: str
    tipo_produto: TipoProdutoEnum
    estoque_atual: float
    estoque_minimo: float
    unidade_medida: str
    total_entradas: float
    total_saidas: float
    valor_entradas: float
    ultima_movimentacao: Optional[datetime] = None


class ConsumoTerrenoResumo(BaseModel):
    terreno_id: int
    terreno_nome: str
    produto_nome: str
    tipo_manejo: str
    total_aplicado: float
    unidade_medida: str
    numero_aplicacoes: int
    ultima_aplicacao: Optional[datetime] = None
    custo_total: Optional[float] = None


class PrevisaoConsumo(BaseModel):
    produto_id: int
    produto_nome: str
    consumo_mensal_medio: float
    estoque_atual: float
    dias_restantes: int
    data_prevista_fim: datetime
    recomendacao: str  # COMPRAR_URGENTE, COMPRAR_BREVE, OK


class ProdutoAutocomplete(BaseModel):
    value: int
    label: str
    nome: str
    estoque_atual: float
    estoque_minimo: float
    unidade_medida: str
    tipo_produto: TipoProdutoEnum
    status_estoque: StatusEstoqueEnum
    dose_recomendada: Optional[float] = None


# === ANÁLISES SOLO SCHEMAS ===
class AnalisesSoloBase(BaseModel):
    ID_TERRENO: int
    DATA_COLETA: datetime
    DATA_RESULTADO: Optional[datetime] = None
    LABORATORIO: Optional[str] = Field(None, max_length=100)

    # Parâmetros químicos
    PH_AGUA: Optional[float] = Field(None, ge=0, le=14)
    PH_CACL2: Optional[float] = Field(None, ge=0, le=14)
    MATERIA_ORGANICA: Optional[float] = Field(None, ge=0, le=100)
    FOSFORO: Optional[float] = Field(None, ge=0)
    POTASSIO: Optional[float] = Field(None, ge=0)
    CALCIO: Optional[float] = Field(None, ge=0)
    MAGNESIO: Optional[float] = Field(None, ge=0)
    ALUMINIO: Optional[float] = Field(None, ge=0)
    H_AL: Optional[float] = Field(None, ge=0)
    CTC: Optional[float] = Field(None, ge=0)
    SATURACAO_BASES: Optional[float] = Field(None, ge=0, le=100)
    SATURACAO_ALUMINIO: Optional[float] = Field(None, ge=0, le=100)

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
    pass


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
    ALUMINIO: Optional[float] = Field(None, ge=0)
    H_AL: Optional[float] = Field(None, ge=0)
    CTC: Optional[float] = Field(None, ge=0)
    SATURACAO_BASES: Optional[float] = Field(None, ge=0, le=100)
    SATURACAO_ALUMINIO: Optional[float] = Field(None, ge=0, le=100)
    ENXOFRE: Optional[float] = Field(None, ge=0)
    BORO: Optional[float] = Field(None, ge=0)
    COBRE: Optional[float] = Field(None, ge=0)
    FERRO: Optional[float] = Field(None, ge=0)
    MANGANES: Optional[float] = Field(None, ge=0)
    ZINCO: Optional[float] = Field(None, ge=0)
    OBSERVACOES: Optional[str] = None
    RECOMENDACOES: Optional[str] = None


class AnalisesSoloResponse(AnalisesSoloBase):
    ID: int
    ARQUIVO_LAUDO: Optional[str] = None
    ID_USUARIO_CADASTRO: int
    DATA_CADASTRO: Optional[datetime] = None

    # Campo relacionado
    terreno_nome: Optional[str] = None

    class Config:
        from_attributes = True
