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
from .manejo import ProdutoManejo, AnalisesSolo, ManejoTerrenos

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
           'AnalisesSolo',
           'ManejoTerrenos'
           ]
