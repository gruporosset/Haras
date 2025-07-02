# backend/app/models/__init__.py
from .animal import Animal
from .crescimento import HistoricoCrescimento
from .ferrageamento import FerrageamentoMixin, FerrageamentoResumo
from .manejo import (
    AnalisesSolo,
    ManejoTerrenos,
    MovimentacaoProdutoManejo,
    ProdutoManejo,
)
from .medicamento import Medicamento, MovimentacaoMedicamento
from .mfa import MFAConfig
from .movimentacao import MovimentacaoAnimais
from .racao import (
    FornecimentoRacaoAnimal,
    ItemPlanoAlimentar,
    MovimentacaoProdutoRacao,
    PlanoAlimentar,
    ProdutoRacao,
)
from .reproducao import Reproducao
from .saude import SaudeAnimais
from .sessao import Sessao
from .terreno import Terreno
from .user import User

# Garante que todos os modelos são importados e registrados
__all__ = [
    "User",
    "MFAConfig",
    "Sessao",
    "Terreno",
    "Animal",
    "HistoricoCrescimento",
    "Medicamento",
    "MovimentacaoMedicamento",
    "SaudeAnimais",
    "MovimentacaoAnimais",
    "Reproducao",
    "ProdutoManejo",
    "MovimentacaoProdutoManejo",
    "AnalisesSolo",
    "ManejoTerrenos",
    "FerrageamentoResumo",
    "FerrageamentoMixin",
    "ProdutoRacao",
    "MovimentacaoProdutoRacao",
    "PlanoAlimentar",
    "ItemPlanoAlimentar",
    "FornecimentoRacaoAnimal",
]
