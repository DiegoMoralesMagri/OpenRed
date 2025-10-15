#!/usr/bin/env python3
"""
Test rapide des endpoints pour identifier les erreurs 500
"""

import requests
import sys

def test_endpoints():
    """Tester les endpoints qui génèrent des erreurs 500"""
    
    print("🧪 Test des endpoints avec erreurs 500")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Session avec auth
    session = requests.Session()
    login_data = {"username": "Diego", "password": "OpenRed"}
    login_response = session.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
    
    if login_response.status_code != 200:
        print("❌ Échec authentification")
        return False
    
    print("✅ Authentification réussie")
    
    # Tester les endpoints
    endpoints = [
        "/api/phantom/status",
        "/api/images/system-stats", 
        "/api/images/my-urns"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Test {endpoint}...")
        try:
            response = session.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Succès: {len(str(data))} caractères")
            elif response.status_code == 500:
                print(f"   ❌ Erreur 500: {response.text[:200]}...")
            else:
                print(f"   ⚠️ Status {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
    
    return True

if __name__ == "__main__":
    test_endpoints()