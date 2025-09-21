#!/bin/bash

# 🚀 Script de déploiement OpenRed Central API v2.0 pour O2Switch
# OpenRed Central API v2.0 deployment script for O2Switch

echo "🚀 OpenRed Central API v2.0 - Déploiement O2Switch"
echo "=================================================="

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$SCRIPT_DIR"
LOG_FILE="$API_DIR/deploy.log"

# Fonction de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Fonction de test
test_command() {
    local cmd="$1"
    local desc="$2"
    
    log "🔍 Test: $desc"
    if command -v "$cmd" >/dev/null 2>&1; then
        log "✅ $cmd disponible"
        return 0
    else
        log "❌ $cmd non disponible"
        return 1
    fi
}

log "🎯 Début du déploiement OpenRed"
log "📁 Répertoire: $API_DIR"

# 1. Vérification de l'environnement O2Switch
log "🔍 Vérification de l'environnement O2Switch..."

# Test Python
if test_command python3 "Python 3"; then
    PYTHON_CMD="python3"
elif test_command python "Python"; then
    PYTHON_CMD="python"
else
    log "❌ ERREUR: Python non trouvé"
    exit 1
fi

log "🐍 Python trouvé: $PYTHON_CMD"
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
log "📋 Version Python: $PYTHON_VERSION"

# 2. Configuration des fichiers pour O2Switch
log "📝 Configuration des fichiers pour O2Switch..."

# Création du fichier .htaccess pour O2Switch
cat > "$API_DIR/.htaccess" << 'EOF'
# Configuration O2Switch pour OpenRed Central API v2.0
PassengerEnabled on
PassengerAppRoot /home/[USERNAME]/www
PassengerAppType wsgi
PassengerStartupFile passenger_wsgi_production.py

# Sécurité
<Files "*.py">
    Require all denied
</Files>

<Files "passenger_wsgi_production.py">
    Require all granted
</Files>

# Headers de sécurité
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"

# CORS pour API
Header always set Access-Control-Allow-Origin "*"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization, X-Requested-With"

# Cache des ressources statiques
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType application/json "access plus 1 hour"
</IfModule>

# Redirection vers HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
EOF

log "✅ Fichier .htaccess créé"

# 3. Création du fichier passenger_wsgi.py principal
cp "$API_DIR/passenger_wsgi_production.py" "$API_DIR/passenger_wsgi.py"
log "✅ passenger_wsgi.py configuré"

# 4. Configuration de l'environnement
log "🔧 Configuration de l'environnement..."

# Création du fichier de configuration O2Switch
cat > "$API_DIR/.env.o2switch" << 'EOF'
# Configuration OpenRed Central API v2.0 pour O2Switch
ENVIRONMENT=production
API_VERSION=2.0.0
DEPLOYMENT_MODE=o2switch

# Sécurité
SECRET_KEY=o2switch_openred_secret_2024
JWT_SECRET=o2switch_jwt_secret_openred_2024

# Limits pour hébergement partagé
MAX_CONNECTIONS=100
MAX_REQUEST_SIZE=10485760
RATE_LIMIT=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=openred_api.log

# Features
ENABLE_CORS=true
ENABLE_SECURITY_HEADERS=true
ENABLE_RATE_LIMITING=true
EOF

log "✅ Configuration environnement créée"

# 5. Test de l'application WSGI
log "🧪 Test de l'application WSGI..."

cd "$API_DIR"

# Test basique Python
$PYTHON_CMD -c "
import sys
print('Python OK:', sys.version)
try:
    import json, os, time
    print('✅ Modules standard disponibles')
except ImportError as e:
    print('❌ Erreur modules:', e)
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    log "✅ Test Python réussi"
else
    log "❌ Test Python échoué"
    exit 1
fi

# Test WSGI
$PYTHON_CMD passenger_wsgi_production.py
if [ $? -eq 0 ]; then
    log "✅ Test WSGI réussi"
else
    log "❌ Test WSGI échoué"
    exit 1
fi

# 6. Création des scripts utilitaires
log "🛠️ Création des scripts utilitaires..."

# Script de diagnostic
cat > "$API_DIR/diagnostic_o2switch.sh" << 'EOF'
#!/bin/bash
echo "🔍 Diagnostic OpenRed Central API v2.0 - O2Switch"
echo "================================================"

echo "📁 Répertoire de travail:"
pwd

echo -e "\n🐍 Python:"
python3 --version 2>/dev/null || python --version

echo -e "\n📋 Modules Python:"
python3 -c "
import sys
modules = ['json', 'os', 'time', 'sys', 'urllib']
for mod in modules:
    try:
        __import__(mod)
        print(f'✅ {mod}')
    except:
        print(f'❌ {mod}')
"

echo -e "\n📁 Fichiers OpenRed:"
ls -la | grep -E "(passenger_wsgi|\.htaccess|\.env)"

