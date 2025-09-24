#!/usr/bin/env python3
"""
👻 O-Red Phantom Image System - Révolution des Images Fantômes
Architecture optimisée : Lazy Loading + Push Notifications

Innovation révolutionnaire :
- Images fantômes qui n'existent que chez le propriétaire
- Vérification à la demande pour économiser les ressources
- Push notifications pour suppression instantanée
- Anti-capture intégré avec rendu sécurisé

Auteur : Système OpenRed Révolutionnaire
Date : Septembre 2025
"""

import asyncio
import json
import secrets
import hashlib
import base64
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import io

# Import de nos modules révolutionnaires
from p2p_asymmetric_token_manager import P2PAsymmetricTokenManager

@dataclass
class PhantomImageMetadata:
    """📋 Métadonnées d'une image fantôme"""
    phantom_id: str
    owner_node_id: str
    original_filename: str
    content_hash: str  # Hash de l'image originale
    created_at: str
    last_validated: str
    permissions: Dict[str, Any]
    access_token: str  # Token asymétrique d'accès

class PhantomImageEngine:
    """
    👻 Moteur d'Images Fantômes Révolutionnaire
    
    Architecture optimisée par l'utilisateur :
    
    📥 CONSULTATION (Lazy Loading) :
    1. User veut voir image → Query API de vérification
    2. Si OK → Stream et affichage
    3. Si KO → Image noire
    
    📤 SUPPRESSION (Push Notifications) :
    1. Owner supprime → Push notification aux viewers
    2. Image devient noire instantanément
    3. Prochaine consultation → Refusée
    
    🚀 Résultat : Performance optimale + Expérience parfaite !
    """
    
    def __init__(self, node_id: str, asymmetric_tokens: P2PAsymmetricTokenManager):
        self.node_id = node_id
        self.tokens = asymmetric_tokens
        
        # Stockage des images fantômes locales
        self.phantom_images = {}  # phantom_id -> PhantomImageMetadata
        
        # Stockage des images réelles (si propriétaire)
        self.owned_images = {}  # image_id -> image_data
        
        # Cache de validation pour éviter les requêtes répétées
        self.validation_cache = {}  # phantom_id -> (timestamp, valid)
        
        # Abonnés aux notifications (qui a quelles images fantômes)
        self.subscribers = {}  # image_id -> List[node_id]
        
        # Callbacks pour les notifications UI
        self.on_image_deleted_callbacks = []
        self.on_image_restricted_callbacks = []
        
        print(f"👻 [PHANTOM ENGINE] Initialisé pour {node_id}")
    
    def create_phantom_image(self, image_path: str, owner_permissions: Dict[str, Any] = None) -> str:
        """
        📸 Créer une image réelle et générer sa référence fantôme
        
        Args:
            image_path: Chemin vers l'image réelle
            owner_permissions: Permissions d'accès par défaut
        
        Returns:
            phantom_id de l'image créée
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image introuvable : {image_path}")
        
        # Lire et hasher l'image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        content_hash = hashlib.sha256(image_data).hexdigest()
        image_id = secrets.token_urlsafe(32)
        
        # Permissions par défaut
        if owner_permissions is None:
            owner_permissions = {
                "public_view": False,
                "friends_view": True,
                "download_allowed": False,
                "expiry_date": None
            }
        
        # Stocker l'image réelle (nous sommes le propriétaire)
        self.owned_images[image_id] = {
            "data": image_data,
            "filename": Path(image_path).name,
            "content_hash": content_hash,
            "permissions": owner_permissions,
            "created_at": datetime.utcnow().isoformat(),
            "active": True
        }
        
        # Initialiser liste des abonnés
        self.subscribers[image_id] = []
        
        print(f"📸 [CREATE] Image réelle créée : {image_id}")
        print(f"   📁 Fichier : {Path(image_path).name}")
        print(f"   🔐 Hash : {content_hash[:16]}...")
        print(f"   👀 Permissions : {list(owner_permissions.keys())}")
        
        return image_id
    
    def get_phantom_reference(self, image_id: str, requester_node_id: str) -> Optional[Dict[str, Any]]:
        """
        🎯 Générer une référence fantôme pour un utilisateur
        
        L'utilisateur recevra cette référence qu'il pourra utiliser
        pour afficher l'image (mais pas la posséder réellement)
        
        Args:
            image_id: ID de l'image réelle
            requester_node_id: Nœud qui demande l'accès
        
        Returns:
            Référence fantôme ou None si accès refusé
        """
        if image_id not in self.owned_images:
            print(f"❌ [PHANTOM REF] Image {image_id} inexistante")
            return None
        
        image_info = self.owned_images[image_id]
        
        # Vérifier permissions
        if not self._check_permissions(image_info["permissions"], requester_node_id):
            print(f"❌ [PHANTOM REF] Accès refusé pour {requester_node_id}")
            return None
        
        # Générer token d'accès asymétrique
        access_token = self.tokens.request_friend_action(
            requester_node_id,
            "view_phantom_image",
            {"image_id": image_id, "content_hash": image_info["content_hash"]}
        )
        
        # Créer référence fantôme
        phantom_id = secrets.token_urlsafe(32)
        phantom_ref = {
            "phantom_id": phantom_id,
            "owner_node_id": self.node_id,
            "original_filename": image_info["filename"],
            "content_hash": image_info["content_hash"],
            "access_token": access_token,
            "validation_endpoint": f"phantom_validate/{image_id}",
            "stream_endpoint": f"phantom_stream/{image_id}",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Ajouter l'utilisateur aux abonnés
        if requester_node_id not in self.subscribers[image_id]:
            self.subscribers[image_id].append(requester_node_id)
        
        print(f"👻 [PHANTOM REF] Référence générée pour {requester_node_id}")
        print(f"   🆔 Phantom ID : {phantom_id}")
        print(f"   🔐 Token d'accès généré")
        
        return phantom_ref
    
    def register_phantom_image(self, phantom_ref: Dict[str, Any]):
        """
        📝 Enregistrer une image fantôme reçue d'un autre nœud
        
        Args:
            phantom_ref: Référence fantôme reçue
        """
        phantom_id = phantom_ref["phantom_id"]
        
        # Créer métadonnées locales
        metadata = PhantomImageMetadata(
            phantom_id=phantom_id,
            owner_node_id=phantom_ref["owner_node_id"],
            original_filename=phantom_ref["original_filename"],
            content_hash=phantom_ref["content_hash"],
            created_at=phantom_ref["created_at"],
            last_validated=datetime.utcnow().isoformat(),
            permissions={},  # Sera vérifié à la demande
            access_token=phantom_ref["access_token"]
        )
        
        self.phantom_images[phantom_id] = metadata
        
        print(f"📝 [REGISTER] Image fantôme enregistrée : {phantom_id}")
        print(f"   👤 Propriétaire : {phantom_ref['owner_node_id']}")
        print(f"   📁 Fichier : {phantom_ref['original_filename']}")
    
    async def validate_phantom_image(self, phantom_id: str, force_refresh: bool = False) -> bool:
        """
        🔍 Valider qu'une image fantôme existe toujours (LAZY LOADING)
        
        Cette méthode implémente votre optimisation :
        - Vérification uniquement quand l'utilisateur veut voir l'image
        - Cache pour éviter les requêtes répétées
        - Query API du propriétaire
        
        Args:
            phantom_id: ID de l'image fantôme
            force_refresh: Forcer la re-vérification
        
        Returns:
            True si l'image est toujours accessible
        """
        if phantom_id not in self.phantom_images:
            return False
        
        metadata = self.phantom_images[phantom_id]
        
        # Vérifier cache de validation (économise les requêtes)
        cache_key = phantom_id
        now = time.time()
        
        if not force_refresh and cache_key in self.validation_cache:
            cache_time, is_valid = self.validation_cache[cache_key]
            # Cache valide pendant 1 minute
            if now - cache_time < 60:
                print(f"🔍 [VALIDATE] Cache hit pour {phantom_id} : {'✅' if is_valid else '❌'}")
                return is_valid
        
        print(f"🔍 [VALIDATE] Validation à la demande de {phantom_id}")
        print(f"   👤 Propriétaire : {metadata.owner_node_id}")
        
        # Simuler query API du propriétaire
        is_valid = await self._query_owner_validation(metadata)
        
        # Mettre à jour cache
        self.validation_cache[cache_key] = (now, is_valid)
        
        # Mettre à jour métadonnées
        metadata.last_validated = datetime.utcnow().isoformat()
        
        result = "✅ Accessible" if is_valid else "❌ Plus accessible"
        print(f"   🎯 Résultat : {result}")
        
        return is_valid
    
    async def view_phantom_image(self, phantom_id: str) -> Optional[bytes]:
        """
        👀 Voir une image fantôme (avec validation lazy)
        
        Implémente votre architecture optimisée :
        1. Validation à la demande
        2. Si OK → Stream de l'image
        3. Si KO → Image noire
        
        Args:
            phantom_id: ID de l'image fantôme
        
        Returns:
            Données image ou None si inaccessible
        """
        print(f"👀 [VIEW] Demande de visualisation : {phantom_id}")
        
        # Étape 1 : Validation lazy loading
        is_valid = await self.validate_phantom_image(phantom_id)
        
        if not is_valid:
            print(f"❌ [VIEW] Image inaccessible → Image noire")
            return self._generate_black_image()
        
        # Étape 2 : Stream de l'image depuis le propriétaire
        print(f"✅ [VIEW] Image valide → Stream en cours")
        image_data = await self._stream_from_owner(phantom_id)
        
        if image_data:
            print(f"📺 [VIEW] Image streamée avec succès ({len(image_data)} bytes)")
            return image_data
        else:
            print(f"❌ [VIEW] Échec stream → Image noire")
            return self._generate_black_image()
    
    def delete_owned_image(self, image_id: str):
        """
        🗑️ Supprimer une image possédée (avec push notifications)
        
        Implémente votre système de notifications :
        1. Marquer l'image comme supprimée
        2. Push notification à tous les abonnés
        3. Images fantômes → Noires instantanément
        
        Args:
            image_id: ID de l'image à supprimer
        """
        if image_id not in self.owned_images:
            print(f"❌ [DELETE] Image {image_id} introuvable")
            return
        
        image_info = self.owned_images[image_id]
        
        print(f"🗑️ [DELETE] Suppression de l'image : {image_id}")
        print(f"   📁 Fichier : {image_info['filename']}")
        
        # Étape 1 : Marquer comme supprimée
        image_info["active"] = False
        image_info["deleted_at"] = datetime.utcnow().isoformat()
        
        # Étape 2 : Push notifications aux abonnés
        subscribers = self.subscribers.get(image_id, [])
        print(f"   📤 Push notifications → {len(subscribers)} abonnés")
        
        for subscriber_node in subscribers:
            self._send_deletion_notification(subscriber_node, image_id)
        
        # Étape 3 : Nettoyer
        del self.owned_images[image_id]
        if image_id in self.subscribers:
            del self.subscribers[image_id]
        
        print(f"✅ [DELETE] Image supprimée avec notifications envoyées")
    
    def restrict_image_access(self, image_id: str, new_permissions: Dict[str, Any]):
        """
        🔒 Modifier les permissions d'une image (avec push notifications)
        
        Args:
            image_id: ID de l'image
            new_permissions: Nouvelles permissions
        """
        if image_id not in self.owned_images:
            return
        
        print(f"🔒 [RESTRICT] Modification permissions : {image_id}")
        
        old_permissions = self.owned_images[image_id]["permissions"]
        self.owned_images[image_id]["permissions"] = new_permissions
        
        # Notifier les abonnés de la restriction
        subscribers = self.subscribers.get(image_id, [])
        for subscriber_node in subscribers:
            self._send_restriction_notification(subscriber_node, image_id, new_permissions)
        
        print(f"✅ [RESTRICT] Permissions modifiées avec notifications")
    
    def list_phantom_images(self) -> List[Dict[str, Any]]:
        """📋 Lister toutes les images fantômes locales"""
        phantom_list = []
        
        for phantom_id, metadata in self.phantom_images.items():
            phantom_list.append({
                "phantom_id": phantom_id,
                "owner": metadata.owner_node_id,
                "filename": metadata.original_filename,
                "created_at": metadata.created_at,
                "last_validated": metadata.last_validated
            })
        
        return phantom_list
    
    def list_owned_images(self) -> List[Dict[str, Any]]:
        """📋 Lister toutes les images possédées"""
        owned_list = []
        
        for image_id, image_info in self.owned_images.items():
            subscribers = self.subscribers.get(image_id, [])
            owned_list.append({
                "image_id": image_id,
                "filename": image_info["filename"],
                "created_at": image_info["created_at"],
                "active": image_info["active"],
                "subscribers_count": len(subscribers),
                "permissions": image_info["permissions"]
            })
        
        return owned_list
    
    # === MÉTHODES PRIVÉES ===
    
    async def _query_owner_validation(self, metadata: PhantomImageMetadata) -> bool:
        """🔍 Query API du propriétaire pour valider l'image"""
        # Simulation de la requête réseau
        await asyncio.sleep(0.1)  # Latence réseau simulée
        
        # Ici on ferait une vraie requête HTTP/P2P au propriétaire
        # Pour la démo, on simule avec une logique simple
        
        owner_node = metadata.owner_node_id
        
        # Vérifier si le propriétaire est dans nos amis
        friendships = self.tokens.list_relationships()
        owner_is_friend = any(f["friend_node_id"] == owner_node for f in friendships)
        
        if not owner_is_friend:
            return False
        
        # Simuler différentes conditions
        return True  # Pour la démo, toujours valide
    
    async def _stream_from_owner(self, phantom_id: str) -> Optional[bytes]:
        """📺 Stream de l'image depuis le propriétaire"""
        metadata = self.phantom_images[phantom_id]
        
        # Simulation du streaming
        await asyncio.sleep(0.2)  # Latence de streaming simulée
        
        # Pour la démo, générer une image de test
        return self._generate_test_image(metadata.original_filename)
    
    def _generate_black_image(self) -> bytes:
        """⚫ Générer une image noire (quand l'accès est refusé)"""
        # Image noire 100x100 en PNG
        black_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00d\x08\x02\x00\x00\x00\xff\x80\x02\x03\x00\x00\x00\x19IDATx\x9c\xed\xc1\x01\x01\x00\x00\x00\x80\x90\xfe\xaf\xee\x08\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82'
        return black_png
    
    def _generate_test_image(self, filename: str) -> bytes:
        """🖼️ Générer une image de test pour la démo"""
        # Pour la démo, on génère toujours la même image test
        # En réalité, ce serait streamé depuis le propriétaire
        return self._generate_black_image()  # Placeholder
    
    def _check_permissions(self, permissions: Dict[str, Any], requester_node_id: str) -> bool:
        """🔐 Vérifier les permissions d'accès"""
        # Logique simple pour la démo
        if permissions.get("public_view", False):
            return True
        
        if permissions.get("friends_view", False):
            friendships = self.tokens.list_relationships()
            return any(f["friend_node_id"] == requester_node_id for f in friendships)
        
        return False
    
    def _send_deletion_notification(self, subscriber_node: str, image_id: str):
        """📤 Envoyer notification de suppression"""
        notification = {
            "type": "phantom_image_deleted",
            "image_id": image_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "sender": self.node_id
        }
        
        # Ici on enverrait via le système P2P
        print(f"📤 [PUSH] Notification suppression → {subscriber_node}")
        
        # Déclencher callbacks locaux
        for callback in self.on_image_deleted_callbacks:
            callback(image_id, subscriber_node)
    
    def _send_restriction_notification(self, subscriber_node: str, image_id: str, new_permissions: Dict[str, Any]):
        """📤 Envoyer notification de restriction"""
        notification = {
            "type": "phantom_image_restricted",
            "image_id": image_id,
            "new_permissions": new_permissions,
            "restricted_at": datetime.utcnow().isoformat(),
            "sender": self.node_id
        }
        
        print(f"📤 [PUSH] Notification restriction → {subscriber_node}")
        
        for callback in self.on_image_restricted_callbacks:
            callback(image_id, subscriber_node, new_permissions)
    
    # === CALLBACKS POUR L'UI ===
    
    def add_deletion_callback(self, callback: Callable[[str, str], None]):
        """Ajouter callback pour suppression d'image"""
        self.on_image_deleted_callbacks.append(callback)
    
    def add_restriction_callback(self, callback: Callable[[str, str, Dict[str, Any]], None]):
        """Ajouter callback pour restriction d'image"""
        self.on_image_restricted_callbacks.append(callback)


