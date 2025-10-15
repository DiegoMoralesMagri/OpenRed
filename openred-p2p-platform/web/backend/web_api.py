# === OpenRed P2P Platform - Web API Backend ===
# Interface web révolutionnaire pour gestion constellation P2P
# FastAPI + WebSockets pour temps réel

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Request, Depends, Cookie, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import json
import time
import asyncio
import threading
from typing import Dict, List, Optional
from dataclasses import asdict
import uvicorn
import os
import sys
import uuid
from datetime import datetime
import glob

# Import du nœud P2P principal
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from openred_p2p_node import OpenRedP2PNode
from friendship_protocol import FriendshipProtocol, FriendshipPermissions, PermissionLevel, FriendshipStatus
from social_messaging import DistributedMessaging, MessageType
from conditional_urn_sharing import ConditionalURNSharing, URNAccessLevel
from simple_protocol_helper import initialize_simple_protocol, send_friendship_request_simple, get_simple_protocol_status, process_pending_friendship_requests
from user_profile import UserProfileManager, UserProfile, FriendGroup, PrivacyLevel
from authentic_phantom_urn_system import AuthenticPhantomUrnSystem
from phantom_projection_server import PhantomProjectionServer

# Import du système d'authentification
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
from auth import OpenRedAuth

# Import du protocole spider pour découverte Internet
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'internet_discovery'))
try:
    from spider_protocol import InternetSpiderProtocol
    from spider_handler import SpiderProtocolHandler
    SPIDER_AVAILABLE = True
    print("🕷️ Internet Spider Protocol available")
except ImportError as e:
    SPIDER_AVAILABLE = False
    print(f"[WARNING] Internet Spider Protocol not available: {e}")

