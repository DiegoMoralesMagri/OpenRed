#!/usr/bin/env python3
"""
Test d'upload d'image pour vérifier que tout fonctionne
"""

import requests
import io
from PIL import Image
import time

def test_image_upload():
    """Tester l'upload d'une image complète"""
    
    print("🧪 Test upload image Enhanced Phantom URN")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Session avec auth
    session = requests.Session()
    login_data = {"username": "Diego", "password": "OpenRed"}
    login_response = session.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
    
    if login_response.status_code != 200:
        print("❌ Échec authentification")
        return False
    
    print("✅ Authentification réussie")
    
    # Créer une image de test
    print("\n🖼️ Création image de test...")
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Tester l'upload
    print("\n🔥 Test upload vers Enhanced Phantom URN...")
    try:
        files = {'file': ('test_image.png', img_bytes, 'image/png')}
        upload_response = session.post(f"{base_url}/api/images/upload", files=files, timeout=30)
        
        print(f"Status upload: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            print("🎉 UPLOAD RÉUSSI !")
            print(f"   Phantom ID: {result.get('phantom_id', 'N/A')}")
            print(f"   Fragments: {result.get('total_fragments', 'N/A')}")
            print(f"   Enhanced System: {result.get('enhanced_system', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur upload: {upload_response.status_code}")
            print(f"   Détails: {upload_response.text[:300]}...")
            return False
            
    except Exception as e:
        print(f"💥 Exception upload: {e}")
        return False

if __name__ == "__main__":
    success = test_image_upload()
    print(f"\n{'🎉 SUCCÈS' if success else '❌ ÉCHEC'} - Test upload terminé")