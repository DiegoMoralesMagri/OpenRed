"""
Configuration centralisée pour OpenRed Central API
Centralized configuration for OpenRed Central API
Configuración centralizada para OpenRed Central API
OpenRed 中央 API 的集中配置

Gestion sécurisée de toutes les variables d'environnement et paramètres
de l'application avec validation et typage strict.

Secure management of all environment variables and application parameters
with validation and strict typing.

Gestión segura de todas las variables de entorno y parámetros de la aplicación
con validación y tipado estricto.

使用验证和严格类型检查安全管理所有环境变量和应用程序参数。
"""

from pydantic_settings import BaseSettings
from pydantic import validator, Field
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Configuration principale de l'application
    Main application configuration
    Configuración principal de la aplicación
    主应用程序配置
    """
    
    # === Application | Application | Aplicación | 应用程序 ===
    app_name: str = "OpenRed Central API"
    app_version: str = "2.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    testing: bool = Field(default=False, env="TESTING")
    
    # === API Configuration | API Configuration | Configuración API | API 配置 ===
    api_v1_prefix: str = "/api/v1"
    max_request_size: int = Field(default=10 * 1024 * 1024, env="MAX_REQUEST_SIZE")  # 10MB
    
    # === Sécurité | Security | Seguridad | 安全 ===
    secret_key: str = Field(..., env="SECRET_KEY", min_length=32)
    jwt_algorithm: str = "RS256"
    jwt_access_token_expire_minutes: int = Field(default=15, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Clés RSA pour JWT (chemins vers les fichiers)
    jwt_private_key_path: str = Field(..., env="JWT_PRIVATE_KEY_PATH")
    jwt_public_key_path: str = Field(..., env="JWT_PUBLIC_KEY_PATH")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=100, env="RATE_LIMIT_BURST")
    
    # === Base de données ===
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    
    # === Redis ===
    redis_url: str = Field(..., env="REDIS_URL")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    # === Elasticsearch (optionnel pour les logs) ===
    elasticsearch_url: Optional[str] = Field(default=None, env="ELASTICSEARCH_URL")
    elasticsearch_index_prefix: str = Field(default="openred-central", env="ELASTICSEARCH_INDEX_PREFIX")
    
    # === CORS ===
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    allowed_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE"], env="ALLOWED_METHODS")
    allowed_headers: List[str] = Field(default=["*"], env="ALLOWED_HEADERS")
    
    # === Monitoring ===
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_path: str = Field(default="/metrics", env="METRICS_PATH")
    
    # === Logging ===
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json ou text
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # === Cryptographie ===
    encryption_key: str = Field(..., env="ENCRYPTION_KEY", min_length=32)
    password_hash_rounds: int = Field(default=12, env="PASSWORD_HASH_ROUNDS")
    
    # === Node Management ===
    max_nodes_per_ip: int = Field(default=5, env="MAX_NODES_PER_IP")
    node_heartbeat_timeout_minutes: int = Field(default=10, env="NODE_HEARTBEAT_TIMEOUT_MINUTES")
    node_cleanup_interval_hours: int = Field(default=24, env="NODE_CLEANUP_INTERVAL_HOURS")
    
    # === Message Routing ===
    max_message_size: int = Field(default=1024 * 1024, env="MAX_MESSAGE_SIZE")  # 1MB
    message_ttl_hours: int = Field(default=72, env="MESSAGE_TTL_HOURS")
    max_messages_per_hour: int = Field(default=1000, env="MAX_MESSAGES_PER_HOUR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('environment')
    def validate_environment(cls, v):
        valid_envs = ['development', 'staging', 'production']
        if v not in valid_envs:
            raise ValueError(f'Environment must be one of: {valid_envs}')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    @validator('log_format')
    def validate_log_format(cls, v):
        valid_formats = ['json', 'text']
        if v not in valid_formats:
            raise ValueError(f'Log format must be one of: {valid_formats}')
        return v
    
    @validator('jwt_private_key_path', 'jwt_public_key_path')
    def validate_key_files_exist(cls, v):
        if not Path(v).exists():
            raise ValueError(f'Key file does not exist: {v}')
        return v
    
    @property
    def jwt_private_key(self) -> str:
        """Charge la clé privée RSA depuis le fichier"""
        with open(self.jwt_private_key_path, 'r') as f:
            return f.read()
    
    @property
    def jwt_public_key(self) -> str:
        """Charge la clé publique RSA depuis le fichier"""
        with open(self.jwt_public_key_path, 'r') as f:
            return f.read()
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"


# Instance globale des paramètres
settings = Settings()
