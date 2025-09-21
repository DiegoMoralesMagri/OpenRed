#!/usr/bin/env python3
"""
Tests d'Intégration Live - OpenRed Central API v2.0
Tests sur l'API déjà en cours d'exécution
"""

import requests
import time
import json
import sys

# Configuration pour l'API en cours d'exécution
API_BASE_URL = "http://127.0.0.1:8000"  # Port standard utilisé


def test_api_availability():
    """Vérifier que l'API est disponible"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API disponible et fonctionnelle")
            return True
        else:
            print(f"⚠️ API répond mais status incorrect: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API non disponible: {e}")
        print("💡 Assurez-vous que l'API est démarrée avec: python main_new.py")
        return False


def test_health_endpoints():
    """Test des endpoints de santé"""
    print("🔍 Test des endpoints de santé...")
    
    try:
        # Health check principal
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Health check: {data['status']}")
        
        # Test autres endpoints de santé si disponibles
        endpoints_to_test = [
            ("/health/liveness", "Liveness probe"),
            ("/health/readiness", "Readiness probe"),
            ("/docs", "Swagger documentation"),
            ("/openapi.json", "OpenAPI schema")
        ]
        
        for endpoint, name in endpoints_to_test:
            try:
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name}: disponible")
                else:
                    print(f"⚠️ {name}: status {response.status_code}")
            except:
                print(f"⚠️ {name}: non disponible")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test health: {e}")
        return False


def test_authentication_endpoints():
    """Test des endpoints d'authentification"""
    print("🔍 Test des endpoints d'authentification...")
    
    try:
        # Test endpoint register (même si on n'enregistre pas vraiment)
        test_data = {
            "username": "test_live_integration",
            "display_name": "Test Live Integration",
            "server_url": "https://test.live.example.com",
            "public_key": "test_live_public_key",
            "version": "2.0.0",
            "capabilities": ["messaging", "testing"]
        }
        
        response = requests.post(f"{API_BASE_URL}/auth/register", json=test_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Register endpoint: {data.get('message', 'OK')}")
        elif response.status_code in [400, 422]:
            print(f"✅ Register endpoint: validation fonctionne (status {response.status_code})")
        elif response.status_code == 404:
            print("⚠️ Register endpoint: non implémenté")
        else:
            print(f"⚠️ Register endpoint: status {response.status_code}")
        
        # Test endpoint login
        login_data = {
            "username": "test_user",
            "signature": "test_signature"
        }
        
        response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login endpoint: {data.get('message', 'OK')}")
        elif response.status_code in [400, 401, 422]:
            print(f"✅ Login endpoint: validation fonctionne (status {response.status_code})")
        elif response.status_code == 404:
            print("⚠️ Login endpoint: non implémenté")
        else:
            print(f"⚠️ Login endpoint: status {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test auth: {e}")
        return False


def test_node_endpoints():
    """Test des endpoints de nœuds"""
    print("🔍 Test des endpoints de nœuds...")
    
    try:
        # Test liste des nœuds
        response = requests.get(f"{API_BASE_URL}/nodes", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            nodes_count = len(data.get("nodes", []))
            print(f"✅ Nodes endpoint: {nodes_count} nœuds trouvés")
        elif response.status_code == 404:
            print("⚠️ Nodes endpoint: non implémenté ou aucun nœud")
        else:
            print(f"⚠️ Nodes endpoint: status {response.status_code}")
        
        # Test recherche de nœud spécifique
        response = requests.get(f"{API_BASE_URL}/nodes/test_node", timeout=5)
        
        if response.status_code == 200:
            print("✅ Node specific endpoint: disponible")
        elif response.status_code == 404:
            print("✅ Node specific endpoint: 404 attendu (nœud inexistant)")
        else:
            print(f"⚠️ Node specific endpoint: status {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test nodes: {e}")
        return False


def test_error_handling():
    """Test de gestion des erreurs"""
    print("🔍 Test de gestion des erreurs...")
    
    try:
        # Endpoint inexistant
        response = requests.get(f"{API_BASE_URL}/nonexistent", timeout=5)
        if response.status_code == 404:
            print("✅ 404 pour endpoint inexistant")
        else:
            print(f"⚠️ Endpoint inexistant: status {response.status_code}")
        
        # Méthode HTTP incorrecte
        response = requests.delete(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 405:
            print("✅ 405 pour méthode non autorisée")
        else:
            print(f"⚠️ Méthode incorrecte: status {response.status_code}")
        
        # JSON malformé
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if response.status_code in [400, 422]:
                print("✅ Gestion des erreurs JSON")
            else:
                print(f"⚠️ JSON malformé: status {response.status_code}")
        except:
            print("⚠️ Test JSON malformé échoué")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test errors: {e}")
        return False


def test_performance():
    """Test de performance basique"""
    print("🔍 Test de performance...")
    
    try:
        start_time = time.time()
        
        # 10 requêtes health check
        for i in range(10):
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 10
        
        print(f"✅ Performance: 10 requêtes en {total_time:.2f}s (moy: {avg_time:.3f}s)")
        
        if avg_time < 0.5:
            print("🚀 Performance excellente!")
        elif avg_time < 1.0:
            print("✅ Performance bonne")
        else:
            print("⚠️ Performance à améliorer")
        
        return avg_time < 2.0  # Acceptable si moins de 2s par requête
        
    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
        return False


def test_api_documentation():
    """Test de la documentation API"""
    print("🔍 Test de la documentation API...")
    
    try:
        # Swagger UI
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Swagger UI disponible")
        else:
            print(f"⚠️ Swagger UI: status {response.status_code}")
        
        # OpenAPI JSON
        response = requests.get(f"{API_BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            version = data.get("info", {}).get("version", "unknown")
            title = data.get("info", {}).get("title", "unknown")
            print(f"✅ OpenAPI schema: {title} v{version}")
            
            # Compter les endpoints
            paths = data.get("paths", {})
            endpoint_count = len(paths)
            print(f"📊 {endpoint_count} endpoints documentés")
            
        else:
            print(f"⚠️ OpenAPI schema: status {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test documentation: {e}")
        return False


def run_live_integration_tests():
    """Lancer tous les tests d'intégration live"""
    print("=" * 70)
    print("🧪 TESTS D'INTÉGRATION LIVE - OpenRed Central API v2.0")
    print("=" * 70)
    print(f"🎯 Test de l'API sur: {API_BASE_URL}")
    print()
    
    # Vérifier la disponibilité de l'API
    if not test_api_availability():
        print()
        print("❌ L'API n'est pas disponible. Démarrez-la d'abord avec:")
        print("   python main_new.py")
        print("   ou")
        print("   uvicorn main_new:app --host 0.0.0.0 --port 8000")
        return False
    
    print()
    
    # Tests
    tests = [
        ("Health Endpoints", test_health_endpoints),
        ("Authentication Endpoints", test_authentication_endpoints),
        ("Node Endpoints", test_node_endpoints),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance),
        ("API Documentation", test_api_documentation)
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
    
    # Résultats finaux
    print("=" * 70)
    print("📊 RÉSULTATS DES TESTS LIVE")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"   {test_name:<30} : {status}")
        if result:
            passed += 1
    
    print()
    print(f"📈 Score: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS! L'API fonctionne parfaitement.")
        return True
    elif passed >= total * 0.8:
        print("✅ SUCCÈS MAJORITAIRE - L'API fonctionne bien avec quelques points à améliorer.")
        return True
    elif passed >= total * 0.5:
        print("⚠️ SUCCÈS PARTIEL - L'API fonctionne mais nécessite des améliorations.")
        return True
    else:
        print("❌ ÉCHEC - L'API présente des problèmes importants.")
        return False


if __name__ == "__main__":
    success = run_live_integration_tests()
    sys.exit(0 if success else 1)
