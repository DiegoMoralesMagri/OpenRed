# === OpenRed P2P Platform : Nœud Autonome Révolutionnaire ===
# Architecture 100% P2P Pure avec Schrödinger Phoenix URN
# Découverte automatique "Phare dans la Nuit" + Sécurité 3 Phases

import os
import sys
import json
import time
import asyncio
import threading
import argparse
import socket
from typing import Dict, Optional
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# Import des composants P2P révolutionnaires
from core.udp_discovery.lighthouse_protocol import LighthouseProtocol
from core.p2p_security.three_phase_protocol import ThreePhaseHandshake, DirectP2PConnection
from core.schrodinger_phoenix.p2p_distribution import P2PPhantomUrnEngine, P2PUrnDistributionManager

# Pas d'import direct du protocole simple ici pour éviter import circulaire

class OpenRedP2PNode:
    """
    Nœud OpenRed P2P Autonome Révolutionnaire
    - Découverte automatique UDP multicast
    - Sécurité P2P 3 phases (REQUEST/VERIFY/FINALIZE)
    - Distribution URN/Phantom avec Schrödinger Phoenix
    - Communications directes sans API centrale
    """
    
    def __init__(self, node_id: str, sector: str = "general", p2p_port: int = 8080, profile_manager=None):
        self.node_id = node_id
        self.sector = sector
        self.p2p_port = p2p_port
        self.profile_manager = profile_manager
        
        # Génération clés cryptographiques RSA 2048
        print("🔐 Generating RSA 2048 cryptographic keys...")
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # Initialisation composants P2P avec gestionnaire de profil
        self.lighthouse = LighthouseProtocol(
            node_id=node_id,
            private_key=self.private_key,
            public_key=self.public_key,
            sector=sector,
            profile_manager=profile_manager
        )
        
        self.security_protocol = ThreePhaseHandshake(
            node_fingerprint=self.lighthouse.fingerprint,
            private_key=self.private_key,
            public_key=self.public_key
        )
        
        self.p2p_connection = DirectP2PConnection(
            security_protocol=self.security_protocol,
            listen_port=p2p_port
        )
        
        # Système Phantom URN avec composant Schrödinger Phoenix P2P
        self.phantom_urn_engine = P2PPhantomUrnEngine(
            node_fingerprint=self.lighthouse.fingerprint,
            p2p_network=self.lighthouse,
            cache_dir=f"./phantom_urn_cache_{node_id}"
        )
        
        self.urn_distribution = P2PUrnDistributionManager(self.phantom_urn_engine)
        
        # Configuration callbacks réseau
        self._setup_network_callbacks()
        
        # Initialisation du protocole simple 3 phases (import dynamique)
        try:
            # Import dynamique pour éviter import circulaire
            sys.path.append(os.path.join(os.path.dirname(__file__), 'web', 'backend'))
            from simple_protocol_helper import initialize_simple_protocol
            
            simple_init_success = initialize_simple_protocol(self)
            if simple_init_success:
                print("🔐 Simple 3-Phase Protocol initialized!")
            else:
                print("❌ Failed to initialize Simple 3-Phase Protocol")
        except Exception as e:
            print(f"⚠️ Simple protocol not available: {e}")
            print("🔐 Using legacy three-phase protocol")
        
        # État du nœud
        self.running = False
        self.start_time = time.time()
        
        print(f"🚀 OpenRed P2P Node initialized")
        print(f"   Node ID: {self.node_id}")
        print(f"   Fingerprint: {self.lighthouse.fingerprint}")
        print(f"   Sector: {self.sector}")
        print(f"   P2P Port: {self.p2p_port}")
        print(f"   🚫 NO CENTRAL API - Pure P2P Architecture!")
        
    def _setup_network_callbacks(self):
        """Configure les callbacks réseau pour événements P2P"""
        
        def on_node_discovered(beacon, sender_ip):
            print(f"🔍 New node discovered: {beacon.node_id}")
            print(f"   Fingerprint: {beacon.fingerprint[:8]}...")
            print(f"   Sector: {beacon.sector}")
            print(f"   Phantom URN System: {beacon.urn_phantom_support}")
            
            # Auto-connexion si nœud compatible Phantom URN
            if beacon.urn_phantom_support and beacon.sector == self.sector:
                print(f"🤝 Initiating auto-connection to compatible node...")
                success = self.lighthouse.initiate_p2p_connection(beacon.fingerprint)
                if success:
                    print(f"✅ Auto-connection established")
                    
        def on_connection_established(fingerprint, socket_conn):
            print(f"🔗 P2P connection established with {fingerprint[:8]}...")
            
            # Enregistrer handler pour messages URN et sociaux
            session_id = f"session_{fingerprint[:8]}"
            self.p2p_connection.register_connection_handler(
                session_id, 
                self._handle_urn_messages
            )
            
            # Vérifier s'il y a des messages sociaux en attente pour ce fingerprint
            if hasattr(self, 'pending_social_messages'):
                pending = self.pending_social_messages.get(fingerprint, [])
                for message_data in pending:
                    print(f"📤 Sending pending social message to {fingerprint[:8]}...")
                    try:
                        # Envoyer via la connexion socket directement
                        message_json = json.dumps(message_data)
                        socket_conn.send(message_json.encode())
                        print(f"✅ Pending message sent successfully")
                    except Exception as e:
                        print(f"❌ Failed to send pending message: {e}")
                
                # Nettoyer les messages envoyés
                if fingerprint in self.pending_social_messages:
                    del self.pending_social_messages[fingerprint]
            
        self.lighthouse.on_node_discovered = on_node_discovered
        self.lighthouse.on_connection_established = on_connection_established
        
    def _handle_urn_messages(self, socket_conn, session_id):
        """Gestionnaire messages URN et sociaux via connexions P2P"""
        try:
            while True:
                try:
                    data = socket_conn.recv(4096)
                    if not data:
                        break
                    
                    # Tenter de parser le JSON
                    try:
                        message = json.loads(data.decode())
                    except json.JSONDecodeError:
                        # Peut-être un message sécurisé, essayer de le traiter différemment
                        print(f"⚠️ Non-JSON message received, ignoring")
                        continue
                    
                    message_type = message.get("type")
                    print(f"📨 Received message type: {message_type}")
                    
                    if message_type == "urn_query":
                        # Traiter requête URN
                        response = self.phantom_urn_engine.handle_urn_query(
                            message, 
                            message.get("requester", "unknown")
                        )
                        socket_conn.send(json.dumps(response).encode())
                        
                    elif message_type == "quantum_matrix_request":
                        # Traiter demande matrice quantique Schrödinger Phoenix
                        matrix_data = self.phantom_urn_engine.handle_matrix_request(
                            message,
                            message.get("requester", "unknown")
                        )
                        if matrix_data:
                            socket_conn.send(json.dumps(matrix_data).encode())
                            
                    elif message_type == "urn_announcement":
                        # Traiter annonce nouvel URN
                        urn_id = message.get("urn_id")
                        provider = message.get("provider")
                        print(f"📢 New URN announced: {urn_id} by {provider[:8]}...")
                        
                    elif message_type == "friendship_request":
                        # Traiter demande d'amitié directement
                        print(f"👥 Received friendship request directly")
                        print(f"   From: {message.get('from_node_id')}")
                        print(f"   Message: {message.get('message')}")
                        
                        # Utiliser le callback si disponible
                        if hasattr(self, 'social_message_handler') and self.social_message_handler:
                            # Appeler le handler de manière synchrone avec un wrapper async
                            import asyncio
                            if asyncio.iscoroutinefunction(self.social_message_handler):
                                # Handler async - l'exécuter en background
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                loop.run_until_complete(self.social_message_handler(session_id, message))
                            else:
                                # Handler sync
                                self.social_message_handler(session_id, message)
                        
                        # Envoyer accusé de réception
                        response = {"status": "received", "type": "friendship_request_ack"}
                        socket_conn.send(json.dumps(response).encode())
                        
                    elif message_type in ["friendship_response", "message", "urn_share"]:
                        # Autres messages sociaux
                        if hasattr(self, 'social_message_handler') and self.social_message_handler:
                            if asyncio.iscoroutinefunction(self.social_message_handler):
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                loop.run_until_complete(self.social_message_handler(session_id, message))
                            else:
                                self.social_message_handler(session_id, message)
                                
                except socket.timeout:
                    continue
                except Exception as msg_error:
                    print(f"⚠️ Error processing individual message: {msg_error}")
                    
        except Exception as e:
            print(f"⚠️ P2P message handler error: {e}")
            
    def set_social_message_handler(self, handler_func):
        """Définit le handler pour messages sociaux"""
        self.social_message_handler = handler_func
        print("📡 Social message handler registered")
        
    def queue_social_message(self, target_fingerprint: str, message_data: dict):
        """Met en file d'attente un message social pour envoi dès connexion"""
        if not hasattr(self, 'pending_social_messages'):
            self.pending_social_messages = {}
        
        if target_fingerprint not in self.pending_social_messages:
            self.pending_social_messages[target_fingerprint] = []
        
        self.pending_social_messages[target_fingerprint].append(message_data)
        print(f"📬 Queued social message for {target_fingerprint[:8]}...")
        
        # Essayer d'établir la connexion immédiatement
        try:
            self.lighthouse.initiate_p2p_connection(target_fingerprint)
        except Exception as e:
            print(f"⚠️ Could not initiate immediate connection: {e}")
            
    async def start_node(self):
        """Démarre le nœud P2P autonome"""
        print(f"🚀 Starting OpenRed P2P Node...")
        
        self.running = True
        
        # Démarrage serveur P2P
        self.p2p_connection.start_p2p_server()
        
        # Démarrage protocole "Phare dans la Nuit"
        self.lighthouse.start_lighthouse(self.p2p_port)
        
        # Indexation URN locaux (si répertoire existe)
        urn_dir = f"./urn-files/{self.node_id}"
        if os.path.exists(urn_dir):
            await self.phantom_urn_engine.index_local_urns(urn_dir)
        else:
            print(f"ℹ️ No local URN directory found: {urn_dir}")
            
        print(f"✅ OpenRed P2P Node fully operational!")
        print(f"   🌟 Broadcasting lighthouse beacon every 30s")
        print(f"   🔐 P2P security protocol active")
        print(f"   🔱 Phantom URN System with Schrödinger Phoenix ready")
        print(f"   🌐 Discovering P2P constellation...")
        
    async def stop_node(self):
        """Arrête le nœud P2P"""
        print(f"🛑 Stopping OpenRed P2P Node...")
        
        self.running = False
        self.lighthouse.stop_lighthouse()
        self.p2p_connection.stop_p2p_server()
        
        print(f"✅ Node stopped gracefully")
        
    async def resurrect_urn(self, urn_id: str):
        """Interface publique pour résurrection URN"""
        print(f"🔱 Requesting URN resurrection: {urn_id}")
        
        result = await self.phantom_urn_engine.resurrect_urn_p2p(urn_id)
        
        if result:
            print(f"✅ URN {urn_id} resurrected successfully!")
            return result
        else:
            print(f"❌ URN {urn_id} resurrection failed")
            return None
            
    def get_node_status(self) -> Dict:
        """État complet du nœud P2P"""
        uptime = time.time() - self.start_time
        lighthouse_stats = self.lighthouse.get_network_stats()
        security_stats = self.security_protocol.get_security_stats()
        urn_stats = self.phantom_urn_engine.get_p2p_stats()
        
        return {
            "node_info": {
                "node_id": self.node_id,
                "fingerprint": self.lighthouse.fingerprint,
                "sector": self.sector,
                "p2p_port": self.p2p_port,
                "uptime_seconds": uptime,
                "running": self.running
            },
            "network": lighthouse_stats,
            "security": security_stats,
            "urn_phantom_system": urn_stats,
            "architecture": "openred_pure_p2p_v1.0"
        }
        
    def print_constellation_map(self):
        """Affiche la carte de la constellation P2P"""
        discovered = self.lighthouse.get_discovered_nodes()
        
        print(f"\n🌌 P2P Constellation Map")
        print(f"═" * 50)
        print(f"🌟 Own Node: {self.node_id} ({self.lighthouse.fingerprint[:8]}...)")
        print(f"📡 Discovered Nodes: {len(discovered)}")
        
        for fingerprint, node_info in discovered.items():
            beacon = node_info["beacon"]
            last_seen = time.time() - node_info["last_seen"]
            
            print(f"  🔗 {beacon.node_id} ({fingerprint[:8]}...)")
            print(f"     Sector: {beacon.sector}")
            print(f"     IP: {node_info['ip']}")
            print(f"     Phantom URN System: {'✅' if beacon.urn_phantom_support else '❌'}")
            print(f"     Last Seen: {last_seen:.0f}s ago")
            print()
            
        active_connections = len(self.p2p_connection.active_connections)
        print(f"🔐 Active P2P Connections: {active_connections}")
        print(f"═" * 50)

