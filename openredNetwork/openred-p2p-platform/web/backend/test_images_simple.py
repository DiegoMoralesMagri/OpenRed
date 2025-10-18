#!/usr/bin/env python3
"""
Test simple de la page /images sans Selenium
"""

import requests
import sys

def test_images_page_simple():
    """Test simple de la page /images"""
    
    print("🧪 Test simple page /images")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test d'accessibilité de base
    print("\n🌐 Test accessibilité...")
    try:
        response = requests.get(f"{base_url}/images", timeout=5)
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
            
            # Vérifier qu'il n'y a pas d'accolades en trop
            lines = content.split('\n')
            suspicious_lines = []
            
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped == '}' and i > 1:
                    prev_line = lines[i-2].strip() if i > 1 else ""
                    if prev_line.endswith('}'):
                        suspicious_lines.append(f"Ligne {i}: {line.strip()}")
            
            if suspicious_lines:
                print("\n⚠️ Accolades suspectes détectées:")
                for line in suspicious_lines:
                    print(f"   {line}")
            else:
                print("\n✅ Pas d'accolades en trop détectées")
                
            return True
                
        else:
            print(f"❌ Page /images retourne {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False

if __name__ == "__main__":
    success = test_images_page_simple()
    sys.exit(0 if success else 1)