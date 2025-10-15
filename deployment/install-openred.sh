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
    
    # URLs de téléchargement (avec fallback)
    DOWNLOAD_URLS=(
        "https://github.com/DiegoMoralesMagri/OpenRed/raw/main/deployment/openred-complete.zip"
        "https://github.com/DiegoMoralesMagri/OpenRed/releases/latest/download/openred-complete.zip"
        "https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/openred-complete.zip"
    )
    
    # Télécharger le package avec fallback
    DOWNLOAD_SUCCESS=false
    for url in "${DOWNLOAD_URLS[@]}"; do
        log "Tentative de téléchargement depuis: $url"
        if command -v curl &> /dev/null; then
            if curl -sL "$url" -o openred.zip && [[ -s openred.zip ]]; then
                DOWNLOAD_SUCCESS=true
                break
            fi
        elif command -v wget &> /dev/null; then
            if wget -q "$url" -O openred.zip && [[ -s openred.zip ]]; then
                DOWNLOAD_SUCCESS=true
                break
            fi
        fi
        log "Échec du téléchargement depuis $url"
    done
    
    if [[ "$DOWNLOAD_SUCCESS" != true ]]; then
        echo "❌ Impossible de télécharger OpenRed"
        echo "📋 Solutions alternatives:"
        echo "   1. Téléchargez manuellement: https://github.com/DiegoMoralesMagri/OpenRed/archive/main.zip"
        echo "   2. Clonez le repo: git clone https://github.com/DiegoMoralesMagri/OpenRed.git"
        exit 1
    fi
    
    # Vérifier l'intégrité du fichier ZIP
    if ! unzip -t openred.zip &>/dev/null; then
        echo "❌ Fichier ZIP corrompu"
        rm -f openred.zip
        exit 1
    fi
    
    success "Package téléchargé avec succès"
    
    # Extraire
    if command -v unzip &> /dev/null; then
        log "Extraction du package..."
        unzip -q openred.zip
        rm openred.zip
        success "Extraction terminée"
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