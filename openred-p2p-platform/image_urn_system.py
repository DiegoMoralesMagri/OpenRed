"""
OpenRed Image URN System
========================

Système dual pour les images:
1. Streaming ORP (OpenRed Protocol) - Projection temps réel
2. URN Download System - Partage et téléchargement

Fonctionnalités:
- Upload d'images → Conversion URN
- Streaming Phantom (protocole ORP)
- Partage URN entre amis
- Téléchargement URN sécurisé
"""

import os
import io
import time
import hashlib
import base64
import json
from typing import Dict, List, Optional, Tuple
from PIL import Image
import asyncio
from dataclasses import dataclass
from enum import Enum

class ImageURNType(Enum):
    """Types de URN image"""
    DOWNLOAD = "download"  # URN téléchargeable
    STREAM = "stream"      # URN streamable ORP
    HYBRID = "hybrid"      # Les deux modes

class ORPStreamMode(Enum):
    """Modes de streaming ORP"""
    REAL_TIME = "real_time"     # Streaming temps réel
    PROJECTION = "projection"   # Projection d'écran
    PHANTOM = "phantom"         # Mode Phantom URN

@dataclass
class ImageURNMetadata:
    """Métadonnées URN image"""
    urn_id: str
    filename: str
    original_size: int
    compressed_size: int
    dimensions: Tuple[int, int]
    mime_type: str
    upload_time: float
    owner_id: str
    urn_type: ImageURNType
    stream_mode: Optional[ORPStreamMode] = None
    access_level: str = "friends"
    download_count: int = 0
    stream_count: int = 0

class ImageURNProcessor:
    """Processeur d'images pour URN"""
    
    def __init__(self, max_size: int = 2048, quality: int = 85):
        self.max_size = max_size
        self.quality = quality
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    def validate_image(self, file_data: bytes, filename: str) -> bool:
        """Valide une image"""
        try:
            # Vérifier l'extension
            ext = os.path.splitext(filename.lower())[1]
            if ext not in self.supported_formats:
                return False
            
            # Vérifier que c'est une vraie image
            image = Image.open(io.BytesIO(file_data))
            image.verify()
            return True
        except Exception:
            return False
    
    def process_image(self, file_data: bytes, filename: str) -> Tuple[bytes, Dict]:
        """Traite une image pour URN"""
        try:
            image = Image.open(io.BytesIO(file_data))
            
            # Conserver les métadonnées originales
            original_size = len(file_data)
            original_dimensions = image.size
            
            # Redimensionner si nécessaire
            if max(image.size) > self.max_size:
                image.thumbnail((self.max_size, self.max_size), Image.Resampling.LANCZOS)
            
            # Convertir en RGB si nécessaire
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Compresser
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=self.quality, optimize=True)
            compressed_data = output.getvalue()
            
            metadata = {
                'original_size': original_size,
                'compressed_size': len(compressed_data),
                'original_dimensions': original_dimensions,
                'final_dimensions': image.size,
                'compression_ratio': len(compressed_data) / original_size,
                'mime_type': 'image/jpeg'
            }
            
            return compressed_data, metadata
            
        except Exception as e:
            raise ValueError(f"Erreur traitement image: {e}")

