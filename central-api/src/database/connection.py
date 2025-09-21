"""
Utilitaires de base de données pour OpenRed Central API
Database utilities for OpenRed Central API
Utilidades de base de datos para OpenRed Central API
OpenRed 中央 API 的数据库工具
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator, Optional
import os
import logging

# Configuration du logger | Logger configuration | Configuración del logger | 日志配置
logger = logging.getLogger(__name__)

# Base pour les modèles SQLAlchemy | SQLAlchemy models base | Base para modelos SQLAlchemy | SQLAlchemy模型基类
Base = declarative_base()

# Métadonnées de la base de données | Database metadata | Metadatos de la base de datos | 数据库元数据
metadata = MetaData()

# Variables globales pour la base de données | Global database variables | Variables globales de base de datos | 全局数据库变量
engine = None
SessionLocal = None


def create_database_engine():
    """
    Crée le moteur de base de données avec pool de connexions
    Create database engine with connection pool
    Crea el motor de base de datos con pool de conexiones
    创建带连接池的数据库引擎
    """
    global engine
    
    if engine is None:
        # Import des settings ici pour éviter les imports circulaires | Import settings here to avoid circular imports | Importar configuración aquí para evitar importaciones circulares | 在此处导入设置以避免循环导入
        from src.core.config import settings
        
        database_url = settings.database_url
        
        # Configuration du moteur avec pool | Engine configuration with pool | Configuración del motor con pool | 带连接池的引擎配置
        engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            future=True
        )
        
        logger.info(f"Moteur de base de données créé | Database engine created | Motor de base de datos creado | 数据库引擎已创建")
    
    return engine


def create_session_factory():
    """
    Crée la factory de sessions SQLAlchemy
    Create SQLAlchemy session factory
    Crea la fábrica de sesiones SQLAlchemy
    创建SQLAlchemy会话工厂
    """
    global SessionLocal
    
    if SessionLocal is None:
        engine = create_database_engine()
        SessionLocal = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        logger.info(f"Factory de sessions créée | Session factory created | Fábrica de sesiones creada | 会话工厂已创建")
    
    return SessionLocal


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Gestionnaire de contexte pour les sessions de base de données
    Context manager for database sessions
    Gestor de contexto para sesiones de base de datos
    数据库会话的上下文管理器
    """
    if SessionLocal is None:
        create_session_factory()
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erreur de session de base de données | Database session error | Error de sesión de base de datos | 数据库会话错误: {e}")
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    Dépendance FastAPI pour les sessions de base de données
    FastAPI dependency for database sessions
    Dependencia FastAPI para sesiones de base de datos
    数据库会话的FastAPI依赖
    """
    with get_db_session() as session:
        yield session


async def check_database_connection() -> bool:
    """
    Vérifie la connexion à la base de données
    Check database connection
    Verifica la conexión a la base de datos
    检查数据库连接
    """
    try:
        engine = create_database_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Échec de connexion à la base de données | Database connection failed | Fallo de conexión a la base de datos | 数据库连接失败: {e}")
        return False


async def get_database_info() -> dict:
    """
    Récupère les informations de la base de données
    Get database information
    Obtiene información de la base de datos
    获取数据库信息
    """
    try:
        engine = create_database_engine()
        with engine.connect() as connection:
            # Version PostgreSQL | PostgreSQL version | Versión PostgreSQL | PostgreSQL版本
            version_result = connection.execute(text("SELECT version()"))
            version = version_result.scalar()
            
            # Taille de la base de données | Database size | Tamaño de la base de datos | 数据库大小
            size_result = connection.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """))
            size = size_result.scalar()
            
            # Nombre de connexions actives | Active connections count | Número de conexiones activas | 活跃连接数
            connections_result = connection.execute(text("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE state = 'active'
            """))
            active_connections = connections_result.scalar()
            
            return {
                "version": version,
                "size": size,
                "active_connections": active_connections,
                "pool_size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow()
            }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des infos DB | Error getting DB info | Error al obtener info de DB | 获取数据库信息时出错: {e}")
        return {"error": str(e)}


def create_tables():
    """
    Crée toutes les tables de la base de données
    Create all database tables
    Crea todas las tablas de la base de datos
    创建所有数据库表
    """
    try:
        engine = create_database_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Tables créées avec succès | Tables created successfully | Tablas creadas exitosamente | 表创建成功")
    except Exception as e:
        logger.error(f"Erreur lors de la création des tables | Error creating tables | Error al crear tablas | 创建表时出错: {e}")
        raise


def drop_tables():
    """
    Supprime toutes les tables de la base de données
    Drop all database tables
    Elimina todas las tablas de la base de datos
    删除所有数据库表
    """
    try:
        engine = create_database_engine()
        Base.metadata.drop_all(bind=engine)
        logger.info("Tables supprimées avec succès | Tables dropped successfully | Tablas eliminadas exitosamente | 表删除成功")
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des tables | Error dropping tables | Error al eliminar tablas | 删除表时出错: {e}")
        raise


def init_database():
    """
    Initialise la base de données (crée le moteur et les tables)
    Initialize database (create engine and tables)
    Inicializa la base de datos (crea el motor y las tablas)
    初始化数据库（创建引擎和表）
    """
    logger.info("Initialisation de la base de données | Database initialization | Inicialización de la base de datos | 数据库初始化开始")
    
    # Crée le moteur et la factory de sessions | Create engine and session factory | Crea motor y fábrica de sesiones | 创建引擎和会话工厂
    create_database_engine()
    create_session_factory()
    
    # Crée les tables si elles n'existent pas | Create tables if they don't exist | Crea tablas si no existen | 如果表不存在则创建
    create_tables()
    
    logger.info("Base de données initialisée | Database initialized | Base de datos inicializada | 数据库初始化完成")


def close_database():
    """
    Ferme toutes les connexions à la base de données
    Close all database connections
    Cierra todas las conexiones de la base de datos
    关闭所有数据库连接
    """
    global engine, SessionLocal
    
    if engine:
        engine.dispose()
        engine = None
        logger.info("Moteur de base de données fermé | Database engine closed | Motor de base de datos cerrado | 数据库引擎已关闭")
    
    if SessionLocal:
        SessionLocal = None
        logger.info("Factory de sessions fermée | Session factory closed | Fábrica de sesiones cerrada | 会话工厂已关闭")
