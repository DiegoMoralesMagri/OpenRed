#!/usr/bin/env python3
"""
🔥 SYSTÈME PHANTOM URN AUTHENTIQUE POUR WEB API
==============================================
Implémentation du vrai système Phantom URN avec fragmentation atomique
Basé sur phantom_urn_system.py du dossier phantom-images-demo

Architecture Phantom URN:
1. BURN: Image → Cendres atomiques cryptées chaînées
2. URN: Métadonnées d'accès + clé d'activation
3. ORP: Projection streaming pour visualisation
4. PHOENIX: Reconstruction temps réel depuis les cendres

INNOVATION: Chaque pixel = 1 fragment crypté avec clé suivante
SÉCURITÉ: Aucune image physique stockée, seulement fragments cryptés
"""

import os
import json
import hashlib
import secrets
import time
import uuid
import base64
import threading
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from PIL import Image
import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)

@dataclass
class AshFragment:
    """Fragment de cendre - un pixel crypté avec chaînage"""
    color_rgb: Tuple[int, int, int]
    position: Tuple[int, int]  # (x, y)
    next_fragment_name: str
    next_decrypt_key: bytes
    creation_timestamp: float

@dataclass
class UrnConfig:
    """Configuration d'une urne Phantom"""
    image_hash: str
    total_fragments: int
    image_dimensions: Tuple[int, int]
    creation_time: float
    authorized_node: str
    burn_after_reads: int = 1
    phantom_id: str = ""

@dataclass
class OrpMetadata:
    """Métadonnées pour fichier .orp"""
    phantom_id: str
    phantom_name: str
    server_url: str
    dimensions: Tuple[int, int]
    access_token: Optional[str] = None
    created_at: str = ""

