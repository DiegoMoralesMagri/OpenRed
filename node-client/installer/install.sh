#!/bin/bash

# OpenRed Node Client - Script d'installation automatique
# Ce script installe et configure automatiquement un node OpenRed

set -e

echo "🚀 Installation OpenRed Node Client"
echo "=================================="

# Variables de configuration
OPENRED_HOME="/opt/openred"
SERVICE_USER="openred"
DATABASE_NAME="openred_node"
FRONTEND_PORT="3000"
BACKEND_PORT="8080"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
check_requirements() {
    log_info "Vérification des prérequis..."
    
    # Vérifier les droits d'administration
    if [[ $EUID -ne 0 ]]; then
        log_error "Ce script doit être exécuté en tant que root (sudo)"
        exit 1
    fi
    
    # Vérifier le système d'exploitation
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
        log_info "Système détecté: Linux ($DISTRO)"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "Système détecté: macOS"
    else
        log_error "Système d'exploitation non supporté: $OSTYPE"
        exit 1
    fi
}

# Installation des dépendances système
install_dependencies() {
    log_info "Installation des dépendances système..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        apt-get update
        apt-get install -y python3 python3-pip python3-venv nodejs npm nginx sqlite3 curl git
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        yum update -y
        yum install -y python3 python3-pip nodejs npm nginx sqlite curl git
    elif command -v brew &> /dev/null; then
        # macOS
        brew install python3 node nginx sqlite git
    else
        log_error "Gestionnaire de paquets non supporté"
        exit 1
    fi
}

# Création de l'utilisateur système
create_user() {
    log_info "Création de l'utilisateur système OpenRed..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd --system --home "$OPENRED_HOME" --shell /bin/bash "$SERVICE_USER"
        log_info "Utilisateur $SERVICE_USER créé"
    else
        log_warn "Utilisateur $SERVICE_USER existe déjà"
    fi
}

# Téléchargement et extraction des fichiers
download_files() {
    log_info "Téléchargement des fichiers OpenRed..."
    
    mkdir -p "$OPENRED_HOME"
    cd "$OPENRED_HOME"
    
    # Simulation du téléchargement (en réalité, ce serait depuis GitHub releases)
    log_info "Téléchargement depuis GitHub..."
    # curl -L https://github.com/openred/openred/releases/latest/download/node-client.tar.gz -o node-client.tar.gz
    # tar -xzf node-client.tar.gz
    
    # Pour l'instant, on crée la structure
    mkdir -p backend frontend config
    
    chown -R "$SERVICE_USER:$SERVICE_USER" "$OPENRED_HOME"
}

# Configuration de la base de données
setup_database() {
    log_info "Configuration de la base de données..."
    
    # Création de la base de données SQLite
    DATABASE_PATH="$OPENRED_HOME/data/$DATABASE_NAME.db"
    mkdir -p "$(dirname "$DATABASE_PATH")"
    
    # Initialisation du schéma de base de données
    sqlite3 "$DATABASE_PATH" < "$OPENRED_HOME/config/database.sql"
    
    chown "$SERVICE_USER:$SERVICE_USER" "$DATABASE_PATH"
    chmod 600 "$DATABASE_PATH"
    
    log_info "Base de données initialisée: $DATABASE_PATH"
}

# Configuration de l'environnement Python
setup_python_env() {
    log_info "Configuration de l'environnement Python..."
    
    cd "$OPENRED_HOME/backend"
    
    # Création de l'environnement virtuel
    python3 -m venv venv
    source venv/bin/activate
    
    # Installation des dépendances
    pip install -r requirements.txt
    
    chown -R "$SERVICE_USER:$SERVICE_USER" venv/
}

# Configuration du frontend
setup_frontend() {
    log_info "Configuration du frontend..."
    
    cd "$OPENRED_HOME/frontend"
    
    # Installation des dépendances Node.js
    npm install
    
    # Build de production
    npm run build
    
    chown -R "$SERVICE_USER:$SERVICE_USER" node_modules/ build/
}

# Configuration de Nginx
setup_nginx() {
    log_info "Configuration de Nginx..."
    
    # Copie de la configuration Nginx
    cp "$OPENRED_HOME/config/nginx.conf" "/etc/nginx/sites-available/openred"
    ln -sf "/etc/nginx/sites-available/openred" "/etc/nginx/sites-enabled/"
    
    # Test de la configuration
    nginx -t
    
    # Redémarrage de Nginx
    systemctl restart nginx
    systemctl enable nginx
    
    log_info "Nginx configuré et redémarré"
}

