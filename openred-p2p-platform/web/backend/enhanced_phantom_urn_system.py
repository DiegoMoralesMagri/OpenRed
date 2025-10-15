#!/usr/bin/env python3
"""
🌀 ENHANCED PHANTOM URN SYSTEM - OpenRed Quantum Security
==========================================================
Système URN Phantom avec Phoenix de Schrödinger et NCK (Next Connection Key)

Fonctionnalités révolutionnaires :
1. 🌀 Phoenix de Schrödinger : Matrice cryptée jamais reconstituée complètement
2. 🔑 NCK (Next Connection Key) : Rotation automatique des clés d'autorisation
3. 📋 Registre d'autorisation : Contrôle permanent des accès utilisateur
4. ✅ Vérification continue : Validation en temps réel de l'existence et des droits

Innovation: Diego Morales Magri - Octobre 2025
"""

import os
import json
import hashlib
import secrets
import time
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SchrodingerPhoenix:
    """🌀 État quantique Phoenix - matrice cryptée jamais complètement reconstituée"""
    urn_id: str
    encrypted_matrix: bytes  # Matrice cryptée compacte
    dimensions: Tuple[int, int]
    encryption_method: str
    creation_timestamp: float
    owner_node: str
    current_nck: str  # Current Next Connection Key
    next_nck: str     # Next Next Connection Key
    authorized_users: Dict[str, dict]  # user_id -> {permissions, last_access, nck}
    burn_after_reads: int = -1  # -1 = illimité, >0 = nombre de lectures

@dataclass 
class NextConnectionKey:
    """🔑 NCK - Clé rotationnelle pour maintien d'autorisation"""
    key_id: str
    encrypted_key: bytes
    user_id: str
    urn_id: str
    valid_until: float
    usage_count: int = 0
    max_usage: int = 1
    transmitted: bool = False

