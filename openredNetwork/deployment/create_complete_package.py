#!/usr/bin/env python3
"""
🚀 OpenRed Complete Package Creator
Crée un package ZIP complet pour le déploiement one-liner
"""

import os
import zipfile
import json
import shutil
from datetime import datetime

def create_complete_package():
    """Crée le package OpenRed complet"""
    print("🚀 Création du package OpenRed complet...")
    
    # Répertoire de base
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    
    # Nom du package
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    package_name = f"openred-complete-{timestamp}.zip"
    package_path = os.path.join(base_dir, package_name)
    
    print(f"📦 Création de {package_name}...")
    
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # 1. Web Platform complète
        web_platform_dir = os.path.join(project_root, "openred-p2p-platform")
        if os.path.exists(web_platform_dir):
            for root, dirs, files in os.walk(web_platform_dir):
                # Exclure les dossiers de test volumineux
                dirs[:] = [d for d in dirs if not d.startswith('test_') and d != '__pycache__']
                
                for file in files:
                    if not file.endswith(('.pyc', '.pyo')) and not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, project_root)
                        zipf.write(file_path, arc_path)
                        print(f"  + {arc_path}")
        
        # 2. Phantom Images System
        phantom_dir = os.path.join(project_root, "phantom-images-demo")
        essential_phantom_files = [
            "orp_viewer.py",
            "phantom_urn_system.py",
            "register_orp_extension.py",
            "URN_SYSTEM_PRESENTATION.md",
            "ARCHITECTURE_STATUS.md"
        ]
        
        for file in essential_phantom_files:
            file_path = os.path.join(phantom_dir, file)
            if os.path.exists(file_path):
                arc_path = f"phantom-images-demo/{file}"
                zipf.write(file_path, arc_path)
                print(f"  + {arc_path}")
        
        # 3. Node Client P2P
        node_client_dir = os.path.join(project_root, "node-client")
        if os.path.exists(node_client_dir):
            for file in os.listdir(node_client_dir):
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(node_client_dir, file)
                    arc_path = f"node-client/{file}"
                    zipf.write(file_path, arc_path)
                    print(f"  + {arc_path}")
        
        # 4. Documentation essentielle
        docs = [
            "README.md",
            "REVOLUTION_SUCCESS.md",
            "URN_COMPLETE_DOCUMENTATION.md"
        ]
        
        for doc in docs:
            doc_path = os.path.join(project_root, doc)
            if os.path.exists(doc_path):
                zipf.write(doc_path, doc)
                print(f"  + {doc}")
        
        # 5. Scripts de déploiement
        deployment_files = [
            "universal_installer.py",
            "setup_distribution.py"
        ]
        
        for script in deployment_files:
            script_path = os.path.join(base_dir, script)
            if os.path.exists(script_path):
                arc_path = f"deployment/{script}"
                zipf.write(script_path, arc_path)
                print(f"  + {arc_path}")
        
        # 6. Configuration par défaut
        config = {
            "version": "2.0.0",
            "platform": "openred-complete",
            "features": [
                "phantom-images",
                "urn-phoenix",
                "spider-protocol",
                "p2p-asymmetric",
                "web-platform"
            ],
            "installation": {
                "auto_configure": True,
                "enable_web": True,
                "enable_p2p": True
            }
        }
        
        config_data = json.dumps(config, indent=2)
        zipf.writestr("config.json", config_data)
        print("  + config.json")
        
        # 7. Script de démarrage
        startup_script = '''#!/usr/bin/env python3
"""
🚀 OpenRed Startup Script
Démarre automatiquement tous les services OpenRed
"""

import os
import sys
import subprocess
import json

def start_openred():
    print("🚀 Démarrage OpenRed...")
    
    # Charger la configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print(f"📦 Version: {config['version']}")
    print(f"🌟 Fonctionnalités: {', '.join(config['features'])}")
    
    # Démarrer le serveur web si activé
    if config['installation']['enable_web']:
        web_dir = 'openred-p2p-platform/web/backend'
        if os.path.exists(web_dir):
            print("🌐 Démarrage du serveur web...")
            os.chdir(web_dir)
            subprocess.Popen([sys.executable, 'web_api.py'])
            print("✅ Serveur web démarré sur http://localhost:8000")
    
    print("🎉 OpenRed démarré avec succès!")

if __name__ == "__main__":
    start_openred()
'''
        
        zipf.writestr("start_openred.py", startup_script)
        print("  + start_openred.py")
    
    # Statistiques
    file_size = os.path.getsize(package_path)
    print(f"\n✅ Package créé: {package_name}")
    print(f"📏 Taille: {file_size/1024:.1f} KB")
    
    return package_path

if __name__ == "__main__":
    package_path = create_complete_package()
    print(f"\n🎯 Package prêt: {os.path.basename(package_path)}")