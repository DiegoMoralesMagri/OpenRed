#!/bin/bash
# 🌐 OpenRed - Installateur DEBUG pour Hébergement Mutualisé
# Version avec debugging étendu pour identifier les problèmes

set -e

echo "🌐 OpenRed - Installation Hébergement Mutualisé (DEBUG MODE)"
echo "============================================================"

# Configuration
PACKAGE_URL="https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/openred-shared-hosting.zip"
PACKAGE_FILE="openred-shared-hosting.zip"
INSTALL_DIR="."

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_debug() {
    echo -e "${YELLOW}[DEBUG]${NC} $1"
}

# Vérification de l'environnement avec debugging
check_environment() {
    print_status "Vérification de l'environnement..."
    print_debug "PWD: $(pwd)"
    print_debug "USER: $(whoami 2>/dev/null || echo 'unknown')"
    print_debug "HOME: $HOME"
    
    # Vérifier la commande de téléchargement
    print_debug "Test de curl..."
    if command -v curl >/dev/null 2>&1; then
        DOWNLOAD_CMD="curl -L -o"
        print_success "Curl disponible pour le téléchargement"
        print_debug "Curl version: $(curl --version | head -1)"
    else
        print_debug "Curl non trouvé, test de wget..."
        if command -v wget >/dev/null 2>&1; then
            DOWNLOAD_CMD="wget -O"
            print_success "Wget disponible pour le téléchargement"
            print_debug "Wget version: $(wget --version | head -1)"
        else
            print_error "Curl ou wget requis pour le téléchargement"
            print_debug "Commandes disponibles: $(which curl wget 2>/dev/null || echo 'aucune')"
            exit 1
        fi
    fi
    
    # Vérifier unzip
    print_debug "Test d'unzip..."
    if ! command -v unzip >/dev/null 2>&1; then
        print_error "Unzip requis pour l'extraction"
        print_debug "Commande unzip non trouvée dans PATH"
        exit 1
    else
        print_success "Unzip disponible"
        print_debug "Unzip version: $(unzip -v | head -1)"
    fi
    
    # Vérifier Python
    print_debug "Test de Python..."
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
        print_success "Python 3 détecté"
        print_debug "Python3 version: $(python3 --version)"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
        print_success "Python détecté"
        print_debug "Python version: $(python --version)"
    else
        print_warning "Python non détecté - Fonctionnalités limitées"
        print_debug "Aucune version de Python trouvée"
    fi
    
    # Vérifier les permissions d'écriture
    print_debug "Test des permissions d'écriture..."
    if touch test_write_permission 2>/dev/null; then
        rm -f test_write_permission
        print_success "Permissions d'écriture OK"
    else
        print_error "Pas de permissions d'écriture dans le répertoire courant"
        exit 1
    fi
    
    print_success "Environnement vérifié avec succès"
}

# Téléchargement du package avec debugging étendu
download_package() {
    print_status "Téléchargement du package OpenRed..."
    print_debug "URL: $PACKAGE_URL"
    print_debug "Fichier de destination: $PACKAGE_FILE"
    
    # URLs de fallback
    URLS=(
        "https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/openred-shared-hosting.zip"
        "https://github.com/DiegoMoralesMagri/OpenRed/raw/main/deployment/openred-shared-hosting.zip"
    )
    
    for url in "${URLS[@]}"; do
        print_status "Essai: $url"
        print_debug "Commande: $DOWNLOAD_CMD \"$PACKAGE_FILE\" \"$url\""
        
        if $DOWNLOAD_CMD "$PACKAGE_FILE" "$url" 2>/dev/null; then
            if [ -f "$PACKAGE_FILE" ] && [ -s "$PACKAGE_FILE" ]; then
                local file_size=$(stat -c%s "$PACKAGE_FILE" 2>/dev/null || wc -c < "$PACKAGE_FILE")
                print_success "Package téléchargé avec succès ($file_size bytes)"
                print_debug "Fichier: $(ls -la $PACKAGE_FILE)"
                return 0
            else
                print_debug "Fichier vide ou inexistant après téléchargement"
            fi
        else
            print_debug "Échec de la commande de téléchargement"
        fi
        print_warning "Échec du téléchargement depuis $url"
    done
    
    print_error "Impossible de télécharger le package"
    print_debug "Aucune URL n'a fonctionné"
    exit 1
}

# Installation simple et rapide
install_package() {
    print_status "Installation d'OpenRed..."
    print_debug "Extraction de $PACKAGE_FILE dans $INSTALL_DIR"
    
    # Extraction
    if unzip -q "$PACKAGE_FILE" -d "$INSTALL_DIR" 2>/dev/null; then
        print_success "Package extrait avec succès"
        print_debug "Contenu extrait:"
        find "$INSTALL_DIR" -name "*.php" -o -name "*.html" -o -name "*.js" | head -10 | while read file; do
            print_debug "  - $file"
        done
    else
        print_error "Erreur lors de l'extraction"
        exit 1
    fi
    
    # Nettoyage
    rm -f "$PACKAGE_FILE"
    print_debug "Fichier ZIP supprimé"
    
    print_success "Installation terminée"
}

# Test rapide
test_installation() {
    print_status "Test de l'installation..."
    
    if [ -f "index.php" ] || [ -f "index.html" ]; then
        print_success "Fichiers principaux détectés"
    else
        print_warning "Aucun fichier index détecté"
    fi
    
    # Afficher la structure installée
    print_debug "Structure installée:"
    ls -la | head -10 | while read line; do
        print_debug "  $line"
    done
}

# Affichage final
show_completion() {
    echo ""
    echo "🎉 Installation terminée !"
    echo "========================="
    echo ""
    echo "📁 Fichiers installés dans: $(pwd)"
    echo "🌐 Accès web: http://votre-domaine.com$(pwd | sed 's|'$HOME'||')"
    echo ""
    echo "📖 Pour plus d'informations:"
    echo "   https://github.com/DiegoMoralesMagri/OpenRed"
    echo ""
}

# Programme principal
main() {
    print_status "🚀 Démarrage de l'installation..."
    
    print_debug "Début check_environment"
    check_environment
    print_debug "Fin check_environment"
    
    print_debug "Début download_package"
    download_package
    print_debug "Fin download_package"
    
    print_debug "Début install_package"
    install_package
    print_debug "Fin install_package"
    
    print_debug "Début test_installation"
    test_installation
    print_debug "Fin test_installation"
    
    print_debug "Début show_completion"
    show_completion
    print_debug "Fin show_completion"
    
    echo ""
    print_success "OpenRed installé avec succès ! 🎉"
}

# Gestion des erreurs
cleanup_on_error() {
    print_error "Erreur lors de l'installation"
    print_debug "Nettoyage en cours..."
    if [ -f "$PACKAGE_FILE" ]; then
        rm -f "$PACKAGE_FILE"
        print_debug "Fichier $PACKAGE_FILE supprimé"
    fi
    exit 1
}

trap cleanup_on_error ERR

# Lancement
main "$@"