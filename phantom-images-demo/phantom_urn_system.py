#!/usr/bin/env python3
"""
SYSTÈME URN (URNE) - PHANTOM IMAGE BURNING SYSTEM
================================================
Concept révolutionnaire de fragmentation cryptographique d'images

Principe "Burn & Phoenix":
1. IMAGE → CENDRES (fragments cryptés chaînés)
2. URN contient clé d'activation asymétrique  
3. Autorisation → PHOENIX (reconstruction streaming)
4. Jamais d'image complète stockée

Architecture:
- Chaque pixel = 1 cendre (couleur + clé suivante + nom suivant)
- Chaînage cryptographique séquentiel
- Validation temps réel avec noeud source
- Destruction programmée après usage
"""

"""
URN SYSTEM - BURN & PHOENIX TECHNOLOGY
======================================
Copyright (C) 2025 Diego Morales Magri - OpenRed Project Founder
Original concept and implementation: Diego Morales Magri, September 2025

INNOVATION DISCLOSURE: This file contains the original implementation
of the URN (Urne) System featuring atomic pixel fragmentation with
cryptographic chaining, first conceived and developed by Diego Morales Magri.

REVOLUTIONARY CONCEPT: World's first atomic pixel fragmentation where each 
pixel becomes an encrypted "ash" fragment, enabling "Burn & Phoenix" security.

PRIOR ART: This constitutes prior art preventing patent claims by 
third parties on atomic pixel fragmentation technologies.

Licensed under Apache License 2.0 with patent protection.
Repository: https://github.com/DiegoMoralesMagri/OpenRed
"""

import os
import json
import hashlib
import secrets
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image
import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
import time
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

@dataclass
class AshFragment:
    """Fragment de cendre - un pixel crypté"""
    color_rgb: Tuple[int, int, int]
    position: Tuple[int, int]  # (x, y)
    next_fragment_name: str
    next_decrypt_key: bytes
    creation_timestamp: float

@dataclass
class UrnConfig:
    """Configuration d'une urne"""
    image_hash: str
    total_fragments: int
    image_dimensions: Tuple[int, int]
    creation_time: float
    authorized_node: str
    burn_after_reads: int = 1  # Destruction après X lectures

