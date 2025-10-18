#!/bin/bash
# 🌐 OpenRed AUTHENTIC Platform - Installation CORRIGÉE
# Version corrigée pour hébergement mutualisé

echo "🌐 OpenRed AUTHENTIC Platform - Installation CORRIGÉE"
echo "===================================================="
echo "🎯 Déploiement du VRAI système OpenRed"
echo "🔧 Version CORRIGÉE pour hébergements mutualisés"
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

echo "🔧 Configuration pour hébergement mutualisé..."

# Créer les dossiers nécessaires
mkdir -p data/users data/profiles data/messages data/sessions
chmod 755 data data/users data/profiles data/messages data/sessions

echo "📝 Création du serveur OpenRed..."

# Créer le serveur Python (CORRECT cette fois !)
python3 << 'PYTHON_END'
import os

server_code = '''#!/usr/bin/env python3
"""
OpenRed Simple Server - Compatible hébergement mutualisé
Version corrigée avec gestion propre des fichiers
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import uuid
import datetime

class OpenRedHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=".", **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/web/frontend/login.html'
        elif self.path == '/api/status':
            self.send_api_response({'status': 'online', 'server': 'OpenRed'})
            return
        elif self.path.startswith('/api/'):
            self.handle_api_get()
            return
        super().do_GET()
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api_post()
        else:
            self.send_error(404)
    
    def handle_api_get(self):
        if self.path == '/api/users':
            users = self.load_users()
            self.send_api_response({'users': list(users.keys())})
        else:
            self.send_api_response({'error': 'API endpoint not found'}, 404)
    
    def handle_api_post(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
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
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if len(username) < 3 or len(password) < 6:
            self.send_api_response({'success': False, 'error': 'Username >= 3 chars, password >= 6 chars'})
            return
        
        users = self.load_users()
        
        if username in users and users[username].get('password') == password:
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
            self.send_api_response({'success': False, 'error': 'Login failed'})
    
    def handle_register(self, data):
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if len(username) < 3 or len(password) < 6:
            self.send_api_response({'success': False, 'error': 'Username >= 3 chars, password >= 6 chars'})
            return
        
        users = self.load_users()
        
        if username in users:
            self.send_api_response({'success': False, 'error': 'Username already taken'})
            return
        
        session_token = str(uuid.uuid4())
        users[username] = {
            'password': password,
            'created_at': datetime.datetime.now().isoformat(),
            'session_token': session_token,
            'profile': {
                'display_name': username,
                'bio': 'New OpenRed member',
                'status': 'online',
                'privacy': 'private'
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
        token = data.get('token', '')
        users = self.load_users()
        
        user_found = None
        for username, user_data in users.items():
            if user_data.get('session_token') == token:
                user_found = username
                break
        
        if not user_found:
            self.send_api_response({'success': False, 'error': 'Invalid token'}, 401)
            return
        
        if 'profile' in data:
            users[user_found]['profile'].update(data['profile'])
            self.save_users(users)
        
        self.send_api_response({
            'success': True,
            'profile': users[user_found]['profile']
        })
    
    def load_users(self):
        users_file = 'data/users/users.json'
        if os.path.exists(users_file):
            try:
                with open(users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self, users):
        users_file = 'data/users/users.json'
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    
    def send_api_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.wfile.write(response)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    PORT = 8000
    
    print("🌐 OpenRed Server Starting...")
    print(f"🚀 Server: http://localhost:{PORT}")
    print(f"🔐 Interface: http://localhost:{PORT}/web/frontend/login.html")
    print("🎯 Press Ctrl+C to stop")
    
    try:
        with socketserver.TCPServer(("", PORT), OpenRedHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
'''

with open('simple_openred_server.py', 'w', encoding='utf-8') as f:
    f.write(server_code)

print("✅ Serveur OpenRed créé avec succès")
PYTHON_END

chmod +x simple_openred_server.py

# Créer le script de lancement (CORRECT)
cat > launch_openred.sh << 'LAUNCH_END'
#!/bin/bash
echo "🌐 Lancement OpenRed Platform..."
cd "$(dirname "$0")"
mkdir -p data/users
python3 simple_openred_server.py
LAUNCH_END

chmod +x launch_openred.sh

echo "🔧 Configuration finale..."
find . -name "*.py" -exec chmod 644 {} \;
find . -name "*.html" -exec chmod 644 {} \;
find . -name "*.sh" -exec chmod 755 {} \;

echo ""
echo "🎉 OpenRed AUTHENTIQUE installé correctement !"
echo "=============================================="
echo ""
echo "✅ Fichiers créés correctement :"
echo "  📄 simple_openred_server.py"
echo "  🚀 launch_openred.sh"
echo "  📁 Dossiers de données"
echo ""
echo "🚀 LANCEMENT :"
echo "  ./launch_openred.sh"
echo ""
echo "🔗 ACCÈS :"
echo "  Interface: http://votre-domaine.com:8000/web/frontend/login.html"
echo "  API: http://votre-domaine.com:8000/api/status"
echo ""
echo "🎯 Installation CORRIGÉE - Plus d'erreurs de fichiers !"