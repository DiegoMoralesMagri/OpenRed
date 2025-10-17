#!/usr/bin/env python3
"""
🔧 TEST INTERFACE JAVASCRIPT - Enhanced Functions
================================================
Test pour vérifier que toutes les fonctions JavaScript sont définies
"""

import requests

def test_interface_javascript():
    """Test des fonctions JavaScript de l'interface"""
    
    print("🔧 TEST FONCTIONS JAVASCRIPT ENHANCED")
    print("=" * 40)
    
    API_BASE = "http://localhost:8000"
    
    try:
        # Récupérer la page HTML
        response = requests.get(f"{API_BASE}/", timeout=5)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Vérifier présence des fonctions
            functions_to_check = [
                "loadMyPhantoms",
                "showActiveStreams", 
                "connectProjectionServer",
                "loadActiveProjections",
                "handleFiles",
                "uploadImage",
                "checkAuthStatus"
            ]
            
            print("🔍 Vérification fonctions JavaScript:")
            
            for func in functions_to_check:
                if f"function {func}" in html_content or f"async function {func}" in html_content:
                    print(f"  ✅ {func} - Définie")
                else:
                    print(f"  ❌ {func} - MANQUANTE")
            
            # Vérifier que les onclick sont présents
            onclick_checks = [
                'onclick="loadMyPhantoms()"',
                'onclick="showActiveStreams()"',
                'onclick="connectProjectionServer()"'
            ]
            
            print(f"\n🔗 Vérification événements onclick:")
            
            for onclick in onclick_checks:
                if onclick in html_content:
                    print(f"  ✅ {onclick} - Présent")
                else:
                    print(f"  ❌ {onclick} - MANQUANT")
            
            # Vérifier ordre des définitions
            loadmy_pos = html_content.find("function loadMyPhantoms")
            dom_pos = html_content.find("DOMContentLoaded")
            
            if loadmy_pos > 0 and dom_pos > 0:
                if loadmy_pos < dom_pos:
                    print(f"\n✅ Ordre correct: Fonctions définies avant DOMContentLoaded")
                else:
                    print(f"\n❌ ERREUR: Fonctions définies après DOMContentLoaded")
            
            print(f"\n🎯 INSTRUCTIONS:")
            print(f"1. Rechargez la page: http://localhost:8000")
            print(f"2. Connectez-vous: Diego / OpenRed")
            print(f"3. Ouvrez F12 (Console)")
            print(f"4. Vous devriez voir: '🚀 Initialisation Enhanced Phantom URN Interface'")
            print(f"5. Cliquez sur les boutons - ils ne devraient plus générer d'erreurs!")
            
        else:
            print(f"❌ Erreur accès page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")

if __name__ == "__main__":
    test_interface_javascript()