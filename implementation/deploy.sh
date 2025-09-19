#!/bin/bash

# Script de déploiement automatisé pour l'écosystème O-Red
# Version: 1.0.0
# Auteur: O-Red Community

set -e  # Arrêt en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ORED_VERSION="1.0.0"
DEPLOYMENT_ENV=${1:-development}
PROJECT_ROOT=$(pwd)

echo -e "${BLUE}🚀 Déploiement de l'écosystème O-Red v${ORED_VERSION}${NC}"
echo -e "${BLUE}📁 Répertoire: ${PROJECT_ROOT}${NC}"
echo -e "${BLUE}🌍 Environnement: ${DEPLOYMENT_ENV}${NC}"
echo ""

# Fonction pour afficher les étapes
step_counter=1
print_step() {
    echo -e "${GREEN}[${step_counter}/10] $1${NC}"
    ((step_counter++))
}

# Fonction pour vérifier les prérequis
check_prerequisites() {
    print_step "Vérification des prérequis"
    
    # Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker n'est pas installé${NC}"
        exit 1
    fi
    echo -e "✅ Docker: $(docker --version)"
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"
        exit 1
    fi
    echo -e "✅ Docker Compose: $(docker-compose --version)"
    
    # Node.js (pour l'interface web)
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js n'est pas installé${NC}"
        exit 1
    fi
    echo -e "✅ Node.js: $(node --version)"
    
    # Python (pour l'API et les nœuds)
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
        exit 1
    fi
    echo -e "✅ Python: $(python3 --version)"
    
    echo ""
}

# Configuration de l'environnement
setup_environment() {
    print_step "Configuration de l'environnement"
    
    # Création du fichier .env si nécessaire
    if [ ! -f "${PROJECT_ROOT}/central-api/.env" ]; then
        echo -e "${YELLOW}📝 Création du fichier .env pour l'API centrale${NC}"
        cat > "${PROJECT_ROOT}/central-api/.env" << EOF
# Configuration O-Red API Centrale - ${DEPLOYMENT_ENV}
DEBUG=${DEBUG:-false}
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql+asyncpg://ored:ored_secure_password@postgres:5432/ored_central
REDIS_URL=redis://redis:6379/0
LOG_LEVEL=INFO
PROMETHEUS_ENABLED=true

# Configuration P2P
P2P_PORT=8001
P2P_MAX_CONNECTIONS=100

# Configuration IA
AI_DISTRIBUTED_COMPUTING_ENABLED=true
AI_PRIVACY_LEVEL=maximum

# Configuration sécurité
POST_QUANTUM_ENABLED=true
RATE_LIMIT_ENABLED=true
EOF
    fi
    
    # Création des dossiers nécessaires
    mkdir -p "${PROJECT_ROOT}/logs"
    mkdir -p "${PROJECT_ROOT}/storage"
    mkdir -p "${PROJECT_ROOT}/data/postgres"
    mkdir -p "${PROJECT_ROOT}/data/redis"
    
    echo -e "✅ Environnement configuré"
    echo ""
}

# Construction des images Docker
build_images() {
    print_step "Construction des images Docker"
    
    cd "${PROJECT_ROOT}/central-api"
    echo -e "${BLUE}🔨 Construction de l'image API centrale...${NC}"
    docker build -t ored/central-api:${ORED_VERSION} .
    docker tag ored/central-api:${ORED_VERSION} ored/central-api:latest
    
    if [ -d "${PROJECT_ROOT}/web-interface" ]; then
        cd "${PROJECT_ROOT}/web-interface"
        echo -e "${BLUE}🔨 Construction de l'image interface web...${NC}"
        # Vérifier si le Dockerfile existe
        if [ -f "Dockerfile" ]; then
            docker build -t ored/web-interface:${ORED_VERSION} .
            docker tag ored/web-interface:${ORED_VERSION} ored/web-interface:latest
        else
            echo -e "${YELLOW}⚠️  Dockerfile de l'interface web non trouvé, construction ignorée${NC}"
        fi
    fi
    
    if [ -d "${PROJECT_ROOT}/node-client" ]; then
        cd "${PROJECT_ROOT}/node-client"
        echo -e "${BLUE}🔨 Construction de l'image client nœud...${NC}"
        # Vérifier si le Dockerfile existe
        if [ -f "Dockerfile" ]; then
            docker build -t ored/node-client:${ORED_VERSION} .
            docker tag ored/node-client:${ORED_VERSION} ored/node-client:latest
        else
            echo -e "${YELLOW}⚠️  Dockerfile du client nœud non trouvé, construction ignorée${NC}"
        fi
    fi
    
    echo -e "✅ Images Docker construites"
    echo ""
}

