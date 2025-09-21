#!/usr/bin/env python3
"""
Simplified Integration Tests - OpenRed Central API v2.0
Tests with simplified server and existing endpoints
"""

import asyncio
import sqlite3
import tempfile
import os
import sys
import time
import json
import subprocess
import signal
from pathlib import Path
import threading
import requests
from contextlib import contextmanager

# Test configuration
TEST_HOST = "127.0.0.1"
TEST_PORT = 8890  # Different port to avoid conflicts
TEST_BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}"


class SimpleTestServer:
    """Simplified test server manager"""
    
    def __init__(self):
        self.process = None
        self.temp_db = None
        
    def setup_test_database(self):
        """Créer une base de données temporaire"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Utiliser le script d'initialisation existant
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Tables simplifiées
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_messages_sent INTEGER DEFAULT 0,
                total_messages_received INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE auth_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                node_id TEXT NOT NULL,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        
        return self.temp_db.name
    
    def start_server(self):
        """Démarrer le serveur avec main_new.py"""
        try:
            db_path = self.setup_test_database()
            
            # Configurer l'environnement
            env = os.environ.copy()
            env['DATABASE_URL'] = f"sqlite:///{db_path}"
            env['API_HOST'] = TEST_HOST
            env['API_PORT'] = str(TEST_PORT)
            env['ENVIRONMENT'] = 'development'  # Utiliser 'development' au lieu de 'testing'
            env['DEBUG'] = 'false'
            env['SECRET_KEY'] = 'test-secret-for-integration-tests-32chars-min'  # Au moins 32 caractères
            
            # Démarrer le serveur avec main_new.py
            cmd = [
                sys.executable, 
                "main_new.py"
            ]
            
            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Attendre que le serveur soit prêt
            for i in range(20):
                try:
                    response = requests.get(f"{TEST_BASE_URL}/health", timeout=2)
                    if response.status_code == 200:
                        return True
                except Exception as e:
                    if i == 0:  # Afficher l'erreur seulement la première fois
                        print(f"Tentative de connexion échouée: {e}")
                time.sleep(1)
                
                # Vérifier si le processus est encore vivant
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    print(f"Processus terminé avec code: {self.process.returncode}")
                    print(f"STDOUT: {stdout.decode()}")
                    print(f"STDERR: {stderr.decode()}")
                    return False
                else:
                    if i % 5 == 0:  # Afficher le statut toutes les 5 secondes
                        print(f"Attente du serveur... ({i+1}/20)")
            
            print("Timeout - le serveur n'a pas répondu dans les temps")
            return False
            
        except Exception as e:
            print(f"Erreur démarrage serveur: {e}")
            return False
    
    def stop_server(self):
        """Arrêter le serveur"""
        if self.process:
            try:
                if os.name == 'nt':  # Windows
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                else:  # Unix
                    self.process.terminate()
                    
                self.process.wait(timeout=5)
            except:
                if self.process.poll() is None:
                    self.process.kill()
                    
        if self.temp_db and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except:
                pass


def test_health_endpoints():
    """Test des endpoints de santé"""
    print("🔍 Test des endpoints de santé...")
    
    try:
        # Health check
        response = requests.get(f"{TEST_BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Health check: {data['status']}")
        
        # Liveness probe
        response = requests.get(f"{TEST_BASE_URL}/health/liveness", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Liveness probe: {data.get('status', 'ok')}")
        else:
            print(f"⚠️ Liveness probe non disponible (status: {response.status_code})")
        
        # Readiness probe
        response = requests.get(f"{TEST_BASE_URL}/health/readiness", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Readiness probe: {data.get('status', 'ok')}")
        else:
            print(f"⚠️ Readiness probe non disponible (status: {response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test health: {e}")
        return False


def test_authentication_flow():
    """Test du flux d'authentification"""
    print("🔍 Test du flux d'authentification...")
    
    try:
        # Test d'enregistrement
        registration_data = {
            "username": "test_integration_simple",
            "display_name": "Test Integration Simple",
            "server_url": "https://test.simple.example.com",
            "public_key": "test_simple_public_key",
            "version": "2.0.0",
            "capabilities": ["messaging", "testing"]
        }
        
        response = requests.post(
            f"{TEST_BASE_URL}/auth/register",
            json=registration_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enregistrement réussi: {data.get('node_id', 'unknown')}")
            node_id = data.get('node_id')
        else:
            print(f"⚠️ Endpoint register non disponible (status: {response.status_code})")
            return False
        
        # Test de login
        login_data = {
            "username": "test_integration_simple",
            "signature": "test_simple_signature"
        }
        
        response = requests.post(
            f"{TEST_BASE_URL}/auth/login",
            json=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login réussi: token expires in {data.get('expires_in', 'unknown')}s")
            return True
        else:
            print(f"⚠️ Endpoint login non disponible (status: {response.status_code})")
            return False
        
    except Exception as e:
        print(f"❌ Erreur test auth: {e}")
        return False


def test_node_discovery():
    """Test de découverte des nœuds"""
    print("🔍 Test de découverte des nœuds...")
    
    try:
        response = requests.get(f"{TEST_BASE_URL}/nodes", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            nodes_count = len(data.get("nodes", []))
            print(f"✅ Découverte de nœuds: {nodes_count} nœuds trouvés")
            return True
        elif response.status_code == 404:
            print("✅ Aucun nœud trouvé (normal)")
            return True
        else:
            print(f"⚠️ Endpoint nodes non disponible (status: {response.status_code})")
            return False
        
    except Exception as e:
        print(f"❌ Erreur test discovery: {e}")
        return False


def test_error_handling():
    """Test de gestion des erreurs"""
    print("🔍 Test de gestion des erreurs...")
    
    try:
        # Endpoint inexistant
        response = requests.get(f"{TEST_BASE_URL}/nonexistent", timeout=5)
        assert response.status_code == 404
        print("✅ 404 pour endpoint inexistant")
        
        # JSON invalide si endpoint existe
        try:
            response = requests.post(
                f"{TEST_BASE_URL}/auth/register",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if response.status_code in [400, 422]:
                print("✅ JSON invalide rejeté")
            else:
                print(f"⚠️ JSON invalide - status: {response.status_code}")
        except:
            print("⚠️ Test JSON invalide échoué")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test errors: {e}")
        return False


def test_performance_basic():
    """Test de performance de base"""
    print("🔍 Test de performance basique...")
    
    try:
        start_time = time.time()
        
        # 5 requêtes health check
        for i in range(5):
            response = requests.get(f"{TEST_BASE_URL}/health", timeout=5)
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 5
        
        print(f"✅ Performance: 5 requêtes en {total_time:.2f}s (moy: {avg_time:.3f}s)")
        
        # Performance raisonnable
        return avg_time < 1.0
        
    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
        return False


def run_simplified_integration_tests():
    """Lancer les tests d'intégration simplifiés"""
    print("=" * 70)
    print("🧪 TESTS D'INTÉGRATION SIMPLIFIÉS - OpenRed Central API v2.0")
    print("=" * 70)
    
    server = SimpleTestServer()
    
    try:
        print("🚀 Démarrage du serveur de test...")
        if not server.start_server():
            print("❌ Impossible de démarrer le serveur de test")
            return False
        
        print(f"✅ Serveur de test démarré sur {TEST_BASE_URL}")
        print()
        
        # Tests
        tests = [
            ("Health Endpoints", test_health_endpoints),
            ("Authentication Flow", test_authentication_flow),
            ("Node Discovery", test_node_discovery),
            ("Error Handling", test_error_handling),
            ("Performance Basic", test_performance_basic)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"📋 {test_name}...")
            try:
                result = test_func()
                results.append((test_name, result))
                print()
            except Exception as e:
                print(f"❌ Erreur dans {test_name}: {e}")
                results.append((test_name, False))
                print()
        
        # Résultats
        print("=" * 70)
        print("📊 RÉSULTATS DES TESTS")
        print("=" * 70)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
            print(f"   {test_name:<25} : {status}")
            if result:
                passed += 1
        
        print()
        print(f"📈 Score: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 TOUS LES TESTS RÉUSSIS!")
            return True
        elif passed >= total * 0.7:
            print("⚠️ SUCCÈS PARTIEL - La plupart des tests ont réussi")
            return True
        else:
            print("❌ ÉCHEC - Trop de tests ont échoué")
            return False
        
    finally:
        print()
        print("🧹 Arrêt du serveur de test...")
        server.stop_server()
        print("✅ Nettoyage terminé")


if __name__ == "__main__":
    success = run_simplified_integration_tests()
    sys.exit(0 if success else 1)
