#!/bin/bash

# FR: Script d'installation OpenRed pour O2Switch
# EN: OpenRed installation script for O2Switch
# ES: Script de instalación de OpenRed para O2Switch
# ZH: O2Switch的OpenRed安装脚本

echo "🚀 Installation OpenRed sur O2Switch"
echo "===================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Vérification de l'environnement
log "Vérification de l'environnement..."

# Vérifier Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    log "Python trouvé: $PYTHON_VERSION"
else
    error "Python3 non trouvé. Veuillez l'installer via cPanel."
    exit 1
fi

# Vérifier pip
if command -v pip3 &> /dev/null; then
    log "pip3 trouvé"
else
    error "pip3 non trouvé. Installation de pip..."
    python3 -m ensurepip --default-pip
fi

# Créer les répertoires nécessaires
log "Création de la structure de répertoires..."
mkdir -p ~/openred_api
mkdir -p ~/openred_node
mkdir -p ~/logs
mkdir -p ~/openred_uploads

# Installation des dépendances Python
log "Installation des dépendances Python..."
cd ~/openred_api

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements-production.txt

# Configuration de la base de données
log "Configuration de la base de données..."
warning "Pensez à créer la base de données MySQL via cPanel:"
warning "1. Nom de la base: openred_db"
warning "2. Utilisateur: openred_user"
warning "3. Privilèges: TOUS sur openred_db"

# Copier le fichier de configuration
log "Configuration de l'environnement..."
cp .env.production.template .env.production
warning "Editez le fichier .env.production avec vos vraies valeurs"

# Migrations de base de données
log "Initialisation de la base de données..."
python -m alembic upgrade head

# Configuration des permissions
log "Configuration des permissions..."
chmod 755 ~/openred_api
chmod 644 ~/openred_api/.env.production
chmod 755 ~/logs
chmod 755 ~/openred_uploads

# Configuration du serveur web
log "Configuration du serveur web..."
cat > ~/openred_api/start.sh << 'EOF'
#!/bin/bash
cd ~/openred_api
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
EOF

chmod +x ~/openred_api/start.sh

# Instructions finales
echo ""
echo -e "${BLUE}📋 ÉTAPES SUIVANTES:${NC}"
echo "1. Editez ~/openred_api/.env.production avec vos vraies valeurs"
echo "2. Créez la base de données MySQL via cPanel"
echo "3. Configurez le sous-domaine api.o-red.org vers ~/openred_api"
echo "4. Lancez l'API avec: ~/openred_api/start.sh"
echo ""
echo -e "${GREEN}✅ Installation terminée!${NC}"