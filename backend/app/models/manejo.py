# backend/app/models/manejo.py
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.types import CLOB
from .base import Base


class TipoProdutoEnum(str, enum.Enum):
    FERTILIZANTE = "FERTILIZANTE"
    DEFENSIVO = "DEFENSIVO"
    CORRETIVO = "CORRETIVO"
    SEMENTE = "SEMENTE"


class ProdutoManejo(Base):
    __tablename__ = "PRODUTOS_MANEJO"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOME = Column(String(100), nullable=False)
    TIPO_PRODUTO = Column(Enum(TipoProdutoEnum), nullable=False)
    PRINCIPIO_ATIVO = Column(String(200))
    CONCENTRACAO = Column(String(50))
    UNIDADE_MEDIDA = Column(String(20), nullable=False)  # KG, L, T, SC
    FABRICANTE = Column(String(100))
    REGISTRO_MINISTERIO = Column(String(50))
    OBSERVACOES = Column(CLOB)
    ATIVO = Column(String(1), default='S')
    ID_USUARIO_CADASTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_CADASTRO = Column(DateTime(timezone=True), server_default=func.now())


class AnalisesSolo(Base):
    __tablename__ = "ANALISES_SOLO"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_TERRENO = Column(Integer, ForeignKey('TERRENOS.ID'), nullable=False)
    DATA_COLETA = Column(DateTime, nullable=False)
    DATA_RESULTADO = Column(DateTime)
    LABORATORIO = Column(String(100))

    # Parâmetros químicos principais
    PH_AGUA = Column(Float)  # pH em água
    PH_CACL2 = Column(Float)  # pH em CaCl2
    MATERIA_ORGANICA = Column(Float)  # %
    FOSFORO = Column(Float)  # mg/dm³
    POTASSIO = Column(Float)  # cmolc/dm³
    CALCIO = Column(Float)  # cmolc/dm³
    MAGNESIO = Column(Float)  # cmolc/dm³
    ALUMINIO = Column(Float)  # cmolc/dm³
    H_AL = Column(Float)  # H+Al cmolc/dm³
    CTC = Column(Float)  # Capacidade de Troca Catiônica
    SATURACAO_BASES = Column(Float)  # %
    SATURACAO_ALUMINIO = Column(Float)  # %

    # Micronutrientes
    ENXOFRE = Column(Float)  # mg/dm³
    BORO = Column(Float)  # mg/dm³
    COBRE = Column(Float)  # mg/dm³
    FERRO = Column(Float)  # mg/dm³
    MANGANES = Column(Float)  # mg/dm³
    ZINCO = Column(Float)  # mg/dm³

    OBSERVACOES = Column(CLOB)
    RECOMENDACOES = Column(CLOB)
    ARQUIVO_LAUDO = Column(String(500))  # Path do PDF
    ID_USUARIO_CADASTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_CADASTRO = Column(DateTime(timezone=True), server_default=func.now())


class ManejoTerrenos(Base):
    __tablename__ = "MANEJO_TERRENOS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_TERRENO = Column(Integer, ForeignKey('TERRENOS.ID'), nullable=False)
    ID_PRODUTO = Column(Integer, ForeignKey(
        'PRODUTOS_MANEJO.ID'), nullable=False)
    # ADUBACAO, CALAGEM, PLANTIO, APLICACAO_DEFENSIVO
    TIPO_MANEJO = Column(String(50), nullable=False)
    DATA_APLICACAO = Column(DateTime, nullable=False)
    QUANTIDADE = Column(Float, nullable=False)  # Quantidade aplicada
    UNIDADE_MEDIDA = Column(String(20), nullable=False)  # KG/HA, L/HA, T/HA
    DOSE_HECTARE = Column(Float)  # Dose por hectare
    AREA_APLICADA = Column(Float)  # Hectares aplicados
    CUSTO_TOTAL = Column(Float)  # Custo total da aplicação
    EQUIPAMENTO_UTILIZADO = Column(String(100))
    CONDICOES_CLIMATICAS = Column(String(200))
    PERIODO_CARENCIA = Column(Integer)  # Dias sem animais
    DATA_LIBERACAO = Column(DateTime)  # Calculado automaticamente
    OBSERVACOES = Column(CLOB)
    ID_USUARIO_REGISTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_REGISTRO = Column(DateTime(timezone=True), server_default=func.now())
