# === O-RedSearch P2P avec Architecture Sécurisée Intégrée ===
# Combinaison de la découverte UDP + votre protocole de sécurité

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

# Import de votre architecture de sécurité
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
    """Gestionnaire de connexions P2P avec votre architecture de sécurité"""
    
    def __init__(self, node_beacon: SecureP2PNodeBeacon, security_protocol: SimpleP2PSecurityProtocol):
        self.node_info = node_beacon
        self.active_connections = {}
        self.p2p_server_socket = None
        
        # Utiliser le protocole de sécurité fourni (même fingerprint cohérent)
        self.security_protocol = security_protocol
        
        print(f"🔐 Secure P2P initialized for {node_beacon.node_fingerprint}")
        print(f"   Fingerprint: {self.security_protocol.public_key_fingerprint}")
        
    def start_p2p_server(self):
        """Démarre serveur P2P avec votre architecture de sécurité"""
        def server_thread():
            try:
                self.p2p_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.p2p_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                port = self.node_info.p2p_endpoint["port"]
                self.p2p_server_socket.bind(("0.0.0.0", port))
                self.p2p_server_socket.listen(5)
                
                print(f"🔗 Secure P2P server started on port {port}")
                
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
        """Traite connexion P2P avec votre protocole de sécurité"""
        try:
            # Recevoir handshake de connexion
            data = client_sock.recv(4096)
            handshake_request = json.loads(data.decode())
            
            print(f"🔗 Secure P2P handshake from {addr[0]}")
            print(f"   Source: {handshake_request.get('source_fingerprint', 'unknown')[:8]}...")
            print(f"   Target: {handshake_request.get('target_fingerprint', 'unknown')[:8]}...")
            print(f"   Our fingerprint: {self.security_protocol.public_key_fingerprint[:8]}...")
            
            # Vérifier handshake avec votre protocole
            valid, response = self.security_protocol.verify_and_respond_handshake(handshake_request)
            
            if valid:
                # Handshake valide, accepter connexion
                print(f"✅ Handshake verified, connection accepted")
                
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
                print(f"❌ Handshake verification failed: {response.get('error', 'unknown')}")
                
            # Envoyer réponse
            client_sock.send(json.dumps(response).encode())
            
            if not valid:
                client_sock.close()
                
        except Exception as e:
            print(f"❌ Secure P2P connection handling error: {e}")
            client_sock.close()
            
    def connect_to_secure_peer(self, target_node: Dict) -> bool:
        """Connexion sécurisée avec votre protocole"""
        try:
            # Extraire fingerprint du nœud cible - UTILISER LE VRAI FINGERPRINT DU BEACON
            target_fingerprint = target_node.get("node_fingerprint")
            if not target_fingerprint:
                print(f"❌ No fingerprint for target node")
                return False
            
            # Éviter auto-connexion
            if target_fingerprint == self.security_protocol.public_key_fingerprint:
                print(f"🔄 Skipping self-connection")
                return True  # Pas d'erreur, juste skip
            
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
                
            print(f"🔗 Attempting secure connection to {target_fingerprint[:8]}...")
            print(f"🔗 Attempting secure connection to {target_fingerprint[:8]}... on port {target_port}")
            print(f"   Our fingerprint: {self.security_protocol.public_key_fingerprint[:8]}...")
            
            # Créer handshake avec votre protocole
            handshake = self.security_protocol.create_connection_handshake(target_fingerprint)
            print(f"   Handshake created for target: {handshake.get('target_fingerprint', 'unknown')[:8]}...")
            
            # Établir connexion TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect(("127.0.0.1", target_port))
            
            # Envoyer handshake
            sock.send(json.dumps(handshake).encode())
            
            # Recevoir réponse
            response_data = sock.recv(4096)
            response = json.loads(response_data.decode())
            
            print(f"   Response status: {response.get('status', 'unknown')}")
            
            # Finaliser connexion avec votre protocole
            connected, connection_token = self.security_protocol.finalize_connection(response, handshake)
            
            if connected:
                # Connexion établie avec succès !
                self.active_connections[target_fingerprint] = {
                    "socket": sock,
                    "address": ("127.0.0.1", target_port),
                    "established_at": time.time(),
                    "status": "connected",
                    "connection_token": connection_token
                }
                
                print(f"✅ Secure P2P connection established with {target_fingerprint[:8]}...")
                print(f"   Connection ID: {connection_token['connection_id']}")
                print(f"   Mutual Link: {connection_token['mutual_link'][:16]}...")
                return True
                
            else:
                print(f"❌ Connection finalization failed: {connection_token.get('error', 'unknown')}")
                sock.close()
                return False
                
        except Exception as e:
            print(f"❌ Secure P2P connection failed: {e}")
            return False
    
    def send_secure_message(self, target_fingerprint: str, message: Dict) -> bool:
        """Envoie message sécurisé via connexion P2P établie"""
        if target_fingerprint not in self.active_connections:
            print(f"❌ No active connection to {target_fingerprint[:8]}...")
            return False
            
        try:
            connection = self.active_connections[target_fingerprint]
            sock = connection["socket"]
            
            # Ajouter métadonnées de sécurité
            secure_message = {
                "type": "secure_p2p_message",
                "source_fingerprint": self.security_protocol.public_key_fingerprint,
                "target_fingerprint": target_fingerprint,
                "timestamp": time.time(),
                "mutual_link": connection.get("mutual_link"),
                "payload": message
            }
            
            sock.send(json.dumps(secure_message).encode())
            print(f"📤 Secure message sent to {target_fingerprint[:8]}...")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send secure message: {e}")
            return False
    
    def get_connection_stats(self) -> Dict:
        """Statistiques des connexions sécurisées"""
        active_count = len(self.active_connections)
        connections = []
        
        for fingerprint, conn in self.active_connections.items():
            duration = int(time.time() - conn["established_at"])
            connections.append({
                "fingerprint": fingerprint[:8] + "...",
                "duration": duration,
                "status": conn["status"],
                "mutual_link": conn.get("mutual_link", "")[:8] + "..."
            })
            
        return {
            "active_connections": active_count,
            "connections": connections
        }

