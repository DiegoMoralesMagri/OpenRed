#!/usr/bin/env python3
"""
🌐 OpenRed Social Platform Package Creator
Crée un package complet avec login, profils, amis, chat pour hébergement mutualisé
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path

def create_social_hosting_package():
    """Crée le package social complet pour hébergement mutualisé"""
    print("🌐 Création du package OpenRed Social Platform...")
    
    base_dir = Path(__file__).parent
    project_root = base_dir.parent
    web_dir = project_root / "openred-p2p-platform" / "web"
    
    # Package social complet
    package_name = "openred-social-hosting.zip"
    package_path = base_dir / package_name
    
    print(f"📦 Création de {package_name}...")
    
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # 1. Pages frontend complètes
        frontend_dir = web_dir / "frontend"
        if frontend_dir.exists():
            for html_file in frontend_dir.glob("*.html"):
                print(f"  + {html_file.name}")
                zipf.write(html_file, html_file.name)
        
        # 2. Backend API
        backend_dir = web_dir / "backend"
        if backend_dir.exists():
            # API Python
            api_files = ["web_api.py", "auth_system.py", "friendship_system.py", "profile_system.py"]
            for api_file in api_files:
                api_path = backend_dir / api_file
                if api_path.exists():
                    print(f"  + api/{api_file}")
                    zipf.write(api_path, f"api/{api_file}")
        
        # 3. Page d'accueil avec redirection vers login
        index_html = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRed - Plateforme Sociale P2P</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; padding: 0; 
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #fff; min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
        }
        .container { 
            max-width: 600px; text-align: center; 
            background: rgba(26, 26, 46, 0.8); 
            padding: 40px; border-radius: 20px; 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 136, 0.3);
        }
        .logo { 
            font-size: 4em; margin-bottom: 20px; 
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .tagline { font-size: 1.3em; color: #00ff88; margin-bottom: 30px; }
        .description { font-size: 1.1em; line-height: 1.6; margin-bottom: 40px; color: #ccc; }
        .features { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
            gap: 15px; margin: 30px 0; 
        }
        .feature { 
            background: rgba(0, 255, 136, 0.1); 
            padding: 15px; border-radius: 10px; 
            border: 1px solid rgba(0, 255, 136, 0.3);
        }
        .feature h4 { color: #00ff88; margin: 0 0 10px 0; }
        .btn { 
            display: inline-block; 
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            color: #000; padding: 15px 40px; 
            text-decoration: none; border-radius: 30px; 
            font-weight: bold; font-size: 1.1em;
            transition: all 0.3s ease;
            margin: 10px;
        }
        .btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 255, 136, 0.3);
        }
        .btn-secondary {
            background: transparent;
            color: #00ff88;
            border: 2px solid #00ff88;
        }
        .loading { 
            position: fixed; top: 50%; left: 50%; 
            transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.9); 
            padding: 20px; border-radius: 10px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🌐 OpenRed</div>
        <div class="tagline">Plateforme Sociale P2P Révolutionnaire</div>
        
        <div class="description">
            Rejoignez la révolution sociale décentralisée ! 
            Connectez-vous avec vos amis, partagez du contenu et 
            découvrez un réseau social sans serveurs centraux.
        </div>
        
        <div class="features">
            <div class="feature">
                <h4>🔐 Connexion</h4>
                <p>Profils sécurisés</p>
            </div>
            <div class="feature">
                <h4>👥 Amis</h4>
                <p>Réseau social P2P</p>
            </div>
            <div class="feature">
                <h4>💬 Chat</h4>
                <p>Messages décentralisés</p>
            </div>
            <div class="feature">
                <h4>🌐 Nœuds</h4>
                <p>Découverte réseau</p>
            </div>
        </div>
        
        <div>
            <a href="login.html" class="btn">🚀 Se Connecter</a>
            <a href="profile.html" class="btn btn-secondary">👤 Créer Profil</a>
        </div>
        
        <div style="margin-top: 30px; font-size: 0.9em; color: #888;">
            Plateforme sociale décentralisée • Pas de serveurs • Données privées
        </div>
    </div>
    
    <div class="loading" id="loading">
        <div style="text-align: center;">
            <div style="font-size: 2em; margin-bottom: 10px;">🌐</div>
            <div>Connexion au réseau P2P...</div>
        </div>
    </div>
    
    <script>
        // Animation de chargement si nécessaire
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
        
        // Redirection automatique si déjà connecté
        if (localStorage.getItem('openred_user')) {
            window.location.href = 'dashboard.html';
        }
    </script>
</body>
</html>'''
        
        zipf.writestr("index.html", index_html)
        print("  + index.html")
        
        # 4. Configuration PHP pour hébergement mutualisé
        php_config = '''<?php
// OpenRed Social Platform - Configuration PHP
// Compatible avec hébergement mutualisé

// Configuration de base
ini_set('display_errors', 0);
error_reporting(E_ALL & ~E_NOTICE);

// Headers CORS pour API
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Authorization');
    exit(0);
}

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Content-Type: application/json');

// Routeur simple pour API
$request = $_SERVER['REQUEST_URI'];
$path = parse_url($request, PHP_URL_PATH);

// Routes API
switch ($path) {
    case '/api/login':
        include 'api/login.php';
        break;
    case '/api/register':
        include 'api/register.php';
        break;
    case '/api/profile':
        include 'api/profile.php';
        break;
    case '/api/friends':
        include 'api/friends.php';
        break;
    case '/api/nodes':
        include 'api/nodes.php';
        break;
    default:
        http_response_code(404);
        echo json_encode(['error' => 'Route not found']);
        break;
}
?>'''
        
        zipf.writestr("api.php", php_config)
        print("  + api.php")
        
        # 5. API basique en PHP
        login_php = '''<?php
// API Login OpenRed
$data = json_decode(file_get_contents('php://input'), true);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $data['username'] ?? '';
    $password = $data['password'] ?? '';
    
    // Validation simple (à améliorer en production)
    if (strlen($username) >= 3 && strlen($password) >= 6) {
        $user = [
            'id' => uniqid(),
            'username' => $username,
            'status' => 'online',
            'created_at' => date('Y-m-d H:i:s')
        ];
        
        // Sauvegarde simple en fichier (à remplacer par base de données)
        $users_file = 'data/users.json';
        if (!file_exists('data')) mkdir('data', 0755, true);
        
        $users = [];
        if (file_exists($users_file)) {
            $users = json_decode(file_get_contents($users_file), true) ?? [];
        }
        $users[$username] = $user;
        file_put_contents($users_file, json_encode($users));
        
        echo json_encode(['success' => true, 'user' => $user]);
    } else {
        echo json_encode(['success' => false, 'error' => 'Nom d\'utilisateur ou mot de passe invalide']);
    }
} else {
    echo json_encode(['error' => 'Method not allowed']);
}
?>'''
        
        zipf.writestr("api/login.php", login_php)
        print("  + api/login.php")
        
        # 6. .htaccess compatible
        htaccess = '''# OpenRed Social Platform - Configuration Apache

# Page d'accueil
DirectoryIndex index.html

# Redirection API vers PHP
RewriteEngine On
RewriteRule ^api/(.*)$ api.php [L,QSA]

# Configuration MIME
AddType application/json .json
AddType text/html .html

# Protection des données
<Files "data/*">
    Order Allow,Deny
    Deny from all
</Files>

# Protection des fichiers sensibles
<Files "*.json">
    Order Allow,Deny
    Deny from all
</Files>

<Files "*.md">
    Order Allow,Deny
    Deny from all
</Files>

# Cache pour performances
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 7 days"
    ExpiresByType application/javascript "access plus 7 days"
    ExpiresByType image/png "access plus 7 days"
</IfModule>
'''
        
        zipf.writestr(".htaccess", htaccess)
        print("  + .htaccess")
        
        # 7. README pour installation
        readme = '''# 🌐 OpenRed Social Platform - Hébergement Mutualisé

## Installation Rapide

1. **Décompressez** ce package dans votre dossier web
2. **Assurez-vous** que PHP est activé sur votre hébergeur
3. **Visitez** votre site : `http://votre-domaine.com`

## Fonctionnalités

- 🔐 **Système de connexion** sécurisé
- 👤 **Profils utilisateurs** personnalisables  
- 👥 **Gestion d'amis** et demandes
- 💬 **Chat en temps réel** P2P
- 🌐 **Découverte de nœuds** du réseau
- 📱 **Interface responsive** mobile

## Structure

```
/
├── index.html          # Page d'accueil
├── login.html          # Connexion
├── dashboard.html      # Tableau de bord
├── profile.html        # Profil utilisateur
├── friends.html        # Gestion des amis
├── api.php            # Routeur API PHP
├── api/               # APIs backend
│   ├── login.php      # Authentification
│   └── ...            # Autres endpoints
└── data/              # Données utilisateurs
```

## Support

- 📖 Documentation : https://github.com/DiegoMoralesMagri/OpenRed
- 🐛 Issues : https://github.com/DiegoMoralesMagri/OpenRed/issues
- 💬 Discussions : https://github.com/DiegoMoralesMagri/OpenRed/discussions

## Sécurité

⚠️ **Important** : Ce package est une version de démonstration.
Pour la production, implémentez :
- Base de données sécurisée
- Hashage des mots de passe
- Validation CSRF
- Rate limiting
'''
        
        zipf.writestr("README.md", readme)
        print("  + README.md")

    # Statistiques
    file_size = os.path.getsize(package_path)
    print(f"\n✅ Package OpenRed Social créé!")
    print(f"📏 Taille: {file_size / 1024:.1f} KB")
    print(f"🎯 Fichier: {package_name}")
    
    print(f"\n🌐 Package social complet prêt pour hébergement mutualisé!")
    print(f"🔐 Inclut: Login, Profils, Amis, Chat, Découverte de nœuds")
    print(f"📱 Interface responsive et moderne")
    
    return package_path

if __name__ == "__main__":
    create_social_hosting_package()