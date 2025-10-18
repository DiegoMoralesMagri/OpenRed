#!/usr/bin/env python3
"""
🧹 OpenRed Auth Reset Tool
Remet à zéro complètement le système d'authentification
"""

import os
import json
import shutil
from pathlib import Path

def reset_auth_system():
    """Reset complet du système d'authentification"""
    print("🧹 === OpenRed Auth Reset Tool ===\n")
    
    # Répertoires de données possibles
    data_dirs = [
        "./user_data",
        "./user_data_2", 
        os.getenv("OPENRED_DATA_DIR", "./user_data"),
        "../user_data",
        "../../user_data"
    ]
    
    auth_files_found = []
    
    # Chercher tous les fichiers auth.json
    for data_dir in data_dirs:
        auth_file = os.path.join(data_dir, "auth.json")
        if os.path.exists(auth_file):
            auth_files_found.append(auth_file)
            print(f"🔍 Found auth file: {auth_file}")
    
    # Chercher dans le répertoire courant et sous-répertoires
    for root, dirs, files in os.walk("."):
        for file in files:
            if file == "auth.json":
                auth_path = os.path.join(root, file)
                if auth_path not in auth_files_found:
                    auth_files_found.append(auth_path)
                    print(f"🔍 Found auth file: {auth_path}")
    
    if not auth_files_found:
        print("✅ No auth files found - system is clean")
        
        # Vérifier quand même via l'API
        try:
            import requests
            response = requests.get("http://localhost:8000/api/auth/status")
            if response.status_code == 200:
                data = response.json()
                if data.get("configured"):
                    print("⚠️ API reports user configured but no auth.json found")
                    print("   This might be an in-memory state - restart server")
                else:
                    print("✅ API confirms no user configured")
        except Exception as e:
            print(f"ℹ️ Could not check API status: {e}")
        
        return
    
    # Supprimer tous les fichiers auth trouvés
    print(f"\n🗑️ Found {len(auth_files_found)} auth files to remove:")
    
    for auth_file in auth_files_found:
        try:
            # Afficher le contenu avant suppression
            with open(auth_file, 'r') as f:
                data = json.load(f)
                username = data.get("username", "unknown")
                created_at = data.get("created_at", "unknown")
                print(f"   📄 {auth_file}")
                print(f"      User: {username}")
                print(f"      Created: {created_at}")
            
            # Supprimer le fichier
            os.remove(auth_file)
            print(f"   ✅ Removed: {auth_file}")
            
        except Exception as e:
            print(f"   ❌ Error removing {auth_file}: {e}")
    
    print(f"\n🎯 Auth reset complete!")
    print("📝 Next steps:")
    print("   1. Restart the OpenRed server")
    print("   2. Go to http://localhost:8000/login")
    print("   3. Use 'Première Installation' tab")
    print("   4. Create your new account")

def main():
    reset_auth_system()

if __name__ == "__main__":
    main()