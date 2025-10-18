# === OpenRed P2P Platform - Profil Utilisateur Permanent ===
# Système de profil persistant pour réseau social P2P

import os
import json
import uuid
import time
import io
import base64
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class PrivacyLevel(Enum):
    PUBLIC = "public"
    FRIENDS = "friends"
    FAMILY = "family"
    PROFESSIONAL = "professional"
    PRIVATE = "private"
    CUSTOM_GROUP = "custom_group"
    SPECIFIC_USER = "specific_user"

@dataclass
class UserProfile:
    """Profil utilisateur permanent pour le réseau social P2P"""
    user_id: str  # UUID permanent
    display_name: str
    real_name: str
    bio: str
    sector: str
    profile_picture: Optional[str]  # Photo complète en base64
    profile_thumbnail: Optional[str]  # Miniature légère pour beacons UDP
    background_image: Optional[str]
    location: str
    profession: str
    interests: List[str]
    privacy_settings: Dict[str, str]
    created_at: float
    last_updated: float
    
    @classmethod
    def create_new(cls, display_name: str, real_name: str = "", bio: str = "", sector: str = "general"):
        """Crée un nouveau profil utilisateur"""
        return cls(
            user_id=str(uuid.uuid4()),
            display_name=display_name,
            real_name=real_name,
            bio=bio,
            sector=sector,
            profile_picture=None,
            profile_thumbnail=None,
            background_image=None,
            location="",
            profession="",
            interests=[],
            privacy_settings={
                "profile_visibility": PrivacyLevel.PUBLIC.value,
                "contact_info": PrivacyLevel.FRIENDS.value,
                "posts_default": PrivacyLevel.FRIENDS.value,
                "photos_default": PrivacyLevel.FRIENDS.value
            },
            created_at=time.time(),
            last_updated=time.time()
        )

@dataclass
class FriendGroup:
    """Groupe d'amis personnalisé"""
    group_id: str
    name: str
    description: str
    color: str
    members: List[str]  # Liste des fingerprints
    created_at: float
    
    @classmethod
    def create_default_groups(cls):
        """Crée les groupes par défaut"""
        return [
            cls(
                group_id="friends",
                name="Amis",
                description="Amis proches",
                color="#4CAF50",
                members=[],
                created_at=time.time()
            ),
            cls(
                group_id="family",
                name="Famille",
                description="Membres de la famille",
                color="#FF5722",
                members=[],
                created_at=time.time()
            ),
            cls(
                group_id="professional",
                name="Professionnel",
                description="Contacts professionnels",
                color="#2196F3",
                members=[],
                created_at=time.time()
            )
        ]

