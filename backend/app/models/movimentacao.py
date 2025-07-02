from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.types import CLOB

from .base import Base


class MovimentacaoAnimais(Base):
    __tablename__ = "MOVIMENTACOES_ANIMAIS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_ANIMAL = Column(Integer, ForeignKey("ANIMAIS.ID"), nullable=False)
    # TRANSFERENCIA, ENTRADA, SAIDA, VENDA, EMPRESTIMO
    TIPO_MOVIMENTACAO = Column(String(50), nullable=False)
    DATA_MOVIMENTACAO = Column(DateTime, nullable=False)
    ID_TERRENO_ORIGEM = Column(Integer, ForeignKey("TERRENOS.ID"))
    ID_TERRENO_DESTINO = Column(Integer, ForeignKey("TERRENOS.ID"))
    ORIGEM_EXTERNA = Column(String(100))  # Para origens fora da fazenda
    DESTINO_EXTERNO = Column(String(100))  # Para destinos fora da fazenda
    MOTIVO = Column(String(200))
    OBSERVACOES = Column(CLOB)
    ID_USUARIO_REGISTRO = Column(Integer, ForeignKey("USUARIOS.ID"))
    DATA_REGISTRO = Column(DateTime(timezone=True), server_default=func.now())