# Intégration avec le système de beacons existant
class SecureP2PNetworkBeaconBroadcaster:
    """Broadcaster avec fingerprints pour sécurité"""
    
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
        """Démarre diffusion de beacons sécurisés"""
        def broadcast_thread():
            try:
                self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                self.is_running = True
                print(f"🌐 Secure beacon started (fingerprint: {self.node_beacon.node_fingerprint})")
                
                while self.is_running:
                    # Créer beacon avec fingerprint
                    beacon = self._create_secure_beacon()
                    
                    # Chiffrer beacon
                    fernet = Fernet(self.network_key)
                    encrypted_beacon = fernet.encrypt(json.dumps(beacon).encode())
                    
                    # Envoyer beacon
                    self.broadcast_socket.sendto(
                        encrypted_beacon,
                        (self.multicast_group, self.multicast_port)
                    )
                    
                    print(f"🌐 Secure beacon sent: {self.node_beacon.node_fingerprint[:8]}... ({self.node_beacon.sector})")
                    time.sleep(10)  # Beacon toutes les 10 secondes
                    
            except Exception as e:
                print(f"❌ Secure beacon error: {e}")
                
        threading.Thread(target=broadcast_thread, daemon=True).start()
    
    def _create_secure_beacon(self) -> Dict:
        """Crée beacon avec fingerprint cryptographique"""
        beacon = asdict(self.node_beacon)
        beacon["timestamp"] = time.time()
        beacon["beacon_type"] = "secure_p2p_discovery"
        beacon["protocol_version"] = "1.0"
        
        # Ajouter métadonnées de sécurité
        beacon["security"] = {
            "fingerprint": self.node_beacon.node_fingerprint,
            "hash_display": self.node_beacon.node_hash[:8] + "...",  # Pour compatibilité affichage
            "crypto_ready": True
        }
        
        return beacon
    
    def stop_broadcasting(self):
        """Arrête diffusion de beacons"""
        self.is_running = False
        if self.broadcast_socket:
            self.broadcast_socket.close()

class SecureP2PNetworkScanner:
    """Scanner réseau pour découverte de nœuds sécurisés"""
    
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
        """Démarre scan des beacons sécurisés"""
        def scanner_thread():
            try:
                self.scanner_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.scanner_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.scanner_socket.bind(('', self.multicast_port))
                
                # Rejoindre groupe multicast
                mreq = socket.inet_aton(self.multicast_group) + socket.inet_aton('0.0.0.0')
                self.scanner_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                
                self.is_scanning = True
                print(f"🔍 Secure network scanner started")
                
                while self.is_scanning:
                    try:
                        # Recevoir beacon
                        data, addr = self.scanner_socket.recvfrom(4096)
                        
                        # Déchiffrer beacon
                        fernet = Fernet(self.network_key)
                        decrypted_data = fernet.decrypt(data)
                        beacon = json.loads(decrypted_data.decode())
                        
                        # Traiter beacon sécurisé
                        if beacon.get("beacon_type") == "secure_p2p_discovery":
                            self._process_secure_beacon(beacon, addr)
                            
                    except Exception as e:
                        if self.is_scanning:  # Ignorer erreurs lors de l'arrêt
                            continue
                            
            except Exception as e:
                print(f"❌ Secure scanner error: {e}")
                
        threading.Thread(target=scanner_thread, daemon=True).start()
    
    def _process_secure_beacon(self, beacon: Dict, addr: Tuple[str, int]):
        """Traite beacon sécurisé découvert"""
        try:
            fingerprint = beacon.get("node_fingerprint")
            if not fingerprint:
                return
                
            # Mettre à jour nœud découvert
            self.discovered_nodes[fingerprint] = {
                "node_fingerprint": fingerprint,
                "node_hash": beacon.get("node_hash", ""),
                "sector": beacon.get("sector", "unknown"),
                "services": beacon.get("services", []),
                "activity_level": beacon.get("activity_level", 0),
                "p2p_endpoint": beacon.get("p2p_endpoint", {}),
                "last_seen": time.time(),
                "source_address": addr[0],
                "security": beacon.get("security", {})
            }
            
            print(f"✨ Secure node discovered: {fingerprint[:8]}... ({beacon.get('sector', 'unknown')})")
            
        except Exception as e:
            print(f"❌ Error processing secure beacon: {e}")
    
    def get_discovered_nodes(self) -> List[Dict]:
        """Retourne liste des nœuds sécurisés découverts"""
        current_time = time.time()
        active_nodes = []
        
        for fingerprint, node_data in self.discovered_nodes.items():
            # Nœuds vus dans les 60 dernières secondes
            if current_time - node_data["last_seen"] <= 60:
                active_nodes.append(node_data)
                
        return active_nodes
    
    def stop_scanning(self):
        """Arrête scan réseau"""
        self.is_scanning = False
        if self.scanner_socket:
            self.scanner_socket.close()