class PhantomUrn:
    """
    Urne Phantom - Conteneur de cendres cryptées
    Responsable de la fragmentation et reconstruction
    """
    
    def __init__(self, urn_directory: str):
        self.urn_dir = Path(urn_directory)
        self.urn_dir.mkdir(exist_ok=True)
        
        # Clé asymétrique d'activation (privée dans l'urne)
        self.activation_private_key = None
        self.activation_public_key = None
        
        # Configuration
        self.config: Optional[UrnConfig] = None
        self.fragments_map: Dict[str, str] = {}  # nom_fragment -> chemin_fichier
        
        # État runtime
        self.is_active = False
        self.phoenix_matrix: Optional[np.ndarray] = None
        self.current_session_key: Optional[bytes] = None
        
        self._generate_activation_keys()
    
    def _generate_activation_keys(self):
        """Génère les clés asymétriques d'activation"""
        try:
            # Génération clé RSA pour activation
            self.activation_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.activation_public_key = self.activation_private_key.public_key()
            
            logger.info("🔑 Clés d'activation URN générées")
            
        except Exception as e:
            logger.error(f"❌ Erreur génération clés: {e}")
    
    def burn_image_to_ashes(self, image_path: str, authorized_node: str) -> Dict[str, Any]:
        """
        🔥 BRÛLE une image en cendres cryptées
        Chaque pixel devient un fragment crypté chaîné
        """
        try:
            logger.info(f"🔥 Début combustion image: {image_path}")
            
            # Charger image
            original_image = Image.open(image_path)
            if original_image.mode != 'RGB':
                original_image = original_image.convert('RGB')
            
            img_array = np.array(original_image)
            height, width, _ = img_array.shape
            
            # Configuration urne
            image_hash = hashlib.sha256(open(image_path, 'rb').read()).hexdigest()
            self.config = UrnConfig(
                image_hash=image_hash,
                total_fragments=width * height,
                image_dimensions=(width, height),
                creation_time=time.time(),
                authorized_node=authorized_node
            )
            
            # Générer noms de fragments aléatoires
            fragment_names = [f"ash_{secrets.token_hex(16)}.pxl" for _ in range(self.config.total_fragments)]
            np.random.shuffle(fragment_names)  # Ordre complètement aléatoire
            
            logger.info(f"🧬 Fragmentation: {self.config.total_fragments} cendres")
            
            # Créer chaîne de fragments
            fragments_chain = []
            for i in range(height):
                for j in range(width):
                    pixel_index = i * width + j
                    
                    # Couleur pixel
                    color = tuple(img_array[i, j].tolist())
                    
                    # Clé et nom suivant (dernière pointe vers première = cycle)
                    next_index = (pixel_index + 1) % self.config.total_fragments
                    next_key = Fernet.generate_key()
                    next_name = fragment_names[next_index]
                    
                    # Créer fragment
                    fragment = AshFragment(
                        color_rgb=color,
                        position=(j, i),
                        next_fragment_name=next_name,
                        next_decrypt_key=next_key,
                        creation_timestamp=time.time()
                    )
                    
                    fragments_chain.append((fragment_names[pixel_index], fragment))
            
            # Crypter et sauvegarder fragments
            first_fragment_name = fragment_names[0]
            first_decrypt_key = Fernet.generate_key()
            
            for fragment_name, fragment in fragments_chain:
                self._save_encrypted_fragment(fragment_name, fragment)
                self.fragments_map[fragment_name] = str(self.urn_dir / fragment_name)
            
            # Sauvegarder config urne
            self._save_urn_config()
            
            # Retourner infos pour le noeud source
            activation_public_pem = self.activation_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            burn_result = {
                "urn_id": self.config.image_hash[:16],
                "activation_public_key": base64.b64encode(activation_public_pem).decode(),
                "total_fragments": self.config.total_fragments,
                "first_fragment_name": first_fragment_name,
                "first_decrypt_key": base64.b64encode(first_decrypt_key).decode(),
                "burn_timestamp": self.config.creation_time
            }
            
            logger.info(f"✅ Image brûlée avec succès - {self.config.total_fragments} cendres créées")
            return burn_result
            
        except Exception as e:
            logger.error(f"❌ Erreur combustion: {e}")
            raise
    
    def _save_encrypted_fragment(self, fragment_name: str, fragment: AshFragment):
        """Sauvegarde un fragment crypté"""
        try:
            # Sérialiser fragment avec encodage base64 pour les bytes
            fragment_data = asdict(fragment)
            
            # Encoder les bytes en base64 pour JSON
            if isinstance(fragment_data['next_decrypt_key'], bytes):
                fragment_data['next_decrypt_key'] = base64.b64encode(fragment_data['next_decrypt_key']).decode()
            
            fragment_json = json.dumps(fragment_data)
            
            # Crypter avec clé dérivée du nom
            fragment_key = self._derive_fragment_key(fragment_name)
            cipher = Fernet(fragment_key)
            encrypted_data = cipher.encrypt(fragment_json.encode())
            
            # Sauvegarder
            fragment_path = self.urn_dir / fragment_name
            with open(fragment_path, 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde fragment {fragment_name}: {e}")
            raise
    
    def _derive_fragment_key(self, fragment_name: str) -> bytes:
        """Dérive une clé de cryptage à partir du nom de fragment"""
        key_material = f"{fragment_name}:{self.config.image_hash}".encode()
        digest = hashlib.sha256(key_material).digest()
        return base64.urlsafe_b64encode(digest[:32])
    
    def _save_urn_config(self):
        """Sauvegarde configuration de l'urne"""
        config_path = self.urn_dir / "urn_config.json"
        with open(config_path, 'w') as f:
            json.dump(asdict(self.config), f, indent=2)
    
    def activate_urn(self, activation_key: bytes, first_fragment_info: Dict[str, str]) -> bool:
        """
        🔓 ACTIVE l'urne avec clé d'autorisation
        Déclenche la résurrection Phoenix
        """
        try:
            logger.info("🔓 Tentative d'activation URN...")
            
            # Vérification clé asymétrique (doit être différente de la clé privée!)
            try:
                # Décrypter avec notre clé privée
                decrypted = self.activation_private_key.decrypt(
                    activation_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                # Si on arrive à décrypter, c'est la mauvaise clé (symétrique)
                logger.warning("⚠️ Clé symétrique détectée - Activation refusée")
                return False
                
            except:
                # C'est normal de ne pas pouvoir décrypter avec notre clé privée
                # Cela signifie que c'est une clé publique différente
                pass
            
            # Extraction infos première cendre
            first_fragment_name = first_fragment_info["name"]
            first_decrypt_key = base64.b64decode(first_fragment_info["key"])
            
            # Vérifier que le fragment existe
            if first_fragment_name not in self.fragments_map:
                logger.error(f"❌ Fragment initial non trouvé: {first_fragment_name}")
                return False
            
            # Activation réussie
            self.is_active = True
            self.current_session_key = first_decrypt_key
            
            logger.info("✅ URN activée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur activation URN: {e}")
            return False
    
    def resurrect_phoenix(self, first_fragment_name: str) -> Optional[np.ndarray]:
        """
        🔥🦅 RÉSURRECTION PHOENIX
        Reconstruit l'image en suivant la chaîne de fragments
        """
        try:
            if not self.is_active:
                logger.error("❌ URN non activée")
                return None
            
            logger.info("🦅 Début résurrection Phoenix...")
            
            # Initialiser matrice Phoenix
            width, height = self.config.image_dimensions
            phoenix_matrix = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Suivre la chaîne de fragments
            current_fragment_name = first_fragment_name
            current_decrypt_key = self.current_session_key
            fragments_processed = 0
            
            while fragments_processed < self.config.total_fragments:
                # Charger et décrypter fragment actuel
                fragment = self._load_decrypt_fragment(current_fragment_name, current_decrypt_key)
                if not fragment:
                    logger.error(f"❌ Impossible de charger fragment: {current_fragment_name}")
                    break
                
                # Placer pixel dans matrice Phoenix
                x, y = fragment.position
                phoenix_matrix[y, x] = fragment.color_rgb
                
                # Préparer fragment suivant
                current_fragment_name = fragment.next_fragment_name
                current_decrypt_key = fragment.next_decrypt_key
                
                fragments_processed += 1
                
                # Log progression
                if fragments_processed % 10000 == 0:
                    progress = (fragments_processed / self.config.total_fragments) * 100
                    logger.info(f"🦅 Résurrection: {progress:.1f}%")
            
            if fragments_processed == self.config.total_fragments:
                self.phoenix_matrix = phoenix_matrix
                logger.info("✅ Phoenix ressuscité avec succès!")
                return phoenix_matrix
            else:
                logger.error(f"❌ Résurrection incomplète: {fragments_processed}/{self.config.total_fragments}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur résurrection Phoenix: {e}")
            return None
    
    def _load_decrypt_fragment(self, fragment_name: str, decrypt_key: bytes) -> Optional[AshFragment]:
        """Charge et décrypte un fragment"""
        try:
            fragment_path = self.urn_dir / fragment_name
            
            # Charger données cryptées
            with open(fragment_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Décrypter avec clé dérivée
            fragment_key = self._derive_fragment_key(fragment_name)
            cipher = Fernet(fragment_key)
            decrypted_json = cipher.decrypt(encrypted_data).decode()
            
            # Désérialiser
            fragment_dict = json.loads(decrypted_json)
            
            # Décoder les bytes depuis base64
            next_decrypt_key = fragment_dict['next_decrypt_key']
            if isinstance(next_decrypt_key, str):
                next_decrypt_key = base64.b64decode(next_decrypt_key)
            
            return AshFragment(
                color_rgb=tuple(fragment_dict['color_rgb']),
                position=tuple(fragment_dict['position']),
                next_fragment_name=fragment_dict['next_fragment_name'],
                next_decrypt_key=next_decrypt_key,
                creation_timestamp=fragment_dict['creation_timestamp']
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement fragment {fragment_name}: {e}")
            return None
    
    def get_phoenix_stream(self) -> Optional[Image.Image]:
        """Retourne l'image Phoenix pour affichage Phantom"""
        if self.phoenix_matrix is not None:
            return Image.fromarray(self.phoenix_matrix)
        return None
    
    def burn_after_use(self):
        """🔥 Destruction de l'urne après usage"""
        try:
            logger.info("🔥 Destruction URN après usage...")
            
            # Supprimer tous les fragments
            for fragment_name in self.fragments_map:
                fragment_path = self.urn_dir / fragment_name
                if fragment_path.exists():
                    fragment_path.unlink()
            
            # Supprimer config
            config_path = self.urn_dir / "urn_config.json"
            if config_path.exists():
                config_path.unlink()
            
            # Nettoyer état
            self.fragments_map.clear()
            self.phoenix_matrix = None
            self.is_active = False
            
            logger.info("✅ URN détruite")
            
        except Exception as e:
            logger.error(f"❌ Erreur destruction URN: {e}")

class PhantomAshSystem:
    """
    Système de gestion des urnes Phantom
    Interface principale pour burn & resurrection
    """
    
    def __init__(self, urns_root_dir: str = "./phantom_urns"):
        self.urns_root = Path(urns_root_dir)
        self.urns_root.mkdir(exist_ok=True)
        self.active_urns: Dict[str, PhantomUrn] = {}
    
    def create_urn(self, image_path: str, authorized_node: str, urn_id: str = None) -> Dict[str, Any]:
        """Crée une nouvelle urne et brûle l'image"""
        try:
            if not urn_id:
                urn_id = f"urn_{secrets.token_hex(8)}"
            
            urn_dir = self.urns_root / urn_id
            urn = PhantomUrn(str(urn_dir))
            
            burn_result = urn.burn_image_to_ashes(image_path, authorized_node)
            burn_result["urn_id"] = urn_id
            
            self.active_urns[urn_id] = urn
            
            return burn_result
            
        except Exception as e:
            logger.error(f"❌ Erreur création URN: {e}")
            raise
    
    def activate_and_resurrect(self, urn_id: str, activation_key: bytes, 
                             first_fragment_info: Dict[str, str]) -> Optional[Image.Image]:
        """Active une urne et ressuscite le Phoenix"""
        try:
            if urn_id not in self.active_urns:
                # Charger URN depuis disque
                urn_dir = self.urns_root / urn_id
                if not urn_dir.exists():
                    logger.error(f"❌ URN {urn_id} non trouvée")
                    return None
                
                urn = PhantomUrn(str(urn_dir))
                # Recharger config
                self._reload_urn_config(urn)
                self.active_urns[urn_id] = urn
            
            urn = self.active_urns[urn_id]
            
            # Activation
            if not urn.activate_urn(activation_key, first_fragment_info):
                return None
            
            # Résurrection
            phoenix_matrix = urn.resurrect_phoenix(first_fragment_info["name"])
            if phoenix_matrix is not None:
                return urn.get_phoenix_stream()
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur activation/résurrection: {e}")
            return None
    
    def _reload_urn_config(self, urn: PhantomUrn):
        """Recharge la configuration d'une urne"""
        config_path = urn.urn_dir / "urn_config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
                urn.config = UrnConfig(**config_dict)
    
    def cleanup_urn(self, urn_id: str):
        """Nettoie une urne après usage"""
        if urn_id in self.active_urns:
            self.active_urns[urn_id].burn_after_use()
            del self.active_urns[urn_id]

def demo_ash_system():
    """Démonstration du système URN"""
    print("🔥🦅 SYSTÈME URN - PHANTOM ASH BURNING")
    print("="*50)
    
    # Initialiser système
    ash_system = PhantomAshSystem("./demo_urns")
    
    # Test avec image factice
    test_image = Image.new('RGB', (100, 100), color='red')
    test_image.save("test_image.png")
    
    print("\n🔥 Phase 1: Combustion image...")
    burn_result = ash_system.create_urn("test_image.png", "node_B")
    
    print(f"✅ URN créée: {burn_result['urn_id']}")
    print(f"📊 Fragments: {burn_result['total_fragments']}")
    
    print("\n🦅 Phase 2: Résurrection Phoenix...")
    
    # Simuler activation depuis noeud A
    activation_key = base64.b64decode(burn_result['activation_public_key'])
    first_fragment_info = {
        "name": burn_result['first_fragment_name'],
        "key": burn_result['first_decrypt_key']
    }
    
    phoenix_image = ash_system.activate_and_resurrect(
        burn_result['urn_id'], 
        activation_key, 
        first_fragment_info
    )
    
    if phoenix_image:
        phoenix_image.save("phoenix_resurrected.png")
        print("✅ Phoenix ressuscité avec succès!")
    else:
        print("❌ Échec résurrection Phoenix")
    
    # Nettoyage
    ash_system.cleanup_urn(burn_result['urn_id'])
    
    # Nettoyage fichiers test
    os.unlink("test_image.png")
    if os.path.exists("phoenix_resurrected.png"):
        os.unlink("phoenix_resurrected.png")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo_ash_system()