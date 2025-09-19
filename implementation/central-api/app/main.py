# FR: Fichier: main.py — Entrypoint FastAPI (implementation/central-api)
# EN: File: main.py — FastAPI entrypoint (implementation/central-api)
# ES: Archivo: main.py — Punto de entrada FastAPI (implementation/central-api)
# ZH: 文件: main.py — FastAPI 入口 (implementation/central-api)

# O-Red Central API
# API centrale pour la coordination du réseau O-Red décentralisé

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Optional
import asyncio
from datetime import datetime

from .core.config import settings
from .core.security import verify_ored_token, create_ored_token
from .core.database import init_db, close_db
from .api.routes import nodes, users, messages, ai, store, search
from .services.node_registry import NodeRegistryService
from .services.federation import FederationService
from .services.analytics import AnalyticsService

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Gestionnaire de contexte pour l'initialisation/fermeture
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    try:
        # Initialisation
        logger.info("🚀 Initialisation de l'API centrale O-Red...")
        
        # Base de données
        await init_db()
        logger.info("✅ Base de données initialisée")
        
        # Services
        app.state.node_registry = NodeRegistryService()
        app.state.federation = FederationService()
        app.state.analytics = AnalyticsService()
        
        # Démarrage des services de fond
        asyncio.create_task(app.state.node_registry.start_heartbeat_monitor())
        asyncio.create_task(app.state.federation.start_sync_service())
        
        logger.info("🌐 Services O-Red démarrés avec succès")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        raise
    finally:
        # Nettoyage
        logger.info("🔄 Arrêt des services O-Red...")
        await close_db()
        logger.info("✅ Services arrêtés proprement")

# Création de l'application FastAPI
app = FastAPI(
    title="O-Red Central API",
    description="""
    API centrale pour l'écosystème O-Red décentralisé.
    
    ## Fonctionnalités
    
    * **Enregistrement de nœuds** - Découverte et coordination P2P
    * **Authentification O-RedID** - Système d'identité décentralisée
    * **Messagerie fédérée** - Communication inter-nœuds sécurisée
    * **Coordination IA** - O-RedMind distribué
    * **Marketplace** - O-RedStore décentralisée
    * **Recherche** - O-RedSearch distribuée
    
    ## Sécurité
    
    * Cryptographie post-quantique
    * Zero-knowledge authentication
    * End-to-end encryption
    * Privacy by design
    """,
    version="1.0.0",
    contact={
        "name": "O-Red Community",
        "url": "https://github.com/o-red/ecosystem",
        "email": "contact@o-red.org"
    },
    license_info={
        "name": "GNU Affero General Public License v3.0",
        "url": "https://www.gnu.org/licenses/agpl-3.0.html"
    },
    lifespan=lifespan
)

# Configuration CORS sécurisée
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Protection contre les attaques Host Header
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Schéma de sécurité
security = HTTPBearer()

# Endpoints de santé
@app.get("/", tags=["Health"])
async def root():
    """Point d'entrée principal de l'API"""
    return {
        "message": "O-Red Central API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "ecosystem": {
            "nodes_registered": await app.state.node_registry.get_node_count(),
            "federation_status": "active",
            "ai_network_status": "operational"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Vérification de santé détaillée"""
    try:
        # Vérification des services
        db_status = await check_database_health()
        federation_status = await app.state.federation.health_check()
        ai_status = await check_ai_network_health()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": db_status,
                "federation": federation_status,
                "ai_network": ai_status,
                "node_registry": "operational"
            },
            "metrics": {
                "active_nodes": await app.state.node_registry.get_active_node_count(),
                "total_messages": await get_message_count(),
                "ai_requests_24h": await app.state.analytics.get_ai_requests_count()
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/metrics", tags=["Monitoring"])
async def get_metrics(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Métriques détaillées (accès authentifié)"""
    # Vérification de l'authentification
    token_data = await verify_ored_token(credentials.credentials)
    if not token_data or not token_data.get("admin_access"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return await app.state.analytics.get_comprehensive_metrics()

# Inclusion des routes
app.include_router(nodes.router, prefix="/api/v1/nodes", tags=["Nodes"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["Messages"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["O-RedMind"])
app.include_router(store.router, prefix="/api/v1/store", tags=["O-RedStore"])
app.include_router(search.router, prefix="/api/v1/search", tags=["O-RedSearch"])

# Gestionnaires d'erreur globaux
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Resource not found",
        "message": "The requested O-Red resource was not found",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.exception_handler(500)
async def server_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal server error",
        "message": "An error occurred in the O-Red central API",
        "timestamp": datetime.utcnow().isoformat()
    }

# Fonctions utilitaires
async def check_database_health():
    """Vérification de santé de la base de données"""
    # TODO: Implémenter la vérification DB
    return "operational"

async def check_ai_network_health():
    """Vérification de santé du réseau IA"""
    # TODO: Implémenter la vérification réseau IA
    return "operational"

async def get_message_count():
    """Obtenir le nombre total de messages"""
    # TODO: Implémenter le comptage des messages
    return 0

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )