# FR: Fichier: database.py — Connexion et utilitaires de la base de données
# EN: File: database.py — Database connection utilities
# ES: Archivo: database.py — Utilidades de conexión a base de datos
# ZH: 文件: database.py — 数据库连接和实用程序

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Node(Base):
    __tablename__ = "nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(255))
    server_url = Column(String(500), nullable=False)
    public_key = Column(Text, nullable=False)
    
    # Status and metadata
    status = Column(String(50), default="active")  # active, inactive, suspended
    last_heartbeat = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Technical info
    version = Column(String(50))
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

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, index=True, nullable=False)
    from_node_id = Column(String(255), nullable=False, index=True)
    to_node_id = Column(String(255), nullable=False, index=True)
    
    message_type = Column(String(100), nullable=False)
    content = Column(Text)
    metadata = Column(JSON)
    
    status = Column(String(50), default="pending")  # pending, delivered, failed
    attempts = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())
    delivered_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Message(id='{self.message_id}', from='{self.from_node_id}', to='{self.to_node_id}')>"