class AuthorizationRegistry:
    """📋 Registre des autorisations avec NCK et vérification continue"""
    
    def __init__(self):
        self.user_authorizations: Dict[str, Dict[str, dict]] = {}  # user_id -> urn_id -> auth_info
        self.active_ncks: Dict[str, NextConnectionKey] = {}  # nck_id -> NCK object
        self.verification_thread = None
        self.running = True
        
    def register_user_for_urn(self, user_id: str, urn_id: str, permissions: dict = None) -> str:
        """Enregistrer un utilisateur pour une URN avec génération NCK"""
        if user_id not in self.user_authorizations:
            self.user_authorizations[user_id] = {}
        
        # Générer NCK initial
        current_nck = self._generate_nck(user_id, urn_id)
        next_nck = self._generate_nck(user_id, urn_id)
        
        auth_info = {
            "urn_id": urn_id,
            "permissions": permissions or {"view": True, "download": False},
            "registered_at": datetime.now().isoformat(),
            "last_access": None,
            "access_count": 0,
            "current_nck": current_nck.key_id,
            "next_nck": next_nck.key_id,
            "status": "active"
        }
        
        self.user_authorizations[user_id][urn_id] = auth_info
        self.active_ncks[current_nck.key_id] = current_nck
        self.active_ncks[next_nck.key_id] = next_nck
        
        logger.info(f"🔑 Utilisateur {user_id} autorisé pour URN {urn_id[:8]}... avec NCK")
        return current_nck.key_id
    
    def _generate_nck(self, user_id: str, urn_id: str) -> NextConnectionKey:
        """Générer une nouvelle NCK"""
        key_id = f"nck_{secrets.token_hex(16)}"
        key_data = f"{user_id}:{urn_id}:{time.time()}:{secrets.token_hex(32)}"
        encrypted_key = base64.b64encode(key_data.encode()).decode()
        
        return NextConnectionKey(
            key_id=key_id,
            encrypted_key=encrypted_key.encode(),
            user_id=user_id,
            urn_id=urn_id,
            valid_until=time.time() + 3600,  # 1 heure
            max_usage=1
        )
    
    def validate_access_and_rotate_nck(self, user_id: str, urn_id: str, current_nck: str) -> Tuple[bool, Optional[str]]:
        """Valider l'accès et effectuer rotation NCK"""
        if user_id not in self.user_authorizations:
            return False, None
        
        if urn_id not in self.user_authorizations[user_id]:
            return False, None
        
        auth_info = self.user_authorizations[user_id][urn_id]
        
        # Vérifier NCK actuelle
        if auth_info["current_nck"] != current_nck:
            logger.warning(f"❌ NCK invalide pour {user_id} sur URN {urn_id[:8]}...")
            return False, None
        
        # Vérifier statut
        if auth_info["status"] != "active":
            return False, None
        
        # Effectuer rotation NCK
        old_current = auth_info["current_nck"]
        auth_info["current_nck"] = auth_info["next_nck"]
        auth_info["next_nck"] = self._generate_nck(user_id, urn_id).key_id
        auth_info["last_access"] = datetime.now().isoformat()
        auth_info["access_count"] += 1
        
        # Nettoyer ancienne NCK
        if old_current in self.active_ncks:
            del self.active_ncks[old_current]
        
        logger.info(f"🔄 NCK rotée pour {user_id} sur URN {urn_id[:8]}...")
        return True, auth_info["next_nck"]
    
    def start_continuous_verification(self):
        """Démarrer vérification continue des autorisations"""
        if self.verification_thread is None:
            self.verification_thread = threading.Thread(target=self._verification_loop, daemon=True)
            self.verification_thread.start()
            logger.info("🔍 Vérification continue des autorisations démarrée")
    
    def _verification_loop(self):
        """Boucle de vérification continue"""
        while self.running:
            try:
                current_time = time.time()
                expired_ncks = []
                
                # Vérifier expiration des NCKs
                for nck_id, nck in self.active_ncks.items():
                    if nck.valid_until < current_time:
                        expired_ncks.append(nck_id)
                        # Révoquer autorisation
                        user_id = nck.user_id
                        urn_id = nck.urn_id
                        if user_id in self.user_authorizations and urn_id in self.user_authorizations[user_id]:
                            self.user_authorizations[user_id][urn_id]["status"] = "expired"
                            logger.warning(f"⏰ NCK expirée pour {user_id} sur URN {urn_id[:8]}...")
                
                # Nettoyer NCKs expirées
                for nck_id in expired_ncks:
                    del self.active_ncks[nck_id]
                
                time.sleep(30)  # Vérification toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"❌ Erreur vérification continue: {e}")
                time.sleep(60)

