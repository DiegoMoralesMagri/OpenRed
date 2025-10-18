# === OpenRed P2P Friendship Protocol ===
# Système d'amitié P2P avec autorisations granulaires
# Gestion demandes, acceptations, permissions et relations sociales

import json
import time
import asyncio
import hashlib
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import os

class FriendshipStatus(Enum):
    """Statuts des relations d'amitié"""
    PENDING_SENT = "pending_sent"        # Demande envoyée, en attente
    PENDING_RECEIVED = "pending_received" # Demande reçue, en attente
    ACCEPTED = "accepted"                # Amitié acceptée
    BLOCKED = "blocked"                  # Utilisateur bloqué
    REJECTED = "rejected"                # Demande refusée

class PermissionLevel(Enum):
    """Niveaux d'autorisation pour amis"""
    NONE = 0           # Aucune permission
    BASIC = 1          # Messages uniquement
    MEDIUM = 2         # Messages + URN publics
    HIGH = 3           # Messages + URN + Photos
    FULL = 4           # Accès complet

@dataclass
class FriendshipPermissions:
    """Permissions accordées à un ami"""
    messaging: bool = False           # Autoriser messages privés
    urn_access: bool = False         # Accès aux URN Phantom
    photo_sharing: bool = False      # Partage de photos
    file_sharing: bool = False       # Partage de fichiers
    presence_info: bool = False      # Voir statut en ligne
    custom_permissions: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.custom_permissions is None:
            self.custom_permissions = {}
    
    @classmethod
    def from_level(cls, level: PermissionLevel):
        """Créer permissions depuis niveau prédéfini"""
        if level == PermissionLevel.NONE:
            return cls()
        elif level == PermissionLevel.BASIC:
            return cls(messaging=True)
        elif level == PermissionLevel.MEDIUM:
            return cls(messaging=True, urn_access=True, presence_info=True)
        elif level == PermissionLevel.HIGH:
            return cls(messaging=True, urn_access=True, photo_sharing=True, presence_info=True)
        elif level == PermissionLevel.FULL:
            return cls(messaging=True, urn_access=True, photo_sharing=True, 
                      file_sharing=True, presence_info=True)
        return cls()

@dataclass
class FriendshipRequest:
    """Demande d'amitié P2P"""
    from_fingerprint: str
    to_fingerprint: str
    from_node_id: str
    to_node_id: str
    message: str
    requested_permissions: FriendshipPermissions
    timestamp: float
    request_id: str
    signature: Optional[str] = None
    
    def __post_init__(self):
        if not self.request_id:
            # Générer ID unique basé sur les participants et timestamp
            content = f"{self.from_fingerprint}:{self.to_fingerprint}:{self.timestamp}"
            self.request_id = hashlib.sha256(content.encode()).hexdigest()[:16]

@dataclass
class Friendship:
    """Relation d'amitié établie"""
    friend_fingerprint: str
    friend_node_id: str
    status: FriendshipStatus
    permissions_granted: FriendshipPermissions  # Permissions que j'accorde
    permissions_received: FriendshipPermissions # Permissions qu'il m'accorde
    created_at: float
    last_interaction: float
    trust_score: float = 1.0  # Score de confiance (0-1)
    notes: str = ""
    
    def update_interaction(self):
        """Met à jour timestamp dernière interaction"""
        self.last_interaction = time.time()

