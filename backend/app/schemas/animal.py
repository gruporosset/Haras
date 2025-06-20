from pydantic import BaseModel, Field, field_serializer, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class SexoEnum(str, Enum):
    M = "M"
    F = "F"

class StatusAnimalEnum(str, Enum):
    ATIVO = "ATIVO"
    VENDIDO = "VENDIDO"
    MORTO = "MORTO"
    EMPRESTADO = "EMPRESTADO"

class AnimalBase(BaseModel):
    NOME: str = Field(..., max_length=100)
    NUMERO_REGISTRO: Optional[str] = Field(None, max_length=50)
    CHIP_IDENTIFICACAO: Optional[str] = Field(None, max_length=50)
    SEXO: Optional[SexoEnum] = None
    DATA_NASCIMENTO: Optional[datetime] = None
    PELAGEM: Optional[str] = Field(None, max_length=50)
    STATUS_ANIMAL: StatusAnimalEnum = StatusAnimalEnum.ATIVO
    ID_PAI: Optional[int] = None
    ID_MAE: Optional[int] = None
    ORIGEM: Optional[str] = Field(None, max_length=100)
    OBSERVACOES: Optional[str] = None
    PESO_ATUAL: Optional[float] = Field(None, ge=0)
    FOTO_PRINCIPAL: Optional[str] = Field(None, max_length=500)

class AnimalCreate(AnimalBase):
    ID_USUARIO_CADASTRO: int

    @field_validator('NUMERO_REGISTRO', 'CHIP_IDENTIFICACAO')
    def validate_unique_fields(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v

class AnimalUpdate(BaseModel):
    NOME: Optional[str] = Field(None, max_length=100)
    NUMERO_REGISTRO: Optional[str] = Field(None, max_length=50)
    CHIP_IDENTIFICACAO: Optional[str] = Field(None, max_length=50)
    SEXO: Optional[SexoEnum] = None
    DATA_NASCIMENTO: Optional[datetime] = None
    PELAGEM: Optional[str] = Field(None, max_length=50)
    STATUS_ANIMAL: Optional[StatusAnimalEnum] = None
    ID_PAI: Optional[int] = None
    ID_MAE: Optional[int] = None
    ORIGEM: Optional[str] = Field(None, max_length=100)
    OBSERVACOES: Optional[str] = None
    PESO_ATUAL: Optional[float] = Field(None, ge=0)
    FOTO_PRINCIPAL: Optional[str] = Field(None, max_length=500)
    ID_USUARIO_ALTERACAO: Optional[int] = None

class AnimalResponse(AnimalBase):
    ID: int
    ID_USUARIO_CADASTRO: int
    DATA_CADASTRO: Optional[datetime] = None
    ID_USUARIO_ALTERACAO: Optional[int] = None
    DATA_ALTERACAO: Optional[datetime] = None

    @field_serializer('DATA_NASCIMENTO', 'DATA_CADASTRO', 'DATA_ALTERACAO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%Y-%m-%d") if dt else None

    class Config:
        from_attributes = True

class AnimalGenealogia(BaseModel):
    animal: AnimalResponse
    pai: Optional['AnimalGenealogia'] = None
    mae: Optional['AnimalGenealogia'] = None
    
    class Config:
        from_attributes = True

# Upload de foto
class FotoUploadResponse(BaseModel):
    filename: str
    url: str
    message: str