# Test du système sécurisé complet
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='O-RedSearch Secure P2P')
    parser.add_argument('--node-id', required=True, help='Node identifier')
    parser.add_argument('--sector', required=True, help='Node sector')
    parser.add_argument('--port', type=int, default=9000, help='P2P port')
    parser.add_argument('--auto-connect', action='store_true', help='Auto-connect to discovered nodes')
    
    args = parser.parse_args()
    
    # Créer nœud sécurisé
    node_hash = hashlib.sha256(f"{args.node_id}{time.time()}".encode()).hexdigest()
    
    # Initialiser protocole de sécurité
    security_protocol = SimpleP2PSecurityProtocol(args.node_id)
    
    # Créer beacon sécurisé avec le MÊME fingerprint que le protocole de sécurité
    secure_beacon = SecureP2PNodeBeacon(
        node_fingerprint=security_protocol.public_key_fingerprint,  # ⚠️ UTILISER LE MÊME FINGERPRINT
        node_hash=node_hash,
        sector=args.sector,
        services=["storage", "compute", "secure_p2p"],
        activity_level=secrets.randbelow(20) + 80,
        zone_hash="zone_" + hashlib.sha256(f"48.8566:2.3522".encode()).hexdigest()[:16],
        p2p_endpoint={"ip": "127.0.0.1", "port": args.port},
        timestamp=time.time()
    )
    
    # Démarrer tous les systèmes
    connection_manager = SecureP2PConnectionManager(secure_beacon, security_protocol)
    broadcaster = SecureP2PNetworkBeaconBroadcaster(secure_beacon)
    scanner = SecureP2PNetworkScanner()
    
    # Lancer services
    connection_manager.start_p2p_server()
    broadcaster.start_broadcasting()
    scanner.start_scanning()
    
    print(f"\n🚀 O-RedSearch Secure P2P started")
    print(f"   Fingerprint: {security_protocol.public_key_fingerprint}")
    print(f"   Sector: {args.sector}")
    print(f"   P2P Port: {args.port}")
    print(f"   Auto-connect: {args.auto_connect}")
    
    # Boucle principale avec découverte et connexion
    try:
        discovery_cycle = 0
        while True:
            time.sleep(15)
            discovery_cycle += 1
            
            # Découvrir nœuds sécurisés
            discovered_nodes = scanner.get_discovered_nodes()
            
            print(f"\n📊 Secure Discovery cycle {discovery_cycle}")
            print(f"   Discovered secure nodes: {len(discovered_nodes)}")
            
            # Afficher nœuds découverts
            for node in discovered_nodes:
                fingerprint = node['node_fingerprint']
                sector = node['sector']
                activity = node['activity_level']
                print(f"   - {fingerprint[:8]}...: {sector} | Activity: {activity}%")
                
                # Auto-connexion si activée
                if (args.auto_connect and 
                    len(connection_manager.active_connections) < 3 and 
                    fingerprint != security_protocol.public_key_fingerprint):
                    
                    # Éviter auto-connexion et connexions multiples
                    if fingerprint not in connection_manager.active_connections:
                        print(f"🔗 Attempting secure connection to {fingerprint[:8]}...")
                        success = connection_manager.connect_to_secure_peer(node)
                        
                        if success:
                            # Envoyer message de test sécurisé
                            test_message = {
                                "type": "secure_greeting",
                                "content": f"Hello from secure {args.sector} node!",
                                "timestamp": time.time(),
                                "security_level": "encrypted_p2p"
                            }
                            connection_manager.send_secure_message(fingerprint, test_message)
            
            # Stats de connexion sécurisées
            stats = connection_manager.get_connection_stats()
            print(f"\n🔗 Secure P2P Connections: {stats['active_connections']}")
            for conn in stats['connections']:
                print(f"   - {conn['fingerprint']}: {conn['duration']}s (Link: {conn['mutual_link']})")
            
            print(f"🌐 Secure Network: {len(discovered_nodes)} nodes discovered")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping Secure P2P...")
        broadcaster.stop_broadcasting()
        scanner.stop_scanning()
        print(f"✅ Secure P2P system stopped")