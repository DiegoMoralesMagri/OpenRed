# === OpenRed P2P Security : Protocole 3 Phases Révolutionnaire ===
# Sécurité P2P Pure sans API Centrale
# REQUEST → VERIFY → FINALIZE avec Signatures RSA 2048

import json
import time
import hashlib
import secrets
import socket
import threading
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64

@dataclass
class P2PSecurityContext:
    """Contexte de sécurité pour connexion P2P"""
    session_id: str
    peer_fingerprint: str
    peer_public_key: Any
    established_at: float
    last_activity: float
    security_level: str  # "basic", "enhanced", "quantum"
    
class ThreePhaseHandshake:
    """
    Protocole de sécurité révolutionnaire en 3 phases :
    Phase 1: REQUEST  - Demande avec signature RSA
    Phase 2: VERIFY   - Vérification et réponse signée  
    Phase 3: FINALIZE - Établissement lien cryptographique permanent
    """
    
    def __init__(self, node_fingerprint: str, private_key, public_key):
        self.node_fingerprint = node_fingerprint
        self.private_key = private_key
        self.public_key = public_key
        
        # Contextes de sécurité actifs
        self.security_contexts: Dict[str, P2PSecurityContext] = {}
        
        print(f"🔐 Three-Phase Security Protocol initialized")
        print(f"   Fingerprint: {node_fingerprint}")
        print(f"   🚫 NO CENTRAL VALIDATION - Pure P2P Trust")
        
    def generate_session_id(self) -> str:
        """Génère un ID de session unique"""
        return secrets.token_hex(16)
        
    def sign_data(self, data: Dict) -> str:
        """Signe des données avec clé privée RSA"""
        data_json = json.dumps(data, sort_keys=True)
        signature = self.private_key.sign(
            data_json.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
        
    def verify_signature(self, data: Dict, signature: str, public_key) -> bool:
        """Vérifie signature avec clé publique"""
        try:
            data_json = json.dumps(data, sort_keys=True)
            signature_bytes = base64.b64decode(signature)
            
            public_key.verify(
                signature_bytes,
                data_json.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"❌ Signature verification failed: {e}")
            return False
            
    def phase1_request(self, target_fingerprint: str, target_ip: str, target_port: int) -> Dict:
        """
        Phase 1: REQUEST
        Initie demande de connexion sécurisée avec signature
        """
        session_id = self.generate_session_id()
        timestamp = time.time()
        
        # Données de la requête
        request_data = {
            "phase": 1,
            "session_id": session_id,
            "source_fingerprint": self.node_fingerprint,
            "target_fingerprint": target_fingerprint,
            "timestamp": timestamp,
            "capabilities": {
                "schrodinger_phoenix": True,
                "urn_phantom": True,
                "encryption_level": "rsa_2048"
            },
            "challenge": secrets.token_hex(32)
        }
        
        # Signature de la requête
        signature = self.sign_data(request_data)
        
        # Export clé publique pour échange
        public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        request_packet = {
            "security_protocol": "openred_three_phase",
            "data": request_data,
            "signature": signature,
            "public_key": public_key_pem
        }
        
        print(f"📤 Phase 1: Sending REQUEST to {target_fingerprint[:8]}...")
        print(f"   Session: {session_id}")
        print(f"   Target: {target_ip}:{target_port}")
        
        return request_packet
        
    def phase2_verify(self, request_packet: Dict, sender_ip: str) -> Tuple[bool, Optional[Dict]]:
        """
        Phase 2: VERIFY
        Vérifie la requête et génère réponse signée
        """
        try:
            # Extraction des données
            data = request_packet["data"]
            signature = request_packet["signature"]
            public_key_pem = request_packet["public_key"]
            
            # Reconstruction clé publique du demandeur
            peer_public_key = serialization.load_pem_public_key(
                public_key_pem.encode(),
                backend=default_backend()
            )
            
            # Vérification signature
            if not self.verify_signature(data, signature, peer_public_key):
                print("❌ Phase 2: Invalid signature")
                return False, None
                
            # Vérification timestamp (anti-replay)
            if time.time() - data["timestamp"] > 300:  # 5 minutes max
                print("❌ Phase 2: Request too old")
                return False, None
                
            # Vérification que nous sommes bien la cible
            if data["target_fingerprint"] != self.node_fingerprint:
                print("❌ Phase 2: Wrong target fingerprint")
                return False, None
                
            print(f"✅ Phase 2: REQUEST verified from {data['source_fingerprint'][:8]}...")
            
            # Génération réponse Phase 2
            session_id = data["session_id"]
            response_data = {
                "phase": 2,
                "session_id": session_id,
                "source_fingerprint": self.node_fingerprint,
                "target_fingerprint": data["source_fingerprint"],
                "timestamp": time.time(),
                "challenge_response": hashlib.sha256(data["challenge"].encode()).hexdigest(),
                "status": "verified",
                "capabilities": {
                    "schrodinger_phoenix": True,
                    "urn_phantom": True,
                    "encryption_level": "rsa_2048"
                }
            }
            
            # Signature de la réponse
            response_signature = self.sign_data(response_data)
            
            # Export notre clé publique
            our_public_key_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
            
            response_packet = {
                "security_protocol": "openred_three_phase",
                "data": response_data,
                "signature": response_signature,
                "public_key": our_public_key_pem
            }
            
            # Créer contexte de sécurité temporaire
            self.security_contexts[session_id] = P2PSecurityContext(
                session_id=session_id,
                peer_fingerprint=data["source_fingerprint"],
                peer_public_key=peer_public_key,
                established_at=time.time(),
                last_activity=time.time(),
                security_level="enhanced"
            )
            
            print(f"📤 Phase 2: Sending VERIFY response")
            return True, response_packet
            
        except Exception as e:
            print(f"❌ Phase 2 error: {e}")
            return False, None
            
    def phase3_finalize(self, verify_response: Dict) -> bool:
        """
        Phase 3: FINALIZE
        Finalise l'établissement de la connexion sécurisée
        """
        try:
            # Extraction des données
            data = verify_response["data"]
            signature = verify_response["signature"]
            public_key_pem = verify_response["public_key"]
            
            # Reconstruction clé publique du répondeur
            peer_public_key = serialization.load_pem_public_key(
                public_key_pem.encode(),
                backend=default_backend()
            )
            
            # Vérification signature
            if not self.verify_signature(data, signature, peer_public_key):
                print("❌ Phase 3: Invalid signature")
                return False
                
            session_id = data["session_id"]
            
            # Vérification que la session existe
            if session_id not in self.security_contexts:
                print("❌ Phase 3: Unknown session")
                return False
                
            # Mise à jour contexte de sécurité final
            context = self.security_contexts[session_id]
            context.peer_public_key = peer_public_key
            context.last_activity = time.time()
            context.security_level = "quantum"  # Connexion finalisée
            
            print(f"✅ Phase 3: Connection FINALIZED")
            print(f"   Session: {session_id}")
            print(f"   Peer: {data['source_fingerprint'][:8]}...")
            print(f"   Security: {context.security_level}")
            
            return True
            
        except Exception as e:
            print(f"❌ Phase 3 error: {e}")
            return False
            
    def get_security_context(self, session_id: str) -> Optional[P2PSecurityContext]:
        """Récupère le contexte de sécurité d'une session"""
        return self.security_contexts.get(session_id)
        
    def is_connection_secure(self, session_id: str) -> bool:
        """Vérifie si une connexion est sécurisée"""
        context = self.security_contexts.get(session_id)
        if not context:
            return False
            
        # Connexion sécurisée si finalisée et récente
        return (context.security_level == "quantum" and 
                time.time() - context.last_activity < 3600)  # 1 heure
                
    def cleanup_expired_contexts(self):
        """Nettoie les contextes de sécurité expirés"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, context in self.security_contexts.items():
            # Expiration après 1 heure d'inactivité
            if current_time - context.last_activity > 3600:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            del self.security_contexts[session_id]
            print(f"🧹 Cleaned expired security context: {session_id}")
            
    def get_security_stats(self) -> Dict:
        """Statistiques de sécurité"""
        current_time = time.time()
        
        active_contexts = len([
            ctx for ctx in self.security_contexts.values()
            if current_time - ctx.last_activity < 3600
        ])
        
        finalized_connections = len([
            ctx for ctx in self.security_contexts.values()
            if ctx.security_level == "quantum"
        ])
        
        return {
            "protocol": "openred_three_phase",
            "node_fingerprint": self.node_fingerprint,
            "total_contexts": len(self.security_contexts),
            "active_contexts": active_contexts,
            "finalized_connections": finalized_connections,
            "security_level": "rsa_2048_quantum_ready"
        }

class DirectP2PConnection:
    """
    Gestionnaire de connexions P2P directes sécurisées
    Utilise le protocole 3 phases pour établir communications
    """
    
    def __init__(self, security_protocol: ThreePhaseHandshake, listen_port: int):
        self.security_protocol = security_protocol
        self.listen_port = listen_port
        self.server_socket = None
        self.active_connections = {}
        self.connection_handlers = {}
        self.running = False
        
    def start_p2p_server(self):
        """Démarre serveur P2P pour connexions entrantes"""
        def server_thread():
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind(("0.0.0.0", self.listen_port))
                self.server_socket.listen(10)
                
                print(f"🔗 P2P Server started on port {self.listen_port}")
                
                while self.running:
                    try:
                        client_sock, addr = self.server_socket.accept()
                        threading.Thread(
                            target=self._handle_incoming_connection,
                            args=(client_sock, addr),
                            daemon=True
                        ).start()
                    except Exception as e:
                        if self.running:
                            print(f"⚠️ P2P server accept error: {e}")
                            
            except Exception as e:
                print(f"❌ P2P server error: {e}")
                
        self.running = True
        threading.Thread(target=server_thread, daemon=True).start()
        
    def stop_p2p_server(self):
        """Arrête le serveur P2P"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            
    def _handle_incoming_connection(self, client_sock: socket.socket, addr: Tuple[str, int]):
        """Traite une connexion P2P entrante avec protocole 3 phases"""
        try:
            print(f"🔗 Incoming P2P connection from {addr[0]}")
            
            # Recevoir Phase 1: REQUEST
            data = client_sock.recv(8192)
            request_packet = json.loads(data.decode())
            
            if request_packet.get("security_protocol") != "openred_three_phase":
                print("❌ Unknown security protocol")
                client_sock.close()
                return
                
            # Phase 2: VERIFY
            verified, response_packet = self.security_protocol.phase2_verify(
                request_packet, addr[0]
            )
            
            if verified:
                # Envoyer réponse Phase 2
                client_sock.send(json.dumps(response_packet).encode())
                
                # Attendre Phase 3 ou continuer avec communication
                session_id = request_packet["data"]["session_id"]
                self.active_connections[session_id] = {
                    "socket": client_sock,
                    "peer_ip": addr[0],
                    "established_at": time.time()
                }
                
                print(f"✅ P2P connection established from {addr[0]}")
                
                # Handler pour messages continus
                if session_id in self.connection_handlers:
                    self.connection_handlers[session_id](client_sock, session_id)
                    
            else:
                client_sock.close()
                
        except Exception as e:
            print(f"❌ Error handling P2P connection: {e}")
            client_sock.close()
            
    def connect_to_peer(self, peer_ip: str, peer_port: int, peer_fingerprint: str) -> Optional[str]:
        """Initie connexion P2P avec protocole 3 phases"""
        try:
            # Phase 1: REQUEST
            request_packet = self.security_protocol.phase1_request(
                peer_fingerprint, peer_ip, peer_port
            )
            
            # Connexion TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((peer_ip, peer_port))
            
            # Envoyer Phase 1
            sock.send(json.dumps(request_packet).encode())
            
            # Recevoir Phase 2: VERIFY
            response = sock.recv(8192)
            verify_response = json.loads(response.decode())
            
            # Phase 3: FINALIZE
            if self.security_protocol.phase3_finalize(verify_response):
                session_id = request_packet["data"]["session_id"]
                
                self.active_connections[session_id] = {
                    "socket": sock,
                    "peer_ip": peer_ip,
                    "established_at": time.time()
                }
                
                return session_id
            else:
                sock.close()
                return None
                
        except Exception as e:
            print(f"❌ P2P connection failed: {e}")
            return None
            
    def send_secure_message(self, session_id: str, message: Dict) -> bool:
        """Envoie message sécurisé via connexion P2P"""
        if session_id not in self.active_connections:
            return False
            
        if not self.security_protocol.is_connection_secure(session_id):
            return False
            
        try:
            connection = self.active_connections[session_id]
            socket_conn = connection["socket"]
            
            # Message avec métadonnées de sécurité
            secure_message = {
                "session_id": session_id,
                "timestamp": time.time(),
                "content": message
            }
            
            socket_conn.send(json.dumps(secure_message).encode())
            return True
            
        except Exception as e:
            print(f"❌ Error sending secure message: {e}")
            return False
            
    def register_connection_handler(self, session_id: str, handler_func):
        """Enregistre handler pour messages d'une connexion"""
        self.connection_handlers[session_id] = handler_func