class AuthenticPhantomUrnSystem:
    """
    Système URN Phantom authentique pour l'API Web
    """
    
    def __init__(self, storage_dir: str = "phantom_urns", projection_server_url: str = "http://localhost:8002"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.projection_server_url = projection_server_url
        
        # Registre des URNs actives
        self.active_urns: Dict[str, UrnConfig] = {}
        self.urn_fragments: Dict[str, Dict[str, str]] = {}  # urn_id -> {fragment_name -> filepath}
        
        # Cache pour projection
        self.phantom_cache: Dict[str, np.ndarray] = {}
        
        # Clés d'activation
        self.activation_keys: Dict[str, Tuple[Any, Any]] = {}  # urn_id -> (private_key, public_key)
        
        logger.info(f"🔥 Phantom URN System initialisé - Storage: {self.storage_dir}")
    
    def burn_image_to_phantom_urn(self, image_path: str, phantom_name: str, authorized_node: str) -> Dict[str, Any]:
        """
        🔥 BRÛLE une image en URN Phantom avec fragmentation atomique
        """
        try:
            logger.info(f"🔥 Début combustion: {phantom_name}")
            
            # Charger et préparer l'image
            original_image = Image.open(image_path)
            if original_image.mode != 'RGB':
                original_image = original_image.convert('RGB')
            
            img_array = np.array(original_image)
            height, width, _ = img_array.shape
            
            # Générer ID unique pour cette URN
            image_hash = hashlib.sha256(open(image_path, 'rb').read()).hexdigest()
            phantom_id = f"phantom_{secrets.token_hex(8)}_{int(time.time())}"
            
            # Configuration URN
            config = UrnConfig(
                image_hash=image_hash,
                total_fragments=width * height,
                image_dimensions=(width, height),
                creation_time=time.time(),
                authorized_node=authorized_node,
                phantom_id=phantom_id
            )
            
            # Créer dossier URN
            urn_dir = self.storage_dir / phantom_id
            urn_dir.mkdir(exist_ok=True)
            
            # Générer clés d'activation RSA
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            self.activation_keys[phantom_id] = (private_key, public_key)
            
            # Fragmentation atomique
            fragment_chain = self._atomic_fragmentation(img_array, urn_dir, phantom_id)
            
            # Registre URN
            self.active_urns[phantom_id] = config
            self.urn_fragments[phantom_id] = fragment_chain
            
            # Sauvegarder configuration
            config_path = urn_dir / "urn_config.json"
            with open(config_path, 'w') as f:
                json.dump(asdict(config), f, indent=2)
            
            # Créer métadonnées ORP
            orp_metadata = OrpMetadata(
                phantom_id=phantom_id,
                phantom_name=phantom_name,
                server_url=self.projection_server_url,
                dimensions=(width, height),
                access_token=secrets.token_urlsafe(32),
                created_at=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Générer fichier .orp
            orp_path = self._generate_orp_file(orp_metadata, urn_dir)
            
            logger.info(f"✅ URN Phantom créée: {phantom_id} ({config.total_fragments} fragments)")
            
            return {
                "status": "success",
                "phantom_id": phantom_id,
                "urn_config": asdict(config),
                "orp_file": str(orp_path),
                "total_fragments": config.total_fragments,
                "projection_server": self.projection_server_url,
                "access_token": orp_metadata.access_token
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur combustion: {e}")
            raise
    
    def _atomic_fragmentation(self, img_array: np.ndarray, urn_dir: Path, phantom_id: str) -> Dict[str, str]:
        """
        Fragmentation atomique des pixels avec chaînage cryptographique
        """
        height, width, _ = img_array.shape
        total_pixels = width * height
        
        # Générer noms de fragments aléatoires
        fragment_names = [f"ash_{secrets.token_hex(16)}.pxl" for _ in range(total_pixels)]
        np.random.shuffle(fragment_names)
        
        logger.info(f"🧬 Fragmentation atomique: {total_pixels} cendres")
        
        fragments_map = {}
        
        # Créer chaîne de fragments
        for i in range(height):
            for j in range(width):
                pixel_index = i * width + j
                
                # Couleur du pixel
                color = tuple(img_array[i, j].tolist())
                
                # Clé et nom suivant (chaînage circulaire)
                next_index = (pixel_index + 1) % total_pixels
                next_key = Fernet.generate_key()
                next_name = fragment_names[next_index]
                
                # Créer fragment atomique
                fragment = AshFragment(
                    color_rgb=color,
                    position=(j, i),
                    next_fragment_name=next_name,
                    next_decrypt_key=next_key,
                    creation_timestamp=time.time()
                )
                
                # Crypter et sauvegarder fragment
                fragment_path = self._save_encrypted_fragment(
                    fragment_names[pixel_index], 
                    fragment, 
                    urn_dir, 
                    phantom_id
                )
                
                fragments_map[fragment_names[pixel_index]] = str(fragment_path)
        
        return fragments_map
    
    def _save_encrypted_fragment(self, fragment_name: str, fragment: AshFragment, urn_dir: Path, phantom_id: str) -> Path:
        """Sauvegarde un fragment crypté"""
        try:
            # Sérialiser fragment
            fragment_data = asdict(fragment)
            
            # Encoder bytes en base64 pour JSON
            if isinstance(fragment_data['next_decrypt_key'], bytes):
                fragment_data['next_decrypt_key'] = base64.b64encode(fragment_data['next_decrypt_key']).decode()
            
            fragment_json = json.dumps(fragment_data)
            
            # Crypter avec clé dérivée
            fragment_key = self._derive_fragment_key(fragment_name, phantom_id)
            cipher = Fernet(fragment_key)
            encrypted_data = cipher.encrypt(fragment_json.encode())
            
            # Sauvegarder
            fragment_path = urn_dir / fragment_name
            with open(fragment_path, 'wb') as f:
                f.write(encrypted_data)
            
            return fragment_path
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde fragment {fragment_name}: {e}")
            raise
    
    def _derive_fragment_key(self, fragment_name: str, phantom_id: str) -> bytes:
        """Dérive une clé de cryptage pour un fragment"""
        key_material = f"{fragment_name}:{phantom_id}".encode()
        digest = hashlib.sha256(key_material).digest()
        return base64.urlsafe_b64encode(digest[:32])
    
    def _generate_orp_file(self, metadata: OrpMetadata, urn_dir: Path) -> Path:
        """Génère un fichier .orp authentique"""
        orp_data = {
            "format_version": "1.0.0",
            "phantom_id": metadata.phantom_id,
            "phantom_name": metadata.phantom_name,
            "mime_type": "image/phantom",
            "dimensions": {
                "width": metadata.dimensions[0],
                "height": metadata.dimensions[1]
            },
            "created_at": metadata.created_at,
            "file_id": str(uuid.uuid4()),
            "description": f"Phantom URN: {metadata.phantom_name}",
            "access_data": {
                "server_url": metadata.server_url,
                "phantom_endpoint": f"/phantom/{metadata.phantom_id}",
                "websocket_url": metadata.server_url.replace("http", "ws") + "/ws",
                "access_method": "websocket_primary"
            },
            "security_data": {
                "access_token": metadata.access_token,
                "permissions": {
                    "view": True,
                    "download": False,  # Jamais de download physique !
                    "share": True,
                    "expires_at": None
                },
                "requires_server": True,
                "anti_capture": True,
                "phantom_protocol": True
            }
        }
        
        # Créer fichier .orp
        orp_path = urn_dir / f"{metadata.phantom_name}.orp"
        with open(orp_path, 'w') as f:
            json.dump(orp_data, f, indent=2)
        
        return orp_path
    
    def get_phantom_for_projection(self, phantom_id: str, access_token: str) -> Optional[np.ndarray]:
        """
        🔄 PHOENIX - Reconstruction d'image pour projection
        """
        try:
            if phantom_id not in self.active_urns:
                logger.error(f"URN {phantom_id} non trouvée")
                return None
            
            # Vérifier token d'accès (simulation)
            if not access_token:
                logger.error("Token d'accès requis")
                return None
            
            # Check cache
            if phantom_id in self.phantom_cache:
                logger.info(f"🔄 Cache hit pour {phantom_id}")
                return self.phantom_cache[phantom_id]
            
            # Reconstruction depuis fragments
            config = self.active_urns[phantom_id]
            fragments_map = self.urn_fragments[phantom_id]
            
            logger.info(f"🔄 Reconstruction Phoenix: {phantom_id}")
            
            # Reconstruire image
            width, height = config.image_dimensions
            reconstructed = np.zeros((height, width, 3), dtype=np.uint8)
            
            urn_dir = self.storage_dir / phantom_id
            
            # Décrypter et assembler fragments
            for fragment_name, fragment_path in fragments_map.items():
                try:
                    fragment = self._load_encrypted_fragment(fragment_name, phantom_id, urn_dir)
                    if fragment:
                        x, y = fragment.position
                        if 0 <= x < width and 0 <= y < height:
                            reconstructed[y, x] = fragment.color_rgb
                except Exception as e:
                    logger.warning(f"Erreur fragment {fragment_name}: {e}")
                    continue
            
            # Cache pour projections futures
            self.phantom_cache[phantom_id] = reconstructed
            
            logger.info(f"✅ Phoenix terminé: {phantom_id}")
            return reconstructed
            
        except Exception as e:
            logger.error(f"❌ Erreur reconstruction Phoenix: {e}")
            return None
    
    def _load_encrypted_fragment(self, fragment_name: str, phantom_id: str, urn_dir: Path) -> Optional[AshFragment]:
        """Charge et décrypte un fragment"""
        try:
            fragment_path = urn_dir / fragment_name
            if not fragment_path.exists():
                return None
            
            # Charger données cryptées
            with open(fragment_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Décrypter
            fragment_key = self._derive_fragment_key(fragment_name, phantom_id)
            cipher = Fernet(fragment_key)
            decrypted_json = cipher.decrypt(encrypted_data).decode()
            
            # Désérialiser
            fragment_data = json.loads(decrypted_json)
            
            # Décoder clé suivante
            if isinstance(fragment_data['next_decrypt_key'], str):
                fragment_data['next_decrypt_key'] = base64.b64decode(fragment_data['next_decrypt_key'])
            
            return AshFragment(**fragment_data)
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement fragment {fragment_name}: {e}")
            return None
    
    def list_active_phantoms(self) -> List[Dict[str, Any]]:
        """Liste des URNs Phantom actives"""
        phantoms = []
        for phantom_id, config in self.active_urns.items():
            phantoms.append({
                "phantom_id": phantom_id,
                "dimensions": config.image_dimensions,
                "total_fragments": config.total_fragments,
                "created_at": config.creation_time,
                "authorized_node": config.authorized_node
            })
        return phantoms
    
    def delete_phantom_urn(self, phantom_id: str) -> bool:
        """Supprime une URN Phantom (destruction complète)"""
        try:
            if phantom_id not in self.active_urns:
                return False
            
            # Supprimer dossier URN
            urn_dir = self.storage_dir / phantom_id
            if urn_dir.exists():
                import shutil
                shutil.rmtree(urn_dir)
            
            # Nettoyer registres
            del self.active_urns[phantom_id]
            if phantom_id in self.urn_fragments:
                del self.urn_fragments[phantom_id]
            if phantom_id in self.phantom_cache:
                del self.phantom_cache[phantom_id]
            if phantom_id in self.activation_keys:
                del self.activation_keys[phantom_id]
            
            logger.info(f"🔥 URN Phantom détruite: {phantom_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur destruction URN: {e}")
            return False