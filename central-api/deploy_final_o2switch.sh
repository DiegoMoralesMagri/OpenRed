#!/bin/bash

# 🚀 OpenRed Central API v2.0 - Déploiement Multi-Mode O2Switch
# Deployment script with multiple hosting modes

echo "🚀 OpenRed Central API v2.0 - Déploiement O2Switch"
echo "=================================================="
echo "🎯 Solutions multiples pour hébergement partagé"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/deploy.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Menu de sélection
echo "📋 MODES DE DÉPLOIEMENT DISPONIBLES :"
echo ""
echo "1️⃣  MODE WSGI (Recommandé)"
echo "   ✅ Performance optimale"
echo "   ✅ Compatible Passenger"
echo "   ✅ Headers de sécurité"
echo ""
echo "2️⃣  MODE CGI (Compatibilité maximale)"
echo "   ✅ Fonctionne partout"
echo "   ✅ Pas de processus persistant"
echo "   ✅ Très simple"
echo ""
echo "3️⃣  MODE STANDALONE (Test local)"
echo "   ✅ Serveur intégré"
echo "   ✅ Pour développement"
echo "   ❌ Peut être tué par l'hébergeur"
echo ""

read -p "🔧 Choisissez le mode (1, 2 ou 3) : " MODE

case $MODE in
    1)
        echo "🎯 Déploiement MODE WSGI"
        log "Déploiement WSGI sélectionné"
        
        # Configuration WSGI
        cp "$SCRIPT_DIR/passenger_wsgi_production.py" "$SCRIPT_DIR/passenger_wsgi.py"
        
        cat > "$SCRIPT_DIR/.htaccess" << 'EOF'
PassengerEnabled on
PassengerAppRoot /home/[USERNAME]/www
PassengerAppType wsgi
PassengerStartupFile passenger_wsgi.py

Header always set Access-Control-Allow-Origin "*"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization"

<Files "*.py">
    Require all denied
</Files>

<Files "passenger_wsgi.py">
    Require all granted
</Files>

RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
EOF
        
        log "✅ Configuration WSGI créée"
        echo "✅ Mode WSGI configuré"
        echo "📋 Fichiers principaux : passenger_wsgi.py, .htaccess"
        echo "🌐 Accès : https://[votre-domaine]/"
        ;;
        
    2)
        echo "🎯 Déploiement MODE CGI"
        log "Déploiement CGI sélectionné"
        
        # Configuration CGI
        cp "$SCRIPT_DIR/.htaccess_cgi" "$SCRIPT_DIR/.htaccess"
        chmod +x "$SCRIPT_DIR/index.py"
        
        log "✅ Configuration CGI créée"
        echo "✅ Mode CGI configuré"
        echo "📋 Fichiers principaux : index.py, .htaccess"
        echo "🌐 Accès : https://[votre-domaine]/"
        ;;
        
    3)
        echo "🎯 Déploiement MODE STANDALONE"
        log "Déploiement STANDALONE sélectionné"
        
        # Configuration standalone  
        cat > "$SCRIPT_DIR/.htaccess" << 'EOF'
# Redirection vers le port du serveur standalone
RewriteEngine On
RewriteRule ^(.*)$ http://localhost:8000/$1 [P,L]

Header always set Access-Control-Allow-Origin "*"
EOF
        
        log "✅ Configuration STANDALONE créée"
        echo "✅ Mode STANDALONE configuré"
        echo "📋 Fichiers principaux : main_standalone.py, .htaccess"
        echo "🚨 ATTENTION : Ce mode peut être tué par l'hébergeur"
        echo "🌐 Démarrage : python3 main_standalone.py"
        ;;
        
    *)
        echo "❌ Mode invalide"
        exit 1
        ;;
esac

# Configuration commune
cat > "$SCRIPT_DIR/.env.o2switch" << 'EOF'
ENVIRONMENT=production
API_VERSION=2.0.0
DEPLOYMENT_MODE=o2switch
SECRET_KEY=o2switch_openred_2024
LOG_LEVEL=INFO
EOF

