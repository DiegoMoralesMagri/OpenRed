#!/usr/bin/env python3
"""
Format de Fichier OpenRed Phantom (.orp)
========================================
Spécification du format révolutionnaire .orp pour images fantômes.
Les fichiers .orp ne contiennent JAMAIS l'image, mais uniquement
les métadonnées pour accéder à la projection phantom.
"""

import json
import base64
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import uuid

class OrpFormat:
    """
    Format OpenRed Phantom (.orp)
    
    Structure:
    - Header: Identification du format
    - Metadata: Informations de la projection
    - Access: Données d'accès au serveur phantom
    - Security: Tokens et vérifications
    - Signature: Intégrité du fichier
    """
    
    VERSION = "1.0.0"
    MAGIC_HEADER = b"ORPHANTOM"  # 9 bytes magic
    
    def __init__(self):
        self.metadata = {}
        self.access_data = {}
        self.security_data = {}
        
    @classmethod
    def create_phantom_file(cls, 
                          phantom_id: str,
                          phantom_name: str,
                          server_url: str,
                          phantom_size: tuple,  # (width, height)
                          mime_type: str = "image/jpeg",
                          access_token: Optional[str] = None,
                          permissions: Optional[Dict] = None) -> 'OrpFormat':
        """
        Crée un nouveau fichier .orp pour une projection phantom
        """
        orp = cls()
        
        # Métadonnées de base
        orp.metadata = {
            "format_version": cls.VERSION,
            "phantom_id": phantom_id,
            "phantom_name": phantom_name,
            "mime_type": mime_type,
            "dimensions": {
                "width": phantom_size[0],
                "height": phantom_size[1]
            },
            "created_at": datetime.now().isoformat(),
            "file_id": str(uuid.uuid4()),
            "description": f"OpenRed Phantom: {phantom_name}"
        }
        
        # Données d'accès
        orp.access_data = {
            "server_url": server_url,
            "phantom_endpoint": f"/phantom/{phantom_id}",
            "websocket_url": server_url.replace("http", "ws") + "/ws",
            "fallback_urls": [],  # Serveurs de secours
            "access_method": "websocket_primary"
        }
        
        # Sécurité et permissions
        orp.security_data = {
            "access_token": access_token,
            "permissions": permissions or {
                "view": True,
                "download": False,  # JAMAIS pour les phantoms !
                "share": True,
                "expires_at": None
            },
            "checksum": cls._generate_checksum(phantom_id, phantom_name),
            "requires_server": True,  # Critique !
            "anti_capture": True
        }
        
        return orp
    
    @staticmethod
    def _generate_checksum(phantom_id: str, phantom_name: str) -> str:
        """Génère un checksum pour l'intégrité du fichier"""
        combined = f"{phantom_id}:{phantom_name}:{datetime.now().date()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def to_orp_bytes(self) -> bytes:
        """
        Sérialise le fichier .orp en bytes
        
        Format binaire:
        [MAGIC_HEADER][VERSION][METADATA_SIZE][METADATA][ACCESS_SIZE][ACCESS][SECURITY_SIZE][SECURITY][SIGNATURE]
        """
        # Sérialisation JSON des sections
        metadata_json = json.dumps(self.metadata, separators=(',', ':')).encode()
        access_json = json.dumps(self.access_data, separators=(',', ':')).encode()
        security_json = json.dumps(self.security_data, separators=(',', ':')).encode()
        
        # Construction du fichier binaire
        data = bytearray()
        
        # Magic header
        data.extend(self.MAGIC_HEADER)
        
        # Version (4 bytes)
        version_bytes = self.VERSION.encode().ljust(4, b'\x00')[:4]
        data.extend(version_bytes)
        
        # Tailles des sections (4 bytes chacune)
        data.extend(len(metadata_json).to_bytes(4, 'little'))
        data.extend(len(access_json).to_bytes(4, 'little'))
        data.extend(len(security_json).to_bytes(4, 'little'))
        
        # Données des sections
        data.extend(metadata_json)
        data.extend(access_json)
        data.extend(security_json)
        
        # Signature d'intégrité (SHA256 des données)
        signature = hashlib.sha256(data).hexdigest().encode()
        data.extend(signature)
        
        return bytes(data)
    
    @classmethod
    def from_orp_bytes(cls, data: bytes) -> 'OrpFormat':
        """
        Désérialise un fichier .orp depuis bytes
        """
        if len(data) < 25:  # Minimum pour header + tailles
            raise ValueError("Fichier .orp invalide: trop petit")
        
        # Vérification magic header
        if data[:9] != cls.MAGIC_HEADER:
            raise ValueError("Fichier .orp invalide: magic header incorrect")
        
        # Version
        version = data[9:13].rstrip(b'\x00').decode()
        
        # Tailles des sections
        offset = 13
        metadata_size = int.from_bytes(data[offset:offset+4], 'little')
        access_size = int.from_bytes(data[offset+4:offset+8], 'little')
        security_size = int.from_bytes(data[offset+8:offset+12], 'little')
        
        # Extraction des sections
        offset = 25  # Après header + tailles
        
        metadata_json = data[offset:offset+metadata_size]
        offset += metadata_size
        
        access_json = data[offset:offset+access_size]
        offset += access_size
        
        security_json = data[offset:offset+security_size]
        offset += security_size
        
        # Signature
        signature = data[offset:offset+64]  # SHA256 = 64 chars hex
        
        # Vérification intégrité
        data_without_sig = data[:offset]
        expected_sig = hashlib.sha256(data_without_sig).hexdigest().encode()
        if signature != expected_sig:
            raise ValueError("Fichier .orp corrompu: signature invalide")
        
        # Création de l'objet
        orp = cls()
        orp.metadata = json.loads(metadata_json.decode())
        orp.access_data = json.loads(access_json.decode())
        orp.security_data = json.loads(security_json.decode())
        
        return orp
    
    def save_to_file(self, filepath: Path):
        """Sauvegarde le fichier .orp"""
        filepath = Path(filepath)
        if not filepath.suffix:
            filepath = filepath.with_suffix('.orp')
        
        with open(filepath, 'wb') as f:
            f.write(self.to_orp_bytes())
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'OrpFormat':
        """Charge un fichier .orp"""
        with open(filepath, 'rb') as f:
            return cls.from_orp_bytes(f.read())
    
    def get_display_info(self) -> Dict[str, Any]:
        """Informations d'affichage pour le viewer"""
        return {
            "name": self.metadata.get("phantom_name", "Phantom Inconnu"),
            "dimensions": self.metadata.get("dimensions", {"width": 0, "height": 0}),
            "server_url": self.access_data.get("server_url", ""),
            "phantom_id": self.metadata.get("phantom_id", ""),
            "created_at": self.metadata.get("created_at", ""),
            "requires_server": self.security_data.get("requires_server", True),
            "file_id": self.metadata.get("file_id", "")
        }
    
    def is_valid(self) -> bool:
        """Vérifie la validité du fichier .orp"""
        required_metadata = ["phantom_id", "phantom_name", "format_version"]
        required_access = ["server_url", "phantom_endpoint"]
        required_security = ["requires_server"]
        
        for key in required_metadata:
            if key not in self.metadata:
                return False
        
        for key in required_access:
            if key not in self.access_data:
                return False
        
        for key in required_security:
            if key not in self.security_data:
                return False
        
        return True

