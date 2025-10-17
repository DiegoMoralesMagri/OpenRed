#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 Serveur Web OpenRed Network
Interface web pour accéder aux forts via navigateur standard
"""

import sys
import os

# Configuration pour Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Ajout du chemin du projet
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import json
import threading
import time
from urllib.parse import urlparse, parse_qs
import http.server
import socketserver
from typing import Dict, Any


class ServeurWebOpenRed:
    """
    🌐 Serveur web pour OpenRed Network
    Permet l'accès aux forts via navigateur standard
    """
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.serveur_actif = False
        self.thread_serveur = None
        
    def demarrer_serveur(self):
        """Démarre le serveur web"""
        try:
            print("🌐 Démarrage serveur web OpenRed Network...")
            print(f"🔗 Accès web: http://localhost:{self.port}")
            print("🌍 Interface accessible depuis n'importe quel navigateur")
            
            self.serveur_actif = True
            self.thread_serveur = threading.Thread(target=self._serveur_http)
            self.thread_serveur.daemon = True
            self.thread_serveur.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur démarrage serveur: {e}")
            return False
    
    def arreter_serveur(self):
        """Arrête le serveur web"""
        self.serveur_actif = False
        print("🛑 Serveur web arrêté")
    
    def _serveur_http(self):
        """Thread du serveur HTTP"""
        try:
            with socketserver.TCPServer(("", self.port), HandlerWeb) as httpd:
                httpd.serveur_parent = self
                print(f"✅ Serveur web actif sur port {self.port}")
                
                while self.serveur_actif:
                    httpd.handle_request()
                    
        except Exception as e:
            print(f"❌ Erreur serveur HTTP: {e}")


class HandlerWeb(http.server.BaseHTTPRequestHandler):
    """Handler pour les requêtes web"""
    
    def do_GET(self):
        """Traite les requêtes GET"""
        try:
            path = self.path
            
            # Page d'accueil
            if path == "/" or path == "/index.html":
                self._servir_page_accueil()
            
            # Accès à un fort spécifique
            elif path.startswith("/fort/"):
                fort_id = path.split("/fort/")[1].split("/")[0]
                self._servir_page_fort(fort_id)
            
            # API de statut
            elif path.startswith("/api/status/"):
                fort_id = path.split("/api/status/")[1]
                self._api_statut_fort(fort_id)
            
            # API de résolution
            elif path.startswith("/api/resolve/"):
                fort_id = path.split("/api/resolve/")[1]
                self._api_resoudre_fort(fort_id)
            
            # Ressources statiques
            elif path.startswith("/static/"):
                self._servir_statique(path)
            
            # Redirection URLs orp://
            elif path.startswith("/orp/"):
                url_orp = path.replace("/orp/", "orp://")
                self._traiter_url_orp(url_orp)
            
            else:
                self._erreur_404()
                
        except Exception as e:
            print(f"❌ Erreur handler: {e}")
            self._erreur_500()
    
    def _servir_page_accueil(self):
        """Page d'accueil du serveur web"""
        html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRed Network - Accès Web</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(15px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .logo {
            font-size: 48px;
            margin-bottom: 10px;
        }
        .titre {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .sous-titre {
            font-size: 18px;
            opacity: 0.9;
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
        }
        .form-groupe {
            margin: 20px 0;
        }
        .form-groupe label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-groupe input {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255,255,255,0.2);
            color: white;
            font-size: 16px;
        }
        .form-groupe input::placeholder {
            color: rgba(255,255,255,0.7);
        }
        .btn {
            background: #ff6b6b;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: #ff5252;
            transform: translateY(-2px);
        }
        .exemples {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .exemple {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .exemple:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }
        .code {
            background: rgba(0,0,0,0.3);
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 14px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🏰</div>
            <div class="titre">OpenRed Network</div>
            <div class="sous-titre">Accès Web aux Forts Décentralisés</div>
        </div>
        
        <div class="section">
            <h2>🔗 Accès Direct à un Fort</h2>
            <div class="form-groupe">
                <label for="fort-id">ID du Fort (16 caractères hexadécimaux):</label>
                <input type="text" id="fort-id" placeholder="1234567890abcdef" maxlength="16">
            </div>
            <button class="btn" onclick="accederFort()">Accéder au Fort</button>
        </div>
        
        <div class="section">
            <h2>🌐 URL OpenRed Protocol (orp://)</h2>
            <div class="form-groupe">
                <label for="url-orp">URL orp:// complète:</label>
                <input type="text" id="url-orp" placeholder="orp://fort_1234567890abcdef.openred/fenetre">
            </div>
            <button class="btn" onclick="traiterUrlOrp()">Ouvrir URL</button>
        </div>
        
        <div class="section">
            <h2>📝 Exemples de Forts</h2>
            <div class="exemples">
                <div class="exemple" onclick="ouvrirExemple('fort_1234567890abcdef', '')">
                    <h3>🏠 Fort Principal</h3>
                    <div class="code">orp://fort_1234567890abcdef.openred/</div>
                    <p>Accès direct au fort principal</p>
                </div>
                
                <div class="exemple" onclick="ouvrirExemple('fort_abcdef1234567890', 'fenetre')">
                    <h3>🪟 Fenêtre Publique</h3>
                    <div class="code">orp://fort_abcdef1234567890.openred/fenetre</div>
                    <p>Interface publique du fort</p>
                </div>
                
                <div class="exemple" onclick="ouvrirExemple('fort_fedcba0987654321', 'projection/demo')">
                    <h3>🎭 Projection Demo</h3>
                    <div class="code">orp://fort_fedcba0987654321.openred/projection/demo</div>
                    <p>Projection de démonstration</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>💡 Installation Client</h2>
            <p>Pour une expérience optimale, installez le client OpenRed Network:</p>
            <div class="code">python installer_protocole_orp.py</div>
            <p>Ceci permettra l'ouverture directe des liens orp:// depuis votre navigateur.</p>
        </div>
    </div>
    
    <script>
        function accederFort() {
            const fortId = document.getElementById('fort-id').value.trim();
            
            if (!fortId) {
                alert('Veuillez saisir un ID de fort');
                return;
            }
            
            if (fortId.length !== 16) {
                alert('L\\'ID du fort doit faire exactement 16 caractères');
                return;
            }
            
            // Redirection vers la page du fort
            window.location.href = `/fort/fort_${fortId}`;
        }
        
        function traiterUrlOrp() {
            const urlOrp = document.getElementById('url-orp').value.trim();
            
            if (!urlOrp) {
                alert('Veuillez saisir une URL orp://');
                return;
            }
            
            if (!urlOrp.startsWith('orp://')) {
                alert('L\\'URL doit commencer par orp://');
                return;
            }
            
            // Conversion vers URL web
            const urlWeb = urlOrp.replace('orp://', '/orp/');
            window.location.href = urlWeb;
        }
        
        function ouvrirExemple(fortId, chemin) {
            const url = chemin ? `/fort/${fortId}/${chemin}` : `/fort/${fortId}`;
            window.location.href = url;
        }
    </script>
</body>
</html>
        """
        
        self._repondre_html(html)
    
    def _servir_page_fort(self, fort_id: str):
        """Page spécifique d'un fort"""
        try:
            # Import du module de navigation
            from modules.internet import NavigateurWeb
            
            navigateur = NavigateurWeb()
            html = navigateur.generer_interface_web(fort_id)
            
            self._repondre_html(html)
            
        except Exception as e:
            print(f"❌ Erreur page fort: {e}")
            self._erreur_500()
    
    def _api_statut_fort(self, fort_id: str):
        """API pour vérifier le statut d'un fort"""
        try:
            from modules.protocole import ResolveurORP, ValidateurAdresseORP
            
            # Validation de l'ID
            if not ValidateurAdresseORP.valider_fort_id(fort_id):
                response = {"error": "ID fort invalide", "online": False}
            else:
                # Tentative de résolution
                resolveur = ResolveurORP()
                url_test = f"orp://{fort_id}.openred/"
                resultat = resolveur.resoudre(url_test)
                
                response = {
                    "fort_id": fort_id,
                    "online": resultat is not None,
                    "adresse": f"{resultat[0]}:{resultat[1]}" if resultat else None,
                    "timestamp": int(time.time())
                }
            
            self._repondre_json(response)
            
        except Exception as e:
            print(f"❌ Erreur API statut: {e}")
            response = {"error": str(e), "online": False}
            self._repondre_json(response)
    
    def _api_resoudre_fort(self, fort_id: str):
        """API pour résoudre un fort"""
        try:
            from modules.protocole import ResolveurORP
            
            resolveur = ResolveurORP()
            url = f"orp://{fort_id}.openred/"
            resultat = resolveur.resoudre(url)
            
            if resultat:
                response = {
                    "success": True,
                    "fort_id": fort_id,
                    "ip": resultat[0],
                    "port": resultat[1]
                }
            else:
                response = {
                    "success": False,
                    "error": "Fort non trouvé"
                }
            
            self._repondre_json(response)
            
        except Exception as e:
            response = {
                "success": False,
                "error": str(e)
            }
            self._repondre_json(response)
    
    def _traiter_url_orp(self, url_orp: str):
        """Traite une URL orp:// et redirige"""
        try:
            from modules.protocole import GestionnaireProtocole
            
            print(f"🌐 Traitement URL web: {url_orp}")
            
            # Traitement via le gestionnaire de protocole
            gestionnaire = GestionnaireProtocole()
            resultat = gestionnaire.traiter_url(url_orp)
            
            if resultat:
                html = f"""
                <html>
                <head><title>Connexion réussie</title></head>
                <body>
                    <h1>✅ Connexion établie</h1>
                    <p>Connexion vers {url_orp} réussie</p>
                    <a href="/">Retour à l'accueil</a>
                </body>
                </html>
                """
            else:
                html = f"""
                <html>
                <head><title>Connexion échouée</title></head>
                <body>
                    <h1>❌ Connexion échouée</h1>
                    <p>Impossible de se connecter à {url_orp}</p>
                    <p>Le fort pourrait être hors ligne ou inexistant.</p>
                    <a href="/">Retour à l'accueil</a>
                </body>
                </html>
                """
            
            self._repondre_html(html)
            
        except Exception as e:
            print(f"❌ Erreur traitement URL: {e}")
            self._erreur_500()
    
    def _repondre_html(self, html: str):
        """Répond avec du HTML"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _repondre_json(self, data: Dict[str, Any]):
        """Répond avec du JSON"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _erreur_404(self):
        """Erreur 404"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = "<html><body><h1>404 - Page non trouvée</h1></body></html>"
        self.wfile.write(html.encode())
    
    def _erreur_500(self):
        """Erreur 500"""
        self.send_response(500)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = "<html><body><h1>500 - Erreur serveur</h1></body></html>"
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Supprime les logs HTTP par défaut"""
        pass


def demarrer_serveur_web(port: int = 8080):
    """
    🚀 Démarre le serveur web OpenRed Network
    
    Args:
        port: Port d'écoute du serveur
    """
    print("=" * 60)
    print("    🌐 SERVEUR WEB OPENRED NETWORK")
    print("=" * 60)
    print()
    
    try:
        serveur = ServeurWebOpenRed(port)
        
        if serveur.demarrer_serveur():
            print(f"✅ Serveur web démarré avec succès")
            print()
            print("🌍 ACCÈS WEB DISPONIBLE:")
            print(f"  • Interface: http://localhost:{port}")
            print(f"  • Fort direct: http://localhost:{port}/fort/[fort_id]")
            print(f"  • API statut: http://localhost:{port}/api/status/[fort_id]")
            print()
            print("🔗 Vous pouvez maintenant accéder aux forts OpenRed")
            print("   directement depuis votre navigateur web !")
            
            return serveur
        else:
            print("❌ Échec démarrage serveur web")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


if __name__ == "__main__":
    # Démarrage du serveur web
    serveur = demarrer_serveur_web()
    
    if serveur:
        try:
            print("\nAppuyez sur Ctrl+C pour arrêter le serveur...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur...")
            serveur.arreter_serveur()
    
    print("🔚 Serveur arrêté")