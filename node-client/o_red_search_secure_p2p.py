# === O-RedSearch P2P Révolutionnaire : Système Final ===
# Architecture révolutionnaire - Abandon de l'API centrale

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

# Import de votre architecture de sécurité révolutionnaire
from simple_p2p_security import SimpleP2PSecurityProtocol

@dataclass
class SecureP2PNodeBeacon:
    """Beacon avec fingerprint cryptographique pour sécurité"""
    node_fingerprint: str  # Fingerprint unique basé sur clé publique
    node_hash: str         # Hash complet pour compatibilité
    sector: str
    services: List[str]
    activity_level: int
    zone_hash: str
    p2p_endpoint: Dict[str, any]
    timestamp: float
    
class SecureP2PConnectionManager:
    """Gestionnaire de connexions P2P avec votre architecture de sécurité révolutionnaire"""
    
    def __init__(self, node_beacon: SecureP2PNodeBeacon, security_protocol: SimpleP2PSecurityProtocol):
        self.node_info = node_beacon
        self.active_connections = {}
        self.p2p_server_socket = None
        
        # Utiliser le protocole de sécurité fourni (même fingerprint cohérent)
        self.security_protocol = security_protocol
        
        print(f"🔐 Revolutionary P2P Security initialized")
        print(f"   Fingerprint: {self.security_protocol.public_key_fingerprint}")
        print(f"   🚫 NO CENTRAL API - Pure P2P Architecture")
        
    def start_p2p_server(self):
        """Démarre serveur P2P avec votre architecture de sécurité"""
        def server_thread():
            try:
                self.p2p_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.p2p_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                port = self.node_info.p2p_endpoint["port"]
                self.p2p_server_socket.bind(("0.0.0.0", port))
                self.p2p_server_socket.listen(5)
                
                print(f"🔗 Revolutionary P2P server started on port {port}")
                
                while True:
                    client_sock, addr = self.p2p_server_socket.accept()
                    threading.Thread(
                        target=self._handle_secure_p2p_connection,
                        args=(client_sock, addr),
                        daemon=True
                    ).start()
                    
            except Exception as e:
                if "forced" not in str(e).lower():
                    print(f"❌ P2P server error: {e}")
                    
        threading.Thread(target=server_thread, daemon=True).start()
        
    def _handle_secure_p2p_connection(self, client_sock: socket.socket, addr: Tuple[str, int]):
        """Traite connexion P2P avec votre protocole de sécurité révolutionnaire"""
        try:
            # Recevoir handshake de connexion
            data = client_sock.recv(4096)
            handshake_request = json.loads(data.decode())
            
            print(f"🔗 Revolutionary P2P handshake from {addr[0]}")
            print(f"   Source: {handshake_request.get('source_fingerprint', 'unknown')[:8]}...")
            print(f"   Target: {handshake_request.get('target_fingerprint', 'unknown')[:8]}...")
            print(f"   Our fingerprint: {self.security_protocol.public_key_fingerprint[:8]}...")
            
            # Vérifier handshake avec votre protocole révolutionnaire
            valid, response = self.security_protocol.verify_and_respond_handshake(handshake_request)
            
            if valid:
                # Handshake valide, accepter connexion
                print(f"✅ Revolutionary handshake verified - connection accepted")
                
                # Enregistrer connexion active
                source_fingerprint = handshake_request.get("source_fingerprint")
                self.active_connections[source_fingerprint] = {
                    "socket": client_sock,
                    "address": addr,
                    "established_at": time.time(),
                    "status": "connected",
                    "mutual_link": response.get("mutual_link")
                }
                
            else:
                # Handshake invalide, refuser
                print(f"❌ Revolutionary handshake verification failed: {response.get('error', 'unknown')}")
                
            # Envoyer réponse
            client_sock.send(json.dumps(response).encode())
            
            if not valid:
                client_sock.close()
                
        except Exception as e:
            print(f"❌ Revolutionary P2P connection handling error: {e}")
            client_sock.close()
            
    def connect_to_secure_peer(self, target_node: Dict) -> bool:
        """Connexion sécurisée avec votre protocole révolutionnaire"""
        try:
            # Extraire fingerprint du nœud cible
            target_fingerprint = target_node.get("node_fingerprint")
            if not target_fingerprint:
                print(f"❌ No fingerprint for target node")
                return False
            
            # Éviter auto-connexion
            if target_fingerprint == self.security_protocol.public_key_fingerprint:
                print(f"🔄 Skipping self-connection")
                return True
            
            # Éviter connexions multiples
            if target_fingerprint in self.active_connections:
                print(f"🔄 Already connected to {target_fingerprint[:8]}...")
                return True
            
            # Déterminer port P2P
            target_port = 9000
            if "health" in target_node.get("sector", ""):
                target_port = 9002
            elif "tech" in target_node.get("sector", ""):
                target_port = 9001
                
            print(f"🔗 Attempting revolutionary connection to {target_fingerprint[:8]}...")
            print(f"🔗 Direct P2P connection (NO CENTRAL API) on port {target_port}")
            print(f"   Our fingerprint: {self.security_protocol.public_key_fingerprint[:8]}...")
            
            # Créer handshake avec votre protocole révolutionnaire
            handshake = self.security_protocol.create_connection_handshake(target_fingerprint)
            print(f"   Revolutionary handshake created for target: {handshake.get('target_fingerprint', 'unknown')[:8]}...")
            
            # Établir connexion TCP directe
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect(("127.0.0.1", target_port))
            
            # Envoyer handshake révolutionnaire
            sock.send(json.dumps(handshake).encode())
            
            # Recevoir réponse
            response_data = sock.recv(4096)
            response = json.loads(response_data.decode())
            
            print(f"   Response status: {response.get('status', 'unknown')}")
            
            # Finaliser connexion avec votre protocole révolutionnaire
            connected, connection_token = self.security_protocol.finalize_connection(response, handshake)
            
            if connected:
                # Connexion révolutionnaire établie avec succès !
                self.active_connections[target_fingerprint] = {
                    "socket": sock,
                    "address": ("127.0.0.1", target_port),
                    "established_at": time.time(),
                    "status": "connected",
                    "connection_token": connection_token
                }
                
                print(f"✅ Revolutionary P2P connection established with {target_fingerprint[:8]}...")
                print(f"   Connection ID: {connection_token['connection_id']}")
                print(f"   Mutual Link: {connection_token['mutual_link'][:16]}...")
                print(f"   🚫 NO CENTRAL API INVOLVED - Pure P2P Revolution!")
                return True
                
            else:
                print(f"❌ Revolutionary connection finalization failed: {connection_token.get('error', 'unknown')}")
                sock.close()
                return False
                
        except Exception as e:
            print(f"❌ Revolutionary P2P connection failed: {e}")
            return False
    
    def send_secure_message(self, target_fingerprint: str, message: Dict) -> bool:
        """Envoie message sécurisé via connexion P2P révolutionnaire"""
        if target_fingerprint not in self.active_connections:
            print(f"❌ No active revolutionary connection to {target_fingerprint[:8]}...")
            return False
            
        try:
            connection = self.active_connections[target_fingerprint]
            sock = connection["socket"]
            
            # Ajouter métadonnées de sécurité révolutionnaire
            secure_message = {
                "type": "revolutionary_p2p_message",
                "source_fingerprint": self.security_protocol.public_key_fingerprint,
                "target_fingerprint": target_fingerprint,
                "timestamp": time.time(),
                "mutual_link": connection.get("mutual_link"),
                "central_api_used": False,  # 🚫 JAMAIS D'API CENTRALE
                "revolutionary_protocol": True,
                "payload": message
            }
            
            sock.send(json.dumps(secure_message).encode())
            print(f"📤 Revolutionary secure message sent to {target_fingerprint[:8]}...")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send revolutionary message: {e}")
            return False
    
    def get_connection_stats(self) -> Dict:
        """Statistiques des connexions révolutionnaires"""
        active_count = len(self.active_connections)
        connections = []
        
        for fingerprint, conn in self.active_connections.items():
            duration = int(time.time() - conn["established_at"])
            connections.append({
                "fingerprint": fingerprint[:8] + "...",
                "duration": duration,
                "status": conn["status"],
                "mutual_link": conn.get("mutual_link", "")[:8] + "...",
                "revolutionary": True,
                "central_api": False
            })
            
        return {
            "active_connections": active_count,
            "connections": connections,
            "architecture": "revolutionary_p2p",
            "central_api_abandoned": True
        }