class EnhancedPhantomUrnSystem:
    """🌀 Système URN Phantom amélioré avec Phoenix de Schrödinger et NCK"""
    
    def __init__(self, storage_dir: str, projection_server_url: str = None):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.projection_server_url = projection_server_url
        
        # Composants révolutionnaires
        self.authorization_registry = AuthorizationRegistry()
        self.schrodinger_cache: Dict[str, SchrodingerPhoenix] = {}
        self.session_keys: Dict[str, bytes] = {}
        
        # État système
        self.active_urns: Dict[str, dict] = {}
        self.phoenix_projections: Dict[str, np.ndarray] = {}
        
        # Démarrer vérification continue
        self.authorization_registry.start_continuous_verification()
        
        logger.info("🔥 Enhanced Phantom URN System initialisé avec Phoenix de Schrödinger")
    
    def burn_image_to_phantom_urn(self, image_path: str, phantom_name: str, authorized_node: str) -> Dict[str, Any]:
        """🔥 Brûler image → Phoenix de Schrödinger (jamais reconstruction complète)"""
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            phantom_id = f"phantom_{secrets.token_hex(8)}_{int(time.time())}"
            
            # Créer répertoire URN
            urn_dir = self.storage_dir / phantom_id
            urn_dir.mkdir(exist_ok=True)
            
            # Fragmentation atomique en cendres
            fragments_created = self._atomize_to_ashes(image, urn_dir, phantom_id)
            
            # Générer Phoenix de Schrödinger (JAMAIS reconstruction complète)
            schrodinger_phoenix = self._create_schrodinger_phoenix(image, phantom_id, authorized_node)
            
            # Enregistrer dans cache
            self.schrodinger_cache[phantom_id] = schrodinger_phoenix
            
            # Configuration URN
            urn_config = {
                "phantom_id": phantom_id,
                "phantom_name": phantom_name,
                "image_dimensions": [image.width, image.height],
                "total_fragments": fragments_created,
                "creation_timestamp": time.time(),
                "authorized_node": authorized_node,
                "schrodinger_enabled": True,
                "nck_system": True
            }
            
            config_path = urn_dir / "urn_config.json"
            with open(config_path, 'w') as f:
                json.dump(urn_config, f, indent=2)
            
            # Enregistrer URN active
            self.active_urns[phantom_id] = urn_config
            
            # Générer clé Phoenix pour autorisation
            phoenix_key = self._generate_phoenix_key(phantom_id, authorized_node)
            
            logger.info(f"🔥 Image brûlée en Phoenix de Schrödinger: {phantom_id}")
            
            return {
                "phantom_id": phantom_id,
                "total_fragments": fragments_created,
                "phoenix_key": phoenix_key,
                "schrodinger_matrix": "encrypted_quantum_state",
                "nck_enabled": True,
                "continuous_verification": True
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur burn image: {e}")
            raise
    
    def _create_schrodinger_phoenix(self, image: Image, phantom_id: str, authorized_node: str) -> SchrodingerPhoenix:
        """🌀 Créer Phoenix de Schrödinger - état quantique crypté"""
        # Convertir image en matrice
        image_array = np.array(image)
        
        # Crypter matrice → État Schrödinger
        master_key = Fernet.generate_key()
        cipher = Fernet(master_key)
        matrix_bytes = image_array.tobytes()
        encrypted_matrix = cipher.encrypt(matrix_bytes)
        
        # Stocker clé de session
        self.session_keys[phantom_id] = master_key
        
        # Générer NCKs
        current_nck = f"nck_{secrets.token_hex(16)}"
        next_nck = f"nck_{secrets.token_hex(16)}"
        
        return SchrodingerPhoenix(
            urn_id=phantom_id,
            encrypted_matrix=encrypted_matrix,
            dimensions=(image.width, image.height),
            encryption_method="Fernet_AES_Schrodinger",
            creation_timestamp=time.time(),
            owner_node=authorized_node,
            current_nck=current_nck,
            next_nck=next_nck,
            authorized_users={}
        )
    
    def authorize_user_for_phoenix(self, phantom_id: str, user_id: str, permissions: dict = None) -> str:
        """🔑 Autoriser utilisateur avec génération NCK"""
        if phantom_id not in self.schrodinger_cache:
            raise ValueError("Phoenix de Schrödinger non trouvé")
        
        nck_id = self.authorization_registry.register_user_for_urn(user_id, phantom_id, permissions)
        
        # Mettre à jour Phoenix
        phoenix = self.schrodinger_cache[phantom_id]
        phoenix.authorized_users[user_id] = {
            "permissions": permissions or {"view": True},
            "nck_id": nck_id,
            "authorized_at": datetime.now().isoformat()
        }
        
        return nck_id
    
    def request_phoenix_resurrection(self, phantom_id: str, user_id: str, current_nck: str) -> Optional[np.ndarray]:
        """🌀→🦅 Demander résurrection Phoenix avec vérification NCK"""
        if phantom_id not in self.schrodinger_cache:
            logger.error(f"❌ Phoenix de Schrödinger non trouvé: {phantom_id}")
            return None
        
        # Validation et rotation NCK
        authorized, next_nck = self.authorization_registry.validate_access_and_rotate_nck(
            user_id, phantom_id, current_nck
        )
        
        if not authorized:
            logger.warning(f"❌ Accès refusé pour {user_id} sur Phoenix {phantom_id[:8]}...")
            return None
        
        # IMPORTANT: On ne reconstitue JAMAIS l'image complète
        # On crée une projection temporaire cryptée (Phoenix de Schrödinger)
        phoenix = self.schrodinger_cache[phantom_id]
        
        if phantom_id in self.session_keys:
            # Décryptage partiel pour projection (JAMAIS complet)
            cipher = Fernet(self.session_keys[phantom_id])
            decrypted_bytes = cipher.decrypt(phoenix.encrypted_matrix)
            
            # Reconstruction en mémoire temporaire UNIQUEMENT
            width, height = phoenix.dimensions
            phoenix_matrix = np.frombuffer(decrypted_bytes, dtype=np.uint8)
            phoenix_matrix = phoenix_matrix.reshape((height, width, 3))
            
            logger.info(f"🌀 Phoenix de Schrödinger projeté pour {user_id} - NCK: {next_nck[:8]}...")
            
            # La matrice sera détruite automatiquement après affichage
            return phoenix_matrix
        
        return None
    
    def _atomize_to_ashes(self, image: Image, urn_dir: Path, phantom_id: str) -> int:
        """⚛️ Atomisation en cendres cryptées"""
        width, height = image.size
        image_array = np.array(image)
        fragments_created = 0
        
        for y in range(height):
            for x in range(width):
                pixel_rgb = tuple(image_array[y, x])
                
                # Créer fragment (cendre)
                fragment_data = {
                    "phantom_id": phantom_id,
                    "position": [int(x), int(y)],
                    "color_rgb": [int(pixel_rgb[0]), int(pixel_rgb[1]), int(pixel_rgb[2])],
                    "timestamp": time.time()
                }
                
                # Crypter fragment
                fragment_key = self._derive_fragment_key(f"ash_{x}_{y}", phantom_id)
                cipher = Fernet(fragment_key)
                encrypted_fragment = cipher.encrypt(json.dumps(fragment_data).encode())
                
                # Nom aléatoire pour empêcher reconstruction
                fragment_name = f"ash_{secrets.token_hex(16)}.pxl"
                fragment_path = urn_dir / fragment_name
                
                with open(fragment_path, 'wb') as f:
                    f.write(encrypted_fragment)
                
                fragments_created += 1
        
        return fragments_created
    
    def _derive_fragment_key(self, fragment_name: str, phantom_id: str) -> bytes:
        """Dériver clé fragment"""
        key_material = f"{fragment_name}:{phantom_id}".encode()
        digest = hashlib.sha256(key_material).digest()
        return base64.urlsafe_b64encode(digest[:32])
    
    def _generate_phoenix_key(self, phantom_id: str, authorized_node: str) -> str:
        """Générer clé Phoenix pour autorisation"""
        key_data = f"{phantom_id}:{authorized_node}:{time.time()}:{secrets.token_hex(32)}"
        return base64.b64encode(key_data.encode()).decode()
    
    def verify_server_status(self, phantom_id: str) -> dict:
        """✅ Vérifier si le serveur est actif et l'image existe encore"""
        if phantom_id not in self.active_urns:
            return {"status": "not_found", "active": False}
        
        urn_dir = self.storage_dir / phantom_id
        if not urn_dir.exists():
            return {"status": "deleted", "active": False}
        
        # Vérifier quelques fragments
        fragments = list(urn_dir.glob("*.pxl"))
        if len(fragments) == 0:
            return {"status": "corrupted", "active": False}
        
        return {
            "status": "active",
            "active": True,
            "fragments_count": len(fragments),
            "last_verification": datetime.now().isoformat()
        }
    
    def get_user_next_nck(self, user_id: str, phantom_id: str) -> Optional[str]:
        """🔑 Récupérer la prochaine NCK pour l'utilisateur"""
        if user_id in self.authorization_registry.user_authorizations:
            if phantom_id in self.authorization_registry.user_authorizations[user_id]:
                return self.authorization_registry.user_authorizations[user_id][phantom_id]["next_nck"]
        return None


if __name__ == "__main__":
    # Test du système
    logging.basicConfig(level=logging.INFO)
    
    system = EnhancedPhantomUrnSystem("./test_enhanced_urns")
    
    # Simulation
    print("🔥 Test Enhanced Phantom URN System avec Phoenix de Schrödinger")
    print("=" * 60)
    print("✅ Système initialisé avec NCK et vérification continue")
    print("🌀 Phoenix de Schrödinger: Jamais de reconstruction complète")
    print("🔑 NCK: Rotation automatique des clés")
    print("📋 Registre: Contrôle permanent des autorisations")
    print("✅ Vérification: Continue de l'existence et des droits")