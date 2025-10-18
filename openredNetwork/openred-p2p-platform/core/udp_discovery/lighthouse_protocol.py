# === OpenRed P2P Platform : Système "Phare dans la Nuit" Révolutionnaire ===
# Architecture 100% P2P Pure - Aucune API Centrale !
# Découverte UDP Multicast avec Sécurité Cryptographique Avancée

import socket
import json
import threading
import time
import hashlib
import secrets
import struct
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
import os

@dataclass
class P2PNodeBeacon:
    """Beacon cryptographique pour découverte P2P "phare dans la nuit" """
    fingerprint: str            # Fingerprint RSA unique du nœud
    node_id: str               # Identifiant unique du nœud
    sector: str                # Secteur d'activité (tech, health, general...)
    services: List[str]        # Services disponibles
    capabilities: Dict         # Capacités du nœud
    p2p_endpoint: Dict         # Point de connexion P2P
    network_zone: str          # Zone réseau (local, vpn, global...)
    activity_level: int        # Niveau d'activité (0-100)
    signature: str             # Signature RSA du beacon
    timestamp: float           # Horodatage anti-replay
    urn_phantom_support: bool  # Support URN/Phantom avec Schrödinger Phoenix
    discovery_info: Optional[Dict] = None  # Informations de profil pour découverte (optionnel)
    
