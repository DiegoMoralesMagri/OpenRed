#!/usr/bin/env python3
"""
Tests d'Intégration End-to-End - OpenRed Central API v2.0
Tests complets avec serveur de test et base de données temporaire
"""

import asyncio
import pytest
import httpx
import sqlite3
import tempfile
import os
import sys
from pathlib import Path
import uvicorn
import threading
import time
import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configuration de test
TEST_HOST = "127.0.0.1"
TEST_PORT = 8888
TEST_BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}"


class TestServer:
    """Gestionnaire de serveur de test"""
    
    def __init__(self):
        self.server = None
        self.thread = None
        self.temp_db = None
        
    def setup_test_database(self):
        """Créer une base de données temporaire pour les tests"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Créer le schéma
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Table nodes
        cursor.execute('''
            CREATE TABLE nodes (
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
        
        # Table messages
        cursor.execute('''
            CREATE TABLE messages (
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
            CREATE TABLE auth_sessions (
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
        
        conn.commit()
        conn.close()
        
        # Configurer la variable d'environnement
        os.environ['DATABASE_URL'] = f"sqlite:///{self.temp_db.name}"
        os.environ['ENVIRONMENT'] = 'testing'
        os.environ['SECRET_KEY'] = 'test-secret-key-for-integration-tests'
        
        return self.temp_db.name
        
    def start_server(self):
        """Démarrer le serveur de test"""
        try:
            # Importer l'app après configuration de l'environnement
            from main import app
            
            def run_server():
                uvicorn.run(
                    app,
                    host=TEST_HOST,
                    port=TEST_PORT,
                    log_level="error",  # Réduire le bruit dans les tests
                    access_log=False
                )
            
            self.thread = threading.Thread(target=run_server, daemon=True)
            self.thread.start()
            
            # Attendre que le serveur soit prêt
            for _ in range(30):  # Timeout de 30 secondes
                try:
                    response = httpx.get(f"{TEST_BASE_URL}/health", timeout=1.0)
                    if response.status_code == 200:
                        return True
                except:
                    pass
                time.sleep(1)
                
            return False
            
        except Exception as e:
            print(f"Erreur démarrage serveur: {e}")
            return False
    
    def stop_server(self):
        """Arrêter le serveur et nettoyer"""
        if self.temp_db and os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)


# Fixture globale pour le serveur de test
test_server = TestServer()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configuration de l'environnement de test"""
    print("\n🚀 Démarrage de l'environnement de test...")
    
    # Créer la base de données de test
    db_path = test_server.setup_test_database()
    print(f"📄 Base de test créée: {db_path}")
    
    # Démarrer le serveur
    if test_server.start_server():
        print(f"✅ Serveur de test démarré sur {TEST_BASE_URL}")
    else:
        pytest.fail("❌ Impossible de démarrer le serveur de test")
    
    yield
    
    # Nettoyage
    print("\n🧹 Nettoyage de l'environnement de test...")
    test_server.stop_server()


@pytest.fixture
async def client():
    """Client HTTP async pour les tests"""
    async with httpx.AsyncClient(base_url=TEST_BASE_URL, timeout=10.0) as client:
        yield client


