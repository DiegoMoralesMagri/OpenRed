#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test des corrections d'endpoints
"""

import requests

def test_endpoints():
    """Test des endpoints corrigés"""
    
    BASE_URL = "http://localhost:8000"
    
    # Login pour obtenir le token
    login_data = {"username": "Diego", "password": "OpenRed"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Échec login")
        return
    
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🧪 Test des endpoints corrigés")
    print("=" * 40)
    
    # Test 1: System stats
    print("\n📊 Test system-stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/images/system-stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats OK: {data['stats']['system_type']}")
            print(f"   Phantoms: {data['stats']['active_phantoms']}")
            print(f"   Phoenixes: {data['stats']['schrodinger_phoenixes']}")
        else:
            print(f"❌ Erreur stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception stats: {e}")
    
    # Test 2: My URNs
    print("\n🔱 Test my-urns...")
    try:
        response = requests.get(f"{BASE_URL}/api/images/my-urns", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ URNs OK: {data['total']} phantoms")
            for phantom in data['phantoms'][:2]:  # Max 2
                print(f"   - {phantom['phantom_id'][:20]}... ({phantom['type']})")
        else:
            print(f"❌ Erreur URNs: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception URNs: {e}")
    
    # Test 3: Active streams
    print("\n📡 Test active-streams...")
    try:
        response = requests.get(f"{BASE_URL}/api/images/active-streams", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Streams OK: {data['total']} streams")
            for stream in data['streams'][:2]:  # Max 2
                print(f"   - {stream['phantom_id'][:20]}... ({stream.get('type', 'unknown')})")
        else:
            print(f"❌ Erreur streams: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception streams: {e}")
    
    print("\n✅ Tests terminés")

if __name__ == "__main__":
    test_endpoints()