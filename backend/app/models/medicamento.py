# backend/app/models/medicamento.py
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.types import CLOB
from .base import Base


class FormaFarmaceuticaEnum(str, enum.Enum):
    INJETAVEL = "INJETAVEL"
    ORAL = "ORAL"
    TOPICO = "TOPICO"


class TipoMovimentacaoEnum(str, enum.Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE = "AJUSTE"


class Medicamento(Base):
    __tablename__ = "MEDICAMENTOS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOME = Column(String(200), nullable=False)
    PRINCIPIO_ATIVO = Column(String(200))
    CONCENTRACAO = Column(String(100))
    FORMA_FARMACEUTICA = Column(Enum(FormaFarmaceuticaEnum))
    FABRICANTE = Column(String(100))
    REGISTRO_MAPA = Column(String(50))

    # Controle de Estoque
    ESTOQUE_ATUAL = Column(Float, default=0)
    ESTOQUE_MINIMO = Column(Float, default=0)
    # ML, G, COMPRIMIDO, DOSE
    UNIDADE_MEDIDA = Column(String(20), nullable=False)

    # Validade e Lote
    LOTE_ATUAL = Column(String(50))
    DATA_VALIDADE = Column(DateTime)
    DATA_FABRICACAO = Column(DateTime)

    # Custos
    PRECO_UNITARIO = Column(Float)
    FORNECEDOR = Column(String(100))

    # Prescrição
    REQUER_RECEITA = Column(String(1), default='N')
    PERIODO_CARENCIA = Column(Integer)  # dias para abate

    OBSERVACOES = Column(CLOB)
    ATIVO = Column(String(1), default='S')
    ID_USUARIO_CADASTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_CADASTRO = Column(DateTime(timezone=True), server_default=func.now())


class MovimentacaoMedicamento(Base):
    __tablename__ = "MOVIMENTACAO_MEDICAMENTOS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_MEDICAMENTO = Column(Integer, ForeignKey(
        'MEDICAMENTOS.ID'), nullable=False)
    TIPO_MOVIMENTACAO = Column(Enum(TipoMovimentacaoEnum), nullable=False)
    QUANTIDADE = Column(Float, nullable=False)
    QUANTIDADE_ANTERIOR = Column(Float)
    QUANTIDADE_ATUAL = Column(Float)

    # Referência para saída (aplicação em animal)
    ID_ANIMAL = Column(Integer, ForeignKey('ANIMAIS.ID'))
    ID_SAUDE_ANIMAL = Column(Integer, ForeignKey('SAUDE_ANIMAIS.ID'))

    # Dados da entrada (compra)
    NOTA_FISCAL = Column(String(100))
    FORNECEDOR = Column(String(100))
    PRECO_UNITARIO = Column(Float)
    LOTE = Column(String(50))
    DATA_VALIDADE = Column(DateTime)

    MOTIVO = Column(String(200))
    OBSERVACOES = Column(CLOB)
    ID_USUARIO_REGISTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_REGISTRO = Column(DateTime(timezone=True), server_default=func.now())
