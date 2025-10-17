# === OpenRed P2P Conditional URN Sharing ===
# Système de partage sélectif Phantom URN basé sur les permissions d'amitié
# Contrôle d'accès granulaire et cache distribué intelligent

import json
import time
import hashlib
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os

class URNAccessLevel(Enum):
    """Niveaux d'accès aux URN"""
    PRIVATE = 0        # Accès privé uniquement
    FRIENDS_ONLY = 1   # Amis seulement
    FRIENDS_URN = 2    # Amis avec permission URN
    FRIENDS_PHOTOS = 3 # Amis avec permission photos
    PUBLIC = 4         # Accès public

@dataclass
class URNAccessRule:
    """Règle d'accès pour un URN"""
    urn_id: str
    owner_fingerprint: str
    access_level: URNAccessLevel
    allowed_fingerprints: Set[str]
    blocked_fingerprints: Set[str]
    created_at: float
    expires_at: Optional[float] = None
    usage_count: int = 0
    max_usage: Optional[int] = None
    
    def __post_init__(self):
        if isinstance(self.allowed_fingerprints, list):
            self.allowed_fingerprints = set(self.allowed_fingerprints)
        if isinstance(self.blocked_fingerprints, list):
            self.blocked_fingerprints = set(self.blocked_fingerprints)

@dataclass
class URNShareLog:
    """Journal des partages d'URN"""
    urn_id: str
    shared_by: str
    shared_with: str
    shared_at: float
    access_granted: bool
    reason: str

