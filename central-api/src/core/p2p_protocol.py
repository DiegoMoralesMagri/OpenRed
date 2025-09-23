# Protocol P2P ultra-minimaliste pour OpenRed
# Ultra-minimalist P2P protocol for OpenRed
# Protocolo P2P ultra-minimalista para OpenRed
# OpenRed 超极简P2P协议

import socket
import json
import hashlib
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
import struct

@dataclass
class P2PMessage:
    """
    Message P2P ultra-simple
    Ultra-simple P2P message
    Mensaje P2P ultra-simple
    超简单P2P消息
    """
    type: str                    # 'request', 'response', 'heartbeat', 'data'
    action: str                  # 'handshake', 'compute', 'transfer', etc.
    node_id: str                 # ID du nœud expéditeur
    session_id: str              # ID de session pour suivi
    payload: Dict[str, Any]      # Données utiles
    timestamp: float             # Timestamp Unix
    signature: Optional[str] = None  # Signature optionnelle
    
    def to_bytes(self) -> bytes:
        """Sérialisation ultra-rapide en bytes"""
        data = asdict(self)
        json_str = json.dumps(data, separators=(',', ':'))
        json_bytes = json_str.encode('utf-8')
        
        # Préfixe avec la taille (4 bytes big-endian)
        # Prefix with size (4 bytes big-endian)
        # Prefijo con tamaño (4 bytes big-endian)
        # 大小前缀（4字节大端序）
        size = len(json_bytes)
        return struct.pack('>I', size) + json_bytes
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'P2PMessage':
        """Désérialisation ultra-rapide depuis bytes"""
        json_str = data.decode('utf-8')
        data_dict = json.loads(json_str)
        return cls(**data_dict)

