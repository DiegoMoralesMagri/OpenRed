#!/usr/bin/env python3
"""
🌉 PONT NAVIGATEUR-RÉSOLVEUR P2P - OPENRED
=========================================

Serveur HTTP local qui permet aux extensions navigateur
de communiquer avec le résolveur P2P OpenRed.

Fonctionnalités :
- API REST pour résolution orp://
- Interface CORS pour extensions
- Cache local intelligent
- Statistiques de résolution
- Interface web de diagnostic

Port par défaut : 7888
"""

import os
import sys
import json
import time
import threading
from typing import Dict, Optional
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class PontNavigateurHTTP(BaseHTTPRequestHandler):
    """Gestionnaire HTTP pour les requêtes des extensions navigateur"""
    
    def do_OPTIONS(self):
        """Gère les requêtes CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Gère les requêtes GET"""
        if self.path == '/status':
            self._handle_status()
        elif self.path == '/stats':
            self._handle_stats()
        elif self.path == '/cache':
            self._handle_cache()
        elif self.path.startswith('/resolve'):
            self._handle_resolve_get()
        else:
            self._handle_default()
    
    def do_POST(self):
        """Gère les requêtes POST"""
        if self.path == '/resolve':
            self._handle_resolve_post()
        else:
            self._send_error(404, "Endpoint non trouvé")
    
    def _handle_status(self):
        """Status du pont"""
        status = {
            "service": "OpenRed Browser Bridge",
            "version": "1.0.0",
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "resolveur_p2p": self.server.resolveur_disponible,
            "cache_entries": len(self.server.cache_resolution)
        }
        
        self._send_json_response(status)
    
    def _handle_stats(self):
        """Statistiques détaillées"""
        stats = {
            "resolutions_totales": self.server.stats['resolutions_totales'],
            "resolutions_reussies": self.server.stats['resolutions_reussies'],
            "resolutions_cache": self.server.stats['resolutions_cache'],
            "temps_moyen_resolution": self.server.stats.get('temps_moyen', 0),
            "derniere_resolution": self.server.stats.get('derniere_resolution'),
            "cache_hit_ratio": self._calculer_cache_hit_ratio(),
            "uptime": time.time() - self.server.temps_demarrage
        }
        
        self._send_json_response(stats)
    
    def _handle_cache(self):
        """Contenu du cache"""
        cache_data = []
        
        for url, entry in self.server.cache_resolution.items():
            cache_data.append({
                "orp_url": url,
                "resolved_url": entry["resolved_url"],
                "timestamp": entry["timestamp"],
                "age_seconds": time.time() - entry["timestamp"],
                "source": entry.get("source", "unknown")
            })
        
        self._send_json_response({
            "cache_entries": cache_data,
            "total_entries": len(cache_data)
        })
    
    def _handle_resolve_get(self):
        """Résolution via GET (URL en paramètre)"""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        orp_url = params.get('url', [None])[0]
        if not orp_url:
            self._send_error(400, "Paramètre 'url' requis")
            return
        
        self._resoudre_url(orp_url, "get_request")
    
    def _handle_resolve_post(self):
        """Résolution via POST (JSON)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            request_data = json.loads(post_data.decode('utf-8'))
            orp_url = request_data.get('orp_url')
            source = request_data.get('source', 'post_request')
            
            if not orp_url:
                self._send_error(400, "Champ 'orp_url' requis")
                return
            
            self._resoudre_url(orp_url, source)
            
        except json.JSONDecodeError:
            self._send_error(400, "JSON invalide")
        except Exception as e:
            self._send_error(500, f"Erreur serveur: {e}")
    
    def _resoudre_url(self, orp_url: str, source: str):
        """Résout une URL orp://"""
        start_time = time.time()
        
        try:
            # Incrémente les stats
            self.server.stats['resolutions_totales'] += 1
            
            # Vérifie le cache
            cached = self.server.cache_resolution.get(orp_url)
            if cached and (time.time() - cached['timestamp']) < self.server.cache_ttl:
                self.server.stats['resolutions_cache'] += 1
                
                response = {
                    "success": True,
                    "resolved_url": cached["resolved_url"],
                    "source": "cache",
                    "cached": True,
                    "resolution_time": 0.001
                }
                
                self._send_json_response(response)
                return
            
            # Résolution via le système P2P
            resolved_url = self._resoudre_via_p2p(orp_url)
            
            resolution_time = time.time() - start_time
            
            if resolved_url:
                # Met en cache
                self.server.cache_resolution[orp_url] = {
                    "resolved_url": resolved_url,
                    "timestamp": time.time(),
                    "source": source
                }
                
                # Statistiques
                self.server.stats['resolutions_reussies'] += 1
                self.server.stats['derniere_resolution'] = datetime.now().isoformat()
                
                # Temps moyen
                if 'temps_moyen' not in self.server.stats:
                    self.server.stats['temps_moyen'] = resolution_time
                else:
                    self.server.stats['temps_moyen'] = (
                        self.server.stats['temps_moyen'] * 0.9 + resolution_time * 0.1
                    )
                
                response = {
                    "success": True,
                    "resolved_url": resolved_url,
                    "source": "p2p_resolver",
                    "cached": False,
                    "resolution_time": resolution_time
                }
                
                self._send_json_response(response)
            else:
                response = {
                    "success": False,
                    "error": "Impossible de résoudre l'URL orp://",
                    "orp_url": orp_url,
                    "resolution_time": resolution_time
                }
                
                self._send_json_response(response, status_code=404)
        
        except Exception as e:
            response = {
                "success": False,
                "error": str(e),
                "orp_url": orp_url
            }
            
            self._send_json_response(response, status_code=500)
    
    def _resoudre_via_p2p(self, orp_url: str) -> Optional[str]:
        """Résout via le système P2P OpenRed"""
        try:
            # Import dynamique pour éviter les dépendances circulaires
            sys.path.append(os.path.join(os.getcwd(), 'modules', 'internet'))
            from resolveur_p2p_decentralise import resoudre_url_orp
            
            resultat = resoudre_url_orp(orp_url)
            
            if resultat and resultat.get('url_complete'):
                return resultat['url_complete']
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur résolution P2P: {e}")
            return None
    
    def _handle_default(self):
        """Page d'accueil"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>OpenRed Browser Bridge</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { color: #007acc; border-bottom: 2px solid #007acc; padding-bottom: 10px; }
                .status { background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .endpoint { background: #f9f9f9; padding: 10px; border-left: 3px solid #007acc; margin: 10px 0; }
                .success { color: #00cc00; }
                .error { color: #cc0000; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌉 OpenRed Browser Bridge</h1>
                <p>Pont entre navigateurs et résolveur P2P OpenRed</p>
            </div>
            
            <div class="status">
                <h3>Status du Service</h3>
                <p class="success">✅ Actif et fonctionnel</p>
                <p><strong>Port:</strong> 7888</p>
                <p><strong>Version:</strong> 1.0.0</p>
            </div>
            
            <h3>API Endpoints</h3>
            
            <div class="endpoint">
                <strong>GET /status</strong><br>
                Status du service et informations système
            </div>
            
            <div class="endpoint">
                <strong>POST /resolve</strong><br>
                Résolution d'URLs orp://<br>
                Body: {"orp_url": "orp://fort_123.openred/page"}
            </div>
            
            <div class="endpoint">
                <strong>GET /stats</strong><br>
                Statistiques de résolution
            </div>
            
            <div class="endpoint">
                <strong>GET /cache</strong><br>
                Contenu du cache de résolution
            </div>
            
            <h3>Test de Résolution</h3>
            <p>Testez une URL orp:// :</p>
            <input type="text" id="testUrl" placeholder="orp://fort_example.openred/" style="width: 300px;">
            <button onclick="testResolve()">Résoudre</button>
            <div id="result" style="margin-top: 10px;"></div>
            
            <script>
                async function testResolve() {
                    const url = document.getElementById('testUrl').value;
                    const resultDiv = document.getElementById('result');
                    
                    if (!url) {
                        resultDiv.innerHTML = '<p class="error">Veuillez entrer une URL</p>';
                        return;
                    }
                    
                    try {
                        const response = await fetch('/resolve', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ orp_url: url, source: 'web_test' })
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            resultDiv.innerHTML = `
                                <p class="success">✅ Résolution réussie</p>
                                <p><strong>URL résolue:</strong> <a href="${result.resolved_url}" target="_blank">${result.resolved_url}</a></p>
                                <p><strong>Temps:</strong> ${(result.resolution_time * 1000).toFixed(1)}ms</p>
                                <p><strong>Source:</strong> ${result.source}</p>
                            `;
                        } else {
                            resultDiv.innerHTML = `<p class="error">❌ ${result.error}</p>`;
                        }
                    } catch (error) {
                        resultDiv.innerHTML = `<p class="error">❌ Erreur: ${error.message}</p>`;
                    }
                }
            </script>
        </body>
        </html>
        """
        
        self._send_html_response(html)
    
    def _calculer_cache_hit_ratio(self) -> float:
        """Calcule le ratio de hits du cache"""
        total = self.server.stats['resolutions_totales']
        cache_hits = self.server.stats['resolutions_cache']
        
        if total == 0:
            return 0.0
        
        return (cache_hits / total) * 100
    
    def _send_json_response(self, data: Dict, status_code: int = 200):
        """Envoie une réponse JSON"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))
    
    def _send_html_response(self, html: str):
        """Envoie une réponse HTML"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(html.encode('utf-8'))
    
    def _send_error(self, code: int, message: str):
        """Envoie une erreur JSON"""
        error_response = {
            "success": False,
            "error": message,
            "code": code,
            "timestamp": datetime.now().isoformat()
        }
        
        self._send_json_response(error_response, code)
    
    def log_message(self, format, *args):
        """Surcharge pour personnaliser les logs"""
        print(f"🌉 [{datetime.now().strftime('%H:%M:%S')}] {format % args}")


