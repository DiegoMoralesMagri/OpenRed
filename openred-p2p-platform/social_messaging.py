# === OpenRed P2P Social Messaging System ===
# Messagerie P2P chiffrée entre amis avec autorisations
# Support messages texte, fichiers, URN Phantom

import json
import time
import asyncio
import hashlib
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

class MessageType(Enum):
    """Types de messages P2P"""
    TEXT = "text"                    # Message texte simple
    URN_SHARE = "urn_share"         # Partage URN Phantom
    FILE_SHARE = "file_share"       # Partage de fichier
    PHOTO_SHARE = "photo_share"     # Partage de photo
    SYSTEM = "system"               # Message système
    FRIENDSHIP_REQUEST = "friendship_request"  # Demande d'amitié
    FRIENDSHIP_RESPONSE = "friendship_response"  # Réponse demande

class MessageStatus(Enum):
    """Statut des messages"""
    PENDING = "pending"       # En attente d'envoi
    SENT = "sent"            # Envoyé
    DELIVERED = "delivered"   # Délivré
    READ = "read"            # Lu
    FAILED = "failed"        # Échec envoi

@dataclass
class Message:
    """Message P2P chiffré"""
    message_id: str
    from_fingerprint: str
    to_fingerprint: str
    message_type: MessageType
    content: str
    metadata: Dict[str, Any]
    timestamp: float
    encrypted: bool = True
    signature: Optional[str] = None
    status: MessageStatus = MessageStatus.PENDING
    reply_to: Optional[str] = None  # ID message parent pour réponses
    
    def __post_init__(self):
        if not self.message_id:
            # Générer ID unique
            content_hash = hashlib.sha256(
                f"{self.from_fingerprint}:{self.to_fingerprint}:{self.timestamp}:{self.content}".encode()
            ).hexdigest()
            self.message_id = content_hash[:16]

@dataclass
class Conversation:
    """Conversation entre participants (vue agrégée)"""
    participants: List[str]  # Liste des fingerprints participants
    participant_names: Dict[str, str]  # fingerprint -> node_id
    last_message_time: float
    unread_count: int = 0
    is_group: bool = False
    
    def get_conversation_id(self) -> str:
        """ID unique de la conversation basé sur les participants"""
        sorted_participants = sorted(self.participants)
        return hashlib.sha256(":".join(sorted_participants).encode()).hexdigest()[:16]

@dataclass
class MessageSyncInfo:
    """Informations de synchronisation des messages"""
    participant_fingerprint: str
    last_sync_timestamp: float
    message_count: int
    last_message_id: Optional[str] = None

