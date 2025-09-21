#!/usr/bin/env python3
"""
Version ultra-simplifiée pour O2Switch SANS aucune dépendance externe
Ultra-simplified version for O2Switch WITHOUT any external dependencies

Utilise uniquement les modules intégrés à Python
Uses only Python built-in modules
"""

import os
import sys
import json
from urllib.parse import parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Configuration pour O2Switch
os.environ.setdefault('ENVIRONMENT', 'production')

class OpenRedHandler(BaseHTTPRequestHandler):
    """Gestionnaire HTTP simple avec toutes les routes nécessaires"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_cors_headers()
        
        # Routage simple
        if self.path == '/':
            self.serve_root()
        elif self.path == '/health':
            self.serve_health()
        elif self.path.startswith('/api/v1/status'):
            self.serve_api_status()
        elif self.path.startswith('/api/v1/nodes/discover'):
            self.serve_nodes_discover()
        else:
            self.serve_404()
    
    def do_POST(self):
        """Handle POST requests"""
        self.send_cors_headers()
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(post_data)
        except json.JSONDecodeError:
            data = {}
        
        if self.path.startswith('/api/v1/auth/register'):
            self.serve_auth_register(data)
        elif self.path.startswith('/api/v1/auth/login'):
            self.serve_auth_login(data)
        elif self.path.startswith('/api/v1/messages/send'):
            self.serve_message_send(data)
        else:
            self.serve_404()
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
    
    def serve_json(self, data, status=200):
        """Send JSON response"""
        if status != 200:
            self.send_response(status)
            self.send_cors_headers()
        self.end_headers()
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def serve_root(self):
        """Serve root endpoint"""
        data = {
            "message": "OpenRed Central API v2.0 - O2Switch Edition",
            "status": "running",
            "version": "2.0.0",
            "environment": "production",
            "mode": "standalone_http_server",
            "description": "API centrale pour l'écosystème OpenRed décentralisé",
            "features": {
                "authentication": True,
                "node_management": True,
                "message_routing": True,
                "monitoring": True
            },
            "endpoints": {
                "health": "/health",
                "api_status": "/api/v1/status",
                "auth_register": "/api/v1/auth/register (POST)",
                "auth_login": "/api/v1/auth/login (POST)",
                "nodes_discover": "/api/v1/nodes/discover",
                "message_send": "/api/v1/messages/send (POST)"
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "server_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "encoding": sys.getdefaultencoding()
            }
        }
        self.serve_json(data)
    
    def serve_health(self):
        """Serve health check endpoint"""
        data = {
            "status": "healthy",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "version": "2.0.0",
            "environment": "production",
            "uptime": time.time(),
            "checks": {
                "api": "operational",
                "server": "running",
                "python": "available"
            }
        }
        self.serve_json(data)
    
    def serve_api_status(self):
        """Serve API status endpoint"""
        data = {
            "api_version": "v1",
            "status": "operational",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "capabilities": {
                "authentication": "available",
                "node_registration": "available",
                "node_discovery": "available",
                "message_routing": "available",
                "health_monitoring": "available"
            },
            "limits": {
                "max_nodes": 1000,
                "max_messages_per_minute": 100,
                "max_request_size": "1MB"
            }
        }
        self.serve_json(data)
    
    def serve_auth_register(self, data):
        """Serve authentication registration endpoint"""
        response = {
            "message": "Node registration processed",
            "status": "success",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "node_id": f"node_{int(time.time())}",
            "token": f"temp_token_{int(time.time())}",
            "expires_in": 3600,
            "note": "Version simplifiée - Configuration complète requise pour production"
        }
        self.serve_json(response)
    
    def serve_auth_login(self, data):
        """Serve authentication login endpoint"""
        response = {
            "message": "Node authentication processed",
            "status": "success",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "access_token": f"access_{int(time.time())}",
            "refresh_token": f"refresh_{int(time.time())}",
            "token_type": "Bearer",
            "expires_in": 900,
            "note": "Version simplifiée - Configuration complète requise pour production"
        }
        self.serve_json(response)
    
    def serve_nodes_discover(self):
        """Serve nodes discovery endpoint"""
        response = {
            "message": "Node discovery processed",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "nodes": [
                {
                    "id": "node_1",
                    "address": "127.0.0.1:8001",
                    "status": "online",
                    "last_seen": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            ],
            "total_nodes": 1,
            "note": "Version simplifiée - Base de données requise pour données réelles"
        }
        self.serve_json(response)
    
    def serve_message_send(self, data):
        """Serve message sending endpoint"""
        response = {
            "message": "Message queued for delivery",
            "status": "success",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "message_id": f"msg_{int(time.time())}",
            "recipients": 1,
            "note": "Version simplifiée - Système de messages complet requis pour production"
        }
        self.serve_json(response)
    
    def serve_404(self):
        """Serve 404 response"""
        data = {
            "error": "Not Found",
            "status": 404,
            "path": self.path,
            "message": "Endpoint non trouvé",
            "available_endpoints": [
                "/",
                "/health", 
                "/api/v1/status",
                "/api/v1/auth/register (POST)",
                "/api/v1/auth/login (POST)",
                "/api/v1/nodes/discover",
                "/api/v1/messages/send (POST)"
            ]
        }
        self.send_response(404)
        self.send_cors_headers()
        self.serve_json(data, 404)
    
    def log_message(self, format, *args):
        """Custom logging"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {self.address_string()} - {format % args}")

def create_wsgi_app():
    """Create WSGI application wrapper"""
    def application(environ, start_response):
        # Simulation basique d'une requête HTTP pour WSGI
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        
        # Headers de base
        headers = [
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        ]
        
        # Route simple pour WSGI
        if path == '/':
            response = {
                "message": "OpenRed Central API v2.0 - WSGI Mode",
                "status": "running",
                "version": "2.0.0",
                "mode": "wsgi_standalone"
            }
        else:
            response = {
                "message": "OpenRed Central API v2.0",
                "status": "running", 
                "path": path,
                "method": method
            }
        
        start_response('200 OK', headers)
        return [json.dumps(response, ensure_ascii=False).encode('utf-8')]
    
    return application

# Application WSGI pour O2Switch
application = create_wsgi_app()

def run_server(port=8000):
    """Run standalone HTTP server"""
    try:
        server = HTTPServer(('0.0.0.0', port), OpenRedHandler)
        print(f"🚀 OpenRed Central API v2.0 - Server démarré sur le port {port}")
        print(f"📍 Accès: http://localhost:{port}")
        print("🛑 Arrêt avec Ctrl+C")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Serveur arrêté proprement")
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")

if __name__ == "__main__":
    print("🚀 OpenRed Central API v2.0 - Version Standalone O2Switch")
    print("Sans dépendances externes - Modules Python intégrés uniquement")
    
    # Démarrage du serveur
    port = int(os.environ.get('PORT', 8000))
    run_server(port)
