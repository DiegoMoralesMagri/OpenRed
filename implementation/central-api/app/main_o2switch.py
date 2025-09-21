#!/usr/bin/env python3
# FR: Version optimisée pour O2Switch avec WSGI
# EN: O2Switch optimized version with WSGI
# ES: Versión optimizada para O2Switch con WSGI
# ZH: O2Switch优化版本，支持WSGI

"""
OpenRed Central API - Version O2Switch
Version simplifiée compatible avec l'hébergement partagé O2Switch
"""

import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any

# Configuration de base pour O2Switch
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('O2SWITCH_MODE', 'True')

# Ajouter le répertoire de l'app au Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError as e:
    # Fallback pour environnements avec dépendances limitées
    print(f"Import error: {e}")
    print("Veuillez installer les dépendances: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# Configuration simple pour O2Switch
class SimpleConfig:
    """Configuration simplifiée pour O2Switch"""
    
    def __init__(self):
        self.APP_NAME = "O-Red Central API"
        self.VERSION = "1.0.0-o2switch"
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', 8000))
        
        # Sécurité
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret-key')
        if self.SECRET_KEY == 'change-this-secret-key':
            print("⚠️  WARNING: Utilisez une vraie clé secrète en production!")
        
        # CORS simple pour O2Switch
        self.ALLOWED_ORIGINS = self._parse_list(os.getenv('ALLOWED_ORIGINS', '["*"]'))
        self.ALLOWED_HOSTS = self._parse_list(os.getenv('ALLOWED_HOSTS', '["*"]'))
        
        # Base de données
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./openred.db')
        
        # Domaine
        self.DOMAIN = os.getenv('DOMAIN', 'localhost')
        self.API_DOMAIN = os.getenv('API_DOMAIN', 'api.localhost')
    
    def _parse_list(self, value: str) -> List[str]:
        """Parse une liste depuis une string"""
        try:
            import json
            return json.loads(value)
        except:
            return [value.strip('"\'')]

# Configuration globale
config = SimpleConfig()

# Modèles Pydantic simples
class NodeRegistration(BaseModel):
    """Modèle pour l'enregistrement d'un nœud"""
    node_id: str
    name: str
    description: Optional[str] = None
    endpoint: str
    capabilities: List[str] = []

class NodeResponse(BaseModel):
    """Réponse d'enregistrement de nœud"""
    success: bool
    node_id: str
    message: str
    registered_at: str

class HealthResponse(BaseModel):
    """Réponse de santé"""
    status: str
    timestamp: str
    version: str
    o2switch_mode: bool

# Application FastAPI
app = FastAPI(
    title=config.APP_NAME,
    description="API centrale OpenRed optimisée pour O2Switch",
    version=config.VERSION,
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None
)

# Middleware CORS simple
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Storage simple en mémoire pour les nœuds (en production, utilisez une vraie DB)
nodes_storage: Dict[str, Dict[str, Any]] = {}

# Routes principales
@app.get("/", response_model=dict)
async def root():
    """Point d'entrée principal"""
    return {
        "message": "OpenRed Central API - O2Switch",
        "version": config.VERSION,
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "o2switch_mode": True,
        "nodes_count": len(nodes_storage),
        "docs_url": "/docs" if config.DEBUG else "disabled"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de santé"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=config.VERSION,
        o2switch_mode=True
    )

@app.get("/diagnostic")
async def diagnostic():
    """Diagnostic système pour O2Switch"""
    import platform
    
    diagnostic_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "working_directory": os.getcwd(),
        "environment": {
            "HOST": config.HOST,
            "PORT": config.PORT,
            "DEBUG": config.DEBUG,
            "DOMAIN": config.DOMAIN,
            "DATABASE_URL": config.DATABASE_URL[:50] + "..." if len(config.DATABASE_URL) > 50 else config.DATABASE_URL
        },
        "modules_status": {},
        "file_permissions": {},
        "nodes_registered": len(nodes_storage)
    }
    
    # Test des modules
    required_modules = ['fastapi', 'uvicorn', 'pydantic']
    for module in required_modules:
        try:
            __import__(module)
            diagnostic_info["modules_status"][module] = "✅ OK"
        except ImportError:
            diagnostic_info["modules_status"][module] = "❌ MISSING"
    
    # Test des permissions de fichier
    try:
        test_file = '/tmp/test_openred.txt'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        diagnostic_info["file_permissions"]["tmp_write"] = "✅ OK"
    except Exception as e:
        diagnostic_info["file_permissions"]["tmp_write"] = f"❌ ERROR: {str(e)}"
    
    return diagnostic_info

# Routes API pour les nœuds
@app.post("/api/v1/nodes/register", response_model=NodeResponse)
async def register_node(node: NodeRegistration):
    """Enregistrer un nouveau nœud"""
    try:
        # Validation simple
        if node.node_id in nodes_storage:
            raise HTTPException(status_code=409, detail="Node already registered")
        
        # Enregistrement
        nodes_storage[node.node_id] = {
            "node_id": node.node_id,
            "name": node.name,
            "description": node.description,
            "endpoint": node.endpoint,
            "capabilities": node.capabilities,
            "registered_at": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        return NodeResponse(
            success=True,
            node_id=node.node_id,
            message="Node registered successfully",
            registered_at=nodes_storage[node.node_id]["registered_at"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.get("/api/v1/nodes", response_model=dict)
async def list_nodes():
    """Lister tous les nœuds enregistrés"""
    return {
        "nodes": list(nodes_storage.values()),
        "total": len(nodes_storage),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/nodes/{node_id}", response_model=dict)
async def get_node(node_id: str):
    """Obtenir les détails d'un nœud"""
    if node_id not in nodes_storage:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return nodes_storage[node_id]

@app.delete("/api/v1/nodes/{node_id}", response_model=dict)
async def unregister_node(node_id: str):
    """Désenregistrer un nœud"""
    if node_id not in nodes_storage:
        raise HTTPException(status_code=404, detail="Node not found")
    
    removed_node = nodes_storage.pop(node_id)
    return {
        "success": True,
        "message": f"Node {node_id} unregistered",
        "node": removed_node,
        "timestamp": datetime.utcnow().isoformat()
    }

# Gestion des erreurs
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested OpenRed resource was not found",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An error occurred in the OpenRed API",
            "timestamp": datetime.utcnow().isoformat(),
            "o2switch_mode": True
        }
    )

# Point d'entrée WSGI pour cPanel
application = app

# Pour les tests locaux
if __name__ == "__main__":
    print(f"🚀 Démarrage OpenRed API v{config.VERSION} (Mode O2Switch)")
    print(f"📍 URL: http://{config.HOST}:{config.PORT}")
    print(f"🔧 Debug: {config.DEBUG}")
    print(f"📊 Documentation: http://{config.HOST}:{config.PORT}/docs" if config.DEBUG else "📊 Documentation: disabled in production")
    
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level="info" if config.DEBUG else "warning"
    )