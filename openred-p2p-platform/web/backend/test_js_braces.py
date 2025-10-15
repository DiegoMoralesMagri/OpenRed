#!/usr/bin/env python3
"""
Analyseur d'accolades JavaScript pour détecter les erreurs de syntaxe
"""

import requests
import sys
import re

def analyze_javascript_braces():
    """Analyser les accolades dans le JavaScript de la page /images"""
    
    print("🔍 Analyse des accolades JavaScript")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Créer une session avec auth
    session = requests.Session()
    
    # Login
    login_data = {"username": "Diego", "password": "OpenRed"}
    login_response = session.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
    
    if login_response.status_code != 200:
        print("❌ Échec authentification")
        return False
    
    # Récupérer la page
    response = session.get(f"{base_url}/images", timeout=5)
    if response.status_code != 200:
        print(f"❌ Page inaccessible: {response.status_code}")
        return False
    
    content = response.text
    
    # Extraire juste la section JavaScript
    script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    if not script_match:
        print("❌ Pas de section <script> trouvée")
        return False
    
    js_content = script_match.group(1)
    
    # Analyser ligne par ligne
    lines = js_content.split('\n')
    
    brace_stack = []
    errors = []
    
    for line_num, line in enumerate(lines, 1):
        # Enlever les commentaires
        line_clean = re.sub(r'//.*$', '', line)
        
        # Compter les accolades
        for char_pos, char in enumerate(line_clean):
            if char == '{':
                brace_stack.append((line_num, char_pos, 'open'))
            elif char == '}':
                if brace_stack:
                    brace_stack.pop()
                else:
                    errors.append(f"Ligne {line_num}: Accolade fermante sans ouvrante")
    
    # Vérifier les accolades non fermées
    if brace_stack:
        for line_num, pos, _ in brace_stack:
            errors.append(f"Ligne {line_num}: Accolade ouvrante non fermée")
    
    print(f"📊 Analyse terminée:")
    print(f"   Lignes JavaScript: {len(lines)}")
    print(f"   Erreurs détectées: {len(errors)}")
    
    if errors:
        print("\n❌ Erreurs trouvées:")
        for error in errors[:10]:  # Limiter à 10 erreurs
            print(f"   {error}")
        if len(errors) > 10:
            print(f"   ... et {len(errors) - 10} autres erreurs")
    else:
        print("✅ Aucune erreur d'accolades détectée")
    
    # Chercher les fonctions problématiques spécifiquement
    print("\n🔍 Vérification fonctions spécifiques...")
    
    function_patterns = [
        r'function\s+loadMyPhantoms\s*\(\s*\)\s*{',
        r'function\s+showActiveStreams\s*\(\s*\)\s*{',
        r'function\s+connectProjectionServer\s*\(\s*\)\s*{'
    ]
    
    for pattern in function_patterns:
        matches = re.finditer(pattern, js_content)
        for match in matches:
            # Trouver la ligne
            lines_before = js_content[:match.start()].count('\n')
            print(f"   ✅ Fonction trouvée ligne {lines_before + 1}")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = analyze_javascript_braces()
    sys.exit(0 if success else 1)