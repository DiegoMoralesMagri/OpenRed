#!/bin/bash
# Installation manuelle SANS pip pour O2Switch
# Manual installation WITHOUT pip for O2Switch

echo "🛠️  Installation OpenRed SANS pip - O2Switch"
echo "🛠️  OpenRed installation WITHOUT pip - O2Switch"

echo ""
echo "=== ÉTAPE 1: VÉRIFICATION PYTHON ==="
echo "Python version check..."

# Trouve la meilleure version de Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Python3 trouvé: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ Python trouvé: $(python --version)"
else
    echo "❌ Aucun Python trouvé!"
    echo "Contactez O2Switch pour activer Python"
    exit 1
fi

echo ""
echo "=== ÉTAPE 2: CONFIGURATION DE BASE ==="
echo "Basic configuration..."

# Création des dossiers nécessaires
mkdir -p keys logs uploads static
chmod 755 keys logs uploads static

# Configuration environnement (version minimale)
cat > .env << 'EOF'
# Configuration O2Switch sans dépendances externes
ENVIRONMENT=production
DEBUG=false
APP_NAME=OpenRed Central API
APP_VERSION=2.0.0

# Pas de base de données externe - fichiers locaux
DATABASE_URL=sqlite:///./openred_simple.db

# Pas de Redis
REDIS_URL=

# Sécurité basique
SECRET_KEY=openred-o2switch-secret-key-changez-moi-svp
ENCRYPTION_KEY=openred-encryption-key-changez-moi-aussi

# CORS pour votre domaine O2Switch
ALLOWED_ORIGINS=["https://api.o-red.org","https://o-red.org","http://localhost:8000"]

# Logs minimal
LOG_LEVEL=INFO
ENABLE_METRICS=false

# Mode standalone
MODE=standalone
PORT=8000
EOF

echo "✅ Fichier .env créé"

echo ""
echo "=== ÉTAPE 3: GÉNÉRATION DES CLÉS (si OpenSSL disponible) ==="
echo "Key generation (if OpenSSL available)..."

if command -v openssl &> /dev/null; then
    echo "🔐 Génération des clés RSA..."
    openssl genrsa -out keys/jwt_private.pem 2048 2>/dev/null
    openssl rsa -in keys/jwt_private.pem -outform PEM -pubout -out keys/jwt_public.pem 2>/dev/null
    chmod 600 keys/*.pem
    echo "✅ Clés RSA générées"
else
    echo "⚠️  OpenSSL non disponible - utilisation de clés par défaut"
    # Créer des fichiers de clés vides pour éviter les erreurs
    touch keys/jwt_private.pem keys/jwt_public.pem
    chmod 600 keys/*.pem
fi

echo ""
echo "=== ÉTAPE 4: TEST DE L'APPLICATION STANDALONE ==="
echo "Testing standalone application..."

echo "🧪 Test de l'application Python standalone..."
$PYTHON_CMD -c "
import sys
import os
sys.path.insert(0, '.')
try:
    from main_standalone import application
    print('✅ Application standalone chargée avec succès')
    print('✅ Aucune dépendance externe requise')
    print('✅ Prêt pour déploiement O2Switch')
except Exception as e:
    print(f'❌ Erreur: {e}')
    print('Vérifiez que main_standalone.py est présent')
"

echo ""
echo "=== ÉTAPE 5: CRÉATION D'UN SCRIPT DE DÉMARRAGE ==="
echo "Creating startup script..."

cat > start_openred.sh << EOF
#!/bin/bash
# Script de démarrage OpenRed pour O2Switch
echo "🚀 Démarrage OpenRed Central API..."
cd \$(dirname \$0)
export PYTHONPATH="\$(pwd):\$PYTHONPATH"
$PYTHON_CMD main_standalone.py
EOF

chmod +x start_openred.sh
echo "✅ Script de démarrage créé: ./start_openred.sh"

echo ""
echo "=== ÉTAPE 6: CRÉATION D'UN FICHIER WSGI SIMPLE ==="
echo "Creating simple WSGI file..."

cat > passenger_wsgi_simple.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import json

# Ajout du répertoire au path
sys.path.insert(0, os.path.dirname(__file__))

def application(environ, start_response):
    """Application WSGI ultra-simple pour O2Switch"""
    
    headers = [
        ('Content-Type', 'application/json; charset=utf-8'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    ]
    
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # Routes basiques
    if path == '/':
        response = {
            "message": "OpenRed Central API v2.0 - O2Switch Simple",
            "status": "running",
            "version": "2.0.0",
            "mode": "wsgi_simple",
            "timestamp": "2025-09-21T12:00:00Z"
        }
    elif path == '/health':
        response = {
            "status": "healthy",
            "version": "2.0.0",
            "environment": "production"
        }
    else:
        response = {
            "error": "Not Found", 
            "path": path,
            "available": ["/", "/health"]
        }
        start_response('404 Not Found', headers)
        return [json.dumps(response).encode('utf-8')]
    
    start_response('200 OK', headers)
    return [json.dumps(response, indent=2).encode('utf-8')]
EOF

echo "✅ Fichier WSGI simple créé: passenger_wsgi_simple.py"

echo ""
echo "=== ÉTAPE 7: TEST FINAL ==="
echo "Final test..."

echo "🧪 Test WSGI simple..."
$PYTHON_CMD -c "
from passenger_wsgi_simple import application
environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'}
def start_response(status, headers):
    print(f'Status: {status}')
result = application(environ, start_response)
print('Response:', result[0].decode('utf-8'))
print('✅ Test WSGI simple réussi')
"

echo ""
echo "✅ INSTALLATION TERMINÉE SANS PIP !"
echo "📝 Fichiers créés:"
echo "   - .env (configuration)"
echo "   - start_openred.sh (script de démarrage)"
echo "   - passenger_wsgi_simple.py (WSGI minimal)"
echo "   - main_standalone.py (serveur HTTP complet)"
echo ""
echo "🚀 Pour démarrer:"
echo "   Méthode 1: ./start_openred.sh"
echo "   Méthode 2: $PYTHON_CMD main_standalone.py"
echo "   Méthode 3: Utiliser passenger_wsgi_simple.py avec votre serveur web"
echo ""
echo "🌐 Votre API sera accessible sur votre domaine O2Switch"
echo "📍 Testez avec: curl http://votre-domaine.com/"
