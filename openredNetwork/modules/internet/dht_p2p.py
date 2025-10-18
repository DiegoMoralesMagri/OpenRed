#!/usr/bin/env python3
"""
SYSTÈME DE DÉCOUVERTE P2P DÉCENTRALISÉ
=====================================

Architecture 100% décentralisée conforme au Manifeste OpenRed :
- Aucune dépendance vers les géants (GitHub, Google, etc.)
- DHT (Distributed Hash Table) pour la découverte
- Réseau de seeds distribués
- Protocole gossip pour propagation
- DNS communautaire auto-hébergé

Violation corrigée :
❌ GitHub Registry (Microsoft) 
✅ DHT P2P + Seeds distribués

Conformité Manifeste :
✅ Article III - Décentralisation irréversible
✅ Article III - Absence de point central  
✅ Article III - Architecture P2P obligatoire
✅ Article III - Résistance à la censure
"""

import socket
import json
import time
import threading
import hashlib
import random
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import struct


@dataclass
class FortInfo:
    """Information d'un fort dans le réseau P2P"""
    fort_id: str
    nom: str
    ip_publique: str
    port: int
    cle_publique: str
    timestamp: float
    version_protocole: str = "1.0"
    
    def to_bytes(self) -> bytes:
        """Sérialise en bytes pour le réseau"""
        data = asdict(self)
        json_str = json.dumps(data, separators=(',', ':'))
        return json_str.encode('utf-8')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'FortInfo':
        """Désérialise depuis bytes"""
        json_str = data.decode('utf-8')
        data_dict = json.loads(json_str)
        return cls(**data_dict)
    
    def is_expired(self, ttl_hours: int = 24) -> bool:
        """Vérifie si l'info est expirée"""
        age = time.time() - self.timestamp
        return age > (ttl_hours * 3600)


