#!/usr/bin/env python3
"""
🌐 O-Red P2P Discovery Wrapper
Wrapper simplifié pour compatibilité avec le système asymétrique

Auteur : Système OpenRed P2P Révolutionnaire  
Date : Septembre 2025
"""

import socket
import json
import threading
import time
import secrets
from typing import Dict, Any, Optional
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

class O_RedSearch_P2P:
    """
    🔍 Découverte P2P simplifiée pour système asymétrique
    
    Wrapper compatible avec l'architecture révolutionnaire
    """
    
    MULTICAST_GROUP = "224.0.1.100"
    MULTICAST_PORT = 5354
    
    def __init__(self, node_id: str, display_name: str, port: int):
        """
        Initialiser la découverte P2P
        
        Args:
            node_id: Identifiant unique du nœud
            display_name: Nom d'affichage du nœud
            port: Port d'écoute du nœud
        """
        self.node_id = node_id
        self.display_name = display_name
        self.port = port
        
        # Générer identité cryptographique
        self._generate_identity()
        
        # État de découverte
        self.discovered_peers = {}
        self.running = False
        
        # Sockets multicast
        self.broadcast_socket = None
        self.listen_socket = None
        
        print(f"🔍 [DISCOVERY] Initialisé pour {display_name}")
        print(f"🆔 Node ID : {node_id}")
        print(f"🌐 Port : {port}")
    
    def _generate_identity(self):
        """🔐 Générer l'identité cryptographique du nœud"""
        # Générer paire de clés RSA principale
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Identité complète
        self.identity = {
            "node_id": self.node_id,
            "private_key": private_key,
            "public_key": public_key
        }
        
        # Empreinte publique
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Fingerprint pour identification
        import hashlib
        self.fingerprint = hashlib.sha256(public_pem).hexdigest()[:16]
        
        print(f"🔐 [IDENTITY] Fingerprint : {self.fingerprint}")
    
    async def start_discovery(self):
        """🚀 Démarrer la découverte multicast"""
        print("🚀 [DISCOVERY] Démarrage de la découverte P2P")
        
        self.running = True
        
        # Démarrer l'écoute en arrière-plan
        listen_thread = threading.Thread(target=self._listen_for_peers, daemon=True)
        listen_thread.start()
        
        # Démarrer la diffusion en arrière-plan
        broadcast_thread = threading.Thread(target=self._broadcast_presence, daemon=True)
        broadcast_thread.start()
        
        print(f"📡 [DISCOVERY] Écoute sur {self.MULTICAST_GROUP}:{self.MULTICAST_PORT}")
        print("🔍 [DISCOVERY] Diffusion de présence activée")
        
        # Maintenir la découverte active
        while self.running:
            await asyncio.sleep(1)
    
    def _listen_for_peers(self):
        """👂 Écouter les annonces de pairs"""
        try:
            # Créer socket d'écoute multicast
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind sur toutes les interfaces
            self.listen_socket.bind(('', self.MULTICAST_PORT))
            
            # Rejoindre le groupe multicast
            mreq = socket.inet_aton(self.MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
            self.listen_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            print(f"👂 [LISTEN] Écoute multicast active")
            
            while self.running:
                try:
                    data, addr = self.listen_socket.recvfrom(1024)
                    self._process_peer_announcement(data.decode(), addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"❌ [LISTEN] Erreur : {str(e)}")
                        
        except Exception as e:
            print(f"❌ [LISTEN] Erreur socket : {str(e)}")
    
    def _broadcast_presence(self):
        """📡 Diffuser notre présence"""
        try:
            # Créer socket de diffusion
            self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.broadcast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            
            while self.running:
                # Créer annonce
                announcement = {
                    "type": "peer_announcement",
                    "node_id": self.node_id,
                    "display_name": self.display_name,
                    "port": self.port,
                    "fingerprint": self.fingerprint,
                    "timestamp": time.time(),
                    "services": ["asymmetric_tokens", "secure_p2p"],
                    "version": "1.0"
                }
                
                # Envoyer via multicast
                announcement_data = json.dumps(announcement).encode()
                self.broadcast_socket.sendto(
                    announcement_data,
                    (self.MULTICAST_GROUP, self.MULTICAST_PORT)
                )
                
                # Attendre avant prochaine annonce
                time.sleep(30)  # Annonce toutes les 30 secondes
                
        except Exception as e:
            print(f"❌ [BROADCAST] Erreur : {str(e)}")
    
    def _process_peer_announcement(self, data: str, addr):
        """📨 Traiter une annonce de pair"""
        try:
            announcement = json.loads(data)
            
            # Ignorer nos propres annonces
            if announcement.get("node_id") == self.node_id:
                return
            
            # Ignorer si pas une annonce de pair
            if announcement.get("type") != "peer_announcement":
                return
            
            peer_id = announcement.get("node_id")
            if not peer_id:
                return
            
            # Mettre à jour les pairs découverts
            peer_info = {
                "node_id": peer_id,
                "display_name": announcement.get("display_name", peer_id),
                "address": addr[0],
                "port": announcement.get("port"),
                "fingerprint": announcement.get("fingerprint"),
                "services": announcement.get("services", []),
                "last_seen": datetime.utcnow().isoformat(),
                "version": announcement.get("version", "unknown")
            }
            
            # Nouveau pair découvert
            if peer_id not in self.discovered_peers:
                print(f"🆕 [PEER] Découvert : {peer_info['display_name']} ({peer_id})")
                print(f"   📍 Adresse : {addr[0]}:{peer_info['port']}")
                print(f"   🔐 Fingerprint : {peer_info['fingerprint']}")
            
            self.discovered_peers[peer_id] = peer_info
            
        except json.JSONDecodeError:
            pass  # Ignorer les données malformées
        except Exception as e:
            print(f"❌ [PROCESS] Erreur : {str(e)}")
    
    def stop_discovery(self):
        """🛑 Arrêter la découverte"""
        print("🛑 [DISCOVERY] Arrêt de la découverte P2P")
        
        self.running = False
        
        if self.listen_socket:
            self.listen_socket.close()
            
        if self.broadcast_socket:
            self.broadcast_socket.close()
    
    def get_discovered_peers(self) -> Dict[str, Dict[str, Any]]:
        """📋 Obtenir la liste des pairs découverts"""
        return self.discovered_peers.copy()
    
    def get_peer_count(self) -> int:
        """🔢 Obtenir le nombre de pairs découverts"""
        return len(self.discovered_peers)


# Import asyncio pour compatibilité
import asyncio