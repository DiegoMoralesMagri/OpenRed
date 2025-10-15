#!/bin/bash
# === Script de démarrage Web Interface ===
# Lance l'interface web OpenRed P2P Platform

echo "🌐 Starting OpenRed P2P Web Interface..."

# Variables d'environnement par défaut
export OPENRED_NODE_ID=${OPENRED_NODE_ID:-"web_node_$(date +%s)"}
export OPENRED_SECTOR=${OPENRED_SECTOR:-"general"}
export OPENRED_P2P_PORT=${OPENRED_P2P_PORT:-"8080"}
export OPENRED_WEB_PORT=${OPENRED_WEB_PORT:-"8000"}

echo "📡 Node ID: $OPENRED_NODE_ID"
echo "🎯 Sector: $OPENRED_SECTOR"
echo "🔗 P2P Port: $OPENRED_P2P_PORT"
echo "🌐 Web Port: $OPENRED_WEB_PORT"

# Installation des dépendances si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt

echo "🚀 Starting FastAPI web server..."
python web_api.py