#!/usr/bin/env python3
"""
O-RedSearch : Passive Discovery Engine
Révolutionne la découverte P2P par signalisation passive (beacon protocol)
"""

import socket
import json
import threading
import time
import math
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

@dataclass
class NodeBeacon:
    """Structure des données de balise nœud"""
    node_id: str
    location: Dict[str, float]  # {"lat": 48.8566, "lng": 2.3522, "elevation": 35}
    services: List[str]         # ["storage", "compute", "relay", "search"]
    activity_level: int         # 0-100
    sector: str                 # "tech", "health", "education", "finance"
    connection_info: Dict[str, any]  # IPs, ports, protocols
    capabilities: Dict[str, any] = None  # Capacités techniques
    metadata: Dict[str, any] = None      # Métadonnées personnalisées

class BeaconBroadcaster:
    """Émetteur de balises - Le phare qui signale sa présence"""
    
    def __init__(self, node_info: NodeBeacon, broadcast_interval: int = 30):
        self.node_info = node_info
        self.broadcast_interval = broadcast_interval
        self.multicast_group = '224.0.0.250'  # mDNS range
        self.port = 5353
        self.running = False
        self.sock = None
        
    def start_broadcasting(self):
        """Démarre l'émission périodique de balises"""
        if self.running:
            return
            
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Permettre multicast
        ttl = 2  # Time-to-live (2 = réseau local + 1 saut)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        
        threading.Thread(target=self._broadcast_loop, daemon=True).start()
        print(f"🚨 Beacon started for node {self.node_info.node_id}")
        
    def stop_broadcasting(self):
        """Arrête l'émission"""
        self.running = False
        if self.sock:
            self.sock.close()
            
    def _broadcast_loop(self):
        """Boucle d'émission des balises"""
        while self.running:
            try:
                beacon_data = self._create_beacon_message()
                message = json.dumps(beacon_data, default=str).encode('utf-8')
                
                self.sock.sendto(message, (self.multicast_group, self.port))
                print(f"📡 Beacon sent: {self.node_info.node_id} ({self.node_info.sector})")
                
            except Exception as e:
                print(f"❌ Beacon error: {e}")
                
            time.sleep(self.broadcast_interval)
            
    def _create_beacon_message(self) -> Dict:
        """Crée le message de balise"""
        return {
            "type": "o-red-beacon",
            "version": "1.0",
            "timestamp": time.time(),
            "beacon_id": hashlib.sha256(f"{self.node_info.node_id}{time.time()}".encode()).hexdigest()[:16],
            "node_data": asdict(self.node_info)
        }

