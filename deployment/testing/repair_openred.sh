#!/bin/bash
# 🔧 OpenRed REPAIR - Création des fichiers manquants
# Répare l'installation OpenRed sur votre serveur

echo "🔧 OpenRed REPAIR - Réparation de l'installation"
echo "==============================================="

# 1. Créer le serveur simple manquant
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
            self.send_api_response({'status': 'online', 'server': 'OpenRed Simple', 'version': '1.0'})
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
            self.send_api_response({'users': list(users.keys()), 'count': len(users)})
        elif self.path == '/api/health':
            self.send_api_response({'status': 'healthy', 'timestamp': datetime.datetime.now().isoformat()})
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
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if len(username) < 3 or len(password) < 6:
            self.send_api_response({'success': False, 'error': 'Username >= 3 chars, password >= 6 chars'})
            return
        
        users = self.load_users()
        
        if username in users:
            # Vérification password
            if users[username].get('password') == password:
                session_token = str(uuid.uuid4())
                users[username]['last_login'] = datetime.datetime.now().isoformat()
                users[username]['session_token'] = session_token
                self.save_users(users)
                
                self.send_api_response({
                    'success': True,
                    'message': 'Connexion réussie',
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
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if len(username) < 3:
            self.send_api_response({'success': False, 'error': 'Nom d\'utilisateur doit faire au moins 3 caractères'})
            return
        
        if len(password) < 6:
            self.send_api_response({'success': False, 'error': 'Mot de passe doit faire au moins 6 caractères'})
            return
        
        users = self.load_users()
        
        if username in users:
            self.send_api_response({'success': False, 'error': 'Nom d\'utilisateur déjà pris'})
            return
        
        # Créer le nouvel utilisateur
        session_token = str(uuid.uuid4())
        users[username] = {
            'password': password,  # À hasher en production !
            'created_at': datetime.datetime.now().isoformat(),
            'session_token': session_token,
            'profile': {
                'display_name': username,
                'bio': 'Nouveau membre OpenRed',
                'status': 'online',
                'privacy': 'private'
            }
        }
        
        self.save_users(users)
        
        self.send_api_response({
            'success': True,
            'message': 'Compte créé avec succès',
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
            self.send_api_response({'success': False, 'error': 'Session expirée, reconnectez-vous'}, 401)
            return
        
        # Mise à jour du profil
        if 'profile' in data:
            users[user_found]['profile'].update(data['profile'])
            self.save_users(users)
            
            self.send_api_response({
                'success': True,
                'message': 'Profil mis à jour',
                'profile': users[user_found]['profile']
            })
        else:
            self.send_api_response({
                'success': True,
                'profile': users[user_found]['profile']
            })
    
    def load_users(self):
        """Charger les utilisateurs depuis le fichier"""
        users_file = 'data/users/users.json'
        if os.path.exists(users_file):
            try:
                with open(users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self, users):
        """Sauvegarder les utilisateurs"""
        users_file = 'data/users/users.json'
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    
    def send_api_response(self, data, status=200):
        """Envoyer une réponse API JSON"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.wfile.write(response)
    
    def do_OPTIONS(self):
        """Gestion CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Log des requêtes"""
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {format % args}")

def main():
    PORT = 8000
    
    print(f"🌐 OpenRed Simple Server - Démarrage")
    print(f"===================================")
    print(f"🚀 Serveur: http://localhost:{PORT}")
    print(f"🔐 Interface: http://localhost:{PORT}/web/frontend/login.html")
    print(f"📊 API Status: http://localhost:{PORT}/api/status")
    print(f"👥 API Health: http://localhost:{PORT}/api/health")
    print(f"")
    print(f"🎯 OpenRed AUTHENTIQUE - Compatible hébergement mutualisé")
    print(f"💾 Données: ./data/users/users.json")
    print(f"🔧 Ctrl+C pour arrêter")
    print(f"")
    
    try:
        with socketserver.TCPServer(("", PORT), OpenRedHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Serveur OpenRed arrêté proprement")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} déjà utilisé. Essayez un autre port ou arrêtez le processus existant.")
        else:
            print(f"❌ Erreur serveur: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    main()
EOF

echo "✅ Serveur simple_openred_server.py créé"

# 2. Créer le script de lancement
cat > launch_openred.sh << 'EOF'
#!/bin/bash
# Lancement OpenRed Simple Server

echo "🌐 Lancement OpenRed Platform..."
echo "==============================="

# Aller dans le bon répertoire
cd "$(dirname "$0")"

# Vérifier que le serveur existe
if [ ! -f "simple_openred_server.py" ]; then
    echo "❌ Fichier simple_openred_server.py manquant"
    echo "🔧 Exécutez d'abord le script de réparation"
    exit 1
fi

# Créer les dossiers de données si nécessaire
mkdir -p data/users data/profiles data/messages

# Lancer le serveur
echo "🚀 Démarrage du serveur OpenRed..."
python3 simple_openred_server.py
EOF

chmod +x launch_openred.sh
echo "✅ Script launch_openred.sh créé"

# 3. Créer un script de test rapide
cat > test_openred.sh << 'EOF'
#!/bin/bash
# Test rapide OpenRed

echo "🧪 Test OpenRed Platform"
echo "======================="

# Test du serveur en arrière-plan
python3 simple_openred_server.py &
SERVER_PID=$!

sleep 2

# Test API
echo "📡 Test API Status..."
if curl -s http://localhost:8000/api/status | grep -q "online"; then
    echo "✅ API fonctionne"
else
    echo "❌ API ne répond pas"
fi

# Arrêter le serveur de test
kill $SERVER_PID 2>/dev/null

echo "🎯 Test terminé"
EOF

chmod +x test_openred.sh
echo "✅ Script test_openred.sh créé"

# 4. Vérifications finales
echo ""
echo "🔧 Configuration des permissions..."
chmod 755 *.sh 2>/dev/null
chmod 644 *.py 2>/dev/null

echo ""
echo "🎉 Réparation OpenRed terminée !"
echo "==============================="
echo ""
echo "📁 Fichiers créés :"
echo "  ✅ simple_openred_server.py - Serveur principal"
echo "  ✅ launch_openred.sh - Script de lancement"
echo "  ✅ test_openred.sh - Test rapide"
echo ""
echo "🚀 Pour démarrer OpenRed :"
echo "  ./launch_openred.sh"
echo ""
echo "🧪 Pour tester :"
echo "  ./test_openred.sh"
echo ""
echo "🌐 Interface sera disponible sur :"
echo "  http://votre-domaine.com:8000/web/frontend/login.html"