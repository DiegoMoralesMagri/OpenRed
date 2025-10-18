#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de l'upload avec les corrections Enhanced Phantom URN System
"""

import requests
import time
import json
from PIL import Image, ImageDraw

def create_test_image():
    """Créer une image de test simple"""
    img = Image.new('RGB', (200, 200), color='lightblue')
    draw = ImageDraw.Draw(img)
    draw.text((50, 90), "TEST URN", fill='darkblue')
    
    test_path = "test_image_corrected.png"
    img.save(test_path)
    return test_path

def test_enhanced_phantom_upload():
    """Test complet de l'upload avec Enhanced Phantom URN System"""
    
    print("🧪 Test Upload Enhanced Phantom URN System")
    print("=" * 50)
    
    # Configuration
    BASE_URL = "http://localhost:8000"
    
    # 1. Créer image de test
    print("📸 Création d'une image de test...")
    test_image = create_test_image()
    
    # 2. Login
    print("🔐 Connexion...")
    login_data = {
        "username": "Diego",
        "password": "OpenRed"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Échec login: {response.status_code}")
        print(f"Réponse: {response.text}")
        return
    
    # Récupérer token
    login_result = response.json()
    print(f"Login result: {login_result}")
    auth_token = login_result.get("access_token") or login_result.get("token")
    
    if not auth_token:
        print("❌ Token non trouvé dans la réponse")
        return
        
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    print(f"✅ Connexion réussie - Token: {auth_token[:20]}...")
    
    # 3. Test stats système (pour vérifier la correction)
    print("\n📊 Test stats système...")
    try:
        stats_response = requests.get(f"{BASE_URL}/api/images/system-stats", headers=headers)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"✅ Stats système: {stats['system_type']}")
            print(f"   Phantoms actifs: {stats['active_phantoms']}")
            print(f"   Phoenixes Schrödinger: {stats.get('schrodinger_phoenixes', 0)}")
        else:
            print(f"❌ Erreur stats: {stats_response.status_code}")
    except Exception as e:
        print(f"❌ Erreur stats: {e}")
    
    # 4. Upload image
    print("\n🔥 Upload image vers Enhanced Phantom URN...")
    
    with open(test_image, 'rb') as f:
        files = {
            'file': ('test_corrected.png', f, 'image/png')
        }
        data = {
            'phantom_name': 'Test Enhanced URN Corrected'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/images/upload", 
            files=files, 
            data=data, 
            headers=headers
        )
    
    if response.status_code != 200:
        print(f"❌ Échec upload: {response.status_code}")
        try:
            print(f"Erreur: {response.json()}")
        except:
            print(f"Réponse: {response.text}")
        return
    
    # Récupérer job ID
    result = response.json()
    job_id = result["job_id"]
    print(f"✅ Upload initié - Job ID: {job_id}")
    
    # 5. Suivre le progrès
    print("\n⏳ Suivi du traitement...")
    
    for attempt in range(30):  # 30 tentatives max
        try:
            status_response = requests.get(
                f"{BASE_URL}/api/jobs/{job_id}/status", 
                headers=headers
            )
            
            if status_response.status_code == 200:
                job_status = status_response.json()
                status = job_status["status"]
                progress = job_status.get("progress", 0)
                
                print(f"📊 Status: {status} - Progress: {progress}%")
                
                if status == "completed":
                    print("🎉 SUCCÈS ! URN créée")
                    result = job_status.get("result", {})
                    print(f"   Phantom ID: {result.get('phantom_id', 'N/A')}")
                    print(f"   Fragments: {result.get('total_fragments', 'N/A')}")
                    print(f"   Phoenix Key: {result.get('phoenix_key', 'N/A')[:20]}...")
                    print(f"   System: {result.get('system_type', 'N/A')}")
                    break
                elif status == "failed":
                    print(f"❌ ÉCHEC: {job_status.get('error', 'Erreur inconnue')}")
                    break
                    
        except Exception as e:
            print(f"❌ Erreur status: {e}")
        
        time.sleep(2)
    
    # 6. Test des URNs utilisateur
    print("\n📋 Test liste URNs utilisateur...")
    try:
        urns_response = requests.get(f"{BASE_URL}/api/images/my-urns", headers=headers)
        if urns_response.status_code == 200:
            urns = urns_response.json()
            print(f"✅ URNs trouvées: {urns['total']}")
            for phantom in urns.get('phantoms', [])[:3]:  # Afficher max 3
                print(f"   - {phantom['phantom_id']} ({phantom['type']})")
        else:
            print(f"❌ Erreur URNs: {urns_response.status_code}")
    except Exception as e:
        print(f"❌ Erreur URNs: {e}")
    
    print("\n🏁 Test terminé")

if __name__ == "__main__":
    test_enhanced_phantom_upload()