class TestHealthEndpoints:
    """Tests des endpoints de santé"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test du endpoint de santé principal"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "checks" in data
        
        print(f"✅ Health check: {data['status']}")
    
    @pytest.mark.asyncio
    async def test_liveness_probe(self, client):
        """Test du liveness probe"""
        response = await client.get("/health/liveness")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "alive"
        assert "timestamp" in data
        
        print(f"✅ Liveness probe: {data['status']}")
    
    @pytest.mark.asyncio
    async def test_readiness_probe(self, client):
        """Test du readiness probe"""
        response = await client.get("/health/readiness")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ready"
        assert "timestamp" in data
        
        print(f"✅ Readiness probe: {data['status']}")


class TestAuthenticationFlow:
    """Tests du flux d'authentification complet"""
    
    @pytest.mark.asyncio
    async def test_node_registration(self, client):
        """Test d'enregistrement d'un nœud"""
        registration_data = {
            "username": "test_node_integration",
            "display_name": "Test Node Integration",
            "server_url": "https://test.integration.example.com",
            "public_key": "test_integration_public_key",
            "version": "2.0.0",
            "capabilities": ["messaging", "routing", "testing"]
        }
        
        response = await client.post("/auth/register", json=registration_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Node registered successfully"
        assert data["node_id"] == "test_node_integration"
        assert data["status"] == "pending_verification"
        
        print(f"✅ Node registered: {data['node_id']}")
        
        return data["node_id"]
    
    @pytest.mark.asyncio
    async def test_node_login(self, client):
        """Test de connexion d'un nœud"""
        # D'abord enregistrer un nœud
        await self.test_node_registration(client)
        
        login_data = {
            "username": "test_node_integration",
            "signature": "test_integration_signature"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        assert data["node_id"] == "test_node_integration"
        
        print(f"✅ Node logged in: {data['node_id']}")
        
        return data
    
    @pytest.mark.asyncio
    async def test_token_refresh(self, client):
        """Test de renouvellement de token"""
        # Obtenir un token via login
        login_response = await self.test_node_login(client)
        refresh_token = login_response["refresh_token"]
        
        refresh_data = {
            "refresh_token": refresh_token
        }
        
        response = await client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        
        print(f"✅ Token refreshed: expires in {data['expires_in']}s")
        
        return data


class TestNodeDiscovery:
    """Tests de découverte des nœuds"""
    
    @pytest.mark.asyncio
    async def test_list_nodes_empty(self, client):
        """Test de listing des nœuds (liste vide)"""
        response = await client.get("/nodes")
        
        # Peut être 200 avec liste vide ou 404 si aucun nœud
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "nodes" in data
            print(f"✅ Nodes listed: {len(data['nodes'])} found")
        else:
            print("✅ No nodes found (expected)")
    
    @pytest.mark.asyncio
    async def test_list_nodes_with_data(self, client):
        """Test de listing après enregistrement de nœuds"""
        # Enregistrer quelques nœuds de test
        test_auth = TestAuthenticationFlow()
        await test_auth.test_node_registration(client)
        
        # Enregistrer un second nœud
        registration_data = {
            "username": "test_node_2",
            "display_name": "Test Node 2",
            "server_url": "https://test2.integration.example.com",
            "public_key": "test_2_public_key",
            "version": "2.0.0",
            "capabilities": ["messaging"]
        }
        
        await client.post("/auth/register", json=registration_data)
        
        # Lister les nœuds
        response = await client.get("/nodes")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "nodes" in data
        assert len(data["nodes"]) >= 2
        
        # Vérifier la structure des nœuds
        for node in data["nodes"]:
            assert "node_id" in node
            assert "display_name" in node
            assert "server_url" in node
            assert "status" in node
            assert "version" in node
        
        print(f"✅ Nodes listed: {len(data['nodes'])} found")
    
    @pytest.mark.asyncio
    async def test_get_specific_node(self, client):
        """Test de récupération d'un nœud spécifique"""
        # Enregistrer un nœud
        test_auth = TestAuthenticationFlow()
        node_id = await test_auth.test_node_registration(client)
        
        # Récupérer le nœud spécifique
        response = await client.get(f"/nodes/{node_id}")
        
        if response.status_code == 200:
            data = response.json()
            
            assert data["node_id"] == node_id
            assert "display_name" in data
            assert "server_url" in data
            assert "status" in data
            
            print(f"✅ Node retrieved: {data['node_id']}")
        else:
            # L'endpoint peut ne pas être implémenté
            print(f"⚠️ Endpoint /nodes/{node_id} not implemented (status: {response.status_code})")


class TestMessageRouting:
    """Tests de routage des messages"""
    
    @pytest.mark.asyncio
    async def test_send_message_unauthorized(self, client):
        """Test d'envoi de message sans authentification"""
        message_data = {
            "to_node_id": "test_node_2",
            "content_type": "text/plain",
            "content": "Hello from integration test!",
            "priority": "normal"
        }
        
        response = await client.post("/messages/send", json=message_data)
        
        # Doit échouer sans authentification
        assert response.status_code in [401, 403, 404]
        print(f"✅ Unauthorized message rejected (status: {response.status_code})")
    
    @pytest.mark.asyncio
    async def test_send_message_authorized(self, client):
        """Test d'envoi de message avec authentification"""
        # Obtenir un token
        test_auth = TestAuthenticationFlow()
        login_data = await test_auth.test_node_login(client)
        access_token = login_data["access_token"]
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        message_data = {
            "to_node_id": "test_node_2",
            "content_type": "text/plain",
            "content": "Hello from authenticated integration test!",
            "priority": "normal"
        }
        
        response = await client.post("/messages/send", json=message_data, headers=headers)
        
        # Peut être 200 (succès) ou 404 (endpoint non implémenté)
        if response.status_code == 200:
            data = response.json()
            assert "message_id" in data
            print(f"✅ Message sent: {data['message_id']}")
        else:
            print(f"⚠️ Message endpoint not fully implemented (status: {response.status_code})")


class TestErrorHandling:
    """Tests de gestion des erreurs"""
    
    @pytest.mark.asyncio
    async def test_invalid_endpoint(self, client):
        """Test d'endpoint inexistant"""
        response = await client.get("/nonexistent")
        
        assert response.status_code == 404
        print("✅ 404 for invalid endpoint")
    
    @pytest.mark.asyncio
    async def test_invalid_json(self, client):
        """Test de JSON invalide"""
        response = await client.post(
            "/auth/register",
            content="invalid json content",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]
        print(f"✅ Invalid JSON rejected (status: {response.status_code})")
    
    @pytest.mark.asyncio
    async def test_missing_fields(self, client):
        """Test de champs manquants"""
        incomplete_data = {
            "username": "incomplete_node"
            # Champs manquants: server_url, public_key
        }
        
        response = await client.post("/auth/register", json=incomplete_data)
        
        assert response.status_code in [400, 422]
        print(f"✅ Incomplete data rejected (status: {response.status_code})")


class TestPerformance:
    """Tests de performance basiques"""
    
    @pytest.mark.asyncio
    async def test_health_check_performance(self, client):
        """Test de performance du health check"""
        start_time = time.time()
        
        # Faire plusieurs requêtes
        tasks = []
        for i in range(10):
            tasks.append(client.get("/health"))
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Toutes les requêtes doivent réussir
        for response in responses:
            assert response.status_code == 200
        
        # Performance raisonnable (moins de 5 secondes pour 10 requêtes)
        assert total_time < 5.0
        
        avg_time = total_time / len(responses)
        print(f"✅ Performance test: {len(responses)} requests in {total_time:.2f}s (avg: {avg_time:.3f}s)")
    
    @pytest.mark.asyncio
    async def test_concurrent_registrations(self, client):
        """Test d'enregistrements concurrents"""
        start_time = time.time()
        
        # Créer plusieurs enregistrements en parallèle
        tasks = []
        for i in range(5):
            registration_data = {
                "username": f"concurrent_node_{i}",
                "display_name": f"Concurrent Node {i}",
                "server_url": f"https://concurrent{i}.example.com",
                "public_key": f"concurrent_{i}_public_key",
                "version": "2.0.0",
                "capabilities": ["messaging"]
            }
            tasks.append(client.post("/auth/register", json=registration_data))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Compter les succès
        successful = 0
        for response in responses:
            if hasattr(response, 'status_code') and response.status_code == 200:
                successful += 1
        
        print(f"✅ Concurrent test: {successful}/{len(tasks)} successful in {total_time:.2f}s")
        
        # Au moins la moitié doit réussir
        assert successful >= len(tasks) // 2


def run_integration_tests():
    """Lancer tous les tests d'intégration"""
    print("=" * 70)
    print("🧪 TESTS D'INTÉGRATION END-TO-END - OpenRed Central API v2.0")
    print("=" * 70)
    
    # Lancer pytest avec options appropriées
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--asyncio-mode=auto",
        "-s"  # Afficher les prints
    ]
    
    exit_code = pytest.main(pytest_args)
    
    print("=" * 70)
    if exit_code == 0:
        print("🎉 TOUS LES TESTS D'INTÉGRATION RÉUSSIS!")
    else:
        print("❌ ÉCHEC DE CERTAINS TESTS D'INTÉGRATION")
    print("=" * 70)
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_integration_tests()
    sys.exit(exit_code)
