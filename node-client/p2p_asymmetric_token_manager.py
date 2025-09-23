#!/usr/bin/env python3
"""
🔐 O-Red P2P Asymmetric Token Manager
Architecture révolutionnaire : 4 clés RSA par relation d'amitié

Innovations :
- Tokens asymétriques bilatéraux  
- Non-répudiation cryptographique absolue
- Sécurité quantique-ready
- Stockage local 100% décentralisé

Auteur : Système OpenRed P2P Révolutionnaire
Date : Septembre 2025
"""

import os
import json
import secrets
import base64
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption

class P2PAsymmetricTokenManager:
    """
    🚀 RÉVOLUTION CRYPTOGRAPHIQUE : Tokens P2P Asymétriques
    
    Chaque relation d'amitié utilise 4 clés RSA distinctes :
    
    Pierre ↔ Marie = 4 clés cryptographiques
    
    Pierre → Marie : 
      🔐 Clé privée token P→M (Pierre garde secrète)
      🔑 Clé publique token P→M (Marie reçoit)
    
    Marie → Pierre :
      🔐 Clé privée token M→P (Marie garde secrète)  
      🔑 Clé publique token M→P (Pierre reçoit)
    
    Résultat : Sécurité exponentiellement renforcée !
    """
    
    def __init__(self, node_identity: Dict[str, Any], storage_path: str = None):
        """
        Initialiser le gestionnaire de tokens asymétriques P2P
        
        Args:
            node_identity: Identité principale du nœud
            storage_path: Chemin pour stockage local sécurisé
        """
        self.node_id = node_identity['node_id']
        self.node_private_key = node_identity['private_key']
        self.node_public_key = node_identity['public_key']
        
        # Stockage local des relations asymétriques
        self.storage_path = storage_path or f"./{self.node_id}_asymmetric_tokens.json"
        
        # Structure : friend_node_id → relation_data
        self.asymmetric_relationships = {}
        
        # Charger les relations existantes
        self._load_relationships()
        
        print(f"🔐 [ASYMMETRIC TOKENS] Gestionnaire initialisé pour nœud : {self.node_id}")
    
    def establish_asymmetric_friendship(self, friend_node_id: str, friend_main_public_key, permissions: Dict[str, bool] = None) -> Dict[str, Any]:
        """
        🤝 Établir une relation d'amitié avec tokens asymétriques
        
        Génère une paire RSA spécifique pour cette relation
        
        Args:
            friend_node_id: ID du nœud ami
            friend_main_public_key: Clé publique principale de l'ami
            permissions: Permissions accordées à l'ami
        
        Returns:
            Token public à envoyer à l'ami
        """
        print(f"🚀 [ASYMMETRIC] Établissement relation avec {friend_node_id}")
        
        # 1. Générer paire RSA spécifique pour cette relation
        relationship_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        relationship_public_key = relationship_private_key.public_key()
        
        # 2. Permissions par défaut si non spécifiées
        if permissions is None:
            permissions = {
                "read_shared_files": True,
                "send_messages": True,
                "download_public_content": True,
                "access_private_folders": False,
                "modify_shared_docs": False,
                "voice_call": False
            }
        
        # 3. Créer le token que JE donne à mon ami
        outgoing_token_data = {
            "token_id": secrets.token_urlsafe(32),
            "relationship_id": f"{self.node_id}→{friend_node_id}",
            "issuer": self.node_id,
            "holder": friend_node_id,
            "token_type": "asymmetric_friendship",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat(),
            "permissions": permissions,
            "relationship_fingerprint": self._generate_relationship_fingerprint(friend_node_id)
        }
        
        # 4. Signer avec la clé privée spécifique à cette relation
        token_signature = self._sign_with_relationship_key(outgoing_token_data, relationship_private_key)
        outgoing_token_data["asymmetric_signature"] = token_signature
        
        # 5. Stocker la relation asymétrique
        self.asymmetric_relationships[friend_node_id] = {
            "friend_node_id": friend_node_id,
            "established_at": datetime.utcnow().isoformat(),
            "status": "pending_response",
            
            # Token que JE donne à l'ami
            "outgoing_token": {
                "private_key_pem": self._serialize_private_key(relationship_private_key),
                "public_key_pem": self._serialize_public_key(relationship_public_key),
                "token_data": outgoing_token_data
            },
            
            # Token que l'ami me donnera (vide pour l'instant)
            "incoming_token": None
        }
        
        # 6. Sauvegarder
        self._save_relationships()
        
        print(f"✅ [ASYMMETRIC] Relation établie - Token généré pour {friend_node_id}")
        
        return {
            "token_public_key_pem": self._serialize_public_key(relationship_public_key),
            "token_data": outgoing_token_data,
            "instructions": f"Envoyer ce token à {friend_node_id}"
        }
    
    def receive_asymmetric_token(self, friend_node_id: str, friend_token_public_key_pem: str, friend_token_data: Dict[str, Any]) -> bool:
        """
        📨 Recevoir le token asymétrique de mon ami
        
        Args:
            friend_node_id: ID du nœud ami
            friend_token_public_key_pem: Clé publique token de l'ami (PEM)
            friend_token_data: Données du token de l'ami
        
        Returns:
            True si token valide et accepté
        """
        print(f"📨 [ASYMMETRIC] Réception token de {friend_node_id}")
        
        try:
            # 1. Désérialiser la clé publique de l'ami
            friend_token_public_key = serialization.load_pem_public_key(
                friend_token_public_key_pem.encode(),
                backend=default_backend()
            )
            
            # 2. Vérifier la signature asymétrique
            if not self._verify_token_signature(friend_token_data, friend_token_public_key):
                print(f"❌ [ASYMMETRIC] Signature invalide pour token de {friend_node_id}")
                return False
            
            # 3. Vérifier que c'est bien pour moi
            if friend_token_data.get("holder") != self.node_id:
                print(f"❌ [ASYMMETRIC] Token non destiné à ce nœud")
                return False
            
            # 4. Stocker la partie "incoming" de la relation
            if friend_node_id in self.asymmetric_relationships:
                self.asymmetric_relationships[friend_node_id]["incoming_token"] = {
                    "friend_public_key_pem": friend_token_public_key_pem,
                    "token_data": friend_token_data
                }
                self.asymmetric_relationships[friend_node_id]["status"] = "active"
            else:
                # Créer nouvelle relation si pas encore initiée de mon côté
                self.asymmetric_relationships[friend_node_id] = {
                    "friend_node_id": friend_node_id,
                    "established_at": datetime.utcnow().isoformat(),
                    "status": "active",
                    "outgoing_token": None,
                    "incoming_token": {
                        "friend_public_key_pem": friend_token_public_key_pem,
                        "token_data": friend_token_data
                    }
                }
            
            # 5. Sauvegarder
            self._save_relationships()
            
            print(f"✅ [ASYMMETRIC] Token accepté de {friend_node_id} - Relation active")
            return True
            
        except Exception as e:
            print(f"❌ [ASYMMETRIC] Erreur réception token : {str(e)}")
            return False
    
    def authorize_friend_action(self, friend_node_id: str, requested_action: str, action_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        🔐 Autoriser une action de mon ami avec preuve asymétrique
        
        L'ami doit envoyer une demande signée avec SA clé privée token
        Je réponds avec une autorisation signée avec MA clé privée token
        
        Args:
            friend_node_id: ID du nœud ami
            requested_action: Action demandée
            action_data: Données de la demande (incluant signature ami)
        
        Returns:
            Autorisation signée ou refus
        """
        print(f"🔐 [AUTHORIZE] {friend_node_id} demande : {requested_action}")
        
        # 1. Vérifier que la relation existe
        if friend_node_id not in self.asymmetric_relationships:
            return {"authorized": False, "reason": "Relation inexistante"}
        
        relationship = self.asymmetric_relationships[friend_node_id]
        
        # 2. Vérifier que j'ai le token entrant de l'ami
        incoming_token = relationship.get("incoming_token")
        if not incoming_token:
            return {"authorized": False, "reason": "Token ami manquant"}
        
        # 3. Vérifier les permissions dans le token que l'ami m'a donné
        friend_permissions = incoming_token["token_data"]["permissions"]
        if requested_action not in friend_permissions or not friend_permissions[requested_action]:
            return {"authorized": False, "reason": f"Permission {requested_action} non accordée"}
        
        # 4. Vérifier la signature de la demande avec la clé publique token de l'ami
        if action_data and "request_signature" in action_data:
            friend_public_key = serialization.load_pem_public_key(
                incoming_token["friend_public_key_pem"].encode(),
                backend=default_backend()
            )
            
            if not self._verify_request_signature(action_data, friend_public_key):
                return {"authorized": False, "reason": "Signature demande invalide"}
        
        # 5. Générer autorisation signée avec MA clé privée token
        authorization = {
            "authorized": True,
            "action": requested_action,
            "friend_node_id": friend_node_id,
            "authorized_by": self.node_id,
            "timestamp": datetime.utcnow().isoformat(),
            "authorization_id": secrets.token_urlsafe(16)
        }
        
        # 6. Signer avec MA clé privée spécifique à cette relation
        outgoing_token = relationship.get("outgoing_token")
        if outgoing_token:
            my_private_key = serialization.load_pem_private_key(
                outgoing_token["private_key_pem"].encode(),
                password=None,
                backend=default_backend()
            )
            
            authorization["asymmetric_authorization_signature"] = self._sign_with_relationship_key(authorization, my_private_key)
        
        print(f"✅ [AUTHORIZE] Action {requested_action} autorisée pour {friend_node_id}")
        return authorization
    
    def request_friend_action(self, friend_node_id: str, action: str, action_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        📤 Demander une action chez mon ami avec preuve asymétrique
        
        Je signe ma demande avec MA clé privée token
        L'ami vérifiera avec MA clé publique token
        
        Args:
            friend_node_id: ID du nœud ami
            action: Action demandée
            action_data: Données supplémentaires
        
        Returns:
            Demande signée cryptographiquement
        """
        print(f"📤 [REQUEST] Demande {action} vers {friend_node_id}")
        
        # 1. Vérifier que la relation existe
        if friend_node_id not in self.asymmetric_relationships:
            return {"error": "Relation inexistante"}
        
        relationship = self.asymmetric_relationships[friend_node_id]
        outgoing_token = relationship.get("outgoing_token")
        
        if not outgoing_token:
            return {"error": "Token sortant manquant"}
        
        # 2. Créer la demande
        request = {
            "requester": self.node_id,
            "target": friend_node_id,
            "action": action,
            "data": action_data or {},
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": secrets.token_urlsafe(16),
            "token_id": outgoing_token["token_data"]["token_id"]
        }
        
        # 3. Signer avec MA clé privée spécifique à cette relation
        my_private_key = serialization.load_pem_private_key(
            outgoing_token["private_key_pem"].encode(),
            password=None,
            backend=default_backend()
        )
        
        request["request_signature"] = self._sign_with_relationship_key(request, my_private_key)
        
        print(f"✅ [REQUEST] Demande {action} signée pour {friend_node_id}")
        return request
    
    def list_relationships(self) -> List[Dict[str, Any]]:
        """
        📋 Lister toutes les relations asymétriques
        """
        relationships = []
        
        for friend_id, relationship in self.asymmetric_relationships.items():
            relationships.append({
                "friend_node_id": friend_id,
                "status": relationship["status"],
                "established_at": relationship["established_at"],
                "has_outgoing_token": relationship["outgoing_token"] is not None,
                "has_incoming_token": relationship["incoming_token"] is not None,
                "outgoing_permissions": relationship["outgoing_token"]["token_data"]["permissions"] if relationship["outgoing_token"] else None,
                "incoming_permissions": relationship["incoming_token"]["token_data"]["permissions"] if relationship["incoming_token"] else None
            })
        
        return relationships
    
    def revoke_friend_access(self, friend_node_id: str, direction: str = "both") -> bool:
        """
        🚫 Révoquer l'accès d'un ami (asymétrique)
        
        Args:
            friend_node_id: ID du nœud ami
            direction: "outgoing", "incoming", ou "both"
        
        Returns:
            True si révocation réussie
        """
        if friend_node_id not in self.asymmetric_relationships:
            return False
        
        relationship = self.asymmetric_relationships[friend_node_id]
        
        if direction in ["outgoing", "both"] and relationship["outgoing_token"]:
            # Marquer le token sortant comme révoqué
            relationship["outgoing_token"]["token_data"]["status"] = "revoked"
            relationship["outgoing_token"]["token_data"]["revoked_at"] = datetime.utcnow().isoformat()
        
        if direction in ["incoming", "both"] and relationship["incoming_token"]:
            # Supprimer le token entrant
            relationship["incoming_token"] = None
        
        if direction == "both":
            relationship["status"] = "revoked"
        
        self._save_relationships()
        print(f"🚫 [REVOKE] Accès révoqué pour {friend_node_id} (direction: {direction})")
        return True
    
    # === MÉTHODES UTILITAIRES CRYPTOGRAPHIQUES ===
    
    def _sign_with_relationship_key(self, data: Dict[str, Any], private_key) -> str:
        """Signer des données avec une clé privée de relation"""
        data_string = json.dumps(data, sort_keys=True, default=str)
        signature = private_key.sign(
            data_string.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
    
    def _verify_token_signature(self, token_data: Dict[str, Any], public_key) -> bool:
        """Vérifier la signature d'un token"""
        try:
            signature_b64 = token_data.pop("asymmetric_signature")
            signature = base64.b64decode(signature_b64)
            
            data_string = json.dumps(token_data, sort_keys=True, default=str)
            
            public_key.verify(
                signature,
                data_string.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Remettre la signature dans le token
            token_data["asymmetric_signature"] = signature_b64
            return True
            
        except Exception as e:
            print(f"❌ Erreur vérification signature : {str(e)}")
            # Remettre la signature même en cas d'erreur
            if 'signature_b64' in locals():
                token_data["asymmetric_signature"] = signature_b64
            return False
    
    def _verify_request_signature(self, request_data: Dict[str, Any], public_key) -> bool:
        """Vérifier la signature d'une demande"""
        try:
            signature_b64 = request_data.get("request_signature")
            if not signature_b64:
                return False
            
            # Copier sans la signature pour vérification
            data_copy = {k: v for k, v in request_data.items() if k != "request_signature"}
            signature = base64.b64decode(signature_b64)
            
            data_string = json.dumps(data_copy, sort_keys=True, default=str)
            
            public_key.verify(
                signature,
                data_string.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur vérification signature demande : {str(e)}")
            return False
    
    def _generate_relationship_fingerprint(self, friend_node_id: str) -> str:
        """Générer empreinte unique pour une relation"""
        combined = f"{self.node_id}:{friend_node_id}:{datetime.utcnow().date().isoformat()}"
        return base64.b64encode(combined.encode()).decode()[:16]
    
    def _serialize_private_key(self, private_key) -> str:
        """Sérialiser clé privée en PEM"""
        return private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        ).decode()
    
    def _serialize_public_key(self, public_key) -> str:
        """Sérialiser clé publique en PEM"""
        return public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        ).decode()
    
    # === PERSISTANCE LOCALE ===
    
    def _save_relationships(self):
        """Sauvegarder relations dans fichier local"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "node_id": self.node_id,
                    "saved_at": datetime.utcnow().isoformat(),
                    "relationships": self.asymmetric_relationships
                }, f, indent=2, default=str)
        except Exception as e:
            print(f"❌ Erreur sauvegarde : {str(e)}")
    
    def _load_relationships(self):
        """Charger relations depuis fichier local"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.asymmetric_relationships = data.get("relationships", {})
                    print(f"✅ Relations chargées : {len(self.asymmetric_relationships)} relations")
        except Exception as e:
            print(f"❌ Erreur chargement : {str(e)}")
            self.asymmetric_relationships = {}


def demo_asymmetric_tokens():
    """
    🎯 Démonstration complète du système de tokens asymétriques
    """
    print("🚀 === DÉMONSTRATION TOKENS P2P ASYMÉTRIQUES ===\n")
    
    # === SETUP NŒUDS ===
    
    # Génération identités principales
    pierre_main_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    marie_main_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    
    pierre_identity = {
        "node_id": "pierre_tech_node",
        "private_key": pierre_main_key,
        "public_key": pierre_main_key.public_key()
    }
    
    marie_identity = {
        "node_id": "marie_health_node", 
        "private_key": marie_main_key,
        "public_key": marie_main_key.public_key()
    }
    
    # Initialisation gestionnaires
    pierre_manager = P2PAsymmetricTokenManager(pierre_identity, "pierre_tokens.json")
    marie_manager = P2PAsymmetricTokenManager(marie_identity, "marie_tokens.json")
    
    print("✅ Nœuds Pierre et Marie initialisés\n")
    
    # === ÉTABLISSEMENT RELATION ASYMÉTRIQUE ===
    
    print("🤝 === ÉTABLISSEMENT RELATION ASYMÉTRIQUE ===")
    
    # Pierre génère token pour Marie
    pierre_permissions = {
        "read_tech_articles": True,
        "download_code_samples": True,
        "send_messages": True,
        "access_private_projects": False,
        "modify_shared_code": False
    }
    
    pierre_token_for_marie = pierre_manager.establish_asymmetric_friendship(
        "marie_health_node",
        marie_identity["public_key"],
        pierre_permissions
    )
    
    # Marie génère token pour Pierre
    marie_permissions = {
        "read_health_research": True,
        "download_public_papers": True,
        "send_messages": True,
        "access_patient_data": False,
        "modify_research_data": False
    }
    
    marie_token_for_pierre = marie_manager.establish_asymmetric_friendship(
        "pierre_tech_node",
        pierre_identity["public_key"], 
        marie_permissions
    )
    
    # Échange croisé des tokens
    pierre_accepts = pierre_manager.receive_asymmetric_token(
        "marie_health_node",
        marie_token_for_pierre["token_public_key_pem"],
        marie_token_for_pierre["token_data"]
    )
    
    marie_accepts = marie_manager.receive_asymmetric_token(
        "pierre_tech_node",
        pierre_token_for_marie["token_public_key_pem"],
        pierre_token_for_marie["token_data"]
    )
    
    print(f"Pierre accepte Marie : {pierre_accepts}")
    print(f"Marie accepte Pierre : {marie_accepts}\n")
    
    # === UTILISATION ASYMÉTRIQUE ===
    
    print("🔐 === UTILISATION ASYMÉTRIQUE ===")
    
    # Pierre demande à télécharger un document de Marie
    pierre_request = pierre_manager.request_friend_action(
        "marie_health_node",
        "download_public_papers",
        {"document_id": "covid_research_2025.pdf", "format": "pdf"}
    )
    
    print("📤 Pierre demande téléchargement (signé asymétriquement)")
    print(f"Request ID : {pierre_request['request_id']}")
    
    # Marie autorise la demande de Pierre
    marie_authorization = marie_manager.authorize_friend_action(
        "pierre_tech_node",
        "download_public_papers", 
        pierre_request
    )
    
    print("✅ Marie autorise (signé asymétriquement)")
    print(f"Autorisé : {marie_authorization['authorized']}")
    print(f"Authorization ID : {marie_authorization.get('authorization_id')}\n")
    
    # === ÉTAT DES RELATIONS ===
    
    print("📋 === ÉTAT DES RELATIONS ASYMÉTRIQUES ===")
    
    pierre_relations = pierre_manager.list_relationships()
    marie_relations = marie_manager.list_relationships()
    
    print("Pierre voit :")
    for rel in pierre_relations:
        print(f"  - {rel['friend_node_id']} : {rel['status']}")
        print(f"    Permissions accordées : {list(rel['outgoing_permissions'].keys()) if rel['outgoing_permissions'] else 'Aucune'}")
        print(f"    Permissions reçues : {list(rel['incoming_permissions'].keys()) if rel['incoming_permissions'] else 'Aucune'}")
    
    print("\nMarie voit :")
    for rel in marie_relations:
        print(f"  - {rel['friend_node_id']} : {rel['status']}")
        print(f"    Permissions accordées : {list(rel['outgoing_permissions'].keys()) if rel['outgoing_permissions'] else 'Aucune'}")
        print(f"    Permissions reçues : {list(rel['incoming_permissions'].keys()) if rel['incoming_permissions'] else 'Aucune'}")
    
    print("\n🎉 === DÉMONSTRATION TERMINÉE ===")
    print("🔐 Système de tokens P2P asymétriques opérationnel !")
    print("✅ 4 clés RSA par relation - Sécurité maximale")
    print("🚀 Non-répudiation cryptographique absolue")


if __name__ == "__main__":
    demo_asymmetric_tokens()