#!/usr/bin/env python3
"""
URN SYSTEM DEBUG & PHANTOM INTEGRATION
=====================================
Version de debug pour diagnostiquer les problèmes de sauvegarde
+ Intégration améliorée avec le système PHANTOM
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

# Configuration logging avec plus de détails
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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
    burn_after_reads: int = 1

class PhantomUrnDebug:
    """Version debug de PhantomUrn avec logs détaillés"""
    
    def __init__(self, urn_directory: str):
        self.urn_dir = Path(urn_directory)
        print(f"🔧 DEBUG: Initialisation URN dans: {self.urn_dir}")
        
        # Créer le répertoire avec vérification
        try:
            self.urn_dir.mkdir(exist_ok=True, parents=True)
            print(f"✅ DEBUG: Répertoire créé/vérifié: {self.urn_dir}")
            print(f"📂 DEBUG: Permissions répertoire: {oct(os.stat(self.urn_dir).st_mode)[-3:]}")
        except Exception as e:
            print(f"❌ DEBUG: Erreur création répertoire: {e}")
            raise
        
        # Clés asymétriques
        self.activation_private_key = None
        self.activation_public_key = None
        
        # Configuration
        self.config: Optional[UrnConfig] = None
        self.fragments_map: Dict[str, str] = {}
        
        # État runtime
        self.is_active = False
        self.phoenix_matrix: Optional[np.ndarray] = None
        
    def burn_image(self, image_path: str, authorized_node: str = "node_A") -> Dict[str, Any]:
        """Combustion avec debug détaillé"""
        print(f"🔥 DEBUG: Début combustion de {image_path}")
        
        try:
            # Charger image
            image = Image.open(image_path).convert('RGB')
            print(f"📊 DEBUG: Image chargée: {image.size}, mode: {image.mode}")
            
            # Générer clés d'activation
            self._generate_activation_keys()
            print("🔑 DEBUG: Clés d'activation générées")
            
            # Fragmenter image
            fragments = self._create_fragments(image)
            total_fragments = len(fragments)
            print(f"🧩 DEBUG: {total_fragments} fragments créés")
            
            # Sauvegarder fragments avec debug
            saved_count = 0
            for fragment_name, fragment in fragments.items():
                try:
                    self._save_encrypted_fragment_debug(fragment_name, fragment)
                    saved_count += 1
                    if saved_count % 100 == 0:  # Log tous les 100 fragments
                        print(f"💾 DEBUG: {saved_count}/{total_fragments} fragments sauvés...")
                except Exception as e:
                    print(f"❌ DEBUG: Erreur sauvegarde fragment {fragment_name}: {e}")
                    raise
            
            print(f"✅ DEBUG: Tous les fragments sauvés ({saved_count} total)")
            
            # Créer configuration
            image_hash = hashlib.sha256(image.tobytes()).hexdigest()
            self.config = UrnConfig(
                image_hash=image_hash,
                total_fragments=total_fragments,
                image_dimensions=image.size,
                creation_time=time.time(),
                authorized_node=authorized_node
            )
            
            # Sauvegarder config
            self._save_config_debug()
            
            # Préparer premier fragment pour activation
            first_fragment_name = next(iter(fragments.keys()))
            first_fragment = fragments[first_fragment_name]
            
            print(f"🎯 DEBUG: Premier fragment: {first_fragment_name}")
            
            return {
                "urn_id": str(self.urn_dir.name),
                "total_fragments": total_fragments,
                "activation_public_key": base64.b64encode(
                    self.activation_public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                ).decode(),
                "first_fragment_name": first_fragment_name,
                "first_decrypt_key": base64.b64encode(first_fragment.next_decrypt_key).decode()
            }
            
        except Exception as e:
            print(f"💥 DEBUG: ERREUR CRITIQUE dans burn_image: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _save_encrypted_fragment_debug(self, fragment_name: str, fragment: AshFragment):
        """Sauvegarde avec debug détaillé"""
        try:
            print(f"💾 DEBUG: Sauvegarde fragment {fragment_name}")
            
            # Sérialiser fragment
            fragment_data = asdict(fragment)
            print(f"📋 DEBUG: Fragment data keys: {fragment_data.keys()}")
            
            # Encoder bytes en base64
            if isinstance(fragment_data['next_decrypt_key'], bytes):
                fragment_data['next_decrypt_key'] = base64.b64encode(fragment_data['next_decrypt_key']).decode()
                print("🔄 DEBUG: Clé convertie en base64")
            
            fragment_json = json.dumps(fragment_data)
            print(f"📄 DEBUG: JSON fragment: {len(fragment_json)} chars")
            
            # Crypter
            fragment_key = self._derive_fragment_key(fragment_name)
            cipher = Fernet(fragment_key)
            encrypted_data = cipher.encrypt(fragment_json.encode())
            print(f"🔒 DEBUG: Fragment crypté: {len(encrypted_data)} bytes")
            
            # Sauvegarder
            fragment_path = self.urn_dir / fragment_name
            print(f"💾 DEBUG: Sauvegarde vers: {fragment_path}")
            
            with open(fragment_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Vérifier sauvegarde
            if fragment_path.exists():
                file_size = os.path.getsize(fragment_path)
                print(f"✅ DEBUG: Fragment sauvé! Taille: {file_size} bytes")
                self.fragments_map[fragment_name] = str(fragment_path)
            else:
                print(f"❌ DEBUG: Fichier non créé: {fragment_path}")
                
        except Exception as e:
            print(f"💥 DEBUG: Erreur sauvegarde fragment {fragment_name}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _save_config_debug(self):
        """Sauvegarde config avec debug"""
        try:
            config_path = self.urn_dir / "urn_config.json"
            config_data = asdict(self.config)
            
            print(f"⚙️ DEBUG: Sauvegarde config vers: {config_path}")
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            if config_path.exists():
                print(f"✅ DEBUG: Config sauvée! Taille: {os.path.getsize(config_path)} bytes")
            
        except Exception as e:
            print(f"❌ DEBUG: Erreur sauvegarde config: {e}")
            raise
    
    def _generate_activation_keys(self):
        """Génération clés asymétriques"""
        self.activation_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.activation_public_key = self.activation_private_key.public_key()
    
    def _create_fragments(self, image: Image.Image) -> Dict[str, AshFragment]:
        """Création fragments avec noms aléatoires"""
        fragments = {}
        pixels = np.array(image)
        height, width = pixels.shape[:2]
        
        # Créer chaîne de fragments randomisée
        all_positions = [(x, y) for y in range(height) for x in range(width)]
        
        print(f"🎲 DEBUG: Mélange {len(all_positions)} positions...")
        
        # Créer fragments avec chaînage
        for i, (x, y) in enumerate(all_positions):
            fragment_name = f"ash_{secrets.token_hex(16)}.fragment"
            
            # Déterminer fragment suivant
            if i < len(all_positions) - 1:
                next_fragment_name = f"ash_{secrets.token_hex(16)}.fragment"
            else:
                next_fragment_name = "END_OF_CHAIN"
            
            # Générer clé pour déchiffrer le suivant
            next_key = os.urandom(32)
            
            # Créer fragment
            fragment = AshFragment(
                color_rgb=tuple(pixels[y, x][:3].astype(int)),
                position=(x, y),
                next_fragment_name=next_fragment_name,
                next_decrypt_key=next_key,
                creation_timestamp=time.time()
            )
            
            fragments[fragment_name] = fragment
            
            if i > 0 and i % 1000 == 0:
                print(f"🧩 DEBUG: {i}/{len(all_positions)} fragments créés...")
        
        return fragments
    
    def _derive_fragment_key(self, fragment_name: str) -> bytes:
        """Dérivation clé fragment"""
        key_material = f"fragment_{fragment_name}_{self.config.image_hash if self.config else 'temp'}"
        digest = hashlib.sha256(key_material.encode()).digest()
        return base64.urlsafe_b64encode(digest)
    
    def list_directory_contents(self):
        """Debug: lister le contenu du répertoire"""
        print(f"\n📂 DEBUG: Contenu de {self.urn_dir}:")
        try:
            if self.urn_dir.exists():
                items = list(self.urn_dir.iterdir())
                print(f"📊 DEBUG: {len(items)} éléments trouvés")
                for item in items:
                    if item.is_file():
                        size = os.path.getsize(item)
                        print(f"  📄 {item.name} ({size} bytes)")
                    else:
                        print(f"  📁 {item.name}/")
            else:
                print("❌ DEBUG: Répertoire n'existe pas!")
        except Exception as e:
            print(f"❌ DEBUG: Erreur listage: {e}")

def demo_urn_debug():
    """Demo avec debug complet"""
    print("🔥🦅 SYSTÈME URN - DEBUG COMPLET")
    print("="*50)
    
    # Initialiser système avec debug
    urn_system = PhantomUrnDebug("./demo_urns_debug")
    
    # Créer image test
    print("\n🎨 Création image test...")
    test_image = Image.new('RGB', (10, 10))  # Image très petite pour debug
    # Remplir avec des couleurs différentes
    pixels = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
    test_image = Image.fromarray(pixels)
    test_image.save("test_debug_image.png")
    print("✅ Image test créée: test_debug_image.png")
    
    # Test combustion avec debug
    print("\n🔥 Phase BURN avec debug...")
    try:
        burn_result = urn_system.burn_image("test_debug_image.png", "node_debug")
        print("\n✅ COMBUSTION RÉUSSIE!")
        print(f"URN ID: {burn_result['urn_id']}")
        print(f"Fragments: {burn_result['total_fragments']}")
    except Exception as e:
        print(f"\n💥 ÉCHEC COMBUSTION: {e}")
        import traceback
        traceback.print_exc()
    
    # Vérifier contenu répertoire
    urn_system.list_directory_contents()
    
    # Nettoyage
    if os.path.exists("test_debug_image.png"):
        os.unlink("test_debug_image.png")

if __name__ == "__main__":
    demo_urn_debug()