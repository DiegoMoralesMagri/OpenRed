# FR: Fichier: schemas.py — Schémas Pydantic pour les modèles de données
# EN: File: schemas.py — Pydantic schemas for data models
# ES: Archivo: schemas.py — Esquemas Pydantic para modelos de datos
# ZH: 文件: schemas.py — 数据模型的 Pydantic 模式

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class NodeRegistration(BaseModel):
    username: str
    display_name: Optional[str] = None
    server_url: str
    public_key: str
    version: Optional[str] = "1.0.0"
    capabilities: Optional[List[str]] = []
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (with _ and - allowed)')
        return v
    
    @validator('server_url')
    def server_url_valid(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Server URL must start with http:// or https://')
        return v

class NodeResponse(BaseModel):
    node_id: str
    username: str
    display_name: Optional[str]
    server_url: str
    status: str
    last_heartbeat: datetime
    created_at: datetime
    version: Optional[str]
    capabilities: Optional[List[str]]

class NodeDiscovery(BaseModel):
    query: Optional[str] = None
    node_ids: Optional[List[str]] = None
    usernames: Optional[List[str]] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0

class MessageRoute(BaseModel):
    from_node_id: str
    to_node_id: str
    message_type: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    message_id: str
    status: str
    created_at: datetime
    delivered_at: Optional[datetime] = None

class NodeStatus(BaseModel):
    node_id: str
    status: str
    last_heartbeat: datetime
    is_online: bool