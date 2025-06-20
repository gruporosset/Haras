from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional
from datetime import datetime
from enum import Enum

class TipoMovimentacaoEnum(str, Enum):
    TRANSFERENCIA = "TRANSFERENCIA"
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    VENDA = "VENDA"
    EMPRESTIMO = "EMPRESTIMO"
    RETORNO = "RETORNO"

class MovimentacaoBase(BaseModel):
    ID_ANIMAL: int
    TIPO_MOVIMENTACAO: TipoMovimentacaoEnum
    DATA_MOVIMENTACAO: datetime
    ID_TERRENO_ORIGEM: Optional[int] = None
    ID_TERRENO_DESTINO: Optional[int] = None
    ORIGEM_EXTERNA: Optional[str] = Field(None, max_length=100)
    DESTINO_EXTERNO: Optional[str] = Field(None, max_length=100)
    MOTIVO: Optional[str] = Field(None, max_length=200)
    OBSERVACOES: Optional[str] = None

class MovimentacaoCreate(MovimentacaoBase):
    ID_USUARIO_REGISTRO: int

    @field_validator('DATA_MOVIMENTACAO')
    @classmethod
    def validate_data_movimentacao(cls, v):
        if v > datetime.now():
            raise ValueError('Data de movimentação não pode ser no futuro')
        return v

    @field_validator('ID_TERRENO_DESTINO')
    @classmethod
    def validate_destino(cls, v, info):
        # Validar que não seja o mesmo terreno de origem
        if v and info.data.get('ID_TERRENO_ORIGEM') and v == info.data['ID_TERRENO_ORIGEM']:
            raise ValueError('Terreno de destino deve ser diferente da origem')
        return v

class MovimentacaoUpdate(BaseModel):
    TIPO_MOVIMENTACAO: Optional[TipoMovimentacaoEnum] = None
    DATA_MOVIMENTACAO: Optional[datetime] = None
    ID_TERRENO_ORIGEM: Optional[int] = None
    ID_TERRENO_DESTINO: Optional[int] = None
    ORIGEM_EXTERNA: Optional[str] = Field(None, max_length=100)
    DESTINO_EXTERNO: Optional[str] = Field(None, max_length=100)
    MOTIVO: Optional[str] = Field(None, max_length=200)
    OBSERVACOES: Optional[str] = None
    ID_USUARIO_REGISTRO: Optional[int] = None

class MovimentacaoResponse(MovimentacaoBase):
    ID: int
    ID_USUARIO_REGISTRO: int
    DATA_REGISTRO: Optional[datetime] = None
    
    # Campos relacionados para exibição
    animal_nome: Optional[str] = None
    terreno_origem_nome: Optional[str] = None
    terreno_destino_nome: Optional[str] = None

    @field_serializer('DATA_MOVIMENTACAO', 'DATA_REGISTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else None

    class Config:
        from_attributes = True

# Schemas para relatórios
class LocalizacaoAtual(BaseModel):
    animal_id: int
    animal_nome: str
    terreno_atual: Optional[str] = None
    local_externo: Optional[str] = None
    data_ultima_movimentacao: datetime
    tipo_ultima_movimentacao: str

class HistoricoMovimentacao(BaseModel):
    movimentacoes: list[MovimentacaoResponse]
    localizacao_atual: Optional[str] = None