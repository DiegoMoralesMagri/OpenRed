#!/bin/bash

# OpenRed P2P Platform - Démarrage Rapide
# Compatible Linux/macOS

echo "🌐 Démarrage OpenRed P2P Platform..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trouvé. Installez Python 3.8+ d'abord."
    exit 1
fi

# Aller dans le répertoire du script
cd "$(dirname "$0")"

# Vérifier l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "🔧 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔌 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances si nécessaire
if [ ! -f "venv/installed" ]; then
    echo "📦 Installation des dépendances..."
    pip install fastapi uvicorn websockets pillow cryptography
    touch venv/installed
fi

# Définir les variables d'environnement par défaut
export OPENRED_WEB_PORT=${OPENRED_WEB_PORT:-8000}
export OPENRED_P2P_PORT=${OPENRED_P2P_PORT:-8080}
export OPENRED_DATA_DIR=${OPENRED_DATA_DIR:-./user_data}
export OPENRED_SPIDER_ENABLED=${OPENRED_SPIDER_ENABLED:-true}

# Créer le répertoire de données si nécessaire
mkdir -p "$OPENRED_DATA_DIR"

echo "🚀 Démarrage du serveur OpenRed..."
echo "📱 Interface web : http://localhost:$OPENRED_WEB_PORT"
echo "🔗 Port P2P : $OPENRED_P2P_PORT"
echo "💾 Données : $OPENRED_DATA_DIR"
echo "🕷️ Spider Internet : $OPENRED_SPIDER_ENABLED"
echo ""
echo "👆 Appuyez sur Ctrl+C pour arrêter"
echo "================================================"

# Démarrer le serveur
python web/backend/web_api.py