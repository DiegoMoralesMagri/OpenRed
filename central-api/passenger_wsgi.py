#!/usr/bin/env python3
"""
Application WSGI pour déploiement O2Switch
WSGI application for O2Switch deployment

Version simplifiée compatible avec les hébergements partagés
Simplified version compatible with shared hosting
"""

import os
import sys
from pathlib import Path

# Ajout du répertoire de l'application au PYTHONPATH
# Add application directory to PYTHONPATH
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Configuration pour O2Switch
# O2Switch configuration
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'false')

try:
    # Import de l'application FastAPI
    # Import FastAPI application
    from main_new import app
    
    # Configuration WSGI
    # WSGI configuration
    application = app
    
except ImportError as e:
    # Fallback vers une application simple si main_new échoue
    # Fallback to simple application if main_new fails
    print(f"Erreur d'import: {e}")
    
    # Application WSGI simple de secours
    # Simple fallback WSGI application
    def application(environ, start_response):
        status = '200 OK'
        headers = [
            ('Content-type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        ]
        start_response(status, headers)
        
        response = {
            "message": "OpenRed Central API - O2Switch Deployment",
            "status": "running",
            "version": "2.0.0",
            "environment": "production",
            "error": f"Application principale non disponible: {str(e)}"
        }
        
        import json
        return [json.dumps(response, ensure_ascii=False).encode('utf-8')]

# Point d'entrée pour les tests locaux
# Entry point for local testing
if __name__ == "__main__":
    print("🚀 OpenRed Central API - Mode WSGI O2Switch")
    print("Application prête pour déploiement")
    print("Application ready for deployment")