# Installation des dépendances
install_dependencies() {
    print_step "Installation des dépendances"
    
    # API centrale
    if [ -f "${PROJECT_ROOT}/central-api/requirements.txt" ]; then
        echo -e "${BLUE}📦 Installation des dépendances Python (API centrale)...${NC}"
        cd "${PROJECT_ROOT}/central-api"
        python3 -m pip install -r requirements.txt
    fi
    
    # Interface web
    if [ -f "${PROJECT_ROOT}/web-interface/package.json" ]; then
        echo -e "${BLUE}📦 Installation des dépendances Node.js (Interface web)...${NC}"
        cd "${PROJECT_ROOT}/web-interface"
        npm install
    fi
    
    # Client nœud
    if [ -f "${PROJECT_ROOT}/node-client/requirements.txt" ]; then
        echo -e "${BLUE}📦 Installation des dépendances Python (Client nœud)...${NC}"
        cd "${PROJECT_ROOT}/node-client"
        python3 -m pip install -r requirements.txt
    fi
    
    echo -e "✅ Dépendances installées"
    echo ""
}

# Configuration de la base de données
setup_database() {
    print_step "Configuration de la base de données"
    
    # Création du script d'initialisation de la base de données
    mkdir -p "${PROJECT_ROOT}/central-api/db"
    cat > "${PROJECT_ROOT}/central-api/db/init.sql" << EOF
-- Script d'initialisation de la base de données O-Red
-- Version: ${ORED_VERSION}

-- Création de la base de données (si nécessaire)
-- CREATE DATABASE ored_central;

-- Extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_crypto";

-- Index pour améliorer les performances
-- Ces index seront créés automatiquement par SQLAlchemy lors du premier démarrage

-- Configuration des permissions
-- GRANT ALL PRIVILEGES ON DATABASE ored_central TO ored;

-- Insertion de données de test (seulement en développement)
DO \$\$
BEGIN
    IF '${DEPLOYMENT_ENV}' = 'development' THEN
        -- Des données de test peuvent être ajoutées ici
        RAISE NOTICE 'Base de données configurée pour le développement';
    END IF;
END \$\$;
EOF
    
    echo -e "✅ Configuration de la base de données créée"
    echo ""
}

