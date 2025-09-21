#!/bin/bash

# FR: Script d'installation OpenRed pour O2Switch (Version améliorée)
# EN: OpenRed installation script for O2Switch (Enhanced version)
# ES: Script de instalación de OpenRed para O2Switch (Versión mejorada)
# ZH: O2Switch的OpenRed安装脚本（增强版）

echo "🚀 Installation OpenRed sur O2Switch v2.0"
echo "=========================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonction de log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Variables globales
PROJECT_HOME="${HOME}/openred_api"
LOG_DIR="${HOME}/logs"
UPLOAD_DIR="${HOME}/openred_uploads"
BACKUP_DIR="${HOME}/openred_backup"
VENV_DIR="${PROJECT_HOME}/venv"

# Configuration utilisateur
USERNAME=$(whoami)
CURRENT_DATE=$(date +%Y%m%d_%H%M%S)

# Fonctions utilitaires
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        success "$1 trouvé: $(which $1)"
        return 0
    else
        error "$1 non trouvé"
        return 1
    fi
}

create_backup() {
    if [ -d "$PROJECT_HOME" ]; then
        warning "Installation existante détectée"
        info "Création d'une sauvegarde..."
        mkdir -p "$BACKUP_DIR"
        cp -r "$PROJECT_HOME" "$BACKUP_DIR/openred_api_backup_$CURRENT_DATE"
        success "Sauvegarde créée: $BACKUP_DIR/openred_api_backup_$CURRENT_DATE"
    fi
}

# Vérification de l'environnement
log "Vérification de l'environnement O2Switch..."

# Informations système
info "Système: $(uname -a)"
info "Utilisateur: $USERNAME"
info "Répertoire home: $HOME"

# Vérifier Python
if check_command python3; then
    PYTHON_VERSION=$(python3 --version)
    log "Python trouvé: $PYTHON_VERSION"
    
    # Vérifier la version minimale (3.8+)
    PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [ "$(echo "$PYTHON_VER >= 3.8" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
        success "Version Python compatible ($PYTHON_VER)"
    else
        warning "Version Python ancienne ($PYTHON_VER), recommandé 3.8+"
    fi
else
    error "Python3 non trouvé. Contactez le support O2Switch."
    exit 1
fi

# Vérifier pip
if check_command pip3; then
    PIP_VERSION=$(pip3 --version)
    log "pip trouvé: $PIP_VERSION"
else
    warning "pip3 non trouvé. Tentative d'installation..."
    python3 -m ensurepip --default-pip 2>/dev/null || {
        error "Impossible d'installer pip. Contactez le support O2Switch."
        exit 1
    }
    success "pip installé avec succès"
fi

# Vérifier l'espace disque
DISK_SPACE=$(df -h "$HOME" | awk 'NR==2 {print $4}')
info "Espace disque disponible: $DISK_SPACE"

# Sauvegarde de l'installation existante
create_backup

# Créer les répertoires nécessaires
log "Création de la structure de répertoires..."
mkdir -p "$PROJECT_HOME"
mkdir -p "$LOG_DIR"
mkdir -p "$UPLOAD_DIR"
mkdir -p "$BACKUP_DIR"

# Configuration des permissions
chmod 755 "$PROJECT_HOME"
chmod 755 "$LOG_DIR"
chmod 755 "$UPLOAD_DIR"
chmod 755 "$BACKUP_DIR"

success "Structure de répertoires créée"

# Installation des dépendances Python
log "Configuration de l'environnement virtuel Python..."
cd "$PROJECT_HOME"

# Supprimer l'ancien environnement virtuel s'il existe
if [ -d "$VENV_DIR" ]; then
    warning "Suppression de l'ancien environnement virtuel..."
    rm -rf "$VENV_DIR"
fi

# Créer un nouvel environnement virtuel
python3 -m venv "$VENV_DIR" || {
    error "Échec de la création de l'environnement virtuel"
    exit 1
}

# Activer l'environnement virtuel
source "$VENV_DIR/bin/activate" || {
    error "Échec de l'activation de l'environnement virtuel"
    exit 1
}

success "Environnement virtuel créé et activé"

# Mettre à jour pip dans l'environnement virtuel
log "Mise à jour de pip..."
pip install --upgrade pip --quiet

# Installation par étapes avec gestion d'erreurs
log "Installation des dépendances minimales..."
if pip install -r requirements-minimal.txt --quiet; then
    success "Dépendances minimales installées avec succès"
    
    # Tenter l'installation des dépendances complètes
    log "Installation des dépendances complètes..."
    if pip install -r requirements-production.txt --quiet; then
        success "Toutes les dépendances installées avec succès"
        INSTALL_STATUS="complete"
    else
        warning "Certaines dépendances optionnelles ont échoué"
        warning "L'API fonctionnera en mode minimal"
        INSTALL_STATUS="minimal"
    fi
else
    error "Échec de l'installation des dépendances minimales"
    error "Tentative avec des dépendances de base uniquement..."
    
    # Installation de secours avec uniquement les modules essentiels
    if pip install fastapi uvicorn pydantic python-dotenv --quiet; then
        warning "Installation de secours réussie (mode de base)"
        INSTALL_STATUS="basic"
    else
        error "Échec total de l'installation des dépendances"
        exit 1
    fi
fi

# Test de l'installation
log "Test de l'installation des modules..."
python3 -c "
import fastapi, uvicorn, pydantic
print('✅ Modules principaux importés avec succès')
print(f'FastAPI: {fastapi.__version__}')
print(f'Uvicorn: {uvicorn.__version__}')
print(f'Pydantic: {pydantic.__version__}')
" || {
    error "Test d'importation échoué"
    exit 1
}