class ServeurPontNavigateur:
    """Serveur pont entre navigateurs et résolveur P2P"""
    
    def __init__(self, port: int = 7888):
        self.port = port
        self.cache_resolution = {}
        self.cache_ttl = 300  # 5 minutes
        self.stats = {
            'resolutions_totales': 0,
            'resolutions_reussies': 0,
            'resolutions_cache': 0
        }
        self.temps_demarrage = time.time()
        self.resolveur_disponible = False
        self.serveur = None
        
    def demarrer(self):
        """Démarre le serveur pont"""
        try:
            self.serveur = HTTPServer(('localhost', self.port), PontNavigateurHTTP)
            
            # Partage les données avec le handler
            self.serveur.cache_resolution = self.cache_resolution
            self.serveur.cache_ttl = self.cache_ttl
            self.serveur.stats = self.stats
            self.serveur.temps_demarrage = self.temps_demarrage
            self.serveur.resolveur_disponible = self._detecter_resolveur()
            
            print(f"🌉 === PONT NAVIGATEUR OPENRED ===")
            print(f"Port: {self.port}")
            print(f"URL: http://localhost:{self.port}")
            print(f"Résolveur P2P: {'✅ Détecté' if self.serveur.resolveur_disponible else '⚠️  Non détecté'}")
            print("=" * 40)
            
            # Thread de nettoyage cache
            threading.Thread(target=self._nettoyer_cache_periodique, daemon=True).start()
            
            print(f"🌐 Serveur démarré sur http://localhost:{self.port}")
            print("💡 Testez dans votre navigateur !")
            
            self.serveur.serve_forever()
            
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur pont...")
            if self.serveur:
                self.serveur.shutdown()
        except Exception as e:
            print(f"❌ Erreur serveur pont: {e}")
    
    def _detecter_resolveur(self) -> bool:
        """Détecte si le résolveur P2P est disponible"""
        try:
            sys.path.append(os.path.join(os.getcwd(), 'modules', 'internet'))
            from resolveur_p2p_decentralise import resoudre_url_orp
            return True
        except:
            return False
    
    def _nettoyer_cache_periodique(self):
        """Nettoie le cache périodiquement"""
        while True:
            time.sleep(60)  # Toutes les minutes
            
            maintenant = time.time()
            cles_a_supprimer = []
            
            for url, entry in self.cache_resolution.items():
                if maintenant - entry['timestamp'] > self.cache_ttl:
                    cles_a_supprimer.append(url)
            
            for cle in cles_a_supprimer:
                del self.cache_resolution[cle]
            
            if cles_a_supprimer:
                print(f"🧹 Cache nettoyé: {len(cles_a_supprimer)} entrées expirées")


if __name__ == "__main__":
    serveur = ServeurPontNavigateur()
    serveur.demarrer()