#!/usr/bin/env python3
"""Test simple du téléversement d'image avec Phantom URN automatique"""

import requests
import io
from PIL import Image
import json

# Configuration
API_BASE = "http://localhost:8000"
USERNAME = "Diego"
PASSWORD = "OpenRed"

def main():
    print("🔥 Test Téléversement d'Image avec Phantom URN automatique")
    print("=" * 60)
    
    # 1. Login Diego
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(f"{API_BASE}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    token = response.json().get('token')
    print(f"✅ Login successful! Token: {token[:20]}...")
    
    # 2. Créer et téléverser une image
    img = Image.new('RGB', (150, 150), color='purple')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    print(f"\n📸 Image créée: 150x150 = 22,500 pixels")
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("ma_belle_image.png", img_bytes.getvalue(), "image/png")}
    
    response = requests.post(f"{API_BASE}/api/images/upload", headers=headers, files=files)
    
    print(f"Upload Response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload et Phantom URN créés automatiquement!")
        print(f"\n📊 Résultats:")
        print(f"  - Phantom ID: {result.get('phantom_id')}")
        print(f"  - Fragments atomiques: {result.get('total_fragments')}")
        print(f"  - Projection ORP: {result.get('dual_system', {}).get('orp_streaming')}")
        print(f"  - Téléchargement URN: {result.get('dual_system', {}).get('urn_download')}")
        print(f"  - Message: {result.get('message')}")
        
        print(f"\n🎯 Votre image est maintenant:")
        print(f"  1. 💾 Stockée en original sur votre serveur")
        print(f"  2. 👻 Disponible en projection ORP publique")
        print(f"  3. 💎 Fragmentée en URN pour téléchargement sécurisé")
        
    else:
        print(f"❌ Upload failed: {response.text}")

if __name__ == "__main__":
    main()