success "Test d'importation réussi"

# Configuration de la base de données
log "Configuration de la base de données..."
echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║               CONFIGURATION BASE DE DONNÉES           ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
warning "Vous devez créer la base de données MySQL via cPanel:"
warning "1. Connectez-vous à cPanel"
warning "2. Allez dans 'Bases de données MySQL'"
warning "3. Créez une base de données nommée: 'openred_db'"
warning "4. Créez un utilisateur: 'openred_user'"
warning "5. Assignez TOUS les privilèges à l'utilisateur sur la base"
warning "6. Notez le nom complet de la base et de l'utilisateur (avec préfixe)"
echo ""

# Configuration de l'environnement
log "Configuration de l'environnement..."

# Choisir le bon template selon le mode d'installation
if [ -f ".env.o2switch.template" ]; then
    TEMPLATE_FILE=".env.o2switch.template"
    info "Utilisation du template O2Switch optimisé"
else
    TEMPLATE_FILE=".env.production.template"
    info "Utilisation du template de production standard"
fi

if [ -f "$TEMPLATE_FILE" ]; then
    cp "$TEMPLATE_FILE" .env.production
    success "Fichier de configuration créé: .env.production"
    
    # Remplacer les variables automatiquement détectables
    sed -i "s|YOUR_USERNAME|$USERNAME|g" .env.production
    sed -i "s|/home/YOUR_USERNAME|$HOME|g" .env.production
    
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    CONFIGURATION                      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    warning "IMPORTANT: Éditez le fichier .env.production avec vos vraies valeurs:"
    warning "nano $PROJECT_HOME/.env.production"
    echo ""
    warning "Variables à modifier obligatoirement:"
    echo "  - DATABASE_URL: Remplacez par vos vraies informations MySQL"
    echo "  - SECRET_KEY: Générez une clé secrète forte"
    echo "  - DOMAIN: Votre vrai nom de domaine"
    echo "  - API_DOMAIN: Votre sous-domaine API"
else
    error "Template de configuration non trouvé"
    exit 1
fi

# Création des scripts de gestion
log "Création des scripts de gestion..."

# Script de démarrage
cat > "$PROJECT_HOME/start.sh" << 'EOF'
#!/bin/bash
# Script de démarrage OpenRed pour O2Switch

cd "$(dirname "$0")"
source venv/bin/activate

# Charger les variables d'environnement
if [ -f .env.production ]; then
    export $(grep -v '^#' .env.production | xargs)
fi