class ConditionalURNSharing:
    """Système de partage conditionnel Phantom URN"""
    
    def __init__(self, node_id: str, fingerprint: str, friendship_protocol, phantom_urn_engine):
        self.node_id = node_id
        self.fingerprint = fingerprint
        self.friendship_protocol = friendship_protocol
        self.phantom_urn_engine = phantom_urn_engine
        
        # Règles d'accès aux URN
        self.access_rules: Dict[str, URNAccessRule] = {}  # urn_id -> URNAccessRule
        self.share_logs: List[URNShareLog] = []
        
        # Cache des URN partagés avec nous
        self.received_urns: Dict[str, Dict] = {}  # urn_id -> metadata
        
        # Stockage persistant
        self.storage_path = f"./urn_sharing_{node_id}"
        os.makedirs(self.storage_path, exist_ok=True)
        self._load_sharing_data()
        
        print(f"🔱 Conditional URN Sharing initialized")
        print(f"   Node: {node_id}")
        print(f"   Access rules: {len(self.access_rules)}")
        print(f"   Storage: {self.storage_path}")
    
    def _load_sharing_data(self):
        """Charge les données de partage"""
        try:
            # Charger règles d'accès
            rules_file = os.path.join(self.storage_path, "access_rules.json")
            if os.path.exists(rules_file):
                with open(rules_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for urn_id, rule_data in data.items():
                    rule = URNAccessRule(
                        urn_id=rule_data['urn_id'],
                        owner_fingerprint=rule_data['owner_fingerprint'],
                        access_level=URNAccessLevel(rule_data['access_level']),
                        allowed_fingerprints=set(rule_data['allowed_fingerprints']),
                        blocked_fingerprints=set(rule_data['blocked_fingerprints']),
                        created_at=rule_data['created_at'],
                        expires_at=rule_data.get('expires_at'),
                        usage_count=rule_data.get('usage_count', 0),
                        max_usage=rule_data.get('max_usage')
                    )
                    self.access_rules[urn_id] = rule
            
            # Charger logs de partage
            logs_file = os.path.join(self.storage_path, "share_logs.json")
            if os.path.exists(logs_file):
                with open(logs_file, 'r', encoding='utf-8') as f:
                    logs_data = json.load(f)
                
                for log_data in logs_data:
                    log = URNShareLog(**log_data)
                    self.share_logs.append(log)
            
            # Charger URN reçus
            received_file = os.path.join(self.storage_path, "received_urns.json")
            if os.path.exists(received_file):
                with open(received_file, 'r', encoding='utf-8') as f:
                    self.received_urns = json.load(f)
            
            print(f"📂 Loaded sharing data: {len(self.access_rules)} rules, {len(self.share_logs)} logs")
            
        except Exception as e:
            print(f"⚠️ Error loading sharing data: {e}")
    
    def _save_sharing_data(self):
        """Sauvegarde les données de partage"""
        try:
            # Sauvegarder règles d'accès
            rules_file = os.path.join(self.storage_path, "access_rules.json")
            rules_data = {}
            for urn_id, rule in self.access_rules.items():
                rules_data[urn_id] = {
                    'urn_id': rule.urn_id,
                    'owner_fingerprint': rule.owner_fingerprint,
                    'access_level': rule.access_level.value,
                    'allowed_fingerprints': list(rule.allowed_fingerprints),
                    'blocked_fingerprints': list(rule.blocked_fingerprints),
                    'created_at': rule.created_at,
                    'expires_at': rule.expires_at,
                    'usage_count': rule.usage_count,
                    'max_usage': rule.max_usage
                }
            
            with open(rules_file, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)
            
            # Sauvegarder logs
            logs_file = os.path.join(self.storage_path, "share_logs.json")
            logs_data = [asdict(log) for log in self.share_logs]
            
            with open(logs_file, 'w', encoding='utf-8') as f:
                json.dump(logs_data, f, indent=2, ensure_ascii=False)
            
            # Sauvegarder URN reçus
            received_file = os.path.join(self.storage_path, "received_urns.json")
            with open(received_file, 'w', encoding='utf-8') as f:
                json.dump(self.received_urns, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error saving sharing data: {e}")
    
    def create_urn_access_rule(
        self, 
        urn_id: str, 
        access_level: URNAccessLevel,
        allowed_fingerprints: Optional[Set[str]] = None,
        expires_hours: Optional[int] = None,
        max_usage: Optional[int] = None
    ) -> URNAccessRule:
        """Crée une règle d'accès pour un URN"""
        
        if allowed_fingerprints is None:
            allowed_fingerprints = set()
        
        expires_at = None
        if expires_hours:
            expires_at = time.time() + (expires_hours * 3600)
        
        rule = URNAccessRule(
            urn_id=urn_id,
            owner_fingerprint=self.fingerprint,
            access_level=access_level,
            allowed_fingerprints=allowed_fingerprints,
            blocked_fingerprints=set(),
            created_at=time.time(),
            expires_at=expires_at,
            max_usage=max_usage
        )
        
        self.access_rules[urn_id] = rule
        self._save_sharing_data()
        
        print(f"🔱 URN access rule created for {urn_id}")
        print(f"   Access level: {access_level.name}")
        print(f"   Allowed friends: {len(allowed_fingerprints)}")
        if expires_at:
            print(f"   Expires: {time.ctime(expires_at)}")
        
        return rule
    
    def check_urn_access(self, urn_id: str, requester_fingerprint: str) -> Tuple[bool, str]:
        """Vérifie si un utilisateur peut accéder à un URN"""
        
        # URN n'existe pas
        if urn_id not in self.access_rules:
            return False, "URN not found or no access rule"
        
        rule = self.access_rules[urn_id]
        
        # Vérifier expiration
        if rule.expires_at and time.time() > rule.expires_at:
            return False, "Access rule expired"
        
        # Vérifier limite d'usage
        if rule.max_usage and rule.usage_count >= rule.max_usage:
            return False, "Usage limit exceeded"
        
        # Propriétaire a toujours accès
        if requester_fingerprint == rule.owner_fingerprint:
            return True, "Owner access"
        
        # Vérifier blocage explicite
        if requester_fingerprint in rule.blocked_fingerprints:
            return False, "User blocked"
        
        # Accès privé uniquement au propriétaire
        if rule.access_level == URNAccessLevel.PRIVATE:
            return False, "Private URN"
        
        # Accès public
        if rule.access_level == URNAccessLevel.PUBLIC:
            return True, "Public access"
        
        # Vérifier amitié
        if not self.friendship_protocol.is_friend(requester_fingerprint):
            return False, "Not a friend"
        
        # Accès amis uniquement
        if rule.access_level == URNAccessLevel.FRIENDS_ONLY:
            return True, "Friend access"
        
        # Vérifier permissions spécifiques
        if rule.access_level == URNAccessLevel.FRIENDS_URN:
            if self.friendship_protocol.has_permission(requester_fingerprint, 'urn_access'):
                return True, "Friend with URN permission"
            else:
                return False, "Friend without URN permission"
        
        if rule.access_level == URNAccessLevel.FRIENDS_PHOTOS:
            if self.friendship_protocol.has_permission(requester_fingerprint, 'photo_sharing'):
                return True, "Friend with photo permission"
            else:
                return False, "Friend without photo permission"
        
        # Vérifier liste explicite
        if requester_fingerprint in rule.allowed_fingerprints:
            return True, "Explicitly allowed"
        
        return False, "Access denied"
    
    def request_urn_access(self, urn_id: str, owner_fingerprint: str) -> Optional[Dict]:
        """Demande l'accès à un URN d'un autre nœud"""
        
        # Vérifier si on est ami avec le propriétaire
        if not self.friendship_protocol.is_friend(owner_fingerprint):
            print(f"❌ Cannot request URN {urn_id} - not friends with owner")
            return None
        
        # Vérifier nos permissions
        has_urn_permission = self.friendship_protocol.has_permission(owner_fingerprint, 'urn_access')
        has_photo_permission = self.friendship_protocol.has_permission(owner_fingerprint, 'photo_sharing')
        
        if not has_urn_permission:
            print(f"❌ Cannot request URN {urn_id} - no URN permission from owner")
            return None
        
        # TODO: Envoyer requête P2P pour demander l'URN
        # Pour l'instant, simulation
        print(f"🔱 URN access requested: {urn_id}")
        print(f"   Owner: {owner_fingerprint[:12]}...")
        print(f"   URN permission: {has_urn_permission}")
        print(f"   Photo permission: {has_photo_permission}")
        
        return {
            'urn_id': urn_id,
            'owner_fingerprint': owner_fingerprint,
            'requested_at': time.time(),
            'permissions': {
                'urn_access': has_urn_permission,
                'photo_sharing': has_photo_permission
            }
        }
    
    def share_urn_with_friend(
        self, 
        urn_id: str, 
        friend_fingerprint: str, 
        message: str = ""
    ) -> bool:
        """Partage un URN avec un ami spécifique"""
        
        # Vérifier que l'URN existe dans nos règles
        if urn_id not in self.access_rules:
            print(f"❌ Cannot share URN {urn_id} - no access rule found")
            return False
        
        # Vérifier l'accès
        can_access, reason = self.check_urn_access(urn_id, friend_fingerprint)
        
        # Logger la tentative
        log = URNShareLog(
            urn_id=urn_id,
            shared_by=self.fingerprint,
            shared_with=friend_fingerprint,
            shared_at=time.time(),
            access_granted=can_access,
            reason=reason
        )
        self.share_logs.append(log)
        
        if can_access:
            # Incrémenter compteur d'usage
            self.access_rules[urn_id].usage_count += 1
            self._save_sharing_data()
            
            # TODO: Envoyer URN via messagerie sociale
            print(f"✅ URN shared: {urn_id}")
            print(f"   With: {friend_fingerprint[:12]}...")
            print(f"   Reason: {reason}")
            
            return True
        else:
            print(f"❌ URN sharing denied: {urn_id}")
            print(f"   Reason: {reason}")
            return False
    
    def receive_shared_urn(self, urn_id: str, urn_metadata: Dict, sender_fingerprint: str):
        """Reçoit un URN partagé"""
        
        # Vérifier que l'expéditeur est un ami
        if not self.friendship_protocol.is_friend(sender_fingerprint):
            print(f"❌ Rejected URN from non-friend: {sender_fingerprint}")
            return
        
        # Stocker l'URN reçu
        self.received_urns[urn_id] = {
            'metadata': urn_metadata,
            'received_from': sender_fingerprint,
            'received_at': time.time(),
            'access_level': 'shared_with_me'
        }
        
        # Ajouter au cache Phantom URN si possible
        if hasattr(self.phantom_urn_engine, 'add_shared_urn'):
            self.phantom_urn_engine.add_shared_urn(urn_id, urn_metadata, sender_fingerprint)
        
        self._save_sharing_data()
        
        print(f"🔱 URN received and cached: {urn_id}")
        print(f"   From: {sender_fingerprint[:12]}...")
        print(f"   Metadata: {list(urn_metadata.keys())}")
    
    def get_my_shared_urns(self) -> List[Dict]:
        """Liste des URN que j'ai partagés"""
        shared_urns = []
        
        for urn_id, rule in self.access_rules.items():
            if rule.owner_fingerprint == self.fingerprint:
                # Compter les partages
                share_count = len([log for log in self.share_logs 
                                 if log.urn_id == urn_id and log.access_granted])
                
                shared_urns.append({
                    'urn_id': urn_id,
                    'access_level': rule.access_level.name,
                    'created_at': rule.created_at,
                    'expires_at': rule.expires_at,
                    'usage_count': rule.usage_count,
                    'max_usage': rule.max_usage,
                    'share_count': share_count,
                    'allowed_friends': len(rule.allowed_fingerprints)
                })
        
        return shared_urns
    
    def get_received_urns(self) -> List[Dict]:
        """Liste des URN reçus de mes amis"""
        received_list = []
        
        for urn_id, urn_data in self.received_urns.items():
            received_list.append({
                'urn_id': urn_id,
                'received_from': urn_data['received_from'],
                'received_at': urn_data['received_at'],
                'metadata': urn_data['metadata']
            })
        
        return received_list
    
    def get_sharing_stats(self) -> Dict:
        """Statistiques de partage URN"""
        total_rules = len(self.access_rules)
        my_urns = len([r for r in self.access_rules.values() 
                      if r.owner_fingerprint == self.fingerprint])
        received_urns = len(self.received_urns)
        
        successful_shares = len([log for log in self.share_logs if log.access_granted])
        denied_shares = len([log for log in self.share_logs if not log.access_granted])
        
        return {
            'total_access_rules': total_rules,
            'my_shared_urns': my_urns,
            'received_urns': received_urns,
            'successful_shares': successful_shares,
            'denied_shares': denied_shares,
            'total_share_attempts': len(self.share_logs)
        }
    
    def cleanup_expired_rules(self):
        """Nettoie les règles expirées"""
        current_time = time.time()
        expired_urns = []
        
        for urn_id, rule in self.access_rules.items():
            if rule.expires_at and current_time > rule.expires_at:
                expired_urns.append(urn_id)
        
        for urn_id in expired_urns:
            del self.access_rules[urn_id]
            print(f"🗑️ Expired URN rule removed: {urn_id}")
        
        if expired_urns:
            self._save_sharing_data()
        
        return len(expired_urns)