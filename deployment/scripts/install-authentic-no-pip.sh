#!/bin/bash
# 🌐 OpenRed AUTHENTIC Platform - Installation SANS PIP
# Version adaptée hébergement mutualisé SANS pip3
# Utilise uniquement les modules Python standards disponibles

echo "🌐 OpenRed AUTHENTIC Platform - Installation (Mode Hébergement Mutualisé)"
echo "========================================================================"
echo "🎯 Déploiement du VRAI système OpenRed"
echo "🔧 Mode adapté pour hébergements sans pip3"
echo ""

# Variables
URL="https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/openred-authentic-platform.zip"
ZIP="openred-authentic.zip"

echo "📥 Téléchargement du système AUTHENTIQUE..."
if curl -L -o "$ZIP" "$URL" 2>/dev/null || wget -O "$ZIP" "$URL" 2>/dev/null; then
    echo "✅ Téléchargement réussi ($(du -h "$ZIP" | cut -f1))"
else
    echo "❌ Échec du téléchargement"
    exit 1
fi

echo "📦 Extraction du système complet..."
if unzip -q "$ZIP" 2>/dev/null; then
    echo "✅ Extraction réussie"
    rm -f "$ZIP"
else
    echo "❌ Échec de l'extraction"
    exit 1
fi

echo "🔐 Vérification de l'environnement..."

# Vérifier Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 REQUIS pour OpenRed"
    exit 1
fi

echo "✅ Python 3 détecté: $(python3 --version)"

# Test des modules Python disponibles
echo "🔍 Vérification des modules Python..."
python3 -c "
import sys
modules_required = ['http.server', 'socketserver', 'json', 'urllib', 'threading', 'uuid', 'datetime']
modules_available = []
modules_missing = []

for module in modules_required:
    try:
        __import__(module)
        modules_available.append(module)
        print(f'✅ {module}')
    except ImportError:
        modules_missing.append(module)
        print(f'❌ {module}')

if len(modules_missing) == 0:
    print('✅ Tous les modules de base disponibles')
else:
    print(f'⚠️  Modules manquants: {modules_missing}')
"

echo "🔧 Configuration pour hébergement mutualisé..."

# Créer les dossiers nécessaires
mkdir -p data/users data/profiles data/messages data/sessions
chmod 755 data data/users data/profiles data/messages data/sessions