class DHTP2P:
    """
    DHT (Distributed Hash Table) P2P pour découverte des forts
    
    Inspiré de Kademlia/BitTorrent mais adapté aux forts OpenRed
    """
    
    def __init__(self, port: int = 7777):
        self.port = port
        self.node_id = self._generate_node_id()
        self.routing_table: Dict[str, Tuple[str, int]] = {}
        self.fort_storage: Dict[str, FortInfo] = {}
        self.seeds = self._get_community_seeds()
        self.running = False
        self.socket = None
        
    def _generate_node_id(self) -> str:
        """Génère un ID unique pour ce nœud"""
        # Utilise MAC + timestamp pour l'unicité
        import uuid
        mac = uuid.getnode()
        timestamp = int(time.time() * 1000)
        data = f"{mac}:{timestamp}".encode()
        return hashlib.sha256(data).hexdigest()
    
    def _get_community_seeds(self) -> List[Tuple[str, int]]:
        """
        Seeds communautaires distribués (ZÉRO dépendance géants)
        
        Ces seeds sont des nœuds volontaires de la communauté,
        PAS des serveurs contrôlés par des géants.
        """
        return [
            # Seeds communautaires OpenRed (à remplacer par des vrais)
            ("seed1.openred.community", 7777),
            ("seed2.openred.community", 7777), 
            ("seed3.openred.community", 7777),
            # Seeds communautaires secondaires
            ("openred-node1.community", 7777),
            ("openred-node2.community", 7777),
            # Bootstrap local par défaut
            ("127.0.0.1", 7777),
        ]
    
    def start(self):
        """Démarre le nœud DHT"""
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind(("0.0.0.0", self.port))
            print(f"🌐 DHT P2P démarré sur port {self.port}")
            print(f"🔑 Node ID: {self.node_id[:16]}...")
            
            # Thread d'écoute
            listen_thread = threading.Thread(target=self._listen_loop)
            listen_thread.daemon = True
            listen_thread.start()
            
            # Thread de maintenance
            maintenance_thread = threading.Thread(target=self._maintenance_loop)
            maintenance_thread.daemon = True
            maintenance_thread.start()
            
            # Bootstrap initial
            self._bootstrap()
            
        except Exception as e:
            print(f"❌ Erreur démarrage DHT: {e}")
            self.running = False
    
    def stop(self):
        """Arrête le nœud DHT"""
        self.running = False
        if self.socket:
            self.socket.close()
    
    def _listen_loop(self):
        """Boucle d'écoute des messages"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                self._handle_message(data, addr)
            except Exception as e:
                if self.running:
                    print(f"❌ Erreur réception: {e}")
                time.sleep(0.1)
    
    def _maintenance_loop(self):
        """Maintenance périodique du DHT"""
        while self.running:
            try:
                # Nettoie les entrées expirées
                self._cleanup_expired()
                
                # Ping des nœuds connus
                self._ping_nodes()
                
                # Re-publie nos forts
                self._republish_forts()
                
            except Exception as e:
                print(f"❌ Erreur maintenance: {e}")
            
            time.sleep(60)  # Maintenance toutes les minutes
    
    def _bootstrap(self):
        """Bootstrap initial avec les seeds"""
        print("🚀 Bootstrap DHT P2P...")
        
        for seed_host, seed_port in self.seeds:
            try:
                # Ping le seed
                self._send_ping(seed_host, seed_port)
                
                # Demande la liste des nœuds
                self._send_find_nodes(seed_host, seed_port, self.node_id)
                
            except Exception as e:
                print(f"⚠️  Seed {seed_host} injoignable: {e}")
                continue
        
        print(f"✅ Bootstrap terminé, {len(self.routing_table)} nœuds connus")
    
    def _handle_message(self, data: bytes, addr: Tuple[str, int]):
        """Traite un message reçu"""
        try:
            # Décode le message
            if len(data) < 4:
                return
                
            msg_type = struct.unpack("!I", data[:4])[0]
            payload = data[4:]
            
            if msg_type == 1:  # PING
                self._handle_ping(payload, addr)
            elif msg_type == 2:  # PONG  
                self._handle_pong(payload, addr)
            elif msg_type == 3:  # FIND_NODES
                self._handle_find_nodes(payload, addr)
            elif msg_type == 4:  # NODES_RESPONSE
                self._handle_nodes_response(payload, addr)
            elif msg_type == 5:  # STORE_FORT
                self._handle_store_fort(payload, addr)
            elif msg_type == 6:  # FIND_FORT
                self._handle_find_fort(payload, addr)
            elif msg_type == 7:  # FORT_RESPONSE
                self._handle_fort_response(payload, addr)
                
        except Exception as e:
            print(f"❌ Erreur traitement message de {addr}: {e}")
    
    def _send_ping(self, host: str, port: int):
        """Envoie un PING"""
        msg = struct.pack("!I", 1) + self.node_id.encode()
        try:
            self.socket.sendto(msg, (host, port))
        except:
            pass
    
    def _handle_ping(self, payload: bytes, addr: Tuple[str, int]):
        """Traite un PING"""
        try:
            node_id = payload.decode()
            # Ajoute à la table de routage
            self.routing_table[node_id] = addr
            
            # Répond avec PONG
            msg = struct.pack("!I", 2) + self.node_id.encode()
            self.socket.sendto(msg, addr)
            
        except:
            pass
    
    def _handle_pong(self, payload: bytes, addr: Tuple[str, int]):
        """Traite un PONG"""
        try:
            node_id = payload.decode()
            self.routing_table[node_id] = addr
        except:
            pass
    
    def _send_find_nodes(self, host: str, port: int, target_id: str):
        """Demande la liste des nœuds"""
        msg = struct.pack("!I", 3) + self.node_id.encode() + b"|" + target_id.encode()
        try:
            self.socket.sendto(msg, (host, port))
        except:
            pass
    
    def _handle_find_nodes(self, payload: bytes, addr: Tuple[str, int]):
        """Traite une demande de nœuds"""
        try:
            parts = payload.decode().split("|")
            requester_id = parts[0]
            target_id = parts[1]
            
            # Ajoute le demandeur
            self.routing_table[requester_id] = addr
            
            # Trouve les nœuds les plus proches
            closest_nodes = self._find_closest_nodes(target_id, 8)
            
            # Prépare la réponse
            nodes_data = []
            for node_id, (ip, port) in closest_nodes.items():
                nodes_data.append(f"{node_id}:{ip}:{port}")
            
            response = "|".join(nodes_data)
            msg = struct.pack("!I", 4) + response.encode()
            self.socket.sendto(msg, addr)
            
        except:
            pass
    
    def _handle_nodes_response(self, payload: bytes, addr: Tuple[str, int]):
        """Traite une réponse de nœuds"""
        try:
            response = payload.decode()
            if not response:
                return
                
            for node_str in response.split("|"):
                parts = node_str.split(":")
                if len(parts) == 3:
                    node_id, ip, port = parts
                    self.routing_table[node_id] = (ip, int(port))
                    
        except:
            pass
    
    def _find_closest_nodes(self, target_id: str, count: int = 8) -> Dict[str, Tuple[str, int]]:
        """Trouve les nœuds les plus proches d'un ID"""
        distances = []
        
        for node_id, addr in self.routing_table.items():
            # Distance XOR simplifiée
            dist = int(target_id[:16], 16) ^ int(node_id[:16], 16)
            distances.append((dist, node_id, addr))
        
        # Trie par distance et prend les plus proches
        distances.sort()
        
        result = {}
        for _, node_id, addr in distances[:count]:
            result[node_id] = addr
            
        return result
    
    def store_fort(self, fort_info: FortInfo):
        """Stocke un fort dans le DHT"""
        print(f"📡 Publication fort {fort_info.nom} dans DHT P2P...")
        
        # Stocke localement
        self.fort_storage[fort_info.fort_id] = fort_info
        
        # Propage vers les nœuds responsables
        target_nodes = self._find_closest_nodes(fort_info.fort_id, 3)
        
        for node_id, (ip, port) in target_nodes.items():
            try:
                msg = struct.pack("!I", 5) + fort_info.to_bytes()
                self.socket.sendto(msg, (ip, port))
            except:
                continue
    
    def _handle_store_fort(self, payload: bytes, addr: Tuple[str, int]):
        """Traite une demande de stockage de fort"""
        try:
            fort_info = FortInfo.from_bytes(payload)
            
            # Vérifie que l'info n'est pas trop ancienne
            if not fort_info.is_expired(48):  # 48h de TTL
                self.fort_storage[fort_info.fort_id] = fort_info
                print(f"💾 Fort {fort_info.nom} stocké depuis {addr[0]}")
                
        except Exception as e:
            print(f"❌ Erreur stockage fort: {e}")
    
    def find_fort(self, fort_id: str) -> Optional[FortInfo]:
        """Recherche un fort dans le DHT"""
        print(f"🔍 Recherche fort {fort_id[:16]}... dans DHT P2P")
        
        # Vérifie le cache local
        if fort_id in self.fort_storage:
            fort = self.fort_storage[fort_id]
            if not fort.is_expired():
                return fort
        
        # Demande aux nœuds responsables
        target_nodes = self._find_closest_nodes(fort_id, 5)
        
        for node_id, (ip, port) in target_nodes.items():
            try:
                msg = struct.pack("!I", 6) + self.node_id.encode() + b"|" + fort_id.encode()
                self.socket.sendto(msg, (ip, port))
            except:
                continue
        
        # Attend les réponses (simplification)
        time.sleep(2)
        
        # Vérifie si on a reçu le fort
        if fort_id in self.fort_storage:
            return self.fort_storage[fort_id]
        
        return None
    
    def _handle_find_fort(self, payload: bytes, addr: Tuple[str, int]):
        """Traite une recherche de fort"""
        try:
            parts = payload.decode().split("|")
            requester_id = parts[0]
            fort_id = parts[1]
            
            # Vérifie si on a le fort
            if fort_id in self.fort_storage:
                fort = self.fort_storage[fort_id]
                if not fort.is_expired():
                    # Renvoie le fort
                    msg = struct.pack("!I", 7) + fort.to_bytes()
                    self.socket.sendto(msg, addr)
                    
        except:
            pass
    
    def _handle_fort_response(self, payload: bytes, addr: Tuple[str, int]):
        """Traite une réponse de fort"""
        try:
            fort_info = FortInfo.from_bytes(payload)
            
            if not fort_info.is_expired():
                self.fort_storage[fort_info.fort_id] = fort_info
                print(f"📥 Fort {fort_info.nom} reçu de {addr[0]}")
                
        except:
            pass
    
    def _cleanup_expired(self):
        """Nettoie les entrées expirées"""
        expired_forts = []
        
        for fort_id, fort_info in self.fort_storage.items():
            if fort_info.is_expired():
                expired_forts.append(fort_id)
        
        for fort_id in expired_forts:
            del self.fort_storage[fort_id]
            
        if expired_forts:
            print(f"🧹 {len(expired_forts)} forts expirés nettoyés")
    
    def _ping_nodes(self):
        """Ping les nœuds connus pour maintenir la connectivité"""
        dead_nodes = []
        
        for node_id, (ip, port) in list(self.routing_table.items()):
            try:
                self._send_ping(ip, port)
                # Note: dans une vraie implémentation, il faudrait tracker les timeouts
            except:
                dead_nodes.append(node_id)
        
        # Nettoie les nœuds morts (simplification)
        for node_id in dead_nodes:
            if node_id in self.routing_table:
                del self.routing_table[node_id]
    
    def _republish_forts(self):
        """Re-publie nos forts pour maintenir leur disponibilité"""
        for fort_info in self.fort_storage.values():
            if not fort_info.is_expired():
                # Re-propage seulement si c'est "notre" fort
                # (dans une vraie implémentation, on trackera l'origine)
                pass
    
    def get_stats(self) -> Dict:
        """Statistiques du nœud DHT"""
        return {
            "node_id": self.node_id[:16] + "...",
            "routing_table_size": len(self.routing_table),
            "forts_stored": len(self.fort_storage),
            "active_forts": len([f for f in self.fort_storage.values() if not f.is_expired()]),
            "port": self.port,
            "running": self.running
        }