class PassiveBeaconScanner:
    """Scanner passif - Écoute les phares sans interaction"""
    
    def __init__(self, cache_duration: int = 120):
        self.discovered_nodes = {}  # Cache des nœuds découverts
        self.cache_duration = cache_duration  # Durée de vie cache (secondes)
        self.running = False
        self.sock = None
        self.stats = defaultdict(int)
        
    def start_scanning(self):
        """Démarre l'écoute passive"""
        if self.running:
            return
            
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.sock.bind(('', self.port or 5353))
        except:
            self.sock.bind(('', 0))  # Port automatique si 5353 occupé
            
        # Rejoindre groupe multicast
        mreq = socket.inet_aton('224.0.0.250') + socket.inet_aton('0.0.0.0')
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        threading.Thread(target=self._scan_loop, daemon=True).start()
        threading.Thread(target=self._cleanup_loop, daemon=True).start()
        
        print("👁️ Passive scanner started - listening for beacons...")
        
    def stop_scanning(self):
        """Arrête l'écoute"""
        self.running = False
        if self.sock:
            self.sock.close()
            
    def _scan_loop(self):
        """Boucle d'écoute des balises"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                self._process_beacon(data, addr)
                self.stats['beacons_received'] += 1
                
            except Exception as e:
                if self.running:  # Ignore erreurs lors de l'arrêt
                    print(f"❌ Scanner error: {e}")
                    
    def _process_beacon(self, data: bytes, addr: Tuple[str, int]):
        """Traite une balise reçue"""
        try:
            beacon = json.loads(data.decode('utf-8'))
            
            if beacon.get("type") != "o-red-beacon":
                return
                
            node_data = beacon.get("node_data", {})
            node_id = node_data.get("node_id")
            
            if not node_id:
                return
                
            # Enrichir avec infos réseau
            enhanced_data = {
                **node_data,
                "discovered_at": time.time(),
                "beacon_timestamp": beacon.get("timestamp"),
                "source_ip": addr[0],
                "source_port": addr[1],
                "beacon_id": beacon.get("beacon_id"),
                "last_seen": time.time()
            }
            
            # Mettre à jour cache
            if node_id in self.discovered_nodes:
                # Nœud connu, mise à jour
                self.discovered_nodes[node_id].update(enhanced_data)
                self.stats['nodes_updated'] += 1
            else:
                # Nouveau nœud
                self.discovered_nodes[node_id] = enhanced_data
                self.stats['nodes_discovered'] += 1
                print(f"🔍 New node discovered: {node_id} ({node_data.get('sector', 'unknown')})")
                
        except Exception as e:
            self.stats['invalid_beacons'] += 1
            
    def _cleanup_loop(self):
        """Nettoyage périodique du cache"""
        while self.running:
            current_time = time.time()
            expired_nodes = []
            
            for node_id, node_data in self.discovered_nodes.items():
                if current_time - node_data["last_seen"] > self.cache_duration:
                    expired_nodes.append(node_id)
                    
            for node_id in expired_nodes:
                del self.discovered_nodes[node_id]
                self.stats['nodes_expired'] += 1
                print(f"⏰ Node expired: {node_id}")
                
            time.sleep(30)  # Nettoyage toutes les 30 secondes

class ORedSearch:
    """Moteur de recherche temps réel O-RedSearch"""
    
    def __init__(self, scanner: PassiveBeaconScanner):
        self.scanner = scanner
        
    def search(self, **filters) -> List[Dict]:
        """
        Recherche en temps réel sans annuaire
        
        Filtres supportés:
        - sector: str
        - services: List[str] ou str
        - min_activity: int (0-100)
        - max_activity: int (0-100) 
        - max_distance_km: float
        - my_location: Dict[str, float] {"lat": x, "lng": y}
        - node_ids: List[str]
        """
        results = []
        current_time = time.time()
        
        for node_id, node_data in self.scanner.discovered_nodes.items():
            # Vérifier fraîcheur
            if current_time - node_data["last_seen"] > self.scanner.cache_duration:
                continue
                
            # Appliquer filtres
            if self._matches_filters(node_data, filters):
                results.append(node_data)
                
        # Trier par pertinence
        return self._sort_by_relevance(results, filters)
        
    def _matches_filters(self, node_data: Dict, filters: Dict) -> bool:
        """Vérifie si un nœud correspond aux filtres"""
        
        # Filtre secteur
        if "sector" in filters:
            if node_data.get("sector") != filters["sector"]:
                return False
                
        # Filtre services
        if "services" in filters:
            required_services = filters["services"]
            if isinstance(required_services, str):
                required_services = [required_services]
                
            node_services = node_data.get("services", [])
            if not any(service in node_services for service in required_services):
                return False
                
        # Filtre activité
        activity = node_data.get("activity_level", 0)
        if "min_activity" in filters and activity < filters["min_activity"]:
            return False
        if "max_activity" in filters and activity > filters["max_activity"]:
            return False
            
        # Filtre distance
        if "max_distance_km" in filters and "my_location" in filters:
            node_location = node_data.get("location", {})
            if node_location:
                distance = self._calculate_distance(
                    filters["my_location"],
                    node_location
                )
                if distance > filters["max_distance_km"]:
                    return False
                    
        # Filtre IDs spécifiques
        if "node_ids" in filters:
            if node_data.get("node_id") not in filters["node_ids"]:
                return False
                
        return True
        
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calcule distance entre deux points GPS (formule haversine)"""
        try:
            lat1, lng1 = math.radians(loc1["lat"]), math.radians(loc1["lng"])
            lat2, lng2 = math.radians(loc2["lat"]), math.radians(loc2["lng"])
            
            dlat = lat2 - lat1
            dlng = lng2 - lng1
            
            a = (math.sin(dlat/2)**2 + 
                 math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2)
            c = 2 * math.asin(math.sqrt(a))
            
            return 6371 * c  # Rayon terre en km
        except:
            return float('inf')
            
    def _sort_by_relevance(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """Trie les résultats par pertinence"""
        def relevance_score(node):
            score = 0
            
            # Bonus activité
            score += node.get("activity_level", 0)
            
            # Bonus fraîcheur
            age = time.time() - node.get("last_seen", 0)
            if age < 60:  # Moins d'1 minute
                score += 50
            elif age < 300:  # Moins de 5 minutes
                score += 20
                
            # Bonus proximité
            if "my_location" in filters and node.get("location"):
                distance = self._calculate_distance(filters["my_location"], node["location"])
                if distance < 10:  # Moins de 10km
                    score += 30
                elif distance < 50:  # Moins de 50km
                    score += 10
                    
            return score
            
        return sorted(results, key=relevance_score, reverse=True)
        
    def get_stats(self) -> Dict:
        """Statistiques du moteur de recherche"""
        return {
            "nodes_in_cache": len(self.scanner.discovered_nodes),
            "scanner_stats": dict(self.scanner.stats),
            "cache_duration": self.scanner.cache_duration
        }

# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration nœud local
    my_node = NodeBeacon(
        node_id="node_paris_001",
        location={"lat": 48.8566, "lng": 2.3522, "elevation": 35},
        services=["storage", "compute"],
        activity_level=85,
        sector="tech",
        connection_info={
            "ip": "192.168.1.100",
            "ports": {"http": 8080, "p2p": 9000},
            "protocols": ["tcp", "udp", "webrtc"]
        }
    )
    
    # Démarrer beacon et scanner
    broadcaster = BeaconBroadcaster(my_node)
    scanner = PassiveBeaconScanner()
    search_engine = ORedSearch(scanner)
    
    broadcaster.start_broadcasting()
    scanner.start_scanning()
    
    # Attendre découvertes
    time.sleep(5)
    
    # Rechercher nœuds
    print("\n🔍 Searching for tech nodes with high activity...")
    results = search_engine.search(
        sector="tech",
        min_activity=70,
        max_distance_km=100,
        my_location={"lat": 48.8566, "lng": 2.3522}
    )
    
    print(f"Found {len(results)} nodes:")
    for node in results[:5]:  # Top 5
        print(f"  - {node['node_id']}: {node['activity_level']}% activity")
        
    # Stats
    print(f"\n📊 Stats: {search_engine.get_stats()}")