class OpenRedP2PNode:
    """
    Nœud P2P ultra-minimaliste pour OpenRed
    Ultra-minimalist P2P node for OpenRed
    Nodo P2P ultra-minimalista para OpenRed
    OpenRed超极简P2P节点
    """
    
    def __init__(self, node_id: str, host: str = '0.0.0.0', port: int = 9000):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        
        # Gestionnaires d'actions P2P
        # P2P action handlers
        # Manejadores de acciones P2P
        # P2P动作处理程序
        self.handlers: Dict[str, Callable] = {}
        
        # Sessions actives
        # Active sessions
        # Sesiones activas
        # 活动会话
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Connexions vers d'autres nœuds
        # Connections to other nodes
        # Conexiones a otros nodos
        # 到其他节点的连接
        self.peer_connections: Dict[str, socket.socket] = {}
        
        # Statistiques empathiques
        # Empathic statistics
        # Estadísticas empáticas
        # 同理心统计
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'peers_connected': 0,
            'sessions_active': 0,
            'start_time': None
        }
        
        # Gestionnaires par défaut
        # Default handlers
        # Manejadores por defecto
        # 默认处理程序
        self._register_default_handlers()
    
    def register_handler(self, action: str, handler: Callable):
        """
        Enregistrer un gestionnaire pour une action P2P
        Register handler for P2P action
        Registrar manejador para acción P2P
        注册P2P动作处理程序
        """
        self.handlers[action] = handler
    
    def _register_default_handlers(self):
        """Gestionnaires P2P par défaut"""
        
        def handle_handshake(message: P2PMessage, peer_socket: socket.socket) -> P2PMessage:
            """Poignée de main empathique"""
            return P2PMessage(
                type='response',
                action='handshake',
                node_id=self.node_id,
                session_id=message.session_id,
                payload={
                    'status': 'connected',
                    'node_info': {
                        'node_id': self.node_id,
                        'capabilities': ['compute', 'storage', 'relay'],
                        'version': '3.0',
                        'empathy_level': 'maximum'
                    }
                },
                timestamp=time.time()
            )
        
        def handle_ping(message: P2PMessage, peer_socket: socket.socket) -> P2PMessage:
            """Ping empathique"""
            return P2PMessage(
                type='response',
                action='pong',
                node_id=self.node_id,
                session_id=message.session_id,
                payload={
                    'status': 'alive',
                    'uptime': time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
                },
                timestamp=time.time()
            )
        
        def handle_status(message: P2PMessage, peer_socket: socket.socket) -> P2PMessage:
            """Statut du nœud"""
            return P2PMessage(
                type='response',
                action='status',
                node_id=self.node_id,
                session_id=message.session_id,
                payload={
                    'node_stats': self.stats,
                    'active_sessions': len(self.sessions),
                    'connected_peers': len(self.peer_connections)
                },
                timestamp=time.time()
            )
        
        self.register_handler('handshake', handle_handshake)
        self.register_handler('ping', handle_ping)
        self.register_handler('status', handle_status)
    
    def start_server(self):
        """
        Démarrer le serveur P2P
        Start P2P server
        Iniciar servidor P2P
        启动P2P服务器
        """
        print(f"🚀 OpenRed P2P Node {self.node_id} starting on {self.host}:{self.port}")
        
        self.stats['start_time'] = time.time()
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(50)  # Queue empathique
            
            self.running = True
            print(f"✅ P2P Node ready for direct peer connections")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    
                    # Gestion dans un thread séparé
                    # Handle in separate thread
                    # Manejar en hilo separado
                    # 在单独线程中处理
                    peer_thread = threading.Thread(
                        target=self._handle_peer_connection,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    peer_thread.start()
                    
                    self.stats['peers_connected'] += 1
                
                except socket.error as e:
                    if self.running:
                        print(f"Accept error: {e}")
        
        except Exception as e:
            print(f"❌ P2P server startup error: {e}")
        
        finally:
            self.stop_server()
    
    def _handle_peer_connection(self, peer_socket: socket.socket, peer_address):
        """
        Gestion d'une connexion P2P entrante
        Handle incoming P2P connection
        Manejar conexión P2P entrante
        处理传入的P2P连接
        """
        try:
            peer_socket.settimeout(30.0)  # Timeout empathique
            
            while self.running:
                # Réception de la taille du message
                # Receive message size
                # Recibir tamaño del mensaje
                # 接收消息大小
                size_data = peer_socket.recv(4)
                if not size_data:
                    break
                
                message_size = struct.unpack('>I', size_data)[0]
                
                # Réception du message complet
                # Receive complete message
                # Recibir mensaje completo
                # 接收完整消息
                message_data = b''
                while len(message_data) < message_size:
                    chunk = peer_socket.recv(message_size - len(message_data))
                    if not chunk:
                        break
                    message_data += chunk
                
                if len(message_data) != message_size:
                    break
                
                # Traitement du message
                # Process message
                # Procesar mensaje
                # 处理消息
                try:
                    message = P2PMessage.from_bytes(message_data)
                    self.stats['messages_received'] += 1
                    
                    response = self._process_p2p_message(message, peer_socket)
                    
                    if response:
                        response_bytes = response.to_bytes()
                        peer_socket.sendall(response_bytes)
                        self.stats['messages_sent'] += 1
                
                except Exception as e:
                    print(f"Message processing error: {e}")
                    break
        
        except socket.timeout:
            print(f"Peer connection timeout from {peer_address}")
        except Exception as e:
            print(f"Peer connection error: {e}")
        
        finally:
            try:
                peer_socket.close()
            except:
                pass
    
    def _process_p2p_message(self, message: P2PMessage, peer_socket: socket.socket) -> Optional[P2PMessage]:
        """
        Traitement empathique des messages P2P
        Empathic P2P message processing
        Procesamiento empático de mensajes P2P
        同理心P2P消息处理
        """
        try:
            # Vérification du type de message
            # Check message type
            # Verificar tipo de mensaje
            # 检查消息类型
            if message.type == 'request' and message.action in self.handlers:
                handler = self.handlers[message.action]
                return handler(message, peer_socket)
            
            elif message.type == 'data':
                # Traitement des données
                # Data processing
                # Procesamiento de datos
                # 数据处理
                print(f"📦 Received data from {message.node_id}: {message.action}")
                return None  # Pas de réponse automatique pour les données
            
            else:
                # Action inconnue
                # Unknown action
                # Acción desconocida
                # 未知动作
                return P2PMessage(
                    type='response',
                    action='error',
                    node_id=self.node_id,
                    session_id=message.session_id,
                    payload={
                        'error': f"Unknown action: {message.action}",
                        'available_actions': list(self.handlers.keys())
                    },
                    timestamp=time.time()
                )
        
        except Exception as e:
            return P2PMessage(
                type='response',
                action='error',
                node_id=self.node_id,
                session_id=message.session_id,
                payload={
                    'error': f"Processing error: {str(e)}",
                    'message_received': True
                },
                timestamp=time.time()
            )
    
    def connect_to_peer(self, peer_host: str, peer_port: int) -> bool:
        """
        Connexion directe à un autre nœud P2P
        Direct connection to another P2P node
        Conexión directa a otro nodo P2P
        直接连接到另一个P2P节点
        """
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.settimeout(10.0)  # Timeout empathique
            peer_socket.connect((peer_host, peer_port))
            
            peer_id = f"{peer_host}:{peer_port}"
            self.peer_connections[peer_id] = peer_socket
            
            # Handshake initial
            # Initial handshake
            # Handshake inicial
            # 初始握手
            handshake_message = P2PMessage(
                type='request',
                action='handshake',
                node_id=self.node_id,
                session_id=f"session_{int(time.time())}",
                payload={'greeting': 'Hello from OpenRed P2P!'},
                timestamp=time.time()
            )
            
            response = self.send_message_to_peer(peer_id, handshake_message)
            if response and response.payload.get('status') == 'connected':
                print(f"✅ Connected to peer {peer_id}")
                return True
            
        except Exception as e:
            print(f"❌ Failed to connect to {peer_host}:{peer_port}: {e}")
        
        return False
    
    def send_message_to_peer(self, peer_id: str, message: P2PMessage) -> Optional[P2PMessage]:
        """
        Envoi de message direct à un peer
        Direct message sending to peer
        Envío directo de mensaje a peer
        向对等方直接发送消息
        """
        if peer_id not in self.peer_connections:
            return None
        
        try:
            peer_socket = self.peer_connections[peer_id]
            message_bytes = message.to_bytes()
            peer_socket.sendall(message_bytes)
            self.stats['messages_sent'] += 1
            
            # Attendre la réponse si c'est une requête
            # Wait for response if it's a request
            # Esperar respuesta si es una solicitud
            # 如果是请求则等待响应
            if message.type == 'request':
                # Réception de la taille
                # Receive size
                # Recibir tamaño
                # 接收大小
                size_data = peer_socket.recv(4)
                if not size_data:
                    return None
                
                response_size = struct.unpack('>I', size_data)[0]
                
                # Réception du message
                # Receive message
                # Recibir mensaje
                # 接收消息
                response_data = b''
                while len(response_data) < response_size:
                    chunk = peer_socket.recv(response_size - len(response_data))
                    if not chunk:
                        break
                    response_data += chunk
                
                if len(response_data) == response_size:
                    response = P2PMessage.from_bytes(response_data)
                    self.stats['messages_received'] += 1
                    return response
            
            return None
        
        except Exception as e:
            print(f"Error sending message to {peer_id}: {e}")
            # Nettoyage de la connexion défaillante
            # Cleanup failed connection
            # Limpiar conexión fallida
            # 清理失败的连接
            if peer_id in self.peer_connections:
                try:
                    self.peer_connections[peer_id].close()
                except:
                    pass
                del self.peer_connections[peer_id]
            
            return None
    
    def stop_server(self):
        """Arrêt empathique du serveur P2P"""
        print(f"🛑 Stopping P2P Node {self.node_id}...")
        self.running = False
        
        # Fermeture de toutes les connexions
        # Close all connections
        # Cerrar todas las conexiones
        # 关闭所有连接
        for peer_id, peer_socket in self.peer_connections.items():
            try:
                peer_socket.close()
            except:
                pass
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        uptime = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        print(f"📊 P2P Node final stats:")
        print(f"   Messages sent: {self.stats['messages_sent']}")
        print(f"   Messages received: {self.stats['messages_received']}")
        print(f"   Peers connected: {self.stats['peers_connected']}")
        print(f"   Uptime: {uptime:.2f}s")
        print("✅ P2P Node stopped gracefully")

# Export
__all__ = [
    "P2PMessage",
    "OpenRedP2PNode"
]