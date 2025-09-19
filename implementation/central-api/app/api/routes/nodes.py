# FR: Fichier: nodes.py — Routes API pour la gestion des nodes (implementation)
# EN: File: nodes.py — API routes for node management (implementation)
# ES: Archivo: nodes.py — Rutas API para gestión de nodos (implementation)
# ZH: 文件: nodes.py — 节点管理的 API 路由 (implementation)

# Routes pour la gestion des nœuds P2P O-Red

from fastapi import APIRouter, HTTPException, Depends, Security, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import logging

from ...core.database import get_db
from ...core.security import verify_ored_token, security
from ...models import Node, User, NodeRegister, NodeResponse, NodeCapabilities
from ...services.node_registry import NodeRegistryService

router = APIRouter()
logger = logging.getLogger(__name__)

# Dépendance pour obtenir le service de registre des nœuds
async def get_node_registry() -> NodeRegistryService:
    from ...main import app
    return app.state.node_registry

@router.post("/register", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def register_node(
    node_data: NodeRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security),
    node_registry: NodeRegistryService = Depends(get_node_registry)
):
    """
    Enregistre un nouveau nœud dans le réseau O-Red P2P
    
    Cette endpoint permet à un nœud de rejoindre le réseau décentralisé O-Red.
    Le nœud doit fournir ses capacités et informations de connexion.
    """
    try:
        # Vérification de l'authentification
        token_data = await verify_ored_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        # Vérification que l'utilisateur existe et correspond au propriétaire
        user_id = token_data.get("sub")
        if user_id != node_data.owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot register node for another user"
            )
        
        # Vérification de la validité des données
        if not await _validate_node_data(node_data, db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node data or configuration"
            )
        
        # Enregistrement du nœud
        new_node = await node_registry.register_node(node_data, db)
        
        # Tâches en arrière-plan
        background_tasks.add_task(_setup_node_monitoring, new_node.node_id)
        background_tasks.add_task(_notify_network_of_new_node, new_node.node_id)
        
        logger.info(f"✅ Nœud {new_node.node_id} enregistré avec succès")
        
        return NodeResponse.model_validate(new_node)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'enregistrement du nœud: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during node registration"
        )

@router.get("/", response_model=List[NodeResponse])
async def list_nodes(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    owner_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    node_registry: NodeRegistryService = Depends(get_node_registry)
):
    """
    Liste les nœuds actifs dans le réseau O-Red
    
    Permet de découvrir les nœuds disponibles pour la communication P2P.
    """
    try:
        nodes = await node_registry.list_nodes(
            skip=skip,
            limit=limit,
            status_filter=status_filter,
            owner_id=owner_id,
            db=db
        )
        
        return [NodeResponse.model_validate(node) for node in nodes]
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des nœuds: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving nodes"
        )

@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    node_registry: NodeRegistryService = Depends(get_node_registry)
):
    """
    Récupère les informations d'un nœud spécifique
    """
    try:
        node = await node_registry.get_node(node_id, db)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )
        
        return NodeResponse.model_validate(node)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération du nœud {node_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving node"
        )

