# backend/app/models/__init__.py
from .base import Base
from .user import User
from .mfa import MFAConfig
from .sessao import Sessao
from .terreno import Terreno
from .animal import Animal
from .crescimento import HistoricoCrescimento
from .medicamento import Medicamento, MovimentacaoMedicamento
from .saude import SaudeAnimais
from .movimentacao import MovimentacaoAnimais
from .reproducao import Reproducao
from .manejo import ProdutoManejo, MovimentacaoProdutoManejo, AnalisesSolo, ManejoTerrenos
from .ferrageamento import FerrageamentoResumo, FerrageamentoMixin
from .racao import (
    ProdutoRacao, MovimentacaoProdutoRacao, PlanoAlimentar,
    ItemPlanoAlimentar, FornecimentoRacaoAnimal
)
# Garante que todos os modelos são importados e registrados
__all__ = ['User',
           'MFAConfig',
           'Sessao',
           'Terreno',
           'Animal',
           'HistoricoCrescimento',
           'Medicamento',
           'MovimentacaoMedicamento',
           'SaudeAnimais',
           'MovimentacaoAnimais',
           'Reproducao',
           'ProdutoManejo',
           'MovimentacaoProdutoManejo',
           'AnalisesSolo',
           'ManejoTerrenos',
           'FerrageamentoResumo',
           'FerrageamentoMixin',
           'ProdutoRacao',
           'MovimentacaoProdutoRacao',
           'PlanoAlimentar',
           'ItemPlanoAlimentar',
           'FornecimentoRacaoAnimal'
           ]
