#!/usr/bin/env python3
"""
O-RedSearch Pure : Découverte 100% Décentralisée
SANS visibilité web - Protection totale des données
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

@dataclass
class SecureNodeBeacon:
    """Structure sécurisée - métadonnées minimales"""
    node_hash: str          # Hash anonyme (pas d'ID réel)
    sector: str            # Secteur flou : "tech", "health", etc.
    services: List[str]    # Services génériques seulement
    activity_level: int    # 0-100
    zone_hash: str         # Zone géographique floue (pas de coords exactes)
    capabilities: Dict[str, int] = None  # Capacités techniques anonymes
    
class EncryptionEngine:
    """Moteur de chiffrement pour balises sécurisées"""
    
    def __init__(self):
        self.master_key = self._generate_ephemeral_key()
        self.fernet = Fernet(self.master_key)
        self.key_rotation_interval = 3600  # 1 heure
        self.last_rotation = time.time()
        
    def _generate_ephemeral_key(self) -> bytes:
        """Génère une clé éphémère"""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"o-red-search-ephemeral"))
        return key
        
    def should_rotate_key(self) -> bool:
        """Vérifie si rotation de clé nécessaire"""
        return time.time() - self.last_rotation > self.key_rotation_interval
        
    def rotate_key(self):
        """Rotation automatique des clés"""
        self.master_key = self._generate_ephemeral_key()
        self.fernet = Fernet(self.master_key)
        self.last_rotation = time.time()
        print("🔄 Key rotated for anonymity")
        
    def encrypt_beacon(self, beacon_data: Dict) -> bytes:
        """Chiffre les données de balise"""
        if self.should_rotate_key():
            self.rotate_key()
            
        json_data = json.dumps(beacon_data, default=str)
        return self.fernet.encrypt(json_data.encode())
        
    def decrypt_beacon(self, encrypted_data: bytes) -> Optional[Dict]:
        """Déchiffre une balise reçue"""
        try:
            decrypted = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted.decode())
        except:
            return None  # Clé différente ou données corrompues

class AnonymousBeaconBroadcaster:
    """Émetteur de balises anonymes et sécurisées"""
    
    def __init__(self, node_info: SecureNodeBeacon, broadcast_interval: int = 45):
        self.node_info = node_info
        self.broadcast_interval = broadcast_interval
        self.encryption = EncryptionEngine()
        self.multicast_groups = [
            '224.0.1.100',  # Groupe O-RedSearch
            '224.0.1.101',  # Backup groupe
        ]
        self.port = 5354  # Port différent de mDNS standard
        self.running = False
        self.sock = None
        
    def start_broadcasting(self):
        """Démarre émission anonyme"""
        if self.running:
            return
            
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Multicast avec TTL limité (anti-surveillance)
        ttl = 2  # Seulement réseau local + 1 saut
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        
        threading.Thread(target=self._anonymous_broadcast_loop, daemon=True).start()
        print(f"👻 Anonymous beacon started (zone: {self.node_info.zone_hash[:8]})")
        
    def stop_broadcasting(self):
        """Arrête émission"""
        self.running = False
        if self.sock:
            self.sock.close()
            
    def _anonymous_broadcast_loop(self):
        """Boucle d'émission anonyme avec rotation"""
        while self.running:
            try:
                # Créer balise chiffrée
                beacon_data = self._create_anonymous_beacon()
                encrypted_beacon = self.encryption.encrypt_beacon(beacon_data)
                
                # Diffuser sur groupes multiples (redondance)
                for group in self.multicast_groups:
                    self.sock.sendto(encrypted_beacon, (group, self.port))
                
                print(f"👻 Anonymous beacon sent (hash: {self.node_info.node_hash[:8]})")
                
                # Anti-corrélation : intervalle variable
                jitter = secrets.randbelow(10) - 5  # ±5 secondes
                time.sleep(self.broadcast_interval + jitter)
                
            except Exception as e:
                print(f"❌ Anonymous beacon error: {e}")
                time.sleep(5)
                
    def _create_anonymous_beacon(self) -> Dict:
        """Crée balise anonyme avec métadonnées minimales"""
        # Timestamp flou (pas de précision exacte)
        fuzzy_timestamp = int(time.time() // 300) * 300  # Arrondi à 5 minutes
        
        return {
            "type": "o-red-anonymous-beacon",
            "version": "2.0-pure",
            "timestamp": fuzzy_timestamp,
            "beacon_id": secrets.token_hex(8),  # ID éphémère
            "node_data": {
                "node_hash": self.node_info.node_hash,
                "sector": self.node_info.sector,
                "services": self.node_info.services,
                "activity_level": self.node_info.activity_level,
                "zone_hash": self.node_info.zone_hash,
                "capabilities": self.node_info.capabilities or {}
            }
        }

class StealthBeaconScanner:
    """Scanner furtif - écoute sans trace"""
    
    def __init__(self, cache_duration: int = 90):
        self.discovered_nodes = {}
        self.cache_duration = cache_duration
        self.encryption = EncryptionEngine()
        self.running = False
        self.sock = None
        self.stats = {"beacons_received": 0, "decryption_failed": 0, "nodes_cached": 0}
        
    def start_stealth_scanning(self):
        """Démarre écoute furtive"""
        if self.running:
            return
            
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.sock.bind(('', 5354))
        except:
            self.sock.bind(('', 0))  # Port auto si occupé
            
        # Rejoindre groupes multicast O-RedSearch
        for group in ['224.0.1.100', '224.0.1.101']:
            mreq = socket.inet_aton(group) + socket.inet_aton('0.0.0.0')
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
        threading.Thread(target=self._stealth_scan_loop, daemon=True).start()
        threading.Thread(target=self._stealth_cleanup_loop, daemon=True).start()
        
        print("👁️‍🗨️ Stealth scanner started - invisible listening...")
        
    def stop_stealth_scanning(self):
        """Arrête écoute"""
        self.running = False
        if self.sock:
            self.sock.close()
            
    def _stealth_scan_loop(self):
        """Boucle d'écoute furtive"""
        while self.running:
            try:
                encrypted_data, addr = self.sock.recvfrom(4096)
                self._process_encrypted_beacon(encrypted_data, addr)
                self.stats["beacons_received"] += 1
                
            except Exception as e:
                if self.running:
                    print(f"❌ Stealth scanner error: {e}")
                    
    def _process_encrypted_beacon(self, encrypted_data: bytes, addr: Tuple[str, int]):
        """Traite balise chiffrée reçue"""
        try:
            # Tentative de déchiffrement
            beacon = self.encryption.decrypt_beacon(encrypted_data)
            
            if not beacon or beacon.get("type") != "o-red-anonymous-beacon":
                self.stats["decryption_failed"] += 1
                return
                
            node_data = beacon.get("node_data", {})
            node_hash = node_data.get("node_hash")
            
            if not node_hash:
                return
                
            # Enrichir avec données réseau minimales
            enhanced_data = {
                **node_data,
                "discovered_at": time.time(),
                "source_ip_hash": hashlib.sha256(addr[0].encode()).hexdigest()[:16],  # IP anonymisée
                "beacon_timestamp": beacon.get("timestamp"),
                "last_seen": time.time()
            }
            
            # Cache anonyme
            if node_hash in self.discovered_nodes:
                self.discovered_nodes[node_hash].update(enhanced_data)
            else:
                self.discovered_nodes[node_hash] = enhanced_data
                self.stats["nodes_cached"] += 1
                print(f"🔍 Anonymous node discovered: {node_hash[:8]} ({node_data.get('sector', 'unknown')})")
                
        except Exception as e:
            self.stats["decryption_failed"] += 1
            
    def _stealth_cleanup_loop(self):
        """Nettoyage furtif - effacement automatique"""
        while self.running:
            current_time = time.time()
            expired_hashes = []
            
            for node_hash, node_data in self.discovered_nodes.items():
                if current_time - node_data["last_seen"] > self.cache_duration:
                    expired_hashes.append(node_hash)
                    
            for node_hash in expired_hashes:
                del self.discovered_nodes[node_hash]
                
            if expired_hashes:
                print(f"🗑️ {len(expired_hashes)} nodes expired (privacy cleanup)")
                
            time.sleep(30)

class PureORedSearch:
    """Moteur de recherche O-RedSearch pur - 100% décentralisé"""
    
    def __init__(self, stealth_scanner: StealthBeaconScanner):
        self.scanner = stealth_scanner
        
    def anonymous_search(self, **filters) -> List[Dict]:
        """
        Recherche anonyme dans cache local uniquement
        
        Filtres supportés:
        - sector: str
        - services: List[str] ou str
        - min_activity: int (0-100)
        - zone_hash: str (zone géographique)
        """
        results = []
        current_time = time.time()
        
        for node_hash, node_data in self.scanner.discovered_nodes.items():
            # Vérifier fraîcheur
            if current_time - node_data["last_seen"] > self.scanner.cache_duration:
                continue
                
            # Appliquer filtres anonymes
            if self._matches_anonymous_filters(node_data, filters):
                # Retourner données anonymisées
                anonymized_result = self._anonymize_result(node_data)
                results.append(anonymized_result)
                
        # Tri par pertinence sans révéler identité
        return self._sort_anonymously(results, filters)
        
    def _matches_anonymous_filters(self, node_data: Dict, filters: Dict) -> bool:
        """Filtre anonyme sans révéler données sensibles"""
        
        if "sector" in filters:
            if node_data.get("sector") != filters["sector"]:
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
            if node_data.get("zone_hash") != filters["zone_hash"]:
                return False
                
        return True
        
    def _anonymize_result(self, node_data: Dict) -> Dict:
        """Anonymise le résultat pour préserver confidentialité"""
        return {
            "node_hash": node_data["node_hash"][:12] + "...",  # Hash tronqué
            "sector": node_data.get("sector"),
            "services": node_data.get("services", []),
            "activity_level": node_data.get("activity_level", 0),
            "zone_hash": node_data.get("zone_hash", "")[:8] + "...",
            "capabilities": node_data.get("capabilities", {}),
            "freshness": time.time() - node_data.get("last_seen", 0),
            "source_region": node_data.get("source_ip_hash", "")[:4] + "..."
        }
        
    def _sort_anonymously(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """Tri anonyme par pertinence"""
        def anonymous_score(node):
            score = 0
            score += node.get("activity_level", 0)
            if node.get("freshness", 999) < 60:  # Moins d'1 minute
                score += 50
            return score
            
        return sorted(results, key=anonymous_score, reverse=True)
        
    def get_anonymous_stats(self) -> Dict:
        """Statistiques anonymes"""
        return {
            "nodes_in_cache": len(self.scanner.discovered_nodes),
            "scanner_stats": dict(self.scanner.stats),
            "cache_duration": self.scanner.cache_duration,
            "encryption_active": True,
            "web_visibility": False  # Confirmé: pas de visibilité web
        }

def create_anonymous_zone_hash(lat: float, lng: float, precision: int = 1000) -> str:
    """Crée un hash de zone géographique flou (non précis)"""
    # Arrondir coordonnées pour créer zones floues
    fuzzy_lat = round(lat * precision) / precision
    fuzzy_lng = round(lng * precision) / precision
    zone_string = f"{fuzzy_lat}:{fuzzy_lng}"
    return hashlib.sha256(zone_string.encode()).hexdigest()

# Exemple d'utilisation pure (sans web)
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='O-RedSearch Pure - 100% Decentralized')
    parser.add_argument('--node-id', required=True, help='Node identifier')
    parser.add_argument('--sector', required=True, help='Node sector')
    parser.add_argument('--lat', type=float, default=48.8566, help='Latitude')
    parser.add_argument('--lng', type=float, default=2.3522, help='Longitude')
    parser.add_argument('--no-web', action='store_true', help='No web visibility (pure P2P)')
    
    args = parser.parse_args()
    
    if not args.no_web:
        print("❌ Error: --no-web required for pure mode")
        print("   Web visibility contradicts data protection philosophy")
        exit(1)
    
    # Créer nœud anonyme
    node_hash = hashlib.sha256(f"{args.node_id}{time.time()}".encode()).hexdigest()
    zone_hash = create_anonymous_zone_hash(args.lat, args.lng)
    
    anonymous_node = SecureNodeBeacon(
        node_hash=node_hash,
        sector=args.sector,
        services=["storage", "compute"],  # Services génériques
        activity_level=secrets.randbelow(20) + 80,  # 80-100%
        zone_hash=zone_hash
    )
    
    # Démarrer système pur
    broadcaster = AnonymousBeaconBroadcaster(anonymous_node)
    scanner = StealthBeaconScanner()
    search_engine = PureORedSearch(scanner)
    
    broadcaster.start_broadcasting()
    scanner.start_stealth_scanning()
    
    print(f"\n🛡️ O-RedSearch Pure started")
    print(f"   Node: {node_hash[:16]}...")
    print(f"   Sector: {args.sector}")
    print(f"   Zone: {zone_hash[:16]}...")
    print(f"   Web visibility: DISABLED ✅")
    
    try:
        while True:
            time.sleep(10)
            stats = search_engine.get_anonymous_stats()
            print(f"📊 Cache: {stats['nodes_in_cache']} nodes | "
                  f"Received: {stats['scanner_stats']['beacons_received']} | "
                  f"Failed: {stats['scanner_stats']['decryption_failed']}")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping pure O-RedSearch...")
        broadcaster.stop_broadcasting()
        scanner.stop_stealth_scanning()