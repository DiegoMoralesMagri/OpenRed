#!/usr/bin/env python3
"""Test du workflow complet : Upload normal → Phantom → Phantom URN"""

import requests
import io
from PIL import Image
import json

# Configuration
API_BASE = "http://localhost:8000"
USERNAME = "Diego"
PASSWORD = "OpenRed"

def test_diego_login():
    """Tester la connexion avec Diego/OpenRed"""
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(f"{API_BASE}/api/auth/login", json=login_data)
    print(f"Login Response: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"✅ Login successful! Token: {token[:20] if token else 'N/A'}...")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_normal_image_upload(token):
    """Tester l'upload normal d'image"""
    # Créer une image de test
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    print(f"Image créée: 100x100 = 10,000 pixels")
    
    # Headers avec token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Données du fichier
    files = {
        "file": ("test_image.png", img_bytes.getvalue(), "image/png")
    }
    
    data = {
        "title": "Test Image Upload",
        "description": "Image normale pour test workflow"
    }
    
    response = requests.post(
        f"{API_BASE}/api/images/upload", 
        headers=headers,
        files=files,
        data=data
    )
    
    print(f"Upload Response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload normal successful!")
        print(f"Image ID: {result['image_info']['image_id']}")
        print(f"Actions disponibles:")
        for action, url in result['image_info'].get('actions', {}).items():
            print(f"  - {action}: {url}")
        return result['image_info']['image_id']
    else:
        print(f"❌ Upload failed: {response.text}")
        return None

def test_create_phantom(image_id, token):
    """Tester la création de phantom ORP"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(
        f"{API_BASE}/api/images/{image_id}/create-phantom",
        headers=headers
    )
    
    print(f"Create Phantom Response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Phantom ORP créé!")
        print(f"Projection URL: {result.get('projection_url')}")
        return True
    else:
        print(f"❌ Phantom creation failed: {response.text}")
        return False

def test_create_phantom_urn(image_id, token):
    """Tester la création de phantom URN"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(
        f"{API_BASE}/api/images/{image_id}/create-phantom-urn",
        headers=headers
    )
    
    print(f"Create Phantom URN Response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Phantom URN créé!")
        print(f"URN ID: {result.get('urn_id')}")
        print(f"Fragments: {result.get('total_fragments')}")
        print(f"Phoenix Key: {result.get('phoenix_key', '')[:20]}..." if result.get('phoenix_key') else "No phoenix key")
        return True
    else:
        print(f"❌ Phantom URN creation failed: {response.text}")
        return False

def main():
    print("🔥 Test Workflow Complet : Upload → Phantom → Phantom URN")
    print("=" * 60)
    
    # 1. Login
    token = test_diego_login()
    if not token:
        return
    
    print()
    
    # 2. Upload normal
    print("📸 ÉTAPE 1: Upload normal d'image")
    image_id = test_normal_image_upload(token)
    if not image_id:
        return
    
    print()
    
    # 3. Créer phantom ORP
    print("👻 ÉTAPE 2: Créer Phantom ORP pour projection")
    test_create_phantom(image_id, token)
    
    print()
    
    # 4. Créer phantom URN
    print("💎 ÉTAPE 3: Créer Phantom URN pour téléchargement sécurisé")
    test_create_phantom_urn(image_id, token)
    
    print()
    print("🎉 Workflow complet testé!")

if __name__ == "__main__":
    main()