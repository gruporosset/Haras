# backend/app/models/racao.py
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.types import CLOB
from .base import Base


class TipoAlimentoEnum(str, enum.Enum):
    CONCENTRADO = "CONCENTRADO"
    VOLUMOSO = "VOLUMOSO"
    SUPLEMENTO = "SUPLEMENTO"
    PREMIX = "PREMIX"
    SAL_MINERAL = "SAL_MINERAL"


class TipoMovimentacaoRacaoEnum(str, enum.Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"
    AJUSTE = "AJUSTE"


class CategoriaNutricionalEnum(str, enum.Enum):
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


class IntensidadeTrabalhoEnum(str, enum.Enum):
    REPOUSO = "REPOUSO"
    LEVE = "LEVE"
    MODERADO = "MODERADO"
    INTENSO = "INTENSO"


class StatusPlanoEnum(str, enum.Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    SUSPENSO = "SUSPENSO"


class ProdutoRacao(Base):
    __tablename__ = "PRODUTOS_RACAO"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOME = Column(String(100), nullable=False)
    TIPO_ALIMENTO = Column(Enum(TipoAlimentoEnum), nullable=False)
    MARCA = Column(String(100))
    FABRICANTE = Column(String(100))

    # === COMPOSIÇÃO NUTRICIONAL ===
    PROTEINA_BRUTA = Column(Float)  # %
    FIBRA_BRUTA = Column(Float)  # %
    ENERGIA_DIGESTIVEL = Column(Float)  # Mcal/kg
    CALCIO = Column(Float)  # %
    FOSFORO = Column(Float)  # %
    MAGNESIO = Column(Float)  # %
    POTASSIO = Column(Float)  # %
    SODIO = Column(Float)  # %

    # === CONTROLE DE ESTOQUE ===
    ESTOQUE_ATUAL = Column(Float, default=0, nullable=False)
    ESTOQUE_MINIMO = Column(Float, default=0, nullable=False)
    ESTOQUE_MAXIMO = Column(Float)
    UNIDADE_MEDIDA = Column(String(20), default='KG')

    # === DADOS COMERCIAIS ===
    PRECO_UNITARIO = Column(Float)
    FORNECEDOR_PRINCIPAL = Column(String(100))
    CODIGO_FORNECEDOR = Column(String(50))

    # === CONTROLE DE QUALIDADE ===
    LOTE_ATUAL = Column(String(50))
    DATA_FABRICACAO = Column(DateTime)
    DATA_VALIDADE = Column(DateTime)
    REGISTRO_MINISTERIO = Column(String(50))

    # === ARMAZENAMENTO ===
    LOCAL_ARMAZENAMENTO = Column(String(100))
    CONDICOES_ARMAZENAMENTO = Column(String(200))

    OBSERVACOES = Column(CLOB)
    ATIVO = Column(String(1), default='S')
    ID_USUARIO_CADASTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_CADASTRO = Column(DateTime(timezone=True), server_default=func.now())
    DATA_ULTIMA_COMPRA = Column(DateTime)


class MovimentacaoProdutoRacao(Base):
    __tablename__ = "MOVIMENTACAO_PRODUTOS_RACAO"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_PRODUTO = Column(Integer, ForeignKey(
        'PRODUTOS_RACAO.ID'), nullable=False)
    TIPO_MOVIMENTACAO = Column(Enum(TipoMovimentacaoRacaoEnum), nullable=False)

    # === QUANTIDADES ===
    QUANTIDADE = Column(Float, nullable=False)
    QUANTIDADE_ANTERIOR = Column(Float)
    QUANTIDADE_ATUAL = Column(Float)

    # === REFERÊNCIA PARA SAÍDA ===
    ID_FORNECIMENTO_ANIMAL = Column(Integer)
    ID_ANIMAL = Column(Integer, ForeignKey('ANIMAIS.ID'))

    # === DADOS DA ENTRADA ===
    NOTA_FISCAL = Column(String(100))
    FORNECEDOR = Column(String(100))
    PRECO_UNITARIO = Column(Float)
    LOTE = Column(String(50))
    DATA_VALIDADE = Column(DateTime)
    DATA_FABRICACAO = Column(DateTime)

    # === OBSERVAÇÕES ===
    MOTIVO = Column(String(200))
    OBSERVACOES = Column(CLOB)

    ID_USUARIO_REGISTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_REGISTRO = Column(DateTime(timezone=True), server_default=func.now())


class PlanoAlimentar(Base):
    __tablename__ = "PLANOS_ALIMENTARES"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_ANIMAL = Column(Integer, ForeignKey('ANIMAIS.ID'), nullable=False)

    # === CATEGORIA NUTRICIONAL ===
    CATEGORIA_NUTRICIONAL = Column(
        Enum(CategoriaNutricionalEnum), nullable=False)

    # === DADOS DO ANIMAL ===
    PESO_REFERENCIA = Column(Float, nullable=False)
    ESCORE_CORPORAL = Column(Float)  # 1-9
    INTENSIDADE_TRABALHO = Column(Enum(IntensidadeTrabalhoEnum))

    # === PARÂMETROS DO PLANO ===
    QUANTIDADE_DIARIA_TOTAL = Column(Float)  # kg/dia
    NUMERO_REFEICOES = Column(Integer, default=3)
    PERCENTUAL_PESO_VIVO = Column(Float)  # % do peso vivo

    # === PERÍODO DE VIGÊNCIA ===
    DATA_INICIO = Column(DateTime, nullable=False)
    DATA_FIM = Column(DateTime)

    # === STATUS ===
    STATUS_PLANO = Column(Enum(StatusPlanoEnum), default='ATIVO')

    OBSERVACOES = Column(CLOB)
    ID_USUARIO_CADASTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_CADASTRO = Column(DateTime(timezone=True), server_default=func.now())


class ItemPlanoAlimentar(Base):
    __tablename__ = "ITENS_PLANO_ALIMENTAR"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_PLANO = Column(Integer, ForeignKey(
        'PLANOS_ALIMENTARES.ID'), nullable=False)
    ID_PRODUTO = Column(Integer, ForeignKey(
        'PRODUTOS_RACAO.ID'), nullable=False)

    # === QUANTIDADES ===
    QUANTIDADE_POR_REFEICAO = Column(Float, nullable=False)
    QUANTIDADE_DIARIA = Column(Float, nullable=False)
    ORDEM_FORNECIMENTO = Column(Integer)

    # === HORÁRIOS ===
    HORARIO_REFEICAO_1 = Column(String(5))  # HH:MM
    HORARIO_REFEICAO_2 = Column(String(5))
    HORARIO_REFEICAO_3 = Column(String(5))
    HORARIO_REFEICAO_4 = Column(String(5))

    OBSERVACOES = Column(String(500))
    ATIVO = Column(String(1), default='S')


class FornecimentoRacaoAnimal(Base):
    __tablename__ = "FORNECIMENTO_RACAO_ANIMAL"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    ID_ANIMAL = Column(Integer, ForeignKey('ANIMAIS.ID'), nullable=False)
    ID_PRODUTO = Column(Integer, ForeignKey(
        'PRODUTOS_RACAO.ID'), nullable=False)
    ID_PLANO = Column(Integer, ForeignKey('PLANOS_ALIMENTARES.ID'))

    # === DADOS DO FORNECIMENTO ===
    DATA_FORNECIMENTO = Column(DateTime, nullable=False)
    HORARIO_FORNECIMENTO = Column(String(5))  # HH:MM
    NUMERO_REFEICAO = Column(Integer)  # 1-4

    # === QUANTIDADES ===
    QUANTIDADE_PLANEJADA = Column(Float)
    QUANTIDADE_FORNECIDA = Column(Float, nullable=False)
    PESO_ANIMAL_REFERENCIA = Column(Float)

    # === CONTROLE ===
    FUNCIONARIO_RESPONSAVEL = Column(String(100))
    OBSERVACOES = Column(String(500))

    ID_USUARIO_REGISTRO = Column(Integer, ForeignKey('USUARIOS.ID'))
    DATA_REGISTRO = Column(DateTime(timezone=True), server_default=func.now())
