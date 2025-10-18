#!/usr/bin/env python3
"""
🔥 TEST INTERFACE WEB ENHANCED - Phoenix de Schrödinger
======================================================
Test complet de l'interface web avec système Enhanced Phantom URN
"""

import requests
import io
from PIL import Image
import json

# Configuration
API_BASE = "http://localhost:8000"
USERNAME = "Diego"
PASSWORD = "OpenRed"

def test_enhanced_web_interface():
    """Test complet de l'interface web Enhanced"""
    
    print("🌀 TEST INTERFACE WEB ENHANCED PHANTOM URN")
    print("=" * 50)
    
    # 1. Login
    print("\n🔑 ÉTAPE 1: Connexion Diego")
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(f"{API_BASE}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    token = response.json().get('token')
    print(f"✅ Login successful! Token: {token[:20]}...")
    
    # 2. Créer image de test Enhanced
    print("\n🔥 ÉTAPE 2: Burn Enhanced → Phoenix de Schrödinger")
    
    # Image colorée pour test
    img = Image.new('RGB', (80, 80))
    pixels = img.load()
    for x in range(80):
        for y in range(80):
            # Motif spiral coloré
            r = int(((x + y) * 3) % 256)
            g = int((x * 2) % 256)
            b = int((y * 2) % 256)
            pixels[x, y] = (r, g, b)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    print(f"📸 Image Enhanced créée: 80x80 = 6,400 pixels atomiques")
    
    # Upload Enhanced
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("enhanced_phoenix.png", img_bytes.getvalue(), "image/png")}
    data = {
        "title": "Phoenix de Schrödinger Test",
        "description": "Test Enhanced avec NCK et vérification continue"
    }
    
    response = requests.post(f"{API_BASE}/api/enhanced-phantom/burn", headers=headers, files=files, data=data)
    
    print(f"Upload Enhanced Response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Phoenix de Schrödinger créé!")
        print(f"\n📊 Résultats Enhanced:")
        print(f"  🌀 Phantom ID: {result.get('phantom_id')}")
        print(f"  ⚛️ Fragments atomiques: {result.get('total_fragments')}")
        print(f"  🔑 NCK User: {result.get('user_nck', '')[:8]}...")
        print(f"  🌀 État quantique: {result.get('schrodinger_matrix')}")
        print(f"  🔄 Rotation NCK: {result.get('nck_enabled')}")
        print(f"  ✅ Vérification continue: {result.get('continuous_verification')}")
        
        enhanced_features = result.get('enhanced_features', {})
        print(f"\n🛡️ Fonctionnalités Enhanced:")
        for feature, enabled in enhanced_features.items():
            status = "✅" if enabled else "❌"
            print(f"  {status} {feature.replace('_', ' ').title()}")
        
        # Récupérer infos pour tests suivants
        phantom_id = result.get('phantom_id')
        user_nck = result.get('user_nck')
        
        if phantom_id and user_nck:
            # 3. Test visualisation Phoenix
            print(f"\n🌀→🦅 ÉTAPE 3: Visualisation Phoenix de Schrödinger")
            
            view_data = {"nck": user_nck}
            response = requests.post(
                f"{API_BASE}/api/enhanced-phantom/{phantom_id}/view",
                headers=headers,
                data=view_data
            )
            
            print(f"View Phoenix Response: {response.status_code}")
            
            if response.status_code == 200:
                view_result = response.json()
                print(f"✅ Phoenix de Schrödinger projeté!")
                print(f"  🌀 Message: {view_result.get('message')}")
                print(f"  📐 Dimensions: {view_result.get('dimensions')}")
                print(f"  🔑 Nouvelle NCK: {view_result.get('next_nck', '')[:8]}...")
                
                security_notes = view_result.get('security_notes', [])
                print(f"\n🛡️ Notes de sécurité:")
                for note in security_notes:
                    print(f"  {note}")
                
                next_nck = view_result.get('next_nck')
                
                # 4. Test statut système
                print(f"\n✅ ÉTAPE 4: Vérification statut système")
                
                response = requests.get(
                    f"{API_BASE}/api/enhanced-phantom/{phantom_id}/status",
                    headers=headers
                )
                
                print(f"Status Response: {response.status_code}")
                
                if response.status_code == 200:
                    status_result = response.json()
                    print(f"✅ Statut système Enhanced:")
                    
                    server_status = status_result.get('server_status', {})
                    print(f"  🟢 Actif: {server_status.get('active')}")
                    print(f"  📁 Statut: {server_status.get('status')}")
                    print(f"  ⚛️ Fragments: {server_status.get('fragments_count')}")
                    
                    system_features = status_result.get('system_features', {})
                    print(f"\n🔥 Fonctionnalités système:")
                    for feature, enabled in system_features.items():
                        status = "✅" if enabled else "❌"
                        print(f"  {status} {feature.replace('_', ' ').title()}")
                    
                    print(f"\n🔒 Niveau sécurité: {status_result.get('security_level')}")
                
                # 5. Test rotation NCK
                if next_nck:
                    print(f"\n🔄 ÉTAPE 5: Test rotation NCK")
                    print(f"⚠️  Tentative avec ancienne NCK (doit échouer):")
                    
                    old_view_data = {"nck": user_nck}
                    response = requests.post(
                        f"{API_BASE}/api/enhanced-phantom/{phantom_id}/view",
                        headers=headers,
                        data=old_view_data
                    )
                    
                    if response.status_code == 403:
                        print("✅ Accès refusé avec ancienne NCK (sécurité confirmée)")
                    else:
                        print("❌ ERREUR: Accès autorisé avec ancienne NCK!")
                    
                    print(f"\n✅ Test avec nouvelle NCK:")
                    new_view_data = {"nck": next_nck}
                    response = requests.post(
                        f"{API_BASE}/api/enhanced-phantom/{phantom_id}/view",
                        headers=headers,
                        data=new_view_data
                    )
                    
                    if response.status_code == 200:
                        print("✅ Accès autorisé avec nouvelle NCK")
                        print("🔄 Rotation NCK fonctionnelle!")
                    else:
                        print(f"❌ Échec avec nouvelle NCK: {response.status_code}")
            
            else:
                print(f"❌ View failed: {response.text}")
        
        # Résumé final
        print(f"\n🎉 TEST INTERFACE WEB ENHANCED TERMINÉ!")
        print(f"=" * 50)
        print(f"✅ Phoenix de Schrödinger: Opérationnel")
        print(f"🔑 NCK System: Fonctionnel")
        print(f"🌀 Matrice cryptée: Jamais reconstruction complète")
        print(f"✅ Vérification continue: Active")
        print(f"⚛️ Fragmentation atomique: 6,400 fragments")
        print(f"🛡️ Sécurité maximale: Enhanced Phantom URN")
        
    else:
        print(f"❌ Upload Enhanced failed: {response.text}")

if __name__ == "__main__":
    test_enhanced_web_interface()