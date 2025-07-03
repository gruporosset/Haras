from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_serializer, field_validator


class SexoEnum(str, Enum):
    M = "M"
    F = "F"


class StatusAnimalEnum(str, Enum):
    ATIVO = "ATIVO"
    VENDIDO = "VENDIDO"
    MORTO = "MORTO"
    EMPRESTADO = "EMPRESTADO"
    APOSENTADO = "APOSENTADO"


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
    PROPRIETARIO: Optional[str] = Field(None, max_length=200)
    CONTATO_PROPRIETARIO: Optional[str] = Field(None, max_length=200)
    CPF_CNPJ_PROPRIETARIO: Optional[str] = Field(None, max_length=20)


class AnimalCreate(AnimalBase):
    ID_USUARIO_CADASTRO: int

    @field_validator("NUMERO_REGISTRO", "CHIP_IDENTIFICACAO")
    @classmethod
    def validate_unique_fields(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v

    @field_validator("CPF_CNPJ_PROPRIETARIO")
    @classmethod
    def validate_cpf_cnpj(cls, v):
        if v and len(v.strip()) == 0:
            return None
        # Remove formatação
        if v:
            v = "".join(filter(str.isdigit, v))
            if len(v) not in [11, 14]:  # CPF tem 11 dígitos, CNPJ tem 14
                raise ValueError("CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos")
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
    PROPRIETARIO: Optional[str] = Field(None, max_length=200)
    CONTATO_PROPRIETARIO: Optional[str] = Field(None, max_length=200)
    CPF_CNPJ_PROPRIETARIO: Optional[str] = Field(None, max_length=20)
    ID_USUARIO_ALTERACAO: Optional[int] = None

    @field_validator("CPF_CNPJ_PROPRIETARIO")
    @classmethod
    def validate_cpf_cnpj(cls, v):
        if v and len(v.strip()) == 0:
            return None
        # Remove formatação
        if v:
            v = "".join(filter(str.isdigit, v))
            if len(v) not in [11, 14]:  # CPF tem 11 dígitos, CNPJ tem 14
                raise ValueError("CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos")
        return v


class AnimalResponse(AnimalBase):
    ID: int
    ID_USUARIO_CADASTRO: int
    DATA_CADASTRO: Optional[datetime] = None
    ID_USUARIO_ALTERACAO: Optional[int] = None
    DATA_ALTERACAO: Optional[datetime] = None

    @field_serializer("DATA_NASCIMENTO", "DATA_CADASTRO", "DATA_ALTERACAO")
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%d/%m/%Y") if dt else None

    class Config:
        from_attributes = True


class AnimalGenealogia(BaseModel):
    animal: AnimalResponse
    pai: Optional["AnimalGenealogia"] = None
    mae: Optional["AnimalGenealogia"] = None

    class Config:
        from_attributes = True


# Upload de foto


class FotoUploadResponse(BaseModel):
    filename: str
    url: str
    message: str