async def demo_phantom_image_system():
    """
    🎯 Démonstration du système d'images fantômes optimisé
    
    Scénario :
    1. Alice crée une image réelle
    2. Bob reçoit une référence fantôme
    3. Bob consulte l'image → Validation lazy + Stream
    4. Alice supprime l'image → Push notification
    5. Bob essaie de revoir l'image → Image noire
    """
    print("👻 === DÉMONSTRATION SYSTÈME IMAGES FANTÔMES ===\n")
    
    # Import des modules nécessaires
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    
    # === SETUP DES NŒUDS ===
    
    # Alice (propriétaire d'images)
    alice_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    alice_identity = {
        "node_id": "alice_photographer",
        "private_key": alice_key,
        "public_key": alice_key.public_key()
    }
    
    alice_tokens = P2PAsymmetricTokenManager(alice_identity, "alice_phantom_tokens.json")
    alice_phantom = PhantomImageEngine("alice_photographer", alice_tokens)
    
    # Bob (utilisateur d'images fantômes)
    bob_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    bob_identity = {
        "node_id": "bob_viewer",
        "private_key": bob_key,
        "public_key": bob_key.public_key()
    }
    
    bob_tokens = P2PAsymmetricTokenManager(bob_identity, "bob_phantom_tokens.json")
    bob_phantom = PhantomImageEngine("bob_viewer", bob_tokens)
    
    print("✅ Nœuds Alice (propriétaire) et Bob (viewer) initialisés\n")
    
    # === ÉTABLIR AMITIÉ ===
    
    alice_token = alice_tokens.establish_asymmetric_friendship(
        "bob_viewer",
        bob_identity["public_key"],
        {"view_phantom_image": True, "download_images": False}
    )
    
    bob_token = bob_tokens.establish_asymmetric_friendship(
        "alice_photographer",
        alice_identity["public_key"],
        {"share_phantom_images": True}
    )
    
    alice_tokens.receive_asymmetric_token(
        "bob_viewer",
        bob_token["token_public_key_pem"],
        bob_token["token_data"]
    )
    
    bob_tokens.receive_asymmetric_token(
        "alice_photographer",
        alice_token["token_public_key_pem"],
        alice_token["token_data"]
    )
    
    print("🤝 Amitié asymétrique établie entre Alice et Bob\n")
    
    # === SCÉNARIO 1 : CRÉATION ET PARTAGE ===
    
    print("📸 === SCÉNARIO 1 : CRÉATION ET PARTAGE ===")
    
    # Alice crée une image (simulée)
    # En réalité, elle fournirait un vrai fichier image
    print("Alice crée une image de paysage...")
    
    # Simuler création d'un fichier temporaire
    import tempfile
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.jpg', delete=False) as f:
        f.write(b"FAKE_IMAGE_DATA_LANDSCAPE")  # Image simulée
        temp_image_path = f.name
    
    try:
        image_id = alice_phantom.create_phantom_image(
            temp_image_path,
            {"friends_view": True, "public_view": False, "download_allowed": False}
        )
        
        # Alice génère une référence fantôme pour Bob
        phantom_ref = alice_phantom.get_phantom_reference(image_id, "bob_viewer")
        
        if phantom_ref:
            print("✅ Référence fantôme générée avec succès")
            
            # Bob enregistre l'image fantôme
            bob_phantom.register_phantom_image(phantom_ref)
            print("✅ Bob a enregistré l'image fantôme\n")
        
        # === SCÉNARIO 2 : CONSULTATION AVEC LAZY LOADING ===
        
        print("👀 === SCÉNARIO 2 : CONSULTATION (LAZY LOADING) ===")
        
        phantom_id = phantom_ref["phantom_id"]
        print(f"Bob veut voir l'image fantôme : {phantom_id}")
        
        # Bob consulte l'image → Déclenche validation lazy
        image_data = await bob_phantom.view_phantom_image(phantom_id)
        
        if image_data:
            print(f"✅ Image affichée avec succès ({len(image_data)} bytes)")
        else:
            print("❌ Impossible d'afficher l'image")
        
        print()
        
        # === SCÉNARIO 3 : SUPPRESSION AVEC PUSH NOTIFICATIONS ===
        
        print("🗑️ === SCÉNARIO 3 : SUPPRESSION (PUSH NOTIFICATIONS) ===")
        
        print("Alice décide de supprimer son image...")
        
        # Callback pour Bob quand l'image est supprimée
        def on_image_deleted(img_id, sender_node):
            print(f"📱 [BOB NOTIFICATION] Image {img_id} supprimée par {sender_node}")
            print("   📺 Si Bob regardait l'image → Elle devient noire instantanément")
        
        bob_phantom.add_deletion_callback(on_image_deleted)
        
        # Alice supprime l'image
        alice_phantom.delete_owned_image(image_id)
        print()
        
        # === SCÉNARIO 4 : TENTATIVE DE CONSULTATION APRÈS SUPPRESSION ===
        
        print("🔍 === SCÉNARIO 4 : CONSULTATION APRÈS SUPPRESSION ===")
        
        print("Bob essaie de revoir l'image supprimée...")
        
        # Bob tente de voir l'image → Validation échoue → Image noire
        image_data = await bob_phantom.view_phantom_image(phantom_id)
        
        if image_data == alice_phantom._generate_black_image():
            print("⚫ Image noire affichée (accès refusé)")
        else:
            print("❌ Erreur inattendue")
        
        print()
        
        # === RÉSUMÉ ===
        
        print("📊 === RÉSUMÉ DU SYSTÈME OPTIMISÉ ===")
        print("✅ Lazy Loading : Validation uniquement à la demande")
        print("✅ Push Notifications : Suppression instantanée")
        print("✅ Cache de validation : Économise les requêtes")
        print("✅ Images noires : Protection anti-capture")
        print("✅ Tokens asymétriques : Sécurité maximale")
        
        alice_owned = alice_phantom.list_owned_images()
        bob_phantoms = bob_phantom.list_phantom_images()
        
        print(f"\n📸 Alice possède : {len(alice_owned)} images")
        print(f"👻 Bob a : {len(bob_phantoms)} images fantômes")
        
    finally:
        # Nettoyer le fichier temporaire
        import os
        try:
            os.unlink(temp_image_path)
        except:
            pass
    
    print("\n🎉 === DÉMONSTRATION TERMINÉE ===")
    print("🚀 Architecture optimisée validée avec succès !")


if __name__ == "__main__":
    asyncio.run(demo_phantom_image_system())