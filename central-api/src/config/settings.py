# FR: Fichier: settings.py — Configuration des paramètres (FastAPI)
# EN: File: settings.py — Application settings configuration (FastAPI)
# ES: Archivo: settings.py — Configuración de parámetros (FastAPI)
# ZH: 文件: settings.py — 应用配置参数 (FastAPI)

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database configuration
    DATABASE_URL: str = "postgresql://openred:openred@localhost/openred_central"
    
    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Node validation
    MAX_NODES_PER_IP: int = 5
    NODE_HEARTBEAT_INTERVAL: int = 300  # 5 minutes
    NODE_TIMEOUT: int = 1800  # 30 minutes
    
    class Config:
        env_file = ".env"

settings = Settings()