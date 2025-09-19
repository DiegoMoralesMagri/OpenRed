# FR: Fichier: test_main.py — Tests d'intégration pour l'API central (implementation)
# EN: File: test_main.py — Integration tests for the central API (implementation)
# ES: Archivo: test_main.py — Pruebas de integración para la API central (implementation)
# ZH: 文件: test_main.py — 中央 API 的集成测试 (implementation)

# Tests de l'API centrale O-Red
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.models import User, Node
from app.core.security import create_access_token

# Configuration des tests
@pytest.fixture
def client():
    """Client de test pour l'API."""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Client asynchrone pour les tests."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def test_user_data():
    """Données de test pour un utilisateur."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def test_node_data():
    """Données de test pour un nœud."""
    return {
        "node_id": "test-node-123",
        "ip_address": "192.168.1.100",
        "port": 8001,
        "public_key": "test_public_key_data",
        "capabilities": ["ai_computing", "storage", "relay"]
    }

class TestHealthCheck:
    """Tests de vérification de santé."""
    
    def test_health_check(self, client):
        """Test du endpoint de santé."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_metrics_endpoint(self, client):
        """Test du endpoint des métriques."""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Vérifier que c'est bien du format Prometheus
        assert "python_info" in response.text

class TestAuthentication:
    """Tests d'authentification."""
    
    def test_register_user_success(self, client, test_user_data):
        """Test d'inscription réussie."""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "password" not in data  # Le mot de passe ne doit pas être retourné

    def test_register_user_duplicate_email(self, client, test_user_data):
        """Test d'inscription avec email déjà utilisé."""
        # Premier utilisateur
        client.post("/api/auth/register", json=test_user_data)
        
        # Tentative avec le même email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "another_user"
        response = client.post("/api/auth/register", json=duplicate_data)
        assert response.status_code == 400

    def test_login_success(self, client, test_user_data):
        """Test de connexion réussie."""
        # Inscription d'abord
        client.post("/api/auth/register", json=test_user_data)
        
        # Connexion
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Test de connexion avec identifiants invalides."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", data=login_data)
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self, client):
        """Test d'accès à un endpoint protégé sans token."""
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_protected_endpoint_with_valid_token(self, client, test_user_data):
        """Test d'accès à un endpoint protégé avec token valide."""
        # Inscription et connexion
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Accès à l'endpoint protégé
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]

class TestNodeManagement:
    """Tests de gestion des nœuds."""
    
    def test_register_node_success(self, client, test_node_data, test_user_data):
        """Test d'enregistrement de nœud réussi."""
        # Créer un utilisateur et obtenir un token
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Enregistrer le nœud
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/nodes/register", json=test_node_data, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["node_id"] == test_node_data["node_id"]
        assert data["status"] == "active"

    def test_get_nodes_list(self, client, test_user_data):
        """Test de récupération de la liste des nœuds."""
        # Créer un utilisateur et obtenir un token
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Récupérer la liste des nœuds
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/nodes/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_node_heartbeat(self, client, test_node_data, test_user_data):
        """Test du heartbeat de nœud."""
        # Créer un utilisateur et enregistrer un nœud
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        client.post("/api/nodes/register", json=test_node_data, headers=headers)
        
        # Envoyer un heartbeat
        heartbeat_data = {
            "node_id": test_node_data["node_id"],
            "cpu_usage": 45.5,
            "memory_usage": 60.2,
            "storage_available": 1000000000,  # 1GB
            "active_connections": 5
        }
        response = client.post("/api/nodes/heartbeat", json=heartbeat_data, headers=headers)
        assert response.status_code == 200

class TestUserManagement:
    """Tests de gestion des utilisateurs."""
    
    def test_get_user_profile(self, client, test_user_data):
        """Test de récupération du profil utilisateur."""
        # Inscription et connexion
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Récupération du profil
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]

    def test_update_user_profile(self, client, test_user_data):
        """Test de mise à jour du profil utilisateur."""
        # Inscription et connexion
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Mise à jour du profil
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {
            "full_name": "Test User Full Name",
            "bio": "This is a test bio"
        }
        response = client.put("/api/users/me", json=update_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["bio"] == update_data["bio"]

class TestAPIValidation:
    """Tests de validation des données API."""
    
    def test_register_invalid_email(self, client):
        """Test d'inscription avec email invalide."""
        invalid_data = {
            "username": "testuser",
            "email": "invalid_email",
            "password": "testpassword123"
        }
        response = client.post("/api/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Test d'inscription avec mot de passe trop court."""
        invalid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"
        }
        response = client.post("/api/auth/register", json=invalid_data)
        assert response.status_code == 422

    def test_node_register_missing_fields(self, client, test_user_data):
        """Test d'enregistrement de nœud avec champs manquants."""
        # Créer un utilisateur et obtenir un token
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Tentative d'enregistrement avec données incomplètes
        headers = {"Authorization": f"Bearer {token}"}
        incomplete_data = {
            "node_id": "test-node-123"
            # Champs manquants : ip_address, port, etc.
        }
        response = client.post("/api/nodes/register", json=incomplete_data, headers=headers)
        assert response.status_code == 422

class TestErrorHandling:
    """Tests de gestion des erreurs."""
    
    def test_404_endpoint(self, client):
        """Test d'accès à un endpoint inexistant."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test de méthode HTTP non autorisée."""
        response = client.delete("/api/auth/register")
        assert response.status_code == 405

    def test_invalid_json(self, client):
        """Test avec JSON invalide."""
        response = client.post(
            "/api/auth/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

class TestRateLimiting:
    """Tests de limitation de taux."""
    
    def test_rate_limiting(self, client):
        """Test de limitation de taux (si activée)."""
        # Faire plusieurs requêtes rapidement
        for i in range(10):
            response = client.get("/health")
            if response.status_code == 429:
                # Rate limiting déclenché
                assert "Retry-After" in response.headers
                break
        else:
            # Rate limiting peut ne pas être activé en mode test
            pass

# Tests de performance (optionnels)
class TestPerformance:
    """Tests de performance basiques."""
    
    def test_health_check_performance(self, client):
        """Test de performance du health check."""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Moins d'une seconde

    def test_concurrent_requests(self, client):
        """Test de requêtes concurrentes."""
        import concurrent.futures
        import time
        
        def make_request():
            return client.get("/health")
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            responses = [future.result() for future in futures]
        end_time = time.time()
        
        # Vérifier que toutes les requêtes ont réussi
        assert all(r.status_code == 200 for r in responses)
        assert (end_time - start_time) < 10.0  # Moins de 10 secondes pour 50 requêtes

if __name__ == "__main__":
    pytest.main([__file__, "-v"])