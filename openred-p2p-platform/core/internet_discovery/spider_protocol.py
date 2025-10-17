# === OpenRed Internet Spider Protocol ===
# Découverte automatique de nœuds P2P sur Internet
# Scanning intelligent + échange viral de listes de nœuds

import socket
import json
import threading
import time
import random
import asyncio
import ipaddress
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import struct

@dataclass
class InternetNode:
    """Nœud OpenRed découvert sur Internet"""
    fingerprint: str
    ip: str
    port: int
    node_id: str
    last_seen: float
    first_discovered: float
    trust_score: float  # 0.0 à 1.0
    response_time: float  # millisecondes
    verified: bool
    discovery_method: str  # "scan", "exchange", "manual"
    
@dataclass
class SpiderHandshake:
    """Handshake rapide pour identification OpenRed"""
    protocol: str = "OpenRed-Spider-v1"
    fingerprint: str = ""
    node_id: str = ""
    timestamp: float = 0.0
    request_type: str = ""  # "discover", "exchange", "ping"
    signature: str = ""

class InternetSpiderProtocol:
    """
    Protocole Spider pour découverte automatique Internet
    - Scanning intelligent d'IP publiques
    - Détection par signature cryptographique
    - Échange viral de listes de nœuds
    """
    
    def __init__(self, lighthouse_protocol, security_protocol):
        self.lighthouse = lighthouse_protocol
        self.security = security_protocol
        self.running = False
        
        # Base de données des nœuds Internet
        self.internet_nodes: Dict[str, InternetNode] = {}
        self.scan_history: Set[str] = set()  # IPs déjà scannées
        
        # Configuration scanning
        self.scan_threads = 3  # Threads de scanning parallèles
        self.scan_rate_limit = 0.1  # Secondes entre scans
        self.discovery_port_range = [8080, 8081, 8082, 8083]  # Ports OpenRed courants
        
        # Statistiques
        self.stats = {
            "scans_performed": 0,
            "nodes_discovered": 0,
            "lists_exchanged": 0,
            "last_discovery": 0.0
        }
        
        print("🕷️ Internet Spider Protocol initialized")
        
    def start_spider(self):
        """Démarre le protocole spider"""
        if self.running:
            return
            
        self.running = True
        
        # Thread de scanning automatique
        self.scanner_thread = threading.Thread(
            target=self._auto_scanner,
            daemon=True
        )
        self.scanner_thread.start()
        
        # Thread de maintenance
        self.maintenance_thread = threading.Thread(
            target=self._maintenance_loop,
            daemon=True
        )
        self.maintenance_thread.start()
        
        print("🕷️ Internet Spider started - Hunting for nodes...")
        
    def stop_spider(self):
        """Arrête le protocole spider"""
        self.running = False
        print("🕷️ Internet Spider stopped")
        
    def _auto_scanner(self):
        """Scanner automatique d'IP Internet"""
        while self.running:
            try:
                # Générer une IP publique aléatoire intelligente
                target_ip = self._generate_smart_ip()
                
                if target_ip and target_ip not in self.scan_history:
                    self._scan_ip(target_ip)
                    self.scan_history.add(target_ip)
                    
                    # Limite de taille de l'historique
                    if len(self.scan_history) > 100000:
                        # Garder seulement les plus récents
                        self.scan_history = set(list(self.scan_history)[-50000:])
                
                # Rate limiting
                time.sleep(self.scan_rate_limit)
                
            except Exception as e:
                print(f"🕷️ Scanner error: {e}")
                time.sleep(1)
                
    def _generate_smart_ip(self) -> Optional[str]:
        """Génère une IP publique intelligente à scanner"""
        try:
            # Éviter les plages privées et réservées
            while True:
                # Générer IP aléatoire
                ip_bytes = struct.pack('>I', random.randint(1, 0xFFFFFFFF))
                ip = socket.inet_ntoa(ip_bytes)
                ip_obj = ipaddress.IPv4Address(ip)
                
                # Vérifier que c'est une IP publique
                if (ip_obj.is_global and 
                    not ip_obj.is_multicast and 
                    not ip_obj.is_reserved and
                    not ip_obj.is_loopback):
                    return ip
                    
        except Exception:
            return None
            
    def _scan_ip(self, ip: str):
        """Scanne une IP pour détecter un nœud OpenRed"""
        for port in self.discovery_port_range:
            try:
                if self._quick_openred_check(ip, port):
                    print(f"🎯 Potential OpenRed node found: {ip}:{port}")
                    self._attempt_discovery_handshake(ip, port)
                    
            except Exception:
                pass  # Échec silencieux pour la discrétion
                
        self.stats["scans_performed"] += 1
        
    def _quick_openred_check(self, ip: str, port: int, timeout: float = 2.0) -> bool:
        """Vérification rapide si c'est un nœud OpenRed"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Tentative de connexion
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                # Port ouvert, tenter handshake OpenRed
                return self._test_openred_signature(ip, port)
                
        except Exception:
            pass
            
        return False
        
    def _test_openred_signature(self, ip: str, port: int) -> bool:
        """Test rapide de signature OpenRed"""
        try:
            # Envoyer handshake spider rapide
            handshake = SpiderHandshake(
                fingerprint=self.lighthouse.fingerprint,
                node_id=self.lighthouse.node_id,
                timestamp=time.time(),
                request_type="discover"
            )
            
            # TODO: Signer le handshake
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            sock.connect((ip, port))
            
            # Envoyer requête de découverte
            message = json.dumps(asdict(handshake)).encode('utf-8')
            sock.send(len(message).to_bytes(4, 'big'))
            sock.send(message)
            
            # Attendre réponse
            response_size = int.from_bytes(sock.recv(4), 'big')
            if response_size > 0 and response_size < 10000:
                response_data = sock.recv(response_size)
                response = json.loads(response_data.decode('utf-8'))
                
                # Vérifier si c'est un nœud OpenRed valide
                if (response.get("protocol") == "OpenRed-Spider-v1" and
                    response.get("fingerprint") and
                    response.get("node_id")):
                    return True
                    
            sock.close()
            
        except Exception:
            pass
            
        return False
        
    def _attempt_discovery_handshake(self, ip: str, port: int):
        """Tente un handshake complet avec échange de listes"""
        try:
            start_time = time.time()
            
            # Handshake complet
            handshake = SpiderHandshake(
                fingerprint=self.lighthouse.fingerprint,
                node_id=self.lighthouse.node_id,
                timestamp=time.time(),
                request_type="exchange"
            )
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((ip, port))
            
            # Envoyer requête d'échange
            message = json.dumps({
                "handshake": asdict(handshake),
                "my_nodes": self._get_shareable_nodes()
            }).encode('utf-8')
            
            sock.send(len(message).to_bytes(4, 'big'))
            sock.send(message)
            
            # Recevoir réponse
            response_size = int.from_bytes(sock.recv(4), 'big')
            if response_size > 0 and response_size < 100000:  # Limite raisonnable
                response_data = sock.recv(response_size)
                response = json.loads(response_data.decode('utf-8'))
                
                # Traitement de la réponse
                if response.get("status") == "success":
                    response_time = (time.time() - start_time) * 1000
                    
                    # Ajouter le nœud découvert
                    node = InternetNode(
                        fingerprint=response["fingerprint"],
                        ip=ip,
                        port=port,
                        node_id=response["node_id"],
                        last_seen=time.time(),
                        first_discovered=time.time(),
                        trust_score=0.5,  # Score initial
                        response_time=response_time,
                        verified=True,
                        discovery_method="scan"
                    )
                    
                    self.internet_nodes[response["fingerprint"]] = node
                    self.stats["nodes_discovered"] += 1
                    self.stats["last_discovery"] = time.time()
                    
                    # Traiter les nœuds reçus
                    if "their_nodes" in response:
                        self._process_received_nodes(response["their_nodes"])
                        self.stats["lists_exchanged"] += 1
                        
                    print(f"🌟 New OpenRed node added: {response['node_id']} ({ip}:{port})")
                    print(f"📊 Total internet nodes: {len(self.internet_nodes)}")
                    
            sock.close()
            
        except Exception as e:
            print(f"🕷️ Handshake failed {ip}:{port} - {e}")
            
    def _get_shareable_nodes(self) -> List[Dict]:
        """Retourne la liste des nœuds partageables"""
        # Partager les nœuds vérifiés et récents
        shareable = []
        cutoff_time = time.time() - (24 * 3600)  # 24h
        
        for node in self.internet_nodes.values():
            if (node.verified and 
                node.last_seen > cutoff_time and 
                node.trust_score > 0.3):
                shareable.append({
                    "fingerprint": node.fingerprint,
                    "ip": node.ip,
                    "port": node.port,
                    "node_id": node.node_id,
                    "trust_score": node.trust_score
                })
                
        return shareable[:100]  # Limite à 100 nœuds
        
    def _process_received_nodes(self, received_nodes: List[Dict]):
        """Traite les nœuds reçus d'un autre nœud"""
        for node_data in received_nodes:
            fingerprint = node_data.get("fingerprint")
            
            if fingerprint and fingerprint not in self.internet_nodes:
                # Nouveau nœud reçu
                node = InternetNode(
                    fingerprint=fingerprint,
                    ip=node_data["ip"],
                    port=node_data["port"],
                    node_id=node_data["node_id"],
                    last_seen=0.0,  # Pas encore contacté
                    first_discovered=time.time(),
                    trust_score=max(0.1, node_data.get("trust_score", 0.3) * 0.8),  # Score réduit
                    response_time=0.0,
                    verified=False,  # À vérifier
                    discovery_method="exchange"
                )
                
                self.internet_nodes[fingerprint] = node
                print(f"📨 Received node: {node.node_id} ({node.ip}:{node.port})")
                
    def _maintenance_loop(self):
        """Boucle de maintenance des nœuds"""
        while self.running:
            try:
                self._verify_nodes()
                self._cleanup_old_nodes()
                time.sleep(300)  # Maintenance toutes les 5 minutes
                
            except Exception as e:
                print(f"🕷️ Maintenance error: {e}")
                time.sleep(60)
                
    def _verify_nodes(self):
        """Vérifie la validité des nœuds stockés"""
        for fingerprint, node in list(self.internet_nodes.items()):
            if not node.verified or (time.time() - node.last_seen) > 3600:  # 1h
                # Tenter une vérification
                if self._quick_openred_check(node.ip, node.port):
                    node.last_seen = time.time()
                    node.verified = True
                    node.trust_score = min(1.0, node.trust_score + 0.1)
                else:
                    node.trust_score -= 0.2
                    if node.trust_score <= 0:
                        del self.internet_nodes[fingerprint]
                        
    def _cleanup_old_nodes(self):
        """Nettoie les vieux nœuds"""
        cutoff_time = time.time() - (7 * 24 * 3600)  # 7 jours
        
        to_remove = []
        for fingerprint, node in self.internet_nodes.items():
            if node.last_seen < cutoff_time and node.trust_score < 0.3:
                to_remove.append(fingerprint)
                
        for fingerprint in to_remove:
            del self.internet_nodes[fingerprint]
            
    def get_stats(self) -> Dict:
        """Retourne les statistiques du spider"""
        return {
            **self.stats,
            "total_nodes": len(self.internet_nodes),
            "verified_nodes": sum(1 for n in self.internet_nodes.values() if n.verified),
            "high_trust_nodes": sum(1 for n in self.internet_nodes.values() if n.trust_score > 0.7)
        }
        
    def get_internet_nodes(self) -> List[InternetNode]:
        """Retourne la liste des nœuds Internet découverts"""
        return list(self.internet_nodes.values())