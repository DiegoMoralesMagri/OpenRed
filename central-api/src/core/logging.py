"""
Configuration du logging structuré pour OpenRed Central API

Logging sécurisé avec anonymisation des données sensibles
et intégration avec Elasticsearch pour la recherche.
"""

import logging
import logging.config
import structlog
import sys
from typing import Any, Dict
from datetime import datetime

from .config import settings


class SecurityLogProcessor:
    """Processeur pour anonymiser les données sensibles dans les logs"""
    
    SENSITIVE_FIELDS = {
        'password', 'token', 'key', 'secret', 'private_key', 
        'jwt', 'authorization', 'cookie', 'session'
    }
    
    def __call__(self, logger: logging.Logger, name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie les données sensibles des logs"""
        return self._sanitize_dict(event_dict)
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Récursivement nettoie un dictionnaire"""
        if not isinstance(data, dict):
            return data
        
        cleaned = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            # Vérifie si la clé contient des termes sensibles
            if any(sensitive in key_lower for sensitive in self.SENSITIVE_FIELDS):
                cleaned[key] = "[REDACTED]"
            elif isinstance(value, dict):
                cleaned[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                cleaned[key] = [self._sanitize_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                cleaned[key] = value
        
        return cleaned


class RequestIDProcessor:
    """Ajoute un ID unique à chaque requête pour le tracing"""
    
    def __call__(self, logger: logging.Logger, name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        # L'ID de requête sera ajouté par le middleware
        return event_dict


def setup_logging():
    """Configure le système de logging structuré"""
    
    # Processors communs
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.CallsiteParameterAdder(
            parameters=[structlog.processors.CallsiteParameter.FILENAME,
                       structlog.processors.CallsiteParameter.LINENO]
        ),
        RequestIDProcessor(),
        SecurityLogProcessor(),
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    # Processor final selon le format
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    # Configuration de structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configuration du logging standard
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False),
            },
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": settings.log_format,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": settings.log_level,
                "propagate": True,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO" if settings.debug else "WARNING",
                "propagate": False,
            },
        },
    }
    
    # Ajoute un handler de fichier si configuré
    if settings.log_file:
        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.log_file,
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "formatter": settings.log_format,
        }
        logging_config["loggers"][""]["handlers"].append("file")
    
    logging.config.dictConfig(logging_config)


# Logger structuré global
logger = structlog.get_logger("openred.central_api")


class AuditLogger:
    """Logger spécialisé pour l'audit de sécurité"""
    
    def __init__(self):
        self.logger = structlog.get_logger("openred.audit")
    
    def log_authentication_attempt(self, node_id: str, success: bool, ip_address: str, user_agent: str = None):
        """Log une tentative d'authentification"""
        self.logger.info(
            "authentication_attempt",
            node_id=node_id,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            event_type="auth"
        )
    
    def log_node_registration(self, node_id: str, ip_address: str, server_url: str):
        """Log l'enregistrement d'un node"""
        self.logger.info(
            "node_registration",
            node_id=node_id,
            ip_address=ip_address,
            server_url=server_url,
            event_type="registration"
        )
    
    def log_message_routing(self, from_node: str, to_node: str, message_id: str, success: bool):
        """Log le routage d'un message"""
        self.logger.info(
            "message_routing",
            from_node=from_node,
            to_node=to_node,
            message_id=message_id,
            success=success,
            event_type="message_routing"
        )
    
    def log_security_violation(self, violation_type: str, details: Dict[str, Any], ip_address: str):
        """Log une violation de sécurité"""
        self.logger.warning(
            "security_violation",
            violation_type=violation_type,
            details=details,
            ip_address=ip_address,
            event_type="security"
        )
    
    def log_admin_action(self, admin_id: str, action: str, target: str, ip_address: str):
        """Log une action d'administration"""
        self.logger.info(
            "admin_action",
            admin_id=admin_id,
            action=action,
            target=target,
            ip_address=ip_address,
            event_type="admin"
        )
    
    def log_api_access(self, endpoint: str = None, ip_address: str = None, user_agent: str = None, 
                       status_code: int = None, request_id: str = None, error: str = None,
                       path: str = None, method: str = None, user_id: str = None):
        """Log d'accès API | API access log | Log de acceso a la API | API访问日志"""
        # Support des anciens paramètres pour rétrocompatibilité
        if path and method:
            endpoint = f"{method} {path}"
        
        action = "api_access"
        if error:
            action = "api_error"
        
        extra_data = {}
        if user_agent:
            extra_data["user_agent"] = user_agent
        if status_code:
            extra_data["status_code"] = status_code
        if request_id:
            extra_data["request_id"] = request_id
        if error:
            extra_data["error"] = error
            
        self.logger.info(
            action,
            endpoint=endpoint or "unknown",
            user_id=user_id or "anonymous",
            ip_address=ip_address,
            event_type="api_access",
            **extra_data
        )


# Instance globale de l'audit logger
audit_logger = AuditLogger()