class FriendshipProtocol:
    """Protocole de gestion des amitiés P2P"""
    
    def __init__(self, node_id: str, fingerprint: str, private_key, public_key):
        self.node_id = node_id
        self.fingerprint = fingerprint
        self.private_key = private_key
        self.public_key = public_key
        
        # Stockage des relations
        self.friendships: Dict[str, Friendship] = {}  # fingerprint -> Friendship
        self.pending_requests: Dict[str, FriendshipRequest] = {}  # request_id -> Request
        
        # Callbacks pour événements
        self.on_friendship_request = None
        self.on_friendship_accepted = None
        self.on_friendship_rejected = None
        self.on_message_received = None
        
        # Chargement relations existantes
        self.storage_path = f"./friendship_data_{node_id}"
        os.makedirs(self.storage_path, exist_ok=True)
        self._load_friendships()
        
        print(f"👥 Friendship Protocol initialized")
        print(f"   Node: {node_id}")
        print(f"   Fingerprint: {fingerprint[:12]}...")
        print(f"   Friends: {len(self.friendships)}")
        print(f"   Storage: {self.storage_path}")
    
    def _load_friendships(self):
        """Charge les amitiés depuis le stockage"""
        try:
            friendships_file = os.path.join(self.storage_path, "friendships.json")
            if os.path.exists(friendships_file):
                with open(friendships_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for fp, friend_data in data.items():
                    # Reconstituer les permissions
                    perms_granted = FriendshipPermissions(**friend_data['permissions_granted'])
                    perms_received = FriendshipPermissions(**friend_data['permissions_received'])
                    
                    friendship = Friendship(
                        friend_fingerprint=friend_data['friend_fingerprint'],
                        friend_node_id=friend_data['friend_node_id'],
                        status=FriendshipStatus(friend_data['status']),
                        permissions_granted=perms_granted,
                        permissions_received=perms_received,
                        created_at=friend_data['created_at'],
                        last_interaction=friend_data['last_interaction'],
                        trust_score=friend_data.get('trust_score', 1.0),
                        notes=friend_data.get('notes', '')
                    )
                    self.friendships[fp] = friendship
                    
                print(f"📂 Loaded {len(self.friendships)} friendships")
                
        except Exception as e:
            print(f"⚠️ Error loading friendships: {e}")
    
    def _save_friendships(self):
        """Sauvegarde les amitiés"""
        try:
            friendships_file = os.path.join(self.storage_path, "friendships.json")
            data = {}
            
            for fp, friendship in self.friendships.items():
                data[fp] = {
                    'friend_fingerprint': friendship.friend_fingerprint,
                    'friend_node_id': friendship.friend_node_id,
                    'status': friendship.status.value,
                    'permissions_granted': asdict(friendship.permissions_granted),
                    'permissions_received': asdict(friendship.permissions_received),
                    'created_at': friendship.created_at,
                    'last_interaction': friendship.last_interaction,
                    'trust_score': friendship.trust_score,
                    'notes': friendship.notes
                }
            
            with open(friendships_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error saving friendships: {e}")
    
    def _sign_message(self, message: str) -> str:
        """Signe un message avec la clé privée"""
        try:
            signature = self.private_key.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature.hex()
        except Exception as e:
            print(f"⚠️ Error signing message: {e}")
            return ""
    
    def send_friendship_request(
        self, 
        target_fingerprint: str, 
        target_node_id: str,
        message: str = "Demande d'amitié",
        permissions: Optional[FriendshipPermissions] = None
    ) -> FriendshipRequest:
        """Envoie une demande d'amitié"""
        
        if permissions is None:
            permissions = FriendshipPermissions.from_level(PermissionLevel.BASIC)
        
        # Créer la demande
        request = FriendshipRequest(
            from_fingerprint=self.fingerprint,
            to_fingerprint=target_fingerprint,
            from_node_id=self.node_id,
            to_node_id=target_node_id,
            message=message,
            requested_permissions=permissions,
            timestamp=time.time(),
            request_id=""  # Sera généré automatiquement
        )
        
        # Signer la demande
        request_data = f"{request.from_fingerprint}:{request.to_fingerprint}:{request.timestamp}:{request.message}"
        request.signature = self._sign_message(request_data)
        
        # Stocker comme demande envoyée
        self.pending_requests[request.request_id] = request
        
        # Créer relation en attente
        friendship = Friendship(
            friend_fingerprint=target_fingerprint,
            friend_node_id=target_node_id,
            status=FriendshipStatus.PENDING_SENT,
            permissions_granted=permissions,
            permissions_received=FriendshipPermissions(),
            created_at=time.time(),
            last_interaction=time.time()
        )
        self.friendships[target_fingerprint] = friendship
        self._save_friendships()
        
        print(f"👥 Friendship request sent to {target_node_id}")
        print(f"   Request ID: {request.request_id}")
        print(f"   Permissions: {permissions.messaging}, {permissions.urn_access}, {permissions.photo_sharing}")
        
        return request
    
    def receive_friendship_request(self, request_data: Dict) -> bool:
        """Reçoit et traite une demande d'amitié"""
        try:
            # Reconstituer la demande
            perms_data = request_data['requested_permissions']
            permissions = FriendshipPermissions(**perms_data)
            
            request = FriendshipRequest(
                from_fingerprint=request_data['from_fingerprint'],
                to_fingerprint=request_data['to_fingerprint'],
                from_node_id=request_data['from_node_id'],
                to_node_id=request_data['to_node_id'],
                message=request_data['message'],
                requested_permissions=permissions,
                timestamp=request_data['timestamp'],
                request_id=request_data['request_id'],
                signature=request_data.get('signature')
            )
            
            # Vérifier que c'est bien pour nous
            if request.to_fingerprint != self.fingerprint:
                return False
            
            # Stocker la demande reçue
            self.pending_requests[request.request_id] = request
            
            # Créer/mettre à jour la relation
            if request.from_fingerprint in self.friendships:
                friendship = self.friendships[request.from_fingerprint]
                friendship.status = FriendshipStatus.PENDING_RECEIVED
            else:
                friendship = Friendship(
                    friend_fingerprint=request.from_fingerprint,
                    friend_node_id=request.from_node_id,
                    status=FriendshipStatus.PENDING_RECEIVED,
                    permissions_granted=FriendshipPermissions(),
                    permissions_received=permissions,
                    created_at=time.time(),
                    last_interaction=time.time()
                )
                self.friendships[request.from_fingerprint] = friendship
            
            self._save_friendships()
            
            print(f"👥 Friendship request received from {request.from_node_id}")
            print(f"   Message: {request.message}")
            print(f"   Requested permissions: {permissions.messaging}, {permissions.urn_access}")
            
            # Callback notification
            if self.on_friendship_request:
                self.on_friendship_request(request)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error processing friendship request: {e}")
            return False
    
    def accept_friendship_request(
        self, 
        request_id: str, 
        granted_permissions: Optional[FriendshipPermissions] = None
    ) -> bool:
        """Accepte une demande d'amitié"""
        
        if request_id not in self.pending_requests:
            return False
        
        request = self.pending_requests[request_id]
        
        if granted_permissions is None:
            granted_permissions = FriendshipPermissions.from_level(PermissionLevel.BASIC)
        
        # Mettre à jour la relation
        if request.from_fingerprint in self.friendships:
            friendship = self.friendships[request.from_fingerprint]
            friendship.status = FriendshipStatus.ACCEPTED
            friendship.permissions_granted = granted_permissions
            friendship.permissions_received = request.requested_permissions
            friendship.update_interaction()
            
            self._save_friendships()
            
            # Nettoyer la demande
            del self.pending_requests[request_id]
            
            print(f"✅ Friendship accepted with {request.from_node_id}")
            print(f"   Granted permissions: {granted_permissions.messaging}, {granted_permissions.urn_access}")
            
            # Callback notification
            if self.on_friendship_accepted:
                self.on_friendship_accepted(friendship)
            
            return True
        
        return False
    
    def reject_friendship_request(self, request_id: str, reason: str = "") -> bool:
        """Rejette une demande d'amitié"""
        
        if request_id not in self.pending_requests:
            return False
        
        request = self.pending_requests[request_id]
        
        # Mettre à jour la relation
        if request.from_fingerprint in self.friendships:
            friendship = self.friendships[request.from_fingerprint]
            friendship.status = FriendshipStatus.REJECTED
            friendship.notes = reason
            friendship.update_interaction()
            
            self._save_friendships()
            
            # Nettoyer la demande
            del self.pending_requests[request_id]
            
            print(f"❌ Friendship rejected with {request.from_node_id}")
            if reason:
                print(f"   Reason: {reason}")
            
            # Callback notification
            if self.on_friendship_rejected:
                self.on_friendship_rejected(request, reason)
            
            return True
        
        return False
    
    def block_user(self, fingerprint: str) -> bool:
        """Bloque un utilisateur"""
        if fingerprint in self.friendships:
            friendship = self.friendships[fingerprint]
            friendship.status = FriendshipStatus.BLOCKED
            friendship.permissions_granted = FriendshipPermissions()
            friendship.permissions_received = FriendshipPermissions()
            friendship.update_interaction()
            
            self._save_friendships()
            
            print(f"🚫 User blocked: {friendship.friend_node_id}")
            return True
        
        return False
    
    def is_friend(self, fingerprint: str) -> bool:
        """Vérifie si c'est un ami accepté"""
        return (fingerprint in self.friendships and 
                self.friendships[fingerprint].status == FriendshipStatus.ACCEPTED)
    
    def has_permission(self, fingerprint: str, permission: str) -> bool:
        """Vérifie si un ami a une permission spécifique"""
        if not self.is_friend(fingerprint):
            return False
        
        friendship = self.friendships[fingerprint]
        return getattr(friendship.permissions_granted, permission, False)
    
    def get_friends_list(self) -> List[Friendship]:
        """Retourne la liste des amis acceptés"""
        return [f for f in self.friendships.values() 
                if f.status == FriendshipStatus.ACCEPTED]
    
    def get_pending_requests(self) -> List[FriendshipRequest]:
        """Retourne les demandes en attente"""
        return [r for r in self.pending_requests.values()]
    
    def get_friendship_stats(self) -> Dict:
        """Statistiques des relations d'amitié"""
        stats = {
            'total_friends': len([f for f in self.friendships.values() 
                                if f.status == FriendshipStatus.ACCEPTED]),
            'pending_sent': len([f for f in self.friendships.values() 
                               if f.status == FriendshipStatus.PENDING_SENT]),
            'pending_received': len([f for f in self.friendships.values() 
                                   if f.status == FriendshipStatus.PENDING_RECEIVED]),
            'blocked': len([f for f in self.friendships.values() 
                          if f.status == FriendshipStatus.BLOCKED]),
            'total_requests': len(self.pending_requests)
        }
        return stats