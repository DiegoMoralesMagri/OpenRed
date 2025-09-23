# OpenRed Central-API Package# Package src

# Package for ultra-minimalist P2P node directory
# Paquete para directorio de nodos P2P ultra-minimalista
# 超极简P2P节点目录包

__version__ = "3.0.0"
__description__ = "Ultra-minimalist Central-API for OpenRed P2P network"
__philosophy__ = "Code maison whenever possible"

# Export des composants principaux
# Export main components
# Exportar componentes principales
# 导出主要组件
from .core.config import app_config, security_config, directory_config
from .core.micro_engine import app, HttpRequest, HttpResponse
from .core.directory import directory, NodeRegistration, NodeLifeState
from .core.security import security_engine, quantum_encryption

__all__ = [
    "app_config",
    "security_config", 
    "directory_config",
    "app",
    "HttpRequest",
    "HttpResponse",
    "directory",
    "NodeRegistration",
    "NodeLifeState",
    "security_engine",
    "quantum_encryption"
]