# Configuration du monitoring
setup_monitoring() {
    print_step "Configuration du monitoring"
    
    mkdir -p "${PROJECT_ROOT}/central-api/monitoring"
    
    # Configuration Prometheus
    cat > "${PROJECT_ROOT}/central-api/monitoring/prometheus.yml" << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ored-api'
    static_configs:
      - targets: ['ored-api:8000']
    metrics_path: '/metrics'

  - job_name: 'ored-node'
    static_configs:
      - targets: ['ored-node:8001']
    metrics_path: '/metrics'
EOF
    
    # Configuration Nginx
    mkdir -p "${PROJECT_ROOT}/central-api/nginx"
    cat > "${PROJECT_ROOT}/central-api/nginx/nginx.conf" << EOF
events {
    worker_connections 1024;
}

http {
    upstream ored_api {
        server ored-api:8000;
    }
    
    upstream ored_web {
        server ored-web:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # API routes
        location /api/ {
            proxy_pass http://ored_api;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Interface web
        location / {
            proxy_pass http://ored_web;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF
    
    echo -e "✅ Configuration du monitoring créée"
    echo ""
}

# Démarrage des services
start_services() {
    print_step "Démarrage des services O-Red"
    
    cd "${PROJECT_ROOT}/central-api"
    
    # Arrêt des services existants
    echo -e "${BLUE}🛑 Arrêt des services existants...${NC}"
    docker-compose down || true
    
    # Démarrage des services
    echo -e "${BLUE}🚀 Démarrage des nouveaux services...${NC}"
    docker-compose up -d
    
    # Attendre que les services soient prêts
    echo -e "${BLUE}⏳ Attente de la disponibilité des services...${NC}"
    sleep 10
    
    echo -e "✅ Services démarrés"
    echo ""
}

# Vérification du déploiement
verify_deployment() {
    print_step "Vérification du déploiement"
    
    # Vérification de l'API
    echo -e "${BLUE}🔍 Vérification de l'API centrale...${NC}"
    for i in {1..30}; do
        if curl -f -s "http://localhost:8000/health" > /dev/null; then
            echo -e "✅ API centrale accessible"
            break
        fi
        echo -e "⏳ Tentative ${i}/30..."
        sleep 2
    done
    
    # Vérification de la base de données
    echo -e "${BLUE}🔍 Vérification de la base de données...${NC}"
    if docker-compose exec -T postgres pg_isready -U ored; then
        echo -e "✅ Base de données accessible"
    else
        echo -e "${RED}❌ Base de données non accessible${NC}"
    fi
    
    # Vérification de Redis
    echo -e "${BLUE}🔍 Vérification de Redis...${NC}"
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        echo -e "✅ Redis accessible"
    else
        echo -e "${RED}❌ Redis non accessible${NC}"
    fi
    
    echo ""
}

# Tests automatisés
run_tests() {
    print_step "Exécution des tests"
    
    # Tests de l'API
    if [ -f "${PROJECT_ROOT}/central-api/app/tests/test_main.py" ]; then
        echo -e "${BLUE}🧪 Tests de l'API centrale...${NC}"
        cd "${PROJECT_ROOT}/central-api"
        python3 -m pytest app/tests/ -v || echo -e "${YELLOW}⚠️  Certains tests ont échoué${NC}"
    fi
    
    # Tests de l'interface web
    if [ -f "${PROJECT_ROOT}/web-interface/package.json" ]; then
        echo -e "${BLUE}🧪 Tests de l'interface web...${NC}"
        cd "${PROJECT_ROOT}/web-interface"
        npm test || echo -e "${YELLOW}⚠️  Certains tests ont échoué${NC}"
    fi
    
    echo -e "✅ Tests exécutés"
    echo ""
}

# Affichage des informations finales
show_final_info() {
    print_step "Informations de déploiement"
    
    echo -e "${GREEN}🎉 Déploiement d'O-Red terminé avec succès !${NC}"
    echo ""
    echo -e "${BLUE}📋 Informations d'accès:${NC}"
    echo -e "   🌐 Interface web: http://localhost:3000"
    echo -e "   🔌 API centrale: http://localhost:8000"
    echo -e "   📊 API docs: http://localhost:8000/docs"
    echo -e "   📈 Prometheus: http://localhost:9090"
    echo -e "   📊 Grafana: http://localhost:3001 (admin/ored_admin_password)"
    echo ""
    echo -e "${BLUE}📁 Logs et données:${NC}"
    echo -e "   📝 Logs: ${PROJECT_ROOT}/logs/"
    echo -e "   💾 Stockage: ${PROJECT_ROOT}/storage/"
    echo ""
    echo -e "${BLUE}🔧 Commandes utiles:${NC}"
    echo -e "   docker-compose logs -f      # Voir les logs en temps réel"
    echo -e "   docker-compose ps           # Statut des services"
    echo -e "   docker-compose down         # Arrêter les services"
    echo -e "   docker-compose up -d        # Redémarrer les services"
    echo ""
    echo -e "${GREEN}Bienvenue dans l'écosystème O-Red décentralisé ! 🚀${NC}"
}

# Exécution du script principal
main() {
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                  DÉPLOIEMENT O-RED v${ORED_VERSION}                    ║${NC}"
    echo -e "${BLUE}║                Écosystème Décentralisé                    ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_prerequisites
    setup_environment
    install_dependencies
    setup_database
    setup_monitoring
    build_images
    start_services
    verify_deployment
    
    if [ "${DEPLOYMENT_ENV}" != "production" ]; then
        run_tests
    fi
    
    show_final_info
}

# Gestion des erreurs
trap 'echo -e "${RED}❌ Erreur lors du déploiement${NC}"; exit 1' ERR

# Point d'entrée
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi