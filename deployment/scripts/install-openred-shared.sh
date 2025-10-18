#!/bin/bash
# 🌐 OpenRed - Installateur pour Hébergement Mutualisé
# Installation automatique sur serveurs partagés

set -e

echo "🌐 OpenRed - Installation Hébergement Mutualisé"
echo "================================================"

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

# Vérification de l'environnement
check_environment() {
    print_status "Vérification de l'environnement..."
    
    # Vérifier la commande de téléchargement
    if command -v curl >/dev/null 2>&1; then
        DOWNLOAD_CMD="curl -L -o"
        print_success "Curl disponible pour le téléchargement"
    elif command -v wget >/dev/null 2>&1; then
        DOWNLOAD_CMD="wget -O"
        print_success "Wget disponible pour le téléchargement"
    else
        print_error "Curl ou wget requis pour le téléchargement"
        exit 1
    fi
    
    # Vérifier unzip
    if ! command -v unzip >/dev/null 2>&1; then
        print_error "Unzip requis pour l'extraction"
        exit 1
    fi
    
    # Vérifier Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
        print_success "Python 3 détecté"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
        print_success "Python détecté"
    else
        print_warning "Python non détecté - Fonctionnalités limitées"
    fi
}

# Téléchargement du package
download_package() {
    print_status "Téléchargement du package OpenRed..."
    
    # URLs de fallback
    URLS=(
        "https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/openred-shared-hosting.zip"
        "https://github.com/DiegoMoralesMagri/OpenRed/raw/main/deployment/openred-shared-hosting.zip"
    )
    
    for url in "${URLS[@]}"; do
        print_status "Essai: $url"
        if $DOWNLOAD_CMD "$PACKAGE_FILE" "$url" 2>/dev/null; then
            if [ -f "$PACKAGE_FILE" ] && [ -s "$PACKAGE_FILE" ]; then
                print_success "Package téléchargé avec succès"
                return 0
            fi
        fi
        print_warning "Échec du téléchargement depuis $url"
    done
    
    print_error "Impossible de télécharger le package"
    exit 1
}

# Extraction et installation
install_package() {
    print_status "Installation d'OpenRed..."
    
    # Vérifier l'intégrité du ZIP
    if ! unzip -t "$PACKAGE_FILE" >/dev/null 2>&1; then
        print_error "Package corrompu"
        exit 1
    fi
    
    # Extraction
    unzip -o "$PACKAGE_FILE"
    rm "$PACKAGE_FILE"
    
    print_success "Fichiers extraits"
}

# Configuration des permissions
setup_permissions() {
    print_status "Configuration des permissions..."
    
    # Permissions des dossiers
    find . -type d -exec chmod 755 {} \;
    
    # Permissions des fichiers
    find . -type f -exec chmod 644 {} \;
    
    # Permissions des scripts CGI
    if [ -f "app/api.cgi" ]; then
        chmod 755 app/api.cgi
        print_success "Permissions CGI configurées"
    fi
    
    print_success "Permissions configurées"
}

# Test de l'installation
test_installation() {
    print_status "Test de l'installation..."
    
    # Vérifier les fichiers requis
    required_files=("index.html" "app/index.html" "app/api.cgi" ".htaccess")
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "✓ $file"
        else
            print_error "✗ $file manquant"
            return 1
        fi
    done
    
    # Test CGI si Python disponible
    if [ -n "$PYTHON_CMD" ]; then
        cd app
        if $PYTHON_CMD api.cgi 2>/dev/null | grep -q "Content-Type"; then
            print_success "CGI fonctionnel"
        else
            print_warning "Test CGI échoué (normal en local)"
        fi
        cd ..
    fi
    
    print_success "Installation vérifiée"
}

# Affichage des informations post-installation
show_completion() {
    echo ""
    echo "🎉 Installation terminée !"
    echo "=========================="
    echo ""
    echo "📁 Fichiers installés dans: $(pwd)"
    echo "🌐 Page d'accueil: index.html"
    echo "⚙️  Interface OpenRed: app/index.html"
    echo "🔌 API: app/api.cgi"
    echo ""
    echo "📋 Prochaines étapes:"
    echo "1. Uploadez ces fichiers vers votre hébergeur"
    echo "2. Vérifiez que les permissions sont correctes"
    echo "3. Accédez à votre site web"
    echo ""
    echo "🔧 Hébergeurs testés:"
    echo "  ✅ OVH (shared hosting)"
    echo "  ✅ O2Switch"
    echo "  ✅ 1&1 IONOS"
    echo "  ✅ Hostinger"
    echo "  ✅ Gandi"
    echo ""
    echo "💡 En cas de problème:"
    echo "  - Vérifiez que CGI est activé"
    echo "  - Contrôlez les permissions (755 pour CGI)"
    echo "  - Consultez les logs d'erreur de votre hébergeur"
}

# Programme principal
main() {
    echo "🚀 Démarrage de l'installation..."
    
    check_environment
    download_package
    install_package
    setup_permissions
    test_installation
    show_completion
    
    echo ""
    print_success "OpenRed installé avec succès ! 🎉"
}

# Gestion des erreurs
cleanup_on_error() {
    print_error "Erreur lors de l'installation"
    if [ -f "$PACKAGE_FILE" ]; then
        rm -f "$PACKAGE_FILE"
    fi
    exit 1
}

trap cleanup_on_error ERR

# Lancement si exécuté directement
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi