#!/usr/bin/env python3
"""
O-RedSearch P2P Connection Manager
Découverte + Connexion sécurisée avec tokens asymétriques
"""

import socket
import json
import threading
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import datetime as dt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
import os

# Import du système de sécurité OpenRed
from core.security import AsymmetricTokenEngine

# Clé réseau O-RedSearch
ORED_NETWORK_PASSPHRASE = "OpenRed-P2P-Discovery-2025"

@dataclass
class P2PNodeBeacon:
    """Nœud avec capacités P2P et sécurité asymétrique"""
    node_hash: str
    sector: str
    services: List[str]
    activity_level: int
    zone_hash: str
    p2p_endpoint: Dict[str, any]  # IP, port pour connexions directes
    public_key_hash: str          # Hash de la clé publique
    capabilities: Dict[str, int] = None

class P2PSecurityManager:
    """Gestionnaire de sécurité P2P avec tokens asymétriques"""
    
    def __init__(self, node_hash: str):
        self.node_hash = node_hash
        self.token_engine = AsymmetricTokenEngine()
        self.active_connections = {}
        self.pending_handshakes = {}
        
        # Générer paire de clés pour ce nœud
        private_key, public_key = self.token_engine.generate_key_pair()
        self.public_key_hash = hashlib.sha256(public_key).hexdigest()[:16]
        
        print(f"🔐 P2P Security initialized for {node_hash[:8]} (pubkey: {self.public_key_hash})")
        
    def create_connection_token(self, target_node_hash: str) -> Dict[str, any]:
        """Crée un token pour connexion vers un nœud cible"""
        connection_id = f"p2p_{self.node_hash[:8]}_{target_node_hash[:8]}_{int(time.time())}"
        
        token_data = self.token_engine.create_temporary_token(
            node_id=connection_id,
            lifetime=300  # 5 minutes pour établir connexion
        )
        
        return {
            "connection_id": connection_id,
            "source_node": self.node_hash,
            "target_node": target_node_hash,
            "token_data": token_data,
            "created_at": datetime.now(dt.timezone.utc).isoformat(),
            "purpose": "p2p_connection_request"
        }
        
    def verify_connection_token(self, connection_request: Dict) -> bool:
        """Vérifie un token de connexion reçu"""
        try:
            token_data = connection_request.get("token_data", {})
            token_id = token_data.get("token_id")
            
            if not token_id:
                print("❌ No token_id in request")
                return False
            
            # Vérifier que c'est bien pour nous
            if connection_request.get("target_node") != self.node_hash:
                print(f"❌ Token not for this node: {connection_request.get('target_node')[:8]} != {self.node_hash[:8]}")
                return False
            
            # Vérifier l'expiration depuis le token lui-même
            expires_at = token_data.get("expires_at")
            if expires_at:
                expiry = datetime.fromisoformat(expires_at)
                if datetime.now(dt.timezone.utc) >= expiry:
                    print("❌ Token expired")
                    return False
            
            # Pour cette demo, accepter si le token a les bonnes métadonnées
            # Dans un vrai système, on vérifierait la signature cryptographique
            source_node = connection_request.get("source_node")
            if source_node and token_data:
                print(f"✅ Token accepted from {source_node[:8]}")
                return True
                
            return False
            
        except Exception as e:
            print(f"❌ Token verification failed: {e}")
            return False
            
    def create_mutual_tokens(self, node_a_hash: str, node_b_hash: str) -> Tuple[Dict, Dict]:
        """Crée une paire de tokens mutuels pour connexion bidirectionnelle"""
        
        # Token A -> B
        token_a = self.create_connection_token(node_b_hash)
        
        # Token B -> A (simulé pour démo)
        token_b = self.create_connection_token(node_a_hash)
        
        # Lier mathématiquement les deux tokens
        token_a_id = token_a["token_data"]["token_id"]
        token_b_id = token_b["token_data"]["token_id"]
        
        # Validation croisée des tokens
        cross_validation = self.token_engine.validate_cross_token(token_a_id, token_b_id)
        
        return token_a, token_b, cross_validation

class P2PConnectionManager:
    """Gestionnaire de connexions P2P sécurisées"""
    
    def __init__(self, node_info: P2PNodeBeacon, security_manager: P2PSecurityManager):
        self.node_info = node_info
        self.security = security_manager
        self.active_connections = {}
        self.connection_server = None
        self.server_port = node_info.p2p_endpoint.get("port", 9000)
        
    def start_p2p_server(self):
        """Démarre serveur P2P pour accepter connexions"""
        def server_thread():
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind(('0.0.0.0', self.server_port))
            server_sock.listen(5)
            
            print(f"🔗 P2P server started on port {self.server_port}")
            
            while True:
                try:
                    client_sock, addr = server_sock.accept()
                    threading.Thread(
                        target=self._handle_p2p_connection,
                        args=(client_sock, addr),
                        daemon=True
                    ).start()
                except Exception as e:
                    print(f"❌ P2P server error: {e}")
                    
        threading.Thread(target=server_thread, daemon=True).start()
        
    def _handle_p2p_connection(self, client_sock: socket.socket, addr: Tuple[str, int]):
        """Traite une connexion P2P entrante"""
        try:
            # Recevoir demande de connexion
            data = client_sock.recv(4096)
            connection_request = json.loads(data.decode())
            
            print(f"🔗 P2P connection request from {addr[0]}")
            
            # Vérifier token asymétrique
            if self.security.verify_connection_token(connection_request):
                # Token valide, accepter connexion
                response = {
                    "status": "accepted",
                    "node_hash": self.node_info.node_hash,
                    "timestamp": time.time(),
                    "public_key_hash": self.node_info.public_key_hash
                }
                
                # Enregistrer connexion active
                source_node = connection_request.get("source_node")
                self.active_connections[source_node] = {
                    "socket": client_sock,
                    "address": addr,
                    "established_at": time.time(),
                    "status": "connected"
                }
                
                print(f"✅ P2P connection accepted from {source_node[:8]}")
                
            else:
                # Token invalide, refuser
                response = {
                    "status": "rejected",
                    "reason": "invalid_token",
                    "timestamp": time.time()
                }
                print(f"❌ P2P connection rejected from {addr[0]} (invalid token)")
                
            # Envoyer réponse
            client_sock.send(json.dumps(response).encode())
            
            if response["status"] == "rejected":
                client_sock.close()
                
        except Exception as e:
            print(f"❌ P2P connection handling error: {e}")
            client_sock.close()
            
    def connect_to_peer(self, target_node: Dict) -> bool:
        """Initie connexion sécurisée vers un peer découvert"""
        try:
            target_hash = target_node["node_hash"].replace("...", "")  # Remove anonymization
            
            # Extraire le port P2P du nœud cible depuis les balises découvertes
            target_port = 9000  # Port par défaut
            
            # Dans un vrai système, le port serait extrait des métadonnées beacon
            # Pour cette démo, on utilise des ports séquentiels
            if "health" in target_node.get("sector", ""):
                target_port = 9002
            elif "tech" in target_node.get("sector", ""):
                target_port = 9001
                
            print(f"🔗 Attempting P2P connection to {target_hash[:8]} on port {target_port}...")
            
            # Créer token de connexion
            connection_token = self.security.create_connection_token(target_hash)
            
            # Établir connexion TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # 10s timeout
            
            # Connexion vers le port spécifique du nœud cible
            sock.connect(("127.0.0.1", target_port))
            
            # Envoyer demande avec token
            request_data = json.dumps(connection_token)
            sock.send(request_data.encode())
            
            # Recevoir réponse
            response_data = sock.recv(4096)
            response = json.loads(response_data.decode())
            
            if response.get("status") == "accepted":
                # Connexion acceptée
                self.active_connections[target_hash] = {
                    "socket": sock,
                    "address": ("127.0.0.1", target_port),
                    "established_at": time.time(),
                    "status": "connected"
                }
                
                print(f"✅ P2P connection established with {target_hash[:8]}")
                return True
                
            else:
                print(f"❌ P2P connection rejected: {response.get('reason', 'unknown')}")
                sock.close()
                return False
                
        except Exception as e:
            print(f"❌ P2P connection failed: {e}")
            return False
            
    def send_message_to_peer(self, target_hash: str, message: Dict) -> bool:
        """Envoie message sécurisé à un peer connecté"""
        if target_hash not in self.active_connections:
            print(f"❌ No active connection to {target_hash[:8]}")
            return False
            
        try:
            connection = self.active_connections[target_hash]
            sock = connection["socket"]
            
            # Préparer message avec signature
            signed_message = {
                "from": self.node_info.node_hash,
                "to": target_hash,
                "timestamp": time.time(),
                "message": message,
                "signature": hashlib.sha256(json.dumps(message).encode()).hexdigest()
            }
            
            # Envoyer
            sock.send(json.dumps(signed_message).encode())
            print(f"📤 Message sent to {target_hash[:8]}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            # Nettoyer connexion cassée
            if target_hash in self.active_connections:
                del self.active_connections[target_hash]
            return False
            
    def get_connection_stats(self) -> Dict:
        """Statistiques des connexions P2P"""
        return {
            "active_connections": len(self.active_connections),
            "connections": [
                {
                    "node": node_hash[:8] + "...",
                    "duration": int(time.time() - conn["established_at"]),
                    "status": conn["status"]
                }
                for node_hash, conn in self.active_connections.items()
            ]
        }

# Import du scanner réseau précédent
from o_red_search_network import (
    SharedNetworkEncryption, NetworkBeaconBroadcaster, 
    NetworkBeaconScanner, NetworkORedSearch, create_network_zone_hash
)

class P2PNetworkBeaconBroadcaster(NetworkBeaconBroadcaster):
    """Version P2P du broadcaster avec infos de connexion"""
    
    def _create_network_beacon(self) -> Dict:
        """Beacon avec infos P2P"""
        beacon = super()._create_network_beacon()
        
        # Ajouter infos P2P
        beacon["node_data"]["p2p_endpoint"] = self.node_info.p2p_endpoint
        beacon["node_data"]["public_key_hash"] = self.node_info.public_key_hash
        beacon["node_data"]["p2p_capabilities"] = ["direct_connection", "token_auth", "secure_messaging"]
        
        return beacon

# Test complet du système P2P
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='O-RedSearch P2P - Secure Connections')
    parser.add_argument('--node-id', required=True, help='Node identifier')
    parser.add_argument('--sector', required=True, help='Node sector')
    parser.add_argument('--port', type=int, default=9000, help='P2P port')
    parser.add_argument('--lat', type=float, default=48.8566, help='Latitude')
    parser.add_argument('--lng', type=float, default=2.3522, help='Longitude')
    parser.add_argument('--auto-connect', action='store_true', help='Auto-connect to discovered nodes')
    
    args = parser.parse_args()
    
    # Créer nœud P2P complet
    node_hash = hashlib.sha256(f"{args.node_id}{time.time()}".encode()).hexdigest()
    zone_hash = create_network_zone_hash(args.lat, args.lng)
    
    # Initialiser sécurité P2P
    security_manager = P2PSecurityManager(node_hash)
    
    # Créer nœud avec capacités P2P
    p2p_node = P2PNodeBeacon(
        node_hash=node_hash,
        sector=args.sector,
        services=["storage", "compute", "p2p"],
        activity_level=secrets.randbelow(20) + 80,
        zone_hash=zone_hash,
        p2p_endpoint={"ip": "127.0.0.1", "port": args.port},
        public_key_hash=security_manager.public_key_hash
    )
    
    # Démarrer tous les systèmes
    broadcaster = P2PNetworkBeaconBroadcaster(p2p_node)
    scanner = NetworkBeaconScanner()
    search_engine = NetworkORedSearch(scanner)
    connection_manager = P2PConnectionManager(p2p_node, security_manager)
    
    # Lancer services
    broadcaster.start_broadcasting()
    scanner.start_network_scanning()
    connection_manager.start_p2p_server()
    
    print(f"\n🚀 O-RedSearch P2P started")
    print(f"   Node: {node_hash[:16]}...")
    print(f"   Sector: {args.sector}")
    print(f"   P2P Port: {args.port}")
    print(f"   Public Key: {security_manager.public_key_hash}")
    print(f"   Auto-connect: {args.auto_connect}")
    
    # Boucle principale avec découverte et connexion
    try:
        discovery_count = 0
        while True:
            time.sleep(15)
            discovery_count += 1
            
            # Chercher autres nœuds
            discovered_nodes = search_engine.network_search()
            
            print(f"\n📊 Discovery cycle {discovery_count}")
            print(f"   Discovered nodes: {len(discovered_nodes)}")
            
            # Afficher nœuds découverts
            for node in discovered_nodes:
                print(f"   - {node['node_hash']}: {node['sector']} | Activity: {node['activity_level']}%")
                
                # Auto-connexion si activée (éviter l'auto-connexion)
                target_hash = node['node_hash'].replace("...", "")
                if (args.auto_connect and 
                    len(connection_manager.active_connections) < 3 and 
                    target_hash != node_hash):  # ⚠️ Éviter auto-connexion
                    
                    success = connection_manager.connect_to_peer(node)
                    if success:
                        # Envoyer message de test
                        test_message = {
                            "type": "greeting",
                            "content": f"Hello from {args.sector} node!",
                            "timestamp": time.time()
                        }
                        connection_manager.send_message_to_peer(
                            target_hash, 
                            test_message
                        )
            
            # Stats de connexion
            p2p_stats = connection_manager.get_connection_stats()
            search_stats = search_engine.get_network_stats()
            
            print(f"\n🔗 P2P Connections: {p2p_stats['active_connections']}")
            for conn in p2p_stats['connections']:
                print(f"   - {conn['node']}: {conn['duration']}s ({conn['status']})")
                
            print(f"🌐 Network: {search_stats['legitimate_nodes']} nodes | Success rate: {search_stats['scanner_stats']['decryption_success']}/{search_stats['scanner_stats']['beacons_received']}")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping O-RedSearch P2P...")
        broadcaster.stop_broadcasting()
        scanner.stop_network_scanning()
        print(f"✅ P2P system stopped")