class ORPStreamingEngine:
    """Moteur de streaming ORP (OpenRed Protocol)"""
    
    def __init__(self):
        self.active_streams: Dict[str, Dict] = {}
        self.stream_viewers: Dict[str, List[str]] = {}
        self.projection_buffer: Dict[str, bytes] = {}
    
    async def start_stream(self, urn_id: str, image_data: bytes, 
                          mode: ORPStreamMode = ORPStreamMode.REAL_TIME) -> str:
        """Démarre un stream ORP"""
        stream_id = f"orp_{int(time.time())}_{urn_id[:8]}"
        
        self.active_streams[stream_id] = {
            'urn_id': urn_id,
            'image_data': image_data,
            'mode': mode,
            'start_time': time.time(),
            'viewer_count': 0,
            'projection_active': mode in [ORPStreamMode.PROJECTION, ORPStreamMode.PHANTOM]
        }
        
        self.stream_viewers[stream_id] = []
        
        if mode == ORPStreamMode.PROJECTION:
            await self._setup_projection(stream_id, image_data)
        
        return stream_id
    
    async def _setup_projection(self, stream_id: str, image_data: bytes):
        """Configure la projection d'écran"""
        # Traiter l'image pour projection
        image = Image.open(io.BytesIO(image_data))
        
        # Créer différentes résolutions pour la projection
        projection_sizes = [(1920, 1080), (1280, 720), (854, 480)]
        
        for size in projection_sizes:
            proj_image = image.copy()
            proj_image.thumbnail(size, Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            proj_image.save(output, format='JPEG', quality=90)
            
            self.projection_buffer[f"{stream_id}_{size[0]}x{size[1]}"] = output.getvalue()
    
    def join_stream(self, stream_id: str, viewer_id: str) -> bool:
        """Rejoindre un stream"""
        if stream_id in self.active_streams and viewer_id not in self.stream_viewers[stream_id]:
            self.stream_viewers[stream_id].append(viewer_id)
            self.active_streams[stream_id]['viewer_count'] += 1
            return True
        return False
    
    def leave_stream(self, stream_id: str, viewer_id: str):
        """Quitter un stream"""
        if stream_id in self.stream_viewers and viewer_id in self.stream_viewers[stream_id]:
            self.stream_viewers[stream_id].remove(viewer_id)
            self.active_streams[stream_id]['viewer_count'] -= 1
    
    def get_stream_data(self, stream_id: str, resolution: str = "1280x720") -> Optional[bytes]:
        """Récupérer les données de stream"""
        if stream_id in self.active_streams:
            if resolution in self.projection_buffer:
                return self.projection_buffer[f"{stream_id}_{resolution}"]
            return self.active_streams[stream_id]['image_data']
        return None
    
    def get_active_streams(self) -> List[Dict]:
        """Liste des streams actifs"""
        return [
            {
                'stream_id': sid,
                'urn_id': data['urn_id'],
                'mode': data['mode'].value,
                'viewer_count': data['viewer_count'],
                'duration': time.time() - data['start_time']
            }
            for sid, data in self.active_streams.items()
        ]

class ImageURNSystem:
    """Système principal de gestion des URN images"""
    
    def __init__(self, phantom_urn_engine, storage_path: str = "urn_images"):
        self.phantom_urn_engine = phantom_urn_engine
        self.storage_path = storage_path
        self.processor = ImageURNProcessor()
        self.orp_engine = ORPStreamingEngine()
        self.urns: Dict[str, ImageURNMetadata] = {}
        self.download_tokens: Dict[str, Dict] = {}
        
        # Créer le dossier de stockage
        os.makedirs(storage_path, exist_ok=True)
    
    def generate_urn_id(self, image_data: bytes, owner_id: str) -> str:
        """Génère un ID URN unique"""
        hash_input = f"{time.time()}{len(image_data)}{owner_id}".encode()
        return f"urn_img_{hashlib.sha256(hash_input).hexdigest()[:16]}"
    
    async def upload_image(self, file_data: bytes, filename: str, 
                          owner_id: str, urn_type: ImageURNType = ImageURNType.HYBRID) -> str:
        """Upload et conversion d'image en URN"""
        
        # Validation
        if not self.processor.validate_image(file_data, filename):
            raise ValueError("Format d'image non supporté ou fichier corrompu")
        
        # Traitement
        processed_data, process_meta = self.processor.process_image(file_data, filename)
        
        # Génération URN
        urn_id = self.generate_urn_id(processed_data, owner_id)
        
        # Stockage fichier
        file_path = os.path.join(self.storage_path, f"{urn_id}.jpg")
        with open(file_path, 'wb') as f:
            f.write(processed_data)
        
        # Métadonnées URN
        metadata = ImageURNMetadata(
            urn_id=urn_id,
            filename=filename,
            original_size=process_meta['original_size'],
            compressed_size=process_meta['compressed_size'],
            dimensions=process_meta['final_dimensions'],
            mime_type=process_meta['mime_type'],
            upload_time=time.time(),
            owner_id=owner_id,
            urn_type=urn_type
        )
        
        self.urns[urn_id] = metadata
        
        # Enregistrer dans Phantom URN Engine
        await self._register_phantom_urn(urn_id, metadata, processed_data)
        
        return urn_id
    
    async def _register_phantom_urn(self, urn_id: str, metadata: ImageURNMetadata, data: bytes):
        """Enregistre l'URN dans le moteur Phantom"""
        urn_info = {
            'id': urn_id,
            'type': 'image',
            'subtype': metadata.urn_type.value,
            'size': len(data),
            'metadata': {
                'filename': metadata.filename,
                'dimensions': metadata.dimensions,
                'mime_type': metadata.mime_type,
                'owner': metadata.owner_id
            },
            'access_level': metadata.access_level,
            'created': metadata.upload_time
        }
        
        if hasattr(self.phantom_urn_engine, 'register_local_urn'):
            await self.phantom_urn_engine.register_local_urn(urn_id, urn_info)
    
    async def start_orp_stream(self, urn_id: str, mode: ORPStreamMode = ORPStreamMode.PROJECTION) -> str:
        """Démarre un stream ORP pour une image URN"""
        if urn_id not in self.urns:
            raise ValueError("URN non trouvé")
        
        metadata = self.urns[urn_id]
        if metadata.urn_type not in [ImageURNType.STREAM, ImageURNType.HYBRID]:
            raise ValueError("URN non streamable")
        
        # Charger l'image
        file_path = os.path.join(self.storage_path, f"{urn_id}.jpg")
        with open(file_path, 'rb') as f:
            image_data = f.read()
        
        # Démarrer le stream
        stream_id = await self.orp_engine.start_stream(urn_id, image_data, mode)
        
        # Mettre à jour les statistiques
        metadata.stream_count += 1
        metadata.stream_mode = mode
        
        return stream_id
    
    def generate_download_token(self, urn_id: str, requester_id: str, 
                               expires_in: int = 3600) -> str:
        """Génère un token de téléchargement"""
        if urn_id not in self.urns:
            raise ValueError("URN non trouvé")
        
        metadata = self.urns[urn_id]
        if metadata.urn_type not in [ImageURNType.DOWNLOAD, ImageURNType.HYBRID]:
            raise ValueError("URN non téléchargeable")
        
        token = hashlib.sha256(f"{urn_id}{requester_id}{time.time()}".encode()).hexdigest()[:24]
        
        self.download_tokens[token] = {
            'urn_id': urn_id,
            'requester_id': requester_id,
            'expires': time.time() + expires_in,
            'used': False
        }
        
        return token
    
    def download_urn(self, token: str) -> Tuple[bytes, str, str]:
        """Télécharge un URN avec token"""
        if token not in self.download_tokens:
            raise ValueError("Token invalide")
        
        token_data = self.download_tokens[token]
        
        if token_data['used']:
            raise ValueError("Token déjà utilisé")
        
        if time.time() > token_data['expires']:
            del self.download_tokens[token]
            raise ValueError("Token expiré")
        
        urn_id = token_data['urn_id']
        metadata = self.urns[urn_id]
        
        # Charger l'image
        file_path = os.path.join(self.storage_path, f"{urn_id}.jpg")
        with open(file_path, 'rb') as f:
            image_data = f.read()
        
        # Marquer comme utilisé
        token_data['used'] = True
        metadata.download_count += 1
        
        return image_data, metadata.filename, metadata.mime_type
    
    def get_user_urns(self, user_id: str) -> List[Dict]:
        """Récupère les URNs d'un utilisateur"""
        user_urns = []
        for urn_id, metadata in self.urns.items():
            if metadata.owner_id == user_id:
                user_urns.append({
                    'urn_id': urn_id,
                    'filename': metadata.filename,
                    'size': metadata.compressed_size,
                    'dimensions': metadata.dimensions,
                    'upload_time': metadata.upload_time,
                    'type': metadata.urn_type.value,
                    'download_count': metadata.download_count,
                    'stream_count': metadata.stream_count
                })
        
        return sorted(user_urns, key=lambda x: x['upload_time'], reverse=True)
    
    def get_urn_info(self, urn_id: str) -> Optional[Dict]:
        """Informations sur un URN"""
        if urn_id not in self.urns:
            return None
        
        metadata = self.urns[urn_id]
        return {
            'urn_id': urn_id,
            'filename': metadata.filename,
            'size': metadata.compressed_size,
            'dimensions': metadata.dimensions,
            'mime_type': metadata.mime_type,
            'upload_time': metadata.upload_time,
            'owner_id': metadata.owner_id,
            'type': metadata.urn_type.value,
            'access_level': metadata.access_level,
            'download_count': metadata.download_count,
            'stream_count': metadata.stream_count,
            'stream_mode': metadata.stream_mode.value if metadata.stream_mode else None
        }
    
    def get_system_stats(self) -> Dict:
        """Statistiques du système"""
        total_urns = len(self.urns)
        total_size = sum(m.compressed_size for m in self.urns.values())
        total_downloads = sum(m.download_count for m in self.urns.values())
        total_streams = sum(m.stream_count for m in self.urns.values())
        
        by_type = {}
        for metadata in self.urns.values():
            t = metadata.urn_type.value
            by_type[t] = by_type.get(t, 0) + 1
        
        return {
            'total_urns': total_urns,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_downloads': total_downloads,
            'total_streams': total_streams,
            'active_streams': len(self.orp_engine.active_streams),
            'by_type': by_type,
            'active_tokens': len([t for t in self.download_tokens.values() if not t['used']])
        }