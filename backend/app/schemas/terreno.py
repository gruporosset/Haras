from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime

class TerrenoBase(BaseModel):
    NOME: str = Field(..., max_length=100)
    AREA_HECTARES: float = Field(..., gt=0, le=9999.9999)
    TIPO_SOLO: Optional[str] = Field(None, max_length=50)
    TOPOGRAFIA: Optional[str] = Field(None, max_length=50)
    TIPO_PASTAGEM: Optional[str] = Field(None, max_length=100)
    CAPACIDADE_ANIMAIS: Optional[int] = Field(None, ge=0, le=999)
    LATITUDE: float = Field(..., ge=-90, le=90)
    LONGITUDE: float = Field(..., ge=-180, le=180)
    STATUS_TERRENO: str = Field('DISPONIVEL', max_length=20)
    OBSERVACOES: Optional[str] = None

class TerrenoCreate(TerrenoBase):
    ID_USUARIO_CADASTRO: int

class TerrenoUpdate(BaseModel):
    NOME: Optional[str] = Field(None, max_length=100)
    AREA_HECTARES: Optional[float] = Field(None, gt=0, le=9999.9999)
    TIPO_SOLO: Optional[str] = Field(None, max_length=50)
    TOPOGRAFIA: Optional[str] = Field(None, max_length=50)
    TIPO_PASTAGEM: Optional[str] = Field(None, max_length=100)
    CAPACIDADE_ANIMAIS: Optional[int] = Field(None, ge=0, le=999)
    LATITUDE: Optional[float] = Field(None, ge=-90, le=90)
    LONGITUDE: Optional[float] = Field(None, ge=-180, le=180)
    STATUS_TERRENO: Optional[str] = Field(None, max_length=20)
    OBSERVACOES: Optional[str] = None

class TerrenoResponse(TerrenoBase):
    ID: int
    ID_USUARIO_CADASTRO: int
    DATA_CADASTRO: Optional[datetime] = None

    @field_serializer('DATA_CADASTRO')
    def serialize_dt(self, dt: datetime | None, _info):
        return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None

    class Config:
        from_attributes = True