# Script de test
cat > "$SCRIPT_DIR/test_deployment.sh" << 'EOF'
#!/bin/bash
echo "🧪 Test OpenRed Central API v2.0"
echo "================================"

echo "🔍 Test des fichiers..."
if [ -f ".htaccess" ]; then
    echo "✅ .htaccess présent"
else
    echo "❌ .htaccess manquant"
fi

echo -e "\n🐍 Test Python..."
python3 --version || python --version

echo -e "\n🌐 Test de connectivité..."
if command -v curl >/dev/null; then
    echo "Testing API endpoint..."
    curl -s -H "Accept: application/json" http://localhost/ | head -3
else
    echo "curl non disponible, test manuel requis"
fi

echo -e "\n📋 Résumé du déploiement :"
ls -la | grep -E "(\.htaccess|\.py|\.env)"
EOF

chmod +x "$SCRIPT_DIR/test_deployment.sh"

# Documentation finale
cat > "$SCRIPT_DIR/GUIDE_DEPLOIEMENT_FINAL.md" << 'EOF'
# OpenRed Central API v2.0 - Guide de Déploiement Final

## 🎯 Déploiement réussi !

Votre API OpenRed Central v2.0 est maintenant configurée pour O2Switch.

### 📋 Modes disponibles

#### 1️⃣ Mode WSGI (Recommandé)
- **Fichiers** : `passenger_wsgi.py`, `.htaccess`
- **Accès** : https://[votre-domaine]/
- **Performance** : Optimale
- **Stabilité** : Excellente

#### 2️⃣ Mode CGI (Compatibilité maximale)
- **Fichiers** : `index.py`, `.htaccess`
- **Accès** : https://[votre-domaine]/
- **Performance** : Bonne
- **Stabilité** : Excellente

#### 3️⃣ Mode Standalone (Développement)
- **Fichiers** : `main_standalone.py`, `.htaccess`
- **Démarrage** : `python3 main_standalone.py`
- **Performance** : Très bonne
- **Stabilité** : Variable (peut être tué)

### 🚀 Étapes suivantes

1. **Upload des fichiers** sur votre espace O2Switch
2. **Configuration du domaine** dans votre panel
3. **Test de l'API** : https://[votre-domaine]/
4. **Vérification** : `./test_deployment.sh`

### 📊 Endpoints disponibles

- `GET /` - Page d'accueil API
- `GET /health` - Check de santé
- `GET /api/v1/status` - Statut API
- `GET /api/v1/nodes/discover` - Découverte nœuds
- `POST /api/v1/auth/register` - Enregistrement
- `POST /api/v1/auth/login` - Authentification

### 🔧 Résolution de problèmes

1. **Erreur 500** : Vérifiez les permissions (644 pour .py, 604 pour .htaccess)
2. **Accès refusé** : Vérifiez la configuration Apache
3. **CORS** : Headers configurés automatiquement
4. **HTTPS** : Redirection automatique configurée

### 📞 Support

- **Documentation** : README_O2SWITCH.md
- **Test** : ./test_deployment.sh
- **Logs** : Consultez les logs O2Switch

---
OpenRed Central API v2.0 - Prêt pour la production !
EOF

echo ""
echo "🎉 DÉPLOIEMENT TERMINÉ !"
echo "======================="
echo ""
echo "✅ Configuration choisie : Mode $MODE"
echo "✅ Fichiers créés et configurés"
echo "✅ Scripts utilitaires disponibles"
echo ""
echo "📋 PROCHAINES ÉTAPES :"
echo "1. Uploadez TOUS les fichiers sur O2Switch"
echo "2. Configurez votre domaine/sous-domaine"
echo "3. Testez : https://[votre-domaine]/"
echo "4. Vérifiez : ./test_deployment.sh"
echo ""
echo "📚 Guide complet : GUIDE_DEPLOIEMENT_FINAL.md"
echo ""
log "Déploiement terminé - Mode $MODE"
echo "✨ Votre API OpenRed est prête !"
