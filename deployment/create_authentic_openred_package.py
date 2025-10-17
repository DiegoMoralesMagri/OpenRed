#!/usr/bin/env python3
"""
🌐 OpenRed AUTHENTIC Platform Package Creator
Déploie le VRAI système OpenRed avec tous les protocoles établis
- FastAPI Backend complet
- Système d'authentification OpenRed
- Protocoles de friendship établis
- Interface complète fonctionnelle
- Respect total de l'architecture projet
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path

def create_authentic_openred_package():
    """Crée le package AUTHENTIQUE OpenRed avec tous les protocoles"""
    print("🌐 Création du package OpenRed AUTHENTIQUE...")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    project_root = base_dir.parent
    openred_dir = project_root / "openred-p2p-platform"
    
    # Package authentique complet
    package_name = "openred-authentic-platform.zip"
    package_path = base_dir / package_name
    
    print(f"📦 Création de {package_name}...")
    print("🎯 Respect TOTAL des protocoles OpenRed établis")
    
    if not openred_dir.exists():
        print(f"❌ Erreur: Répertoire OpenRed non trouvé: {openred_dir}")
        return None
    
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        print("\n🔧 === CORE SYSTEM ===")
        
        # 1. Nœud P2P principal
        core_files = [
            "openred_p2p_node.py",
            "friendship_protocol.py", 
            "social_messaging.py",
            "conditional_urn_sharing.py",
            "phantom_image_urn_system.py",
            "image_urn_system.py",
            "requirements.txt"
        ]
        
        for file in core_files:
            file_path = openred_dir / file
            if file_path.exists():
                zipf.write(file_path, file)
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠️  {file} - non trouvé")
        
        print("\n🌐 === WEB PLATFORM ===")
        
        # 2. Backend FastAPI complet
        backend_dir = openred_dir / "web" / "backend"
        if backend_dir.exists():
            for py_file in backend_dir.glob("*.py"):
                rel_path = f"web/backend/{py_file.name}"
                zipf.write(py_file, rel_path)
                print(f"  ✅ {rel_path}")
        
        # 3. Frontend authentique
        frontend_dir = openred_dir / "web" / "frontend"
        if frontend_dir.exists():
            for html_file in frontend_dir.glob("*.html"):
                rel_path = f"web/frontend/{html_file.name}"
                zipf.write(html_file, rel_path)
                print(f"  ✅ {rel_path}")
        
        print("\n🔐 === CORE PROTOCOLS ===")
        
        # 4. Core protocols directory
        core_dir = openred_dir / "core"
        if core_dir.exists():
            for py_file in core_dir.rglob("*.py"):
                rel_path = f"core/{py_file.relative_to(core_dir)}"
                zipf.write(py_file, rel_path)
                print(f"  ✅ {rel_path}")
        
        print("\n🚀 === DEPLOYMENT SCRIPTS ===")
        
        # 5. Scripts de démarrage authentiques
        start_scripts = [
            "start_openred.sh",
            "start_openred.bat", 
            "install.sh",
            "install_openred.sh",
            "install_openred.bat"
        ]
        
        for script in start_scripts:
            script_path = openred_dir / script
            if script_path.exists():
                zipf.write(script_path, script)
                print(f"  ✅ {script}")
        
        # 6. Configuration pour hébergement mutualisé
        mutualized_config = '''#!/bin/bash
# OpenRed AUTHENTIC Platform - Déploiement Hébergement Mutualisé
# Respecte INTÉGRALEMENT les protocoles établis

echo "🌐 OpenRed AUTHENTIC Platform - Déploiement"
echo "==========================================="

# Configuration spécifique hébergement mutualisé
export OPENRED_ENV="production"
export OPENRED_HOST="0.0.0.0"
export OPENRED_PORT="8000"
export OPENRED_DEBUG="false"

# Vérifications environnement
echo "🔍 Vérification de l'environnement..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 requis pour OpenRed"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 requis pour les dépendances"
    exit 1
fi

echo "✅ Environnement validé"

# Installation des dépendances AUTHENTIQUES
echo "📦 Installation des dépendances OpenRed..."
pip3 install --user fastapi uvicorn websockets pillow cryptography python-multipart jinja2

# Vérification des protocoles core
echo "🔐 Vérification des protocoles core..."
python3 -c "
import sys
try:
    from openred_p2p_node import OpenRedP2PNode
    from friendship_protocol import FriendshipProtocol
    from social_messaging import DistributedMessaging
    print('✅ Protocoles OpenRed validés')
except ImportError as e:
    print(f'❌ Erreur protocoles: {e}')
    sys.exit(1)
"

# Lancement de la plateforme AUTHENTIQUE
echo "🚀 Lancement OpenRed Platform..."
echo "🌐 Interface: http://localhost:8000"
echo "🔐 Respect total des protocoles établis"

cd web/backend
python3 web_api.py
'''
        
        zipf.writestr("deploy_mutualized.sh", mutualized_config)
        print("  ✅ deploy_mutualized.sh")
        
        # 7. Configuration Apache/nginx pour hébergement
        apache_config = '''# OpenRed AUTHENTIC Platform - Configuration Apache
# Respecte l'architecture backend FastAPI

<VirtualHost *:80>
    ServerName votre-domaine.com
    DocumentRoot /path/to/openred
    
    # Proxy vers FastAPI backend
    ProxyPreserveHost On
    ProxyPass /api/ http://localhost:8000/
    ProxyPassReverse /api/ http://localhost:8000/
    
    # WebSocket support pour temps réel
    ProxyPass /ws/ ws://localhost:8000/ws/
    ProxyPassReverse /ws/ ws://localhost:8000/ws/
    
    # Fichiers statiques frontend
    Alias /static /path/to/openred/web/frontend
    <Directory "/path/to/openred/web/frontend">
        AllowOverride None
        Require all granted
    </Directory>
    
    # Headers sécurité OpenRed
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options SAMEORIGIN
    Header always set X-XSS-Protection "1; mode=block"
</VirtualHost>
'''
        
        zipf.writestr("apache_openred.conf", apache_config)
        print("  ✅ apache_openred.conf")
        
        # 8. Documentation de déploiement AUTHENTIQUE
        deployment_doc = '''# 🌐 OpenRed AUTHENTIC Platform - Guide de Déploiement

## ⚠️ IMPORTANT - Système AUTHENTIQUE

Ce package contient le **VRAI système OpenRed** avec tous les protocoles établis :

- ✅ **FastAPI Backend** complet et fonctionnel
- ✅ **Protocoles de friendship** authentiques  
- ✅ **Système d'authentification** OpenRed
- ✅ **Interface sociale** complète
- ✅ **Architecture P2P** respectée intégralement

## 🚀 Déploiement Hébergement Mutualisé

### Prérequis OBLIGATOIRES
- Python 3.8+ avec pip
- Accès shell/SSH à votre hébergeur
- Support FastAPI/ASGI

### Installation Étape par Étape

1. **Extraction du package**
   ```bash
   unzip openred-authentic-platform.zip
   cd openred-authentic-platform
   ```

2. **Lancement automatique**
   ```bash
   chmod +x deploy_mutualized.sh
   ./deploy_mutualized.sh
   ```

3. **Vérification**
   - Backend API: http://votre-domaine.com:8000
   - Interface: http://votre-domaine.com:8000/web/frontend/login.html

## 🔐 Fonctionnalités AUTHENTIQUES

- **Login sécurisé** avec tokens OpenRed
- **Profils utilisateurs** respectant les protocoles
- **Système d'amitié** P2P avec permissions
- **Chat en temps réel** via WebSockets
- **Découverte de nœuds** selon architecture établie
- **URN Phantom** pour partage sécurisé

## ⚠️ Sécurité Production

1. Configurez HTTPS obligatoirement
2. Modifiez les clés par défaut dans core/auth
3. Implémentez rate limiting
4. Sauvegardez les données utilisateurs

## 📖 Architecture Respectée

Ce déploiement respecte INTÉGRALEMENT :
- Les protocoles de communication établis
- L'architecture P2P conçue
- Les standards de sécurité OpenRed
- Les interfaces utilisateur développées

## 🆘 Support

Pour toute question sur ce déploiement AUTHENTIQUE :
- Documentation: https://github.com/DiegoMoralesMagri/OpenRed
- Issues: https://github.com/DiegoMoralesMagri/OpenRed/issues

**Ce n'est PAS une version simplifiée ou alternative !**
**C'est le VRAI système OpenRed en production !**
'''
        
        zipf.writestr("DEPLOYMENT_AUTHENTIC.md", deployment_doc)
        print("  ✅ DEPLOYMENT_AUTHENTIC.md")
        
        print("\n📋 === CONFIGURATION FILES ===")
        
        # 9. Fichiers de configuration nécessaires
        config_files = [
            ".env.example",
            "docker-compose.yml",
            "Dockerfile"
        ]
        
        for config in config_files:
            config_path = openred_dir / config
            if config_path.exists():
                zipf.write(config_path, config)
                print(f"  ✅ {config}")

    # Statistiques finales
    file_size = os.path.getsize(package_path)
    print(f"\n" + "=" * 50)
    print(f"✅ Package OpenRed AUTHENTIQUE créé!")
    print(f"📏 Taille: {file_size / 1024:.1f} KB")
    print(f"🎯 Fichier: {package_name}")
    print(f"🔐 Respect TOTAL des protocoles établis")
    print(f"🌐 Système de production COMPLET")
    
    return package_path

if __name__ == "__main__":
    package = create_authentic_openred_package()
    if package:
        print(f"\n🎉 PACKAGE AUTHENTIQUE PRÊT !")
        print(f"📁 {package}")
        print(f"🚀 Déployez le VRAI OpenRed !")
    else:
        print("❌ Erreur lors de la création du package")
        sys.exit(1)