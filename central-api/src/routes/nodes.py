# FR: Fichier: nodes.py — Routes pour la gestion des nodes (API centrale)
# EN: File: nodes.py — Routes for node management (central API)
# ES: Archivo: nodes.py — Rutas para la gestión de nodos (API central)
# ZH: 文件: nodes.py — 节点管理的路由（中央 API）

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models.schemas import NodeRegistration, NodeResponse, NodeDiscovery, NodeStatus
from ..services.node_service import NodeService
from ..utils.database import get_db

router = APIRouter()

@router.post("/register", response_model=dict)
async def register_node(
    node_data: NodeRegistration,
    db: Session = Depends(get_db)
):
    """
    Enregistre un nouveau node dans le système central.
    
    # Comments translations (FR/EN/ES/ZH):
    # FR: Enregistre un nouveau node dans le système central.
    # EN: Registers a new node in the central system.
    # ES: Registra un nuevo nodo en el sistema central.
    # ZH: 在中央系统中注册一个新的节点。
    """
    try:
        node_service = NodeService(db)
        result = await node_service.register_node(node_data)
        return {
            "success": True,
            "node_id": result.node_id,
            "message": "Node registered successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/discover", response_model=List[NodeResponse])
async def discover_nodes(
    query: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Découvre des nodes selon les critères spécifiés.
    
    # Comments translations (FR/EN/ES/ZH):
    # FR: Découvre des nodes selon les critères spécifiés.
    # EN: Discovers nodes according to the specified criteria.
    # ES: Descubre nodos según los criterios especificados.
    # ZH: 根据指定的条件发现节点。
    """
    try:
        node_service = NodeService(db)
        discovery_params = NodeDiscovery(
            query=query,
            limit=limit,
            offset=offset
        )
        nodes = await node_service.discover_nodes(discovery_params)
        return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{node_id}/status", response_model=NodeStatus)
async def get_node_status(
    node_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère le statut d'un node spécifique.
    
    # Comments translations (FR/EN/ES/ZH):
    # FR: Récupère le statut d'un node spécifique.
    # EN: Retrieves the status of a specific node.
    # ES: Recupera el estado de un nodo específico.
    # ZH: 获取特定节点的状态。
    """
    try:
        node_service = NodeService(db)
        status = await node_service.get_node_status(node_id)
        if not status:
            raise HTTPException(status_code=404, detail="Node not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{node_id}/heartbeat")
async def update_heartbeat(
    node_id: str,
    db: Session = Depends(get_db)
):
    """
    Met à jour le heartbeat d'un node pour indiquer qu'il est toujours actif.
    
    # Comments translations (FR/EN/ES/ZH):
    # FR: Met à jour le heartbeat d'un node pour indiquer qu'il est toujours actif.
    # EN: Updates a node's heartbeat to indicate it is still active.
    # ES: Actualiza el heartbeat de un nodo para indicar que todavía está activo.
    # ZH: 更新节点的心跳以表明它仍然处于活动状态。
    """
    try:
        node_service = NodeService(db)
        result = await node_service.update_heartbeat(node_id)
        if not result:
            raise HTTPException(status_code=404, detail="Node not found")
        return {"success": True, "message": "Heartbeat updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{node_id}")
async def unregister_node(
    node_id: str,
    db: Session = Depends(get_db)
):
    """
    Désenregistre un node du système central.
    
    # Comments translations (FR/EN/ES/ZH):
    # FR: Désenregistre un node du système central.
    # EN: Unregisters a node from the central system.
    # ES: Dese registra un nodo del sistema central.
    # ZH: 从中央系统注销节点。
    """
    try:
        node_service = NodeService(db)
        result = await node_service.unregister_node(node_id)
        if not result:
            raise HTTPException(status_code=404, detail="Node not found")
        return {"success": True, "message": "Node unregistered successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")