async def main():
    """Fonction principale pour démarrage nœud"""
    parser = argparse.ArgumentParser(description="OpenRed P2P Node - Revolutionary Decentralized Platform")
    parser.add_argument("--node-id", required=True, help="Unique node identifier")
    parser.add_argument("--sector", default="general", help="Node sector (tech, health, general...)")
    parser.add_argument("--port", type=int, default=8080, help="P2P listening port")
    parser.add_argument("--urn-dir", help="Directory containing URN files to serve")
    parser.add_argument("--auto-resurrect", help="Auto-resurrect URN on startup")
    
    args = parser.parse_args()
    
    # Création nœud P2P
    node = OpenRedP2PNode(
        node_id=args.node_id,
        sector=args.sector,
        p2p_port=args.port
    )
    
    try:
        # Démarrage nœud
        await node.start_node()
        
        # Auto-résurrection URN si demandé
        if args.auto_resurrect:
            print(f"🔱 Auto-resurrecting URN: {args.auto_resurrect}")
            await node.resurrect_urn(args.auto_resurrect)
            
        # Boucle principale
        print(f"\n💡 Node running. Commands:")
        print(f"   status    - Show node status")
        print(f"   map       - Show constellation map")
        print(f"   resurrect <urn_id> - Resurrect URN")
        print(f"   quit      - Stop node")
        print()
        
        while node.running:
            try:
                command = input("OpenRed-P2P> ").strip().lower()
                
                if command == "quit" or command == "exit":
                    break
                elif command == "status":
                    status = node.get_node_status()
                    print(json.dumps(status, indent=2))
                elif command == "map":
                    node.print_constellation_map()
                elif command.startswith("resurrect "):
                    urn_id = command.split(" ", 1)[1]
                    await node.resurrect_urn(urn_id)
                elif command == "help":
                    print("Commands: status, map, resurrect <urn_id>, quit")
                elif command:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
                
    finally:
        await node.stop_node()

if __name__ == "__main__":
    # Configuration async event loop pour Windows
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    asyncio.run(main())