app = FastAPI(
    title="OpenRed P2P Platform API",
    description="Interface web révolutionnaire pour constellation P2P décentralisée",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configuration CORS pour développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production: domaines spécifiques
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance globale du nœud P2P
p2p_node: Optional[OpenRedP2PNode] = None
websocket_connections: List[WebSocket] = []

# Systèmes sociaux
friendship_system: Optional[FriendshipProtocol] = None
messaging_system: Optional[DistributedMessaging] = None
urn_sharing_system: Optional[ConditionalURNSharing] = None

# Système de gestion d'images URN
phantom_urn_system: Optional[AuthenticPhantomUrnSystem] = None
projection_server: Optional[PhantomProjectionServer] = None
async_processor = None

# Gestionnaire de profil utilisateur
profile_manager: Optional[UserProfileManager] = None

# Gestionnaire d'authentification
auth_manager: Optional[OpenRedAuth] = None

# Système de découverte Internet Spider
internet_spider = None
spider_handler = None

class WebSocketManager:
    """Gestionnaire WebSocket pour mises à jour temps réel"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔗 WebSocket connected. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"🔗 WebSocket disconnected. Total: {len(self.active_connections)}")
        
    async def broadcast(self, message: dict):
        """Diffuse message à tous les clients connectés"""
        if not self.active_connections:
            return
            
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                print(f"[WARNING] WebSocket send error: {e}")
                disconnected.append(connection)
                
        # Nettoyer connexions fermées
        for conn in disconnected:
            self.disconnect(conn)

# Gestionnaire WebSocket global
ws_manager = WebSocketManager()

# === Système d'Authentification ===

def get_auth_token(request: Request) -> Optional[str]:
    """Récupère le token d'authentification depuis les cookies ou headers"""
    # Essayer depuis le cookie d'abord
    token = request.cookies.get("openred_token")
    
    # Sinon essayer depuis l'en-tête Authorization
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Retirer "Bearer "
    
    return token

def verify_auth(request: Request) -> str:
    """Vérifie l'authentification et retourne le nom d'utilisateur"""
    global auth_manager
    
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Auth system not initialized")
    
    token = get_auth_token(request)
    
    if not token or not auth_manager.verify_session(token):
        raise HTTPException(
            status_code=401, 
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    username = auth_manager.get_username(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return username

def verify_auth_optional(request: Request) -> Optional[str]:
    """Vérifie l'authentification de manière optionnelle"""
    try:
        return verify_auth(request)
    except HTTPException:
        return None

def get_current_user_id(request: Request) -> Optional[str]:
    """Récupère l'ID de l'utilisateur actuel"""
    username = verify_auth_optional(request)
    if username and p2p_node:
        # Utiliser le fingerprint du nœud comme user_id
        return p2p_node.lighthouse.fingerprint
    return None

# === P2P Functions ===

async def send_friendship_request_p2p(target_fingerprint: str, request) -> bool:
    """Envoie demande d'amitié via P2P"""
    global p2p_node
    
    if not p2p_node:
        print(f"[ERROR] P2P node not available")
        return False
    
    try:
        print(f"🔍 Attempting to send friendship request to {target_fingerprint}")
        
        # Vérifier si le nœud cible est découvert
        discovered = p2p_node.lighthouse.get_discovered_nodes()
        print(f"🔍 Discovered nodes: {list(discovered.keys())}")
        
        if target_fingerprint not in discovered:
            print(f"[ERROR] Target node {target_fingerprint} not discovered")
            return False
        
        # Établir connexion P2P si nécessaire
        target_info = discovered[target_fingerprint]
        target_ip = target_info["ip"]
        beacon = target_info["beacon"]
        target_port = beacon.p2p_endpoint["port"]  # Extraire le port du dictionnaire
        
        print(f"🔍 Target info: IP={target_ip}, Port={target_port}")
        
        # Préparer données de la demande selon le format attendu
        request_data = {
            "request_id": request.request_id,
            "from_fingerprint": request.from_fingerprint,
            "to_fingerprint": request.to_fingerprint,
            "from_node_id": request.from_node_id,
            "to_node_id": request.to_node_id,
            "message": request.message,
            "timestamp": request.timestamp,
            "signature": request.signature,
            "requested_permissions": {
                "messaging": request.requested_permissions.messaging,
                "urn_access": request.requested_permissions.urn_access,
                "photo_sharing": request.requested_permissions.photo_sharing,
                "file_sharing": request.requested_permissions.file_sharing,
                "presence_info": request.requested_permissions.presence_info
            }
        }
        
        # Utiliser le protocole simple 3 phases
        print(f"[UPLOAD] Using Simple 3-Phase Protocol for friendship request")
        success = await send_friendship_request_simple(
            target_fingerprint=target_fingerprint,
            target_ip=target_ip,
            target_port=target_port,
            request_data=request_data
        )
        
        if success:
            print(f"[OK] Friendship request sent successfully via Simple Protocol")
        else:
            print(f"[ERROR] Failed to send friendship request via Simple Protocol")
            
        return success
        
        # Approche simplifiée : envoyer via socket TCP direct
        print(f"� Attempting direct TCP connection to {target_ip}:{target_port}")
        
        import socket
        import json
        
        try:
            # Connexion TCP directe
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # Timeout de 10 secondes
            sock.connect((target_ip, target_port))
            
            # Envoyer données JSON
            message_json = json.dumps(request_data)
            sock.send(message_json.encode())
            
            # Attendre réponse
            response = sock.recv(1024)
            sock.close()
            
            print(f"[OK] Friendship request sent directly to {target_fingerprint}")
            print(f"📨 Response: {response.decode()}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Direct TCP connection failed: {e}")
            
            # Fallback: utiliser le système P2P existant mais avec retry
            print(f"🔄 Trying P2P fallback...")
            
            session_id = p2p_node.p2p_connection.connect_to_peer(target_ip, target_port, target_fingerprint)
            
            if session_id:
                print(f"[OK] P2P connection established, session_id: {session_id}")
                
                # Attendre un peu pour que la connexion soit stable
                await asyncio.sleep(1)
                
                # Envoyer via P2P
                success = p2p_node.p2p_connection.send_secure_message(session_id, request_data)
                
                if success:
                    print(f"[OK] Friendship request sent via P2P to {target_fingerprint}")
                else:
                    print(f"[ERROR] Failed to send friendship request via P2P")
                    
                return success
            else:
                print(f"[ERROR] Both direct and P2P connections failed")
                return False
        
    except Exception as e:
        print(f"[ERROR] Error sending friendship request P2P: {e}")
        import traceback
        traceback.print_exc()
        return False

async def handle_p2p_message(session_id: str, message: Dict):
    """Handler pour messages P2P reçus"""
    global friendship_system
    
    try:
        print(f"📨 Received P2P message: type={message.get('type')}, session={session_id}")
        
        if message.get("type") == "friendship_request":
            print(f"👥 Processing friendship request from {message.get('from_node_id')}")
            print(f"   From: {message.get('from_fingerprint')}")
            print(f"   To: {message.get('to_fingerprint')}")
            print(f"   Message: {message.get('message')}")
            
            if friendship_system:
                # Traiter la demande d'amitié
                result = friendship_system.receive_friendship_request(message)
                print(f"[OK] Friendship request processed: {result}")
            else:
                print(f"[ERROR] Friendship system not initialized")
        else:
            print(f"🔍 Unknown message type: {message.get('type')}")
                
    except Exception as e:
        print(f"[ERROR] Error handling P2P message: {e}")
        import traceback
        traceback.print_exc()

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    global p2p_node, friendship_system, messaging_system, urn_sharing_system, image_urn_system, profile_manager, auth_manager
    
    print("[INIT] Starting OpenRed P2P Web Interface...")
    
    # Initialisation du gestionnaire de profil avec répertoire spécifique
    data_dir = os.getenv("OPENRED_DATA_DIR", "./user_data")
    
    # Initialisation du gestionnaire d'authentification
    auth_manager = OpenRedAuth(data_dir=data_dir)
    print(f"[AUTH] Auth system initialized - User configured: {auth_manager.has_user()}")
    
    profile_manager = UserProfileManager(data_dir=data_dir)
    user_profile = profile_manager.load_or_create_profile()
    profile_manager.load_or_create_groups()
    
    print(f"📁 Répertoire de données: {data_dir}")
    
    # Configuration nœud avec ID permanent
    node_id = os.getenv("OPENRED_NODE_ID", profile_manager.get_permanent_node_id())
    sector = user_profile.sector
    p2p_port = int(os.getenv("OPENRED_P2P_PORT", "8080"))
    
    # Création et démarrage nœud P2P avec gestionnaire de profil
    p2p_node = OpenRedP2PNode(
        node_id=node_id,
        sector=sector,
        p2p_port=p2p_port,
        profile_manager=profile_manager  # Passer le gestionnaire de profil
    )
    
    # Initialisation systèmes sociaux
    friendship_system = FriendshipProtocol(
        node_id=node_id,
        fingerprint=p2p_node.lighthouse.fingerprint,
        private_key=p2p_node.lighthouse.private_key,
        public_key=p2p_node.lighthouse.public_key
    )
    
    messaging_system = DistributedMessaging(
        node_id=node_id,
        fingerprint=p2p_node.lighthouse.fingerprint,
        private_key=p2p_node.lighthouse.private_key,
        public_key=p2p_node.lighthouse.public_key,
        friendship_protocol=friendship_system
    )
    
    urn_sharing_system = ConditionalURNSharing(
        node_id=node_id,
        fingerprint=p2p_node.lighthouse.fingerprint,
        friendship_protocol=friendship_system,
        phantom_urn_engine=p2p_node.phantom_urn_engine
    )
    
    # Initialiser le système Phantom URN authentique Enhanced
    global phantom_urn_system, projection_server
    from enhanced_phantom_urn_system import EnhancedPhantomUrnSystem
    phantom_urn_system = EnhancedPhantomUrnSystem(
        storage_dir=os.path.join(os.path.dirname(__file__), "..", "..", "phantom_urns"),
        projection_server_url="http://localhost:8002"
    )
    
    # Initialiser le serveur de projection ORP
    projection_server = PhantomProjectionServer(
        urn_system=phantom_urn_system,
        port=8002
    )
    
    # Démarrer le serveur de projection en arrière-plan
    projection_server.start_server_thread()
    
    print("👥 Social systems initialized!")
    print("� Phantom URN System initialized!")
    print("[PROJECTION] Projection Server started on port 8002!")
    
    # Initialisation du Spider Protocol pour découverte Internet
    global internet_spider, spider_handler
    if SPIDER_AVAILABLE:
        try:
            from spider_protocol import InternetSpiderProtocol
            from spider_handler import SpiderProtocolHandler
            
            internet_spider = InternetSpiderProtocol(p2p_node.lighthouse, p2p_node.security_protocol)
            spider_handler = SpiderProtocolHandler(p2p_node.lighthouse, internet_spider)
            
            # Démarrer le spider pour la découverte Internet !
            internet_spider.start_spider()
            
            print("🕷️ Internet Spider Protocol initialized and ACTIVE - Hunting across the internet!")
        except Exception as e:
            print(f"[WARNING] Failed to initialize Internet Spider: {e}")
    
    # Initialisation du protocole simple 3 phases
    simple_init_success = initialize_simple_protocol(p2p_node)
    if simple_init_success:
        print("[AUTH] Simple 3-Phase Protocol initialized!")
    else:
        print("[ERROR] Failed to initialize Simple 3-Phase Protocol")
    
    # Démarrage en arrière-plan
    asyncio.create_task(start_p2p_node())
    
    # Démarrage monitoring temps réel
    asyncio.create_task(real_time_monitoring())
    
    # Démarrage traitement demandes d'amitié en attente
    asyncio.create_task(process_pending_requests_monitor())
    
    print("[OK] OpenRed P2P Web Interface ready!")

async def start_p2p_node():
    """Démarre le nœud P2P en arrière-plan"""
    try:
        await p2p_node.start_node()
        
        # Enregistrer handler pour messages P2P sociaux
        p2p_node.set_social_message_handler(handle_p2p_message)
        print("[STREAM] P2P social message handler registered")
        
    except Exception as e:
        print(f"[ERROR] Error starting P2P node: {e}")

async def real_time_monitoring():
    """Monitoring temps réel avec diffusion WebSocket"""
    while True:
        try:
            if p2p_node and p2p_node.running:
                # Collecte des données de status
                status = p2p_node.get_node_status()
                discovered = p2p_node.lighthouse.get_discovered_nodes()
                
                # Message de mise à jour
                update_message = {
                    "type": "status_update",
                    "timestamp": time.time(),
                    "data": {
                        "node_status": status,
                        "discovered_nodes": len(discovered),
                        "active_connections": len(p2p_node.p2p_connection.active_connections),
                        "constellation_map": [
                            {
                                "fingerprint": fp,
                                "node_id": info["beacon"].node_id,
                                "sector": info["beacon"].sector,
                                "ip": info["ip"],
                                "last_seen": time.time() - info["last_seen"],
                                "phantom_urn_support": info["beacon"].urn_phantom_support
                            }
                            for fp, info in discovered.items()
                        ],
                        "social_stats": {
                            "friends": friendship_system.get_friendship_stats() if friendship_system else {},
                            "messages": messaging_system.get_messaging_stats() if messaging_system else {},
                            "urn_sharing": urn_sharing_system.get_sharing_stats() if urn_sharing_system else {},
                            "distributed_messaging": {
                                "sent_messages": len(messaging_system.sent_messages) if messaging_system else 0,
                                "conversations": len(messaging_system.conversations) if messaging_system else 0,
                                "cache_size": len(messaging_system.cache_manager.priority_cache) + len(messaging_system.cache_manager.standard_cache) if messaging_system and hasattr(messaging_system, 'cache_manager') else 0
                            }
                        }
                    }
                }
                
                # Diffusion WebSocket
                await ws_manager.broadcast(update_message)
                
        except Exception as e:
            print(f"[WARNING] Monitoring error: {e}")
            
        await asyncio.sleep(5)  # Mise à jour toutes les 5 secondes

async def process_pending_requests_monitor():
    """Traite périodiquement les demandes d'amitié en attente du protocole simple"""
    await asyncio.sleep(5)  # Attendre l'initialisation
    
    while True:
        try:
            if friendship_system:
                processed_count = process_pending_friendship_requests(friendship_system)
                if processed_count > 0:
                    print(f"[RESPONSE] Processed {processed_count} pending friendship requests")
                    
                    # Notifier les clients WebSocket des nouvelles demandes
                    if websocket_connections:
                        notification = {
                            "type": "new_friendship_requests",
                            "count": processed_count,
                            "timestamp": time.time()
                        }
                        await ws_manager.broadcast(notification)
                        
        except Exception as e:
            print(f"[ERROR] Error processing pending friendship requests: {e}")
            
        await asyncio.sleep(5)  # Vérifier toutes les 5 secondes

# === ROUTES API ===

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Page d'accueil démo - avec authentification"""
    global auth_manager
    
    # Vérifier si le système d'auth est configuré
    if not auth_manager or not auth_manager.has_user():
        return RedirectResponse(url="/login", status_code=302)
    
    # Vérifier l'authentification
    username = verify_auth_optional(request)
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        with open("../frontend/demo.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>[SERVER] OpenRed P2P Platform</title>
            <style>
                body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
                .header { background: #2196F3; color: white; padding: 20px; margin: -20px -20px 20px; border-radius: 8px; }
                .nav a { color: white; text-decoration: none; margin-right: 20px; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 4px; }
                .nav a:hover { background: rgba(255,255,255,0.3); }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>[SERVER] OpenRed P2P Platform</h1>
                <nav class="nav">
                    <a href="/dashboard">[TARGET] Dashboard</a>
                    <a href="/friends">👥 Amis</a>
                    <a href="/messages">💬 Messages</a>
                    <a href="/images">🖼️ Images URN</a>
                    <a href="/profile">👤 Profil</a>
                    <a href="/constellation">🌟 Constellation</a>
                    <a href="/urn">🔱 URN</a>
                </nav>
            </div>
            <h2>[INIT] Bienvenue sur OpenRed !</h2>
            <p>Plateforme P2P décentralisée avec protocole Internet Spider</p>
            <p>Naviguez vers les différentes sections via le menu ci-dessus.</p>
        </body>
        </html>
        """)

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Page de login"""
    try:
        login_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "login.html")
        with open(login_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <h1>[AUTH] Login Required</h1>
        <p>Login page not found. Please check installation.</p>
        """, status_code=404)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Page du tableau de bord"""
    if not verify_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>[TARGET] Dashboard - OpenRed</title>
        <style>
            body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #2196F3; color: white; padding: 20px; margin: -20px -20px 20px; }
            .nav a { color: white; text-decoration: none; margin-right: 20px; }
            .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .stat { text-align: center; padding: 15px; background: #e3f2fd; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>[TARGET] OpenRed Dashboard</h1>
            <nav>
                <a href="/">🏠 Accueil</a>
                <a href="/friends">👥 Amis</a>
                <a href="/messages">💬 Messages</a>
                <a href="/profile">👤 Profil</a>
                <a href="/constellation">🌟 Constellation</a>
                <a href="/urn">🔱 URN</a>
            </nav>
        </div>
        <div class="stats">
            <div class="stat">
                <h3>👥 Amis</h3>
                <div id="friends-count">-</div>
            </div>
            <div class="stat">
                <h3>💬 Messages</h3>
                <div id="messages-count">-</div>
            </div>
            <div class="stat">
                <h3>🔱 URNs</h3>
                <div id="urns-count">-</div>
            </div>
            <div class="stat">
                <h3>🌟 Nœuds P2P</h3>
                <div id="nodes-count">-</div>
            </div>
        </div>
        <script>
            // Charger les statistiques
            Promise.all([
                fetch('/api/social/friends'),
                fetch('/api/social/my-messages'),
                fetch('/api/urn/stats'),
                fetch('/api/constellation')
            ]).then(responses => Promise.all(responses.map(r => r.json())))
              .then(([friends, messages, urns, constellation]) => {
                  document.getElementById('friends-count').textContent = friends.length || 0;
                  document.getElementById('messages-count').textContent = messages.length || 0;
                  document.getElementById('urns-count').textContent = urns.total_urns || 0;
                  document.getElementById('nodes-count').textContent = constellation.nodes?.length || 0;
              });
        </script>
    </body>
    </html>
    """)

@app.get("/friends", response_class=HTMLResponse)
async def friends_page(request: Request):
    """Page de gestion des amis"""
    if not verify_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>👥 Amis - OpenRed</title>
        <style>
            body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #4CAF50; color: white; padding: 20px; margin: -20px -20px 20px; }
            .nav a { color: white; text-decoration: none; margin-right: 20px; }
            .friend-card { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin-left: 5px; }
            .btn-accept { background: #4CAF50; color: white; }
            .btn-reject { background: #f44336; color: white; }
            .btn-add { background: #2196F3; color: white; }
            .tabs { display: flex; margin-bottom: 20px; }
            .tab { padding: 10px 20px; background: white; border: none; cursor: pointer; margin-right: 5px; border-radius: 4px; }
            .tab.active { background: #4CAF50; color: white; }
            .content { display: none; }
            .content.active { display: block; }
            .loading { text-align: center; padding: 20px; color: #666; }
            .friend-info { flex-grow: 1; }
            .friend-name { font-weight: bold; color: #333; }
            .friend-details { font-size: 0.9em; color: #666; margin-top: 5px; }
            .status-badge { padding: 3px 8px; border-radius: 12px; font-size: 0.8em; margin-left: 10px; }
            .status-accepted { background: #e8f5e8; color: #2e7d32; }
            .status-pending { background: #fff3e0; color: #f57c00; }
            .no-data { text-align: center; padding: 40px; color: #999; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>👥 Gestion des Amis</h1>
            <nav>
                <a href="/">🏠 Accueil</a>
                <a href="/dashboard">[TARGET] Dashboard</a>
                <a href="/messages">💬 Messages</a>
                <a href="/profile">👤 Profil</a>
                <a href="/constellation">🌟 Constellation</a>
            </nav>
        </div>
        <div class="tabs">
            <button class="tab active" onclick="showTab('friends', this)">👥 Mes Amis</button>
            <button class="tab" onclick="showTab('requests', this)">[RESPONSE] Demandes</button>
            <button class="tab" onclick="showTab('discover', this)">🔍 Découvrir</button>
        </div>
        
        <div id="friends" class="content active">
            <h2>Mes Amis</h2>
            <div class="loading" id="friends-loading">⏳ Chargement des amis...</div>
            <div id="friends-list" style="display: none;"></div>
        </div>
        
        <div id="requests" class="content">
            <h2>Demandes d'Amitié</h2>
            <div class="loading" id="requests-loading">⏳ Chargement des demandes...</div>
            <div id="requests-list" style="display: none;"></div>
        </div>
        
        <div id="discover" class="content">
            <h2>Nœuds Disponibles</h2>
            <div class="loading" id="nodes-loading">⏳ Recherche de nœuds...</div>
            <div id="nodes-list" style="display: none;"></div>
        </div>
        
        <script>
            function showTab(tabName, element) {
                // Gérer les onglets
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
                element.classList.add('active');
                document.getElementById(tabName).classList.add('active');
                
                // Charger les données si nécessaire
                if (tabName === 'friends' && !document.getElementById('friends-list').innerHTML) {
                    loadFriends();
                } else if (tabName === 'requests' && !document.getElementById('requests-list').innerHTML) {
                    loadRequests();
                } else if (tabName === 'discover' && !document.getElementById('nodes-list').innerHTML) {
                    loadNodes();
                }
            }
            
            function loadFriends() {
                fetch('/api/social/friends')
                    .then(r => r.json())
                    .then(data => {
                        const loading = document.getElementById('friends-loading');
                        const list = document.getElementById('friends-list');
                        
                        loading.style.display = 'none';
                        list.style.display = 'block';
                        
                        console.log('Friends data:', data);
                        
                        if (data.friends && data.friends.length > 0) {
                            list.innerHTML = data.friends.map(f => `
                                <div class="friend-card">
                                    <div class="friend-info">
                                        <div class="friend-name">👤 ${f.name || f.node_id || f.fingerprint.slice(0,8)}...</div>
                                        <div class="friend-details">
                                            ID: ${f.fingerprint.slice(0,16)}...<br>
                                            Ajouté: ${new Date(f.created_at * 1000).toLocaleDateString()}<br>
                                            Dernière interaction: ${f.last_interaction ? new Date(f.last_interaction * 1000).toLocaleDateString() : 'Jamais'}
                                        </div>
                                    </div>
                                    <div>
                                        <span class="status-badge status-${f.status}">${f.status}</span>
                                        <span style="margin-left: 10px; color: #666;">Score: ${f.trust_score}</span>
                                    </div>
                                </div>
                            `).join('');
                        } else {
                            list.innerHTML = '<div class="no-data">👥 Aucun ami pour le moment<br><small>Utilisez l\\'onglet "Découvrir" pour trouver des nœuds à ajouter</small></div>';
                        }
                    })
                    .catch(error => {
                        console.error('Erreur:', error);
                        document.getElementById('friends-loading').innerHTML = '[ERROR] Erreur de chargement';
                    });
            }
            
            function loadRequests() {
                fetch('/api/social/friend-requests')
                    .then(r => r.json())
                    .then(data => {
                        const loading = document.getElementById('requests-loading');
                        const list = document.getElementById('requests-list');
                        
                        loading.style.display = 'none';
                        list.style.display = 'block';
                        
                        console.log('Requests data:', data);
                        
                        if (data.pending && data.pending.length > 0) {
                            list.innerHTML = data.pending.map(r => `
                                <div class="friend-card">
                                    <div class="friend-info">
                                        <div class="friend-name">👤 ${r.sender_name || r.sender_fingerprint.slice(0,8)}...</div>
                                        <div class="friend-details">
                                            De: ${r.sender_fingerprint.slice(0,16)}...<br>
                                            Reçue: ${new Date(r.timestamp * 1000).toLocaleDateString()}
                                        </div>
                                    </div>
                                    <div>
                                        <button class="btn btn-accept" onclick="acceptRequest('${r.request_id}')">[OK] Accepter</button>
                                        <button class="btn btn-reject" onclick="rejectRequest('${r.request_id}')">[ERROR] Refuser</button>
                                    </div>
                                </div>
                            `).join('');
                        } else {
                            list.innerHTML = '<div class="no-data">[RESPONSE] Aucune demande en attente</div>';
                        }
                    })
                    .catch(error => {
                        console.error('Erreur:', error);
                        document.getElementById('requests-loading').innerHTML = '[ERROR] Erreur de chargement';
                    });
            }
            
            function loadNodes() {
                fetch('/api/social/available-nodes')
                    .then(r => r.json())
                    .then(data => {
                        const loading = document.getElementById('nodes-loading');
                        const list = document.getElementById('nodes-list');
                        
                        loading.style.display = 'none';
                        list.style.display = 'block';
                        
                        console.log('Nodes data:', data);
                        
                        if (data.nodes && data.nodes.length > 0) {
                            list.innerHTML = data.nodes.map(n => `
                                <div class="friend-card">
                                    <div class="friend-info">
                                        <div class="friend-name">🌟 ${n.name || n.fingerprint.slice(0,8)}...</div>
                                        <div class="friend-details">
                                            Secteur: ${n.sector || 'N/A'}<br>
                                            ID: ${n.fingerprint.slice(0,16)}...<br>
                                            Distance: ${n.distance || 'N/A'}
                                        </div>
                                    </div>
                                    <div>
                                        <button class="btn btn-add" onclick="sendRequest('${n.fingerprint}')">➕ Ajouter</button>
                                    </div>
                                </div>
                            `).join('');
                        } else {
                            list.innerHTML = '<div class="no-data">🔍 Aucun nœud découvert<br><small>Assurez-vous que l\\'Internet Spider Protocol est actif</small></div>';
                        }
                    })
                    .catch(error => {
                        console.error('Erreur:', error);
                        document.getElementById('nodes-loading').innerHTML = '[ERROR] Erreur de chargement';
                    });
            }
            
            function acceptRequest(id) {
                fetch(`/api/social/accept-friend-request/${id}`, {method: 'POST'})
                    .then(r => r.json())
                    .then(result => {
                        if (result.success) {
                            alert('[OK] Demande acceptée !');
                            loadRequests(); // Recharger
                        } else {
                            alert('[ERROR] Erreur: ' + (result.error || 'Inconnue'));
                        }
                    })
                    .catch(error => {
                        alert('[ERROR] Erreur réseau');
                        console.error(error);
                    });
            }
            
            function rejectRequest(id) {
                fetch(`/api/social/reject-friend-request/${id}`, {method: 'POST'})
                    .then(r => r.json())
                    .then(result => {
                        if (result.success) {
                            alert('[ERROR] Demande refusée');
                            loadRequests(); // Recharger
                        } else {
                            alert('[ERROR] Erreur: ' + (result.error || 'Inconnue'));
                        }
                    });
            }
            
            function sendRequest(fingerprint) {
                fetch('/api/social/send-friend-request', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target_fingerprint: fingerprint})
                })
                .then(r => r.json())
                .then(result => {
                    if (result.success) {
                        alert('[UPLOAD] Demande envoyée !');
                    } else {
                        alert('[ERROR] Erreur: ' + (result.error || 'Inconnue'));
                    }
                });
            }
            
            // Charger les amis par défaut
            loadFriends();
        </script>
    </body>
    </html>
    """)

@app.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request):
    """Page de messagerie"""
    if not verify_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>💬 Messages - OpenRed</title>
        <style>
            body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #FF9800; color: white; padding: 20px; margin: -20px -20px 20px; }
            .nav a { color: white; text-decoration: none; margin-right: 20px; }
            .message { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; }
            .message-sent { background: #e3f2fd; }
            .message-received { background: #f3e5f5; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>💬 Messages</h1>
            <nav>
                <a href="/">🏠 Accueil</a>
                <a href="/dashboard">[TARGET] Dashboard</a>
                <a href="/friends">👥 Amis</a>
                <a href="/profile">👤 Profil</a>
            </nav>
        </div>
        <div id="messages-list"></div>
        <script>
            fetch('/api/social/my-messages').then(r => r.json()).then(messages => {
                const html = messages.map(m => `
                    <div class="message ${m.sender_id === 'me' ? 'message-sent' : 'message-received'}">
                        <strong>${m.sender_name || m.sender_id.slice(0,8)}...</strong>
                        <p>${m.content}</p>
                        <small>${new Date(m.timestamp * 1000).toLocaleString()}</small>
                    </div>
                `).join('');
                document.getElementById('messages-list').innerHTML = html || '<p>Aucun message</p>';
            });
        </script>
    </body>
    </html>
    """)

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Page de profil utilisateur"""
    if not verify_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>👤 Profil - OpenRed</title>
        <style>
            body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #9C27B0; color: white; padding: 20px; margin: -20px -20px 20px; }
            .nav a { color: white; text-decoration: none; margin-right: 20px; }
            .profile-card { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .profile-pic { width: 100px; height: 100px; border-radius: 50%; background: #ddd; margin: 0 auto 20px; display: block; }
            .profile-info { text-align: center; }
            .info-row { display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 4px; }
            .groups { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
            .group { padding: 15px; border-radius: 8px; color: white; text-align: center; }
            .loading { text-align: center; color: #666; padding: 20px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>👤 Mon Profil</h1>
            <nav>
                <a href="/">🏠 Accueil</a>
                <a href="/dashboard">[TARGET] Dashboard</a>
                <a href="/friends">👥 Amis</a>
                <a href="/messages">💬 Messages</a>
                <a href="/constellation">🌟 Constellation</a>
            </nav>
        </div>
        
        <div class="profile-card">
            <div class="loading" id="loading">⏳ Chargement du profil...</div>
            <div id="profile-content" style="display: none;">
                <img id="profile-pic" class="profile-pic" src="" alt="Photo de profil">
                <div class="profile-info">
                    <h2 id="profile-name">-</h2>
                    <div class="info-row">
                        <strong>ID Utilisateur:</strong>
                        <span id="user-id">-</span>
                    </div>
                    <div class="info-row">
                        <strong>Localisation:</strong>
                        <span id="location">-</span>
                    </div>
                    <div class="info-row">
                        <strong>Profession:</strong>
                        <span id="profession">-</span>
                    </div>
                    <div class="info-row">
                        <strong>Secteur:</strong>
                        <span id="sector">-</span>
                    </div>
                    <div class="info-row">
                        <strong>Créé le:</strong>
                        <span id="created-at">-</span>
                    </div>
                    <div class="info-row">
                        <strong>Dernière MAJ:</strong>
                        <span id="last-updated">-</span>
                    </div>
                    
                    <h3>[TARGET] Centres d'intérêt</h3>
                    <div id="interests" style="text-align: center; margin: 15px 0;">-</div>
                    
                    <h3>👥 Groupes d'amis</h3>
                    <div id="groups" class="groups"></div>
                </div>
            </div>
        </div>
        
        <script>
            function loadProfile() {
                fetch('/api/profile')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Profile data:', data);
                        
                        // Masquer le loading
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('profile-content').style.display = 'block';
                        
                        // Remplir les informations
                        document.getElementById('profile-name').textContent = data.profile?.name || 'Utilisateur';
                        document.getElementById('user-id').textContent = (data.profile?.user_id || 'N/A').slice(0, 16) + '...';
                        document.getElementById('location').textContent = data.profile?.location || 'Non spécifiée';
                        document.getElementById('profession').textContent = data.profile?.profession || 'Non spécifiée';
                        document.getElementById('sector').textContent = data.profile?.sector || 'Non défini';
                        
                        // Dates
                        if (data.profile?.created_at) {
                            document.getElementById('created-at').textContent = new Date(data.profile.created_at * 1000).toLocaleDateString();
                        }
                        if (data.profile?.last_updated) {
                            document.getElementById('last-updated').textContent = new Date(data.profile.last_updated * 1000).toLocaleDateString();
                        }
                        
                        // Photo de profil
                        if (data.profile?.profile_thumbnail) {
                            document.getElementById('profile-pic').src = data.profile.profile_thumbnail;
                        }
                        
                        // Centres d'intérêt
                        if (data.profile?.interests && data.profile.interests.length > 0) {
                            document.getElementById('interests').innerHTML = data.profile.interests.map(i => 
                                `<span style="background: #e3f2fd; padding: 5px 10px; margin: 3px; border-radius: 15px; display: inline-block;">${i}</span>`
                            ).join(' ');
                        } else {
                            document.getElementById('interests').textContent = 'Aucun centre d\\'intérêt défini';
                        }
                        
                        // Groupes
                        if (data.groups && data.groups.length > 0) {
                            document.getElementById('groups').innerHTML = data.groups.map(group => 
                                `<div class="group" style="background: ${group.color};">
                                    <h4>${group.name}</h4>
                                    <p style="font-size: 0.9em; opacity: 0.9;">${group.description}</p>
                                    <small>${group.members?.length || 0} membres</small>
                                </div>`
                            ).join('');
                        } else {
                            document.getElementById('groups').innerHTML = '<p>Aucun groupe créé</p>';
                        }
                    })
                    .catch(error => {
                        console.error('Erreur de chargement du profil:', error);
                        document.getElementById('loading').innerHTML = '[ERROR] Erreur de chargement du profil';
                    });
            }
            
            // Charger le profil au chargement de la page
            loadProfile();
        </script>
    </body>
    </html>
    """)

@app.get("/constellation", response_class=HTMLResponse)
async def constellation_page(request: Request):
    """Page de la constellation P2P"""
    if not verify_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌟 Constellation - OpenRed</title>
        <style>
            body { font-family: Arial; margin: 0; padding: 20px; background: #0a0a0a; color: white; }
            .header { background: #1a1a1a; color: white; padding: 20px; margin: -20px -20px 20px; }
            .nav a { color: white; text-decoration: none; margin-right: 20px; }
            .node { background: #333; padding: 15px; margin: 10px; border-radius: 8px; display: inline-block; }
            .node.online { border-left: 4px solid #4CAF50; }
            .node.offline { border-left: 4px solid #f44336; }
            #constellation { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌟 Constellation P2P</h1>
            <nav>
                <a href="/">🏠 Accueil</a>
                <a href="/dashboard">[TARGET] Dashboard</a>
                <a href="/friends">👥 Amis</a>
                <a href="/messages">💬 Messages</a>
            </nav>
        </div>
        <div id="constellation"></div>
        <script>
            fetch('/api/constellation').then(r => r.json()).then(data => {
                const html = data.nodes.map(node => `
                    <div class="node ${node.status || 'offline'}">
                        <h3>🌟 ${node.name || node.fingerprint.slice(0,8)}...</h3>
                        <p><strong>Secteur:</strong> ${node.sector}</p>
                        <p><strong>Distance:</strong> ${node.distance || 'N/A'}</p>
                        <p><strong>Dernier contact:</strong> ${node.last_seen ? new Date(node.last_seen * 1000).toLocaleString() : 'Jamais'}</p>
                    </div>
                `).join('');
                document.getElementById('constellation').innerHTML = html || '<p>Aucun nœud découvert</p>';
            });
        </script>
    </body>
    </html>
    """)

@app.get("/urn", response_class=HTMLResponse)
async def urn_page(request: Request):
    """Page des URNs (Phantom URN System)"""
    if not verify_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🔱 URNs - OpenRed</title>
        <style>
            body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #673AB7; color: white; padding: 20px; margin: -20px -20px 20px; }
            .nav a { color: white; text-decoration: none; margin-right: 20px; }
            .urn-card { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #673AB7; }
            .btn { padding: 8px 16px; background: #673AB7; color: white; border: none; border-radius: 4px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔱 Phantom URN System</h1>
            <nav>
                <a href="/">🏠 Accueil</a>
                <a href="/dashboard">[TARGET] Dashboard</a>
                <a href="/friends">👥 Amis</a>
                <a href="/messages">💬 Messages</a>
            </nav>
        </div>
        <div>
            <button class="btn" onclick="createTestUrn()">🔱 Créer URN Test</button>
        </div>
        <div id="urn-stats"></div>
        <div id="shared-urns"></div>
        <script>
            function loadData() {
                fetch('/api/urn/stats').then(r => r.json()).then(stats => {
                    document.getElementById('urn-stats').innerHTML = `
                        <div class="urn-card">
                            <h3>📊 Statistiques URN</h3>
                            <p><strong>Total URNs:</strong> ${stats.total_urns || 0}</p>
                            <p><strong>URNs actifs:</strong> ${stats.active_urns || 0}</p>
                            <p><strong>URNs partagés:</strong> ${stats.shared_urns || 0}</p>
                        </div>
                    `;
                });
                
                fetch('/api/social/shared-urns').then(r => r.json()).then(urns => {
                    const html = urns.map(urn => `
                        <div class="urn-card">
                            <h4>🔱 ${urn.urn_id.slice(0,16)}...</h4>
                            <p><strong>De:</strong> ${urn.owner_name || urn.owner_id.slice(0,8)}...</p>
                            <p><strong>Accès:</strong> ${urn.access_level}</p>
                            <p><strong>Partagé:</strong> ${new Date(urn.shared_at * 1000).toLocaleString()}</p>
                        </div>
                    `).join('');
                    document.getElementById('shared-urns').innerHTML = html || '<p>Aucun URN partagé</p>';
                });
            }
            
            function createTestUrn() {
                const btn = event.target;
                btn.disabled = true;
                btn.textContent = '🔄 Test en cours...';
                
                fetch('/api/urn/test', {
                    method: 'POST',
                    credentials: 'include'
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Erreur ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(result => {
                    if (result.phantom_urn_engine === "operational") {
                        alert(`[OK] Test URN réussi!\n🔱 Moteur Phantom: ${result.phantom_urn_engine}\n📊 Cache local: ${result.local_cache} URNs\n[SERVER] Index réseau: ${result.network_index} URNs`);
                    } else {
                        alert(`[WARNING] Test URN échoué!\nStatut moteur: ${result.phantom_urn_engine}`);
                    }
                    loadData();
                })
                .catch(error => {
                    console.error('Erreur test URN:', error);
                    alert(`[ERROR] Erreur lors du test URN: ${error.message}`);
                })
                .finally(() => {
                    btn.disabled = false;
                    btn.textContent = '🔱 Créer URN Test';
                });
            }
            
            loadData();
        </script>
    </body>
    </html>
    """)

@app.get("/images", response_class=HTMLResponse)
async def images_page(request: Request):
    """Page de gestion des images URN"""
    if not verify_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🖼️ Images URN - OpenRed</title>
        <style>
            body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #FF5722; color: white; padding: 20px; margin: -20px -20px 20px; }
            .nav a { color: white; text-decoration: none; margin-right: 20px; }
            .nav a:hover { text-decoration: underline; }
            .card { background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .btn { padding: 10px 20px; background: #FF5722; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #E64A19; }
            .btn-secondary { background: #9E9E9E; }
            .btn-secondary:hover { background: #757575; }
            .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; border-radius: 8px; margin: 20px 0; }
            .upload-area.dragover { border-color: #FF5722; background: #fff3f0; }
            .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }
            .image-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .image-preview { width: 100%; height: 200px; object-fit: cover; }
            .image-info { padding: 15px; }
            .stream-indicator { background: #4CAF50; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
            .download-indicator { background: #2196F3; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-number { font-size: 2em; font-weight: bold; color: #FF5722; }
            .loading { text-align: center; padding: 20px; color: #666; }
            .progress-container { background: #f0f0f0; border-radius: 10px; padding: 3px; margin: 10px 0; }
            .progress-bar { background: #FF5722; height: 20px; border-radius: 8px; transition: width 0.3s ease; position: relative; }
            .progress-text { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-size: 12px; font-weight: bold; }
            .job-card { background: #f8f9fa; border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; }
            .job-status { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .status-processing { background: #fff3cd; color: #856404; }
            .status-completed { background: #d4edda; color: #155724; }
            .status-failed { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>� Phantom URN System</h1>
            <nav class="nav">
                <a href="/">🏠 Accueil</a>
                <a href="/dashboard">[TARGET] Dashboard</a>
                <a href="/friends">👥 Amis</a>
                <a href="/urn">🔱 URNs</a>
                <a href="/messages">💬 Messages</a>
            </nav>
        </div>

        <!-- Section Upload -->
        <div class="card">
            <h2>� Burn Images to Phantom URN</h2>
            <div class="upload-area" id="uploadArea">
                <p>[TARGET] Uploadez vos images pour fragmentation atomique</p>
                <p style="font-size: 0.9em; color: #666;">Système dual : Projection ORP publique + URN fragmentée</p>
                <input type="file" id="fileInput" accept="image/*" multiple style="display: none;">
            </div>
            <button class="btn" onclick="document.getElementById('fileInput').click()">[BURN] Burn Images</button>
        </div>

        <!-- Jobs en cours -->
        <div class="card" id="jobsSection" style="display: none;">
            <h2>[INIT] Traitement en cours</h2>
            <div id="activeJobs">
                <!-- Les jobs actifs apparaîtront ici -->
            </div>
        </div>

        <!-- Statistiques -->
        <div class="card">
            <h2>📊 Statistiques Phantom URN</h2>
            <div id="stats" class="stats-grid">
                <div class="loading">Chargement des statistiques...</div>
            </div>
        </div>

        <!-- Système Dual ORP + URN -->
        <div class="card">
            <h2>[PROJECTION] Système Dual ORP + URN</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                <div style="background: #f0f8ff; padding: 15px; border-radius: 8px;">
                    <h3>[STREAM] Système ORP (Public)</h3>
                    <p>• Projection streaming temps réel</p>
                    <p>• WebSocket sur port 8002</p>
                    <p>• Diffusion publique sans stockage</p>
                    <p>• Protection anti-capture active</p>
                </div>
                <div style="background: #fff0f5; padding: 15px; border-radius: 8px;">
                    <h3>[URN] Système URN (Privé)</h3>
                    <p>• Fragmentation atomique cryptée</p>
                    <p>• Chaînage cryptographique</p>
                    <p>• Téléchargement conditionnel</p>
                    <p>• Reconstruction Phoenix</p>
                </div>
            </div>
        </div>

        <!-- Mes Phantom URNs -->
        <div class="card">
            <h2>� Mes Phantom URNs</h2>
            <div class="btn-group">
                <button class="btn" onclick="loadMyPhantoms()">🔄 Actualiser</button>
                <button class="btn btn-secondary" onclick="showActiveStreams()">[PROJECTION] Projections Actives</button>
                <button class="btn btn-secondary" onclick="connectProjectionServer()">[SERVER] Serveur Projection</button>
            </div>
            <div id="myPhantoms" class="image-grid">
                <div class="loading">Chargement de vos phantoms...</div>
            </div>
        </div>

        <!-- Projections Actives -->
        <div class="card" id="projectionsSection" style="display: none;">
            <h2>[PROJECTION] Projections ORP Actives</h2>
            <div id="activeProjections">
                <div class="loading">Chargement des projections...</div>
            </div>
        </div>

        <script>
            // Variables globales
            let myPhantoms = [];
            let systemStats = {};
            let projectionWebSocket = null;

            // FONCTIONS PRINCIPALES (définies avant DOM)
            
            // Charger mes phantoms Enhanced
            async function loadMyPhantoms() {
                console.log('Chargement Phantoms Enhanced...');
                try {
                    const response = await fetch('/api/images/my-urns', {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const data = await response.json();
                        myPhantoms = data.phantoms || [];
                        displayMyPhantoms();
                        console.log('Phantoms charges:', myPhantoms.length);
                    } else {
                        console.warn('Erreur chargement phantoms:', response.status);
                        const container = document.getElementById('myPhantomsList');
                        if (container) {
                            container.innerHTML = '<p>Erreur chargement phantoms Enhanced</p>';
                        }
                    }
                } catch (error) {
                    console.error('Erreur chargement phantoms:', error);
                    const container = document.getElementById('myPhantomsList');
                    if (container) {
                        container.innerHTML = '<p>Erreur connexion Enhanced</p>';
                    }
                }
            }

            // Afficher projections actives Enhanced
            function showActiveStreams() {
                console.log('Affichage projections actives Enhanced...');
                const projectionsSection = document.getElementById('projectionsSection');
                if (projectionsSection) {
                    if (projectionsSection.style.display === 'none' || !projectionsSection.style.display) {
                        projectionsSection.style.display = 'block';
                        loadActiveProjections();
                    } else {
                        projectionsSection.style.display = 'none';
                    }
                } else {
                    console.warn('Section projections non trouvee');
                    alert('Projections Enhanced - La section projections sera bientot disponible!');
                }
            }

            // Connecter serveur de projection Enhanced
            function connectProjectionServer() {
                console.log('Connexion serveur projection Enhanced...');
                alert('Serveur de Projection Enhanced\\n\\nStatus: Actif sur port 8002\\nType: Phoenix de Schrodinger WebSocket\\nSecurite: NCK + Verification continue\\nEnhanced: Projection ORP temporaire uniquement\\n\\nURL: http://localhost:8002\\n\\nAucune image complete n est jamais reconstituee!');
            }

            // Charger projections actives Enhanced
            async function loadActiveProjections() {
                try {
                    console.log('Chargement projections actives...');
                    const response = await fetch('/api/images/active-projections', {
                        credentials: 'include'
                    });

                    const container = document.getElementById('activeProjections');
                    if (response.ok) {
                        const data = await response.json();
                        const projections = data.projections || [];
                        
                        if (container) {
                            if (projections.length === 0) {
                                container.innerHTML = '<p>Aucune projection Enhanced active</p>';
                            } else {
                                container.innerHTML = projections.map(proj => `
                                    <div class="phantom-card">
                                        <h4>Phoenix ${proj.phantom_id}</h4>
                                        <p>Viewers: ${proj.viewers}</p>
                                        <p>Demarre: ${new Date(proj.started_at).toLocaleString()}</p>
                                        <button onclick="stopProjection('${proj.phantom_id}')">Arreter</button>
                                    </div>
                                `).join('');
                            }
                        }
                    } else {
                        if (container) {
                            container.innerHTML = '<p>Erreur chargement projections Enhanced</p>';
                        }
                    }
                } catch (error) {
                    console.error('Erreur projections Enhanced:', error);
                    const container = document.getElementById('activeProjections');
                    if (container) {
                        container.innerHTML = '<p>Erreur connexion projections Enhanced</p>';
                    }
                }
            }

            // Initialisation Enhanced
            document.addEventListener('DOMContentLoaded', function() {
                console.log('[INIT] Initialisation Enhanced Phantom URN Interface');
                
                // Vérifier authentification
                checkAuthStatus();
                
                setupUpload();
                loadStats();
                loadMyPhantoms();  // Changé de loadMyImages() à loadMyPhantoms()
                
                // Actualiser toutes les 30 secondes
                setInterval(() => {
                    loadStats();
                    if (document.getElementById('projectionsSection').style.display !== 'none') {
                        showActiveStreams();
                    }
                }, 30000);
                
                console.log('[OK] Interface Enhanced initialisée');
            });

            // Vérification statut authentification
            async function checkAuthStatus() {
                try {
                    console.log('[AUTH] Vérification authentification...');
                    const response = await fetch('/api/phantom/status', {
                        credentials: 'include'
                    });
                    console.log('[AUTH] Statut auth:', response.status);
                    if (!response.ok && response.status === 401) {
                        console.warn('[ERROR] Non authentifié');
                        alert('[WARNING] Veuillez vous connecter pour utiliser l interface Enhanced');
                    } else {
                        console.log('[OK] Authentifié');
                    }
                } catch (error) {
                    console.error('[ERROR] Erreur vérification auth:', error);
                }
            }

            // Configuration upload
            function setupUpload() {
                const uploadArea = document.getElementById('uploadArea');
                const fileInput = document.getElementById('fileInput');

                // Drag & Drop
                uploadArea.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    uploadArea.classList.add('dragover');
                });

                uploadArea.addEventListener('dragleave', () => {
                    uploadArea.classList.remove('dragover');
                });

                uploadArea.addEventListener('drop', (e) => {
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');
                    handleFiles(e.dataTransfer.files);
                });

                // File input Enhanced
                fileInput.addEventListener('change', (e) => {
                    console.log('📁 Fichier sélectionné:', e.target.files);
                    handleFiles(e.target.files);
                });

                // Click upload area Enhanced
                uploadArea.addEventListener('click', () => {
                    console.log('[CLICK] Click zone upload');
                    fileInput.click();
                });
            }

            // Gestion fichiers Enhanced
            function handleFiles(files) {
                console.log('[FILES] Traitement fichiers:', files.length);
                Array.from(files).forEach(file => {
                    console.log('[FILE] Fichier:', file.name, file.type, file.size);
                    if (file.type.startsWith('image/')) {
                        console.log('[OK] Image valide, début upload Enhanced...');
                        uploadImage(file);
                    } else {
                        console.warn('[ERROR] Type fichier non supporté:', file.type);
                        alert('[WARNING] Seules les images sont supportées: ' + file.name);
                    }
                });
            }

            // Upload image et burn en Phantom URN Enhanced
            async function uploadImage(file) {
                console.log('[BURN] Début upload Enhanced:', file.name);
                
                const formData = new FormData();
                formData.append('file', file);

                try {
                    console.log('[UPLOAD] Envoi vers /api/images/upload...');
                    const response = await fetch('/api/images/upload', {
                        method: 'POST',
                        credentials: 'include',
                        body: formData
                    });

                    console.log('[RESPONSE] Réponse serveur:', response.status);

                    if (response.ok) {
                        const result = await response.json();
                        console.log('[OK] Upload initié:', result);
                        
                        if (result.job_id) {
                            // Système asynchrone - afficher message de progression
                            alert(`[BURN] Upload réussi !

Fichier: ${result.filename}
Job ID: ${result.job_id}
Statut: ${result.status}
Temps estimé: ${result.estimated_time}

Le traitement URN Phantom est en cours en arrière-plan.
Vous pouvez vérifier le progrès dans la section "Mes Phantoms".`);
                            
                            // Démarrer le polling du statut
                            pollJobStatus(result.job_id);
                            
                        } else {
                            // Ancien système synchrone (fallback)
                            alert(`[PHOENIX] Phoenix de Schrödinger créé!
                        
[URN] Phantom ID: ${result.phantom_id}
[ATOMIC] Fragments atomiques: ${result.total_fragments}
[KEY] NCK System: Activé
[OK] Vérification continue: Active
[PHOENIX] État quantique: Crypté

Système dual Enhanced:
• [ORP] ORP: ${result.dual_system?.orp_streaming || 'Actif'}
• [URN] URN: ${result.dual_system?.urn_download || 'Fragments cryptés'}`);
                        }
                        
                        loadMyPhantoms();
                        loadStats();
                    } else {
                        console.error('[ERROR] Erreur réponse:', response.status);
                        const error = await response.json();
                        console.error('[ERROR] Détails erreur:', error);
                        alert('[ERROR] Erreur upload Enhanced: ' + (error.detail || 'Erreur inconnue'));
                    }
                } catch (error) {
                    console.error('[ERROR] Erreur upload Enhanced:', error);
                    alert('[ERROR] Erreur upload Enhanced: ' + error.message);
                }
            }

            // Polling du statut d'un job
            async function pollJobStatus(jobId) {
                console.log('[INIT] Démarrage polling job:', jobId);
                
                // Afficher la section jobs et créer la barre de progression
                showJobProgress(jobId);
                
                const poll = async () => {
                    try {
                        const response = await fetch(`/api/images/job-status/${jobId}`, {
                            credentials: 'include'
                        });
                        
                        if (response.ok) {
                            const job = await response.json();
                            console.log(`[${job.status.toUpperCase()}] Job ${jobId}: ${job.progress}%`);
                            
                            // Mettre à jour la barre de progression
                            updateJobProgress(jobId, job);
                            
                            if (job.status === 'completed') {
                                console.log('[OK] Job terminé:', job.result);
                                
                                // Marquer comme terminé
                                completeJobProgress(jobId, job);
                                
                                alert(`[OK] URN Phantom créé !

Phantom ID: ${job.result.phantom_id}
Fragments: ${job.result.total_fragments}
Temps total: ${Math.round((job.completed_at - job.created_at))} secondes

Le système Enhanced est maintenant actif !`);
                                
                                // Recharger la liste
                                loadMyPhantoms();
                                loadStats();
                                return; // Arrêter le polling
                                
                            } else if (job.status === 'failed') {
                                console.error('[ERROR] Job échoué:', job.error);
                                failJobProgress(jobId, job);
                                alert(`[ERROR] Échec création URN: ${job.error}`);
                                return; // Arrêter le polling
                                
                            } else {
                                // Continuer le polling
                                setTimeout(poll, 3000); // Vérifier toutes les 3 secondes
                            }
                        } else {
                            console.warn('[WARNING] Erreur vérification job:', response.status);
                            setTimeout(poll, 5000); // Réessayer dans 5 secondes
                        }
                        
                    } catch (error) {
                        console.error('[ERROR] Erreur polling:', error);
                        setTimeout(poll, 5000); // Réessayer dans 5 secondes
                    }
                };
                
                // Démarrer le premier poll dans 2 secondes
                setTimeout(poll, 2000);
            }

            // Afficher la section jobs et créer une barre de progression
            function showJobProgress(jobId) {
                const jobsSection = document.getElementById('jobsSection');
                const activeJobs = document.getElementById('activeJobs');
                
                // Afficher la section
                jobsSection.style.display = 'block';
                
                // Créer la carte de job
                const jobCard = document.createElement('div');
                jobCard.className = 'job-card';
                jobCard.id = `job-${jobId}`;
                
                jobCard.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span><strong>Job:</strong> ${jobId.substring(0, 8)}...</span>
                        <span class="job-status status-processing" id="status-${jobId}">PROCESSING</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar" id="progress-${jobId}" style="width: 0%;">
                            <span class="progress-text" id="progress-text-${jobId}">0%</span>
                        </div>
                    </div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">
                        <span id="filename-${jobId}">Initialisation...</span>
                    </div>
                `;
                
                activeJobs.appendChild(jobCard);
            }

            // Mettre à jour la progression d'un job
            function updateJobProgress(jobId, job) {
                const progressBar = document.getElementById(`progress-${jobId}`);
                const progressText = document.getElementById(`progress-text-${jobId}`);
                const filename = document.getElementById(`filename-${jobId}`);
                
                if (progressBar && progressText) {
                    progressBar.style.width = `${job.progress}%`;
                    progressText.textContent = `${job.progress}%`;
                }
                
                if (filename) {
                    filename.textContent = `Fichier: ${job.filename}`;
                }
            }

            // Marquer un job comme terminé
            function completeJobProgress(jobId, job) {
                const status = document.getElementById(`status-${jobId}`);
                const progressBar = document.getElementById(`progress-${jobId}`);
                const progressText = document.getElementById(`progress-text-${jobId}`);
                
                if (status) {
                    status.textContent = 'COMPLETED';
                    status.className = 'job-status status-completed';
                }
                
                if (progressBar && progressText) {
                    progressBar.style.width = '100%';
                    progressText.textContent = 'Terminé !';
                }
                
                // Masquer après 5 secondes
                setTimeout(() => {
                    const jobCard = document.getElementById(`job-${jobId}`);
                    if (jobCard) {
                        jobCard.remove();
                        
                        // Masquer la section si plus de jobs
                        const activeJobs = document.getElementById('activeJobs');
                        if (activeJobs.children.length === 0) {
                            document.getElementById('jobsSection').style.display = 'none';
                        }
                    }
                }, 5000);
            }

            // Marquer un job comme échoué
            function failJobProgress(jobId, job) {
                const status = document.getElementById(`status-${jobId}`);
                const progressText = document.getElementById(`progress-text-${jobId}`);
                
                if (status) {
                    status.textContent = 'FAILED';
                    status.className = 'job-status status-failed';
                }
                
                if (progressText) {
                    progressText.textContent = 'Erreur !';
                }
            }

            // Charger statistiques
            async function loadStats() {
                try {
                    const response = await fetch('/api/images/system-stats', {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const data = await response.json();
                        systemStats = data.stats;
                        displayStats();
                    }
                } catch (error) {
                    console.error('Erreur stats:', error);
                }
            }

            // Afficher statistiques Phantom URN
            function displayStats() {
                const statsContainer = document.getElementById('stats');
                
                const fragmentation = systemStats.fragmentation || {};
                const projectionServer = systemStats.projection_server || {};
                
                statsContainer.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${systemStats.active_phantoms || 0}</div>
                        <div>Phantoms Actifs</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${systemStats.total_fragments || 0}</div>
                        <div>Fragments Atomiques</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${projectionServer.active_connections || 0}</div>
                        <div>Connexions ORP</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${fragmentation.atomic_pixels ? '[OK]' : '[ERROR]'}</div>
                        <div>Fragmentation Atomique</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${fragmentation.cryptographic_chaining ? '[OK]' : '[ERROR]'}</div>
                        <div>Chaînage Cryptographique</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${fragmentation.physical_storage ? '[WARNING]' : '🔒'}</div>
                        <div>Stockage Physique</div>
                    </div>`;
            }

            // Charger mes phantoms
            async function loadMyPhantoms() {
                try {
                    const response = await fetch('/api/images/my-urns', {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const data = await response.json();
                        myPhantoms = data.phantoms;
                        displayMyPhantoms();
                    }
                } catch (error) {
                    console.error('Erreur phantoms:', error);
                }
            }

            // Afficher mes phantoms
            function displayMyPhantoms() {
                const container = document.getElementById('myPhantoms');
                
                if (myPhantoms.length === 0) {
                    container.innerHTML = '<p>Aucun Phantom URN. Uploadez votre première image pour la fragmentation atomique!</p>';
                    return;
                }

                container.innerHTML = myPhantoms.map(phantom => `
                    <div class="image-card">
                        <div class="image-info">
                            <h4>🔥 ${phantom.phantom_id}</h4>
                            <p><strong>Nom:</strong> ${phantom.phantom_name || 'Sans nom'}</p>
                            <p><strong>Dimensions:</strong> ${phantom.dimensions[0]}x${phantom.dimensions[1]}</p>
                            <p><strong>Fragments atomiques:</strong> ${phantom.total_fragments}</p>
                            <p><strong>Type:</strong> 
                                <span class="stream-indicator">[ENHANCED] Phoenix Schrödinger</span> 
                                <span class="download-indicator">🔱 URN Fragmentée</span>
                            </p>
                            <p><strong>Streaming:</strong> ${phantom.streaming_url}</p>
                            <p><strong>WebSocket:</strong> ${phantom.websocket_url}</p>
                            <div style="margin-top: 10px;">
                                <button class="btn" onclick="startPhantomProjection('${phantom.phantom_id}')">[PROJECTION] Projection ORP</button>
                                ${phantom.type !== 'stream' ? 
                                    `<button class="btn" onclick="generateDownloadToken('${phantom.phantom_id}')">💾 Token DL</button>` : ''
                                }
                                <button class="btn btn-secondary" onclick="showUrnInfo('${phantom.phantom_id}')">ℹ️ Info</button>
                                <button class="btn btn-secondary" onclick="enableURNDownload('${phantom.phantom_id}')">[URN] Activer URN</button>
                                <button class="btn btn-secondary" onclick="viewPhantomInfo('${phantom.phantom_id}')">[FILES] Info</button>
                            </div>
                        </div>
                    </div>
                `).join('');
            }

            // Démarrer projection phantom
            async function startPhantomProjection(phantomId) {
                try {
                    const response = await fetch(`/api/images/start-stream/${phantomId}`, {
                        method: 'POST',
                        credentials: 'include',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({mode: 'projection'})
                    });

                    if (response.ok) {
                        const result = await response.json();
                        alert(`[PROJECTION] Projection ORP configurée!
                        
Phantom ID: ${result.phantom_id}
WebSocket: ${result.streaming_info.websocket_url}
HTTP: ${result.streaming_info.http_endpoint}
Protocol: ${result.streaming_info.protocol}
Dimensions: ${result.streaming_info.dimensions.join('x')}
Fragments: ${result.streaming_info.total_fragments}`);
                        loadStats();
                    } else {
                        const error = await response.json();
                        alert('[ERROR] Erreur projection: ' + error.detail);
                    }
                } catch (error) {
                    alert('[ERROR] Erreur projection: ' + error.message);
                }
            }

            // Activer téléchargement URN
            async function enableURNDownload(phantomId) {
                try {
                    const response = await fetch(`/api/phantom/${phantomId}/enable-urn-download`, {
                        method: 'POST',
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        alert(`[URN] URN téléchargeable activée!
                        
Phantom ID: ${result.phantom_id}
Token de téléchargement: ${result.download_token}
Message: ${result.message}

Fragments atomiques maintenant disponibles pour téléchargement.`);
                    } else {
                        const error = await response.json();
                        alert('[ERROR] Erreur activation URN: ' + error.detail);
                    }
                } catch (error) {
                    alert('[ERROR] Erreur activation URN: ' + error.message);
                }
            }

            // Voir informations phantom
            async function viewPhantomInfo(phantomId) {
                try {
                    const response = await fetch(`/api/phantom/${phantomId}/orp`, {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const result = await response.json();
                        const orp = result.orp_info;
                        alert(`[ORP] Informations Phantom URN
                        
Phantom ID: ${result.phantom_id}
Type: ${orp.type}
Description: ${orp.description}

Streaming URL: ${orp.streaming_url}
Projection: ${orp.projection_endpoint}

Système dual opérationnel!`);
                    } else {
                        const error = await response.json();
                        alert('[ERROR] Erreur info: ' + error.detail);
                    }
                } catch (error) {
                    alert('[ERROR] Erreur info: ' + error.message);
                }
            }

            // Connexion serveur projection
            function connectProjectionServer() {
                if (projectionWebSocket && projectionWebSocket.readyState === WebSocket.OPEN) {
                    alert('Déjà connecté au serveur de projection ORP!');
                    return;
                }

                try {
                    projectionWebSocket = new WebSocket('ws://localhost:8002/ws');
                    
                    projectionWebSocket.onopen = function() {
                        alert('[OK] Connecté au serveur de projection ORP!');
                    };
                    
                    projectionWebSocket.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        console.log('Message ORP:', data);
                        
                        if (data.type === 'phantom_list') {
                            console.log(`[STREAM] ${data.count} phantoms disponibles pour projection`);
                        } else if (data.type === 'phantom_projection') {
                            console.log(`[PROJECTION] Projection reçue: ${data.phantom_id}`);
                        }
                    };
                    
                    projectionWebSocket.onclose = function() {
                        console.log('Connexion ORP fermée');
                        projectionWebSocket = null;
                    };
                    
                } catch (error) {
                    alert('[ERROR] Erreur connexion ORP: ' + error.message);
                }
            }

            // Afficher info URN
            async function showUrnInfo(urnId) {
                try {
                    const response = await fetch(`/api/images/urn-info/${urnId}`, {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const data = await response.json();
                        const info = data.urn_info;
                        
                        alert(`[FILES] Informations URN\\n\\n` +
                              `🆔 ID: ${info.urn_id}\\n` +
                              `📁 Fichier: ${info.filename}\\n` +
                              `📊 Taille: ${(info.size / 1024).toFixed(1)} KB\\n` +
                              `📐 Dimensions: ${info.dimensions[0]}x${info.dimensions[1]}\\n` +
                              `📅 Upload: ${new Date(info.upload_time * 1000).toLocaleString()}\\n` +
                              `🔒 Accès: ${info.access_level}\\n` +
                              `[RESPONSE] Téléchargements: ${info.download_count}\\n` +
                              `📺 Streams: ${info.stream_count}`);
                    }
                } catch (error) {
                    alert('[ERROR] Erreur info: ' + error.message);
                }
            }

            // Afficher projections actives
            function showActiveStreams() {
                const section = document.getElementById('projectionsSection');
                section.style.display = section.style.display === 'none' ? 'block' : 'none';
                
                if (section.style.display === 'block') {
                    loadActiveProjections();
                }
            }

            // Charger projections actives
            async function loadActiveProjections() {
                try {
                    const response = await fetch('/api/images/active-streams', {
                        credentials: 'include'
                    });

                    if (response.ok) {
                        const data = await response.json();
                        displayActiveProjections(data.streams);
                    }
                } catch (error) {
                    console.error('Erreur projections:', error);
                }
            }

            // Afficher projections actives
            function displayActiveProjections(streams) {
                const container = document.getElementById('activeProjections');
                
                if (streams.length === 0) {
                    container.innerHTML = '<p>Aucune projection active. Les phantoms sont prêts pour projection ORP!</p>';
                    return;
                }

                container.innerHTML = streams.map(stream => `
                    <div class="card">
                        <h4>📺 Phantom ${stream.phantom_id ? stream.phantom_id.slice(0, 16) : 'Unknown'}...</h4>
                        <p><strong>Nom:</strong> ${stream.phantom_name || 'Sans nom'}</p>
                        <p><strong>Dimensions:</strong> ${stream.dimensions ? stream.dimensions.join('x') : 'N/A'}</p>
                        <p><strong>Fragments:</strong> ${stream.fragments || 0}</p>
                        <p><strong>Type:</strong> ${stream.type || 'phantom_urn'}</p>
                        <p><strong>Status:</strong> ${stream.status}</p>
                        <button class="btn" onclick="startPhantomProjection('${stream.phantom_id}')">� Projection ORP</button>
                        <button class="btn btn-secondary" onclick="viewPhantomInfo('${stream.phantom_id}')">ℹ️ Info</button>
                    </div>
                `).join('');
            }

            // Rejoindre stream
            async function joinStream(streamId) {
                try {
                    const response = await fetch(`/api/images/join-stream/${streamId}`, {
                        method: 'POST',
                        credentials: 'include'
                    });

                    if (response.ok) {
                        alert('[OK] Stream rejoint avec succès!');
                        loadActiveStreams();
                    } else {
                        const error = await response.json();
                        alert('[ERROR] Erreur join: ' + error.detail);
                    }
                } catch (error) {
                    alert('[ERROR] Erreur join: ' + error.message);
                }
            }

            // Voir données stream
            function viewStreamData(streamId) {
                const url = `/api/images/stream-data/${streamId}`;
                window.open(url, '_blank');
            }
        </script>
    </body>
    </html>
    """)

# Section suivante : WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket pour mises à jour temps réel"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Maintenir connexion vivante
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# === API Authentication Endpoints ===

@app.get("/api/auth/status")
async def auth_status():
    """Statut du système d'authentification"""
    global auth_manager
    
    if not auth_manager:
        return {"configured": False, "message": "Auth system not initialized"}
    
    return {
        "configured": auth_manager.has_user(),
        "stats": auth_manager.get_auth_stats() if auth_manager.has_user() else {}
    }

@app.post("/api/auth/setup")
async def auth_setup(setup_data: dict):
    """Configuration initiale du compte utilisateur"""
    global auth_manager
    
    print(f"🔧 Setup request received: {setup_data}")
    
    if not auth_manager:
        print("[ERROR] Auth manager not initialized")
        raise HTTPException(status_code=503, detail="Auth system not initialized")
    
    if auth_manager.has_user():
        print("[WARNING] User already configured")
        raise HTTPException(status_code=400, detail="User already configured")
    
    username = setup_data.get("username", "").strip()
    password = setup_data.get("password", "")
    
    print(f"🔧 Username: '{username}' (len: {len(username)})")
    print(f"🔧 Password length: {len(password)}")
    
    if not username or len(username) < 3:
        print(f"[ERROR] Username too short: '{username}'")
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    
    if not password or len(password) < 6:
        print(f"[ERROR] Password too short: {len(password)} chars")
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    print(f"🔧 Attempting to create user '{username}'...")
    success = auth_manager.create_user(username, password)
    
    if not success:
        print(f"[ERROR] Failed to create user '{username}'")
        raise HTTPException(status_code=400, detail="Failed to create user")
    
    print(f"[OK] User '{username}' created successfully")
    return {
        "success": True,
        "message": f"User '{username}' created successfully",
        "username": username
    }

@app.post("/api/auth/login")
async def auth_login(login_data: dict):
    """Connexion utilisateur"""
    global auth_manager
    
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Auth system not initialized")
    
    if not auth_manager.has_user():
        raise HTTPException(status_code=400, detail="No user configured. Please setup first.")
    
    username = login_data.get("username", "").strip()
    password = login_data.get("password", "")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    token = auth_manager.authenticate(username, password)
    
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Créer la réponse avec le token dans un cookie sécurisé
    response = JSONResponse({
        "success": True,
        "message": "Login successful",
        "token": token,
        "username": username
    })
    
    # Configurer le cookie sécurisé
    response.set_cookie(
        key="openred_token",
        value=token,
        max_age=24 * 60 * 60,  # 24 heures
        httponly=True,  # Empêche accès JavaScript
        secure=False,   # True en HTTPS seulement
        samesite="lax"
    )
    
    return response

@app.post("/api/auth/logout")
async def auth_logout(request: Request):
    """Déconnexion utilisateur"""
    global auth_manager
    
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Auth system not initialized")
    
    token = get_auth_token(request)
    
    if token:
        auth_manager.logout(token)
    
    # Créer la réponse et supprimer le cookie
    response = JSONResponse({
        "success": True,
        "message": "Logout successful"
    })
    
    response.delete_cookie(key="openred_token")
    
    return response

@app.post("/api/auth/change-password")
async def auth_change_password(request: Request, password_data: dict):
    """Changement de mot de passe"""
    global auth_manager
    
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Auth system not initialized")
    
    # Vérifier l'authentification
    username = verify_auth(request)
    
    old_password = password_data.get("old_password", "")
    new_password = password_data.get("new_password", "")
    
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="Old and new passwords required")
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    
    success = auth_manager.change_password(old_password, new_password)
    
    if not success:
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    return {
        "success": True,
        "message": "Password changed successfully"
    }

# === API Endpoints ===

@app.get("/api/health")
async def health_check():
    """Vérification santé du service"""
    global p2p_node
    
    if not p2p_node:
        raise HTTPException(status_code=503, detail="P2P Node not initialized")
        
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "p2p_node_running": p2p_node.running,
        "version": "1.0.0"
    }

@app.get("/api/status")
async def get_node_status(request: Request):
    """Status complet du nœud P2P"""
    # Vérifier l'authentification
    verify_auth(request)
    
    global p2p_node
    
    if not p2p_node:
        raise HTTPException(status_code=503, detail="P2P Node not initialized")
        
    return p2p_node.get_node_status()

@app.get("/api/constellation")
async def get_constellation():
    """Carte de la constellation P2P"""
    global p2p_node
    
    if not p2p_node:
        raise HTTPException(status_code=503, detail="P2P Node not initialized")
        
    discovered = p2p_node.lighthouse.get_discovered_nodes()
    
    constellation_map = []
    for fingerprint, node_info in discovered.items():
        beacon = node_info["beacon"]
        constellation_map.append({
            "fingerprint": fingerprint,
            "node_id": beacon.node_id,
            "sector": beacon.sector,
            "services": beacon.services,
            "capabilities": beacon.capabilities,
            "ip": node_info["ip"],
            "last_seen": time.time() - node_info["last_seen"],
            "phantom_urn_support": beacon.urn_phantom_support,
            "p2p_endpoint": beacon.p2p_endpoint
        })
        
    return {
        "own_node": {
            "fingerprint": p2p_node.lighthouse.fingerprint,
            "node_id": p2p_node.node_id,
            "sector": p2p_node.sector
        },
        "discovered_nodes": constellation_map,
        "total_discovered": len(constellation_map),
        "active_connections": len(p2p_node.p2p_connection.active_connections)
    }

@app.get("/api/urn/stats")
async def get_urn_stats():
    """Statistiques système Phantom URN"""
    global p2p_node
    
    if not p2p_node:
        raise HTTPException(status_code=503, detail="P2P Node not initialized")
        
    return p2p_node.phantom_urn_engine.get_p2p_stats()

@app.post("/api/urn/{urn_id}/resurrect")
async def resurrect_urn(urn_id: str):
    """Résurrection d'un URN via réseau P2P"""
    global p2p_node
    
    if not p2p_node:
        raise HTTPException(status_code=503, detail="P2P Node not initialized")
        
    try:
        result = await p2p_node.resurrect_urn(urn_id)
        
        if result:
            return {
                "success": True,
                "urn_id": urn_id,
                "message": "URN ressuscité avec succès",
                "timestamp": time.time()
            }
        else:
            return {
                "success": False,
                "urn_id": urn_id,
                "message": "URN non trouvé sur le réseau P2P",
                "timestamp": time.time()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur résurrection URN: {str(e)}")

@app.post("/api/urn/test")
async def test_urn_system():
    """Test du système URN/Phantom"""
    global p2p_node
    
    if not p2p_node:
        raise HTTPException(status_code=503, detail="P2P Node not initialized")
        
    test_results = {
        "phantom_urn_engine": "operational" if p2p_node.phantom_urn_engine else "error",
        "local_cache": len(p2p_node.phantom_urn_engine.local_urn_cache),
        "network_index": len(p2p_node.phantom_urn_engine.network_urn_index),
        "timestamp": time.time()
    }
    
    return test_results

# =============================================================================
# PHANTOM STATUS ENDPOINT
# =============================================================================

@app.get("/api/phantom/status")
async def phantom_status(request: Request):
    """Statut du système Enhanced Phantom URN"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system
    
    if not phantom_urn_system:
        return {
            "status": "initializing",
            "phantom_system": False,
            "enhanced_system": False,
            "message": "Phantom URN system not initialized"
        }
    
    return {
        "status": "active",
        "phantom_system": True,
        "enhanced_system": True,
        "phoenix_de_schrodinger": True,
        "nck_system": True,
        "authorization_registry": True,
        "message": "Enhanced Phantom URN System Active"
    }

# =============================================================================
# ENDPOINTS IMAGE URN SYSTEM
# =============================================================================

@app.post("/api/images/upload")
async def upload_image(request: Request, file: UploadFile = File(...)):
    """Upload d'image et traitement asynchrone en URN Phantom"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system, async_processor
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Phantom URN System not initialized")
    
    # Récupérer l'utilisateur
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")
    
    try:
        # Lire le fichier rapidement
        file_data = await file.read()
        
        # Vérifier la taille (max 10MB)
        if len(file_data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
        # Sauvegarder temporairement
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name
        
        # Soumettre le job asynchrone
        if not async_processor:
            from async_phantom_processor import initialize_async_processor
            async_processor = initialize_async_processor(phantom_urn_system)
            await async_processor.start_worker()
        
        job_id = async_processor.submit_job(user_id, file.filename or "phantom_image", temp_path)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Image reçue ! Traitement URN Phantom en cours...",
            "status": "processing",
            "estimated_time": "30-60 secondes",
            "check_status_url": f"/api/images/job-status/{job_id}",
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/images/job-status/{job_id}")
async def get_job_status(job_id: str, request: Request):
    """Vérifier le statut d'un job de traitement URN"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global async_processor
    
    if not async_processor:
        raise HTTPException(status_code=503, detail="Async processor not initialized")
    
    job_status = async_processor.get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_status

@app.get("/api/images/my-jobs")  
async def get_my_jobs(request: Request):
    """Récupérer mes jobs de traitement URN"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global async_processor
    
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not async_processor:
        return {"jobs": []}
    
    jobs = async_processor.get_user_jobs(user_id)
    return {"jobs": jobs}

@app.get("/api/images/my-urns")
async def get_my_phantom_urns(request: Request):
    """Récupérer mes URNs Phantom"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Phantom URN System not initialized")
    
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Lister les phantoms de l'utilisateur depuis active_urns
    active_urns = phantom_urn_system.active_urns if hasattr(phantom_urn_system, 'active_urns') else {}
    
    # Filtrer par propriétaire (pour l'instant tous sont visibles)
    user_phantoms = []
    for phantom_id, phantom_data in active_urns.items():
        user_phantoms.append({
            "phantom_id": phantom_id,
            "phantom_name": phantom_data.get("phantom_name", "Unknown"),
            "dimensions": phantom_data.get("image_dimensions", [0, 0]),
            "total_fragments": phantom_data.get("total_fragments", 0),
            "created_at": phantom_data.get("creation_timestamp", 0),
            "authorized_node": phantom_data.get("authorized_node", "unknown"),
            "type": "enhanced_phantom_urn",
            "schrodinger_enabled": phantom_data.get("schrodinger_enabled", False),
            "nck_system": phantom_data.get("nck_system", False),
            "streaming_url": f"http://localhost:8002/phantom/{phantom_id}",
            "websocket_url": f"ws://localhost:8002/ws"
        })
    
    return {
        "success": True,
        "phantoms": user_phantoms,
        "total": len(user_phantoms),
        "system": "enhanced_phantom_urn"
    }

@app.post("/api/images/start-stream/{phantom_id}")
async def start_phantom_stream(phantom_id: str, request: Request, mode: str = "projection"):
    """Démarrer une projection ORP pour un phantom"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system, projection_server
    
    if not phantom_urn_system or not projection_server:
        raise HTTPException(status_code=503, detail="Phantom System not initialized")
    
    try:
        # Vérifier que le phantom existe
        if phantom_id not in phantom_urn_system.active_urns:
            raise HTTPException(status_code=404, detail="Phantom not found")
        
        # Retourner les infos de streaming
        config = phantom_urn_system.active_urns[phantom_id]
        
        return {
            "success": True,
            "phantom_id": phantom_id,
            "streaming_info": {
                "websocket_url": f"ws://localhost:8002/ws",
                "http_endpoint": f"http://localhost:8002/phantom/{phantom_id}",
                "dimensions": config.get("image_dimensions", [0, 0]),
                "total_fragments": config.get("total_fragments", 0),
                "protocol": "ORP"
            },
            "message": f"Phantom prêt pour projection ORP"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stream error: {e}")

@app.get("/api/images/active-streams")
async def get_active_phantom_streams(request: Request):
    """Liste des phantoms disponibles pour streaming"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system, projection_server
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Phantom System not initialized")
    
    # Lister tous les phantoms actifs depuis active_urns
    active_urns = phantom_urn_system.active_urns if hasattr(phantom_urn_system, 'active_urns') else {}
    
    streams = []
    for phantom_id, phantom_data in active_urns.items():
        streams.append({
            "phantom_id": phantom_id,
            "phantom_name": phantom_data.get("phantom_name", "Unknown"),
            "dimensions": phantom_data.get("image_dimensions", [0, 0]),
            "fragments": phantom_data.get("total_fragments", 0),
            "created_at": phantom_data.get("creation_timestamp", 0),
            "authorized_node": phantom_data.get("authorized_node", "unknown"),
            "streaming_url": f"ws://localhost:8002/ws",
            "status": "available",
            "type": "enhanced_phantom_urn"
        })
    
    return {
        "success": True,
        "streams": streams,
        "total": len(streams),
        "projection_server": "http://localhost:8002"
    }

@app.post("/api/images/join-stream/{stream_id}")
async def join_image_stream(stream_id: str, request: Request):
    """Rejoindre un stream d'image"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global image_urn_system
    
    if not image_urn_system:
        raise HTTPException(status_code=503, detail="Image URN System not initialized")
    
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")
    
    success = image_urn_system.orp_engine.join_stream(stream_id, user_id)
    
    if success:
        return {
            "success": True,
            "stream_id": stream_id,
            "message": "Stream rejoint avec succès"
        }
    else:
        raise HTTPException(status_code=404, detail="Stream not found or already joined")

@app.get("/api/images/stream-data/{stream_id}")
async def get_stream_data(stream_id: str, request: Request, resolution: str = "1280x720"):
    """Récupérer les données d'un stream"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global image_urn_system
    
    if not image_urn_system:
        raise HTTPException(status_code=503, detail="Image URN System not initialized")
    
    stream_data = image_urn_system.orp_engine.get_stream_data(stream_id, resolution)
    
    if stream_data:
        return Response(
            content=stream_data,
            media_type="image/jpeg",
            headers={"Cache-Control": "no-cache"}
        )
    else:
        raise HTTPException(status_code=404, detail="Stream data not found")

@app.post("/api/images/generate-download-token/{urn_id}")
async def generate_download_token(urn_id: str, request: Request):
    """Générer un token de téléchargement pour un URN"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global image_urn_system
    
    if not image_urn_system:
        raise HTTPException(status_code=503, detail="Image URN System not initialized")
    
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")
    
    try:
        token = image_urn_system.generate_download_token(urn_id, user_id)
        
        return {
            "success": True,
            "token": token,
            "urn_id": urn_id,
            "expires_in": 3600,  # 1 heure
            "message": "Token de téléchargement généré"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/images/download/{token}")
async def download_image_urn(token: str):
    """Télécharger une image URN avec token"""
    global image_urn_system
    
    if not image_urn_system:
        raise HTTPException(status_code=503, detail="Image URN System not initialized")
    
    try:
        image_data, filename, mime_type = image_urn_system.download_urn(token)
        
        return Response(
            content=image_data,
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(image_data))
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/images/urn-info/{urn_id}")
async def get_urn_info(urn_id: str, request: Request):
    """Informations sur un URN d'image"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global image_urn_system
    
    if not image_urn_system:
        raise HTTPException(status_code=503, detail="Image URN System not initialized")
    
    urn_info = image_urn_system.get_urn_info(urn_id)
    
    if urn_info:
        return {
            "success": True,
            "urn_info": urn_info
        }
    else:
        raise HTTPException(status_code=404, detail="URN not found")

@app.get("/api/images/system-stats")
async def get_phantom_system_stats(request: Request):
    """Statistiques du système Phantom URN Enhanced"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system, projection_server
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Phantom URN System not initialized")
    
    # Statistiques du système Enhanced
    active_urns = phantom_urn_system.active_urns if hasattr(phantom_urn_system, 'active_urns') else {}
    total_fragments = sum(urn.get("total_fragments", 0) for urn in active_urns.values())
    
    stats = {
        "system_type": "enhanced_phantom_urn",
        "active_phantoms": len(active_urns),
        "total_fragments": total_fragments,
        "schrodinger_phoenixes": len(phantom_urn_system.schrodinger_cache) if hasattr(phantom_urn_system, 'schrodinger_cache') else 0,
        "projection_server": {
            "url": "http://localhost:8002",
            "websocket": "ws://localhost:8002/ws",
            "active_connections": len(projection_server.active_connections) if projection_server else 0
        },
        "fragmentation": {
            "atomic_pixels": True,
            "cryptographic_chaining": True,
            "physical_storage": False,
            "burn_and_phoenix": True
        }
    }
    
    return {
        "success": True,
        "stats": stats,
        "dual_system": {
            "orp_streaming": "Available via WebSocket",
            "urn_fragments": "Cryptographically chained"
        }
    }

# === NOUVEAUX ENDPOINTS SYSTÈME DUAL ===

@app.get("/api/phantom/{phantom_id}/orp")
async def get_phantom_orp_file(phantom_id: str, request: Request):
    """Récupérer le fichier .orp pour diffusion publique"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Phantom URN System not initialized")
    
    if phantom_id not in phantom_urn_system.active_urns:
        raise HTTPException(status_code=404, detail="Phantom not found")
    
    # Retourner les infos pour accéder au .orp
    return {
        "success": True,
        "phantom_id": phantom_id,
        "orp_info": {
            "streaming_url": f"ws://localhost:8002/ws",
            "projection_endpoint": f"http://localhost:8002/phantom/{phantom_id}",
            "type": "orp_streaming",
            "description": "Diffusion publique en streaming ORP"
        }
    }

@app.post("/api/phantom/{phantom_id}/enable-urn-download")
async def enable_urn_download(phantom_id: str, request: Request):
    """Activer le téléchargement URN pour un phantom (décision du propriétaire)"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Phantom URN System not initialized")
    
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")
    
    if phantom_id not in phantom_urn_system.active_urns:
        raise HTTPException(status_code=404, detail="Phantom not found")
    
    # Générer token de téléchargement URN
    import secrets
    download_token = secrets.token_urlsafe(32)
    
    # TODO: Stocker le token avec permissions
    
    return {
        "success": True,
        "phantom_id": phantom_id,
        "urn_download_enabled": True,
        "download_token": download_token,
        "message": "URN téléchargeable activée - fragments atomiques disponibles"
    }

@app.get("/api/phantom/{phantom_id}/phoenix-reconstruction")
async def get_phoenix_reconstruction(phantom_id: str, request: Request, token: Optional[str] = None):
    """Reconstruction Phoenix d'un phantom pour projection"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Phantom URN System not initialized")
    
    if phantom_id not in phantom_urn_system.active_urns:
        raise HTTPException(status_code=404, detail="Phantom not found")
    
    # Token requis pour la reconstruction
    if not token:
        raise HTTPException(status_code=401, detail="Access token required for Phoenix reconstruction")
    
    # Reconstruction Phoenix
    phantom_image = phantom_urn_system.get_phantom_for_projection(phantom_id, token)
    
    if phantom_image is None:
        raise HTTPException(status_code=403, detail="Phoenix reconstruction failed - invalid token or phantom")
    
    # Convertir en base64 pour transmission
    from PIL import Image
    import io
    import base64
    
    pil_image = Image.fromarray(phantom_image)
    buffer = io.BytesIO()
    pil_image.save(buffer, format='JPEG', quality=90)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "success": True,
        "phantom_id": phantom_id,
        "reconstruction": "phoenix_completed",
        "image_data": image_base64,
            "dimensions": phantom_image.shape[:2],
            "warning": "Image reconstruite en mémoire uniquement - aucun stockage physique"
        }

@app.post("/api/enhanced-phantom/burn")
async def burn_image_enhanced(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(None)
):
    """[BURN] Burn Enhanced : Image → Phoenix de Schrödinger avec NCK"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Enhanced Phantom URN System not initialized")
    
    # Validation du fichier
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Sauvegarder temporairement l'image
        image_bytes = await file.read()
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(image_bytes)
            temp_image_path = temp_file.name
        
        try:
            # Burn Enhanced vers Phoenix de Schrödinger
            burn_result = phantom_urn_system.burn_image_to_phantom_urn(
                image_path=temp_image_path,
                phantom_name=title,
                authorized_node="Diego"
            )
            
            # Autoriser l'utilisateur connecté
            user_id = "Diego"  # TODO: Récupérer depuis token
            nck_id = phantom_urn_system.authorize_user_for_phoenix(
                burn_result["phantom_id"],
                user_id,
                {"view": True, "download": True}
            )
            
            return {
                "success": True,
                "message": "[PHOENIX] Phoenix de Schrödinger créé avec succès!",
                "phantom_id": burn_result["phantom_id"],
                "total_fragments": burn_result["total_fragments"],
                "phoenix_key": burn_result["phoenix_key"],
                "schrodinger_matrix": burn_result["schrodinger_matrix"],
                "nck_enabled": burn_result["nck_enabled"],
                "continuous_verification": burn_result["continuous_verification"],
                "user_nck": nck_id,
                "enhanced_features": {
                    "never_fully_reconstructed": True,
                    "quantum_encrypted_state": True,
                    "automatic_key_rotation": True,
                    "continuous_authorization_check": True,
                    "atomic_fragmentation": True
                },
                "actions": {
                    "view_phoenix": f"/api/enhanced-phantom/{burn_result['phantom_id']}/view",
                    "authorize_user": f"/api/enhanced-phantom/{burn_result['phantom_id']}/authorize",
                    "check_status": f"/api/enhanced-phantom/{burn_result['phantom_id']}/status"
                }
            }
            
        finally:
            # Nettoyer fichier temporaire
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                
    except Exception as e:
        print(f"Erreur burn Enhanced: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create Enhanced Phoenix: {str(e)}")

@app.post("/api/enhanced-phantom/{phantom_id}/view")
async def view_phoenix_schrodinger(
    phantom_id: str, 
    request: Request,
    nck: str = Form(...)
):
    """[PHOENIX]→🦅 Voir Phoenix de Schrödinger avec vérification NCK"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Enhanced Phantom URN System not initialized")
    
    try:
        user_id = "Diego"  # TODO: Récupérer depuis token
        
        # Demander résurrection Phoenix avec NCK
        phoenix_matrix = phantom_urn_system.request_phoenix_resurrection(
            phantom_id, user_id, nck
        )
        
        if phoenix_matrix is None:
            raise HTTPException(status_code=403, detail="[KEY] NCK invalide ou accès refusé")
        
        # Convertir en base64 pour transmission
        from PIL import Image
        import io
        import base64
        
        pil_image = Image.fromarray(phoenix_matrix.astype('uint8'))
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG', quality=90)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Récupérer nouvelle NCK
        next_nck = phantom_urn_system.get_user_next_nck(user_id, phantom_id)
        
        return {
            "success": True,
            "message": "[PHOENIX] Phoenix de Schrödinger projeté temporairement",
            "phantom_id": phantom_id,
            "image_data": image_base64,
            "dimensions": phoenix_matrix.shape[:2],
            "next_nck": next_nck,
            "security_notes": [
                "[PHOENIX] Matrice cryptée temporaire uniquement",
                "[KEY] NCK automatiquement rotée",
                "🚫 Jamais de reconstruction complète",
                "[OK] Vérification continue active",
                "[ATOMIC] Image atomiquement fragmentée"
            ],
            "warning": "🔒 Image projetée en mémoire temporaire - Contrôle total propriétaire"
        }
        
    except Exception as e:
        print(f"Erreur view Phoenix: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to view Phoenix: {str(e)}")

@app.post("/api/enhanced-phantom/{phantom_id}/authorize")
async def authorize_user_for_phoenix(
    phantom_id: str,
    request: Request,
    user_id: str = Form(...),
    permissions: str = Form(...)
):
    """[KEY] Autoriser utilisateur avec génération NCK"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Enhanced Phantom URN System not initialized")
    
    try:
        import json
        permissions_dict = json.loads(permissions)
        
        # Autoriser utilisateur
        nck_id = phantom_urn_system.authorize_user_for_phoenix(
            phantom_id, user_id, permissions_dict
        )
        
        return {
            "success": True,
            "message": f"[KEY] Utilisateur {user_id} autorisé avec NCK",
            "phantom_id": phantom_id,
            "user_id": user_id,
            "nck_id": nck_id,
            "permissions": permissions_dict,
            "features": {
                "automatic_key_rotation": True,
                "continuous_verification": True,
                "quantum_security": True
            }
        }
        
    except Exception as e:
        print(f"Erreur autorisation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to authorize user: {str(e)}")

@app.get("/api/enhanced-phantom/{phantom_id}/status")
async def check_phantom_status(phantom_id: str, request: Request):
    """[OK] Vérifier statut Phoenix et serveur"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Enhanced Phantom URN System not initialized")
    
    try:
        # Vérifier statut serveur
        status = phantom_urn_system.verify_server_status(phantom_id)
        
        return {
            "success": True,
            "phantom_id": phantom_id,
            "server_status": status,
            "system_features": {
                "schrodinger_phoenix": True,
                "nck_rotation": True,
                "continuous_verification": True,
                "atomic_fragmentation": True,
                "quantum_encryption": True
            },
            "security_level": "🔒 MAXIMUM - Enhanced Phantom URN"
        }
        
    except Exception as e:
        print(f"Erreur status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check status: {str(e)}")@app.post("/api/images/upload")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(None)
):
    """Téléverser une image normale sur le serveur du nœud propriétaire"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Validation du fichier
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Créer le répertoire d'images si nécessaire
        images_dir = os.path.join(os.path.dirname(__file__), "..", "..", "user_images")
        os.makedirs(images_dir, exist_ok=True)
        
        # Générer un nom de fichier unique
        import uuid
        from datetime import datetime
        
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.png'
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = os.path.join(images_dir, unique_filename)
        
        # Sauvegarder l'image
        image_bytes = await file.read()
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        
        # Obtenir les informations de l'image
        from PIL import Image
        pil_image = Image.open(file_path)
        
        # Générer un ID d'image
        image_id = uuid.uuid4().hex
        
        # Métadonnées de l'image
        image_info = {
            "image_id": image_id,
            "title": title,
            "description": description,
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "dimensions": f"{pil_image.width}x{pil_image.height}",
            "total_pixels": pil_image.width * pil_image.height,
            "file_size": len(image_bytes),
            "upload_time": datetime.now().isoformat(),
            "owner": "Diego"  # Utilisateur connecté
        }
        
        return {
            "success": True,
            "message": "Image téléversée avec succès",
            "image_info": image_info,
            "actions": {
                "create_phantom": f"/api/images/{image_id}/create-phantom",
                "create_phantom_urn": f"/api/images/{image_id}/create-phantom-urn",
                "view_image": f"/api/images/{image_id}"
            }
        }
        
    except Exception as e:
        print(f"Erreur lors du téléversement: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@app.post("/api/images/{image_id}/create-phantom")
async def create_phantom_from_image(image_id: str, request: Request):
    """Créer une version phantom (ORP) à partir d'une image stockée"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # TODO: Récupérer les métadonnées de l'image depuis une base de données ou un stockage
    # Pour l'instant, on va chercher dans le répertoire
    images_dir = os.path.join(os.path.dirname(__file__), "..", "..", "user_images")
    
    # Trouver l'image (simplification pour le prototype)
    import glob
    image_files = glob.glob(os.path.join(images_dir, "*"))
    
    if not image_files:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Prendre la première image trouvée (à améliorer avec vraie DB)
    image_path = image_files[0]
    
    return {
        "success": True,
        "message": "Phantom ORP créé",
        "image_id": image_id,
        "phantom_type": "ORP",
        "projection_url": f"http://localhost:8002/phantom/{image_id}/orp"
    }
async def burn_image_to_phantom_urn(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(None)
):
    """Brûler une image vers le système Phantom URN avec fragmentation atomique"""
    if not verify_auth(request):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global phantom_urn_system
    
    if not phantom_urn_system:
        raise HTTPException(status_code=503, detail="Phantom URN System not initialized")
    
    # Validation du fichier
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Lire et traiter l'image
        image_bytes = await file.read()
        
        from PIL import Image
        import io
        import tempfile
        import os
        
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Convertir en mode RGB si nécessaire
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Sauvegarder temporairement l'image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            pil_image.save(temp_file.name, format='PNG')
            temp_image_path = temp_file.name
        
        try:
            # Brûler l'image vers le système Phantom URN
            urn_result = phantom_urn_system.burn_image_to_phantom_urn(
                image_path=temp_image_path,
                phantom_name=title,
                authorized_node="Diego"  # Utiliser l'utilisateur connecté
            )
            
            return {
                "success": True,
                "urn_id": urn_result["phantom_id"],
                "total_fragments": urn_result["total_fragments"],
                "phoenix_key": urn_result["phoenix_key"],
                "projection_url": f"http://localhost:8002/phantom/{urn_result['phantom_id']}/orp",
                "urn_info": {
                    "title": title,
                    "description": description,
                    "dimensions": f"{pil_image.width}x{pil_image.height}",
                    "total_pixels": pil_image.width * pil_image.height,
                    "fragmentation": "atomic"
                },
                "message": f"Image fragmentée en {urn_result['total_fragments']} atomes cryptographiques"
            }
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
        
    except Exception as e:
        print(f"Erreur lors de la création du Phantom URN: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create Phantom URN: {str(e)}")

@app.get("/api/security")
async def get_security_status():
    """Status sécurité P2P"""
    global p2p_node
    
    if not p2p_node:
        raise HTTPException(status_code=503, detail="P2P Node not initialized")
        
    return p2p_node.security_protocol.get_security_stats()

@app.post("/api/connect/{target_fingerprint}")
async def connect_to_peer(target_fingerprint: str):
    """Initie connexion P2P avec un nœud spécifique"""
    global p2p_node
    
    if not p2p_node:
        raise HTTPException(status_code=503, detail="P2P Node not initialized")
        
    try:
        success = p2p_node.lighthouse.initiate_p2p_connection(target_fingerprint)
        
        return {
            "success": success,
            "target_fingerprint": target_fingerprint,
            "message": "Connexion établie" if success else "Échec connexion",
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur connexion: {str(e)}")

# === ROUTES SOCIAL/FRIENDSHIP ===

@app.get("/api/social/available-nodes")
async def get_available_nodes():
    """Liste des nœuds disponibles pour l'amitié"""
    global p2p_node, friendship_system
    
    if not p2p_node:
        raise HTTPException(status_code=503, detail="P2P Node not initialized")
    
    # Récupérer les nœuds découverts
    discovered = p2p_node.lighthouse.get_discovered_nodes()
    
    # Liste des amis existants pour filtrer
    existing_friends = set()
    if friendship_system:
        friends = friendship_system.get_friends_list()
        existing_friends = {friend.friend_fingerprint for friend in friends}
    
    # Construire la liste des nœuds disponibles
    available_nodes = []
    for fingerprint, info in discovered.items():
        # Exclure son propre nœud et les amis existants
        if fingerprint != p2p_node.lighthouse.fingerprint and fingerprint not in existing_friends:
            node_data = {
                "fingerprint": fingerprint,
                "node_id": info["beacon"].node_id,
                "sector": info["beacon"].sector,
                "ip": info["ip"],
                "last_seen": time.time() - info["last_seen"],
                "phantom_urn_support": info["beacon"].urn_phantom_support,
                "rssi": info.get("rssi", 0),
                "can_send_friend_request": True
            }
            
            # Ajouter les informations de profil si disponibles dans le beacon
            if hasattr(info["beacon"], 'discovery_info') and info["beacon"].discovery_info:
                node_data["profile_info"] = info["beacon"].discovery_info
            
            available_nodes.append(node_data)
    
    # Trier par dernière vue (plus récents en premier)
    available_nodes.sort(key=lambda x: x["last_seen"])
    
    return {
        "available_nodes": available_nodes,
        "total_available": len(available_nodes),
        "total_discovered": len(discovered),
        "own_fingerprint": p2p_node.lighthouse.fingerprint
    }

@app.get("/api/social/friends")
async def get_friends_list():
    """Liste des amis acceptés avec informations de profil"""
    global friendship_system, p2p_node
    
    if not friendship_system:
        raise HTTPException(status_code=503, detail="Friendship system not initialized")
    
    friends = friendship_system.get_friends_list()
    friends_data = []
    
    # Récupérer les nœuds découverts pour enrichir les informations
    discovered_nodes = {}
    if p2p_node:
        discovered_nodes = p2p_node.lighthouse.get_discovered_nodes()
    
    for friend in friends:
        friend_data = {
            "fingerprint": friend.friend_fingerprint,
            "node_id": friend.friend_node_id,
            "status": friend.status.value,
            "created_at": friend.created_at,
            "last_interaction": friend.last_interaction,
            "trust_score": friend.trust_score,
            "permissions_granted": {
                "messaging": friend.permissions_granted.messaging,
                "urn_access": friend.permissions_granted.urn_access,
                "photo_sharing": friend.permissions_granted.photo_sharing,
                "file_sharing": friend.permissions_granted.file_sharing,
                "presence_info": friend.permissions_granted.presence_info
            },
            "permissions_received": {
                "messaging": friend.permissions_received.messaging,
                "urn_access": friend.permissions_received.urn_access,
                "photo_sharing": friend.permissions_received.photo_sharing,
                "file_sharing": friend.permissions_received.file_sharing,
                "presence_info": friend.permissions_received.presence_info
            }
        }
        
        # Ajouter les informations de profil si disponibles
        if friend.friend_fingerprint in discovered_nodes:
            node_info = discovered_nodes[friend.friend_fingerprint]
            beacon = node_info.get("beacon")
            if beacon and hasattr(beacon, 'discovery_info'):
                discovery_info = beacon.discovery_info
                friend_data.update({
                    "profile": {
                        "display_name": discovery_info.get("display_name", friend.friend_node_id),
                        "real_name": discovery_info.get("real_name", ""),
                        "bio": discovery_info.get("bio", ""),
                        "sector": discovery_info.get("sector", ""),
                        "profession": discovery_info.get("profession", ""),
                        "location": discovery_info.get("location", ""),
                        "interests": discovery_info.get("interests", []),
                        "profile_picture": discovery_info.get("profile_picture", None)
                    },
                    "online": True,
                    "last_seen": node_info.get("last_seen", 0)
                })
            else:
                friend_data.update({
                    "profile": {
                        "display_name": friend.friend_node_id,
                        "real_name": "",
                        "bio": "",
                        "sector": "",
                        "profession": "",
                        "location": "",
                        "interests": [],
                        "profile_picture": None
                    },
                    "online": True,
                    "last_seen": node_info.get("last_seen", 0)
                })
        else:
            # Ami hors ligne - pas d'informations de profil récentes
            friend_data.update({
                "profile": {
                    "display_name": friend.friend_node_id,
                    "real_name": "",
                    "bio": "",
                    "sector": "",
                    "profession": "",
                    "location": "",
                    "interests": [],
                    "profile_picture": None
                },
                "online": False,
                "last_seen": friend.last_interaction
            })
        
        friends_data.append(friend_data)
    
    return {
        "friends": friends_data,
        "total_friends": len(friends_data),
        "stats": friendship_system.get_friendship_stats()
    }

@app.get("/api/social/friend-requests")
async def get_friend_requests():
    """Demandes d'amitié en attente"""
    global friendship_system
    
    if not friendship_system:
        raise HTTPException(status_code=503, detail="Friendship system not initialized")
    
    requests = friendship_system.get_pending_requests()
    requests_data = []
    
    for request in requests:
        requests_data.append({
            "request_id": request.request_id,
            "from_fingerprint": request.from_fingerprint,
            "from_node_id": request.from_node_id,
            "message": request.message,
            "timestamp": request.timestamp,
            "requested_permissions": {
                "messaging": request.requested_permissions.messaging,
                "urn_access": request.requested_permissions.urn_access,
                "photo_sharing": request.requested_permissions.photo_sharing,
                "file_sharing": request.requested_permissions.file_sharing,
                "presence_info": request.requested_permissions.presence_info
            }
        })
    
    return {
        "pending_requests": requests_data,
        "total_requests": len(requests_data)
    }

@app.post("/api/social/send-friend-request")
async def send_friend_request(request_data: Dict):
    """Envoie une demande d'amitié"""
    global friendship_system, p2p_node
    
    if not friendship_system:
        raise HTTPException(status_code=503, detail="Friendship system not initialized")
    
    try:
        target_fingerprint = request_data["target_fingerprint"]
        message = request_data.get("message", "Demande d'amitié")
        
        # Récupérer le node_id depuis les nœuds découverts
        target_node_id = None
        if p2p_node:
            discovered = p2p_node.lighthouse.get_discovered_nodes()
            if target_fingerprint in discovered:
                target_node_id = discovered[target_fingerprint]["beacon"].node_id
        
        if not target_node_id:
            raise HTTPException(status_code=404, detail="Node not found in discovered nodes")
        
        # Créer permissions par défaut (niveau 2 - standard)
        level = PermissionLevel(request_data.get("permission_level", 2))
        permissions = FriendshipPermissions.from_level(level)
        
        # Envoyer la demande
        request = friendship_system.send_friendship_request(
            target_fingerprint=target_fingerprint,
            target_node_id=target_node_id,
            message=message,
            permissions=permissions
        )
        
        # Envoyer via P2P avec protocole simple
        friendship_request_sent = await send_friendship_request_p2p(
            target_fingerprint, request
        )
        
        return {
            "success": True,
            "request_id": request.request_id,
            "target_node_id": target_node_id,
            "p2p_sent": friendship_request_sent,
            "message": "Demande d'amitié envoyée" + (" via P2P" if friendship_request_sent else " (local seulement)"),
            "timestamp": time.time()
        }
        
    except Exception as e:
        print(f"[ERROR] Error sending friend request: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur envoi demande: {str(e)}")

@app.post("/api/social/accept-friend-request/{request_id}")
async def accept_friend_request(request_id: str, response_data: Dict):
    """Accepte une demande d'amitié"""
    global friendship_system, p2p_node
    
    if not friendship_system:
        raise HTTPException(status_code=503, detail="Friendship system not initialized")
    
    try:
        # Récupérer les informations de la demande avant acceptation
        if request_id not in friendship_system.pending_requests:
            raise HTTPException(status_code=404, detail="Demande introuvable")
        
        request = friendship_system.pending_requests[request_id]
        original_sender_fingerprint = request.from_fingerprint
        original_sender_node_id = request.from_node_id
        
        # Créer permissions accordées
        level = PermissionLevel(response_data.get("permission_level", 1))
        granted_permissions = FriendshipPermissions.from_level(level)
        
        success = friendship_system.accept_friendship_request(request_id, granted_permissions)
        
        if success and p2p_node:
            # Notifier l'expéditeur original que sa demande a été acceptée
            print(f"[UPLOAD] Notifying {original_sender_node_id} that friendship was accepted")
            
            # Préparer notification d'acceptation
            acceptance_data = {
                "request_id": request_id,
                "accepted_by_fingerprint": friendship_system.fingerprint,
                "accepted_by_node_id": friendship_system.node_id,
                "granted_permissions": {
                    "messaging": granted_permissions.messaging,
                    "urn_access": granted_permissions.urn_access,
                    "photo_sharing": granted_permissions.photo_sharing,
                    "file_sharing": granted_permissions.file_sharing,
                    "presence_info": granted_permissions.presence_info
                },
                "timestamp": time.time()
            }
            
            # Envoyer via protocole simple DIRECTEMENT comme friendship_accepted
            try:
                discovered = p2p_node.lighthouse.get_discovered_nodes()
                if original_sender_fingerprint in discovered:
                    target_info = discovered[original_sender_fingerprint]
                    target_ip = target_info["ip"]
                    beacon = target_info["beacon"]
                    target_port = beacon.p2p_endpoint["port"]
                    
                    # Envoyer notification via protocole simple SANS encapsuler dans friendship_request
                    notification_sent = await send_friendship_request_simple(
                        target_fingerprint=original_sender_fingerprint,
                        target_ip=target_ip,
                        target_port=target_port,
                        request_data={
                            "type": "friendship_accepted",
                            "data": acceptance_data
                        }
                    )
                    
                    if notification_sent:
                        print(f"[OK] Acceptance notification sent to {original_sender_node_id}")
                    else:
                        print(f"[ERROR] Failed to send acceptance notification to {original_sender_node_id}")
                        
                else:
                    print(f"[WARNING] Cannot notify {original_sender_node_id} - not discovered")
                    
            except Exception as notify_error:
                print(f"[ERROR] Error sending acceptance notification: {notify_error}")
        
        return {
            "success": success,
            "message": "Demande acceptée" if success else "Erreur acceptation",
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur acceptation: {str(e)}")

@app.post("/api/social/reject-friend-request/{request_id}")
async def reject_friend_request(request_id: str, response_data: Dict):
    """Rejette une demande d'amitié"""
    global friendship_system
    
    if not friendship_system:
        raise HTTPException(status_code=503, detail="Friendship system not initialized")
    
    try:
        reason = response_data.get("reason", "")
        success = friendship_system.reject_friendship_request(request_id, reason)
        
        return {
            "success": success,
            "message": "Demande rejetée" if success else "Erreur rejet",
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur rejet: {str(e)}")

# === ROUTES MESSAGING ===

@app.get("/api/social/conversations")
async def get_conversations():
    """Liste des conversations distribuées"""
    global messaging_system
    
    if not messaging_system:
        raise HTTPException(status_code=503, detail="Messaging system not initialized")
    
    conversations = messaging_system.get_conversations_list()
    
    return {
        "conversations": conversations,
        "total_conversations": len(conversations),
        "stats": messaging_system.get_messaging_stats()
    }

@app.get("/api/social/conversation/{conversation_id}")
async def get_conversation_messages(conversation_id: str, auto_sync: bool = True):
    """Messages d'une conversation distribuée"""
    global messaging_system
    
    if not messaging_system:
        raise HTTPException(status_code=503, detail="Messaging system not initialized")
    
    # Récupérer la conversation
    if conversation_id not in messaging_system.conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = messaging_system.conversations[conversation_id]
    
    try:
        # Ouvrir la conversation avec synchronisation
        conversation_data = await messaging_system.open_conversation(
            participants=conversation.participants,
            auto_sync=auto_sync
        )
        
        return conversation_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading conversation: {str(e)}")

@app.post("/api/social/sync-conversation/{conversation_id}")
async def sync_conversation(conversation_id: str):
    """Force la synchronisation d'une conversation"""
    global messaging_system
    
    if not messaging_system:
        raise HTTPException(status_code=503, detail="Messaging system not initialized")
    
    if conversation_id not in messaging_system.conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = messaging_system.conversations[conversation_id]
    
    try:
        # Forcer synchronisation pour tous les participants
        sync_results = {}
        for participant_fp in conversation.participants:
            if participant_fp != messaging_system.fingerprint:
                messages = await messaging_system.fetch_messages_from_participant(participant_fp)
                sync_results[participant_fp] = len(messages)
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "sync_results": sync_results,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing conversation: {str(e)}")

@app.get("/api/social/my-messages")
async def get_my_sent_messages(participant_fp: Optional[str] = None):
    """Récupère mes messages envoyés (pour servir aux autres)"""
    global messaging_system
    
    if not messaging_system:
        raise HTTPException(status_code=503, detail="Messaging system not initialized")
    
    if participant_fp:
        # Messages pour un participant spécifique
        messages = messaging_system.serve_my_messages_for_conversation(participant_fp)
    else:
        # Tous mes messages envoyés
        messages = list(messaging_system.sent_messages.values())
    
    messages_data = []
    for message in messages:
        messages_data.append({
            "message_id": message.message_id,
            "from_fingerprint": message.from_fingerprint,
            "to_fingerprint": message.to_fingerprint,
            "message_type": message.message_type.value,
            "content": message.content,
            "metadata": message.metadata,
            "timestamp": message.timestamp,
            "status": message.status.value,
            "reply_to": message.reply_to
        })
    
    return {
        "messages": messages_data,
        "total_messages": len(messages_data),
        "participant_filter": participant_fp
    }

@app.post("/api/social/send-message")
async def send_message(message_data: Dict):
    """Envoie un message"""
    global messaging_system
    
    if not messaging_system:
        raise HTTPException(status_code=503, detail="Messaging system not initialized")
    
    try:
        recipient_fingerprint = message_data["recipient_fingerprint"]
        content = message_data["content"]
        reply_to = message_data.get("reply_to")
        
        message = messaging_system.send_text_message(
            recipient_fingerprint=recipient_fingerprint,
            content=content,
            reply_to=reply_to
        )
        
        if message:
            return {
                "success": True,
                "message_id": message.message_id,
                "message": "Message envoyé",
                "timestamp": time.time()
            }
        else:
            return {
                "success": False,
                "message": "Permission de messagerie manquante",
                "timestamp": time.time()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur envoi message: {str(e)}")

# === ROUTES URN SHARING ===

@app.get("/api/social/shared-urns")
async def get_shared_urns():
    """URN partagés par moi"""
    global urn_sharing_system
    
    if not urn_sharing_system:
        raise HTTPException(status_code=503, detail="URN sharing system not initialized")
    
    shared_urns = urn_sharing_system.get_my_shared_urns()
    received_urns = urn_sharing_system.get_received_urns()
    
    return {
        "shared_by_me": shared_urns,
        "received_from_friends": received_urns,
        "stats": urn_sharing_system.get_sharing_stats()
    }

@app.post("/api/social/share-urn")
async def share_urn_with_friend(share_data: Dict):
    """Partage un URN avec un ami"""
    global urn_sharing_system
    
    if not urn_sharing_system:
        raise HTTPException(status_code=503, detail="URN sharing system not initialized")
    
    try:
        urn_id = share_data["urn_id"]
        friend_fingerprint = share_data["friend_fingerprint"]
        message = share_data.get("message", "")
        
        success = urn_sharing_system.share_urn_with_friend(
            urn_id=urn_id,
            friend_fingerprint=friend_fingerprint,
            message=message
        )
        
        return {
            "success": success,
            "message": "URN partagé" if success else "Partage refusé",
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur partage URN: {str(e)}")

@app.post("/api/social/create-urn-rule")
async def create_urn_access_rule(rule_data: Dict):
    """Crée une règle d'accès URN"""
    global urn_sharing_system
    
    if not urn_sharing_system:
        raise HTTPException(status_code=503, detail="URN sharing system not initialized")
    
    try:
        urn_id = rule_data["urn_id"]
        access_level = URNAccessLevel(rule_data["access_level"])
        allowed_fingerprints = set(rule_data.get("allowed_fingerprints", []))
        expires_hours = rule_data.get("expires_hours")
        max_usage = rule_data.get("max_usage")
        
        rule = urn_sharing_system.create_urn_access_rule(
            urn_id=urn_id,
            access_level=access_level,
            allowed_fingerprints=allowed_fingerprints,
            expires_hours=expires_hours,
            max_usage=max_usage
        )
        
        return {
            "success": True,
            "rule_id": rule.urn_id,
            "message": "Règle d'accès créée",
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création règle: {str(e)}")

# Servir fichiers statiques (interface avancée)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "frontend")), name="static")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Dashboard avancé avec interface moderne"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dashboard.html")
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("Dashboard non trouvé", status_code=404)

@app.get("/friends", response_class=HTMLResponse)
async def friends_page():
    """Page de gestion des amis"""
    friends_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "friends.html")
    try:
        with open(friends_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("Page amis non trouvée", status_code=404)

@app.get("/profile", response_class=HTMLResponse)
async def profile_page():
    """Page de profil utilisateur"""
    profile_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "profile.html")
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("Page profil non trouvée", status_code=404)

@app.get("/constellation", response_class=HTMLResponse)
async def constellation_view():
    """Vue constellation complète"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>OpenRed Constellation</title></head>
    <body>
        <h1>🌟 Constellation P2P</h1>
        <p><a href="/">Retour accueil</a></p>
    </body>
    </html>
    """

@app.get("/api/profile")
async def get_user_profile():
    """Récupère le profil utilisateur"""
    if not profile_manager or not profile_manager.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "profile": asdict(profile_manager.profile),
        "groups": [asdict(group) for group in profile_manager.friend_groups]
    }

@app.put("/api/profile")
async def update_user_profile(profile_data: dict):
    """Met à jour le profil utilisateur"""
    if not profile_manager:
        raise HTTPException(status_code=404, detail="Profile manager not initialized")
    
    # Filtrer les champs autorisés
    allowed_fields = ["display_name", "real_name", "bio", "sector", "location", "profession", "interests", "privacy_settings"]
    update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
    
    profile_manager.update_profile(**update_data)
    
    return {"success": True, "message": "Profile updated successfully"}

@app.post("/api/profile/groups")
async def create_friend_group(group_data: dict):
    """Crée un nouveau groupe d'amis"""
    if not profile_manager:
        raise HTTPException(status_code=404, detail="Profile manager not initialized")
    
    name = group_data.get("name", "")
    description = group_data.get("description", "")
    color = group_data.get("color", "#9C27B0")
    
    if not name:
        raise HTTPException(status_code=400, detail="Group name is required")
    
    group = profile_manager.create_custom_group(name, description, color)
    return {"success": True, "group": asdict(group)}

@app.put("/api/profile/groups/{group_id}/members")
async def manage_group_member(group_id: str, member_data: dict):
    """Ajoute ou retire un membre d'un groupe"""
    if not profile_manager:
        raise HTTPException(status_code=404, detail="Profile manager not initialized")
    
    fingerprint = member_data.get("fingerprint", "")
    action = member_data.get("action", "add")  # "add" ou "remove"
    
    if not fingerprint:
        raise HTTPException(status_code=400, detail="Member fingerprint is required")
    
    if action == "add":
        success = profile_manager.add_friend_to_group(fingerprint, group_id)
    elif action == "remove":
        success = profile_manager.remove_friend_from_group(fingerprint, group_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    if not success:
        raise HTTPException(status_code=404, detail="Group not found or operation failed")
    
    return {"success": True, "message": f"Member {action}ed successfully"}

@app.get("/api/profile/discovery-info")
async def get_discovery_info():
    """Récupère les informations de découverte P2P"""
    if not profile_manager:
        raise HTTPException(status_code=404, detail="Profile manager not initialized")
    
    return profile_manager.get_discovery_info()

@app.post("/api/profile/picture")
async def upload_profile_picture(picture_data: dict):
    """Met à jour la photo de profil"""
    if not profile_manager:
        raise HTTPException(status_code=404, detail="Profile manager not initialized")
    
    image_data = picture_data.get("image_data", "")
    if not image_data:
        raise HTTPException(status_code=400, detail="Image data is required")
    
    # Vérifier que c'est du base64 valide
    try:
        import base64
        base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image data format")
    
    success = profile_manager.set_profile_picture(image_data)
    if success:
        return {"success": True, "message": "Profile picture updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update profile picture")

@app.get("/api/profile/picture")
async def get_profile_picture():
    """Récupère la photo de profil publique"""
    if not profile_manager:
        raise HTTPException(status_code=404, detail="Profile manager not initialized")
    
    picture = profile_manager.get_public_profile_picture()
    if picture:
        return {"profile_picture": picture}
    else:
        return {"profile_picture": None}

# === ROUTES INTERNET SPIDER ===

@app.get("/api/spider/status")
async def get_spider_status():
    """Statut du spider de découverte Internet"""
    global internet_spider
    
    if not internet_spider:
        return {
            "available": False,
            "status": "not_initialized",
            "message": "Internet Spider Protocol not available"
        }
    
    stats = internet_spider.get_stats()
    return {
        "available": True,
        "status": "running" if internet_spider.running else "stopped",
        "stats": stats,
        "discovered_nodes": len(internet_spider.internet_nodes)
    }

@app.post("/api/spider/start")
async def start_spider():
    """Démarre le spider de découverte Internet"""
    global internet_spider
    
    if not internet_spider:
        raise HTTPException(status_code=503, detail="Internet Spider not available")
    
    if internet_spider.running:
        return {"success": False, "message": "Spider already running"}
    
    internet_spider.start_spider()
    return {"success": True, "message": "Internet Spider started"}

@app.post("/api/spider/stop")
async def stop_spider():
    """Arrête le spider de découverte Internet"""
    global internet_spider
    
    if not internet_spider:
        raise HTTPException(status_code=503, detail="Internet Spider not available")
    
    if not internet_spider.running:
        return {"success": False, "message": "Spider already stopped"}
    
    internet_spider.stop_spider()
    return {"success": True, "message": "Internet Spider stopped"}

@app.get("/api/spider/nodes")
async def get_internet_nodes():
    """Liste des nœuds Internet découverts"""
    global internet_spider
    
    if not internet_spider:
        raise HTTPException(status_code=503, detail="Internet Spider not available")
    
    nodes = internet_spider.get_internet_nodes()
    return {
        "internet_nodes": [
            {
                "fingerprint": node.fingerprint,
                "node_id": node.node_id,
                "ip": node.ip,
                "port": node.port,
                "last_seen": node.last_seen,
                "trust_score": node.trust_score,
                "verified": node.verified,
                "discovery_method": node.discovery_method,
                "response_time": node.response_time
            }
            for node in nodes
        ],
        "total_nodes": len(nodes)
    }

if __name__ == "__main__":
    # Configuration serveur
    port = int(os.getenv("OPENRED_WEB_PORT", "8000"))
    
    print(f"[SERVER] Starting OpenRed P2P Web Interface on port {port}...")
    
    uvicorn.run(
        "web_api:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Pas de reload en production
        log_level="info"
    )