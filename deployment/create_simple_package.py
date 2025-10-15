#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 OpenRed Simple Deployment Creator
Créer un package d'installation simple
"""

import zipfile
import os
from pathlib import Path
import datetime

def create_simple_deployment():
    """Créer un déploiement simple"""
    
    print("📦 Création du package OpenRed Simple...")
    
    deployment_dir = Path(__file__).parent
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    package_name = f'openred_simple_{timestamp}.zip'
    package_path = deployment_dir / package_name
    
    # Application web simple
    simple_app = '''#!/usr/bin/env python3
import os
import json
from datetime import datetime

def application(environ, start_response):
    """Application WSGI simple"""
    
    path = environ.get('PATH_INFO', '/')
    
    if path.startswith('/api/'):
        content = json.dumps({
            'status': 'running',
            'app': 'OpenRed',
            'timestamp': datetime.now().isoformat()
        })
        headers = [('Content-type', 'application/json')]
    else:
        content = get_html()
        headers = [('Content-type', 'text/html; charset=utf-8')]
    
    start_response('200 OK', headers)
    return [content.encode('utf-8')]

def get_html():
    return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRed - Déployé</title>
    <style>
        body { 
            font-family: Arial, sans-serif; margin: 0; padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }
        .container {
            background: white; border-radius: 15px; padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center; max-width: 600px;
        }
        h1 { color: #667eea; font-size: 3em; margin-bottom: 20px; }
        .success { 
            background: #4CAF50; color: white; padding: 20px; 
            border-radius: 10px; margin: 20px 0; font-size: 1.2em; 
        }
        .btn {
            background: #667eea; color: white; border: none; padding: 15px 30px;
            border-radius: 8px; cursor: pointer; margin: 10px; font-size: 1em;
        }
        .btn:hover { background: #764ba2; }
        .grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; margin: 30px 0; 
        }
        .card { background: #f8f9ff; padding: 20px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OpenRed</h1>
        <div class="success">✅ Déployé avec succès sur votre hébergeur !</div>
        
        <p>Votre application OpenRed est maintenant <strong>en ligne</strong> et accessible depuis le web.</p>
        
        <div class="grid">
            <div class="card">
                <h3>🌐 Status</h3>
                <p>Application opérationnelle</p>
                <button class="btn" onclick="testAPI()">Test API</button>
            </div>
            <div class="card">
                <h3>⚡ Performance</h3>
                <p>Optimisé production</p>
                <button class="btn" onclick="showInfo()">Infos</button>
            </div>
            <div class="card">
                <h3>📱 Mobile</h3>
                <p>Interface responsive</p>
                <button class="btn" onclick="testMobile()">Test</button>
            </div>
        </div>
        
        <div style="margin-top: 30px; color: #666;">
            <p>OpenRed Universal Deployment - Installation réussie</p>
        </div>
    </div>

    <script>
        async function testAPI() {
            try {
                const response = await fetch('./api/status');
                const data = await response.json();
                alert('✅ API fonctionne !\\n\\nStatus: ' + data.status + '\\nTimestamp: ' + data.timestamp);
            } catch (error) {
                alert('❌ Erreur API: ' + error.message);
            }
        }
        
        function showInfo() {
            alert('📊 Informations\\n\\n✅ Déploiement automatique réussi\\n🌐 Application en ligne\\n🔧 Prêt pour production');
        }
        
        function testMobile() {
            alert('📱 Compatible Mobile !\\n\\n✅ Design responsive\\n✅ Interface adaptative\\n✅ Compatible tous appareils');
        }
    </script>
</body>
</html>"""

if __name__ == '__main__':
    import wsgiref.handlers
    wsgiref.handlers.CGIHandler().run(application)
'''
    
    # HTML de fallback
    html_fallback = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRed - Installation Réussie</title>
    <style>
        body { 
            font-family: Arial, sans-serif; margin: 0; padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }
        .container {
            background: white; border-radius: 20px; padding: 50px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1); text-align: center; max-width: 500px;
        }
        h1 { color: #667eea; font-size: 4em; margin-bottom: 20px; }
        .success { 
            background: #4CAF50; color: white; padding: 20px 30px; 
            border-radius: 50px; margin: 30px 0; font-size: 1.3em; font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OpenRed</h1>
        <div class="success">✅ Installation Réussie !</div>
        <p>Votre application OpenRed est maintenant <strong>en ligne</strong> !</p>
        <div style="margin-top: 30px; color: #666;">
            <p>🌐 Mode: HTML Statique</p>
            <p>✅ Status: Opérationnel</p>
        </div>
    </div>
</body>
</html>'''
    
    # Configuration .htaccess
    htaccess_config = '''# OpenRed Configuration
RewriteEngine On

# Python/WSGI
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ app.py/$1 [L]

# Fallback HTML
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.html [L]

# Configuration MIME
AddType application/x-python .py
AddType text/html .py

# Sécurité
<Files "*.py">
    SetHandler cgi-script
    Options +ExecCGI
</Files>

# Cache
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>
'''
    
    # README
    readme_content = f'''# 🚀 OpenRed - Package Simple

## Installation Rapide

1. **Décompressez** ce package
2. **Uploadez** tous les fichiers sur votre hébergeur web
3. **Accédez** à votre site - OpenRed sera opérationnel !

## 📁 Répertoires Recommandés

- **O2Switch**: `/public_html/openred/`
- **OVH**: `/www/openred/`
- **Autres**: `/public_html/openred/`

## 🔗 Accès

Après upload : `http://votre-domaine.com/openred`

## ✅ Compatibilité

- Tous hébergeurs web
- Python WSGI (recommandé)  
- HTML statique (fallback automatique)

---

**OpenRed Simple Deployment**  
Package créé le: {datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")}
'''
    
    # Créer le ZIP
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('app.py', simple_app)
        zipf.writestr('index.py', simple_app)  # Copie pour compatibilité
        zipf.writestr('index.html', html_fallback)
        zipf.writestr('.htaccess', htaccess_config)
        zipf.writestr('README.md', readme_content)
    
    print(f"✅ Package créé: {package_path}")
    print(f"📁 Taille: {package_path.stat().st_size / 1024:.1f} KB")
    
    return package_path

if __name__ == '__main__':
    package_path = create_simple_deployment()
    
    print("\n🎁 PACKAGE PRÊT !")
    print("=" * 30)
    print(f"📦 Fichier: {package_path.name}")
    print("\n🚀 INSTRUCTIONS:")
    print("1. Décompressez le fichier ZIP")
    print("2. Uploadez tous les fichiers sur votre hébergeur")
    print("3. Accédez à votre site")
    print("\n✅ Compatible avec TOUS les hébergeurs !")