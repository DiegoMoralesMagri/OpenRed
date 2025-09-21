#!/usr/bin/env python3
"""
Script d'initialisation de la base de données OpenRed Central API v2.0
Crée toutes les tables nécessaires dans SQLite
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models.database import Base, Node, Message, AuditLog, NodeConnection
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de la base de données
DATABASE_URL = "sqlite+aiosqlite:///openred_dev.db"
SYNC_DATABASE_URL = "sqlite:///openred_dev.db"

async def create_database():
    """Créer toutes les tables de la base de données"""
    try:
        logger.info("🚀 Initialisation de la base de données OpenRed Central API v2.0")
        
        # Créer l'engine async
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        # Créer toutes les tables
        async with engine.begin() as conn:
            logger.info("📋 Création des tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Tables créées avec succès!")
            
            # Vérifier les tables créées
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            
            logger.info("🗄️ Tables disponibles:")
            for table in tables:
                logger.info(f"   - {table[0]}")
                
        await engine.dispose()
        logger.info("🎯 Base de données initialisée avec succès!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        return False

async def test_database():
    """Tester la base de données avec quelques opérations CRUD"""
    try:
        logger.info("🧪 Test de la base de données...")
        
        # Créer l'engine et la session
        engine = create_async_engine(DATABASE_URL)
        async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session_maker() as session:
            # Créer un node de test
            test_node = Node(
                node_id="init_test_node",
                display_name="Init Test Node",
                server_url="https://init.test.example.com",
                public_key="init_test_key",
                version="2.0.0",
                capabilities=["messaging", "testing"],
                status="active"
            )
            
            session.add(test_node)
            await session.commit()
            
            logger.info("✅ Node de test créé")
            
            # Vérifier la création
            await session.refresh(test_node)
            logger.info(f"📝 Node créé: {test_node.node_id} ({test_node.display_name})")
            
        await engine.dispose()
        logger.info("🎉 Test de base de données réussi!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        return False

async def main():
    """Fonction principale"""
    logger.info("=" * 70)
    logger.info("🔧 INITIALISATION BASE DE DONNÉES - OpenRed Central API v2.0")
    logger.info("=" * 70)
    
    # Créer la base de données
    db_success = await create_database()
    if not db_success:
        logger.error("❌ Échec de l'initialisation de la base de données")
        return False
    
    # Tester la base de données
    test_success = await test_database()
    if not test_success:
        logger.error("❌ Échec du test de la base de données")
        return False
    
    logger.info("=" * 70)
    logger.info("🏆 INITIALISATION TERMINÉE AVEC SUCCÈS")
    logger.info("=" * 70)
    logger.info("📄 Fichier créé: openred_dev.db")
    logger.info("🎯 Prêt pour les tests et le développement!")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
