# FR: Fichier: config.py — Chargement de la configuration applicative
# EN: File: config.py — Application configuration loader
# ES: Archivo: config.py — Cargador de configuración de la aplicación
# ZH: 文件: config.py — 应用配置加载器

# Configuration de l'API centrale O-Red

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Configuration principale de l'API O-Red"""
    
    # Application
    APP_NAME: str = "O-Red Central API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Sécurité
    SECRET_KEY: str = os.getenv("SECRET_KEY", "o-red-super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS et sécurité réseau
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://o-red.org",
        "https://app.o-red.org"
    ]
    ALLOWED_HOSTS: List[str] = ["*"]  # À restreindre en production
    
    # Base de données
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://ored:ored_password@localhost:5432/ored_central"
    )
    DATABASE_ECHO: bool = False  # True pour voir les requêtes SQL
    
    # Redis pour cache et sessions
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL: int = 3600  # 1 heure
    
    # Configuration P2P
    P2P_BOOTSTRAP_NODES: List[str] = [
        "node1.o-red.org:8001",
        "node2.o-red.org:8001",
        "node3.o-red.org:8001"
    ]
    P2P_PORT: int = 8001
    P2P_MAX_CONNECTIONS: int = 100
    
    # Configuration O-RedID (Identité décentralisée)
    ORED_ID_ISSUER: str = "o-red.org"
    ORED_ID_KEY_SIZE: int = 4096  # RSA key size
    ORED_ID_CURVE: str = "ed25519"  # Courbe elliptique
    
    # Configuration cryptographique post-quantique
    POST_QUANTUM_ENABLED: bool = True
    PQ_SIGNATURE_ALGORITHM: str = "Dilithium3"  # CRYSTALS-Dilithium
    PQ_KEM_ALGORITHM: str = "Kyber768"  # CRYSTALS-KYBER
    
    # Configuration O-RedMind (IA)
    AI_MODEL_PATH: str = "./models"
    AI_MAX_REQUESTS_PER_MINUTE: int = 60
    AI_DISTRIBUTED_COMPUTING_ENABLED: bool = True
    AI_PRIVACY_LEVEL: str = "maximum"  # minimum, standard, maximum
    
    # Configuration O-RedStore (Marketplace)
    STORE_ENABLE_PAYMENTS: bool = True
    STORE_COMMISSION_RATE: float = 0.05  # 5% commission
    STORE_MIN_REPUTATION_SCORE: int = 50
    
    # Configuration O-RedSearch (Moteur de recherche)
    SEARCH_INDEX_NODES: List[str] = []  # Nœuds d'indexation
    SEARCH_MAX_RESULTS: int = 100
    SEARCH_PRIVACY_MODE: str = "anonymous"  # anonymous, pseudonymous
    
    # Monitoring et métriques
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"
    STRUCTURED_LOGGING: bool = True
    
    # Stockage de fichiers
    FILE_STORAGE_TYPE: str = "local"  # local, s3, ipfs
    FILE_STORAGE_PATH: str = "./storage"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # secondes
    
    # Configuration réseau fédéré
    FEDERATION_ENABLED: bool = True
    FEDERATION_SYNC_INTERVAL: int = 300  # 5 minutes
    FEDERATION_MAX_RETRIES: int = 3
    
    # Configuration de développement
    AUTO_RELOAD: bool = False
    PROFILING_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Instance globale des paramètres
settings = Settings()

# Chemins utiles
PROJECT_ROOT = Path(__file__).parent.parent.parent
STATIC_DIR = PROJECT_ROOT / "static"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
LOGS_DIR = PROJECT_ROOT / "logs"

# Configuration de logging structuré
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "structured": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": "structlog.processors.JSONRenderer",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "structured" if settings.STRUCTURED_LOGGING else "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "structured" if settings.STRUCTURED_LOGGING else "default",
            "filename": LOGS_DIR / "o-red-api.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "sqlalchemy": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False,
        },
    },
}

# Validation de la configuration
def validate_settings():
    """Valide la configuration au démarrage"""
    errors = []
    
    # Vérification des clés de sécurité
    if settings.SECRET_KEY == "o-red-super-secret-key-change-in-production":
        if not settings.DEBUG:
            errors.append("SECRET_KEY must be changed in production")
    
    # Vérification de la base de données
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is required")
    
    # Vérification des chemins
    for directory in [STATIC_DIR, TEMPLATES_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True