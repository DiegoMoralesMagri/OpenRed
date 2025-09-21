#!/usr/bin/env python3
"""
Script d'initialisation SIMPLE de la base de données OpenRed Central API v2.0
Version SQLite compatible - sans UUID, avec types simples
"""

import sqlite3
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base de données
DB_FILE = "openred_dev.db"

def create_simple_database():
    """Créer une base de données SQLite simple avec les tables essentielles"""
    try:
        logger.info("🚀 Création de la base de données SQLite simple")
        
        # Connexion à SQLite
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Table nodes (version simplifiée)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT UNIQUE NOT NULL,
                display_name TEXT,
                server_url TEXT NOT NULL,
                public_key TEXT NOT NULL,
                version TEXT DEFAULT '2.0.0',
                capabilities TEXT DEFAULT '[]',
                status TEXT DEFAULT 'active',
                last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_ip TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_messages_sent INTEGER DEFAULT 0,
                total_messages_received INTEGER DEFAULT 0,
                last_activity TIMESTAMP
            )
        ''')
        
        # Table messages (version simplifiée)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                from_node_id TEXT NOT NULL,
                to_node_id TEXT NOT NULL,
                content_type TEXT NOT NULL,
                encrypted_content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                priority TEXT DEFAULT 'normal',
                ttl TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                delivery_attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                delivered_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table auth_sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auth_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                node_id TEXT NOT NULL,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Table audit_logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT,
                session_id TEXT,
                event_type TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table node_connections
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS node_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_node_id TEXT NOT NULL,
                to_node_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Index pour les performances
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nodes_node_id ON nodes(node_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nodes_status ON nodes(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_from_node ON messages(from_node_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_to_node ON messages(to_node_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_auth_sessions_node_id ON auth_sessions(node_id)')
        
        conn.commit()
        
        # Vérifier les tables créées
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        logger.info("✅ Tables créées:")
        for table in tables:
            logger.info(f"   - {table[0]}")
            
        # Insérer un node de test
        cursor.execute('''
            INSERT OR REPLACE INTO nodes 
            (node_id, display_name, server_url, public_key, version, capabilities, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'test_node_init',
            'Node de Test Init',
            'https://test.init.example.com',
            'test_public_key_init',
            '2.0.0',
            '["messaging", "routing", "testing"]',
            'active'
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("🎯 Base de données créée avec succès!")
        logger.info(f"📄 Fichier: {DB_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

def test_database():
    """Tester la base de données"""
    try:
        logger.info("🧪 Test de la base de données...")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Vérifier les nodes
        cursor.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]
        logger.info(f"📊 Nombre de nodes: {node_count}")
        
        # Afficher les nodes
        cursor.execute("SELECT node_id, display_name, status FROM nodes")
        nodes = cursor.fetchall()
        for node in nodes:
            logger.info(f"   📝 {node[0]} - {node[1]} ({node[2]})")
            
        conn.close()
        logger.info("✅ Test réussi!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        return False

def main():
    """Fonction principale"""
    logger.info("=" * 70)
    logger.info("🔧 CRÉATION BASE DE DONNÉES SIMPLE - OpenRed Central API v2.0")
    logger.info("=" * 70)
    
    # Supprimer l'ancienne base si elle existe
    if Path(DB_FILE).exists():
        Path(DB_FILE).unlink()
        logger.info("🗑️ Ancienne base supprimée")
    
    # Créer la base
    if not create_simple_database():
        return False
    
    # Tester la base
    if not test_database():
        return False
    
    logger.info("=" * 70)
    logger.info("🏆 INITIALISATION TERMINÉE AVEC SUCCÈS!")
    logger.info("=" * 70)
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