class DistributedMessaging:
    """Système de messagerie distribuée P2P"""
    
    def __init__(self, node_id: str, fingerprint: str, private_key, public_key, friendship_protocol):
        self.node_id = node_id
        self.fingerprint = fingerprint
        self.private_key = private_key
        self.public_key = public_key
        self.friendship_protocol = friendship_protocol
        
        # Stockage local - SEULEMENT MES MESSAGES ENVOYÉS
        self.sent_messages: Dict[str, Message] = {}  # message_id -> Message (mes envois)
        
        # Cache temporaire des messages reçus (pour performance)
        self.message_cache: Dict[str, Message] = {}  # message_id -> Message (cache temporaire)
        self.cache_expiry: Dict[str, float] = {}     # message_id -> timestamp expiration
        
        # Conversations actives et synchronisation
        self.conversations: Dict[str, Conversation] = {}  # conversation_id -> Conversation
        self.sync_info: Dict[str, MessageSyncInfo] = {}   # participant_fp -> sync info
        
        # Callbacks
        self.on_message_received = None
        self.on_message_sent = None
        self.on_conversation_updated = None
        
        # Stockage persistant
        self.storage_path = f"./distributed_messages_{node_id}"
        os.makedirs(self.storage_path, exist_ok=True)
        self._load_distributed_data()
        
        print(f"💬 Distributed Messaging initialized")
        print(f"   Node: {node_id}")
        print(f"   Sent messages: {len(self.sent_messages)}")
        print(f"   Active conversations: {len(self.conversations)}")
        print(f"   Storage: {self.storage_path}")
    
    def _load_distributed_data(self):
        """Charge les données distribuées"""
        try:
            # Charger MES messages envoyés uniquement
            sent_file = os.path.join(self.storage_path, "sent_messages.json")
            if os.path.exists(sent_file):
                with open(sent_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for msg_id, msg_data in data.items():
                    message = Message(
                        message_id=msg_data['message_id'],
                        from_fingerprint=msg_data['from_fingerprint'],
                        to_fingerprint=msg_data['to_fingerprint'],
                        message_type=MessageType(msg_data['message_type']),
                        content=msg_data['content'],
                        metadata=msg_data['metadata'],
                        timestamp=msg_data['timestamp'],
                        encrypted=msg_data.get('encrypted', True),
                        signature=msg_data.get('signature'),
                        status=MessageStatus(msg_data.get('status', 'sent')),
                        reply_to=msg_data.get('reply_to')
                    )
                    self.sent_messages[msg_id] = message
            
            # Charger informations de synchronisation
            sync_file = os.path.join(self.storage_path, "sync_info.json")
            if os.path.exists(sync_file):
                with open(sync_file, 'r', encoding='utf-8') as f:
                    sync_data = json.load(f)
                
                for fp, info_data in sync_data.items():
                    sync_info = MessageSyncInfo(
                        participant_fingerprint=info_data['participant_fingerprint'],
                        last_sync_timestamp=info_data['last_sync_timestamp'],
                        message_count=info_data['message_count'],
                        last_message_id=info_data.get('last_message_id')
                    )
                    self.sync_info[fp] = sync_info
            
            # Charger conversations
            conv_file = os.path.join(self.storage_path, "conversations.json")
            if os.path.exists(conv_file):
                with open(conv_file, 'r', encoding='utf-8') as f:
                    conv_data = json.load(f)
                
                for conv_id, conv_info in conv_data.items():
                    conversation = Conversation(
                        participants=conv_info['participants'],
                        participant_names=conv_info['participant_names'],
                        last_message_time=conv_info['last_message_time'],
                        unread_count=conv_info.get('unread_count', 0),
                        is_group=conv_info.get('is_group', False)
                    )
                    self.conversations[conv_id] = conversation
            
            print(f"📂 Loaded distributed data: {len(self.sent_messages)} sent messages")
            
        except Exception as e:
            print(f"⚠️ Error loading distributed data: {e}")
    
    def _save_distributed_data(self):
        """Sauvegarde les données distribuées"""
        try:
            # Sauvegarder MES messages envoyés uniquement
            sent_file = os.path.join(self.storage_path, "sent_messages.json")
            sent_data = {}
            for msg_id, message in self.sent_messages.items():
                sent_data[msg_id] = {
                    'message_id': message.message_id,
                    'from_fingerprint': message.from_fingerprint,
                    'to_fingerprint': message.to_fingerprint,
                    'message_type': message.message_type.value,
                    'content': message.content,
                    'metadata': message.metadata,
                    'timestamp': message.timestamp,
                    'encrypted': message.encrypted,
                    'signature': message.signature,
                    'status': message.status.value,
                    'reply_to': message.reply_to
                }
            
            with open(sent_file, 'w', encoding='utf-8') as f:
                json.dump(sent_data, f, indent=2, ensure_ascii=False)
            
            # Sauvegarder informations de synchronisation
            sync_file = os.path.join(self.storage_path, "sync_info.json")
            sync_data = {}
            for fp, sync_info in self.sync_info.items():
                sync_data[fp] = {
                    'participant_fingerprint': sync_info.participant_fingerprint,
                    'last_sync_timestamp': sync_info.last_sync_timestamp,
                    'message_count': sync_info.message_count,
                    'last_message_id': sync_info.last_message_id
                }
            
            with open(sync_file, 'w', encoding='utf-8') as f:
                json.dump(sync_data, f, indent=2, ensure_ascii=False)
            
            # Sauvegarder conversations
            conv_file = os.path.join(self.storage_path, "conversations.json")
            conv_data = {}
            for conv_id, conversation in self.conversations.items():
                conv_data[conv_id] = {
                    'participants': conversation.participants,
                    'participant_names': conversation.participant_names,
                    'last_message_time': conversation.last_message_time,
                    'unread_count': conversation.unread_count,
                    'is_group': conversation.is_group
                }
            
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(conv_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error saving distributed data: {e}")
    
    def _encrypt_message(self, content: str, recipient_fingerprint: str) -> str:
        """Chiffre un message pour le destinataire"""
        try:
            # TODO: Implémenter chiffrement hybride RSA+AES
            # Pour l'instant, encodage base64 simple
            return base64.b64encode(content.encode()).decode()
        except Exception as e:
            print(f"⚠️ Error encrypting message: {e}")
            return content
    
    def _decrypt_message(self, encrypted_content: str, sender_fingerprint: str) -> str:
        """Déchiffre un message reçu"""
        try:
            # TODO: Implémenter déchiffrement hybride RSA+AES
            # Pour l'instant, décodage base64 simple
            return base64.b64decode(encrypted_content.encode()).decode()
        except Exception as e:
            print(f"⚠️ Error decrypting message: {e}")
            return encrypted_content
    
    def send_text_message(
        self, 
        recipient_fingerprint: str, 
        content: str, 
        reply_to: Optional[str] = None
    ) -> Optional[Message]:
        """Envoie un message texte à un ami (stockage local uniquement)"""
        
        # Vérifier permission de messagerie
        if not self.friendship_protocol.has_permission(recipient_fingerprint, 'messaging'):
            print(f"❌ No messaging permission for {recipient_fingerprint}")
            return None
        
        # Chiffrer le contenu
        encrypted_content = self._encrypt_message(content, recipient_fingerprint)
        
        # Créer le message
        message = Message(
            message_id="",  # Sera généré automatiquement
            from_fingerprint=self.fingerprint,
            to_fingerprint=recipient_fingerprint,
            message_type=MessageType.TEXT,
            content=encrypted_content,
            metadata={'original_length': len(content)},
            timestamp=time.time(),
            reply_to=reply_to
        )
        
        # Stocker UNIQUEMENT dans mes messages envoyés
        self.sent_messages[message.message_id] = message
        
        # Mettre à jour la conversation locale (métadonnées uniquement)
        self._update_conversation_metadata(recipient_fingerprint, message.timestamp)
        
        # TODO: Envoyer via P2P à l'autre nœud
        self._notify_message_sent(message)
        
        self._save_distributed_data()
        
        print(f"💬 Text message sent to {recipient_fingerprint[:12]}...")
        print(f"   Content: {content[:50]}{'...' if len(content) > 50 else ''}")
        print(f"   Stored locally only - recipient will fetch on demand")
        
        return message
    
    def _update_conversation_metadata(self, participant_fingerprint: str, timestamp: float):
        """Met à jour les métadonnées de conversation sans stocker le message"""
        participants = sorted([self.fingerprint, participant_fingerprint])
        conversation_id = hashlib.sha256(":".join(participants).encode()).hexdigest()[:16]
        
        if conversation_id not in self.conversations:
            # Récupérer nom du participant
            participant_name = "unknown"
            if participant_fingerprint in self.friendship_protocol.friendships:
                participant_name = self.friendship_protocol.friendships[participant_fingerprint].friend_node_id
            
            self.conversations[conversation_id] = Conversation(
                participants=participants,
                participant_names={
                    self.fingerprint: self.node_id,
                    participant_fingerprint: participant_name
                },
                last_message_time=timestamp,
                is_group=False
            )
        else:
            self.conversations[conversation_id].last_message_time = timestamp

    async def fetch_messages_from_participant(
        self, 
        participant_fingerprint: str, 
        since_timestamp: float = 0
    ) -> List[Message]:
        """Récupère les messages d'un participant depuis son serveur"""
        
        if not self.friendship_protocol.is_friend(participant_fingerprint):
            print(f"❌ Cannot fetch messages from non-friend: {participant_fingerprint}")
            return []
        
        try:
            # TODO: Implémenter requête P2P réelle
            # Pour l'instant, simulation
            print(f"� Fetching messages from {participant_fingerprint[:12]}...")
            print(f"   Since: {time.ctime(since_timestamp) if since_timestamp else 'beginning'}")
            
            # Simulation de messages reçus
            fetched_messages = []
            
            # En production, ceci sera une requête P2P réelle
            # messages = await self.p2p_client.request_messages(
            #     target_fingerprint=participant_fingerprint,
            #     conversation_with=self.fingerprint,
            #     since_timestamp=since_timestamp
            # )
            
            # Mettre en cache les messages récupérés
            cache_expiry_time = time.time() + 3600  # Cache 1 heure
            for message in fetched_messages:
                self.message_cache[message.message_id] = message
                self.cache_expiry[message.message_id] = cache_expiry_time
            
            # Mettre à jour les infos de synchronisation
            if participant_fingerprint not in self.sync_info:
                self.sync_info[participant_fingerprint] = MessageSyncInfo(
                    participant_fingerprint=participant_fingerprint,
                    last_sync_timestamp=time.time(),
                    message_count=len(fetched_messages)
                )
            else:
                sync_info = self.sync_info[participant_fingerprint]
                sync_info.last_sync_timestamp = time.time()
                sync_info.message_count += len(fetched_messages)
                if fetched_messages:
                    sync_info.last_message_id = fetched_messages[-1].message_id
            
            self._save_distributed_data()
            
            print(f"✅ Fetched {len(fetched_messages)} messages from {participant_fingerprint[:12]}...")
            return fetched_messages
            
        except Exception as e:
            print(f"⚠️ Error fetching messages from {participant_fingerprint}: {e}")
            return []

    async def get_unified_conversation(
        self, 
        participants: List[str],
        limit: int = 50,
        before_timestamp: Optional[float] = None
    ) -> List[Message]:
        """Récupère une conversation unifiée depuis tous les participants"""
        
        all_messages = []
        
        # Récupérer MES messages envoyés dans cette conversation
        my_messages = []
        for message in self.sent_messages.values():
            # Vérifier si ce message fait partie de cette conversation
            if (message.to_fingerprint in participants or 
                message.from_fingerprint in participants):
                if not before_timestamp or message.timestamp < before_timestamp:
                    my_messages.append(message)
        
        all_messages.extend(my_messages)
        
        # Récupérer les messages des autres participants
        for participant_fp in participants:
            if participant_fp == self.fingerprint:
                continue  # Skip moi-même
            
            # Vérifier cache d'abord
            cached_messages = self._get_cached_messages_from_participant(
                participant_fp, before_timestamp
            )
            all_messages.extend(cached_messages)
            
            # Si pas assez en cache, récupérer depuis le serveur
            if len(cached_messages) < limit // len(participants):
                since_timestamp = 0
                if participant_fp in self.sync_info:
                    since_timestamp = self.sync_info[participant_fp].last_sync_timestamp
                
                fetched_messages = await self.fetch_messages_from_participant(
                    participant_fp, since_timestamp
                )
                
                # Filtrer les messages de cette conversation
                conversation_messages = [
                    msg for msg in fetched_messages
                    if (msg.to_fingerprint == self.fingerprint or 
                        msg.from_fingerprint == self.fingerprint)
                ]
                
                all_messages.extend(conversation_messages)
        
        # Trier par timestamp et limiter
        all_messages.sort(key=lambda m: m.timestamp, reverse=True)
        if limit:
            all_messages = all_messages[:limit]
        
        # Retrier dans l'ordre chronologique pour affichage
        all_messages.reverse()
        
        print(f"📝 Unified conversation: {len(all_messages)} messages from {len(participants)} participants")
        
        return all_messages
    
    def _get_cached_messages_from_participant(
        self, 
        participant_fingerprint: str, 
        before_timestamp: Optional[float] = None
    ) -> List[Message]:
        """Récupère les messages en cache d'un participant"""
        
        cached_messages = []
        current_time = time.time()
        
        for msg_id, message in self.message_cache.items():
            # Vérifier expiration du cache
            if msg_id in self.cache_expiry and current_time > self.cache_expiry[msg_id]:
                continue
            
            # Vérifier participant et timestamp
            if (message.from_fingerprint == participant_fingerprint and
                (not before_timestamp or message.timestamp < before_timestamp)):
                cached_messages.append(message)
        
        return cached_messages
    
    def _cleanup_expired_cache(self):
        """Nettoie le cache expiré"""
        current_time = time.time()
        expired_ids = []
        
        for msg_id, expiry_time in self.cache_expiry.items():
            if current_time > expiry_time:
                expired_ids.append(msg_id)
        
        for msg_id in expired_ids:
            if msg_id in self.message_cache:
                del self.message_cache[msg_id]
            if msg_id in self.cache_expiry:
                del self.cache_expiry[msg_id]
        
        if expired_ids:
            print(f"🗑️ Cleaned {len(expired_ids)} expired cached messages")

    def serve_my_messages_for_conversation(
        self, 
        requester_fingerprint: str, 
        since_timestamp: float = 0
    ) -> List[Message]:
        """Sert mes messages pour une conversation à un ami qui les demande"""
        
        # Vérifier permission
        if not self.friendship_protocol.has_permission(requester_fingerprint, 'messaging'):
            print(f"❌ Message access denied for {requester_fingerprint}")
            return []
        
        # Récupérer mes messages vers cet ami
        messages_for_requester = []
        for message in self.sent_messages.values():
            if (message.to_fingerprint == requester_fingerprint and
                message.timestamp >= since_timestamp):
                messages_for_requester.append(message)
        
        # Trier par timestamp
        messages_for_requester.sort(key=lambda m: m.timestamp)
        
        print(f"📤 Serving {len(messages_for_requester)} messages to {requester_fingerprint[:12]}...")
        
        return messages_for_requester
    
    def send_urn_share(
        self, 
        recipient_fingerprint: str, 
        urn_id: str, 
        urn_metadata: Dict[str, Any],
        message: str = ""
    ) -> Optional[Message]:
        """Partage un URN Phantom avec un ami"""
        
        # Vérifier permissions
        if not self.friendship_protocol.has_permission(recipient_fingerprint, 'urn_access'):
            print(f"❌ No URN sharing permission for {recipient_fingerprint}")
            return None
        
        # Préparer le contenu du partage
        share_content = {
            'urn_id': urn_id,
            'metadata': urn_metadata,
            'message': message,
            'shared_by': self.node_id,
            'shared_at': time.time()
        }
        
        # Chiffrer le contenu
        encrypted_content = self._encrypt_message(json.dumps(share_content), recipient_fingerprint)
        
        # Créer le message
        message_obj = Message(
            message_id="",
            from_fingerprint=self.fingerprint,
            to_fingerprint=recipient_fingerprint,
            message_type=MessageType.URN_SHARE,
            content=encrypted_content,
            metadata={
                'urn_id': urn_id,
                'share_type': 'phantom_urn'
            },
            timestamp=time.time()
        )
        
        # Ajouter à la conversation
        self._add_to_conversation(message_obj)
        
        # Stocker le message comme envoyé (architecture distribuée)
        self.sent_messages[message_obj.message_id] = message_obj
        self._save_distributed_data()
        
        print(f"🔱 URN share sent to {recipient_fingerprint[:12]}...")
        print(f"   URN: {urn_id}")
        print(f"   Message: {message}")
        
        return message_obj
    
    def send_photo_share(
        self, 
        recipient_fingerprint: str, 
        photo_data: bytes, 
        filename: str,
        caption: str = ""
    ) -> Optional[Message]:
        """Partage une photo avec un ami"""
        
        # Vérifier permissions
        if not self.friendship_protocol.has_permission(recipient_fingerprint, 'photo_sharing'):
            print(f"❌ No photo sharing permission for {recipient_fingerprint}")
            return None
        
        # Encoder la photo en base64
        photo_b64 = base64.b64encode(photo_data).decode()
        
        # Préparer le contenu
        share_content = {
            'filename': filename,
            'photo_data': photo_b64,
            'caption': caption,
            'size': len(photo_data),
            'shared_by': self.node_id,
            'shared_at': time.time()
        }
        
        # Chiffrer le contenu
        encrypted_content = self._encrypt_message(json.dumps(share_content), recipient_fingerprint)
        
        # Créer le message
        message = Message(
            message_id="",
            from_fingerprint=self.fingerprint,
            to_fingerprint=recipient_fingerprint,
            message_type=MessageType.PHOTO_SHARE,
            content=encrypted_content,
            metadata={
                'filename': filename,
                'size': len(photo_data),
                'caption': caption
            },
            timestamp=time.time()
        )
        
        # Ajouter à la conversation
        self._add_to_conversation(message)
        
        # Stocker le message comme envoyé (architecture distribuée)
        self.sent_messages[message.message_id] = message
        self._save_distributed_data()
        
        print(f"📷 Photo share sent to {recipient_fingerprint[:12]}...")
        print(f"   File: {filename} ({len(photo_data)} bytes)")
        print(f"   Caption: {caption}")
        
        return message
    
    def receive_message(self, message_data: Dict) -> bool:
        """Reçoit notification d'un nouveau message (mais ne le stocke pas)"""
        try:
            # Reconstituer le message
            message = Message(
                message_id=message_data['message_id'],
                from_fingerprint=message_data['from_fingerprint'],
                to_fingerprint=message_data['to_fingerprint'],
                message_type=MessageType(message_data['message_type']),
                content=message_data['content'],
                metadata=message_data['metadata'],
                timestamp=message_data['timestamp'],
                encrypted=message_data.get('encrypted', True),
                signature=message_data.get('signature'),
                status=MessageStatus.DELIVERED,
                reply_to=message_data.get('reply_to')
            )
            
            # Vérifier que c'est pour nous
            if message.to_fingerprint != self.fingerprint:
                return False
            
            # Vérifier permission d'envoi
            if not self.friendship_protocol.has_permission(message.from_fingerprint, 'messaging'):
                print(f"❌ Rejected message from {message.from_fingerprint} - no permission")
                return False
            
            # NE PAS STOCKER LE MESSAGE - juste notifier la réception
            print(f"💬 Message notification received from {message.from_fingerprint[:12]}...")
            print(f"   Type: {message.message_type.value}")
            print(f"   Message stored on sender's server - will fetch on demand")
            
            # Mettre à jour métadonnées conversation
            self._update_conversation_metadata(message.from_fingerprint, message.timestamp)
            
            # Cache temporaire pour performance immédiate (optionnel)
            cache_expiry_time = time.time() + 300  # Cache 5 minutes
            self.message_cache[message.message_id] = message
            self.cache_expiry[message.message_id] = cache_expiry_time
            
            # Traitement spécifique par type
            if message.message_type == MessageType.URN_SHARE:
                self._handle_urn_share_notification(message)
            elif message.message_type == MessageType.PHOTO_SHARE:
                self._handle_photo_share_notification(message)
            
            # Callback notification
            if self.on_message_received:
                self.on_message_received(message)
            
            self._save_distributed_data()
            return True
            
        except Exception as e:
            print(f"⚠️ Error processing message notification: {e}")
            return False
    
    def _handle_urn_share_notification(self, message: Message):
        """Traite notification de partage URN (récupération à la demande)"""
        print(f"🔱 URN share notification from {message.from_fingerprint[:12]}...")
        print(f"   URN will be fetched when conversation is opened")
        
        # Callback pour notification URN
        if self.on_urn_shared:
            self.on_urn_shared(None, None, message.from_fingerprint, message.message_id)
    
    def _handle_photo_share_notification(self, message: Message):
        """Traite notification de partage photo (récupération à la demande)"""
        print(f"📷 Photo share notification from {message.from_fingerprint[:12]}...")
        print(f"   Photo will be fetched when conversation is opened")

    def get_conversations_list(self) -> List[Dict]:
        """Retourne la liste des conversations avec métadonnées"""
        conversations_list = []
        
        for conv_id, conversation in self.conversations.items():
            # Calculer participants autres que moi
            other_participants = [p for p in conversation.participants if p != self.fingerprint]
            
            # Estimer les messages non lus (basé sur la dernière sync)
            unread_estimate = 0
            for participant_fp in other_participants:
                if participant_fp in self.sync_info:
                    sync_info = self.sync_info[participant_fp]
                    # Estimation simple - en production, nécessiterait une requête
                    time_since_sync = time.time() - sync_info.last_sync_timestamp
                    if time_since_sync > 300:  # Plus de 5 minutes
                        unread_estimate += 1
            
            conversations_list.append({
                "conversation_id": conv_id,
                "participants": conversation.participants,
                "participant_names": conversation.participant_names,
                "is_group": conversation.is_group,
                "last_message_time": conversation.last_message_time,
                "unread_estimate": unread_estimate,
                "other_participants": other_participants,
                "sync_status": {
                    participant_fp: {
                        "last_sync": self.sync_info[participant_fp].last_sync_timestamp,
                        "message_count": self.sync_info[participant_fp].message_count
                    } if participant_fp in self.sync_info else {
                        "last_sync": 0,
                        "message_count": 0
                    }
                    for participant_fp in other_participants
                }
            })
        
        # Trier par dernière activité
        conversations_list.sort(key=lambda c: c["last_message_time"], reverse=True)
        
        return conversations_list

    async def open_conversation(
        self, 
        participants: List[str], 
        auto_sync: bool = True
    ) -> Dict:
        """Ouvre une conversation et synchronise les messages"""
        
        # Nettoyer cache expiré
        self._cleanup_expired_cache()
        
        # Synchroniser automatiquement si demandé
        if auto_sync:
            for participant_fp in participants:
                if participant_fp != self.fingerprint:
                    await self.fetch_messages_from_participant(participant_fp)
        
        # Récupérer la conversation unifiée
        messages = await self.get_unified_conversation(participants)
        
        # Créer/mettre à jour conversation
        conversation_id = Conversation(participants=participants, participant_names={}, last_message_time=0).get_conversation_id()
        
        if conversation_id not in self.conversations:
            participant_names = {self.fingerprint: self.node_id}
            for participant_fp in participants:
                if participant_fp != self.fingerprint and participant_fp in self.friendship_protocol.friendships:
                    participant_names[participant_fp] = self.friendship_protocol.friendships[participant_fp].friend_node_id
                else:
                    participant_names[participant_fp] = "unknown"
            
            self.conversations[conversation_id] = Conversation(
                participants=participants,
                participant_names=participant_names,
                last_message_time=messages[-1].timestamp if messages else time.time(),
                is_group=len(participants) > 2
            )
        
        return {
            "conversation_id": conversation_id,
            "participants": participants,
            "messages": [
                {
                    "message_id": msg.message_id,
                    "from_fingerprint": msg.from_fingerprint,
                    "to_fingerprint": msg.to_fingerprint,
                    "message_type": msg.message_type.value,
                    "content": msg.content if not msg.encrypted else self._decrypt_message(msg.content, msg.from_fingerprint),
                    "metadata": msg.metadata,
                    "timestamp": msg.timestamp,
                    "status": msg.status.value,
                    "reply_to": msg.reply_to,
                    "is_own": msg.from_fingerprint == self.fingerprint
                }
                for msg in messages
            ],
            "is_group": len(participants) > 2,
            "total_messages": len(messages)
        }

    def _notify_message_sent(self, message: Message):
        """Notifie l'envoi d'un message via P2P (sans envoyer le contenu)"""
        # TODO: Implémenter notification P2P réelle
        print(f"📤 Notifying {message.to_fingerprint[:12]}... of new message")
        print(f"   Message stored locally - recipient can fetch on demand")
        
        # Callback
        if self.on_message_sent:
            self.on_message_sent(message)

class OfflineMessageManager:
    """Gestionnaire de messages hors ligne et cache intelligent"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.cache_path = f"./offline_cache_{node_id}"
        os.makedirs(self.cache_path, exist_ok=True)
        
        # Cache intelligent avec priorités
        self.priority_cache: Dict[str, Message] = {}  # Messages haute priorité (amis proches)
        self.standard_cache: Dict[str, Message] = {}  # Cache standard
        self.cache_metadata: Dict[str, Dict] = {}     # Métadonnées de cache
        
        self._load_offline_cache()
        
        print(f"💾 Offline Message Manager initialized")
        print(f"   Priority cache: {len(self.priority_cache)} messages")
        print(f"   Standard cache: {len(self.standard_cache)} messages")
    
    def _load_offline_cache(self):
        """Charge le cache hors ligne"""
        try:
            # Cache prioritaire
            priority_file = os.path.join(self.cache_path, "priority_cache.json")
            if os.path.exists(priority_file):
                with open(priority_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for msg_id, msg_data in data.items():
                        message = Message(**msg_data)
                        self.priority_cache[msg_id] = message
            
            # Cache standard
            standard_file = os.path.join(self.cache_path, "standard_cache.json")
            if os.path.exists(standard_file):
                with open(standard_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for msg_id, msg_data in data.items():
                        message = Message(**msg_data)
                        self.standard_cache[msg_id] = message
            
            # Métadonnées
            metadata_file = os.path.join(self.cache_path, "cache_metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.cache_metadata = json.load(f)
                    
        except Exception as e:
            print(f"⚠️ Error loading offline cache: {e}")
    
    def _save_offline_cache(self):
        """Sauvegarde le cache hors ligne"""
        try:
            # Cache prioritaire
            priority_file = os.path.join(self.cache_path, "priority_cache.json")
            priority_data = {
                msg_id: asdict(message) 
                for msg_id, message in self.priority_cache.items()
            }
            with open(priority_file, 'w', encoding='utf-8') as f:
                json.dump(priority_data, f, indent=2, ensure_ascii=False)
            
            # Cache standard
            standard_file = os.path.join(self.cache_path, "standard_cache.json")
            standard_data = {
                msg_id: asdict(message) 
                for msg_id, message in self.standard_cache.items()
            }
            with open(standard_file, 'w', encoding='utf-8') as f:
                json.dump(standard_data, f, indent=2, ensure_ascii=False)
            
            # Métadonnées
            metadata_file = os.path.join(self.cache_path, "cache_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error saving offline cache: {e}")
    
    def cache_message(
        self, 
        message: Message, 
        priority: str = "standard",
        ttl_hours: int = 24
    ):
        """Met en cache un message avec priorité et TTL"""
        
        metadata = {
            "cached_at": time.time(),
            "expires_at": time.time() + (ttl_hours * 3600),
            "priority": priority,
            "access_count": 0,
            "last_accessed": time.time()
        }
        
        if priority == "high":
            self.priority_cache[message.message_id] = message
        else:
            self.standard_cache[message.message_id] = message
        
        self.cache_metadata[message.message_id] = metadata
        self._save_offline_cache()
    
    def get_cached_message(self, message_id: str) -> Optional[Message]:
        """Récupère un message du cache"""
        
        # Vérifier cache prioritaire d'abord
        if message_id in self.priority_cache:
            message = self.priority_cache[message_id]
            self._update_access_stats(message_id)
            return message
        
        # Puis cache standard
        if message_id in self.standard_cache:
            message = self.standard_cache[message_id]
            self._update_access_stats(message_id)
            return message
        
        return None
    
    def _update_access_stats(self, message_id: str):
        """Met à jour les statistiques d'accès"""
        if message_id in self.cache_metadata:
            metadata = self.cache_metadata[message_id]
            metadata["access_count"] += 1
            metadata["last_accessed"] = time.time()
    
    def cleanup_expired_cache(self) -> int:
        """Nettoie le cache expiré"""
        current_time = time.time()
        expired_count = 0
        expired_ids = []
        
        for msg_id, metadata in self.cache_metadata.items():
            if current_time > metadata["expires_at"]:
                expired_ids.append(msg_id)
        
        for msg_id in expired_ids:
            if msg_id in self.priority_cache:
                del self.priority_cache[msg_id]
            if msg_id in self.standard_cache:
                del self.standard_cache[msg_id]
            if msg_id in self.cache_metadata:
                del self.cache_metadata[msg_id]
            expired_count += 1
        
        if expired_count > 0:
            self._save_offline_cache()
            print(f"🗑️ Cleaned {expired_count} expired cached messages")
        
        return expired_count
    
    def get_cache_stats(self) -> Dict:
        """Statistiques du cache"""
        total_messages = len(self.priority_cache) + len(self.standard_cache)
        
        if total_messages == 0:
            return {
                "total_messages": 0,
                "priority_messages": 0,
                "standard_messages": 0,
                "cache_hit_rate": 0,
                "average_age_hours": 0
            }
        
        # Calculer âge moyen
        current_time = time.time()
        total_age = sum(
            current_time - metadata["cached_at"]
            for metadata in self.cache_metadata.values()
        )
        average_age_hours = (total_age / total_messages) / 3600
        
        # Calculer taux d'accès
        total_accesses = sum(
            metadata["access_count"]
            for metadata in self.cache_metadata.values()
        )
        cache_hit_rate = total_accesses / max(1, total_messages)
        
        return {
            "total_messages": total_messages,
            "priority_messages": len(self.priority_cache),
            "standard_messages": len(self.standard_cache),
            "cache_hit_rate": cache_hit_rate,
            "average_age_hours": average_age_hours
        }

# Mise à jour de la classe principale pour intégrer le cache hors ligne
class DistributedMessaging(DistributedMessaging):
    """Version étendue avec cache hors ligne"""
    
    def __init__(self, node_id: str, fingerprint: str, private_key, public_key, friendship_protocol):
        super().__init__(node_id, fingerprint, private_key, public_key, friendship_protocol)
        
        # Gestionnaire de cache hors ligne
        self.offline_manager = OfflineMessageManager(node_id)
        
        print(f"💾 Offline messaging capabilities enabled")
    
    def _handle_urn_share(self, message: Message):
        """Traite un partage d'URN reçu"""
        try:
            share_data = json.loads(message.content)
            urn_id = share_data['urn_id']
            urn_metadata = share_data['metadata']
            
            print(f"🔱 URN shared: {urn_id}")
            print(f"   From: {share_data['shared_by']}")
            print(f"   Message: {share_data.get('message', '')}")
            
            # Callback pour traitement URN
            if self.on_urn_shared:
                self.on_urn_shared(urn_id, urn_metadata, message.from_fingerprint)
                
        except Exception as e:
            print(f"⚠️ Error handling URN share: {e}")
    
    def _handle_photo_share(self, message: Message):
        """Traite un partage de photo reçu"""
        try:
            share_data = json.loads(message.content)
            filename = share_data['filename']
            photo_b64 = share_data['photo_data']
            caption = share_data.get('caption', '')
            
            # Décoder la photo
            photo_data = base64.b64decode(photo_b64.encode())
            
            # Sauvegarder la photo reçue
            photos_dir = os.path.join(self.storage_path, "received_photos")
            os.makedirs(photos_dir, exist_ok=True)
            
            safe_filename = f"{int(time.time())}_{filename}"
            photo_path = os.path.join(photos_dir, safe_filename)
            
            with open(photo_path, 'wb') as f:
                f.write(photo_data)
            
            print(f"📷 Photo received: {filename}")
            print(f"   Saved as: {safe_filename}")
            print(f"   Caption: {caption}")
            print(f"   Size: {len(photo_data)} bytes")
            
        except Exception as e:
            print(f"⚠️ Error handling photo share: {e}")
    
    def _add_to_conversation(self, message: Message):
        """Ajoute un message à la conversation appropriée"""
        # Déterminer le participant (l'autre personne)
        if message.from_fingerprint == self.fingerprint:
            participant_fp = message.to_fingerprint
        else:
            participant_fp = message.from_fingerprint
        
        # Créer conversation si nécessaire
        if participant_fp not in self.conversations:
            # Récupérer infos ami
            friend_node_id = "unknown"
            if participant_fp in self.friendship_protocol.friendships:
                friend_node_id = self.friendship_protocol.friendships[participant_fp].friend_node_id
            
            self.conversations[participant_fp] = Conversation(
                participant_fingerprint=participant_fp,
                participant_node_id=friend_node_id,
                messages=[],
                last_message_time=0
            )
        
        # Ajouter le message
        self.conversations[participant_fp].add_message(message)
    
    def get_conversation(self, participant_fingerprint: str) -> Optional[Conversation]:
        """Récupère une conversation"""
        return self.conversations.get(participant_fingerprint)
    
    def get_all_conversations(self) -> List[Conversation]:
        """Récupère toutes les conversations triées par dernière activité"""
        conversations = list(self.conversations.values())
        conversations.sort(key=lambda c: c.last_message_time, reverse=True)
        return conversations
    
    def mark_conversation_as_read(self, participant_fingerprint: str):
        """Marque une conversation comme lue"""
        if participant_fingerprint in self.conversations:
            self.conversations[participant_fingerprint].mark_as_read()
            self._save_conversations()
    
    def get_unread_count(self) -> int:
        """Nombre total de messages non lus"""
        return sum(conv.unread_count for conv in self.conversations.values())
    
    def get_messaging_stats(self) -> Dict:
        """Statistiques de messagerie distribuée"""
        cache_stats = {}
        if hasattr(self, 'cache_manager'):
            cache_stats = {
                'priority_cache_size': len(self.cache_manager.priority_cache),
                'standard_cache_size': len(self.cache_manager.standard_cache),
                'total_cached_messages': len(self.cache_manager.priority_cache) + len(self.cache_manager.standard_cache)
            }
        
        return {
            'total_conversations': len(self.conversations),
            'sent_messages': len(self.sent_messages),
            'active_conversations': len([conv for conv in self.conversations.values() if conv.last_activity > time.time() - 86400]),  # Conversations actives dernières 24h
            'distributed_storage': True,
            'node_fingerprint': self.fingerprint,
            **cache_stats
        }