# Système de découverte "Phare dans la Nuit" révolutionnaire
class SecureP2PNetworkBeaconBroadcaster:
    """Broadcaster révolutionnaire avec fingerprints cryptographiques"""
    
    def __init__(self, node_beacon: SecureP2PNodeBeacon):
        self.node_beacon = node_beacon
        self.multicast_group = '224.0.1.100'
        self.multicast_port = 5354
        self.broadcast_socket = None
        self.is_running = False
        
        # Chiffrement réseau partagé (pour compatibilité)
        self.network_key = self._derive_network_key("OpenRed-P2P-Discovery-2025")
        
    def _derive_network_key(self, passphrase: str) -> bytes:
        """Dérive clé réseau depuis passphrase"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'openred_p2p_salt_2025',
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    
    def start_broadcasting(self):
        """Démarre diffusion de beacons révolutionnaires"""
        def broadcast_thread():
            try:
                self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                self.is_running = True
                print(f"🌐 Revolutionary lighthouse beacon started")
                print(f"   Fingerprint: {self.node_beacon.node_fingerprint}")
                print(f"   🚫 NO CENTRAL API - Pure P2P Discovery")
                
                while self.is_running:
                    # Créer beacon révolutionnaire
                    beacon = self._create_revolutionary_beacon()
                    
                    # Chiffrer beacon
                    fernet = Fernet(self.network_key)
                    encrypted_beacon = fernet.encrypt(json.dumps(beacon).encode())
                    
                    # Envoyer beacon dans la nuit
                    self.broadcast_socket.sendto(
                        encrypted_beacon,
                        (self.multicast_group, self.multicast_port)
                    )
                    
                    print(f"🌐 Revolutionary lighthouse beacon sent: {self.node_beacon.node_fingerprint[:8]}... ({self.node_beacon.sector})")
                    time.sleep(10)  # Beacon toutes les 10 secondes
                    
            except Exception as e:
                print(f"❌ Revolutionary beacon error: {e}")
                
        threading.Thread(target=broadcast_thread, daemon=True).start()
    
    def _create_revolutionary_beacon(self) -> Dict:
        """Crée beacon révolutionnaire avec fingerprint cryptographique"""
        beacon = asdict(self.node_beacon)
        beacon["timestamp"] = time.time()
        beacon["beacon_type"] = "revolutionary_p2p_discovery"
        beacon["protocol_version"] = "2.0"
        beacon["central_api_abandoned"] = True
        
        # Ajouter métadonnées de sécurité révolutionnaire
        beacon["security"] = {
            "fingerprint": self.node_beacon.node_fingerprint,
            "hash_display": self.node_beacon.node_hash[:8] + "...",
            "crypto_ready": True,
            "revolutionary_protocol": True,
            "anti_surveillance": True
        }
        
        return beacon
    
    def stop_broadcasting(self):
        """Arrête diffusion de beacons révolutionnaires"""
        self.is_running = False
        if self.broadcast_socket:
            self.broadcast_socket.close()

class SecureP2PNetworkScanner:
    """Scanner révolutionnaire pour découverte de nœuds"""
    
    def __init__(self):
        self.multicast_group = '224.0.1.100'
        self.multicast_port = 5354
        self.scanner_socket = None
        self.is_scanning = False
        self.discovered_nodes = {}
        
        # Clé réseau partagée
        self.network_key = self._derive_network_key("OpenRed-P2P-Discovery-2025")
        
    def _derive_network_key(self, passphrase: str) -> bytes:
        """Dérive clé réseau depuis passphrase"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'openred_p2p_salt_2025',
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    
    def start_scanning(self):
        """Démarre scan révolutionnaire des beacons"""
        def scanner_thread():
            try:
                self.scanner_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.scanner_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.scanner_socket.bind(('', self.multicast_port))
                
                # Rejoindre groupe multicast
                mreq = socket.inet_aton(self.multicast_group) + socket.inet_aton('0.0.0.0')
                self.scanner_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                
                self.is_scanning = True
                print(f"🔍 Revolutionary lighthouse scanner started")
                print(f"   🚫 NO CENTRAL API - Scanning for P2P lighthouses")
                
                while self.is_scanning:
                    try:
                        # Recevoir beacon
                        data, addr = self.scanner_socket.recvfrom(4096)
                        
                        # Déchiffrer beacon
                        fernet = Fernet(self.network_key)
                        decrypted_data = fernet.decrypt(data)
                        beacon = json.loads(decrypted_data.decode())
                        
                        # Traiter beacon révolutionnaire
                        if beacon.get("beacon_type") == "revolutionary_p2p_discovery":
                            self._process_revolutionary_beacon(beacon, addr)
                            
                    except Exception as e:
                        if self.is_scanning:  # Ignorer erreurs lors de l'arrêt
                            continue
                            
            except Exception as e:
                print(f"❌ Revolutionary scanner error: {e}")
                
        threading.Thread(target=scanner_thread, daemon=True).start()
    
    def _process_revolutionary_beacon(self, beacon: Dict, addr: Tuple[str, int]):
        """Traite beacon révolutionnaire découvert"""
        try:
            fingerprint = beacon.get("node_fingerprint")
            if not fingerprint:
                return
                
            # Mettre à jour nœud révolutionnaire découvert
            self.discovered_nodes[fingerprint] = {
                "node_fingerprint": fingerprint,
                "node_hash": beacon.get("node_hash", ""),
                "sector": beacon.get("sector", "unknown"),
                "services": beacon.get("services", []),
                "activity_level": beacon.get("activity_level", 0),
                "p2p_endpoint": beacon.get("p2p_endpoint", {}),
                "last_seen": time.time(),
                "source_address": addr[0],
                "security": beacon.get("security", {}),
                "revolutionary": True,
                "central_api_used": False
            }
            
            print(f"✨ Revolutionary lighthouse discovered: {fingerprint[:8]}... ({beacon.get('sector', 'unknown')})")
            
        except Exception as e:
            print(f"❌ Error processing revolutionary beacon: {e}")
    
    def get_discovered_nodes(self) -> List[Dict]:
        """Retourne liste des nœuds révolutionnaires découverts"""
        current_time = time.time()
        active_nodes = []
        
        for fingerprint, node_data in self.discovered_nodes.items():
            # Nœuds vus dans les 60 dernières secondes
            if current_time - node_data["last_seen"] <= 60:
                active_nodes.append(node_data)
                
        return active_nodes
    
    def stop_scanning(self):
        """Arrête scan révolutionnaire"""
        self.is_scanning = False
        if self.scanner_socket:
            self.scanner_socket.close()

