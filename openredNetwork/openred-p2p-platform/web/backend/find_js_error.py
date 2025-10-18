#!/usr/bin/env python3
"""
Test pour identifier l'erreur de syntaxe JavaScript précise
"""

import requests
import re
import sys

def find_js_syntax_error():
    """Trouver l'erreur de syntaxe JavaScript"""
    
    print("🔍 Recherche d'erreur de syntaxe JavaScript")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Session avec auth
    session = requests.Session()
    login_data = {"username": "Diego", "password": "OpenRed"}
    session.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
    
    # Récupérer la page
    response = session.get(f"{base_url}/images", timeout=5)
    content = response.text
    
    # Extraire JavaScript
    script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    if not script_match:
        print("❌ Script non trouvé")
        return
    
    js_content = script_match.group(1)
    lines = js_content.split('\n')
    
    print(f"📄 JavaScript: {len(lines)} lignes")
    
    # Chercher des caractères problématiques
    print("\n🔍 Recherche de caractères problématiques...")
    
    problematic_chars = ['🔥', '📋', '📄', '✅', '❌', '⚠️', '📤', '📥', '🌀', '💎', '⚛️', '🔑', '👻', '💎', '🎭', '📡', '🖱️']
    
    errors_found = []
    
    for line_num, line in enumerate(lines, 1):
        # Chercher les emojis dans les chaînes JavaScript
        for char in problematic_chars:
            if char in line:
                # Vérifier si c'est dans une chaîne de caractères
                if "'" in line or '"' in line:
                    errors_found.append((line_num, char, line.strip()))
    
    if errors_found:
        print(f"\n❌ {len(errors_found)} problèmes détectés:")
        for line_num, char, line in errors_found[:20]:  # Limiter à 20
            print(f"   Ligne {line_num}: {char} dans '{line[:80]}...'")
    else:
        print("✅ Aucun emoji problématique trouvé")
    
    # Chercher des erreurs de guillemets
    print("\n🔍 Vérification guillemets...")
    quote_errors = []
    
    for line_num, line in enumerate(lines, 1):
        # Compter les guillemets
        single_quotes = line.count("'")
        double_quotes = line.count('"')
        
        # Si nombre impair de guillemets
        if single_quotes % 2 != 0 or double_quotes % 2 != 0:
            quote_errors.append((line_num, line.strip()))
    
    if quote_errors:
        print(f"❌ {len(quote_errors)} erreurs de guillemets:")
        for line_num, line in quote_errors[:10]:
            print(f"   Ligne {line_num}: {line[:80]}...")
    else:
        print("✅ Guillemets équilibrés")
    
    # Sauvegarder le JavaScript pour analyse externe
    with open("debug_javascript.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    
    print(f"\n💾 JavaScript sauvegardé dans debug_javascript.js")
    
    return len(errors_found) == 0 and len(quote_errors) == 0

if __name__ == "__main__":
    success = find_js_syntax_error()
    sys.exit(0 if success else 1)