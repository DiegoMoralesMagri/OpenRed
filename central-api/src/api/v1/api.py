"""
Router principal API v1 pour OpenRed Central API
Main API v1 router for OpenRed Central API
Router principal API v1 para OpenRed Central API
OpenRed 中央 API 的主要 API v1 路由器
"""

from fastapi import APIRouter
from src.api.v1.endpoints import auth, nodes, messages, health

# Router principal API v1 | Main API v1 router | Router principal API v1 | 主要 API v1 路由器
api_router = APIRouter()

# Inclusion des sous-routers | Include sub-routers | Inclusión de sub-routers | 包含子路由器

# Authentification | Authentication | Autenticación | 认证
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["Authentication | Autenticación | 认证"]
)

# Gestion des nœuds | Node management | Gestión de nodos | 节点管理  
api_router.include_router(
    nodes.router, 
    prefix="/nodes", 
    tags=["Nodes | Nodos | 节点"]
)

# Messagerie | Messaging | Mensajería | 消息传递
api_router.include_router(
    messages.router, 
    prefix="/messages", 
    tags=["Messages | Mensajes | 消息"]
)

# Monitoring et santé | Monitoring and health | Monitoreo y salud | 监控和健康
api_router.include_router(
    health.router, 
    prefix="/health", 
    tags=["Health | Salud | 健康"]
)
