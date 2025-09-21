#!/usr/bin/env python3
"""
Script de test des endpoints de l'API OpenRed Central
Test script for OpenRed Central API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, headers=None):
    """Test un endpoint et affiche le résultat"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"\n{'='*60}")
        print(f"[{method.upper()}] {endpoint}")
        print(f"Status: {response.status_code}")
        
        try:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response: {response.text}")
            
        return response
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"[{method.upper()}] {endpoint}")
        print(f"ERROR: {str(e)}")
        return None

def main():
    print("🚀 Test de l'API OpenRed Central v2.0")
    print("=" * 60)
    
    # Attendre que l'API soit prête
    time.sleep(2)
    
    # 1. Tests des endpoints de santé
    print("\n📊 ENDPOINTS DE SANTÉ")
    test_endpoint("GET", "/health")
    test_endpoint("GET", "/health/liveness")
    test_endpoint("GET", "/health/readiness")
    
    # 2. Test de la documentation
    print("\n📚 DOCUMENTATION")
    test_endpoint("GET", "/docs")
    test_endpoint("GET", "/openapi.json")
    
    # 3. Test des endpoints d'authentification
    print("\n🔐 ENDPOINTS D'AUTHENTIFICATION")
    
    # Test d'inscription
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "role": "user"
    }
    register_response = test_endpoint("POST", "/auth/register", register_data)
    
    # Test de connexion
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    login_response = test_endpoint("POST", "/auth/login", login_data)
    
    # Récupérer le token si la connexion réussit
    token = None
    if login_response and login_response.status_code == 200:
        try:
            token_data = login_response.json()
            token = token_data.get("access_token")
        except:
            pass
    
    # Headers avec authentification
    auth_headers = {"Authorization": f"Bearer {token}"} if token else None
    
    # Test de refresh token
    if token:
        test_endpoint("POST", "/auth/refresh", headers=auth_headers)
    
    # 4. Test des endpoints de nœuds
    print("\n🔗 ENDPOINTS DE NŒUDS")
    
    # Lister les nœuds
    test_endpoint("GET", "/nodes", headers=auth_headers)
    
    # Créer un nœud
    node_data = {
        "name": "test-node",
        "type": "sensor",
        "description": "Nœud de test",
        "config": {"interval": 30}
    }
    create_node_response = test_endpoint("POST", "/nodes", node_data, auth_headers)
    
    # Récupérer l'ID du nœud créé
    node_id = None
    if create_node_response and create_node_response.status_code in [200, 201]:
        try:
            node_response_data = create_node_response.json()
            node_id = node_response_data.get("id")
        except:
            pass
    
    # Lire un nœud spécifique
    if node_id:
        test_endpoint("GET", f"/nodes/{node_id}", headers=auth_headers)
        
        # Mettre à jour le nœud
        update_data = {
            "name": "test-node-updated",
            "description": "Nœud de test mis à jour"
        }
        test_endpoint("PUT", f"/nodes/{node_id}", update_data, auth_headers)
        
        # Supprimer le nœud
        test_endpoint("DELETE", f"/nodes/{node_id}", headers=auth_headers)
    
    # 5. Test des endpoints de messages
    print("\n💬 ENDPOINTS DE MESSAGES")
    
    # Lister les messages
    test_endpoint("GET", "/messages", headers=auth_headers)
    
    # Créer un message
    message_data = {
        "content": "Message de test",
        "type": "info",
        "source": "test-script"
    }
    test_endpoint("POST", "/messages", message_data, auth_headers)
    
    # Test de déconnexion
    if token:
        print("\n🚪 DÉCONNEXION")
        test_endpoint("POST", "/auth/logout", headers=auth_headers)
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    main()
