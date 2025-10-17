#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de l'endpoint start-stream après corrections
"""

import requests
import time

def test_start_stream():
    """Test de l'endpoint start-stream corrigé"""
    
    # Attendre que le serveur soit prêt
    time.sleep(2)
    
    try:
        print("🧪 Test Start-Stream après correction")
        print("=" * 40)
        
        # Login
        login_data = {'username': 'Diego', 'password': 'OpenRed'}
        response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        
        if response.status_code != 200:
            print('❌ Problème de login')
            return
        
        token = response.json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Lister les phantoms disponibles
        print("📋 Récupération des phantoms...")
        response = requests.get('http://localhost:8000/api/images/my-urns', headers=headers)
        if response.status_code == 200:
            phantoms = response.json()['phantoms']
            if phantoms:
                phantom_id = phantoms[0]['phantom_id']
                print(f"🔥 Test start-stream avec phantom: {phantom_id[:30]}...")
                
                # Test start-stream corrigé
                response = requests.post(f'http://localhost:8000/api/images/start-stream/{phantom_id}', 
                                       headers=headers, 
                                       json={'mode': 'projection'})
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print('✅ SUCCESS! Start-stream fonctionne')
                    streaming_info = result['streaming_info']
                    print(f"   Dimensions: {streaming_info['dimensions']}")
                    print(f"   Fragments: {streaming_info['total_fragments']}")
                    print(f"   WebSocket: {streaming_info['websocket_url']}")
                    print(f"   HTTP: {streaming_info['http_endpoint']}")
                    print(f"   Protocol: {streaming_info['protocol']}")
                else:
                    print(f"❌ Erreur: {response.text}")
            else:
                print('Aucun phantom disponible')
        else:
            print(f"❌ Erreur récupération phantoms: {response.status_code}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_start_stream()