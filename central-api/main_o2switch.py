#!/usr/bin/env python3
"""
Version simplifiée de main_new.py pour O2Switch
Simplified version of main_new.py for O2Switch hosting

Compatible avec les hébergements partagés sans environnement virtuel
Compatible with shared hosting without virtual environment
"""

import os
import sys
from pathlib import Path

# Ajout du répertoire actuel au PYTHONPATH
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "src"))

# Configuration pour O2Switch
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'false')

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    
    # Configuration basique
    app = FastAPI(
        title="OpenRed Central API",
        description="API centrale pour l'écosystème OpenRed",
        version="2.0.0",
        docs_url="/docs" if os.getenv('DEBUG', 'false').lower() == 'true' else None,
        redoc_url="/redoc" if os.getenv('DEBUG', 'false').lower() == 'true' else None
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # À configurer selon votre domaine
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "OpenRed Central API v2.0",
            "status": "running",
            "environment": os.getenv('ENVIRONMENT', 'production'),
            "version": "2.0.0",
            "documentation": "/docs" if os.getenv('DEBUG', 'false').lower() == 'true' else "disabled_in_production"
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": "2025-09-21T12:00:00Z",
            "version": "2.0.0",
            "environment": os.getenv('ENVIRONMENT', 'production')
        }
    
    @app.get("/api/v1/status")
    async def api_status():
        return {
            "api_version": "v1",
            "status": "operational",
            "features": {
                "authentication": "available",
                "node_management": "available", 
                "message_routing": "available"
            }
        }
    
    # Endpoints d'authentification basiques
    @app.post("/api/v1/auth/register")
    async def register_node():
        return {
            "message": "Node registration endpoint",
            "status": "available",
            "note": "Full implementation in main_new.py"
        }
    
    @app.post("/api/v1/auth/login") 
    async def login():
        return {
            "message": "Node login endpoint",
            "status": "available", 
            "note": "Full implementation in main_new.py"
        }
    
    @app.get("/api/v1/nodes/discover")
    async def discover_nodes():
        return {
            "message": "Node discovery endpoint",
            "nodes": [],
            "status": "available",
            "note": "Full implementation in main_new.py"
        }

except ImportError as e:
    print(f"Erreur d'import FastAPI: {e}")
    print("Création d'une application de base...")
    
    # Application de base si FastAPI n'est pas disponible
    class SimpleApp:
        def __call__(self, environ, start_response):
            status = '200 OK'
            headers = [
                ('Content-type', 'application/json'),
                ('Access-Control-Allow-Origin', '*')
            ]
            start_response(status, headers)
            
            response = {
                "message": "OpenRed Central API - Mode de base",
                "status": "running",
                "version": "2.0.0",
                "note": "Version simplifiée pour O2Switch"
            }
            
            import json
            return [json.dumps(response, ensure_ascii=False).encode('utf-8')]
    
    app = SimpleApp()

# Point d'entrée pour les tests locaux
if __name__ == "__main__":
    print("🚀 OpenRed Central API - Version O2Switch")
    
    try:
        # Essai avec uvicorn si disponible
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info"
        )
    except:
        print("Uvicorn non disponible, utilisez passenger_wsgi.py pour le déploiement")
        print("Application prête pour WSGI")
