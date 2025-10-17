#!/usr/bin/env python3
"""
🔧 DIAGNOSTIC UPLOAD PHANTOM URN
==============================
Test des endpoints d'upload pour diagnostiquer le problème
"""

import requests
import json
from PIL import Image
import numpy as np
import os

def create_simple_test_image():
    """Créer une image de test très simple"""
    print("🎨 Création image test simple...")
    
    # Image 50x50 très simple
    image_array = np.zeros((50, 50, 3), dtype=np.uint8)
    image_array[:, :] = [255, 0, 0]  # Rouge uni
    
    pil_image = Image.fromarray(image_array)
    pil_image.save("diagnostic_test.jpg", "JPEG")
    
    print("✅ Image test créée: 50x50 rouge")
    return "diagnostic_test.jpg"

def test_login_flow():
    """Test du processus de connexion complet"""
    print("\n🔐 Test processus de connexion...")
    
    try:
        # 1. Obtenir la page de login
        session = requests.Session()
        
        resp = session.get("http://localhost:8000/")
        print(f"✅ Page accueil: {resp.status_code}")
        
        # 2. Essayer de récupérer les utilisateurs
        resp = session.get("http://localhost:8000/api/users")
        if resp.status_code == 200:
            users = resp.json()
            print(f"✅ Utilisateurs disponibles: {len(users.get('users', []))}")
            
            if users.get('users'):
                # 3. Essayer de se connecter avec le premier utilisateur
                user = users['users'][0]
                login_data = {
                    "username": user['username'],
                    "password": "test"
                }
                
                resp = session.post("http://localhost:8000/api/login", json=login_data)
                print(f"🔐 Login {user['username']}: {resp.status_code}")
                
                if resp.status_code == 200:
                    result = resp.json()
                    print(f"✅ Token reçu: {result.get('access_token', 'NO TOKEN')[:20]}...")
                    return session, result.get('access_token')
                else:
                    print(f"❌ Échec login: {resp.text}")
        else:
            print(f"❌ Erreur utilisateurs: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur login: {e}")
    
    return None, None

def test_upload_with_session(session, token, image_path):
    """Test upload avec session authentifiée"""
    print(f"\n📤 Test upload avec session...")
    
    try:
        # Préparer headers avec token
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        # Préparer fichier
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            
            # Test upload
            resp = session.post(
                "http://localhost:8000/api/images/upload",
                files=files,
                headers=headers
            )
            
            print(f"📤 Upload response: {resp.status_code}")
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"✅ Upload réussi!")
                print(f"   Phantom ID: {result.get('phantom_id')}")
                print(f"   Fragments: {result.get('total_fragments')}")
                return True
            else:
                print(f"❌ Erreur upload: {resp.status_code}")
                print(f"   Response: {resp.text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception upload: {e}")
        return False

def test_direct_upload_no_auth():
    """Test upload direct sans authentification pour voir l'erreur"""
    print(f"\n🔍 Test upload sans auth (pour voir l'erreur)...")
    
    image_path = create_simple_test_image()
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            
            resp = requests.post(
                "http://localhost:8000/api/images/upload",
                files=files
            )
            
            print(f"📤 Upload sans auth: {resp.status_code}")
            print(f"   Response: {resp.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    finally:
        if os.path.exists(image_path):
            os.unlink(image_path)

def test_api_endpoints_status():
    """Test statut des endpoints principaux"""
    print(f"\n🔍 Test des endpoints API...")
    
    endpoints = [
        "/",
        "/images", 
        "/api/users",
        "/api/images/my-urns",
        "/api/images/system-stats"
    ]
    
    for endpoint in endpoints:
        try:
            resp = requests.get(f"http://localhost:8000{endpoint}")
            status_emoji = "✅" if resp.status_code in [200, 401] else "❌"
            print(f"{status_emoji} {endpoint}: {resp.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Exception - {e}")

def main():
    """Diagnostic complet"""
    print("🔧 DIAGNOSTIC UPLOAD PHANTOM URN")
    print("=" * 40)
    
    try:
        # 1. Test endpoints de base
        test_api_endpoints_status()
        
        # 2. Test upload sans auth
        test_direct_upload_no_auth()
        
        # 3. Test processus complet avec auth
        session, token = test_login_flow()
        
        if session and token:
            image_path = create_simple_test_image()
            try:
                success = test_upload_with_session(session, token, image_path)
                
                if success:
                    print("\n🎉 DIAGNOSTIC: Upload fonctionne avec authentification!")
                    print("💡 PROBLÈME PROBABLE: Interface JavaScript ne gère pas l'auth correctement")
                else:
                    print("\n⚠️ DIAGNOSTIC: Problème avec l'endpoint upload")
                    
            finally:
                if os.path.exists(image_path):
                    os.unlink(image_path)
        else:
            print("\n⚠️ DIAGNOSTIC: Problème avec l'authentification")
            
        print(f"\n🔧 SOLUTIONS POSSIBLES:")
        print(f"1. Vérifier que vous êtes connecté dans l'interface web")
        print(f"2. Regarder la console du navigateur (F12) pour erreurs JavaScript")
        print(f"3. Vérifier que les cookies de session sont bien envoyés")
        print(f"4. Tester l'upload avec un fichier plus petit")
        
    except Exception as e:
        print(f"❌ Erreur diagnostic: {e}")

if __name__ == "__main__":
    main()