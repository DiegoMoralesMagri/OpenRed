#!/usr/bin/env python3
# FR: Test de l'API OpenRed O2Switch
# EN: OpenRed O2Switch API Test
# ES: Prueba de API OpenRed O2Switch
# ZH: OpenRed O2Switch API 测试

"""
Test complet de l'API OpenRed optimisée pour O2Switch
"""

import sys
import time
import json
import requests
from datetime import datetime

def test_o2switch_api():
    """Test complet de l'API O2Switch"""
    
    # Configuration de test
    base_url = "http://localhost:8000"
    
    print("🧪 Test de l'API OpenRed O2Switch")
    print("=" * 40)
    
    tests = []
    
    # Test 1: Health Check
    print("\n1️⃣ Test Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK: {data.get('status')}")
            tests.append(("Health Check", True, "OK"))
        else:
            print(f"❌ Health check failed: {response.status_code}")
            tests.append(("Health Check", False, f"Status {response.status_code}"))
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        tests.append(("Health Check", False, str(e)))
    
    # Test 2: Diagnostic
    print("\n2️⃣ Test Diagnostic...")
    try:
        response = requests.get(f"{base_url}/diagnostic", timeout=5)
        if response.status_code == 200:
            data = response.json()
            modules_ok = all("✅" in status for status in data.get("modules_status", {}).values())
            print(f"✅ Diagnostic OK, modules: {'OK' if modules_ok else 'SOME MISSING'}")
            tests.append(("Diagnostic", True, "OK"))
        else:
            print(f"❌ Diagnostic failed: {response.status_code}")
            tests.append(("Diagnostic", False, f"Status {response.status_code}"))
    except Exception as e:
        print(f"❌ Diagnostic error: {str(e)}")
        tests.append(("Diagnostic", False, str(e)))
    
    # Test 3: Enregistrement de nœud
    print("\n3️⃣ Test Enregistrement de Nœud...")
    try:
        node_data = {
            "node_id": f"test-node-{int(time.time())}",
            "name": "Test Node O2Switch",
            "description": "Nœud de test pour validation O2Switch",
            "endpoint": "https://test-node.example.com",
            "capabilities": ["storage", "compute", "ai"]
        }
        
        response = requests.post(
            f"{base_url}/api/v1/nodes/register",
            json=node_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Nœud enregistré: {data.get('node_id')}")
                tests.append(("Node Registration", True, "OK"))
                
                # Test 4: Récupération du nœud
                print("\n4️⃣ Test Récupération de Nœud...")
                response = requests.get(f"{base_url}/api/v1/nodes", timeout=5)
                if response.status_code == 200:
                    nodes_data = response.json()
                    if nodes_data.get("total", 0) > 0:
                        print(f"✅ Nœud trouvé: {nodes_data['total']} nœud(s)")
                        tests.append(("Node Retrieval", True, "OK"))
                    else:
                        print("❌ Aucun nœud trouvé")
                        tests.append(("Node Retrieval", False, "No nodes found"))
                else:
                    print(f"❌ Récupération échouée: {response.status_code}")
                    tests.append(("Node Retrieval", False, f"Status {response.status_code}"))
            else:
                print(f"❌ Enregistrement échoué: {data.get('message')}")
                tests.append(("Node Registration", False, data.get('message')))
        else:
            print(f"❌ Enregistrement échoué: {response.status_code}")
            tests.append(("Node Registration", False, f"Status {response.status_code}"))
    except Exception as e:
        print(f"❌ Erreur d'enregistrement: {str(e)}")
        tests.append(("Node Registration", False, str(e)))
    
    # Test 5: API racine
    print("\n5️⃣ Test API Racine...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "OpenRed Central API - O2Switch":
                print(f"✅ API racine OK: {data.get('version')}")
                tests.append(("Root API", True, "OK"))
            else:
                print(f"❌ API racine inattendue: {data.get('message')}")
                tests.append(("Root API", False, "Unexpected response"))
        else:
            print(f"❌ API racine échouée: {response.status_code}")
            tests.append(("Root API", False, f"Status {response.status_code}"))
    except Exception as e:
        print(f"❌ Erreur API racine: {str(e)}")
        tests.append(("Root API", False, str(e)))
    
    # Résumé
    print("\n📊 Résumé des tests:")
    print("=" * 30)
    passed = sum(1 for _, success, _ in tests if success)
    total = len(tests)
    
    for test_name, success, details in tests:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
    
    print(f"\n🎯 Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS ! L'API O2Switch fonctionne parfaitement.")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
        return False

if __name__ == "__main__":
    # Vérifier si un serveur est supposé être en cours d'exécution
    if len(sys.argv) > 1 and sys.argv[1] == "--wait-for-server":
        print("⏳ Attente du démarrage du serveur...")
        time.sleep(3)
    
    success = test_o2switch_api()
    sys.exit(0 if success else 1)