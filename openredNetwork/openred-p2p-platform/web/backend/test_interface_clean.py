#!/usr/bin/env python3
"""
🔧 TEST RAPIDE INTERFACE - Sans Emojis
====================================
Test de base pour vérifier que l'interface répond
"""

import requests

def test_interface_basic():
    """Test basique de l'interface"""
    
    print("TEST INTERFACE ENHANCED (Sans Emojis)")
    print("=" * 40)
    
    API_BASE = "http://localhost:8000"
    
    try:
        # 1. Test page d'accueil
        response = requests.get(f"{API_BASE}/", timeout=5)
        
        if response.status_code == 200:
            print("✓ Page d'accueil accessible")
            
            # Vérifier que les fonctions de base sont présentes
            html = response.text
            
            functions = ["loadMyPhantoms", "showActiveStreams", "connectProjectionServer"]
            
            for func in functions:
                if f"function {func}" in html:
                    print(f"✓ Fonction {func} trouvée")
                else:
                    print(f"✗ Fonction {func} MANQUANTE")
            
            # Vérifier absence d'emojis problématiques dans JS
            problematic_emojis = ["🔄", "❌", "✅", "🎭", "🌐"]
            emoji_found = False
            
            for emoji in problematic_emojis:
                if emoji in html:
                    emoji_found = True
                    print(f"⚠ Emoji potentiellement problématique trouvé: {emoji}")
            
            if not emoji_found:
                print("✓ Aucun emoji problématique dans le JavaScript")
            
        else:
            print(f"✗ Erreur accès page: {response.status_code}")
            
        # 2. Test login
        login_data = {"username": "Diego", "password": "OpenRed"}
        response = requests.post(f"{API_BASE}/api/auth/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            print("✓ Login fonctionne")
        else:
            print(f"✗ Login échoue: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Erreur test: {e}")
    
    print("\nINSTRUCTIONS:")
    print("1. Rechargez http://localhost:8000 (F5)")
    print("2. Connectez-vous: Diego / OpenRed")
    print("3. Ouvrez F12 - plus d'erreurs JavaScript!")
    print("4. Testez les boutons et l'upload d'image")

if __name__ == "__main__":
    test_interface_basic()