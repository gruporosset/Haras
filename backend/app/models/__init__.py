from .base import Base
from .user import User
from .mfa import MFAConfig
from .terreno import Terreno

# Garante que todos os modelos são importados e registrados
__all__ = ['User', 'Terreno', 'MFAConfig']