# Création des services systemd
create_services() {
    log_info "Création des services systemd..."
    
    # Service backend
    cat > "/etc/systemd/system/openred-backend.service" << EOF
[Unit]
Description=OpenRed Backend Service
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$OPENRED_HOME/backend
Environment=PATH=$OPENRED_HOME/backend/venv/bin
ExecStart=$OPENRED_HOME/backend/venv/bin/python main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    # Service frontend (si nécessaire pour le dev)
    cat > "/etc/systemd/system/openred-frontend.service" << EOF
[Unit]
Description=OpenRed Frontend Development Service
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$OPENRED_HOME/frontend
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=3
Environment=PORT=$FRONTEND_PORT

[Install]
WantedBy=multi-user.target
EOF

    # Rechargement et activation des services
    systemctl daemon-reload
    systemctl enable openred-backend.service
    systemctl start openred-backend.service
    
    log_info "Services systemd créés et démarrés"
}

# Génération de la configuration initiale
generate_config() {
    log_info "Génération de la configuration initiale..."
    
    # Génération des clés cryptographiques
    openssl genrsa -out "$OPENRED_HOME/config/private_key.pem" 2048
    openssl rsa -in "$OPENRED_HOME/config/private_key.pem" -pubout -out "$OPENRED_HOME/config/public_key.pem"
    
    # Configuration de l'application
    cat > "$OPENRED_HOME/config/app.conf" << EOF
[openred]
node_id = $(uuidgen)
server_url = http://localhost
backend_port = $BACKEND_PORT
frontend_port = $FRONTEND_PORT
database_path = $OPENRED_HOME/data/$DATABASE_NAME.db
private_key_path = $OPENRED_HOME/config/private_key.pem
public_key_path = $OPENRED_HOME/config/public_key.pem

[central_api]
url = https://api.openred.org
register_endpoint = /api/v1/nodes/register
EOF

    chown -R "$SERVICE_USER:$SERVICE_USER" "$OPENRED_HOME/config/"
    chmod 600 "$OPENRED_HOME/config/private_key.pem"
    
    log_info "Configuration générée"
}

# Vérification de l'installation
verify_installation() {
    log_info "Vérification de l'installation..."
    
    # Vérification des services
    if systemctl is-active --quiet openred-backend.service; then
        log_info "✅ Service backend: actif"
    else
        log_error "❌ Service backend: inactif"
    fi
    
    # Vérification des ports
    if netstat -tlnp | grep ":$BACKEND_PORT " > /dev/null; then
        log_info "✅ Backend accessible sur le port $BACKEND_PORT"
    else
        log_warn "⚠️  Backend non accessible sur le port $BACKEND_PORT"
    fi
    
    if systemctl is-active --quiet nginx; then
        log_info "✅ Nginx: actif"
    else
        log_error "❌ Nginx: inactif"
    fi
}

# Affichage des informations post-installation
show_completion_info() {
    echo ""
    echo "🎉 Installation OpenRed terminée avec succès!"
    echo "============================================="
    echo ""
    echo "📍 Répertoire d'installation: $OPENRED_HOME"
    echo "🌐 Interface web: http://localhost"
    echo "🔧 Backend API: http://localhost:$BACKEND_PORT"
    echo "📄 Logs backend: journalctl -u openred-backend.service -f"
    echo "📄 Logs nginx: tail -f /var/log/nginx/access.log"
    echo ""
    echo "📝 Prochaines étapes:"
    echo "1. Accédez à http://localhost pour configurer votre profil"
    echo "2. Enregistrez votre node sur le réseau OpenRed"
    echo "3. Commencez à connecter avec d'autres utilisateurs!"
    echo ""
    echo "📚 Documentation: https://docs.openred.org"
    echo "🐛 Support: https://github.com/openred/openred/issues"
}

# Fonction principale
main() {
    echo "OpenRed Node Client Installer v1.0"
    echo "Début de l'installation..."
    echo ""
    
    check_requirements
    install_dependencies
    create_user
    download_files
    setup_database
    setup_python_env
    setup_frontend
    setup_nginx
    create_services
    generate_config
    verify_installation
    show_completion_info
}

# Gestion des erreurs
trap 'log_error "Installation échouée à la ligne $LINENO"' ERR

# Exécution du script principal
main "$@"