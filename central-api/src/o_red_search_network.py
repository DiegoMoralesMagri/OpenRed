#!/usr/bin/env python3
"""
O-RedSearch Pure avec Clé Réseau Partagée
Permet la découverte mutuelle entre nœuds légitimes
"""

import socket
import json
import threading
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

# Clé réseau partagée pour O-RedSearch (changeable)
ORED_NETWORK_PASSPHRASE = "OpenRed-Pure-Discovery-2025"

@dataclass
class SecureNodeBeacon:
    """Structure sécurisée - métadonnées minimales"""
    node_hash: str          
    sector: str            
    services: List[str]    
    activity_level: int    
    zone_hash: str         
    capabilities: Dict[str, int] = None

class SharedNetworkEncryption:
    """Chiffrement avec clé réseau partagée pour découverte légitimes"""
    
    def __init__(self, network_passphrase: str = ORED_NETWORK_PASSPHRASE):
        self.network_passphrase = network_passphrase
        self.fernet = self._create_network_fernet()
        
    def _create_network_fernet(self) -> Fernet:
        """Crée Fernet avec clé dérivée de la passphrase réseau"""
        salt = b"openred-discovery-salt-2025"  # Salt fixe pour compatibilité
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.network_passphrase.encode()))
        return Fernet(key)
        
    def encrypt_beacon(self, beacon_data: Dict) -> bytes:
        """Chiffre avec clé réseau partagée"""
        json_data = json.dumps(beacon_data, default=str)
        return self.fernet.encrypt(json_data.encode())
        
    def decrypt_beacon(self, encrypted_data: bytes) -> Optional[Dict]:
        """Déchiffre avec clé réseau partagée"""
        try:
            decrypted = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted.decode())
        except:
            return None  # Pas un nœud O-RedSearch légitime