class GossipProtocol:
    """
    Protocole Gossip pour propagation d'informations
    
    Complément au DHT pour la diffusion rapide des nouveaux forts
    """
    
    def __init__(self, dht: DHTP2P):
        self.dht = dht
        self.gossip_cache: Set[str] = set()
        self.max_cache_size = 1000
    
    def gossip_fort(self, fort_info: FortInfo):
        """Propage un fort via gossip"""
        gossip_id = hashlib.sha256(f"{fort_info.fort_id}:{fort_info.timestamp}".encode()).hexdigest()
        
        if gossip_id in self.gossip_cache:
            return  # Déjà propagé
        
        self.gossip_cache.add(gossip_id)
        
        # Maintient la taille du cache
        if len(self.gossip_cache) > self.max_cache_size:
            # Supprime les plus anciens (simplification)
            self.gossip_cache = set(list(self.gossip_cache)[-self.max_cache_size//2:])
        
        # Propage à un sous-ensemble aléatoire de nœuds
        nodes = list(self.dht.routing_table.items())
        if len(nodes) > 5:
            nodes = random.sample(nodes, 5)
        
        gossip_msg = {
            "type": "gossip_fort",
            "fort": asdict(fort_info),
            "gossip_id": gossip_id,
            "ttl": 3  # Time To Live pour éviter les boucles
        }
        
        for node_id, (ip, port) in nodes:
            try:
                msg = struct.pack("!I", 8) + json.dumps(gossip_msg).encode()
                self.dht.socket.sendto(msg, (ip, port))
            except:
                continue


# Interface unifiée pour la découverte P2P
class DecouverteP2P:
    """
    Interface unifiée pour la découverte P2P 100% décentralisée
    
    Remplace COMPLÈTEMENT GitHub Registry et autres dépendances centralisées
    """
    
    def __init__(self, port: int = 7777):
        self.dht = DHTP2P(port)
        self.gossip = GossipProtocol(self.dht)
        
    def demarrer(self):
        """Démarre le système de découverte P2P"""
        print("🌐 === DÉCOUVERTE P2P DÉCENTRALISÉE ===")
        print("✅ Conforme au Manifeste OpenRed")
        print("❌ ZÉRO dépendance vers les géants")
        print("🔄 DHT + Gossip + Seeds distribués")
        print("=" * 40)
        
        self.dht.start()
    
    def arreter(self):
        """Arrête le système"""
        self.dht.stop()
    
    def publier_fort(self, fort_info: Dict):
        """Publie un fort dans le réseau P2P"""
        fort = FortInfo(
            fort_id=fort_info["fort_id"],
            nom=fort_info["nom"],
            ip_publique=fort_info["ip_publique"], 
            port=fort_info["port"],
            cle_publique=fort_info["cle_publique"],
            timestamp=time.time()
        )
        
        # Stocke dans DHT
        self.dht.store_fort(fort)
        
        # Propage via gossip
        self.gossip.gossip_fort(fort)
        
        print(f"📡 Fort {fort.nom} publié dans le réseau P2P décentralisé")
    
    def rechercher_fort(self, fort_id: str) -> Optional[Dict]:
        """Recherche un fort dans le réseau P2P"""
        fort = self.dht.find_fort(fort_id)
        
        if fort:
            return {
                "fort_id": fort.fort_id,
                "nom": fort.nom,
                "ip_publique": fort.ip_publique,
                "port": fort.port,
                "cle_publique": fort.cle_publique,
                "timestamp": fort.timestamp
            }
        
        return None
    
    def lister_forts_actifs(self) -> List[Dict]:
        """Liste les forts actifs connus"""
        forts = []
        
        for fort in self.dht.fort_storage.values():
            if not fort.is_expired():
                forts.append({
                    "fort_id": fort.fort_id,
                    "nom": fort.nom,
                    "ip_publique": fort.ip_publique,
                    "port": fort.port,
                    "timestamp": fort.timestamp
                })
        
        return forts
    
    def get_statistiques(self) -> Dict:
        """Statistiques du réseau P2P"""
        return {
            "dht": self.dht.get_stats(),
            "forts_actifs": len([f for f in self.dht.fort_storage.values() if not f.is_expired()]),
            "forts_totaux": len(self.dht.fort_storage),
            "cache_gossip": len(self.gossip.gossip_cache)
        }


if __name__ == "__main__":
    # Test du système P2P
    print("🧪 === TEST DHT P2P DÉCENTRALISÉ ===")
    
    decouverte = DecouverteP2P()
    decouverte.demarrer()
    
    # Simule un fort
    fort_test = {
        "fort_id": "test_fort_" + hashlib.sha256(b"test").hexdigest()[:16],
        "nom": "Fort Test P2P",
        "ip_publique": "192.168.1.100",
        "port": 8080,
        "cle_publique": "test_key_" + hashlib.sha256(b"key").hexdigest()
    }
    
    # Publie le fort
    decouverte.publier_fort(fort_test)
    
    # Statistiques
    stats = decouverte.get_statistiques()
    print(f"\n📊 Statistiques P2P:")
    print(f"   Nœuds connus: {stats['dht']['routing_table_size']}")
    print(f"   Forts actifs: {stats['forts_actifs']}")
    print(f"   Port DHT: {stats['dht']['port']}")
    
    # Garde actif pour tests
    try:
        print("\n⏳ Système P2P actif (Ctrl+C pour arrêter)")
        while True:
            time.sleep(10)
            stats = decouverte.get_statistiques()
            print(f"🔄 Nœuds: {stats['dht']['routing_table_size']}, Forts: {stats['forts_actifs']}")
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du système P2P")
        decouverte.arreter()