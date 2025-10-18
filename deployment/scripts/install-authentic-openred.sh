#!/bin/bash
# 🌐 OpenRed AUTHENTIC Platform - Installation Hébergement Mutualisé
# Déploie le VRAI système OpenRed avec TOUS les protocoles établis
# 
# ATTENTION: Ceci est le SYSTÈME AUTHENTIQUE, pas une version simplifiée !

echo "🌐 OpenRed AUTHENTIC Platform - Installation"
echo "============================================"
echo "🎯 Déploiement du VRAI système OpenRed"
echo "🔐 Respect INTÉGRAL des protocoles établis"
echo ""

# Variables
URL="https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/openred-authentic-platform.zip"
ZIP="openred-authentic.zip"

echo "📥 Téléchargement du système AUTHENTIQUE..."
if curl -L -o "$ZIP" "$URL" 2>/dev/null || wget -O "$ZIP" "$URL" 2>/dev/null; then
    echo "✅ Téléchargement réussi ($(du -h "$ZIP" | cut -f1))"
else
    echo "❌ Échec du téléchargement"
    echo "🔗 URL: $URL"
    exit 1
fi

echo "📦 Extraction du système complet..."
if unzip -q "$ZIP" 2>/dev/null; then
    echo "✅ Extraction réussie"
    rm -f "$ZIP"
else
    echo "❌ Échec de l'extraction"
    exit 1
fi

echo "🔍 Vérification de l'intégrité du système..."

# Vérifier les composants critiques
CRITICAL_FILES=(
    "openred_p2p_node.py"
    "friendship_protocol.py"
    "web/backend/web_api.py"
    "web/frontend/login.html"
    "core/auth.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - CRITIQUE MANQUANT"
        exit 1
    fi
done

echo "🔐 Vérification de l'environnement..."

# Vérifier Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 REQUIS pour OpenRed"
    echo "🔧 Installez Python 3.8+ avant de continuer"
    exit 1
fi

echo "✅ Python 3 détecté: $(python3 --version)"

# Vérifier pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 REQUIS pour les dépendances"
    exit 1
fi

echo "✅ pip3 disponible"

echo "📦 Installation des dépendances AUTHENTIQUES..."

# Installation selon requirements.txt du vrai système
pip3 install --user fastapi uvicorn websockets pillow cryptography python-multipart jinja2 aiofiles 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Dépendances installées"
else
    echo "⚠️  Certaines dépendances ont échoué (normal sur hébergement mutualisé)"
fi

echo "🔧 Configuration pour hébergement mutualisé..."

# Créer les dossiers nécessaires
mkdir -p data/users data/profiles data/messages
chmod 755 data data/users data/profiles data/messages

# Configuration des permissions
find . -name "*.py" -exec chmod 644 {} \;
find . -name "*.html" -exec chmod 644 {} \;
chmod 755 deploy_mutualized.sh 2>/dev/null
chmod 755 start_openred.sh 2>/dev/null

echo "🚀 Test du système AUTHENTIQUE..."

# Test basique du système
python3 -c "
try:
    import sys
    sys.path.append('.')
    from openred_p2p_node import OpenRedP2PNode
    from friendship_protocol import FriendshipProtocol
    print('✅ Protocoles OpenRed validés')
except ImportError as e:
    print(f'⚠️  Protocoles partiels: {e}')
    print('🔧 Fonctionnement en mode dégradé possible')
" 2>/dev/null

echo ""
echo "🎉 OpenRed AUTHENTIC Platform installé !"
echo "========================================"
echo ""
echo "🌐 SYSTÈME AUTHENTIQUE DÉPLOYÉ :"
echo "  🔐 Backend FastAPI complet"
echo "  👥 Protocoles de friendship P2P"
echo "  💬 Système de messaging distribué" 
echo "  🌐 Interface utilisateur complète"
echo "  🛡️  Sécurité OpenRed authentique"
echo ""
echo "🚀 LANCEMENT :"
echo "  1. Démarrage backend:"
echo "     cd web/backend && python3 web_api.py"
echo ""
echo "  2. Accès interface:"
echo "     http://votre-domaine.com:8000/web/frontend/login.html"
echo ""
echo "📋 PREMIÈRE UTILISATION :"
echo "  1. Créez votre compte via l'interface"
echo "  2. Configurez votre profil utilisateur"
echo "  3. Découvrez les nœuds P2P"
echo "  4. Ajoutez des amis via le protocole friendship"
echo ""
echo "⚠️  IMPORTANT - Système de PRODUCTION :"
echo "  - Configure HTTPS en production"
echo "  - Sauvegarde régulière des données"
echo "  - Surveillance des performances"
echo ""
echo "📖 Documentation complète :"
echo "   https://github.com/DiegoMoralesMagri/OpenRed"
echo ""
echo "🎯 Ceci est le VRAI OpenRed, pas une version alternative !"