class UserProfileManager:
    """Gestionnaire de profil utilisateur persistant"""
    
    def __init__(self, data_dir: str = "./user_data"):
        self.data_dir = data_dir
        self.profile_file = os.path.join(data_dir, "user_profile.json")
        self.groups_file = os.path.join(data_dir, "friend_groups.json")
        
        # Créer le dossier si nécessaire
        os.makedirs(data_dir, exist_ok=True)
        
        self.profile: Optional[UserProfile] = None
        self.friend_groups: List[FriendGroup] = []
    
    def create_thumbnail(self, image_base64: str, size: int = 32, quality: int = 15) -> Optional[str]:
        """Crée une miniature ultra-légère à partir d'une image base64"""
        if not PIL_AVAILABLE:
            print("⚠️ PIL/Pillow non disponible - impossible de créer des miniatures")
            return None
            
        try:
            # Décoder l'image base64
            image_data = base64.b64decode(image_base64.split(',')[-1])  # Enlever le préfixe data:image/...
            
            # Ouvrir avec PIL
            img = Image.open(io.BytesIO(image_data))
            
            # Convertir en RGB si nécessaire (pour JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionner en miniature
            img_thumbnail = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Sauvegarder en JPEG avec compression aggressive
            buffer = io.BytesIO()
            img_thumbnail.save(buffer, format='JPEG', quality=quality, optimize=True)
            jpeg_data = buffer.getvalue()
            
            # Encoder en base64
            thumbnail_b64 = base64.b64encode(jpeg_data).decode('utf-8')
            
            print(f"📷 Miniature créée: {len(jpeg_data)} bytes JPEG -> {len(thumbnail_b64)} bytes base64")
            return f"data:image/jpeg;base64,{thumbnail_b64}"
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la miniature: {e}")
            return None
        
    def load_or_create_profile(self, display_name: str = None) -> UserProfile:
        """Charge le profil existant ou en crée un nouveau"""
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Migration: ajouter profile_thumbnail si manquant
                    if 'profile_thumbnail' not in data:
                        data['profile_thumbnail'] = None
                        
                    self.profile = UserProfile(**data)
                    
                    # Si on a une photo mais pas de miniature, la générer
                    if (self.profile.profile_picture and not self.profile.profile_thumbnail):
                        print("🔄 Migration: génération de la miniature pour photo existante...")
                        thumbnail = self.create_thumbnail(self.profile.profile_picture)
                        if thumbnail:
                            self.profile.profile_thumbnail = thumbnail
                            self.save_profile()
                            print("✅ Miniature générée pour profil existant")
                    
                    print(f"👤 Profil chargé: {self.profile.display_name} (ID: {self.profile.user_id[:8]}...)")
                    return self.profile
            except Exception as e:
                print(f"⚠️ Erreur lors du chargement du profil: {e}")
        
        # Créer nouveau profil
        if not display_name:
            display_name = f"Utilisateur_{int(time.time())}"
            
        self.profile = UserProfile.create_new(display_name)
        self.save_profile()
        print(f"✨ Nouveau profil créé: {self.profile.display_name} (ID: {self.profile.user_id[:8]}...)")
        return self.profile
    
    def save_profile(self):
        """Sauvegarde le profil"""
        if self.profile:
            self.profile.last_updated = time.time()
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.profile), f, indent=2, ensure_ascii=False)
    
    def load_or_create_groups(self) -> List[FriendGroup]:
        """Charge les groupes d'amis ou crée les groupes par défaut"""
        if os.path.exists(self.groups_file):
            try:
                with open(self.groups_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.friend_groups = [FriendGroup(**group) for group in data]
                    print(f"👥 {len(self.friend_groups)} groupes d'amis chargés")
                    return self.friend_groups
            except Exception as e:
                print(f"⚠️ Erreur lors du chargement des groupes: {e}")
        
        # Créer groupes par défaut
        self.friend_groups = FriendGroup.create_default_groups()
        self.save_groups()
        print(f"✨ Groupes par défaut créés: {[g.name for g in self.friend_groups]}")
        return self.friend_groups
    
    def save_groups(self):
        """Sauvegarde les groupes d'amis"""
        with open(self.groups_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(group) for group in self.friend_groups], f, indent=2, ensure_ascii=False)
    
    def update_profile(self, **kwargs):
        """Met à jour le profil"""
        if self.profile:
            for key, value in kwargs.items():
                if hasattr(self.profile, key):
                    setattr(self.profile, key, value)
            self.save_profile()
    
    def add_friend_to_group(self, friend_fingerprint: str, group_id: str):
        """Ajoute un ami à un groupe"""
        for group in self.friend_groups:
            if group.group_id == group_id:
                if friend_fingerprint not in group.members:
                    group.members.append(friend_fingerprint)
                    self.save_groups()
                    return True
        return False
    
    def remove_friend_from_group(self, friend_fingerprint: str, group_id: str):
        """Retire un ami d'un groupe"""
        for group in self.friend_groups:
            if group.group_id == group_id:
                if friend_fingerprint in group.members:
                    group.members.remove(friend_fingerprint)
                    self.save_groups()
                    return True
        return False
    
    def create_custom_group(self, name: str, description: str = "", color: str = "#9C27B0"):
        """Crée un groupe personnalisé"""
        group = FriendGroup(
            group_id=str(uuid.uuid4()),
            name=name,
            description=description,
            color=color,
            members=[],
            created_at=time.time()
        )
        self.friend_groups.append(group)
        self.save_groups()
        return group
    
    def get_permanent_node_id(self) -> str:
        """Retourne l'ID de nœud permanent basé sur le profil"""
        if not self.profile:
            self.load_or_create_profile()
        return f"user_{self.profile.user_id}"
    
    def get_discovery_info(self) -> Dict:
        """Retourne les informations pour la découverte P2P (format léger pour UDP)"""
        if not self.profile:
            return {}
        
        discovery_info = {
            "display_name": self.profile.display_name,
            "real_name": self.profile.real_name if self.profile.privacy_settings.get("profile_visibility") == PrivacyLevel.PUBLIC.value else "",
            "bio": self.profile.bio[:50] if self.profile.bio else "",  # Très limitée pour UDP
            "sector": self.profile.sector,
            "profession": self.profile.profession[:30] if self.profile.profession else "",  # Limitée
            "location": self.profile.location[:30] if self.profile.location else "",  # Limitée
            "interests": self.profile.interests[:2] if self.profile.interests else []  # Top 2 seulement
        }
        
        # Ajouter la miniature si disponible et publique (pas la photo complète)
        if (self.profile.profile_thumbnail and 
            self.profile.privacy_settings.get("profile_visibility") in [PrivacyLevel.PUBLIC.value, PrivacyLevel.FRIENDS.value]):
            # Utiliser la miniature ultra-légère pour les beacons UDP
            discovery_info["profile_thumbnail"] = self.profile.profile_thumbnail
        
        return discovery_info
    
    def set_profile_picture(self, image_data: str):
        """Définit la photo de profil (base64) et génère automatiquement la miniature"""
        if self.profile:
            # Stocker la photo complète
            self.profile.profile_picture = image_data
            
            # Générer la miniature ultra-légère
            thumbnail = self.create_thumbnail(image_data)
            if thumbnail:
                self.profile.profile_thumbnail = thumbnail
                print(f"📷 Photo de profil mise à jour avec miniature pour beacons UDP")
            else:
                self.profile.profile_thumbnail = None
                print(f"⚠️ Photo de profil mise à jour mais miniature non créée")
            
            self.save_profile()
            return True
        return False
    
    def get_public_profile_picture(self) -> Optional[str]:
        """Retourne la photo de profil si elle est publique"""
        if (self.profile and self.profile.profile_picture and 
            self.profile.privacy_settings.get("profile_visibility") in [PrivacyLevel.PUBLIC.value, PrivacyLevel.FRIENDS.value]):
            return self.profile.profile_picture
        return None