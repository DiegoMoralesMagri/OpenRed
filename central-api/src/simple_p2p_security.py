# === Architecture P2P Sécurisée Proposée ===
# Basée sur échange de clés publiques + signatures mutuelles

import time
import hashlib
import secrets
import base64
from typing import Dict, Tuple
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

class SimpleP2PSecurityProtocol:
    """Protocole sécurisé simplifié pour connexions P2P directes"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # Identifiant public unique et vérifiable
        self.public_key_fingerprint = self._generate_public_fingerprint()
        
    def _generate_public_fingerprint(self) -> str:
        """Génère empreinte unique basée sur la clé publique"""
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return hashlib.sha256(public_bytes).hexdigest()[:16]
    
    def create_connection_handshake(self, target_node_fingerprint: str) -> Dict:
        """Phase 1: Crée demande de connexion avec clé publique + timestamp"""
        timestamp = int(time.time())
        
        # Données à signer
        handshake_data = f"{self.public_key_fingerprint}:{target_node_fingerprint}:{timestamp}"
        
        # Signature avec clé privée
        signature = self.private_key.sign(
            handshake_data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Export clé publique
        public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            "type": "p2p_handshake_request",
            "source_fingerprint": self.public_key_fingerprint,
            "target_fingerprint": target_node_fingerprint,
            "timestamp": timestamp,
            "public_key": base64.b64encode(public_key_pem).decode(),
            "signature": base64.b64encode(signature).decode(),
            "valid_for": 300  # 5 minutes
        }
    
    def verify_and_respond_handshake(self, handshake_request: Dict) -> Tuple[bool, Dict]:
        """Phase 2: Vérifie handshake et crée réponse"""
        try:
            # Vérifier que c'est pour nous
            if handshake_request["target_fingerprint"] != self.public_key_fingerprint:
                return False, {"error": "handshake_not_for_this_node"}
            
            # Vérifier validité temporelle (5 min max)
            timestamp = handshake_request["timestamp"]
            if abs(time.time() - timestamp) > 300:
                return False, {"error": "handshake_expired"}
            
            # Reconstituer clé publique du demandeur
            public_key_bytes = base64.b64decode(handshake_request["public_key"])
            remote_public_key = serialization.load_pem_public_key(
                public_key_bytes,
                backend=default_backend()
            )
            
            # Vérifier signature
            handshake_data = f"{handshake_request['source_fingerprint']}:{handshake_request['target_fingerprint']}:{timestamp}"
            signature = base64.b64decode(handshake_request["signature"])
            
            remote_public_key.verify(
                signature,
                handshake_data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # ✅ Handshake valide ! Créer réponse
            response_timestamp = int(time.time())
            
            # Créer lien mathématique mutuel
            mutual_link = self._create_mutual_mathematical_link(
                handshake_request['source_fingerprint'],
                self.public_key_fingerprint,
                timestamp,
                response_timestamp
            )
            
            # Signer la réponse
            response_data = f"{self.public_key_fingerprint}:{handshake_request['source_fingerprint']}:{response_timestamp}:{mutual_link}"
            response_signature = self.private_key.sign(
                response_data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Export notre clé publique
            our_public_key_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            response = {
                "type": "p2p_handshake_response",
                "source_fingerprint": self.public_key_fingerprint,
                "target_fingerprint": handshake_request['source_fingerprint'],
                "timestamp": response_timestamp,
                "public_key": base64.b64encode(our_public_key_pem).decode(),
                "signature": base64.b64encode(response_signature).decode(),
                "mutual_link": mutual_link,
                "status": "connection_accepted"
            }
            
            return True, response
            
        except Exception as e:
            return False, {"error": f"handshake_verification_failed: {e}"}
    
    def _create_mutual_mathematical_link(self, node_a: str, node_b: str, 
                                       timestamp_a: int, timestamp_b: int) -> str:
        """Crée lien mathématique vérifiable par les deux nœuds"""
        combined = f"{node_a}:{node_b}:{timestamp_a}:{timestamp_b}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    def finalize_connection(self, handshake_response: Dict, 
                          original_request: Dict) -> Tuple[bool, Dict]:
        """Phase 3: Finalise la connexion après réponse"""
        try:
            # Vérifier que la réponse correspond à notre demande
            response_target = handshake_response.get("target_fingerprint")
            response_source = handshake_response.get("source_fingerprint")
            request_target = original_request.get("target_fingerprint")
            
            if not response_target or not response_source or not request_target:
                return False, {"error": "missing_fingerprint_fields"}
                
            if (response_target != self.public_key_fingerprint or
                response_source != request_target):
                return False, {"error": "response_mismatch"}
            
            # Reconstituer clé publique du répondeur
            public_key_bytes = base64.b64decode(handshake_response["public_key"])
            remote_public_key = serialization.load_pem_public_key(
                public_key_bytes,
                backend=default_backend()
            )
            
            # Vérifier signature de la réponse
            response_data = f"{handshake_response['source_fingerprint']}:{handshake_response['target_fingerprint']}:{handshake_response['timestamp']}:{handshake_response['mutual_link']}"
            signature = base64.b64decode(handshake_response["signature"])
            
            remote_public_key.verify(
                signature,
                response_data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # ✅ Connexion établie avec succès !
            connection_token = {
                "connection_id": f"p2p_{self.public_key_fingerprint}_{handshake_response['source_fingerprint']}",
                "established_at": time.time(),
                "mutual_link": handshake_response["mutual_link"],
                "remote_fingerprint": handshake_response["source_fingerprint"],
                "status": "connected"
            }
            
            return True, connection_token
            
        except Exception as e:
            return False, {"error": f"connection_finalization_failed: {e}"}

# Exemple d'utilisation
if __name__ == "__main__":
    # Simulation connexion entre 2 nœuds
    node_a = SimpleP2PSecurityProtocol("paris_tech")
    node_b = SimpleP2PSecurityProtocol("lyon_health")
    
    print(f"Node A fingerprint: {node_a.public_key_fingerprint}")
    print(f"Node B fingerprint: {node_b.public_key_fingerprint}")
    
    # Phase 1: A demande connexion à B
    handshake = node_a.create_connection_handshake(node_b.public_key_fingerprint)
    print(f"\n✅ Phase 1: Handshake créé (taille: {len(str(handshake))} chars)")
    
    # Phase 2: B vérifie et répond
    valid, response = node_b.verify_and_respond_handshake(handshake)
    print(f"✅ Phase 2: Vérification {'SUCCÈS' if valid else 'ÉCHEC'}")
    
    if valid:
        # Phase 3: A finalise la connexion
        connected, token = node_a.finalize_connection(response, handshake)
        print(f"✅ Phase 3: Connexion {'ÉTABLIE' if connected else 'ÉCHOUÉE'}")
        
        if connected:
            print(f"🔗 Connection ID: {token['connection_id']}")
            print(f"🔐 Mutual Link: {token['mutual_link']}")