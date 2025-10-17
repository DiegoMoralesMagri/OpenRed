#!/usr/bin/env python3
"""
🌐 TEST INTERFACE WEB - Debug Enhanced
=====================================
Test pour déboguer l'interface web Enhanced
"""

import requests
import time

def test_web_interface_debug():
    """Test de débogage de l'interface web"""
    
    print("🌐 TEST DEBUG INTERFACE WEB ENHANCED")
    print("=" * 45)
    
    API_BASE = "http://localhost:8000"
    
    # 1. Test connexion serveur
    print("\n📡 ÉTAPE 1: Test connexion serveur")
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        print(f"✅ Serveur accessible: {response.status_code}")
        if response.status_code == 200:
            print("✅ Page d'accueil chargée")
        else:
            print(f"⚠️ Code inattendu: {response.status_code}")
    except Exception as e:
        print(f"❌ Serveur inaccessible: {e}")
        return
    
    # 2. Test endpoint auth
    print("\n🔐 ÉTAPE 2: Test authentification")
    try:
        login_data = {"username": "Diego", "password": "OpenRed"}
        response = requests.post(f"{API_BASE}/api/auth/login", json=login_data, timeout=5)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login réussi")
            print(f"Token: {data.get('token', 'N/A')[:20]}...")
            
            # Test avec cookie
            cookies = response.cookies
            
            # 3. Test endpoint phantom status
            print("\n👻 ÉTAPE 3: Test endpoint phantom")
            try:
                response = requests.get(f"{API_BASE}/api/phantom/status", cookies=cookies, timeout=5)
                print(f"Phantom status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Endpoint phantom accessible")
                else:
                    print(f"⚠️ Phantom endpoint: {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur phantom endpoint: {e}")
            
            # 4. Test upload simple
            print("\n📤 ÉTAPE 4: Test capacité upload")
            try:
                # Créer fichier test minimal
                test_data = b"GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,"
                files = {"file": ("test.gif", test_data, "image/gif")}
                
                response = requests.post(
                    f"{API_BASE}/api/images/upload", 
                    files=files, 
                    cookies=cookies, 
                    timeout=10
                )
                print(f"Upload test: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Upload fonctionne!")
                    result = response.json()
                    print(f"Phantom ID: {result.get('phantom_id', 'N/A')}")
                elif response.status_code == 400:
                    print("⚠️ Upload refusé (normal pour test minimal)")
                else:
                    print(f"❌ Erreur upload: {response.status_code}")
                    try:
                        error = response.json()
                        print(f"Détails: {error.get('detail', 'N/A')}")
                    except:
                        print(f"Réponse: {response.text[:200]}")
                        
            except Exception as e:
                print(f"❌ Erreur test upload: {e}")
        
        else:
            print(f"❌ Login échec: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
    
    # 5. Recommandations
    print(f"\n💡 RECOMMANDATIONS:")
    print(f"1. Ouvrez http://localhost:8000 dans votre navigateur")
    print(f"2. Ouvrez les outils développeur (F12)")
    print(f"3. Regardez la console pour les logs Enhanced")
    print(f"4. Essayez de sélectionner une image")
    print(f"5. Vérifiez les logs dans la console")
    
    print(f"\n🔍 Si l'interface ne répond toujours pas:")
    print(f"- Vérifiez la console navigateur (F12)")
    print(f"- Rechargez la page (F5)")
    print(f"- Reconnectez-vous avec Diego/OpenRed")

if __name__ == "__main__":
    test_web_interface_debug()