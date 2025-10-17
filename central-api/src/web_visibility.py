#!/usr/bin/env python3
"""
Web Visibility Engine for O-RedSearch
Rendre les nœuds OpenRed découvrables par les moteurs de recherche (Google, Bing, etc.)
"""

import json
import time
import threading
import hashlib
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class WebVisibilityEngine:
    """Moteur de visibilité web pour nœuds OpenRed"""
    
    def __init__(self, node_beacon, port: int = 8080):
        self.node_beacon = node_beacon
        self.port = port
        self.server = None
        self.running = False
        self.page_views = 0
        self.bot_visits = {}
        
    def start_web_server(self):
        """Démarre le serveur web pour la visibilité"""
        if self.running:
            return
            
        self.running = True
        
        class NodePageHandler(BaseHTTPRequestHandler):
            def __init__(self, visibility_engine):
                self.visibility_engine = visibility_engine
                super().__init__()
                
            def __new__(cls, visibility_engine):
                # Closure pour passer l'engine
                def handler(*args, **kwargs):
                    instance = super(NodePageHandler, cls).__new__(cls)
                    instance.visibility_engine = visibility_engine
                    instance.__init__(*args, **kwargs)
                    return instance
                return handler
                
            def do_GET(self):
                self.visibility_engine._handle_request(self)
                
            def log_message(self, format, *args):
                # Désactiver logs HTTP par défaut
                pass
                
        handler = NodePageHandler(self)
        self.server = HTTPServer(('0.0.0.0', self.port), handler)
        
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        print(f"🌐 Web visibility server started on port {self.port}")
        
    def stop_web_server(self):
        """Arrête le serveur web"""
        self.running = False
        if self.server:
            self.server.shutdown()
            
    def _handle_request(self, handler):
        """Traite les requêtes web"""
        path = handler.path
        user_agent = handler.headers.get('User-Agent', '')
        
        # Détecter les bots
        bot_type = self._detect_bot(user_agent)
        if bot_type:
            if bot_type not in self.bot_visits:
                self.bot_visits[bot_type] = []
            self.bot_visits[bot_type].append({
                "timestamp": time.time(),
                "path": path,
                "user_agent": user_agent
            })
            print(f"🤖 Bot visit: {bot_type}")
            
        self.page_views += 1
        
        if path == '/':
            self._serve_main_page(handler)
        elif path == '/api/node-info':
            self._serve_api_info(handler)
        elif path == '/robots.txt':
            self._serve_robots_txt(handler)
        elif path == '/sitemap.xml':
            self._serve_sitemap(handler)
        elif path.startswith('/search'):
            self._serve_search_page(handler)
        else:
            self._serve_404(handler)
            
    def _detect_bot(self, user_agent: str) -> Optional[str]:
        """Détecte le type de bot"""
        user_agent_lower = user_agent.lower()
        
        bots = {
            'googlebot': 'Google',
            'bingbot': 'Bing', 
            'slurp': 'Yahoo',
            'duckduckbot': 'DuckDuckGo',
            'baiduspider': 'Baidu',
            'yandexbot': 'Yandex',
            'facebookexternalhit': 'Facebook',
            'twitterbot': 'Twitter',
            'linkedinbot': 'LinkedIn'
        }
        
        for bot_signature, bot_name in bots.items():
            if bot_signature in user_agent_lower:
                return bot_name
                
        return None
        
    def _serve_main_page(self, handler):
        """Page principale optimisée SEO"""
        html = self._generate_main_html()
        
        handler.send_response(200)
        handler.send_header('Content-Type', 'text/html; charset=utf-8')
        handler.send_header('Cache-Control', 'public, max-age=300')  # 5 min cache
        handler.end_headers()
        handler.wfile.write(html.encode('utf-8'))
        
    def _serve_api_info(self, handler):
        """API JSON pour machines"""
        data = {
            "node_id": self.node_beacon.node_id,
            "sector": self.node_beacon.sector,
            "services": self.node_beacon.services,
            "activity_level": self.node_beacon.activity_level,
            "location": self.node_beacon.location,
            "connection_info": self.node_beacon.connection_info,
            "last_updated": datetime.utcnow().isoformat(),
            "web_stats": {
                "page_views": self.page_views,
                "bot_visits": len(self.bot_visits)
            }
        }
        
        handler.send_response(200)
        handler.send_header('Content-Type', 'application/json')
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.end_headers()
        handler.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
        
    def _serve_robots_txt(self, handler):
        """Fichier robots.txt pour bots"""
        robots = """User-agent: *
Allow: /
Allow: /api/node-info
Allow: /search

Sitemap: http://localhost:{}/sitemap.xml

# OpenRed P2P Node
# Sector: {}
# Services: {}
""".format(self.port, self.node_beacon.sector, ', '.join(self.node_beacon.services))

        handler.send_response(200)
        handler.send_header('Content-Type', 'text/plain')
        handler.end_headers()
        handler.wfile.write(robots.encode('utf-8'))
        
    def _serve_sitemap(self, handler):
        """Sitemap XML pour indexation"""
        base_url = f"http://localhost:{self.port}"
        
        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{datetime.utcnow().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>hourly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{base_url}/api/node-info</loc>
        <lastmod>{datetime.utcnow().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>hourly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{base_url}/search</loc>
        <lastmod>{datetime.utcnow().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.6</priority>
    </url>
</urlset>"""

        handler.send_response(200)
        handler.send_header('Content-Type', 'application/xml')
        handler.end_headers()
        handler.wfile.write(sitemap.encode('utf-8'))
        
    def _serve_search_page(self, handler):
        """Page de recherche dynamique"""
        query_params = parse_qs(urlparse(handler.path).query)
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRed Search - {self.node_beacon.node_id}</title>
    <meta name="description" content="Recherche dans le réseau OpenRed - Nœud {self.node_beacon.sector}">
    <meta name="keywords" content="openred, p2p, search, {self.node_beacon.sector}, decentralized">
</head>
<body>
    <h1>🔍 OpenRed Search</h1>
    <p>Recherche décentralisée via nœud: <strong>{self.node_beacon.node_id}</strong></p>
    
    <form method="GET">
        <input type="text" name="q" placeholder="Rechercher des nœuds..." value="{query_params.get('q', [''])[0]}">
        <button type="submit">Rechercher</button>
    </form>
    
    <h2>Capacités de ce nœud:</h2>
    <ul>
        <li>Secteur: {self.node_beacon.sector}</li>
        <li>Services: {', '.join(self.node_beacon.services)}</li>
        <li>Activité: {self.node_beacon.activity_level}%</li>
    </ul>
    
    <p><a href="/">← Retour à la page principale</a></p>
</body>
</html>"""

        handler.send_response(200)
        handler.send_header('Content-Type', 'text/html; charset=utf-8')
        handler.end_headers()
        handler.wfile.write(html.encode('utf-8'))
        
    def _serve_404(self, handler):
        """Page 404 personnalisée"""
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>404 - OpenRed Node {self.node_beacon.node_id}</title>
</head>
<body>
    <h1>404 - Page non trouvée</h1>
    <p>Cette page n'existe pas sur le nœud OpenRed <strong>{self.node_beacon.node_id}</strong></p>
    <p><a href="/">← Page d'accueil</a></p>
</body>
</html>"""

        handler.send_response(404)
        handler.send_header('Content-Type', 'text/html; charset=utf-8')
        handler.end_headers()
        handler.wfile.write(html.encode('utf-8'))
        
    def _generate_main_html(self) -> str:
        """Génère la page HTML principale optimisée SEO"""
        
        # Calculer hash unique pour cache-busting
        content_hash = hashlib.md5(
            f"{self.node_beacon.node_id}{time.time()}".encode()
        ).hexdigest()[:8]
        
        # Coordonnées pour Schema.org
        location = self.node_beacon.location
        lat, lng = location.get('lat', 0), location.get('lng', 0)
        
        return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- SEO Meta Tags -->
    <title>OpenRed P2P Node - {self.node_beacon.node_id} | {self.node_beacon.sector.title()}</title>
    <meta name="description" content="Nœud OpenRed décentralisé dans le secteur {self.node_beacon.sector}. Services: {', '.join(self.node_beacon.services)}. Activité: {self.node_beacon.activity_level}%">
    <meta name="keywords" content="openred, p2p, {self.node_beacon.sector}, decentralized, blockchain, {', '.join(self.node_beacon.services)}">
    <meta name="author" content="OpenRed Network">
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="OpenRed Node {self.node_beacon.node_id}">
    <meta property="og:description" content="Nœud P2P décentralisé - Secteur {self.node_beacon.sector}">
    <meta property="og:url" content="http://localhost:{self.port}/">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="OpenRed Node {self.node_beacon.node_id}">
    <meta name="twitter:description" content="Nœud P2P décentralisé - {self.node_beacon.sector}">
    
    <!-- Schema.org Structured Data -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "OpenRed Node {self.node_beacon.node_id}",
        "description": "Nœud P2P décentralisé dans le secteur {self.node_beacon.sector}",
        "url": "http://localhost:{self.port}/",
        "foundingDate": "{datetime.utcnow().strftime('%Y-%m-%d')}",
        "address": {{
            "@type": "GeoCoordinates",
            "latitude": {lat},
            "longitude": {lng}
        }},
        "contactPoint": {{
            "@type": "ContactPoint",
            "contactType": "technical support",
            "url": "http://localhost:{self.port}/api/node-info"
        }},
        "knowsAbout": ["{self.node_beacon.sector}", "P2P", "Decentralization", "Blockchain"]
    }}
    </script>
    
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .info-card {{ border: 1px solid #ddd; padding: 15px; border-radius: 8px; }}
        .activity-bar {{ height: 20px; background: #ecf0f1; border-radius: 10px; overflow: hidden; }}
        .activity-fill {{ height: 100%; background: linear-gradient(to right, #e74c3c, #f39c12, #27ae60); width: {self.node_beacon.activity_level}%; }}
        .footer {{ margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 OpenRed P2P Network</h1>
        <h2>Nœud: {self.node_beacon.node_id}</h2>
        <p>Réseau décentralisé pair-à-pair | Secteur: <strong>{self.node_beacon.sector.title()}</strong></p>
    </div>
    
    <div class="info-grid">
        <div class="info-card">
            <h3>📍 Localisation</h3>
            <p>Latitude: {lat}</p>
            <p>Longitude: {lng}</p>
            <p>Altitude: {location.get('elevation', 'N/A')}m</p>
        </div>
        
        <div class="info-card">
            <h3>🔧 Services</h3>
            <ul>
                {''.join(f'<li>{service.title()}</li>' for service in self.node_beacon.services)}
            </ul>
        </div>
        
        <div class="info-card">
            <h3>⚡ Activité</h3>
            <p>Niveau d'activité: <strong>{self.node_beacon.activity_level}%</strong></p>
            <div class="activity-bar">
                <div class="activity-fill"></div>
            </div>
        </div>
        
        <div class="info-card">
            <h3>🔗 Connexion</h3>
            <p>Protocoles: {', '.join(self.node_beacon.connection_info.get('protocols', []))}</p>
            <p>Port P2P: {self.node_beacon.connection_info.get('ports', {}).get('p2p', 'N/A')}</p>
        </div>
    </div>
    
    <h3>🔍 Recherche OpenRed</h3>
    <p>Ce nœud participe au réseau de découverte passive O-RedSearch.</p>
    <ul>
        <li><a href="/search">Interface de recherche</a></li>
        <li><a href="/api/node-info">API JSON</a> (pour machines)</li>
        <li><a href="/robots.txt">Robots.txt</a></li>
        <li><a href="/sitemap.xml">Sitemap</a></li>
    </ul>
    
    <div class="footer">
        <h4>🤖 Informations pour moteurs de recherche</h4>
        <p>Ce nœud fait partie du réseau OpenRed, un système P2P décentralisé révolutionnaire.</p>
        <p><strong>Mots-clés:</strong> OpenRed, P2P, {self.node_beacon.sector}, décentralisé, blockchain, {', '.join(self.node_beacon.services)}</p>
        <p><strong>Dernière mise à jour:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        <p><strong>ID unique:</strong> {content_hash}</p>
        <p><strong>Vues de page:</strong> {self.page_views}</p>
    </div>
    
    <!-- Analytics simplifiés -->
    <script>
        // Ping pour statistiques
        fetch('/api/node-info').then(r => r.json()).then(data => {{
            console.log('Node data loaded:', data.node_id);
        }}).catch(e => console.log('Offline mode'));
    </script>
</body>
</html>"""

    def get_web_stats(self) -> Dict[str, Any]:
        """Statistiques de visibilité web"""
        return {
            "page_views": self.page_views,
            "bot_visits": self.bot_visits,
            "server_running": self.running,
            "port": self.port
        }

# Test de la visibilité web
if __name__ == "__main__":
    from o_red_search import NodeBeacon
    
    # Configuration nœud test
    test_node = NodeBeacon(
        node_id="node_web_test_001",
        location={"lat": 48.8566, "lng": 2.3522, "elevation": 35},
        services=["storage", "search", "relay"],
        activity_level=92,
        sector="tech",
        connection_info={
            "ip": "192.168.1.100",
            "ports": {"http": 8080, "p2p": 9000},
            "protocols": ["tcp", "udp", "webrtc"]
        }
    )
    
    # Démarrer serveur web
    web_engine = WebVisibilityEngine(test_node, port=8080)
    web_engine.start_web_server()
    
    print("🌐 Web server started! Visit:")
    print("  - http://localhost:8080/ (page principale)")
    print("  - http://localhost:8080/api/node-info (API JSON)")
    print("  - http://localhost:8080/search (recherche)")
    print("  - http://localhost:8080/robots.txt (robots)")
    
    try:
        while True:
            time.sleep(10)
            stats = web_engine.get_web_stats()
            print(f"📊 Web stats: {stats['page_views']} views, {len(stats['bot_visits'])} bots")
    except KeyboardInterrupt:
        print("\n🛑 Stopping web server...")
        web_engine.stop_web_server()