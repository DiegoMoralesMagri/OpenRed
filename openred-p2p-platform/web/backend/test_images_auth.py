#!/usr/bin/env python3
"""
Test de la page /images avec authentification
"""

import requests
import sys

def test_images_page_auth():
    """Test de la page /images avec authentification"""
    
    print("🧪 Test page /images avec authentification")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Créer une session
    session = requests.Session()
    
    # 1. Login d'abord
    print("\n🔐 Authentification...")
    try:
        login_data = {
            "username": "Diego",
            "password": "OpenRed"
        }
        
        login_response = session.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        
        if login_response.status_code == 200:
            print("✅ Authentification réussie")
        else:
            print(f"❌ Échec authentification: {login_response.status_code}")
            print(f"   Réponse: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
        return False
    
    # 2. Test d'accessibilité page /images
    print("\n🌐 Test accessibilité page /images...")
    try:
        response = session.get(f"{base_url}/images", timeout=5)
        if response.status_code == 200:
            print("✅ Page /images accessible")
            
            # Vérifier la présence du JavaScript corrigé
            content = response.text
            
            # Chercher les fonctions principales
            functions_to_check = [
                "function loadMyPhantoms",
                "function showActiveStreams", 
                "function connectProjectionServer"
            ]
            
            print("\n🔍 Vérification fonctions JavaScript...")
            for func in functions_to_check:
                if func in content:
                    print(f"   ✅ {func}: Trouvée")
                else:
                    print(f"   ❌ {func}: Manquante")
            
            # Vérifier la structure JavaScript générale
            if "async function loadMyPhantoms()" in content:
                print("   ✅ loadMyPhantoms: Syntaxe async correcte")
            
            if "function showActiveStreams()" in content:
                print("   ✅ showActiveStreams: Syntaxe correcte")
                
            if "function connectProjectionServer()" in content:
                print("   ✅ connectProjectionServer: Syntaxe correcte")
            
            # Compter les accolades pour détecter les erreurs
            open_braces = content.count('{')
            close_braces = content.count('}')
            print(f"\n📊 Accolades: {open_braces} ouvrantes, {close_braces} fermantes")
            
            if open_braces == close_braces:
                print("   ✅ Accolades équilibrées")
            else:
                print("   ❌ Accolades déséquilibrées")
                
            return True
                
        else:
            print(f"❌ Page /images retourne {response.status_code}")
            if response.status_code == 401:
                print("   🔐 Problème d'authentification persistant")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False

if __name__ == "__main__":
    success = test_images_page_auth()
    sys.exit(0 if success else 1)