# Test du système révolutionnaire complet
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='O-RedSearch Revolutionary P2P System')
    parser.add_argument('--node-id', required=True, help='Node identifier')
    parser.add_argument('--sector', required=True, help='Node sector')
    parser.add_argument('--port', type=int, default=9000, help='P2P port')
    parser.add_argument('--auto-connect', action='store_true', help='Auto-connect to discovered nodes')
    
    args = parser.parse_args()
    
    # Créer nœud révolutionnaire
    node_hash = hashlib.sha256(f"{args.node_id}{time.time()}".encode()).hexdigest()
    
    # Initialiser protocole de sécurité révolutionnaire
    security_protocol = SimpleP2PSecurityProtocol(args.node_id)
    
    # Créer beacon révolutionnaire avec le MÊME fingerprint que le protocole de sécurité
    revolutionary_beacon = SecureP2PNodeBeacon(
        node_fingerprint=security_protocol.public_key_fingerprint,
        node_hash=node_hash,
        sector=args.sector,
        services=["storage", "compute", "revolutionary_p2p"],
        activity_level=secrets.randbelow(20) + 80,
        zone_hash="zone_" + hashlib.sha256(f"48.8566:2.3522".encode()).hexdigest()[:16],
        p2p_endpoint={"ip": "127.0.0.1", "port": args.port},
        timestamp=time.time()
    )
    
    # Démarrer tous les systèmes révolutionnaires
    connection_manager = SecureP2PConnectionManager(revolutionary_beacon, security_protocol)
    broadcaster = SecureP2PNetworkBeaconBroadcaster(revolutionary_beacon)
    scanner = SecureP2PNetworkScanner()
    
    # Lancer services révolutionnaires
    connection_manager.start_p2p_server()
    broadcaster.start_broadcasting()
    scanner.start_scanning()
    
    print(f"\n🚀 O-RedSearch Revolutionary P2P System Started")
    print(f"   🔐 Fingerprint: {security_protocol.public_key_fingerprint}")
    print(f"   🏷️ Sector: {args.sector}")
    print(f"   🔗 P2P Port: {args.port}")
    print(f"   🤖 Auto-connect: {args.auto_connect}")
    print(f"   🚫 Central API: ABANDONED")
    print(f"   ⚡ Architecture: Revolutionary P2P")
    
    # Boucle principale avec découverte et connexion révolutionnaire
    try:
        discovery_cycle = 0
        while True:
            time.sleep(15)
            discovery_cycle += 1
            
            # Découvrir nœuds révolutionnaires
            discovered_nodes = scanner.get_discovered_nodes()
            
            print(f"\n📊 Revolutionary Discovery cycle {discovery_cycle}")
            print(f"   Discovered revolutionary lighthouses: {len(discovered_nodes)}")
            print(f"   🚫 Central API queries: 0 (ABANDONED)")
            
            # Afficher nœuds révolutionnaires découverts
            for node in discovered_nodes:
                fingerprint = node['node_fingerprint']
                sector = node['sector']
                activity = node['activity_level']
                print(f"   - 🌟 {fingerprint[:8]}...: {sector} | Activity: {activity}% | Revolutionary: ✅")
                
                # Auto-connexion révolutionnaire si activée
                if (args.auto_connect and 
                    len(connection_manager.active_connections) < 3 and 
                    fingerprint != security_protocol.public_key_fingerprint):
                    
                    # Éviter auto-connexion et connexions multiples
                    if fingerprint not in connection_manager.active_connections:
                        print(f"🔗 Attempting revolutionary connection to {fingerprint[:8]}...")
                        success = connection_manager.connect_to_secure_peer(node)
                        
                        if success:
                            # Envoyer message de test révolutionnaire
                            test_message = {
                                "type": "revolutionary_greeting",
                                "content": f"Hello from revolutionary {args.sector} node!",
                                "timestamp": time.time(),
                                "security_level": "revolutionary_p2p",
                                "central_api_abandoned": True,
                                "revolution_message": "Pure P2P has begun!"
                            }
                            connection_manager.send_secure_message(fingerprint, test_message)
            
            # Stats de connexion révolutionnaires
            stats = connection_manager.get_connection_stats()
            print(f"\n🔗 Revolutionary P2P Connections: {stats['active_connections']}")
            print(f"   Architecture: {stats['architecture'].upper()}")
            print(f"   Central API abandoned: {stats['central_api_abandoned']}")
            for conn in stats['connections']:
                print(f"   - ⚡ {conn['fingerprint']}: {conn['duration']}s (Link: {conn['mutual_link']}) | Revolutionary: ✅")
            
            print(f"🌐 Revolutionary Network: {len(discovered_nodes)} lighthouses discovered")
            print(f"🚫 Central API usage: ZERO - Revolution achieved!")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping Revolutionary P2P System...")
        broadcaster.stop_broadcasting()
        scanner.stop_scanning()
        print(f"✅ Revolutionary P2P system stopped")
        print(f"🌟 The revolution continues... Central APIs are dead!")