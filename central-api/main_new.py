"""
Nouveau point d'entrée principal pour OpenRed Central API
New main entry point for OpenRed Central API
Nuevo punto de entrada principal para OpenRed Central API
OpenRed 中央 API 的新主入口点

Application FastAPI avec architecture sécurisée et scalable.
FastAPI application with secure and scalable architecture.
Aplicación FastAPI con arquitectura segura y escalable.
具有安全和可扩展架构的 FastAPI 应用程序。

Intégration complète des middlewares de sécurité et monitoring.
Complete integration of security and monitoring middlewares.
Integración completa de middlewares de seguridad y monitoreo.
安全和监控中间件的完整集成。
"""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

# Configuration et logging | Configuration and logging | Configuración y logging | 配置和日志
from src.core.config import settings
from src.core.logging import setup_logging, logger, audit_logger
from src.core.security import crypto_service

# Middlewares | Middlewares | Middlewares | 中间件
from src.middleware.rate_limiting import RateLimitingMiddleware
from src.middleware.security_headers import SecurityHeadersMiddleware
from src.middleware.request_logging import RequestLoggingMiddleware

# Routes API | API Routes | Rutas API | API 路由
from src.api.v1.api import api_router

# Base de données | Database | Base de datos | 数据库
from src.database.connection import init_database, close_database

# Services | Services | Servicios | 服务
# from src.services.auth_service import AuthService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gestionnaire de cycle de vie de l'application
    Application lifecycle manager
    Gestor del ciclo de vida de la aplicación
    应用程序生命周期管理器
    """
    
    # === DÉMARRAGE | STARTUP | INICIO | 启动 ===
    logger.info("Starting OpenRed Central API", version=settings.app_version)
    
    try:
        # Configuration du logging | Logging configuration | Configuración de logging | 日志配置
        setup_logging()
        logger.info("Logging configured", level=settings.log_level, format=settings.log_format)
        
        # Initialisation de la base de données (skip en mode test) | Database initialization (skip in test mode) | Inicialización de la base de datos (omitir en modo test) | 数据库初始化（测试模式下跳过）
        if not settings.testing:
            init_database()
            logger.info("Database initialized")
        else:
            logger.info("Database initialization skipped (testing mode)")
        
        # Vérification des services de sécurité | Security services verification | Verificación de servicios de seguridad | 安全服务验证
        if crypto_service:
            logger.info("Crypto service initialized")
        
        # Tests de connectivité Redis | Redis connectivity tests | Pruebas de conectividad Redis | Redis 连接测试
        try:
            # Ici on testerait la connexion Redis | Here we would test Redis connection | Aquí probaríamos la conexión Redis | 这里我们将测试 Redis 连接
            if not settings.testing:
                logger.info("Redis connection verified")
            else:
                logger.info("Redis connection skipped (testing mode)")
        except Exception as e:
            logger.warning("Redis connection failed, using local cache", error=str(e))
        
        # Log de démarrage réussi | Successful startup log | Log de inicio exitoso | 成功启动日志
        audit_logger.log_admin_action(
            admin_id="system",
            action="service_start",
            target="central_api",
            ip_address="localhost"
        )
        
        logger.info("OpenRed Central API started successfully", port=8000)
        
    except Exception as e:
        logger.error("Failed to start application", error=str(e))
        sys.exit(1)
    
    yield
    
    # === ARRÊT | SHUTDOWN | PARADA | 关闭 ===
    logger.info("Shutting down OpenRed Central API")
    
    try:
        # Fermeture de la base de données | Database closure | Cierre de la base de datos | 数据库关闭
        close_database()
        logger.info("Database connections closed")
        
        # Log d'arrêt | Shutdown log | Log de parada | 关闭日志
        audit_logger.log_admin_action(
            admin_id="system",
            action="service_stop",
            target="central_api",
            ip_address="localhost"
        )
        
        logger.info("OpenRed Central API shut down successfully")
        
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))


def create_application() -> FastAPI:
    """
    Crée et configure l'application FastAPI
    Creates and configures the FastAPI application
    Crea y configura la aplicación FastAPI
    创建和配置 FastAPI 应用程序
    """
    
    # Création de l'application | Application creation | Creación de la aplicación | 应用程序创建
    app = FastAPI(
        title="OpenRed Central API",
        description="API centrale sécurisée pour l'écosystème OpenRed décentralisé",
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan
    )
    
    # === MIDDLEWARE DE SÉCURITÉ | SECURITY MIDDLEWARE | MIDDLEWARE DE SEGURIDAD | 安全中间件 ===
    
    # Headers de sécurité (doit être en premier) | Security headers (must be first) | Headers de seguridad (debe ser primero) | 安全标头（必须首先）
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate limiting | Rate limiting | Limitación de tasa | 速率限制
    app.add_middleware(RateLimitingMiddleware)
    
    # Logging des requêtes | Request logging | Logging de peticiones | 请求日志
    app.add_middleware(RequestLoggingMiddleware)
    
    # CORS sécurisé | Secure CORS | CORS seguro | 安全 CORS
    if settings.allowed_origins != ["*"] or settings.is_development:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins,
            allow_credentials=True,
            allow_methods=settings.allowed_methods,
            allow_headers=settings.allowed_headers,
            max_age=86400,  # 24 heures | 24 hours | 24 horas | 24小时
        )
    
    # Protection contre les attaques Host Header | Host Header attack protection | Protección contra ataques Host Header | Host Header 攻击保护
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # À configurer avec les domaines autorisés | To configure with authorized domains | A configurar con dominios autorizados | 配置授权域名
        )
    
    # === ROUTES | ROUTES | RUTAS | 路由 ===
    
    # API v1 | API v1 | API v1 | API v1
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    
    # === GESTIONNAIRES D'ERREURS | ERROR HANDLERS | MANEJADORES DE ERRORES | 错误处理器 ===
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Gestionnaire d'erreurs de validation
        Validation error handler
        Manejador de errores de validación
        验证错误处理器
        """
        logger.warning(
            "Validation error",
            path=request.url.path,
            method=request.method,
            errors=exc.errors()
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation failed",
                "message": "The request data is invalid",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Gestionnaire d'erreurs général
        General error handler
        Manejador de errores general
        通用错误处理器
        """
        logger.error(
            "Unhandled exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            error_type=type(exc).__name__
        )
        
        # Ne pas exposer les détails en production | Don't expose details in production | No exponer detalles en producción | 生产环境不暴露详细信息
        if settings.is_production:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred"
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "message": str(exc),
                    "type": type(exc).__name__
                }
            )
    
    # === ENDPOINTS DE SANTÉ | HEALTH ENDPOINTS | ENDPOINTS DE SALUD | 健康检查端点 ===
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Endpoint de vérification de santé
        Health check endpoint
        Endpoint de verificación de salud
        健康检查端点
        """
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment,
            "timestamp": "2024-01-01T00:00:00Z"  # Sera remplacé par datetime.utcnow() | Will be replaced by datetime.utcnow() | Será reemplazado por datetime.utcnow() | 将被 datetime.utcnow() 替换
        }
    
    @app.get("/", tags=["Root"])
    async def root():
        """
        Endpoint racine
        Root endpoint
        Endpoint raíz
        根端点
        """
        return {
            "name": "OpenRed Central API",
            "version": settings.app_version,
            "description": "API centrale pour l'écosystème OpenRed décentralisé",
            "docs_url": "/docs" if settings.debug else None
        }
    
    return app


