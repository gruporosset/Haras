from .base import Base
from .user import User
from .mfa import MFAConfig
from .sessao import Sessao
from .terreno import Terreno
from .animal import Animal

# Garante que todos os modelos são importados e registrados
__all__ = ['User', 'Terreno', 'Animal', 'MFAConfig', 'Sessao']