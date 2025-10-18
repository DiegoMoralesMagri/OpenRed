#!/usr/bin/env python3
"""Test d'upload d'image avec Diego/OpenRed"""

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
        print(f"Login successful! Token: {token[:20] if token else 'N/A'}...")
        return token
    else:
        print(f"Login failed: {response.text}")
        return None

def test_image_upload(token):
    """Tester l'upload d'image vers le Phantom URN System"""
    # Créer une image de test
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    print(f"Image créée: 100x100 = 10,000 pixels pour fragmentation")
    
    # Headers avec token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Données du fichier
    files = {
        "file": ("test_image.png", img_bytes.getvalue(), "image/png")
    }
    
    data = {
        "title": "Test Phantom URN Burn",
        "description": "Test atomique de fragmentation"
    }
    
    response = requests.post(
        f"{API_BASE}/api/phantom-urn/burn", 
        headers=headers,
        files=files,
        data=data
    )
    
    print(f"Upload Response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload successful!")
        print(f"URN ID: {result.get('urn_id')}")
        print(f"Fragments: {result.get('total_fragments')}")
        print(f"Phoenix Key: {result.get('phoenix_key')[:20]}..." if result.get('phoenix_key') else "No phoenix key")
    else:
        print(f"❌ Upload failed: {response.text}")

def main():
    print("🔥 Test Phantom URN System avec Diego/OpenRed")
    print("=" * 50)
    
    # 1. Login
    token = test_diego_login()
    if not token:
        print("❌ Impossible de se connecter avec Diego/OpenRed")
        return
    
    print()
    
    # 2. Upload
    test_image_upload(token)

if __name__ == "__main__":
    main()