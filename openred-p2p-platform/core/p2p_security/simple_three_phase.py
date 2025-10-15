# === OpenRed P2P : Protocole Simple 3 Phases ===
# Implémentation exacte du protocole convenu
# Phase 1: REQUEST  → Demande avec signature RSA
# Phase 2: VERIFY   → Vérification et réponse signée  
# Phase 3: FINALIZE → Lien mutuel mathématique

import json
import time
import hashlib
import socket
from typing import Dict, Optional, Tuple
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64

class SimpleThreePhase:
    """
    Protocole simple et efficace en 3 phases :
    - Phase 1: REQUEST  → Demande avec signature RSA
    - Phase 2: VERIFY   → Vérification et réponse signée  
    - Phase 3: FINALIZE → Lien mutuel mathématique
    """
    
    def __init__(self, node_id: str, private_key, public_key):
        self.node_id = node_id
        self.private_key = private_key
        self.public_key = public_key
        self.active_links = {}  # Liens mutuels établis
        
        print(f"🔐 Simple Three-Phase Protocol initialized for {node_id}")
        
    def _sign_data(self, data: str) -> str:
        """Signe des données avec la clé privée RSA"""
        signature = self.private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
        
    def _verify_signature(self, data: str, signature: str, public_key_pem: str) -> bool:
        """Vérifie une signature avec une clé publique"""
        try:
            # Reconstruit la clé publique
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode(),
                backend=None
            )
            
            # Vérifie la signature
            signature_bytes = base64.b64decode(signature)
            public_key.verify(
                signature_bytes,
                data.encode(),
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
            
    def _export_public_key(self) -> str:
        """Exporte la clé publique au format PEM"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

    # ============ PHASE 1: REQUEST ============
    def phase1_request(self, target_node: str, message_data: Dict) -> Dict:
        """
        Phase 1: REQUEST
        Demande avec signature RSA
        """
        timestamp = time.time()
        
        # Données de base pour la demande
        request_data = {
            "from": self.node_id,
            "to": target_node,
            "timestamp": timestamp,
            "message": message_data
        }
        
        # Convertit en string pour signature
        data_string = json.dumps(request_data, sort_keys=True)
        
        # Signe la demande
        signature = self._sign_data(data_string)
        
        # Paquet complet
        request_packet = {
            "phase": "REQUEST",
            "data": request_data,
            "signature": signature,
            "public_key": self._export_public_key()
        }
        
        print(f"📤 Phase 1: REQUEST from {self.node_id} to {target_node}")
        return request_packet

    # ============ PHASE 2: VERIFY ============
    def phase2_verify(self, request_packet: Dict) -> Tuple[bool, Optional[Dict]]:
        """
        Phase 2: VERIFY
        Vérification et réponse signée
        """
        try:
            # Extraction des données
            data = request_packet["data"]
            signature = request_packet["signature"]
            sender_public_key = request_packet["public_key"]
            
            # Vérifie que c'est bien pour nous
            if data["to"] != self.node_id:
                print(f"❌ Phase 2: Message not for us ({data['to']} != {self.node_id})")
                return False, None
            
            # Vérifie la signature
            data_string = json.dumps(data, sort_keys=True)
            if not self._verify_signature(data_string, signature, sender_public_key):
                print("❌ Phase 2: Invalid signature")
                return False, None
                
            print(f"✅ Phase 2: VERIFY successful from {data['from']}")
            
            # Prépare la réponse signée
            timestamp = time.time()
            response_data = {
                "from": self.node_id,
                "to": data["from"],
                "timestamp": timestamp,
                "response": "VERIFIED",
                "original_timestamp": data["timestamp"]
            }
            
            # Signe la réponse
            response_string = json.dumps(response_data, sort_keys=True)
            response_signature = self._sign_data(response_string)
            
            verify_packet = {
                "phase": "VERIFY",
                "data": response_data,
                "signature": response_signature,
                "public_key": self._export_public_key()
            }
            
            return True, verify_packet
            
        except Exception as e:
            print(f"❌ Phase 2: Error - {e}")
            return False, None

    # ============ PHASE 3: FINALIZE ============
    def phase3_finalize(self, verify_packet: Dict, original_timestamp: float) -> bool:
        """
        Phase 3: FINALIZE
        Lien mutuel mathématique
        """
        try:
            # Extraction des données
            data = verify_packet["data"]
            signature = verify_packet["signature"]
            sender_public_key = verify_packet["public_key"]
            
            # Vérifie que c'est bien pour nous
            if data["to"] != self.node_id:
                print(f"❌ Phase 3: Response not for us")
                return False
                
            # Vérifie la signature de la réponse
            data_string = json.dumps(data, sort_keys=True)
            if not self._verify_signature(data_string, signature, sender_public_key):
                print("❌ Phase 3: Invalid response signature")
                return False
                
            # Vérifie le timestamp original
            if data["original_timestamp"] != original_timestamp:
                print("❌ Phase 3: Timestamp mismatch")
                return False
                
            # Calcul du lien mutuel mathématique
            link_data = f"{self.node_id}:{data['from']}:{original_timestamp}:{data['timestamp']}"
            mutual_link = hashlib.sha256(link_data.encode()).hexdigest()
            
            # Stocke le lien mutuel
            self.active_links[data["from"]] = {
                "mutual_link": mutual_link,
                "established_at": time.time(),
                "peer_public_key": sender_public_key
            }
            
            print(f"✅ Phase 3: FINALIZE - Mutual link established with {data['from']}")
            print(f"   Link: {mutual_link[:16]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Phase 3: Error - {e}")
            return False

    # ============ TRANSMISSION SIMPLE ============
    def send_simple_message(self, target_ip: str, target_port: int, target_node: str, message_data: Dict) -> bool:
        """
        Envoie un message en utilisant le protocole 3 phases
        """
        try:
            # Phase 1: REQUEST
            request_packet = self.phase1_request(target_node, message_data)
            
            # Envoie via TCP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                sock.connect((target_ip, target_port))
                
                # Envoie la requête
                message = json.dumps(request_packet) + "\n"
                sock.send(message.encode())
                
                # Attend la réponse VERIFY
                response = sock.recv(4096).decode().strip()
                verify_packet = json.loads(response)
                
                # Phase 3: FINALIZE
                if self.phase3_finalize(verify_packet, request_packet["data"]["timestamp"]):
                    print(f"🎉 Message sent successfully to {target_node}")
                    return True
                else:
                    print(f"❌ Failed to finalize connection with {target_node}")
                    return False
                    
        except Exception as e:
            print(f"❌ Failed to send message to {target_node}: {e}")
            return False

    def handle_incoming_message(self, client_socket, client_address):
        """
        Gère un message entrant selon le protocole 3 phases
        """
        try:
            # Reçoit le message
            data = client_socket.recv(4096).decode().strip()
            request_packet = json.loads(data)
            
            if request_packet.get("phase") == "REQUEST":
                # Phase 2: VERIFY
                success, verify_packet = self.phase2_verify(request_packet)
                
                if success and verify_packet:
                    # Envoie la réponse VERIFY
                    response = json.dumps(verify_packet) + "\n"
                    client_socket.send(response.encode())
                    
                    # Traite le message reçu
                    message_data = request_packet["data"]["message"]
                    self._process_received_message(message_data, request_packet["data"]["from"])
                    
                else:
                    # Envoie une erreur
                    error_response = {"phase": "ERROR", "message": "Verification failed"}
                    client_socket.send(json.dumps(error_response).encode())
                    
        except Exception as e:
            print(f"❌ Error handling incoming message: {e}")
        finally:
            client_socket.close()

    def _process_received_message(self, message_data: Dict, sender: str):
        """Traite un message reçu avec succès"""
        print(f"📥 Message received from {sender}: {message_data}")
        
        # Traitement selon le type de message
        if message_data.get("type") == "friendship_request":
            print(f"👥 Friendship request from {sender}")
            
            # Récupérer les données de la demande d'amitié
            friendship_data = message_data.get("data", {})
            
            try:
                # INTÉGRATION DIRECTE: Notifier le système global
                # On utilise une approche callback pour notifier web_api.py
                self._notify_friendship_request_received(friendship_data, sender)
                return True
                
            except Exception as e:
                print(f"❌ Error processing friendship request: {e}")
                return False
                
        elif message_data.get("type") == "friendship_accepted":
            print(f"🎉 Friendship accepted notification from {sender}")
            
            # Récupérer les données d'acceptation
            acceptance_data = message_data.get("data", {})
            
            try:
                # Notifier le système que notre demande a été acceptée
                self._notify_friendship_accepted(acceptance_data, sender)
                return True
                
            except Exception as e:
                print(f"❌ Error processing friendship acceptance: {e}")
                return False
                
        else:
            print(f"ℹ️ Unknown message type: {message_data.get('type')}")
            return False
    
    def _notify_friendship_request_received(self, friendship_data: Dict, sender: str):
        """Notifie le système principal qu'une demande d'amitié a été reçue"""
        print(f"🔔 Notifying system: friendship request from {sender}")
        
        # Pour l'instant, stockons dans un attribut pour que web_api.py puisse le récupérer
        if not hasattr(self, 'pending_friendship_requests'):
            self.pending_friendship_requests = []
            
        request_info = {
            "sender": sender,
            "data": friendship_data,
            "received_at": time.time(),
            "processed": False
        }
        
        self.pending_friendship_requests.append(request_info)
        print(f"✅ Friendship request stored in pending queue")
        
    def _notify_friendship_accepted(self, acceptance_data: Dict, sender: str):
        """Notifie le système qu'une demande d'amitié a été acceptée"""
        print(f"🎉 Processing friendship acceptance from {sender}")
        
        # Stocker les notifications d'acceptation
        if not hasattr(self, 'friendship_acceptances'):
            self.friendship_acceptances = []
            
        acceptance_info = {
            "sender": sender,
            "data": acceptance_data,
            "received_at": time.time(),
            "processed": False
        }
        
        self.friendship_acceptances.append(acceptance_info)
        print(f"✅ Friendship acceptance stored for processing")
        
    def get_pending_friendship_acceptances(self):
        """Retourne les acceptations d'amitié en attente"""
        if not hasattr(self, 'friendship_acceptances'):
            return []
        return [acc for acc in self.friendship_acceptances if not acc['processed']]
        
    def mark_friendship_acceptance_processed(self, sender: str, request_id: str):
        """Marque une acceptation d'amitié comme traitée"""
        if not hasattr(self, 'friendship_acceptances'):
            return
            
        for acc in self.friendship_acceptances:
            if acc['sender'] == sender and acc['data'].get('request_id') == request_id:
                acc['processed'] = True
                print(f"✅ Marked friendship acceptance {request_id} as processed")
        
    def get_pending_friendship_requests(self):
        """Retourne les demandes d'amitié en attente"""
        if not hasattr(self, 'pending_friendship_requests'):
            return []
        return [req for req in self.pending_friendship_requests if not req['processed']]
        
    def mark_friendship_request_processed(self, sender: str, request_id: str):
        """Marque une demande d'amitié comme traitée"""
        if not hasattr(self, 'pending_friendship_requests'):
            return
            
        for req in self.pending_friendship_requests:
            if req['sender'] == sender and req['data'].get('request_id') == request_id:
                req['processed'] = True
                print(f"✅ Marked friendship request {request_id} as processed")
            
    def is_connected_to(self, node_id: str) -> bool:
        """Vérifie si on a un lien mutuel avec un nœud"""
        return node_id in self.active_links
        
    def get_active_connections(self) -> Dict:
        """Retourne les connexions actives"""
        return self.active_links.copy()