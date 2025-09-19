# FR: Fichier: __init__.py — Initialisation du package models
# EN: File: __init__.py — Package initialization for models
# ES: Archivo: __init__.py — Inicialización del paquete models
# ZH: 文件: __init__.py — models 包的初始化

# Modèles de données pour l'écosystème O-Red

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid

Base = declarative_base()

# ================================
# MODÈLES SQLAlchemy (Base de données)
# ================================

class User(Base):
    """Modèle utilisateur O-Red avec O-RedID"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ored_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    public_key = Column(Text, nullable=False)  # Clé publique O-RedID
    profile_data = Column(JSON)  # Données de profil chiffrées
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Préférences
    privacy_level = Column(String(20), default="standard")  # minimum, standard, maximum
    ai_enabled = Column(Boolean, default=True)
    
    # Relations
    nodes = relationship("Node", back_populates="owner")
    messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient")

class Node(Base):
    """Nœud P2P dans le réseau O-Red"""
    __tablename__ = "nodes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Informations réseau
    node_id = Column(String, unique=True, nullable=False, index=True)
    ip_address = Column(String(45))  # IPv6 compatible
    port = Column(Integer)
    public_key = Column(Text, nullable=False)
    
    # Statut
    status = Column(String(20), default="online")  # online, offline, maintenance
    last_heartbeat = Column(DateTime(timezone=True))
    version = Column(String(20))
    
    # Capacités
    capabilities = Column(JSON)  # Services supportés par le nœud
    storage_available = Column(Integer, default=0)  # Go disponibles
    bandwidth_up = Column(Integer, default=0)  # Mbps
    bandwidth_down = Column(Integer, default=0)  # Mbps
    
    # Métriques
    uptime_percentage = Column(Float, default=0.0)
    reputation_score = Column(Integer, default=100)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    owner = relationship("User", back_populates="nodes")

class Message(Base):
    """Messages dans le réseau fédéré O-Red"""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(String, ForeignKey("users.id"))  # Null pour messages publics
    
    # Contenu
    content_type = Column(String(50), default="text")  # text, image, file, ai_response
    content = Column(Text)  # Contenu chiffré
    content_hash = Column(String(64))  # Hash pour vérification d'intégrité
    
    # Métadonnées
    visibility = Column(String(20), default="public")  # public, private, profile_specific
    profile_context = Column(String(50))  # famille, amis, professionnel, public
    
    # Signatures et vérification
    signature = Column(Text)  # Signature numérique
    pq_signature = Column(Text)  # Signature post-quantique
    
    # État
    is_federated = Column(Boolean, default=False)
    federation_nodes = Column(JSON)  # Nœuds ayant reçu le message
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))  # Messages éphémères
    
    # Relations
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="messages_received")

class AIRequest(Base):
    """Requêtes à l'IA O-RedMind"""
    __tablename__ = "ai_requests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Requête
    request_type = Column(String(50), nullable=False)  # text_generation, analysis, search, etc.
    input_data = Column(Text)  # Données d'entrée chiffrées
    input_hash = Column(String(64))
    
    # Traitement
    processing_mode = Column(String(20), default="local")  # local, distributed, hybrid
    allocated_nodes = Column(JSON)  # Nœuds utilisés pour le calcul distribué
    
    # Résultat
    output_data = Column(Text)  # Résultat chiffré
    confidence_score = Column(Float)
    processing_time = Column(Float)  # Secondes
    
    # Statut
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

class StoreItem(Base):
    """Articles dans O-RedStore"""
    __tablename__ = "store_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    seller_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Informations produit
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    tags = Column(JSON)
    
    # Versioning
    version = Column(String(20), default="1.0.0")
    changelog = Column(Text)
    
    # Distribution
    file_hash = Column(String(64))  # Hash IPFS ou équivalent
    file_size = Column(Integer)  # Bytes
    download_nodes = Column(JSON)  # Nœuds hébergeant le fichier
    
    # Pricing
    price = Column(Float, default=0.0)  # 0 = gratuit
    currency = Column(String(10), default="ORED")  # Token O-Red
    license = Column(String(50), default="GPL-3.0")
    
    # Métriques
    download_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Statut
    status = Column(String(20), default="active")  # active, suspended, removed
    verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SearchIndex(Base):
    """Index de recherche distribué O-RedSearch"""
    __tablename__ = "search_index"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Document indexé
    url = Column(String(2000), nullable=False, index=True)
    title = Column(String(500))
    content_hash = Column(String(64), unique=True, nullable=False)
    
    # Contenu
    content_preview = Column(Text)  # Aperçu du contenu
    keywords = Column(JSON)  # Mots-clés extraits
    language = Column(String(10))
    
    # Métadonnées
    domain = Column(String(200), index=True)
    content_type = Column(String(50))
    file_size = Column(Integer)
    
    # Qualité et pertinence
    quality_score = Column(Float, default=0.0)
    authority_score = Column(Float, default=0.0)
    freshness_score = Column(Float, default=1.0)
    
    # Indexation distribuée
    indexed_by_nodes = Column(JSON)  # Nœuds ayant indexé ce contenu
    
    # Timestamps
    first_indexed = Column(DateTime(timezone=True), server_default=func.now())
    last_crawled = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True))

