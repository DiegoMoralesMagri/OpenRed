#!/usr/bin/env python3
"""
🚀 Setup OpenRed Distribution
Configure l'hébergement automatique des fichiers d'installation
"""

import os
import json
import zipfile
import tempfile
import requests
from pathlib import Path
import subprocess

class OpenRedDistribution:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.dist_dir = self.base_dir / "dist"
        self.releases_dir = self.base_dir / "releases"
        
    def create_directories(self):
        """Créer les répertoires nécessaires"""
        self.dist_dir.mkdir(exist_ok=True)
        self.releases_dir.mkdir(exist_ok=True)
        print("📁 Répertoires créés")
    
    def build_complete_package(self):
        """Construire le package complet OpenRed"""
        print("📦 Construction du package complet...")
        
        package_path = self.releases_dir / "openred-complete.zip"
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Ajouter les fichiers principaux
            files_to_include = [
                ("create_simple_package.py", "create_simple_package.py"),
                ("universal_installer.py", "universal_installer.py"),
                ("install_o2switch.py", "install_o2switch.py"),
                ("INSTALLATION_GUIDE.md", "INSTALLATION_GUIDE.md")
            ]
            
            for src, dst in files_to_include:
                src_path = self.base_dir / src
                if src_path.exists():
                    zf.write(src_path, dst)
                    print(f"  ✅ {src}")
            
            # Créer l'application principale
            app_content = '''#!/usr/bin/env python3
import os
import json
from datetime import datetime
from http.server import HTTPServer, CGIHTTPRequestHandler
import socketserver

def application(environ, start_response):
    """Application WSGI OpenRed"""
    content = get_dashboard()
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response('200 OK', headers)
    return [content.encode('utf-8')]

def get_dashboard():
    return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRed - Production</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; padding: 20px; min-height: 100vh;
        }
        .container { 
            max-width: 800px; margin: 0 auto; 
            background: rgba(255,255,255,0.95); 
            border-radius: 15px; padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 { 
            text-align: center; font-size: 3.5em; margin-bottom: 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .success { 
            background: #4CAF50; color: white; padding: 20px; 
            border-radius: 10px; text-align: center; font-size: 1.2em;
            margin-bottom: 30px;
        }
        .grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; margin: 30px 0; 
        }
        .card { 
            background: #f8f9ff; padding: 25px; border-radius: 10px; 
            border-left: 4px solid #667eea; text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OpenRed</h1>
        <div class="success">✅ Installation automatique réussie !</div>
        <p style="text-align: center; font-size: 1.2em;">
            Votre application OpenRed est maintenant <strong>en ligne</strong> et opérationnelle.
        </p>
        <div class="grid">
            <div class="card">
                <h3>🌐 Status</h3>
                <p>Application en ligne</p>
            </div>
            <div class="card">
                <h3>⚡ Performance</h3>
                <p>Optimisé production</p>
            </div>
            <div class="card">
                <h3>🔒 Sécurité</h3>
                <p>Configuration sécurisée</p>
            </div>
            <div class="card">
                <h3>📱 Mobile</h3>
                <p>Interface responsive</p>
            </div>
        </div>
    </div>
</body>
</html>"""

if __name__ == '__main__':
    import wsgiref.handlers
    if os.environ.get('REQUEST_METHOD'):
        # Mode CGI
        wsgiref.handlers.CGIHandler().run(application)
    else:
        # Mode serveur de développement
        from wsgiref.simple_server import make_server
        print("🚀 Démarrage d'OpenRed sur http://localhost:8000")
        print("Appuyez sur Ctrl+C pour arrêter")
        httpd = make_server('', 8000, application)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n✅ Serveur arrêté")
'''
            
            zf.writestr("app.py", app_content)
            
            # Page HTML de fallback
            html_content = '''<!DOCTYPE html>
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
            background: white; border-radius: 20px; padding: 60px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.15); text-align: center; max-width: 500px;
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
        <div class="success">✅ Installation One-Liner Réussie !</div>
        <p>Votre application OpenRed est maintenant <strong>en ligne</strong> !</p>
    </div>
</body>
</html>'''
            
            zf.writestr("index.html", html_content)
            
            # Configuration .htaccess
            htaccess_content = '''RewriteEngine On
DirectoryIndex app.py index.html

<Files "*.py">
    SetHandler cgi-script
    Options +ExecCGI
</Files>

RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ app.py/$1 [L]'''
            
            zf.writestr(".htaccess", htaccess_content)
            
            # Requirements
            requirements_content = '''flask>=2.0.0
requests>=2.25.0'''
            
            zf.writestr("requirements.txt", requirements_content)
        
        size = package_path.stat().st_size / 1024
        print(f"✅ Package complet créé: {package_path.name} ({size:.1f} KB)")
        return package_path
    
    def create_installer_urls(self):
        """Créer les URLs d'installation"""
        print("🌐 Configuration des URLs d'installation...")
        
        # Copier les scripts d'installation
        install_sh = self.dist_dir / "install.sh"
        install_ps1 = self.dist_dir / "install.ps1"
        
        # Copier depuis les fichiers sources
        (self.base_dir / "install-openred.sh").replace(install_sh)
        (self.base_dir / "install-openred.ps1").replace(install_ps1)
        
        print(f"✅ Scripts copiés vers {self.dist_dir}")
        
        return {
            "bash": str(install_sh),
            "powershell": str(install_ps1)
        }
    
    def setup_github_release(self):
        """Instructions pour GitHub Release"""
        print("📋 INSTRUCTIONS GITHUB RELEASE:")
        print("=" * 50)
        print()
        print("1. 🔧 Création de la release:")
        print("   - Allez sur GitHub.com/DiegoMoralesMagri/OpenRed")
        print("   - Cliquez sur 'Releases' puis 'Create a new release'")
        print("   - Tag: v1.0.0 (ou version suivante)")
        print("   - Titre: OpenRed v1.0.0 - Installation One-Liner")
        print()
        print("2. 📦 Fichiers à uploader:")
        package_path = self.releases_dir / "openred-complete.zip"
        if package_path.exists():
            print(f"   - {package_path} (comme openred-complete.zip)")
        print()
        print("3. 🌐 URLs finales qui seront disponibles:")
        print("   - Package: https://github.com/DiegoMoralesMagri/OpenRed/releases/latest/download/openred-complete.zip")
        print()
        print("4. 🚀 Commandes d'installation pour vos utilisateurs:")
        print()
        print("   Linux/macOS:")
        print("   curl -sSL https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/install-openred.sh | bash")
        print()
        print("   Windows PowerShell:")
        print("   iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/install-openred.ps1'))")
        print()
    
    def setup_github_pages(self):
        """Configuration GitHub Pages"""
        print("🌐 CONFIGURATION GITHUB PAGES:")
        print("=" * 40)
        
        # Créer index.html pour GitHub Pages
        pages_dir = self.base_dir / "docs"
        pages_dir.mkdir(exist_ok=True)
        
        index_content = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRed - Installation One-Liner</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; padding: 20px; min-height: 100vh;
        }
        .container { 
            max-width: 800px; margin: 0 auto; 
            background: rgba(255,255,255,0.95); 
            border-radius: 15px; padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 { 
            text-align: center; font-size: 3.5em; margin-bottom: 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .install-box { 
            background: #2d3748; color: #e2e8f0; padding: 25px; 
            border-radius: 10px; margin: 20px 0; font-family: 'Courier New', monospace;
            position: relative;
        }
        .copy-btn {
            position: absolute; top: 10px; right: 10px; 
            background: #4299e1; color: white; border: none; 
            padding: 5px 10px; border-radius: 5px; cursor: pointer;
        }
        .grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; margin: 30px 0; 
        }
        .card { 
            background: #f8f9ff; padding: 25px; border-radius: 10px; 
            border-left: 4px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 OpenRed</h1>
        <h2 style="text-align: center; color: #4a5568;">Installation One-Liner</h2>
        
        <p style="text-align: center; font-size: 1.2em; color: #2d3748;">
            Installez OpenRed en <strong>une seule commande</strong> sur n'importe quel hébergeur !
        </p>
        
        <div class="grid">
            <div class="card">
                <h3>🐧 Linux / macOS</h3>
                <div class="install-box">
                    <button class="copy-btn" onclick="copyToClipboard('bash-cmd')">Copier</button>
                    <code id="bash-cmd">curl -sSL https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/install-openred.sh | bash</code>
                </div>
            </div>
            
            <div class="card">
                <h3>🪟 Windows PowerShell</h3>
                <div class="install-box">
                    <button class="copy-btn" onclick="copyToClipboard('ps-cmd')">Copier</button>
                    <code id="ps-cmd">iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/DiegoMoralesMagri/OpenRed/main/deployment/install-openred.ps1'))</code>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 40px 0;">
            <h3>🌐 Compatible avec tous les hébergeurs</h3>
            <p>O2Switch • OVH • Hostinger • 1&1 • Gandi • VPS • Serveurs dédiés</p>
        </div>
        
        <div style="text-align: center; margin: 40px 0;">
            <a href="https://github.com/DiegoMoralesMagri/OpenRed" 
               style="background: #667eea; color: white; padding: 15px 30px; 
                      border-radius: 25px; text-decoration: none; font-weight: bold;">
                📚 Documentation GitHub
            </a>
        </div>
    </div>

    <script>
        function copyToClipboard(elementId) {
            const element = document.getElementById(elementId);
            const text = element.textContent;
            navigator.clipboard.writeText(text).then(() => {
                alert('✅ Commande copiée !');
            });
        }
    </script>
</body>
</html>'''
        
        with open(pages_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(index_content)
        
        print(f"✅ Page GitHub Pages créée: {pages_dir / 'index.html'}")
        print("📋 Pour activer GitHub Pages:")
        print("   1. Allez dans Settings > Pages de votre repo")
        print("   2. Source: Deploy from a branch")
        print("   3. Branch: main, Folder: /docs")
        print("   4. URL finale: https://diegomoralesmagri.github.io/OpenRed/")
        print()
    
    def create_custom_domain_setup(self):
        """Configuration domaine personnalisé"""
        print("🌐 CONFIGURATION DOMAINE PERSONNALISÉ:")
        print("=" * 45)
        
        # Créer un script Nginx pour serveur personnalisé
        nginx_config = '''server {
    listen 80;
    server_name install.openred.dev;
    
    # Redirection HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name install.openred.dev;
    
    # Certificats SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/install.openred.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/install.openred.dev/privkey.pem;
    
    root /var/www/openred-install;
    index index.html;
    
    # Script bash
    location = / {
        alias /var/www/openred-install/install-openred.sh;
        add_header Content-Type text/plain;
    }
    
    # Script PowerShell
    location = /install.ps1 {
        alias /var/www/openred-install/install-openred.ps1;
        add_header Content-Type text/plain;
    }
    
    # Page web
    location = /web {
        try_files /index.html =404;
    }
}'''
        
        nginx_file = self.dist_dir / "nginx-install.conf"
        with open(nginx_file, "w") as f:
            f.write(nginx_config)
        
        print(f"✅ Configuration Nginx créée: {nginx_file}")
        print()
        print("📋 Étapes pour domaine personnalisé:")
        print("   1. 🌐 Acheter un domaine (ex: install.openred.dev)")
        print("   2. 🖥️ Louer un VPS (DigitalOcean, OVH, etc.)")
        print("   3. 🔧 Installer Nginx sur le VPS")
        print("   4. 📁 Copier les fichiers dans /var/www/openred-install/")
        print("   5. 🔒 Configurer SSL avec Let's Encrypt")
        print("   6. 🚀 Commandes finales:")
        print("      curl -sSL https://install.openred.dev | bash")
        print("      iex ((New-Object System.Net.WebClient).DownloadString('https://install.openred.dev/install.ps1'))")
        print()
    
    def run(self):
        """Exécuter la configuration complète"""
        print("🚀 CONFIGURATION DISTRIBUTION OPENRED")
        print("=" * 50)
        print()
        
        self.create_directories()
        self.build_complete_package()
        self.create_installer_urls()
        
        print()
        print("📋 OPTIONS D'HÉBERGEMENT:")
        print("=" * 30)
        
        print("\n1. 🆓 GitHub (Recommandé - Gratuit)")
        self.setup_github_release()
        self.setup_github_pages()
        
        print("\n2. 🌐 Domaine personnalisé (Avancé)")
        self.create_custom_domain_setup()
        
        print("\n✅ CONFIGURATION TERMINÉE !")
        print("🎯 Choisissez l'option qui vous convient et suivez les instructions")

if __name__ == "__main__":
    distributor = OpenRedDistribution()
    distributor.run()