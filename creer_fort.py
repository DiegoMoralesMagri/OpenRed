#!/usr/bin/env python3
"""
🏰 CRÉATEUR DE FORT OPENRED
==========================

Créé un fort OpenRed avec persistance et support navigateur
"""

import os
import sys
import time
import json
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import des modules OpenRed
sys.path.append(os.path.join(os.getcwd(), 'modules'))
from persistance.gestionnaire_fort import GestionnairePersistanceFort
from internet.resolveur_p2p_decentralise import publier_fort


class ServeurFortOpenRed(BaseHTTPRequestHandler):
    """Serveur HTTP pour le fort OpenRed"""
    
    def do_GET(self):
        """Gère les requêtes GET"""
        if self.path == '/':
            self._page_accueil()
        elif self.path == '/info':
            self._page_info()
        elif self.path == '/api/status':
            self._api_status()
        else:
            self._page_404()
    
    def _page_accueil(self):
        """Page d'accueil du fort"""
        fort_info = self.server.fort_info
        
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{fort_info['nom']} - Fort OpenRed</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 40px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                }}
                .logo {{
                    font-size: 4em;
                    margin-bottom: 20px;
                }}
                .fort-id {{
                    font-family: 'Courier New', monospace;
                    background: rgba(0,0,0,0.3);
                    padding: 10px;
                    border-radius: 5px;
                    word-break: break-all;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .stat-card {{
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                }}
                .stat-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #00ff88;
                }}
                .protocol-info {{
                    background: rgba(0,255,136,0.1);
                    border: 2px solid #00ff88;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .btn {{
                    display: inline-block;
                    background: #00ff88;
                    color: #333;
                    padding: 12px 24px;
                    border-radius: 25px;
                    text-decoration: none;
                    font-weight: bold;
                    margin: 10px;
                    transition: all 0.3s;
                }}
                .btn:hover {{
                    background: #00cc6a;
                    transform: translateY(-2px);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🏰</div>
                    <h1>{fort_info['nom']}</h1>
                    <p>Fort OpenRed P2P - Réseau Décentralisé</p>
                    <div class="fort-id">
                        <strong>Fort ID:</strong> {fort_info['fort_id']}
                    </div>
                </div>
                
                <div class="protocol-info">
                    <h3>🌐 Accès via Protocole ORP://</h3>
                    <p><strong>URL OpenRed:</strong></p>
                    <div class="fort-id">
                        <a href="orp://{fort_info['fort_id']}.openred/" style="color: #00ff88;">
                            orp://{fort_info['fort_id']}.openred/
                        </a>
                    </div>
                    <p><em>Nécessite l'extension navigateur OpenRed ou le pont HTTP actif</em></p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">✅</div>
                        <div>Status</div>
                        <small>Actif</small>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{fort_info['port']}</div>
                        <div>Port</div>
                        <small>HTTP</small>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">🌐</div>
                        <div>Protocole</div>
                        <small>ORP v1.0</small>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">🔒</div>
                        <div>Sécurité</div>
                        <small>P2P Chiffré</small>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 40px;">
                    <a href="/info" class="btn">📋 Informations Fort</a>
                    <a href="/api/status" class="btn">🔧 API Status</a>
                    <a href="https://openred.community" class="btn" target="_blank">🌍 OpenRed Community</a>
                </div>
                
                <div style="text-align: center; margin-top: 30px; opacity: 0.8;">
                    <p><small>
                        Créé le {datetime.fromtimestamp(fort_info['creation_timestamp']).strftime('%d/%m/%Y à %H:%M')} 
                        • Dernière activité: {datetime.fromtimestamp(fort_info['derniere_activite']).strftime('%d/%m/%Y à %H:%M')}
                    </small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self._send_html(html)
    
    def _page_info(self):
        """Page d'informations du fort"""
        fort_info = self.server.fort_info
        
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Informations - {fort_info['nom']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .info-grid {{ display: grid; gap: 15px; }}
                .info-item {{ padding: 15px; background: #f8f9fa; border-left: 4px solid #007acc; }}
                .info-label {{ font-weight: bold; color: #333; }}
                .info-value {{ font-family: monospace; color: #666; margin-top: 5px; }}
                .back-btn {{ display: inline-block; background: #007acc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏰 Informations du Fort</h1>
                
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Nom du Fort</div>
                        <div class="info-value">{fort_info['nom']}</div>
                    </div>
                    
                    <div class="info-item">
                        <div class="info-label">Identifiant Unique</div>
                        <div class="info-value">{fort_info['fort_id']}</div>
                    </div>
                    
                    <div class="info-item">
                        <div class="info-label">Port d'écoute</div>
                        <div class="info-value">{fort_info['port']}</div>
                    </div>
                    
                    <div class="info-item">
                        <div class="info-label">URL OpenRed (orp://)</div>
                        <div class="info-value">orp://{fort_info['fort_id']}.openred/</div>
                    </div>
                    
                    <div class="info-item">
                        <div class="info-label">Clé Publique</div>
                        <div class="info-value">{fort_info['cle_publique']}</div>
                    </div>
                    
                    <div class="info-item">
                        <div class="info-label">Date de Création</div>
                        <div class="info-value">{datetime.fromtimestamp(fort_info['creation_timestamp']).strftime('%d/%m/%Y à %H:%M:%S')}</div>
                    </div>
                    
                    <div class="info-item">
                        <div class="info-label">Dernière Activité</div>
                        <div class="info-value">{datetime.fromtimestamp(fort_info['derniere_activite']).strftime('%d/%m/%Y à %H:%M:%S')}</div>
                    </div>
                </div>
                
                <a href="/" class="back-btn">← Retour à l'accueil</a>
            </div>
        </body>
        </html>
        """
        
        self._send_html(html)
    
    def _api_status(self):
        """API de status JSON"""
        fort_info = self.server.fort_info
        
        status = {
            "status": "active",
            "fort": {
                "id": fort_info['fort_id'],
                "nom": fort_info['nom'],
                "port": fort_info['port'],
                "orp_url": f"orp://{fort_info['fort_id']}.openred/",
                "creation": fort_info['creation_timestamp'],
                "derniere_activite": fort_info['derniere_activite']
            },
            "timestamp": time.time(),
            "uptime": time.time() - self.server.temps_demarrage
        }
        
        self._send_json(status)
    
    def _page_404(self):
        """Page 404"""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>404 - Page non trouvée</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 100px;">
            <h1>🤔 Page non trouvée</h1>
            <p>Cette page n'existe pas sur ce fort OpenRed.</p>
            <a href="/" style="color: #007acc;">← Retour à l'accueil</a>
        </body>
        </html>
        """
        self._send_html(html, 404)
    
    def _send_html(self, html, status=200):
        """Envoie une réponse HTML"""
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _send_json(self, data):
        """Envoie une réponse JSON"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Log personnalisé"""
        print(f"🌐 [{datetime.now().strftime('%H:%M:%S')}] {format % args}")


class FortOpenRed:
    """Fort OpenRed complet avec persistance et serveur web"""
    
    def __init__(self, nom_fort: str, port: int = 8080):
        self.nom_fort = nom_fort
        self.port = port
        self.gestionnaire_persistance = GestionnairePersistanceFort()
        self.serveur = None
        self.temps_demarrage = time.time()
        
    def creer_fort(self):
        """Crée ou restaure le fort"""
        print(f"🏰 === CRÉATION FORT OPENRED ===")
        print(f"Nom: {self.nom_fort}")
        print(f"Port: {self.port}")
        print("=" * 40)
        
        # Crée ou charge l'identité persistante
        self.identite = self.gestionnaire_persistance.creer_ou_charger_identite(
            self.nom_fort, self.port
        )
        
        print(f"✅ Fort créé/restauré: {self.identite.fort_id}")
        
        # Démarre la sauvegarde automatique
        self.gestionnaire_persistance.demarrer_sauvegarde_auto()
        
        return self.identite
    
    def publier_p2p(self):
        """Publie le fort dans le réseau P2P"""
        print("📡 Publication dans le réseau P2P...")
        
        try:
            fort_info = {
                "fort_id": self.identite.fort_id,
                "nom": self.identite.nom,
                "ip_publique": "127.0.0.1",  # Local pour test
                "port": self.identite.port,
                "cle_publique": self.identite.cle_publique,
                "timestamp": time.time()
            }
            
            publier_fort(fort_info)
            print("✅ Fort publié dans le réseau P2P")
            
        except Exception as e:
            print(f"⚠️  Erreur publication P2P: {e}")
            print("🔄 Le fort reste accessible localement")
    
    def demarrer_serveur(self):
        """Démarre le serveur web du fort"""
        try:
            self.serveur = HTTPServer(('0.0.0.0', self.port), ServeurFortOpenRed)
            
            # Partage les informations avec le serveur
            self.serveur.fort_info = {
                "fort_id": self.identite.fort_id,
                "nom": self.identite.nom,
                "port": self.identite.port,
                "cle_publique": self.identite.cle_publique,
                "creation_timestamp": self.identite.creation_timestamp,
                "derniere_activite": self.identite.derniere_activite
            }
            self.serveur.temps_demarrage = self.temps_demarrage
            
            print(f"🌐 Serveur démarré sur port {self.port}")
            print(f"📍 URL locale: http://localhost:{self.port}")
            print(f"🔗 URL OpenRed: orp://{self.identite.fort_id}.openred/")
            print("\n💡 ACCÈS POSSIBLE VIA:")
            print(f"   • HTTP direct: http://localhost:{self.port}")
            print(f"   • Protocole ORP: orp://{self.identite.fort_id}.openred/")
            print(f"   • Avec extension navigateur installée")
            print(f"   • Avec pont HTTP actif (port 7888)")
            
            self.serveur.serve_forever()
            
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du fort...")
            self.arreter()
        except Exception as e:
            print(f"❌ Erreur serveur: {e}")
    
    def arreter(self):
        """Arrête le fort proprement"""
        print("💾 Sauvegarde finale...")
        self.gestionnaire_persistance.arreter_sauvegarde_auto()
        
        if self.serveur:
            self.serveur.shutdown()
        
        print("✅ Fort arrêté proprement")


def main():
    """Fonction principale"""
    print("🏰 === CRÉATEUR DE FORT OPENRED ===")
    print("Créé un fort accessible via orp://")
    print("=" * 40)
    
    # Demande le nom du fort
    nom_fort = input("Nom de votre fort: ").strip()
    if not nom_fort:
        nom_fort = "Mon Fort OpenRed"
    
    # Demande le port
    port_input = input("Port (défaut 8080): ").strip()
    try:
        port = int(port_input) if port_input else 8080
    except ValueError:
        port = 8080
    
    # Crée et démarre le fort
    fort = FortOpenRed(nom_fort, port)
    
    try:
        # Étapes de création
        fort.creer_fort()
        fort.publier_p2p()
        
        print("\n🎉 Fort créé avec succès !")
        print("⏳ Démarrage du serveur...")
        
        fort.demarrer_serveur()
        
    except KeyboardInterrupt:
        print("\n👋 Au revoir !")
        fort.arreter()
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    main()