# ================================
# MODÈLES Pydantic (API/Validation)
# ================================

class NodeCapabilities(BaseModel):
    """Capacités d'un nœud"""
    ai_processing: bool = False
    file_storage: bool = False
    search_indexing: bool = False
    message_relay: bool = True
    store_hosting: bool = False

class NodeStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class PrivacyLevel(str, Enum):
    MINIMUM = "minimum"
    STANDARD = "standard"
    MAXIMUM = "maximum"

class UserCreate(BaseModel):
    """Schéma de création d'utilisateur"""
    username: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_-]+$")
    email: str = Field(..., regex="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    public_key: str
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD
    profile_data: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    """Schéma de réponse utilisateur"""
    id: str
    ored_id: str
    username: str
    email: str
    public_key: str
    is_active: bool
    is_verified: bool
    privacy_level: str
    created_at: datetime
    last_seen: Optional[datetime]
    
    class Config:
        from_attributes = True

class NodeRegister(BaseModel):
    """Schéma d'enregistrement de nœud"""
    owner_id: str
    ip_address: str = Field(..., regex="^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$|^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$")
    port: int = Field(..., ge=1, le=65535)
    public_key: str
    capabilities: NodeCapabilities
    storage_available: int = Field(default=0, ge=0)
    bandwidth_up: int = Field(default=0, ge=0)
    bandwidth_down: int = Field(default=0, ge=0)

class NodeResponse(BaseModel):
    """Schéma de réponse nœud"""
    id: str
    node_id: str
    owner_id: str
    ip_address: str
    port: int
    status: str
    capabilities: Dict[str, Any]
    uptime_percentage: float
    reputation_score: int
    created_at: datetime
    last_heartbeat: Optional[datetime]
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    """Schéma de création de message"""
    recipient_id: Optional[str] = None
    content: str
    content_type: str = "text"
    visibility: str = "public"
    profile_context: str = "public"
    expires_at: Optional[datetime] = None

class MessageResponse(BaseModel):
    """Schéma de réponse message"""
    id: str
    sender_id: str
    recipient_id: Optional[str]
    content: str
    content_type: str
    visibility: str
    profile_context: str
    created_at: datetime
    is_federated: bool
    
    class Config:
        from_attributes = True

class AIRequestCreate(BaseModel):
    """Schéma de requête IA"""
    request_type: str = Field(..., regex="^[a-zA-Z_]+$")
    input_data: str
    processing_mode: str = "local"
    
    @validator('request_type')
    def validate_request_type(cls, v):
        allowed_types = [
            "text_generation", "analysis", "search", "translation", 
            "summarization", "question_answering", "code_generation"
        ]
        if v not in allowed_types:
            raise ValueError(f'request_type must be one of: {", ".join(allowed_types)}')
        return v

class AIRequestResponse(BaseModel):
    """Schéma de réponse IA"""
    id: str
    request_type: str
    status: str
    output_data: Optional[str]
    confidence_score: Optional[float]
    processing_time: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class StoreItemCreate(BaseModel):
    """Schéma de création d'article store"""
    name: str = Field(..., min_length=1, max_length=200)
    description: str
    category: str
    tags: List[str] = []
    version: str = "1.0.0"
    file_hash: str
    file_size: int = Field(..., ge=0)
    price: float = Field(default=0.0, ge=0.0)
    license: str = "GPL-3.0"

class StoreItemResponse(BaseModel):
    """Schéma de réponse article store"""
    id: str
    seller_id: str
    name: str
    description: str
    category: str
    version: str
    price: float
    currency: str
    license: str
    download_count: int
    rating_average: float
    rating_count: int
    status: str
    verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    """Schéma de requête de recherche"""
    query: str = Field(..., min_length=1, max_length=500)
    language: Optional[str] = None
    domain_filter: Optional[str] = None
    content_type_filter: Optional[str] = None
    max_results: int = Field(default=10, ge=1, le=100)
    privacy_mode: str = "anonymous"

class SearchResult(BaseModel):
    """Schéma de résultat de recherche"""
    url: str
    title: str
    content_preview: str
    relevance_score: float
    quality_score: float
    domain: str
    language: str
    last_updated: datetime