def create_sample_orp():
    """Crée un fichier .orp d'exemple"""
    orp = OrpFormat.create_phantom_file(
        phantom_id="phantom_demo_001",
        phantom_name="Démo OpenRed Phantom",
        server_url="ws://localhost:8001",
        phantom_size=(400, 300),
        mime_type="image/png"
    )
    
    # Ajout de métadonnées additionnelles
    orp.metadata["author"] = "OpenRed System"
    orp.metadata["tags"] = ["demo", "phantom", "test"]
    orp.metadata["description_long"] = "Fichier de démonstration du format OpenRed Phantom (.orp)"
    
    return orp

if __name__ == "__main__":
    # Test du format
    print("🔧 Test du format OpenRed Phantom (.orp)")
    
    # Création
    orp = create_sample_orp()
    print(f"✅ Fichier .orp créé: {orp.metadata['phantom_name']}")
    
    # Sauvegarde
    test_file = Path("test_phantom.orp")
    orp.save_to_file(test_file)
    print(f"💾 Sauvegardé: {test_file}")
    
    # Rechargement
    orp_loaded = OrpFormat.load_from_file(test_file)
    print(f"📂 Rechargé: {orp_loaded.metadata['phantom_name']}")
    
    # Informations
    info = orp_loaded.get_display_info()
    print(f"📋 Info: {info}")
    
    # Validation
    print(f"✅ Valide: {orp_loaded.is_valid()}")
    
    print("\n🎉 Format .orp fonctionnel !")