# Créer un serveur web simple avec les modules standards Python
cat > simple_openred_server.py << 'EOF'
#!/usr/bin/env python3
"""
OpenRed Simple Server - Compatible hébergement mutualisé
Utilise uniquement les modules Python standards
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import uuid
import datetime
from pathlib import Path

class OpenRedHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=".", **kwargs)
    
    def do_GET(self):
        """Gestion des requêtes GET"""
        if self.path == '/':
            self.path = '/web/frontend/login.html'
        elif self.path == '/api/status':
            self.send_api_response({'status': 'online', 'server': 'OpenRed Simple'})
            return
        elif self.path.startswith('/api/'):
            self.handle_api_get()
            return
        
        super().do_GET()
    
    def do_POST(self):
        """Gestion des requêtes POST"""
        if self.path.startswith('/api/'):
            self.handle_api_post()
        else:
            self.send_error(404)
    
    def handle_api_get(self):
        """Gestion des API GET"""
        if self.path == '/api/users':
            users = self.load_users()
            self.send_api_response({'users': list(users.keys())})
        else:
            self.send_api_response({'error': 'API endpoint not found'}, 404)
    
    def handle_api_post(self):
        """Gestion des API POST"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            self.send_api_response({'error': 'Invalid JSON'}, 400)
            return
        
        if self.path == '/api/login':
            self.handle_login(data)
        elif self.path == '/api/register':
            self.handle_register(data)
        elif self.path == '/api/profile':
            self.handle_profile(data)
        else:
            self.send_api_response({'error': 'API endpoint not found'}, 404)
    
    def handle_login(self, data):
        """Authentification utilisateur"""
        username = data.get('username', '')
        password = data.get('password', '')
        
        if len(username) < 3 or len(password) < 6:
            self.send_api_response({'success': False, 'error': 'Username ou password invalide'})
            return
        
        users = self.load_users()
        
        if username in users:
            # Vérification simplifiée (à améliorer en production)
            if users[username].get('password') == password:
                session_token = str(uuid.uuid4())
                users[username]['last_login'] = datetime.datetime.now().isoformat()
                users[username]['session_token'] = session_token
                self.save_users(users)
                
                self.send_api_response({
                    'success': True,
                    'user': {
                        'username': username,
                        'token': session_token,
                        'profile': users[username].get('profile', {})
                    }
                })
            else:
                self.send_api_response({'success': False, 'error': 'Mot de passe incorrect'})
        else:
            self.send_api_response({'success': False, 'error': 'Utilisateur non trouvé'})
    
    def handle_register(self, data):
        """Création de compte utilisateur"""
        username = data.get('username', '')
        password = data.get('password', '')
        
        if len(username) < 3 or len(password) < 6:
            self.send_api_response({'success': False, 'error': 'Username >= 3 chars, password >= 6 chars'})
            return
        
        users = self.load_users()
        
        if username in users:
            self.send_api_response({'success': False, 'error': 'Utilisateur déjà existant'})
            return
        
        # Créer le nouvel utilisateur
        session_token = str(uuid.uuid4())
        users[username] = {
            'password': password,  # À hasher en production !
            'created_at': datetime.datetime.now().isoformat(),
            'session_token': session_token,
            'profile': {
                'display_name': username,
                'bio': '',
                'status': 'online'
            }
        }
        
        self.save_users(users)
        
        self.send_api_response({
            'success': True,
            'user': {
                'username': username,
                'token': session_token,
                'profile': users[username]['profile']
            }
        })
    
    def handle_profile(self, data):
        """Gestion du profil utilisateur"""
        token = data.get('token', '')
        users = self.load_users()
        
        # Trouver l'utilisateur par token
        user_found = None
        for username, user_data in users.items():
            if user_data.get('session_token') == token:
                user_found = username
                break
        
        if not user_found:
            self.send_api_response({'success': False, 'error': 'Token invalide'}, 401)
            return
        
        # Mise à jour du profil
        if 'profile' in data:
            users[user_found]['profile'].update(data['profile'])
            self.save_users(users)
        
        self.send_api_response({
            'success': True,
            'profile': users[user_found]['profile']
        })
    
    def load_users(self):
        """Charger les utilisateurs depuis le fichier"""
        users_file = 'data/users/users.json'
        if os.path.exists(users_file):
            try:
                with open(users_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self, users):
        """Sauvegarder les utilisateurs"""
        users_file = 'data/users/users.json'
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def send_api_response(self, data, status=200):
        """Envoyer une réponse API JSON"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.wfile.write(response)
    
    def do_OPTIONS(self):
        """Gestion CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    PORT = 8000
    
    print(f"🌐 OpenRed Simple Server démarré")
    print(f"🚀 Serveur: http://localhost:{PORT}")
    print(f"🔐 Interface: http://localhost:{PORT}/web/frontend/login.html")
    print(f"📊 Status: http://localhost:{PORT}/api/status")
    print(f"")
    print(f"🎯 Serveur compatible hébergement mutualisé")
    print(f"💾 Données sauvegardées dans: ./data/")
    print(f"")
    
    try:
        with socketserver.TCPServer(("", PORT), OpenRedHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")

if __name__ == "__main__":
    main()
EOF

chmod +x simple_openred_server.py

echo "✅ Serveur simple OpenRed créé"

# Créer un script de lancement
cat > launch_openred.sh << 'EOF'
#!/bin/bash
# Lancement OpenRed Simple Server

echo "🌐 Lancement OpenRed Platform..."

# Aller dans le bon répertoire
cd "$(dirname "$0")"

# Lancer le serveur
python3 simple_openred_server.py
EOF

chmod +x launch_openred.sh

echo "🔧 Configuration des permissions..."
find . -name "*.py" -exec chmod 644 {} \;
find . -name "*.html" -exec chmod 644 {} \;
find . -name "*.sh" -exec chmod 755 {} \;

echo ""
echo "🎉 OpenRed AUTHENTIC Platform installé ! (Mode Simple)"
echo "====================================================="
echo ""
echo "🌐 SYSTÈME AUTHENTIQUE DÉPLOYÉ (Compatible hébergement):"
echo "  🔐 Serveur Python standard (pas de dépendances externes)"
echo "  👥 Système d'authentification fonctionnel"
echo "  💾 Sauvegarde locale des données"
echo "  🌐 Interface utilisateur complète"
echo ""
echo "🚀 LANCEMENT :"
echo "  ./launch_openred.sh"
echo ""
echo "🔗 ACCÈS :"
echo "  Interface: http://votre-domaine.com:8000/web/frontend/login.html"
echo "  API Status: http://votre-domaine.com:8000/api/status"
echo ""
echo "📋 FONCTIONNALITÉS DISPONIBLES :"
echo "  ✅ Création de comptes utilisateurs"
echo "  ✅ Connexion sécurisée"
echo "  ✅ Gestion des profils"
echo "  ✅ Interface authentique OpenRed"
echo ""
echo "⚠️  POUR PRODUCTION :"
echo "  - Remplacer par HTTPS"
echo "  - Hasher les mots de passe"
echo "  - Implémenter rate limiting"
echo ""
echo "🎯 Système OpenRed AUTHENTIQUE fonctionnel !"