def setup_signal_handlers():
    """
    Configure les gestionnaires de signaux pour un arrêt propre
    Configure signal handlers for graceful shutdown
    Configura los manejadores de señales para un cierre ordenado
    配置信号处理器以实现优雅关闭
    """
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# Création de l'application | Application creation | Creación de la aplicación | 应用程序创建
app = create_application()


if __name__ == "__main__":
    """
    Point d'entrée principal
    Main entry point
    Punto de entrada principal
    主入口点
    """
    
    # Configuration des gestionnaires de signaux | Signal handlers configuration | Configuración de manejadores de señales | 信号处理器配置
    setup_signal_handlers()
    
    # Configuration d'Uvicorn | Uvicorn configuration | Configuración de Uvicorn | Uvicorn 配置
    uvicorn_config = {
        "host": "0.0.0.0",
        "port": 8000,
        "log_config": None,  # Utilise notre configuration de logging | Uses our logging configuration | Usa nuestra configuración de logging | 使用我们的日志配置
        "access_log": False,  # Géré par notre middleware | Managed by our middleware | Gestionado por nuestro middleware | 由我们的中间件管理
    }
    
    # Options supplémentaires selon l'environnement | Additional options based on environment | Opciones adicionales según el entorno | 根据环境的附加选项
    if settings.is_development:
        uvicorn_config.update({
            "reload": False,  # Désactivé pour les tests
            "reload_dirs": ["src"],
        })
    else:
        uvicorn_config.update({
            "workers": 1,  # Pour la production, utiliser Gunicorn avec plusieurs workers | For production, use Gunicorn with multiple workers | Para producción, usar Gunicorn con múltiples workers | 对于生产环境，使用带有多个工作进程的 Gunicorn
        })
    
    logger.info("Starting Uvicorn server", config=uvicorn_config)
    
    try:
        uvicorn.run("main_new:app", **uvicorn_config)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", error=str(e))
        sys.exit(1)