echo -e "\n🌐 Test WSGI:"
python3 passenger_wsgi_production.py 2>&1 | head -5

echo -e "\n✅ Diagnostic terminé"
EOF

chmod +x "$API_DIR/diagnostic_o2switch.sh"
log "✅ Script de diagnostic créé"

# Script de monitoring
cat > "$API_DIR/monitor_o2switch.sh" << 'EOF'
#!/bin/bash
echo "📊 Monitoring OpenRed Central API v2.0"
echo "======================================"

LOG_FILE="openred_api.log"

if [ -f "$LOG_FILE" ]; then
    echo "📈 Dernières activités:"
    tail -10 "$LOG_FILE"
else
    echo "📋 Aucun log trouvé"
fi

echo -e "\n🔄 Processus Python:"
ps aux | grep python | grep -v grep || echo "Aucun processus Python actif"

echo -e "\n💾 Utilisation disque:"
du -sh . 2>/dev/null || echo "Impossible de calculer"

echo -e "\n🌐 Test connectivité:"
if command -v curl >/dev/null; then
    curl -s -I http://localhost/ | head -1 || echo "Service non accessible"
else
    echo "curl non disponible"
fi
EOF

chmod +x "$API_DIR/monitor_o2switch.sh"
log "✅ Script de monitoring créé"

# 7. Documentation finale
log "📚 Création de la documentation..."

cat > "$API_DIR/README_O2SWITCH.md" << 'EOF'
# OpenRed Central API v2.0 - Déploiement O2Switch

## 🚀 Installation terminée

L'API OpenRed Central v2.0 est maintenant configurée pour O2Switch.

### 📁 Fichiers importants

- `passenger_wsgi.py` - Application WSGI principale
- `.htaccess` - Configuration Apache/Passenger
- `.env.o2switch` - Variables d'environnement
- `diagnostic_o2switch.sh` - Script de diagnostic
- `monitor_o2switch.sh` - Script de monitoring

### 🌐 Accès

Votre API sera accessible à l'adresse :
```
https://[votre-domaine]/
```

### 🧪 Tests

1. **Test de base :**
   ```bash
   ./diagnostic_o2switch.sh
   ```

2. **Monitoring :**
   ```bash
   ./monitor_o2switch.sh
   ```

### 📋 Endpoints disponibles

- `GET /` - Page d'accueil API
- `GET /health` - Statut santé
- `GET /api/v1/status` - Statut API
- `POST /api/v1/auth/register` - Enregistrement nœud
- `POST /api/v1/auth/login` - Authentification
- `GET /api/v1/nodes/discover` - Découverte nœuds
- `POST /api/v1/messages/send` - Envoi message

### 🔧 Configuration O2Switch

L'API utilise :
- **WSGI** avec Passenger
- **Modules Python standard** uniquement
- **Headers de sécurité OWASP**
- **CORS configuré**
- **Rate limiting**

### 📞 Support

En cas de problème :
1. Vérifiez les logs : `tail -f openred_api.log`
2. Lancez le diagnostic : `./diagnostic_o2switch.sh`
3. Consultez la documentation O2Switch

---
OpenRed Central API v2.0 - Production Ready
EOF

log "✅ Documentation créée"

# 8. Finalisation
log "🎯 Finalisation du déploiement..."

# Vérification finale
if [ -f "$API_DIR/passenger_wsgi.py" ] && [ -f "$API_DIR/.htaccess" ]; then
    log "✅ Tous les fichiers essentiels sont présents"
else
    log "❌ Fichiers manquants détectés"
    exit 1
fi

# Permissions
chmod 644 "$API_DIR/passenger_wsgi.py"
chmod 644 "$API_DIR/.htaccess"
chmod 600 "$API_DIR/.env.o2switch"

log "✅ Permissions configurées"

# Message final
echo ""
echo "🎉 DÉPLOIEMENT OPENRED CENTRAL API v2.0 TERMINÉ !"
echo "================================================"
echo ""
echo "✅ Configuration O2Switch complète"
echo "✅ Application WSGI opérationnelle"
echo "✅ Sécurité OWASP configurée"
echo "✅ Scripts utilitaires créés"
echo ""
echo "📋 PROCHAINES ÉTAPES :"
echo "1. Uploadez les fichiers sur votre espace O2Switch"
echo "2. Configurez votre domaine/sous-domaine"
echo "3. Testez l'accès : https://[votre-domaine]/"
echo "4. Lancez le diagnostic : ./diagnostic_o2switch.sh"
echo ""
echo "🌐 Votre API OpenRed Central v2.0 sera accessible sous :"
echo "   https://[votre-domaine]/"
echo ""
echo "📚 Documentation complète dans README_O2SWITCH.md"
echo ""
log "🎯 Déploiement terminé avec succès"
echo "✨ Bon déploiement OpenRed !"