echo "🚀 Démarrage OpenRed API..."
echo "📍 Mode: ${ENVIRONMENT:-production}"
echo "🌐 Host: ${HOST:-0.0.0.0}:${PORT:-8000}"

# Utiliser la version O2Switch si disponible, sinon la version simple
if [ -f "app/main_o2switch.py" ]; then
    echo "📱 Version: O2Switch optimisée"
    uvicorn app.main_o2switch:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --workers 1
elif [ -f "app/main_simple.py" ]; then
    echo "📱 Version: Simple"
    uvicorn app.main_simple:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --workers 1
else
    echo "❌ Aucun fichier principal trouvé"
    exit 1
fi
EOF

# Script de test
cat > "$PROJECT_HOME/test.sh" << 'EOF'
#!/bin/bash
# Script de test OpenRed pour O2Switch

cd "$(dirname "$0")"
source venv/bin/activate

echo "🧪 Test de l'installation OpenRed..."

# Test des modules
echo "📦 Test des modules Python..."
python3 -c "
try:
    import fastapi, uvicorn, pydantic
    print('✅ Modules principaux: OK')
    import sys
    print(f'✅ Python: {sys.version}')
    import fastapi
    print(f'✅ FastAPI: {fastapi.__version__}')
except ImportError as e:
    print(f'❌ Erreur d\'import: {e}')
    exit(1)
"

# Test de l'application
echo "🚀 Test de l'application..."
if [ -f "app/main_o2switch.py" ]; then
    python3 -c "from app.main_o2switch import app; print('✅ Application O2Switch: OK')" || echo "❌ Application O2Switch: ERREUR"
elif [ -f "app/main_simple.py" ]; then
    python3 -c "from app.main_simple import app; print('✅ Application simple: OK')" || echo "❌ Application simple: ERREUR"
fi

# Test de diagnostic
echo "🔍 Diagnostic système..."
if [ -f "diagnostic.py" ]; then
    python3 diagnostic.py | head -20
fi

echo "✅ Tests terminés"
EOF

# Script de diagnostic
cat > "$PROJECT_HOME/diagnostic_o2switch.sh" << 'EOF'
#!/bin/bash
# Script de diagnostic complet pour O2Switch

cd "$(dirname "$0")"

echo "🔍 Diagnostic OpenRed O2Switch"
echo "=============================="

# Informations système
echo "📍 Système:"
echo "  - Utilisateur: $(whoami)"
echo "  - Répertoire: $(pwd)"
echo "  - Python: $(python3 --version 2>/dev/null || echo 'Non trouvé')"
echo "  - Espace disque: $(df -h . | tail -1 | awk '{print $4}')"

# Structure des fichiers
echo ""
echo "📁 Structure des fichiers:"
ls -la

# Environnement virtuel
echo ""
echo "🐍 Environnement virtuel:"
if [ -d "venv" ]; then
    echo "  ✅ Environnement virtuel: Trouvé"
    source venv/bin/activate
    echo "  📦 Packages installés:"
    pip list | grep -E "(fastapi|uvicorn|pydantic)"
else
    echo "  ❌ Environnement virtuel: Non trouvé"
fi

# Configuration
echo ""
echo "⚙️  Configuration:"
if [ -f ".env.production" ]; then
    echo "  ✅ Fichier de configuration: Trouvé"
    echo "  📝 Variables importantes:"
    grep -E "(DATABASE_URL|SECRET_KEY|DOMAIN)" .env.production | sed 's/=.*PASSWORD.*/=***HIDDEN***/' | head -5
else
    echo "  ❌ Fichier de configuration: Non trouvé"
fi

# Test d'application
echo ""
echo "🧪 Test d'application:"
if source venv/bin/activate && python3 -c "from app.main_o2switch import app; print('✅ Application O2Switch: OK')" 2>/dev/null; then
    echo "  ✅ Application principale: OK"
elif source venv/bin/activate && python3 -c "from app.main_simple import app; print('✅ Application simple: OK')" 2>/dev/null; then
    echo "  ✅ Application simple: OK"
else
    echo "  ❌ Application: ERREUR"
fi

echo ""
echo "📋 Diagnostic terminé"
EOF

