#!/usr/bin/env python3
"""
Extraire et numéroter le JavaScript pour identifier les lignes avec erreurs
"""

import requests
import re

def extract_javascript():
    """Extraire le JavaScript et le numéroter"""
    
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
    
    print("📄 JavaScript extrait avec numérotation:")
    print("=" * 50)
    
    # Chercher autour des lignes 200 et 472
    problem_lines = [200, 472]
    
    for problem_line in problem_lines:
        print(f"\n🔍 Autour de la ligne {problem_line}:")
        start = max(1, problem_line - 5)
        end = min(len(lines), problem_line + 5)
        
        for i in range(start, end + 1):
            if i <= len(lines):
                line = lines[i-1] if i > 0 else ""
                marker = ">>> " if i == problem_line else "    "
                print(f"{marker}{i:3d}: {line}")
    
    # Chercher spécifiquement les accolades isolées
    print(f"\n🔍 Recherche d'accolades isolées:")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == '}':
            print(f"Ligne {i}: '{line}'")

if __name__ == "__main__":
    extract_javascript()