class LighthouseProtocol:
    """
    Protocole révolutionnaire "Phare dans la Nuit"
    Découverte P2P pure via UDP Multicast avec sécurité cryptographique
    """
    
    # Configuration révolutionnaire OpenRed - Compatible Windows
    MULTICAST_GROUP = "239.255.255.250"  # UPnP multicast (plus compatible Windows)
    MULTICAST_PORT = 5354                 # Port découverte standard
    BEACON_INTERVAL = 30                  # Intervalle beacon (secondes)
    DISCOVERY_TIMEOUT = 60                # Timeout découverte
    
    def __init__(self, node_id: str, private_key, public_key, sector: str = "general", profile_manager=None):
        self.node_id = node_id
        self.sector = sector
        self.private_key = private_key
        self.public_key = public_key
        self.profile_manager = profile_manager  # Gestionnaire de profil utilisateur
        
        # Calcul fingerprint unique RSA
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.fingerprint = hashlib.sha256(public_pem).hexdigest()[:16]
        
        # État du protocole
        self.discovered_nodes = {}      # Nœuds découverts
        self.active_connections = {}    # Connexions P2P actives
        self.beacon_thread = None       # Thread diffusion beacon
        self.listener_thread = None     # Thread écoute réseau
        self.running = False
        
        # Callbacks pour événements réseau
        self.on_node_discovered: Optional[Callable] = None
        self.on_node_lost: Optional[Callable] = None
        self.on_connection_established: Optional[Callable] = None
        
        print(f"🌟 Lighthouse Protocol initialized")
        print(f"   Node ID: {self.node_id}")
        print(f"   Fingerprint: {self.fingerprint}")
        print(f"   Sector: {self.sector}")
        print(f"   🚫 NO CENTRAL API - Pure P2P Discovery!")
        
    def generate_beacon(self, p2p_port: int, services: List[str] = None) -> P2PNodeBeacon:
        """Génère beacon cryptographique signé avec informations de profil"""
        if services is None:
            services = ["urn_phantom", "messaging", "file_sharing"]
        
        # Récupérer les informations de profil si disponibles
        discovery_info = {}
        if self.profile_manager:
            discovery_info = self.profile_manager.get_discovery_info()
            
        beacon = P2PNodeBeacon(
            fingerprint=self.fingerprint,
            node_id=self.node_id,
            sector=self.sector,
            services=services,
            capabilities={
                "phantom_urn_system": True,
                "schrodinger_phoenix": True,
                "urn_support": True,
                "phantom_support": True,
                "p2p_direct": True
            },
            p2p_endpoint={
                "port": p2p_port,
                "protocol": "tcp"
            },
            network_zone="auto",
            activity_level=100,
            signature="",  # Sera calculé
            timestamp=time.time(),
            urn_phantom_support=True,  # Support système Phantom URN complet
            discovery_info=discovery_info  # Informations de profil
        )
        
        # Signature RSA du beacon
        beacon_data = {
            "fingerprint": beacon.fingerprint,
            "node_id": beacon.node_id,
            "sector": beacon.sector,
            "services": beacon.services,
            "timestamp": beacon.timestamp
        }
        
        beacon_json = json.dumps(beacon_data, sort_keys=True)
        signature = self.private_key.sign(
            beacon_json.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        beacon.signature = base64.b64encode(signature).decode()
        return beacon
        
    def verify_beacon_signature(self, beacon: P2PNodeBeacon, sender_public_key) -> bool:
        """Vérifie la signature RSA d'un beacon"""
        try:
            # Reconstruction des données signées
            beacon_data = {
                "fingerprint": beacon.fingerprint,
                "node_id": beacon.node_id,
                "sector": beacon.sector,
                "services": beacon.services,
                "timestamp": beacon.timestamp
            }
            
            beacon_json = json.dumps(beacon_data, sort_keys=True)
            signature = base64.b64decode(beacon.signature)
            
            # Vérification signature
            sender_public_key.verify(
                signature,
                beacon_json.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
            
        except Exception as e:
            print(f"❌ Beacon signature verification failed: {e}")
            return False
            
    def start_lighthouse(self, p2p_port: int):
        """Démarre le système phare dans la nuit"""
        print(f"🌟 Starting Lighthouse Protocol...")
        print(f"   Multicast: {self.MULTICAST_GROUP}:{self.MULTICAST_PORT}")
        print(f"   P2P Port: {p2p_port}")
        
        self.running = True
        
        # Démarrage thread diffusion beacon
        self.beacon_thread = threading.Thread(
            target=self._beacon_broadcaster,
            args=(p2p_port,),
            daemon=True
        )
        self.beacon_thread.start()
        
        # Démarrage thread écoute réseau
        self.listener_thread = threading.Thread(
            target=self._network_listener,
            daemon=True
        )
        self.listener_thread.start()
        
        print(f"✅ Lighthouse Protocol active - Broadcasting beacon every {self.BEACON_INTERVAL}s")
        
    def stop_lighthouse(self):
        """Arrête le système phare"""
        print("🛑 Stopping Lighthouse Protocol...")
        self.running = False
        
    def _beacon_broadcaster(self, p2p_port: int):
        """Thread de diffusion beacon UDP multicast"""
        # Configuration socket UDP multicast
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Configuration multicast avec interface spécifique pour Windows
        ttl = struct.pack('b', 2)  # TTL pour réseau local/VPN
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        
        # Définir l'interface pour multicast
        try:
            # Essayer avec l'interface locale
            local_ip = socket.gethostbyname(socket.gethostname())
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local_ip))
            print(f"📡 Multicast broadcaster using interface: {local_ip}")
        except Exception as e:
            try:
                # Fallback: interface localhost
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton("127.0.0.1"))
                print(f"📡 Multicast broadcaster using localhost interface")
            except Exception as e2:
                print(f"⚠️ Could not set multicast interface: {e}, {e2}")
        
        try:
            while self.running:
                # Génération beacon signé
                beacon = self.generate_beacon(p2p_port)
                beacon_json = json.dumps(asdict(beacon))
                
                try:
                    # Diffusion UDP multicast
                    sock.sendto(
                        beacon_json.encode('utf-8'),
                        (self.MULTICAST_GROUP, self.MULTICAST_PORT)
                    )
                    print(f"📡 Beacon broadcasted - Fingerprint: {self.fingerprint}")
                except Exception as send_error:
                    print(f"❌ Failed to send beacon: {send_error}")
                    # Essayer en broadcast local comme fallback
                    try:
                        sock.sendto(
                            beacon_json.encode('utf-8'),
                            ('255.255.255.255', self.MULTICAST_PORT)
                        )
                        print(f"📡 Beacon sent via broadcast fallback")
                    except Exception as broadcast_error:
                        print(f"❌ Broadcast fallback also failed: {broadcast_error}")
                
                time.sleep(self.BEACON_INTERVAL)
                
        except Exception as e:
            print(f"❌ Beacon broadcaster error: {e}")
        finally:
            sock.close()
            
    def _network_listener(self):
        """Thread d'écoute réseau pour découverte nœuds"""
        # Configuration socket écoute multicast
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Binding sur toutes interfaces
        sock.bind(('', self.MULTICAST_PORT))
        
        # Rejoindre groupe multicast avec interface spécifique pour Windows
        try:
            # Essayer d'abord avec l'interface locale
            local_ip = socket.gethostbyname(socket.gethostname())
            mreq = struct.pack("4s4s", socket.inet_aton(self.MULTICAST_GROUP), socket.inet_aton(local_ip))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            print(f"📡 Multicast joined using interface: {local_ip}")
        except Exception as e:
            try:
                # Fallback: essayer avec INADDR_ANY
                mreq = struct.pack("4sl", socket.inet_aton(self.MULTICAST_GROUP), socket.INADDR_ANY)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                print(f"📡 Multicast joined using INADDR_ANY")
            except Exception as e2:
                try:
                    # Dernière tentative: interface localhost
                    mreq = struct.pack("4s4s", socket.inet_aton(self.MULTICAST_GROUP), socket.inet_aton("127.0.0.1"))
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                    print(f"📡 Multicast joined using localhost")
                except Exception as e3:
                    print(f"❌ Failed to join multicast group: {e}, {e2}, {e3}")
                    sock.close()
                    return
        
        try:
            while self.running:
                try:
                    # Ajouter timeout pour debug
                    sock.settimeout(1.0)
                    data, addr = sock.recvfrom(4096)
                    print(f"📡 DEBUG: Received UDP data from {addr}: {len(data)} bytes")
                    self._process_discovered_beacon(data.decode('utf-8'), addr[0])
                    
                except socket.timeout:
                    # Timeout normal, continue
                    continue
                except Exception as e:
                    if self.running:  # Ignore errors when stopping
                        print(f"⚠️ Network listener error: {e}")
                        
        except Exception as e:
            print(f"❌ Network listener failed: {e}")
        finally:
            sock.close()
            
    def _process_discovered_beacon(self, beacon_data: str, sender_ip: str):
        """Traite un beacon découvert"""
        try:
            beacon_dict = json.loads(beacon_data)
            
            # Support rétrocompatibilité : ajouter discovery_info si manquant
            if 'discovery_info' not in beacon_dict:
                beacon_dict['discovery_info'] = None
            
            beacon = P2PNodeBeacon(**beacon_dict)
            
            # Ignorer notre propre beacon
            if beacon.fingerprint == self.fingerprint:
                return
                
            # Vérifier âge du beacon (anti-replay)
            if time.time() - beacon.timestamp > 120:  # 2 minutes max
                return
                
            print(f"🔍 Discovered node: {beacon.node_id} ({beacon.fingerprint[:8]}...)")
            print(f"   IP: {sender_ip}")
            print(f"   Sector: {beacon.sector}")
            print(f"   Services: {beacon.services}")
            print(f"   URN/Phantom System: {beacon.urn_phantom_support}")
            
            # Afficher info profil si disponible
            if beacon.discovery_info:
                profile_info = beacon.discovery_info
                print(f"   👤 Profil: {profile_info.get('display_name', 'N/A')}")
                if profile_info.get('profession'):
                    print(f"   💼 Profession: {profile_info.get('profession')}")
                if profile_info.get('location'):
                    print(f"   📍 Localisation: {profile_info.get('location')}")
                if profile_info.get('profile_picture'):
                    print(f"   📷 Photo de profil disponible")
            
            # Ajouter/mettre à jour nœud découvert
            node_info = {
                "beacon": beacon,
                "ip": sender_ip,
                "last_seen": time.time(),
                "connection_attempts": 0
            }
            
            is_new_node = beacon.fingerprint not in self.discovered_nodes
            self.discovered_nodes[beacon.fingerprint] = node_info
            
            # Callback nouveau nœud
            if is_new_node and self.on_node_discovered:
                self.on_node_discovered(beacon, sender_ip)
                
        except Exception as e:
            print(f"⚠️ Error processing beacon: {e}")
            
    def get_discovered_nodes(self) -> Dict:
        """Retourne les nœuds découverts actifs"""
        current_time = time.time()
        active_nodes = {}
        
        for fingerprint, node_info in self.discovered_nodes.items():
            # Nœud actif si vu dans les 3 dernières minutes
            if current_time - node_info["last_seen"] < 180:
                active_nodes[fingerprint] = node_info
                
        return active_nodes
        
    def initiate_p2p_connection(self, target_fingerprint: str) -> bool:
        """Initie une connexion P2P directe avec un nœud"""
        if target_fingerprint not in self.discovered_nodes:
            print(f"❌ Node {target_fingerprint} not found in discovered nodes")
            return False
            
        node_info = self.discovered_nodes[target_fingerprint]
        beacon = node_info["beacon"]
        target_ip = node_info["ip"]
        target_port = beacon.p2p_endpoint["port"]
        
        print(f"🤝 Initiating P2P connection to {beacon.node_id}")
        print(f"   Target: {target_ip}:{target_port}")
        
        try:
            # Connexion TCP directe
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((target_ip, target_port))
            
            # Handshake P2P sécurisé
            handshake = {
                "source_fingerprint": self.fingerprint,
                "target_fingerprint": target_fingerprint,
                "node_id": self.node_id,
                "timestamp": time.time(),
                "protocol_version": "1.0"
            }
            
            sock.send(json.dumps(handshake).encode())
            
            # Attendre réponse
            response = sock.recv(4096)
            response_data = json.loads(response.decode())
            
            if response_data.get("status") == "accepted":
                print(f"✅ P2P connection established with {beacon.node_id}")
                
                # Enregistrer connexion active
                self.active_connections[target_fingerprint] = {
                    "socket": sock,
                    "node_info": node_info,
                    "established_at": time.time()
                }
                
                if self.on_connection_established:
                    self.on_connection_established(target_fingerprint, sock)
                    
                return True
            else:
                print(f"❌ P2P connection rejected: {response_data.get('reason', 'unknown')}")
                sock.close()
                return False
                
        except Exception as e:
            print(f"❌ P2P connection failed: {e}")
            return False
            
    def get_network_stats(self) -> Dict:
        """Statistiques du réseau P2P"""
        active_nodes = self.get_discovered_nodes()
        
        return {
            "lighthouse_active": self.running,
            "own_fingerprint": self.fingerprint,
            "discovered_nodes": len(active_nodes),
            "active_connections": len(self.active_connections),
            "sectors_discovered": list(set(
                node["beacon"].sector for node in active_nodes.values()
            )),
            "urn_phantom_nodes": len([
                node for node in active_nodes.values()
                if node["beacon"].urn_phantom_support
            ])
        }