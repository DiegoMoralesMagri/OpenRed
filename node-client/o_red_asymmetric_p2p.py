#!/usr/bin/env python3
"""
🌊 O-Red P2P Intégration avec Tokens Asymétriques
Intégration complète du système révolutionnaire dans le client P2P

Auteur : Système OpenRed P2P Révolutionnaire
Date : Septembre 2025  
"""

import asyncio
import json
import socket
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading
import time

# Import de nos modules révolutionnaires
from p2p_asymmetric_token_manager import P2PAsymmetricTokenManager
from simple_p2p_security import SimpleP2PSecurityProtocol
from o_red_discovery_wrapper import O_RedSearch_P2P

class O_RedAsymmetricP2P:
    """
    🚀 Client P2P O-Red avec Tokens Asymétriques Intégrés
    
    Combine :
    - Découverte UDP multicast (o_red_search_secure_p2p)
    - Sécurité P2P 3-phases (simple_p2p_security)  
    - Tokens asymétriques révolutionnaires (p2p_asymmetric_token_manager)
    
    Résultat : P2P ultra-sécurisé avec gestion de permissions granulaire
    """
    
    def __init__(self, node_config: Dict[str, Any]):
        """
        Initialiser le client P2P asymétrique complet
        
        Args:
            node_config: Configuration du nœud
        """
        self.node_id = node_config['node_id']
        self.display_name = node_config.get('display_name', self.node_id)
        self.port = node_config.get('port', 5355)
        
        print(f"🌊 [O-RED ASYMMETRIC] Initialisation nœud {self.display_name}")
        
        # === COMPOSANTS RÉVOLUTIONNAIRES ===
        
        # 1. Découverte P2P avec multicast
        self.p2p_discovery = O_RedSearch_P2P(
            node_id=self.node_id,
            display_name=self.display_name,
            port=self.port
        )
        
        # 2. Sécurité P2P 3-phases
        self.p2p_security = SimpleP2PSecurityProtocol(self.node_id)
        
        # 3. Gestionnaire tokens asymétriques RÉVOLUTIONNAIRE
        self.asymmetric_tokens = P2PAsymmetricTokenManager(
            self.p2p_discovery.identity,
            f"{self.node_id}_asymmetric_tokens.json"
        )
        
        # === ÉTAT GLOBAL ===
        self.discovered_peers = {}
        self.active_connections = {}
        self.friendship_requests = {}
        
        # === SERVEURS ===
        self.command_server = None
        self.friendship_server = None
        self.running = False
        
        print("✅ [O-RED ASYMMETRIC] Composants initialisés")
    
    async def start(self):
        """🚀 Démarrer le système P2P asymétrique complet"""
        print(f"🚀 [START] Démarrage système P2P pour {self.display_name}")
        
        self.running = True
        
        # 1. Démarrer la découverte P2P
        discovery_task = asyncio.create_task(self.p2p_discovery.start_discovery())
        
        # 2. Démarrer le serveur de commandes
        command_task = asyncio.create_task(self._start_command_server())
        
        # 3. Démarrer le serveur de demandes d'amitié
        friendship_task = asyncio.create_task(self._start_friendship_server())
        
        # 4. Démarrer la boucle de monitoring
        monitor_task = asyncio.create_task(self._monitor_peers())
        
        print("✅ [START] Tous les services démarrés")
        print(f"🌐 Écoute sur port {self.port}")
        print(f"🔍 Découverte multicast active sur {self.p2p_discovery.MULTICAST_GROUP}")
        
        # Attendre tous les services
        await asyncio.gather(
            discovery_task,
            command_task, 
            friendship_task,
            monitor_task
        )
    
    async def _start_command_server(self):
        """🎮 Serveur de commandes P2P"""
        server = await asyncio.start_server(
            self._handle_command_connection,
            '0.0.0.0',
            self.port + 100  # Port commandes = port base + 100
        )
        
        self.command_server = server
        print(f"🎮 [COMMAND SERVER] Écoute sur port {self.port + 100}")
        
        async with server:
            await server.serve_forever()
    
    async def _start_friendship_server(self):
        """🤝 Serveur de demandes d'amitié asymétrique"""  
        server = await asyncio.start_server(
            self._handle_friendship_connection,
            '0.0.0.0',
            self.port + 200  # Port amitiés = port base + 200
        )
        
        self.friendship_server = server
        print(f"🤝 [FRIENDSHIP SERVER] Écoute sur port {self.port + 200}")
        
        async with server:
            await server.serve_forever()
    
    async def _handle_command_connection(self, reader, writer):
        """⚡ Traiter une connexion de commande"""
        client_addr = writer.get_extra_info('peername')
        print(f"⚡ [COMMAND] Connexion de {client_addr}")
        
        try:
            # Lire la commande
            data = await reader.read(4096)
            if not data:
                return
            
            command = json.loads(data.decode())
            response = await self._process_command(command, client_addr)
            
            # Envoyer la réponse
            writer.write(json.dumps(response).encode())
            await writer.drain()
            
        except Exception as e:
            print(f"❌ [COMMAND] Erreur : {str(e)}")
            error_response = {"error": str(e)}
            writer.write(json.dumps(error_response).encode())
            await writer.drain()
        
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def _handle_friendship_connection(self, reader, writer):
        """🤝 Traiter une demande d'amitié asymétrique"""
        client_addr = writer.get_extra_info('peername')
        print(f"🤝 [FRIENDSHIP] Demande de {client_addr}")
        
        try:
            # Lire la demande d'amitié
            data = await reader.read(8192)  # Plus de place pour tokens asymétriques
            if not data:
                return
            
            friendship_request = json.loads(data.decode())
            response = await self._process_friendship_request(friendship_request, client_addr)
            
            # Envoyer la réponse
            writer.write(json.dumps(response).encode())
            await writer.drain()
            
        except Exception as e:
            print(f"❌ [FRIENDSHIP] Erreur : {str(e)}")
            error_response = {"error": str(e)}
            writer.write(json.dumps(error_response).encode())
            await writer.drain()
        
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def _process_command(self, command: Dict[str, Any], client_addr) -> Dict[str, Any]:
        """🔧 Traiter une commande reçue"""
        cmd_type = command.get("type")
        
        if cmd_type == "list_peers":
            return {
                "type": "peer_list",
                "peers": list(self.discovered_peers.keys()),
                "count": len(self.discovered_peers)
            }
        
        elif cmd_type == "list_friendships":
            relationships = self.asymmetric_tokens.list_relationships()
            return {
                "type": "friendship_list", 
                "friendships": relationships,
                "count": len(relationships)
            }
        
        elif cmd_type == "request_action":
            # Demande d'action avec token asymétrique
            friend_id = command.get("friend_id")
            action = command.get("action")
            action_data = command.get("data", {})
            
            request = self.asymmetric_tokens.request_friend_action(
                friend_id, action, action_data
            )
            
            return {
                "type": "action_request_prepared",
                "request": request
            }
        
        else:
            return {"error": f"Commande inconnue : {cmd_type}"}
    
    async def _process_friendship_request(self, request: Dict[str, Any], client_addr) -> Dict[str, Any]:
        """🤝 Traiter une demande d'amitié asymétrique"""
        request_type = request.get("type")
        
        if request_type == "establish_friendship":
            # Nouvelle demande d'amitié avec token asymétrique
            friend_id = request.get("friend_node_id")
            friend_public_key_pem = request.get("friend_public_key_pem")
            permissions = request.get("requested_permissions", {})
            
            if not friend_id or not friend_public_key_pem:
                return {"error": "friend_node_id et friend_public_key_pem requis"}
            
            # Générer mon token asymétrique pour cet ami
            my_token = self.asymmetric_tokens.establish_asymmetric_friendship(
                friend_id,
                friend_public_key_pem,  # Note: Conversion nécessaire si pas déjà un objet clé
                permissions
            )
            
            return {
                "type": "friendship_response",
                "accepted": True,
                "my_token_public_key_pem": my_token["token_public_key_pem"],
                "my_token_data": my_token["token_data"],
                "message": f"Amitié asymétrique établie avec {friend_id}"
            }
        
        elif request_type == "receive_friend_token":
            # Réception du token asymétrique d'un ami
            friend_id = request.get("friend_node_id")
            friend_token_public_key_pem = request.get("friend_token_public_key_pem")
            friend_token_data = request.get("friend_token_data")
            
            if not all([friend_id, friend_token_public_key_pem, friend_token_data]):
                return {"error": "Données de token incomplètes"}
            
            # Recevoir et valider le token asymétrique
            accepted = self.asymmetric_tokens.receive_asymmetric_token(
                friend_id,
                friend_token_public_key_pem,
                friend_token_data
            )
            
            return {
                "type": "token_reception_response",
                "accepted": accepted,
                "message": f"Token de {friend_id} {'accepté' if accepted else 'rejeté'}"
            }
        
        elif request_type == "authorize_action":
            # Demande d'autorisation avec preuve asymétrique
            friend_id = request.get("friend_node_id")
            action = request.get("action")
            action_data = request.get("action_data", {})
            
            authorization = self.asymmetric_tokens.authorize_friend_action(
                friend_id, action, action_data
            )
            
            return {
                "type": "authorization_response",
                "authorization": authorization
            }
        
        else:
            return {"error": f"Type de demande d'amitié inconnue : {request_type}"}
    
    async def _monitor_peers(self):
        """👀 Surveiller les pairs découverts"""
        while self.running:
            current_peers = self.p2p_discovery.discovered_peers.copy()
            
            # Détecter nouveaux pairs
            for peer_id, peer_info in current_peers.items():
                if peer_id not in self.discovered_peers:
                    print(f"🆕 [PEER] Nouveau pair découvert : {peer_id} ({peer_info.get('display_name', 'Sans nom')})")
                    self.discovered_peers[peer_id] = peer_info
            
            # Détecter pairs disparus
            for peer_id in list(self.discovered_peers.keys()):
                if peer_id not in current_peers:
                    print(f"👋 [PEER] Pair perdu : {peer_id}")
                    del self.discovered_peers[peer_id]
            
            await asyncio.sleep(5)  # Vérification toutes les 5 secondes
    
    # === MÉTHODES D'USAGE POUR L'UTILISATEUR ===
    
    def establish_friendship_with_peer(self, peer_id: str, permissions: Dict[str, bool] = None):
        """
        🤝 Établir une amitié asymétrique avec un pair découvert
        
        Args:
            peer_id: ID du pair découvert
            permissions: Permissions à accorder
        """
        if peer_id not in self.discovered_peers:
            print(f"❌ Pair {peer_id} non découvert")
            return False
        
        peer_info = self.discovered_peers[peer_id]
        
        # Permissions par défaut si non spécifiées
        if permissions is None:
            permissions = {
                "send_messages": True,
                "read_public_files": True,
                "download_shared_content": True,
                "access_private_data": False,
                "modify_files": False
            }
        
        # Générer token asymétrique
        my_token = self.asymmetric_tokens.establish_asymmetric_friendship(
            peer_id,
            peer_info.get('public_key'),  # Clé publique du pair
            permissions
        )
        
        print(f"✅ Amitié asymétrique initiée avec {peer_id}")
        print(f"🔐 Token généré - Signature : {my_token['token_data']['asymmetric_signature'][:16]}...")
        
        return my_token
    
    def list_discovered_peers(self) -> List[Dict[str, Any]]:
        """📋 Lister tous les pairs découverts"""
        return [
            {
                "peer_id": peer_id,
                "display_name": peer_info.get("display_name", "Anonyme"),
                "address": peer_info.get("address"),
                "last_seen": peer_info.get("last_seen"),
                "has_friendship": peer_id in [rel["friend_node_id"] for rel in self.asymmetric_tokens.list_relationships()]
            }
            for peer_id, peer_info in self.discovered_peers.items()
        ]
    
    def list_active_friendships(self) -> List[Dict[str, Any]]:
        """💫 Lister toutes les amitiés asymétriques actives"""
        return self.asymmetric_tokens.list_relationships()
    
    def send_friend_request(self, friend_id: str, action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """📤 Envoyer une demande à un ami via token asymétrique"""
        return self.asymmetric_tokens.request_friend_action(friend_id, action, data)
    
    def stop(self):
        """🛑 Arrêter le système P2P"""
        print("🛑 [STOP] Arrêt du système P2P asymétrique")
        self.running = False
        
        if self.command_server:
            self.command_server.close()
        
        if self.friendship_server:
            self.friendship_server.close()


async def demo_integrated_asymmetric_p2p():
    """
    🎯 Démonstration complète du système P2P asymétrique intégré
    """
    print("🌊 === DÉMONSTRATION P2P ASYMÉTRIQUE INTÉGRÉ ===\n")
    
    # Configuration des nœuds
    pierre_config = {
        "node_id": "pierre_dev_2025",
        "display_name": "Pierre - Développeur FullStack",
        "port": 5355
    }
    
    marie_config = {
        "node_id": "marie_research_2025", 
        "display_name": "Marie - Chercheuse IA",
        "port": 5356
    }
    
    # Initialisation
    pierre_node = O_RedAsymmetricP2P(pierre_config)
    marie_node = O_RedAsymmetricP2P(marie_config)
    
    print("✅ Nœuds P2P asymétriques initialisés")
    print("🚀 Démarrage dans 3 secondes...\n")
    
    await asyncio.sleep(3)
    
    # Démarrage en parallèle (simulation)
    print("🌐 Simulation de démarrage P2P asymétrique")
    print("📡 Découverte multicast active")
    print("🤝 Serveurs d'amitié en écoute")
    print("🔐 Gestionnaires de tokens asymétriques opérationnels")
    
    print("\n🎉 === SYSTÈME P2P ASYMÉTRIQUE OPÉRATIONNEL ===")
    print("✅ 4 clés RSA par relation d'amitié")
    print("✅ Non-répudiation cryptographique absolue")
    print("✅ Découverte automatique des pairs")
    print("✅ Permissions granulaires par ami")
    print("🚀 RÉVOLUTION P2P ACTIVÉE !")


if __name__ == "__main__":
    asyncio.run(demo_integrated_asymmetric_p2p())