"""
Service d'authentification pour OpenRed Central API
Authentication service for OpenRed Central API
Servicio de autenticación para OpenRed Central API
OpenRed 中央 API 的身份验证服务

Gestion complète de l'authentification des nodes avec validation
cryptographique et gestion des sessions.

Complete node authentication management with cryptographic
validation and session management.

Gestión completa de autenticación de nodos con validación
criptográfica y gestión de sesiones.

完整的节点身份验证管理，包括加密验证和会话管理。
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import secrets

from ..core.security import crypto_service, jwt_service, security_validator
from ..core.logging import logger, audit_logger
from ..models.schemas import NodeRegistration, AuthTokens
from ..models.database import Node, AuthSession
from ..utils.database import get_db


class AuthService:
    """
    Service d'authentification principal
    Main authentication service
    Servicio de autenticación principal
    主要身份验证服务
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def register_node(self, node_data: NodeRegistration, ip_address: str) -> Dict[str, Any]:
        """
        Enregistre un nouveau node dans le système
        Register a new node in the system
        Registra un nuevo nodo en el sistema
        在系统中注册一个新节点
        """
        logger.info("Starting node registration", node_id=node_data.username)
        
        # Validation des données
        if not security_validator.validate_node_id(node_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid node ID format"
            )
        
        if not security_validator.validate_url(node_data.server_url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid server URL"
            )
        
        if not security_validator.validate_public_key(node_data.public_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid public key format"
            )
        
        # Vérification de l'unicité du node ID
        existing_node = self.db.query(Node).filter(Node.node_id == node_data.username).first()
        if existing_node:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Node ID already exists"
            )
        
        # Vérification du nombre de nodes par IP
        nodes_count = self.db.query(Node).filter(Node.last_ip == ip_address).count()
        if nodes_count >= 5:  # Limite configurable
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many nodes registered from this IP"
            )
        
        try:
            # Création du node
            node = Node(
                node_id=node_data.username,
                display_name=node_data.display_name,
                server_url=node_data.server_url,
                public_key=crypto_service.encrypt_data(node_data.public_key),  # Chiffrement de la clé
                version=node_data.version or "1.0.0",
                capabilities=node_data.capabilities or [],
                status="active",
                last_ip=ip_address,
                created_at=datetime.utcnow(),
                last_heartbeat=datetime.utcnow()
            )
            
            self.db.add(node)
            self.db.commit()
            self.db.refresh(node)
            
            # Génération des tokens d'authentification
            tokens = await self._generate_auth_tokens(node.node_id)
            
            # Log de l'audit
            audit_logger.log_node_registration(
                node_id=node.node_id,
                ip_address=ip_address,
                server_url=node.server_url
            )
            
            logger.info("Node registered successfully", node_id=node.node_id)
            
            return {
                "node_id": node.node_id,
                "tokens": tokens,
                "message": "Node registered successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to register node", error=str(e), node_id=node_data.username)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    async def authenticate_node(self, node_id: str, signature: str, nonce: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """Authentifie un node avec signature cryptographique"""
        logger.info("Starting node authentication", node_id=node_id)
        
        try:
            # Récupération du node
            node = self.db.query(Node).filter(Node.node_id == node_id).first()
            if not node:
                audit_logger.log_authentication_attempt(node_id, False, ip_address)
                return None
            
            # Vérification du statut
            if node.status != "active":
                audit_logger.log_authentication_attempt(node_id, False, ip_address)
                return None
            
            # Déchiffrement de la clé publique
            public_key = crypto_service.decrypt_data(node.public_key)
            
            # Création du message à vérifier (node_id + nonce + timestamp)
            timestamp = datetime.utcnow().isoformat()
            message = f"{node_id}:{nonce}:{timestamp}"
            
            # Vérification de la signature
            if not crypto_service.verify_signature(message, signature, public_key):
                audit_logger.log_authentication_attempt(node_id, False, ip_address)
                return None
            
            # Mise à jour du heartbeat et de l'IP
            node.last_heartbeat = datetime.utcnow()
            node.last_ip = ip_address
            self.db.commit()
            
            # Génération des tokens
            tokens = await self._generate_auth_tokens(node_id)
            
            audit_logger.log_authentication_attempt(node_id, True, ip_address)
            logger.info("Node authenticated successfully", node_id=node_id)
            
            return {
                "node_id": node_id,
                "tokens": tokens,
                "node_info": {
                    "display_name": node.display_name,
                    "capabilities": node.capabilities,
                    "version": node.version
                }
            }
            
        except Exception as e:
            logger.error("Authentication failed", error=str(e), node_id=node_id)
            audit_logger.log_authentication_attempt(node_id, False, ip_address)
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifie un token JWT et retourne les informations du node"""
        payload = jwt_service.verify_token(token)
        if not payload:
            return None
        
        # Vérification de la session
        session = self.db.query(AuthSession).filter(
            AuthSession.node_id == payload.get("sub"),
            AuthSession.token_hash == crypto_service.hash_sha256(token),
            AuthSession.expires_at > datetime.utcnow(),
            AuthSession.revoked == False
        ).first()
        
        if not session:
            return None
        
        # Mise à jour de l'activité
        session.last_used = datetime.utcnow()
        self.db.commit()
        
        return payload
    
    async def refresh_token(self, refresh_token: str, ip_address: str) -> Optional[AuthTokens]:
        """Renouvelle un token d'accès avec un refresh token"""
        payload = jwt_service.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        node_id = payload.get("sub")
        
        # Vérification de la session de refresh
        session = self.db.query(AuthSession).filter(
            AuthSession.node_id == node_id,
            AuthSession.refresh_token_hash == crypto_service.hash_sha256(refresh_token),
            AuthSession.expires_at > datetime.utcnow(),
            AuthSession.revoked == False
        ).first()
        
        if not session:
            return None
        
        # Révocation de l'ancienne session
        session.revoked = True
        self.db.commit()
        
        # Génération de nouveaux tokens
        return await self._generate_auth_tokens(node_id)
    
    async def revoke_token(self, token: str) -> bool:
        """Révoque un token (logout)"""
        payload = jwt_service.verify_token(token)
        if not payload:
            return False
        
        # Révocation de la session
        session = self.db.query(AuthSession).filter(
            AuthSession.node_id == payload.get("sub"),
            AuthSession.token_hash == crypto_service.hash_sha256(token)
        ).first()
        
        if session:
            session.revoked = True
            self.db.commit()
            return True
        
        return False
    
    async def revoke_all_tokens(self, node_id: str) -> bool:
        """Révoque tous les tokens d'un node"""
        sessions = self.db.query(AuthSession).filter(
            AuthSession.node_id == node_id,
            AuthSession.revoked == False
        ).all()
        
        for session in sessions:
            session.revoked = True
        
        self.db.commit()
        return True
    
    async def _generate_auth_tokens(self, node_id: str) -> AuthTokens:
        """Génère une paire de tokens d'authentification"""
        # Données du token
        token_data = {
            "sub": node_id,
            "iss": "openred-central-api",
            "aud": "openred-nodes"
        }
        
        # Génération des tokens
        access_token = jwt_service.create_access_token(token_data)
        refresh_token = jwt_service.create_refresh_token(token_data)
        
        # Sauvegarde de la session
        session = AuthSession(
            node_id=node_id,
            token_hash=crypto_service.hash_sha256(access_token),
            refresh_token_hash=crypto_service.hash_sha256(refresh_token),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=jwt_service.refresh_token_expire_days),
            last_used=datetime.utcnow(),
            revoked=False
        )
        
        self.db.add(session)
        self.db.commit()
        
        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=jwt_service.access_token_expire_minutes * 60
        )
    
    async def cleanup_expired_sessions(self):
        """Nettoie les sessions expirées"""
        expired_sessions = self.db.query(AuthSession).filter(
            AuthSession.expires_at < datetime.utcnow()
        ).all()
        
        for session in expired_sessions:
            self.db.delete(session)
        
        self.db.commit()
        logger.info("Cleaned up expired sessions", count=len(expired_sessions))
