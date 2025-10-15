#!/bin/bash
# 🚀 OpenRed One-Liner Installer for Linux/macOS
# Usage: curl -sSL https://install.openred.dev | bash

set -e

echo "🚀 OpenRed One-Liner Installer"
echo "=============================="

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# Détection de l'environnement
detect_hosting() {
    if [[ -d "$HOME/public_html" ]]; then
        HOSTING_TYPE="shared"
        WEB_ROOT="$HOME/public_html"
        success "Hébergement partagé détecté"
    elif [[ -d "/var/www/html" ]] && [[ -w "/var/www/html" ]]; then
        HOSTING_TYPE="vps"
        WEB_ROOT="/var/www/html"
        success "VPS détecté"
    elif [[ -d "$HOME/www" ]]; then
        HOSTING_TYPE="ovh"
        WEB_ROOT="$HOME/www"
        success "OVH détecté"
    else
        HOSTING_TYPE="local"
        WEB_ROOT="$HOME/openred"
        log "Installation locale"
    fi
    
    INSTALL_DIR="$WEB_ROOT/openred"
}

# Installation
install_openred() {
    log "Installation dans $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Télécharger le package
    if command -v curl &> /dev/null; then
        curl -sL "https://github.com/DiegoMoralesMagri/OpenRed/releases/latest/download/openred-complete.zip" -o openred.zip
    elif command -v wget &> /dev/null; then
        wget -q "https://github.com/DiegoMoralesMagri/OpenRed/releases/latest/download/openred-complete.zip" -O openred.zip
    else
        echo "❌ curl ou wget requis"
        exit 1
    fi
    
    # Extraire
    if command -v unzip &> /dev/null; then
        unzip -q openred.zip
        rm openred.zip
    else
        echo "❌ unzip requis"
        exit 1
    fi
    
    # Configuration
    if [[ "$HOSTING_TYPE" != "vps" ]]; then
        chmod +x *.py 2>/dev/null || true
    fi
    
    success "OpenRed installé !"
}

# Démarrage
start_server() {
    if [[ "$HOSTING_TYPE" == "local" ]]; then
        if command -v python3 &> /dev/null; then
            log "Démarrage du serveur..."
            nohup python3 app.py > openred.log 2>&1 &
            success "Serveur démarré sur http://localhost:8000"
        fi
    fi
}

# Résultats
show_results() {
    echo ""
    success "🎉 Installation terminée !"
    case $HOSTING_TYPE in
        "local")
            echo "🌐 Accès: http://localhost:8000"
            ;;
        *)
            echo "🌐 Accès: http://votre-domaine.com/openred"
            ;;
    esac
}

# Exécution
detect_hosting
install_openred
start_server
show_results