class NetworkBeaconBroadcaster:
    """Émetteur avec clé réseau partagée"""
    
    def __init__(self, node_info: SecureNodeBeacon, broadcast_interval: int = 30):
        self.node_info = node_info
        self.broadcast_interval = broadcast_interval
        self.encryption = SharedNetworkEncryption()
        self.multicast_groups = [
            '224.0.1.100',  # Groupe O-RedSearch principal
            '224.0.1.101',  # Backup groupe
        ]
        self.port = 5354
        self.running = False
        self.sock = None
        
    def start_broadcasting(self):
        """Démarre émission avec clé réseau"""
        if self.running:
            return
            
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # TTL limité pour sécurité
        ttl = 3  # Réseau local + 2 sauts
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        
        threading.Thread(target=self._network_broadcast_loop, daemon=True).start()
        print(f"🌐 Network beacon started (hash: {self.node_info.node_hash[:8]})")
        
    def stop_broadcasting(self):
        """Arrête émission"""
        self.running = False
        if self.sock:
            self.sock.close()
            
    def _network_broadcast_loop(self):
        """Boucle d'émission réseau"""
        while self.running:
            try:
                beacon_data = self._create_network_beacon()
                encrypted_beacon = self.encryption.encrypt_beacon(beacon_data)
                
                # Diffuser sur groupes multiples
                for group in self.multicast_groups:
                    self.sock.sendto(encrypted_beacon, (group, self.port))
                
                print(f"🌐 Network beacon sent: {self.node_info.node_hash[:8]} ({self.node_info.sector})")
                
                # Intervalle avec jitter anti-corrélation
                jitter = secrets.randbelow(10) - 5
                time.sleep(self.broadcast_interval + jitter)
                
            except Exception as e:
                print(f"❌ Network beacon error: {e}")
                time.sleep(5)
                
    def _create_network_beacon(self) -> Dict:
        """Crée balise réseau"""
        # Timestamp flou pour anti-corrélation
        fuzzy_timestamp = int(time.time() // 180) * 180  # Arrondi à 3 minutes
        
        return {
            "type": "o-red-network-beacon",
            "version": "2.1-shared",
            "timestamp": fuzzy_timestamp,
            "beacon_id": secrets.token_hex(8),
            "node_data": {
                "node_hash": self.node_info.node_hash,
                "sector": self.node_info.sector,
                "services": self.node_info.services,
                "activity_level": self.node_info.activity_level,
                "zone_hash": self.node_info.zone_hash,
                "capabilities": self.node_info.capabilities or {}
            }
        }

class NetworkBeaconScanner:
    """Scanner avec clé réseau partagée - découverte mutuelle"""
    
    def __init__(self, cache_duration: int = 120):
        self.discovered_nodes = {}
        self.cache_duration = cache_duration
        self.encryption = SharedNetworkEncryption()
        self.running = False
        self.sock = None
        self.stats = {"beacons_received": 0, "decryption_success": 0, "nodes_discovered": 0}
        
    def start_network_scanning(self):
        """Démarre écoute réseau"""
        if self.running:
            return
            
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.sock.bind(('', 5354))
        except:
            self.sock.bind(('', 0))
            
        # Rejoindre groupes O-RedSearch
        for group in ['224.0.1.100', '224.0.1.101']:
            mreq = socket.inet_aton(group) + socket.inet_aton('0.0.0.0')
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
        threading.Thread(target=self._network_scan_loop, daemon=True).start()
        threading.Thread(target=self._network_cleanup_loop, daemon=True).start()
        
        print("🔍 Network scanner started - discovering legitimate nodes...")
        
    def stop_network_scanning(self):
        """Arrête écoute"""
        self.running = False
        if self.sock:
            self.sock.close()
            
    def _network_scan_loop(self):
        """Boucle d'écoute réseau"""
        while self.running:
            try:
                encrypted_data, addr = self.sock.recvfrom(4096)
                self._process_network_beacon(encrypted_data, addr)
                self.stats["beacons_received"] += 1
                
            except Exception as e:
                if self.running:
                    print(f"❌ Network scanner error: {e}")
                    
    def _process_network_beacon(self, encrypted_data: bytes, addr: Tuple[str, int]):
        """Traite balise réseau reçue"""
        try:
            # Déchiffrement avec clé réseau
            beacon = self.encryption.decrypt_beacon(encrypted_data)
            
            if not beacon or beacon.get("type") != "o-red-network-beacon":
                return
                
            self.stats["decryption_success"] += 1
            
            node_data = beacon.get("node_data", {})
            node_hash = node_data.get("node_hash")
            
            if not node_hash:
                return
                
            # Enrichir données réseau
            enhanced_data = {
                **node_data,
                "discovered_at": time.time(),
                "source_ip_hash": hashlib.sha256(addr[0].encode()).hexdigest()[:16],
                "beacon_timestamp": beacon.get("timestamp"),
                "last_seen": time.time(),
                "beacon_version": beacon.get("version")
            }
            
            # Cache de découverte
            if node_hash in self.discovered_nodes:
                self.discovered_nodes[node_hash].update(enhanced_data)
            else:
                self.discovered_nodes[node_hash] = enhanced_data
                self.stats["nodes_discovered"] += 1
                print(f"✨ Legitimate node discovered: {node_hash[:8]} ({node_data.get('sector', 'unknown')})")
                
        except Exception as e:
            # Balise non-légitime (clé différente)
            pass
            
    def _network_cleanup_loop(self):
        """Nettoyage cache réseau"""
        while self.running:
            current_time = time.time()
            expired_hashes = []
            
            for node_hash, node_data in self.discovered_nodes.items():
                if current_time - node_data["last_seen"] > self.cache_duration:
                    expired_hashes.append(node_hash)
                    
            for node_hash in expired_hashes:
                del self.discovered_nodes[node_hash]
                
            if expired_hashes:
                print(f"🗑️ {len(expired_hashes)} nodes expired from cache")
                
            time.sleep(30)

class NetworkORedSearch:
    """Moteur de recherche avec découverte réseau"""
    
    def __init__(self, network_scanner: NetworkBeaconScanner):
        self.scanner = network_scanner
        
    def network_search(self, **filters) -> List[Dict]:
        """Recherche dans le réseau O-RedSearch"""
        results = []
        current_time = time.time()
        
        for node_hash, node_data in self.scanner.discovered_nodes.items():
            # Vérifier fraîcheur
            if current_time - node_data["last_seen"] > self.scanner.cache_duration:
                continue
                
            # Appliquer filtres
            if self._matches_network_filters(node_data, filters):
                result = self._prepare_network_result(node_data)
                results.append(result)
                
        return self._sort_by_network_relevance(results, filters)
        
    def _matches_network_filters(self, node_data: Dict, filters: Dict) -> bool:
        """Filtres réseau"""
        if "sector" in filters and node_data.get("sector") != filters["sector"]:
            return False
            
        if "services" in filters:
            required_services = filters["services"]
            if isinstance(required_services, str):
                required_services = [required_services]
            node_services = node_data.get("services", [])
            if not any(service in node_services for service in required_services):
                return False
                
        if "min_activity" in filters:
            if node_data.get("activity_level", 0) < filters["min_activity"]:
                return False
                
        if "zone_hash" in filters:
            if not node_data.get("zone_hash", "").startswith(filters["zone_hash"][:8]):
                return False
                
        return True
        
    def _prepare_network_result(self, node_data: Dict) -> Dict:
        """Prépare résultat réseau"""
        return {
            "node_hash": node_data["node_hash"][:12] + "...",
            "sector": node_data.get("sector"),
            "services": node_data.get("services", []),
            "activity_level": node_data.get("activity_level", 0),
            "zone_hash": node_data.get("zone_hash", "")[:8] + "...",
            "capabilities": node_data.get("capabilities", {}),
            "freshness_seconds": int(time.time() - node_data.get("last_seen", 0)),
            "discovered_at": datetime.fromtimestamp(node_data.get("discovered_at", 0)).strftime("%H:%M:%S")
        }
        
    def _sort_by_network_relevance(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """Tri par pertinence réseau"""
        def network_score(node):
            score = node.get("activity_level", 0)
            if node.get("freshness_seconds", 999) < 60:
                score += 50
            return score
            
        return sorted(results, key=network_score, reverse=True)
        
    def get_network_stats(self) -> Dict:
        """Statistiques réseau"""
        return {
            "legitimate_nodes": len(self.scanner.discovered_nodes),
            "scanner_stats": dict(self.scanner.stats),
            "cache_duration": self.scanner.cache_duration,
            "network_encryption": True,
            "mutual_discovery": True
        }

def create_network_zone_hash(lat: float, lng: float, precision: int = 100) -> str:
    """Zone hash avec précision réseau"""
    fuzzy_lat = round(lat * precision) / precision
    fuzzy_lng = round(lng * precision) / precision
    zone_string = f"{fuzzy_lat}:{fuzzy_lng}"
    return hashlib.sha256(zone_string.encode()).hexdigest()

# Version réseau avec découverte mutuelle
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='O-RedSearch Network - Mutual Discovery')
    parser.add_argument('--node-id', required=True, help='Node identifier')
    parser.add_argument('--sector', required=True, help='Node sector')
    parser.add_argument('--lat', type=float, default=48.8566, help='Latitude')
    parser.add_argument('--lng', type=float, default=2.3522, help='Longitude')
    parser.add_argument('--search-after', type=int, default=60, help='Search after X seconds')
    
    args = parser.parse_args()
    
    # Créer nœud réseau
    node_hash = hashlib.sha256(f"{args.node_id}{time.time()}".encode()).hexdigest()
    zone_hash = create_network_zone_hash(args.lat, args.lng)
    
    network_node = SecureNodeBeacon(
        node_hash=node_hash,
        sector=args.sector,
        services=["storage", "compute", "discovery"],
        activity_level=secrets.randbelow(20) + 80,
        zone_hash=zone_hash
    )
    
    # Démarrer système réseau
    broadcaster = NetworkBeaconBroadcaster(network_node)
    scanner = NetworkBeaconScanner()
    search_engine = NetworkORedSearch(scanner)
    
    broadcaster.start_broadcasting()
    scanner.start_network_scanning()
    
    print(f"\n🌐 O-RedSearch Network started")
    print(f"   Node: {node_hash[:16]}...")
    print(f"   Sector: {args.sector}")
    print(f"   Zone: {zone_hash[:16]}...")
    print(f"   Network Discovery: ENABLED ✅")
    
    # Attendre découvertes puis chercher
    print(f"\n⏳ Waiting {args.search_after}s for network discovery...")
    time.sleep(args.search_after)
    
    # Test de recherche réseau
    print(f"\n🔍 NETWORK SEARCH TESTS")
    print("=" * 40)
    
    # Recherche tous secteurs
    all_results = search_engine.network_search()
    print(f"\n📍 All discovered nodes: {len(all_results)}")
    for node in all_results:
        print(f"   - {node['node_hash']}: {node['sector']} | Activity: {node['activity_level']}% | Fresh: {node['freshness_seconds']}s")
    
    # Recherche par secteur
    if args.sector:
        sector_results = search_engine.network_search(sector=args.sector)
        print(f"\n🎯 Nodes in '{args.sector}' sector: {len(sector_results)}")
        for node in sector_results:
            print(f"   - {node['node_hash']}: {node['services']} | {node['discovered_at']}")
    
    # Stats finales
    stats = search_engine.get_network_stats()
    print(f"\n📊 Network Stats:")
    print(f"   Legitimate nodes: {stats['legitimate_nodes']}")
    print(f"   Beacons received: {stats['scanner_stats']['beacons_received']}")
    print(f"   Successful decryptions: {stats['scanner_stats']['decryption_success']}")
    print(f"   Discovery rate: {stats['scanner_stats']['decryption_success']}/{stats['scanner_stats']['beacons_received']} = {stats['scanner_stats']['decryption_success']/max(1,stats['scanner_stats']['beacons_received'])*100:.1f}%")
    
    try:
        print(f"\n💡 Interactive mode - Press Ctrl+C to exit")
        while True:
            time.sleep(10)
            current_stats = search_engine.get_network_stats()
            print(f"📊 Nodes: {current_stats['legitimate_nodes']} | Beacons: {current_stats['scanner_stats']['beacons_received']} | Success: {current_stats['scanner_stats']['decryption_success']}")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping network discovery...")
        broadcaster.stop_broadcasting()
        scanner.stop_network_scanning()
        print(f"✅ Network O-RedSearch stopped")