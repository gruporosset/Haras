# backend/app/schemas/racao.py
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_serializer, model_validator


class TipoAlimentoEnum(str, Enum):
    CONCENTRADO = "CONCENTRADO"
    VOLUMOSO = "VOLUMOSO"
    SUPLEMENTO = "SUPLEMENTO"
    PREMIX = "PREMIX"
    SAL_MINERAL = "SAL_MINERAL"


class TipoMovimentacaoRacaoEnum(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE = "AJUSTE"


class CategoriaNutricionalEnum(str, Enum):
    POTRO = "POTRO"
    JOVEM = "JOVEM"
    ADULTO_MANUTENCAO = "ADULTO_MANUTENCAO"
    ADULTO_TRABALHO_LEVE = "ADULTO_TRABALHO_LEVE"
    ADULTO_TRABALHO_MODERADO = "ADULTO_TRABALHO_MODERADO"
    ADULTO_TRABALHO_INTENSO = "ADULTO_TRABALHO_INTENSO"
    EGUA_GESTANTE = "EGUA_GESTANTE"
    EGUA_LACTANTE = "EGUA_LACTANTE"
    REPRODUTOR = "REPRODUTOR"
    IDOSO = "IDOSO"


class IntensidadeTrabalhoEnum(str, Enum):
    REPOUSO = "REPOUSO"
    LEVE = "LEVE"
    MODERADO = "MODERADO"
    INTENSO = "INTENSO"


class StatusPlanoEnum(str, Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    SUSPENSO = "SUSPENSO"


class StatusEstoqueRacaoEnum(str, Enum):
    SEM_ESTOQUE = "SEM_ESTOQUE"
    ESTOQUE_BAIXO = "ESTOQUE_BAIXO"
    VENCIMENTO_PROXIMO = "VENCIMENTO_PROXIMO"
    VENCIDO = "VENCIDO"
    OK = "OK"


# === PRODUTO RAÇÃO SCHEMAS ===
class ProdutoRacaoBase(BaseModel):
    NOME: str = Field(..., max_length=100)
    TIPO_ALIMENTO: TipoAlimentoEnum
    MARCA: Optional[str] = Field(None, max_length=100)
    FABRICANTE: Optional[str] = Field(None, max_length=100)

    # Composição nutricional
    PROTEINA_BRUTA: Optional[float] = Field(None, ge=0, le=100)
    FIBRA_BRUTA: Optional[float] = Field(None, ge=0, le=100)
    ENERGIA_DIGESTIVEL: Optional[float] = Field(None, ge=0)
    CALCIO: Optional[float] = Field(None, ge=0, le=100)
    FOSFORO: Optional[float] = Field(None, ge=0, le=100)
    MAGNESIO: Optional[float] = Field(None, ge=0, le=100)
    POTASSIO: Optional[float] = Field(None, ge=0, le=100)
    SODIO: Optional[float] = Field(None, ge=0, le=100)

    # Controle de estoque
    ESTOQUE_ATUAL: float = Field(default=0, ge=0)
    ESTOQUE_MINIMO: float = Field(default=0, ge=0)
    ESTOQUE_MAXIMO: Optional[float] = Field(None, ge=0)
    UNIDADE_MEDIDA: str = Field(default="KG", max_length=20)

    # Dados comerciais
    PRECO_UNITARIO: Optional[float] = Field(None, ge=0)
    FORNECEDOR_PRINCIPAL: Optional[str] = Field(None, max_length=100)
    CODIGO_FORNECEDOR: Optional[str] = Field(None, max_length=50)

    # Controle de qualidade
    LOTE_ATUAL: Optional[str] = Field(None, max_length=50)
    DATA_FABRICACAO: Optional[datetime] = None
    DATA_VALIDADE: Optional[datetime] = None
    REGISTRO_MINISTERIO: Optional[str] = Field(None, max_length=50)

    # Armazenamento
    LOCAL_ARMAZENAMENTO: Optional[str] = Field(None, max_length=100)
    CONDICOES_ARMAZENAMENTO: Optional[str] = Field(None, max_length=200)

    OBSERVACOES: Optional[str] = None

    @model_validator(mode="after")
    def validar_estoques(self):
        if (
            self.ESTOQUE_MAXIMO is not None
            and self.ESTOQUE_MAXIMO <= self.ESTOQUE_MINIMO
        ):
            raise ValueError("Estoque máximo deve ser maior que o mínimo")
        return self

    @model_validator(mode="after")
    def validar_datas(self):
        if (
            self.DATA_FABRICACAO
            and self.DATA_VALIDADE
            and self.DATA_FABRICACAO >= self.DATA_VALIDADE
        ):
            raise ValueError("Data de fabricação deve ser anterior à validade")
        return self

    @field_serializer("DATA_FABRICACAO", "DATA_VALIDADE")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None


class ProdutoRacaoCreate(ProdutoRacaoBase):
    pass


class ProdutoRacaoUpdate(BaseModel):
    NOME: Optional[str] = Field(None, max_length=100)
    TIPO_ALIMENTO: Optional[TipoAlimentoEnum] = None
    MARCA: Optional[str] = Field(None, max_length=100)
    FABRICANTE: Optional[str] = Field(None, max_length=100)
    PROTEINA_BRUTA: Optional[float] = Field(None, ge=0, le=100)
    FIBRA_BRUTA: Optional[float] = Field(None, ge=0, le=100)
    ENERGIA_DIGESTIVEL: Optional[float] = Field(None, ge=0)
    CALCIO: Optional[float] = Field(None, ge=0, le=100)
    FOSFORO: Optional[float] = Field(None, ge=0, le=100)
    MAGNESIO: Optional[float] = Field(None, ge=0, le=100)
    POTASSIO: Optional[float] = Field(None, ge=0, le=100)
    SODIO: Optional[float] = Field(None, ge=0, le=100)
    ESTOQUE_MINIMO: Optional[float] = Field(None, ge=0)
    ESTOQUE_MAXIMO: Optional[float] = Field(None, ge=0)
    UNIDADE_MEDIDA: Optional[str] = Field(None, max_length=20)
    PRECO_UNITARIO: Optional[float] = Field(None, ge=0)
    FORNECEDOR_PRINCIPAL: Optional[str] = Field(None, max_length=100)
    CODIGO_FORNECEDOR: Optional[str] = Field(None, max_length=50)
    LOTE_ATUAL: Optional[str] = Field(None, max_length=50)
    DATA_FABRICACAO: Optional[datetime] = None
    DATA_VALIDADE: Optional[datetime] = None
    REGISTRO_MINISTERIO: Optional[str] = Field(None, max_length=50)
    LOCAL_ARMAZENAMENTO: Optional[str] = Field(None, max_length=100)
    CONDICOES_ARMAZENAMENTO: Optional[str] = Field(None, max_length=200)
    OBSERVACOES: Optional[str] = None


class ProdutoRacaoResponse(ProdutoRacaoBase):
    ID: int
    ID_USUARIO_CADASTRO: int
    DATA_CADASTRO: Optional[datetime] = None
    DATA_ULTIMA_COMPRA: Optional[datetime] = None
    ATIVO: str

    # Campos calculados
    status_estoque: Optional[StatusEstoqueRacaoEnum] = None
    dias_vencimento: Optional[int] = None
    valor_total_estoque: Optional[float] = None

    class Config:
        from_attributes = True


# === MOVIMENTAÇÃO ESTOQUE SCHEMAS ===
class MovimentacaoRacaoBase(BaseModel):
    ID_PRODUTO: int
    TIPO_MOVIMENTACAO: TipoMovimentacaoRacaoEnum
    QUANTIDADE: float = Field(..., gt=0)

    # Dados da entrada
    NOTA_FISCAL: Optional[str] = Field(None, max_length=100)
    FORNECEDOR: Optional[str] = Field(None, max_length=100)
    PRECO_UNITARIO: Optional[float] = Field(None, ge=0)
    LOTE: Optional[str] = Field(None, max_length=50)
    DATA_VALIDADE: Optional[datetime] = None
    DATA_FABRICACAO: Optional[datetime] = None

    MOTIVO: Optional[str] = Field(None, max_length=200)
    OBSERVACOES: Optional[str] = None

    @model_validator(mode="after")
    def validar_datas(self):
        if (
            self.DATA_FABRICACAO
            and self.DATA_VALIDADE
            and self.DATA_FABRICACAO >= self.DATA_VALIDADE
        ):
            raise ValueError("Data de fabricação deve ser anterior à validade")
        return self


class EntradaRacaoCreate(MovimentacaoRacaoBase):
    TIPO_MOVIMENTACAO: TipoMovimentacaoRacaoEnum = Field(
        default=TipoMovimentacaoRacaoEnum.ENTRADA
    )
    NOTA_FISCAL: str = Field(..., max_length=100)
    FORNECEDOR: str = Field(..., max_length=100)
    PRECO_UNITARIO: float = Field(..., ge=0)
    LOTE: str = Field(..., max_length=50)


class SaidaRacaoCreate(BaseModel):
    ID_PRODUTO: int
    QUANTIDADE: float = Field(..., gt=0)
    ID_ANIMAL: Optional[int] = None
    MOTIVO: str = Field(..., max_length=200)
    OBSERVACOES: Optional[str] = None


class AjusteRacaoCreate(BaseModel):
    ID_PRODUTO: int
    QUANTIDADE_NOVA: float = Field(..., ge=0)
    MOTIVO: str = Field(..., max_length=200)
    OBSERVACOES: Optional[str] = None


class MovimentacaoRacaoResponse(MovimentacaoRacaoBase):
    ID: int
    QUANTIDADE_ANTERIOR: Optional[float] = None
    QUANTIDADE_ATUAL: Optional[float] = None
    ID_FORNECIMENTO_ANIMAL: Optional[int] = None
    ID_ANIMAL: Optional[int] = None
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    # Campos relacionados
    produto_nome: Optional[str] = None
    produto_unidade: Optional[str] = None
    animal_nome: Optional[str] = None

    class Config:
        from_attributes = True


# === PLANO ALIMENTAR SCHEMAS ===
class PlanoAlimentarBase(BaseModel):
    ID_ANIMAL: int
    CATEGORIA_NUTRICIONAL: CategoriaNutricionalEnum
    PESO_REFERENCIA: float = Field(..., gt=0)
    ESCORE_CORPORAL: Optional[float] = Field(None, ge=1, le=9)
    INTENSIDADE_TRABALHO: Optional[IntensidadeTrabalhoEnum] = None
    QUANTIDADE_DIARIA_TOTAL: Optional[float] = Field(None, gt=0)
    NUMERO_REFEICOES: int = Field(default=3, ge=1, le=4)
    PERCENTUAL_PESO_VIVO: Optional[float] = Field(None, gt=0, le=100)
    DATA_INICIO: datetime
    DATA_FIM: Optional[datetime] = None
    STATUS_PLANO: StatusPlanoEnum = StatusPlanoEnum.ATIVO
    OBSERVACOES: Optional[str] = None

    @model_validator(mode="after")
    def validar_periodo(self):
        if self.DATA_FIM and self.DATA_FIM <= self.DATA_INICIO:
            raise ValueError("Data fim deve ser posterior à data início")
        return self


class PlanoAlimentarCreate(PlanoAlimentarBase):
    pass


class PlanoAlimentarUpdate(BaseModel):
    CATEGORIA_NUTRICIONAL: Optional[CategoriaNutricionalEnum] = None
    PESO_REFERENCIA: Optional[float] = Field(None, gt=0)
    ESCORE_CORPORAL: Optional[float] = Field(None, ge=1, le=9)
    INTENSIDADE_TRABALHO: Optional[IntensidadeTrabalhoEnum] = None
    QUANTIDADE_DIARIA_TOTAL: Optional[float] = Field(None, gt=0)
    NUMERO_REFEICOES: Optional[int] = Field(None, ge=1, le=4)
    PERCENTUAL_PESO_VIVO: Optional[float] = Field(None, gt=0, le=100)
    DATA_FIM: Optional[datetime] = None
    STATUS_PLANO: Optional[StatusPlanoEnum] = None
    OBSERVACOES: Optional[str] = None


class PlanoAlimentarResponse(PlanoAlimentarBase):
    ID: int
    ID_USUARIO_CADASTRO: int
    DATA_CADASTRO: Optional[datetime] = None

    # Campos relacionados
    animal_nome: Optional[str] = None
    animal_numero_registro: Optional[str] = None
    total_produtos: Optional[int] = None
    custo_diario_estimado: Optional[float] = None

    class Config:
        from_attributes = True


# === ITEM PLANO ALIMENTAR SCHEMAS ===
class ItemPlanoAlimentarBase(BaseModel):
    ID_PLANO: int
    ID_PRODUTO: int
    QUANTIDADE_POR_REFEICAO: float = Field(..., gt=0)
    QUANTIDADE_DIARIA: float = Field(..., gt=0)
    ORDEM_FORNECIMENTO: Optional[int] = Field(None, ge=1, le=100)
    HORARIO_REFEICAO_1: Optional[str] = Field(
        None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    HORARIO_REFEICAO_2: Optional[str] = Field(
        None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    HORARIO_REFEICAO_3: Optional[str] = Field(
        None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    HORARIO_REFEICAO_4: Optional[str] = Field(
        None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    OBSERVACOES: Optional[str] = Field(None, max_length=500)


class ItemPlanoAlimentarCreate(ItemPlanoAlimentarBase):
    pass


class ItemPlanoAlimentarUpdate(BaseModel):
    QUANTIDADE_POR_REFEICAO: Optional[float] = Field(None, gt=0)
    QUANTIDADE_DIARIA: Optional[float] = Field(None, gt=0)
    ORDEM_FORNECIMENTO: Optional[int] = Field(None, ge=1, le=100)
    HORARIO_REFEICAO_1: Optional[str] = Field(
        None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    HORARIO_REFEICAO_2: Optional[str] = Field(
        None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    HORARIO_REFEICAO_3: Optional[str] = Field(
        None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    HORARIO_REFEICAO_4: Optional[str] = Field(
        None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    OBSERVACOES: Optional[str] = Field(None, max_length=500)
    ATIVO: Optional[str] = Field(None, pattern="^[SN]$")


class ItemPlanoAlimentarResponse(ItemPlanoAlimentarBase):
    ID: int
    ATIVO: str

    # Campos relacionados
    produto_nome: Optional[str] = None
    produto_unidade: Optional[str] = None
    produto_tipo: Optional[str] = None
    custo_diario: Optional[float] = None

    class Config:
        from_attributes = True


# === FORNECIMENTO SCHEMAS ===
class FornecimentoRacaoBase(BaseModel):
    ID_ANIMAL: int
    ID_PRODUTO: int
    ID_PLANO: Optional[int] = None
    DATA_FORNECIMENTO: datetime
    HORARIO_FORNECIMENTO: Optional[str] = Field(
        None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    NUMERO_REFEICAO: Optional[int] = Field(None, ge=1, le=4)
    QUANTIDADE_PLANEJADA: Optional[float] = Field(None, gt=0)
    QUANTIDADE_FORNECIDA: float = Field(..., gt=0)
    PESO_ANIMAL_REFERENCIA: Optional[float] = Field(None, gt=0)
    FUNCIONARIO_RESPONSAVEL: Optional[str] = Field(None, max_length=100)
    OBSERVACOES: Optional[str] = Field(None, max_length=500)


class FornecimentoRacaoCreate(FornecimentoRacaoBase):
    pass


class FornecimentoRacaoUpdate(BaseModel):
    DATA_FORNECIMENTO: datetime
    HORARIO_FORNECIMENTO: Optional[str] = Field(
        None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    NUMERO_REFEICAO: Optional[int] = Field(None, ge=1, le=4)
    QUANTIDADE_PLANEJADA: Optional[float] = Field(None, gt=0)
    QUANTIDADE_FORNECIDA: Optional[float] = Field(None, gt=0)
    PESO_ANIMAL_REFERENCIA: Optional[float] = Field(None, gt=0)
    FUNCIONARIO_RESPONSAVEL: Optional[str] = Field(None, max_length=100)
    OBSERVACOES: Optional[str] = Field(None, max_length=500)


class FornecimentoRacaoResponse(FornecimentoRacaoBase):
    ID: int
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None

    # Campos relacionados
    animal_nome: Optional[str] = None
    animal_numero_registro: Optional[str] = None
    produto_nome: Optional[str] = None
    produto_unidade: Optional[str] = None
    custo_fornecimento: Optional[float] = None

    @field_serializer("DATA_FORNECIMENTO")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None

    class Config:
        from_attributes = True


# === RELATÓRIOS E ANÁLISES ===
class EstoqueRacaoBaixo(BaseModel):
    produto_id: int
    nome: str
    tipo_alimento: TipoAlimentoEnum
    estoque_atual: float
    estoque_minimo: float
    unidade_medida: str
    status_alerta: StatusEstoqueRacaoEnum
    dias_vencimento: Optional[int] = None
    fornecedor_principal: Optional[str] = None


class ConsumoAnimalResumo(BaseModel):
    animal_id: int
    animal_nome: str
    numero_registro: str
    produto_nome: str
    tipo_alimento: TipoAlimentoEnum
    total_consumido: float
    media_diaria: float
    custo_total: float
    ultima_refeicao: Optional[datetime] = None


class PrevisaoConsumoRacao(BaseModel):
    produto_id: int
    produto_nome: str
    consumo_diario_medio: float
    estoque_atual: float
    dias_restantes: int
    data_prevista_fim: datetime
    recomendacao: str


class ProdutoRacaoAutocomplete(BaseModel):
    value: int
    label: str
    nome: str
    estoque_atual: float
    unidade_medida: str
    tipo_alimento: TipoAlimentoEnum
    status_estoque: StatusEstoqueRacaoEnum


class CalculoNutricional(BaseModel):
    categoria_nutricional: CategoriaNutricionalEnum
    peso_animal: float
    quantidade_sugerida_kg: float
    percentual_peso_vivo: float
    distribuicao_refeicoes: dict
    observacoes_nutricionais: str
