"""
Modèles de base de données pour OpenRed Central API

Définition des tables et relations avec SQLAlchemy ORM.
Optimisé pour la performance et la sécurité.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, Index, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

Base = declarative_base()


class Node(Base):
    """Modèle pour les nodes enregistrés"""
    __tablename__ = "nodes"
    
    # Clé primaire
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identifiants
    node_id = Column(String(64), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    
    # Configuration réseau
    server_url = Column(String(2048), nullable=False)
    public_key = Column(Text, nullable=False)  # Chiffré
    
    # Métadonnées
    version = Column(String(32), nullable=False, default="1.0.0")
    capabilities = Column(JSONB, nullable=True, default=list)
    
    # État et statut
    status = Column(String(32), nullable=False, default="active", index=True)
    last_heartbeat = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_ip = Column(String(45), nullable=True, index=True)  # IPv6 compatible
    
    # Métadonnées temporelles
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Statistiques
    total_messages_sent = Column(Integer, default=0)
    total_messages_received = Column(Integer, default=0)
    last_activity = Column(DateTime, nullable=True)
    
    # Relations
    auth_sessions = relationship("AuthSession", back_populates="node", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.from_node_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.to_node_id", back_populates="receiver")
    
    # Index composites pour performance
    __table_args__ = (
        Index('idx_nodes_status_heartbeat', 'status', 'last_heartbeat'),
        Index('idx_nodes_ip_created', 'last_ip', 'created_at'),
    )


class AuthSession(Base):
    """Sessions d'authentification avec tokens JWT"""
    __tablename__ = "auth_sessions"
    
    # Clé primaire
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Référence au node
    node_id = Column(String(64), ForeignKey("nodes.node_id"), nullable=False, index=True)
    
    # Hashes des tokens (pour révocation)
    token_hash = Column(String(64), nullable=False, index=True)
    refresh_token_hash = Column(String(64), nullable=False, index=True)
    
    # Métadonnées de session
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    last_used = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # État
    revoked = Column(Boolean, default=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Informations de sécurité
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    
    # Relations
    node = relationship("Node", back_populates="auth_sessions")
    
    # Index composites
    __table_args__ = (
        Index('idx_auth_sessions_node_token', 'node_id', 'token_hash'),
        Index('idx_auth_sessions_expires_revoked', 'expires_at', 'revoked'),
    )


class Message(Base):
    """Messages routés entre nodes"""
    __tablename__ = "messages"
    
    # Clé primaire
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(String(64), unique=True, nullable=False, index=True)
    
    # Routing
    from_node_id = Column(String(64), ForeignKey("nodes.node_id"), nullable=False, index=True)
    to_node_id = Column(String(64), ForeignKey("nodes.node_id"), nullable=False, index=True)
    
    # Contenu (chiffré)
    content_type = Column(String(128), nullable=False)
    encrypted_content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)
    
    # Métadonnées
    priority = Column(String(16), default="normal", index=True)
    ttl = Column(DateTime, nullable=False, index=True)
    
    # État
    status = Column(String(32), default="pending", index=True)
    delivery_attempts = Column(Integer, default=0)
    last_attempt = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    sender = relationship("Node", foreign_keys=[from_node_id], back_populates="sent_messages")
    receiver = relationship("Node", foreign_keys=[to_node_id], back_populates="received_messages")
    
    # Index composites
    __table_args__ = (
        Index('idx_messages_status_priority', 'status', 'priority'),
        Index('idx_messages_ttl_status', 'ttl', 'status'),
        Index('idx_messages_from_created', 'from_node_id', 'created_at'),
        Index('idx_messages_to_created', 'to_node_id', 'created_at'),
    )


class AuditLog(Base):
    """Logs d'audit pour traçabilité"""
    __tablename__ = "audit_logs"
    
    # Clé primaire
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identifiants
    node_id = Column(String(64), nullable=True, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Type d'événement
    event_type = Column(String(64), nullable=False, index=True)
    action = Column(String(128), nullable=False)
    
    # Détails
    details = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(String(512), nullable=True)
    
    # Résultat
    success = Column(Boolean, nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Index composites
    __table_args__ = (
        Index('idx_audit_event_timestamp', 'event_type', 'timestamp'),
        Index('idx_audit_node_timestamp', 'node_id', 'timestamp'),
        Index('idx_audit_ip_timestamp', 'ip_address', 'timestamp'),
    )
    capabilities = Column(JSON)  # List of supported features
    
    # Network info
    ip_address = Column(String(45))  # IPv4 or IPv6
    port = Column(Integer)
    
    def __repr__(self):
        return f"<Node(node_id='{self.node_id}', username='{self.username}')>"

class NodeConnection(Base):
    __tablename__ = "node_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    from_node_id = Column(String(255), nullable=False, index=True)
    to_node_id = Column(String(255), nullable=False, index=True)
    
    relationship_type = Column(String(50), nullable=False)  # friend, follower, blocked
    status = Column(String(50), default="pending")  # pending, accepted, rejected
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<NodeConnection(from='{self.from_node_id}', to='{self.to_node_id}', type='{self.relationship_type}')>"
    
    def __repr__(self):
        return f"<Message(id='{self.message_id}', from='{self.from_node_id}', to='{self.to_node_id}')>"