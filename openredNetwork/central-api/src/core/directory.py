# Gestionnaire d'annuaire ultra-décentralisé pour OpenRed Central API
# Ultra-decentralized directory manager for OpenRed Central API
# Gestor de directorio ultra-descentralizado para OpenRed Central API
# OpenRed Central API 超去中心化目录管理器

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import asyncio
from enum import Enum

from .config import NodeLifeState, directory_config

@dataclass
class NodeRegistration:
    """
    Enregistrement d'un nœud dans l'annuaire
    Node registration in directory
    Registro de nodo en el directorio
    目录中的节点注册
    """
    node_id: str
    ip_address: str
    port: int
    public_key: str
    capabilities: List[str]
    registered_at: datetime
    last_seen: datetime
    expires_at: datetime
    state: NodeLifeState
    failed_checks: int = 0
    last_check_attempt: Optional[datetime] = None
    coma_since: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour sérialisation"""
        data = asdict(self)
        # Conversion des datetime en ISO format
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat() if value else None
            elif isinstance(value, NodeLifeState):
                data[key] = value.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeRegistration':
        """Création depuis un dictionnaire"""
        # Conversion des dates ISO en datetime
        datetime_fields = ['registered_at', 'last_seen', 'expires_at', 'last_check_attempt', 'coma_since']
        for field in datetime_fields:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        if 'state' in data and isinstance(data['state'], str):
            data['state'] = NodeLifeState(data['state'])
            
        return cls(**data)

class UltraDecentralizedDirectory:
    """
    Gestionnaire d'annuaire avec empathie technique intégrée
    Directory manager with built-in technical empathy
    Gestor de directorio con empatía técnica integrada
    内置技术同理心的目录管理器
    """
    
    def __init__(self):
        # Stockage des nœuds en mémoire (sera persisté en base)
        # In-memory node storage (will be persisted to database)
        # Almacenamiento de nodos en memoria (será persistido en base de datos)
        # 内存节点存储（将持久化到数据库）
        self.nodes: Dict[str, NodeRegistration] = {}
        
        # Statistiques de l'annuaire
        # Directory statistics
        # Estadísticas del directorio
        # 目录统计
        self.stats = {
            "total_nodes": 0,
            "active_nodes": 0,
            "coma_nodes": 0,
            "pending_checks": 0
        }
    
    async def register_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enregistrement d'un nouveau nœud avec empathie maximale
        Register new node with maximum empathy
        Registrar nuevo nodo con máxima empatía
        以最大同理心注册新节点
        """
        node_id = node_data["node_id"]
        current_time = datetime.utcnow()
        
        # Vérification si le nœud existe déjà
        # Check if node already exists
        # Verificar si el nodo ya existe
        # 检查节点是否已存在
        if node_id in self.nodes:
            existing_node = self.nodes[node_id]
            
            # Si le nœud était en coma, réveil empathique !
            # If node was in coma, empathic awakening!
            # Si el nodo estaba en coma, ¡despertar empático!
            # 如果节点处于昏迷状态，同理心觉醒！
            if existing_node.state == NodeLifeState.COMA:
                return await self._revive_from_coma(node_id, node_data)
        
        # Vérification de la limite
        # Check limit
        # Verificar límite
        # 检查限制
        if len(self.nodes) >= directory_config.max_nodes:
            return {
                "success": False,
                "error": "Directory at capacity",
                "max_nodes": directory_config.max_nodes,
                "suggestion": "Contact administrator for new instance"
            }
        
        # Création du nouvel enregistrement
        # Create new registration
        # Crear nuevo registro
        # 创建新注册
        registration = NodeRegistration(
            node_id=node_id,
            ip_address=node_data["ip_address"],
            port=node_data["port"],
            public_key=node_data["public_key"],
            capabilities=node_data.get("capabilities", []),
            registered_at=current_time,
            last_seen=current_time,
            expires_at=current_time + timedelta(seconds=directory_config.initial_registration_lifetime),
            state=NodeLifeState.ACTIVE
        )
        
        self.nodes[node_id] = registration
        self._update_stats()
        
        return {
            "success": True,
            "node_id": node_id,
            "registered_at": registration.registered_at.isoformat(),
            "expires_at": registration.expires_at.isoformat(),
            "next_check": (current_time + timedelta(seconds=directory_config.heartbeat_check_interval)).isoformat(),
            "message": "Node registered successfully with 1-year visibility"
        }
    
    async def _revive_from_coma(self, node_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Réveil empathique d'un nœud en coma
        Empathic revival of a coma node
        Despertar empático de un nodo en coma
        昏迷节点的同理心复苏
        """
        current_time = datetime.utcnow()
        node = self.nodes[node_id]
        
        # Mise à jour avec les nouvelles informations
        # Update with new information
        # Actualizar con nueva información
        # 用新信息更新
        node.ip_address = node_data["ip_address"]
        node.port = node_data["port"]
        node.public_key = node_data.get("public_key", node.public_key)
        node.capabilities = node_data.get("capabilities", node.capabilities)
        node.last_seen = current_time
        node.expires_at = current_time + timedelta(seconds=directory_config.initial_registration_lifetime)
        node.state = NodeLifeState.ACTIVE
        node.failed_checks = 0
        node.coma_since = None
        
        coma_duration = current_time - node.coma_since if node.coma_since else timedelta(0)
        
        self._update_stats()
        
        return {
            "success": True,
            "node_id": node_id,
            "message": "Welcome back! Node revived from coma",
            "coma_duration_days": coma_duration.days,
            "registered_at": node.registered_at.isoformat(),
            "revived_at": current_time.isoformat(),
            "expires_at": node.expires_at.isoformat()
        }
    
    async def discover_nodes(self, criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Découverte de nœuds avec filtrage intelligent
        Node discovery with intelligent filtering
        Descubrimiento de nodos con filtrado inteligente
        具有智能过滤的节点发现
        """
        criteria = criteria or {}
        current_time = datetime.utcnow()
        
        # Filtrage des nœuds actifs seulement
        # Filter only active nodes
        # Filtrar solo nodos activos
        # 仅过滤活动节点
        active_nodes = {
            node_id: node for node_id, node in self.nodes.items()
            if node.state == NodeLifeState.ACTIVE and node.expires_at > current_time
        }
        
        # Filtrage par capacités si spécifié
        # Filter by capabilities if specified
        # Filtrar por capacidades si se especifica
        # 如果指定则按能力过滤
        if "capabilities" in criteria:
            required_caps = set(criteria["capabilities"])
            active_nodes = {
                node_id: node for node_id, node in active_nodes.items()
                if required_caps.issubset(set(node.capabilities))
            }
        
        # Filtrage géographique (future extension)
        # Geographic filtering (future extension)
        # Filtrado geográfico (extensión futura)
        # 地理过滤（未来扩展）
        
        # Préparation de la réponse
        # Prepare response
        # Preparar respuesta
        # 准备响应
        discovered_nodes = []
        for node_id, node in active_nodes.items():
            discovered_nodes.append({
                "node_id": node_id,
                "ip_address": node.ip_address,
                "port": node.port,
                "capabilities": node.capabilities,
                "last_seen": node.last_seen.isoformat(),
                "uptime_days": (current_time - node.registered_at).days
            })
        
        return {
            "success": True,
            "total_discovered": len(discovered_nodes),
            "nodes": discovered_nodes,
            "directory_stats": self.get_stats()
        }
    
    async def heartbeat_check(self, node_id: str) -> Dict[str, Any]:
        """
        Vérification de vie empathique d'un nœud
        Empathic life check of a node
        Verificación de vida empática de un nodo
        节点的同理心生命检查
        """
        if node_id not in self.nodes:
            return {"success": False, "error": "Node not found"}
        
        node = self.nodes[node_id]
        current_time = datetime.utcnow()
        
        # Mise à jour de la dernière vérification
        # Update last check
        # Actualizar última verificación
        # 更新最后检查
        node.last_check_attempt = current_time
        node.last_seen = current_time
        
        # Logique empathique selon l'état
        # Empathic logic based on state
        # Lógica empática según el estado
        # 基于状态的同理心逻辑
        if node.state == NodeLifeState.ACTIVE:
            # Renouvellement automatique
            # Automatic renewal
            # Renovación automática
            # 自动续期
            node.expires_at = current_time + timedelta(seconds=directory_config.initial_registration_lifetime)
            return {
                "success": True,
                "message": "Heartbeat confirmed, registration renewed",
                "expires_at": node.expires_at.isoformat()
            }
        
        elif node.state in [NodeLifeState.RETRY_48H, NodeLifeState.RETRY_2W, NodeLifeState.RETRY_2M]:
            # Retour à la vie active !
            # Return to active life!
            # ¡Regreso a la vida activa!
            # 回到活跃生活！
            node.state = NodeLifeState.ACTIVE
            node.failed_checks = 0
            node.expires_at = current_time + timedelta(seconds=directory_config.initial_registration_lifetime)
            
            return {
                "success": True,
                "message": "Node recovered! Back to active state",
                "previous_failed_checks": node.failed_checks,
                "expires_at": node.expires_at.isoformat()
            }
        
        elif node.state == NodeLifeState.COMA:
            # Réveil miraculeux du coma !
            # Miraculous awakening from coma!
            # ¡Despertar milagroso del coma!
            # 奇迹般地从昏迷中醒来！
            return await self._revive_from_coma(node_id, {
                "ip_address": node.ip_address,
                "port": node.port,
                "capabilities": node.capabilities
            })
    
    async def failed_heartbeat(self, node_id: str) -> Dict[str, Any]:
        """
        Gestion empathique d'un échec de heartbeat
        Empathic handling of heartbeat failure
        Manejo empático de falla de heartbeat
        心跳失败的同理心处理
        """
        if node_id not in self.nodes:
            return {"success": False, "error": "Node not found"}
        
        node = self.nodes[node_id]
        current_time = datetime.utcnow()
        
        node.last_check_attempt = current_time
        node.failed_checks += 1
        
        # Logique progressive empathique
        # Progressive empathic logic
        # Lógica progresiva empática
        # 渐进式同理心逻辑
        if node.failed_checks == 1:
            # Premier échec - patience
            # First failure - patience
            # Primer fallo - paciencia
            # 第一次失败 - 耐心
            if node.state == NodeLifeState.ACTIVE:
                node.state = NodeLifeState.FAILED_FIRST_CHECK
                return {
                    "success": True,
                    "message": "First check failed, giving more time (6 months)",
                    "state": node.state.value,
                    "next_check": (current_time + timedelta(seconds=directory_config.heartbeat_check_interval)).isoformat()
                }
        
        elif node.failed_checks == 2:
            # Deuxième échec - début des retry
            # Second failure - start retry
            # Segundo fallo - inicio de reintentos
            # 第二次失败 - 开始重试
            node.state = NodeLifeState.RETRY_48H
            return {
                "success": True,
                "message": "Second check failed, starting retry sequence (48h)",
                "state": node.state.value,
                "retry_in_hours": 48
            }
        
        else:
            # Progression dans les retry ou mise en coma
            # Progress in retry or enter coma
            # Progresión en reintentos o entrada en coma
            # 重试进展或进入昏迷
            return await self._progress_retry_sequence(node_id)
    
    async def _progress_retry_sequence(self, node_id: str) -> Dict[str, Any]:
        """
        Progression empathique dans la séquence de retry
        Empathic progression in retry sequence
        Progresión empática en secuencia de reintentos
        重试序列中的同理心进展
        """
        node = self.nodes[node_id]
        current_time = datetime.utcnow()
        
        if node.state == NodeLifeState.RETRY_48H:
            node.state = NodeLifeState.RETRY_2W
            return {
                "success": True,
                "message": "Escalating to 2-week retry (still hoping...)",
                "state": node.state.value,
                "retry_in_days": 14
            }
        
        elif node.state == NodeLifeState.RETRY_2W:
            node.state = NodeLifeState.RETRY_2M
            return {
                "success": True,
                "message": "Final attempt: 2-month retry (don't give up!)",
                "state": node.state.value,
                "retry_in_days": 60
            }
        
        elif node.state == NodeLifeState.RETRY_2M:
            # Mise en coma avec compassion
            # Enter coma with compassion
            # Entrar en coma con compasión
            # 怀着同情心进入昏迷
            node.state = NodeLifeState.COMA
            node.coma_since = current_time
            
            return {
                "success": True,
                "message": "Node entered compassionate coma (preserving identity for 2 years)",
                "state": node.state.value,
                "coma_duration_max_years": 2,
                "identity_preserved": True
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques de l'annuaire"""
        self._update_stats()
        return self.stats
    
    def _update_stats(self):
        """Mise à jour des statistiques"""
        current_time = datetime.utcnow()
        
        active = sum(1 for node in self.nodes.values() 
                    if node.state == NodeLifeState.ACTIVE and node.expires_at > current_time)
        coma = sum(1 for node in self.nodes.values() 
                  if node.state == NodeLifeState.COMA)
        pending = sum(1 for node in self.nodes.values() 
                     if node.state.value.startswith('pending') or node.state.value.startswith('retry'))
        
        self.stats = {
            "total_nodes": len(self.nodes),
            "active_nodes": active,
            "coma_nodes": coma,
            "pending_checks": pending,
            "last_updated": current_time.isoformat()
        }

# Instance globale de l'annuaire
# Global directory instance
# Instancia global del directorio
# 全局目录实例
directory = UltraDecentralizedDirectory()

# Export
__all__ = [
    "NodeRegistration",
    "UltraDecentralizedDirectory",
    "NodeLifeState",
    "directory"
]