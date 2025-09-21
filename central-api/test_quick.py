#!/usr/bin/env python3
"""
Script de test rapide pour les endpoints OpenRed Central API
Quick test script for OpenRed Central API endpoints
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test un endpoint et affiche le résultat"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 Testing {method} {url}")
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            print(f"❌ Method {method} not supported in this script")
            return
        
        print(f"✅ Status: {response.status_code}")
        
        try:
            json_response = response.json()
            print(f"📄 Response: {json.dumps(json_response, indent=2, ensure_ascii=False)}")
        except:
            print(f"📄 Response (text): {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - API might be down")
    except requests.exceptions.Timeout:
        print(f"❌ Timeout - API might be slow")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Tests principaux"""
    print("🚀 OpenRed Central API - Tests rapides")
    print("=" * 50)
    
    # Test endpoints de base
    test_endpoint("/")
    test_endpoint("/ping")
    
    # Test endpoints de santé
    test_endpoint("/health")
    test_endpoint("/health/liveness")
    test_endpoint("/health/readiness")
    
    # Test endpoints d'authentification
    test_endpoint("/auth/register", "POST", {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    })
    
    test_endpoint("/auth/login", "POST", {
        "username": "testuser",
        "password": "testpassword123"
    })
    
    # Test endpoints de nœuds
    test_endpoint("/nodes")
    
    # Test endpoints de messages
    test_endpoint("/messages")
    
    print("\n🏁 Tests terminés!")

if __name__ == "__main__":
    main()
