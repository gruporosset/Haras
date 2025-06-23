from .base import Base
from .user import User
from .mfa import MFAConfig
from .sessao import Sessao
from .terreno import Terreno
from .animal import Animal
from .crescimento import HistoricoCrescimento
from .saude import SaudeAnimais
from .movimentacao import MovimentacaoAnimais
from .reproducao import Reproducao

# Garante que todos os modelos são importados e registrados
__all__ = ['User', 'Terreno', 'Animal', 'HistoricoCrescimento',
           'SaudeAnimais', 'MovimentacaoAnimais', 'MFAConfig', 'Sessao', 'Reproducao']