# Rendre les scripts exécutables
chmod +x "$PROJECT_HOME/start.sh"
chmod +x "$PROJECT_HOME/test.sh"
chmod +x "$PROJECT_HOME/diagnostic_o2switch.sh"

success "Scripts de gestion créés"

# Configuration des permissions finales
log "Configuration des permissions finales..."
chmod 755 "$PROJECT_HOME"
chmod 644 "$PROJECT_HOME/.env.production" 2>/dev/null
chmod 755 "$LOG_DIR"
chmod 755 "$UPLOAD_DIR"
find "$PROJECT_HOME/app" -name "*.py" -exec chmod 644 {} \; 2>/dev/null

# Test final de l'installation
log "Test final de l'installation..."
cd "$PROJECT_HOME"
source "$VENV_DIR/bin/activate"

if python3 "$PROJECT_HOME/test.sh" >/dev/null 2>&1; then
    success "Test final réussi"
else
    warning "Test final échoué, mais l'installation peut fonctionner"
fi

# Instructions finales
echo ""
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                      INSTALLATION TERMINÉE                  ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📋 ÉTAPES SUIVANTES OBLIGATOIRES:${NC}"
echo ""
echo -e "${YELLOW}1. Configuration de la base de données:${NC}"
echo "   • Connectez-vous à cPanel"
echo "   • Allez dans 'Bases de données MySQL'"
echo "   • Créez: base 'openred_db', utilisateur 'openred_user'"
echo "   • Assignez tous les privilèges"
echo ""
echo -e "${YELLOW}2. Configuration de l'environnement:${NC}"
echo "   • Éditez: $PROJECT_HOME/.env.production"
echo "   • Modifiez DATABASE_URL avec vos vraies informations"
echo "   • Générez une SECRET_KEY forte"
echo "   • Configurez votre DOMAIN"
echo ""
echo -e "${YELLOW}3. Configuration du sous-domaine:${NC}"
echo "   • Dans cPanel > Sous-domaines"
echo "   • Créez 'api.votre-domaine.com' → $PROJECT_HOME"
echo ""
echo -e "${YELLOW}4. Configuration de l'application Python (cPanel):${NC}"
echo "   • Version Python: 3.8+"
echo "   • Domaine: api.votre-domaine.com"
echo "   • Répertoire: openred_api"
if [ "$INSTALL_STATUS" = "complete" ]; then
    echo "   • Point d'entrée: app/main_o2switch.py"
    echo "   • Variable PYTHONPATH: $PROJECT_HOME"
else
    echo "   • Point d'entrée: app/main_simple.py (mode minimal)"
fi
echo ""
echo -e "${CYAN}🔧 COMMANDES UTILES:${NC}"
echo "   • Test de l'installation: $PROJECT_HOME/test.sh"
echo "   • Diagnostic complet: $PROJECT_HOME/diagnostic_o2switch.sh"
echo "   • Démarrage manuel: $PROJECT_HOME/start.sh"
echo ""
echo -e "${CYAN}🌐 URLS DE TEST:${NC}"
echo "   • Health check: https://api.votre-domaine.com/health"
echo "   • Diagnostic: https://api.votre-domaine.com/diagnostic"
if [ "$INSTALL_STATUS" = "complete" ]; then
    echo "   • Documentation: https://api.votre-domaine.com/docs"
fi
echo "   • API nœuds: https://api.votre-domaine.com/api/v1/nodes"
echo ""
echo -e "${GREEN}✅ Installation OpenRed terminée avec succès!${NC}"
echo -e "${BLUE}📊 Statut d'installation: $INSTALL_STATUS${NC}"

if [ "$INSTALL_STATUS" = "basic" ]; then
    echo ""
    warning "Installation en mode de base détectée"
    warning "Certaines fonctionnalités avancées peuvent ne pas être disponibles"
    warning "Pour une installation complète, contactez le support O2Switch"
fi

echo ""
echo -e "${PURPLE}💡 Support et documentation:${NC}"
echo "   • Documentation: https://github.com/DiegoMoralesMagri/OpenRed"
echo "   • Support O2Switch: Via votre espace client"
echo "   • Issues: https://github.com/DiegoMoralesMagri/OpenRed/issues"