# FR: Fichier: messages.py — Routes pour le routage de messages
# EN: File: messages.py — Routes for message routing
# ES: Archivo: messages.py — Rutas para enrutamiento de mensajes
# ZH: 文件: messages.py — 消息路由的路由

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models.schemas import MessageRoute, MessageResponse
from ..services.message_service import MessageService
from ..utils.database import get_db

router = APIRouter()

@router.post("/route", response_model=MessageResponse)
async def route_message(
    message_data: MessageRoute,
    db: Session = Depends(get_db)
):
    """
    Route un message entre deux nodes via le système central.
    """
    try:
        message_service = MessageService(db)
        result = await message_service.route_message(message_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{message_id}/status", response_model=MessageResponse)
async def get_message_status(
    message_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère le statut d'un message.
    """
    try:
        message_service = MessageService(db)
        status = await message_service.get_message_status(message_id)
        if not status:
            raise HTTPException(status_code=404, detail="Message not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/pending/{node_id}")
async def get_pending_messages(
    node_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Récupère les messages en attente pour un node.
    """
    try:
        message_service = MessageService(db)
        messages = await message_service.get_pending_messages(node_id, limit)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")