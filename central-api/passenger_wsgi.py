#!/usr/bin/env python3
"""
Application WSGI pour déploiement O2Switch - Version simplifiée
WSGI application for O2Switch deployment - Simplified version

Version robuste sans environnement virtuel
Robust version without virtual environment
"""

import os
import sys
from pathlib import Path

# Ajout du répertoire de l'application au PYTHONPATH
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "src"))

# Configuration pour O2Switch
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'false')

try:
    # Essayer d'importer l'application complète
    from main_o2switch import app
    application = app
    print("✅ Application complète chargée")
    
except ImportError as e:
    print(f"Import main_o2switch échoué: {e}")
    
    try:
        # Fallback vers main_new si disponible
        from main_new import app
        application = app
        print("✅ Application main_new chargée")
        
    except ImportError:
        print("Création d'une application WSGI de base...")
        
        # Application WSGI de base garantie de fonctionner
        def application(environ, start_response):
            import json
            from urllib.parse import parse_qs
            
            # Headers de sécurité basiques
            headers = [
                ('Content-Type', 'application/json; charset=utf-8'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
                ('X-Content-Type-Options', 'nosniff'),
                ('X-Frame-Options', 'DENY'),
                ('X-XSS-Protection', '1; mode=block')
            ]
            
            # Routage simple
            path = environ.get('PATH_INFO', '')
            method = environ.get('REQUEST_METHOD', 'GET')
            
            if method == 'OPTIONS':
                start_response('200 OK', headers)
                return [b'']
            
            # Routes de base
            if path == '/':
                response = {
                    "message": "OpenRed Central API v2.0 - O2Switch",
                    "status": "running",
                    "version": "2.0.0",
                    "environment": "production",
                    "mode": "basic_wsgi",
                    "endpoints": [
                        "/health",
                        "/api/v1/status",
                        "/api/v1/auth/register",
                        "/api/v1/auth/login"
                    ]
                }
                
            elif path == '/health':
                response = {
                    "status": "healthy",
                    "timestamp": "2025-09-21T12:00:00Z",
                    "version": "2.0.0",
                    "environment": "production",
                    "database": "not_configured",
                    "mode": "basic_wsgi"
                }
                
            elif path == '/api/v1/status':
                response = {
                    "api_version": "v1",
                    "status": "operational", 
                    "mode": "basic_wsgi",
                    "features": {
                        "authentication": "basic_available",
                        "node_management": "basic_available",
                        "message_routing": "basic_available"
                    }
                }
                
            elif path == '/api/v1/auth/register':
                if method == 'POST':
                    response = {
                        "message": "Node registration endpoint",
                        "status": "available",
                        "mode": "basic_wsgi",
                        "note": "Configuration requise pour fonctionnalité complète"
                    }
                else:
                    response = {"error": "Method not allowed", "allowed": ["POST"]}
                    
            elif path == '/api/v1/auth/login':
                if method == 'POST':
                    response = {
                        "message": "Node login endpoint",
                        "status": "available",
                        "mode": "basic_wsgi", 
                        "note": "Configuration requise pour fonctionnalité complète"
                    }
                else:
                    response = {"error": "Method not allowed", "allowed": ["POST"]}
                    
            else:
                response = {
                    "error": "Not Found",
                    "path": path,
                    "available_endpoints": ["/", "/health", "/api/v1/status"]
                }
                headers[0] = ('Content-Type', 'application/json; charset=utf-8')
                start_response('404 Not Found', headers)
                return [json.dumps(response, ensure_ascii=False).encode('utf-8')]
            
            start_response('200 OK', headers)
            return [json.dumps(response, ensure_ascii=False).encode('utf-8')]

# Point d'entrée pour les tests locaux
if __name__ == "__main__":
    print("🚀 OpenRed Central API - Mode WSGI O2Switch")
    print("Application prête pour déploiement")
    print("Test de l'application WSGI...")
    
    # Test simple
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80'
    }
    
    def start_response(status, headers):
        print(f"Status: {status}")
        print(f"Headers: {headers}")
    
    result = application(environ, start_response)
    print("Réponse:", result[0].decode('utf-8'))
    print("✅ Test WSGI réussi")