@router.post("/{node_id}/heartbeat")
async def node_heartbeat(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security),
    node_registry: NodeRegistryService = Depends(get_node_registry)
):
    """
    Heartbeat d'un nœud pour maintenir son statut actif
    
    Les nœuds doivent envoyer un heartbeat régulièrement pour rester
    dans la liste des nœuds actifs du réseau.
    """
    try:
        # Vérification de l'authentification
        token_data = await verify_ored_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        # Vérification que l'utilisateur peut envoyer un heartbeat pour ce nœud
        node = await node_registry.get_node(node_id, db)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )
        
        user_id = token_data.get("sub")
        if node.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot send heartbeat for node owned by another user"
            )
        
        # Mise à jour du heartbeat
        await node_registry.update_heartbeat(node_id, db)
        
        return {
            "status": "success",
            "message": "Heartbeat received",
            "timestamp": datetime.utcnow().isoformat(),
            "next_heartbeat_due": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors du heartbeat pour le nœud {node_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing heartbeat"
        )

@router.put("/{node_id}/capabilities")
async def update_node_capabilities(
    node_id: str,
    capabilities: NodeCapabilities,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security),
    node_registry: NodeRegistryService = Depends(get_node_registry)
):
    """
    Met à jour les capacités d'un nœud
    
    Permet à un nœud de modifier ses capacités (IA, stockage, etc.)
    """
    try:
        # Vérification de l'authentification
        token_data = await verify_ored_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        # Vérification de propriété du nœud
        node = await node_registry.get_node(node_id, db)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )
        
        user_id = token_data.get("sub")
        if node.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update capabilities for node owned by another user"
            )
        
        # Mise à jour des capacités
        updated_node = await node_registry.update_capabilities(
            node_id, capabilities.model_dump(), db
        )
        
        return {
            "status": "success",
            "message": "Node capabilities updated",
            "node": NodeResponse.model_validate(updated_node)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à jour des capacités du nœud {node_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating node capabilities"
        )

@router.delete("/{node_id}")
async def unregister_node(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security),
    node_registry: NodeRegistryService = Depends(get_node_registry)
):
    """
    Désenregistre un nœud du réseau O-Red
    """
    try:
        # Vérification de l'authentification
        token_data = await verify_ored_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        # Vérification de propriété du nœud
        node = await node_registry.get_node(node_id, db)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Node not found"
            )
        
        user_id = token_data.get("sub")
        if node.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot unregister node owned by another user"
            )
        
        # Désenregistrement du nœud
        await node_registry.unregister_node(node_id, db)
        
        return {
            "status": "success",
            "message": "Node unregistered successfully",
            "node_id": node_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors du désenregistrement du nœud {node_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error unregistering node"
        )

@router.get("/discovery/peers")
async def discover_peers(
    node_id: str,
    capabilities_filter: Optional[str] = None,
    max_distance: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security),
    node_registry: NodeRegistryService = Depends(get_node_registry)
):
    """
    Découverte de pairs pour un nœud spécifique
    
    Retourne une liste de nœuds compatibles pour établir des connexions P2P.
    """
    try:
        # Vérification de l'authentification
        token_data = await verify_ored_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        # Découverte des pairs
        peers = await node_registry.discover_peers(
            requesting_node_id=node_id,
            capabilities_filter=capabilities_filter,
            max_distance=max_distance,
            db=db
        )
        
        return {
            "status": "success",
            "peers_found": len(peers),
            "peers": [NodeResponse.model_validate(peer) for peer in peers]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la découverte de pairs pour {node_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error discovering peers"
        )

@router.get("/stats/network")
async def get_network_stats(
    db: AsyncSession = Depends(get_db),
    node_registry: NodeRegistryService = Depends(get_node_registry)
):
    """
    Statistiques du réseau O-Red
    
    Informations publiques sur l'état du réseau décentralisé.
    """
    try:
        stats = await node_registry.get_network_stats(db)
        
        return {
            "network_status": "operational",
            "total_nodes": stats["total_nodes"],
            "online_nodes": stats["online_nodes"],
            "offline_nodes": stats["offline_nodes"],
            "total_storage_gb": stats["total_storage"],
            "total_bandwidth_mbps": stats["total_bandwidth"],
            "geographic_distribution": stats["geographic_distribution"],
            "capabilities_distribution": stats["capabilities_distribution"],
            "average_uptime": stats["average_uptime"],
            "network_health_score": stats["health_score"]
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des statistiques réseau: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving network statistics"
        )

# Fonctions utilitaires privées
async def _validate_node_data(node_data: NodeRegister, db: AsyncSession) -> bool:
    """Valide les données d'enregistrement d'un nœud"""
    try:
        # Vérification que l'utilisateur existe
        # TODO: Implémenter la vérification utilisateur
        
        # Vérification de l'unicité de l'IP/Port
        # TODO: Implémenter la vérification d'unicité
        
        # Validation de la clé publique
        # TODO: Implémenter la validation cryptographique
        
        return True
    except Exception:
        return False

async def _setup_node_monitoring(node_id: str):
    """Configure le monitoring pour un nouveau nœud"""
    logger.info(f"🔍 Configuration du monitoring pour le nœud {node_id}")
    # TODO: Implémenter le monitoring

async def _notify_network_of_new_node(node_id: str):
    """Notifie le réseau de l'arrivée d'un nouveau nœud"""
    logger.info(f"📢 Notification du réseau pour le nouveau nœud {node_id}")
    # TODO: Implémenter la notification P2P