#!/bin/bash
# === OpenRed P2P Platform - Entrypoint Script ===
# Script d'initialisation pour container Docker

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonction de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ✅ $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ⚠️ $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ❌ $1"
}

# Banner OpenRed
show_banner() {
    echo -e "${PURPLE}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                     🚀 OpenRed P2P Platform                      ║"
    echo "║                Revolutionary Decentralized Node                  ║"
    echo "║                                                                   ║"
    echo "║  🌟 Pure P2P Architecture  🔐 RSA 2048 Security                  ║"
    echo "║  📡 UDP Multicast Discovery 🔱 Phantom URN System                ║"
    echo "║  🚫 NO CENTRAL API - Pure Decentralization                       ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Configuration par défaut
setup_defaults() {
    log "Setting up default configuration..."
    
    # Node ID automatique si non défini
    if [ -z "$OPENRED_NODE_ID" ]; then
        OPENRED_NODE_ID="node_$(date +%s)_$(shuf -i 1000-9999 -n 1)"
        log "Generated automatic Node ID: $OPENRED_NODE_ID"
    fi
    
    # Secteur par défaut
    if [ -z "$OPENRED_SECTOR" ]; then
        OPENRED_SECTOR="general"
    fi
    
    # Ports par défaut
    if [ -z "$OPENRED_P2P_PORT" ]; then
        OPENRED_P2P_PORT=8080
    fi
    
    if [ -z "$OPENRED_WEB_PORT" ]; then
        OPENRED_WEB_PORT=8000
    fi
    
    log_success "Configuration: ID=$OPENRED_NODE_ID, Sector=$OPENRED_SECTOR, P2P=$OPENRED_P2P_PORT"
}

# Vérification réseau
check_network() {
    log "Checking network configuration..."
    
    # Vérification connectivité
    if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        log_success "Internet connectivity: OK"
    else
        log_warning "No internet connectivity detected"
    fi
    
    # Vérification interface multicast
    if ip route | grep -q "224.0.0.0/4"; then
        log_success "Multicast routing: OK"
    else
        log_warning "Multicast routing may not be available"
    fi
    
    # Affichage interfaces réseau
    log "Available network interfaces:"
    ip addr show | grep -E "^[0-9]+:" | awk '{print "  - " $2}' | sed 's/:$//'
}

# Préparation répertoires
setup_directories() {
    log "Setting up directories..."
    
    # Création répertoires de données
    mkdir -p /data/phantom_urn_cache
    mkdir -p /data/urn-files
    mkdir -p /data/logs
    mkdir -p /data/config
    mkdir -p /data/keys
    
    # Permissions
    chmod 755 /data/phantom_urn_cache
    chmod 755 /data/urn-files
    chmod 755 /data/logs
    chmod 700 /data/keys  # Clés cryptographiques sensibles
    
    log_success "Directories configured"
}

# Génération configuration
generate_config() {
    log "Generating node configuration..."
    
    cat > /data/config/node.json << EOF
{
    "node_id": "$OPENRED_NODE_ID",
    "sector": "$OPENRED_SECTOR",
    "p2p_port": $OPENRED_P2P_PORT,
    "web_port": $OPENRED_WEB_PORT,
    "lighthouse": {
        "multicast_group": "224.0.1.100",
        "multicast_port": 5354,
        "beacon_interval": 30
    },
    "security": {
        "rsa_key_size": 2048,
        "session_timeout": 3600
    },
    "phantom_urn": {
        "cache_directory": "/data/phantom_urn_cache",
        "urn_directory": "/data/urn-files"
    }
}
EOF
    
    log_success "Configuration file created: /data/config/node.json"
}

# Vérification santé
health_check() {
    log "Performing health check..."
    
    # Vérification Python
    if python3 --version > /dev/null 2>&1; then
        log_success "Python: $(python3 --version)"
    else
        log_error "Python not available"
        exit 1
    fi
    
    # Vérification modules
    if python3 -c "import cryptography, asyncio, socket, json" 2>/dev/null; then
        log_success "Required Python modules: OK"
    else
        log_error "Missing Python modules"
        exit 1
    fi
    
    # Vérification fichiers application
    if [ -f "/app/openred_p2p_node.py" ]; then
        log_success "Application files: OK"
    else
        log_error "Application files missing"
        exit 1
    fi
}

# Démarrage nœud P2P
start_node() {
    log "Starting OpenRed P2P Node..."
    
    cd /app
    
    # Variables d'environnement pour l'application
    export OPENRED_CONFIG_FILE="/data/config/node.json"
    export OPENRED_DATA_DIR="/data"
    
    # Démarrage avec gestion des signaux
    exec python3 openred_p2p_node.py \
        --node-id "$OPENRED_NODE_ID" \
        --sector "$OPENRED_SECTOR" \
        --port "$OPENRED_P2P_PORT" \
        --data-dir "/data" \
        --config "/data/config/node.json"
}

# Démarrage mode interactif
start_interactive() {
    log "Starting interactive mode..."
    
    cd /app
    export OPENRED_CONFIG_FILE="/data/config/node.json"
    export OPENRED_DATA_DIR="/data"
    
    echo ""
    echo -e "${CYAN}🎮 OpenRed P2P Interactive Mode${NC}"
    echo "Available commands:"
    echo "  start           - Start P2P node"
    echo "  test            - Run platform tests"
    echo "  status          - Show node status"
    echo "  config          - Show configuration"
    echo "  logs            - Show logs"
    echo "  shell           - Open bash shell"
    echo ""
    
    exec /bin/bash
}

# Test plateforme
run_tests() {
    log "Running platform tests..."
    
    cd /app
    python3 test_p2p_platform.py
    
    if [ $? -eq 0 ]; then
        log_success "All tests passed!"
    else
        log_error "Tests failed"
        exit 1
    fi
}

# Affichage configuration
show_config() {
    log "Current configuration:"
    
    if [ -f "/data/config/node.json" ]; then
        cat /data/config/node.json | python3 -m json.tool
    else
        log_warning "No configuration file found"
    fi
}

# Main
main() {
    show_banner
    
    case "$1" in
        "start-node")
            setup_defaults
            check_network
            setup_directories
            generate_config
            health_check
            start_node
            ;;
        "interactive")
            setup_defaults
            setup_directories
            generate_config
            start_interactive
            ;;
        "test")
            setup_defaults
            setup_directories
            health_check
            run_tests
            ;;
        "config")
            show_config
            ;;
        "shell")
            exec /bin/bash
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Available commands: start-node, interactive, test, config, shell"
            exit 1
            ;;
    esac
}

# Gestion des signaux pour arrêt propre
trap 'log "Shutting down gracefully..."; exit 0' SIGTERM SIGINT

# Exécution
main "$@"