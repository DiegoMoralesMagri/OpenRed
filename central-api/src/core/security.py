"""
Service de sécurité et cryptographie pour OpenRed Central API
Security and cryptography service for OpenRed Central API
Servicio de seguridad y criptografía para OpenRed Central API
OpenRed 中央 API 的安全和加密服务

Gestion de toutes les opérations cryptographiques, authentification,
et utilitaires de sécurité.

Management of all cryptographic operations, authentication,
and security utilities.

Gestión de todas las operaciones criptográficas, autenticación
y utilidades de seguridad.

管理所有加密操作、身份验证和安全实用程序。
"""

import jwt
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from passlib.hash import argon2

from .config import settings


class CryptoService:
    """
    Service de cryptographie centralisé
    Centralized cryptography service
    Servicio de criptografía centralizado
    集中式加密服务
    """
    
    def __init__(self):
        # Configuration du hashing des mots de passe | Password hashing configuration | Configuración de hash de contraseñas | 密码哈希配置
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__rounds=settings.password_hash_rounds
        )
        
        # Clé de chiffrement symétrique pour les données sensibles
        self._encryption_key = self._derive_key(settings.encryption_key)
        self.cipher_suite = Fernet(self._encryption_key)
    
    def _derive_key(self, password: str) -> bytes:
        """Dérive une clé de chiffrement à partir d'un mot de passe"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'openred_salt_2024',  # Salt fixe pour la consistance
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def hash_password(self, password: str) -> str:
        """Hash un mot de passe avec Argon2"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe contre son hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def encrypt_data(self, data: str) -> str:
        """Chiffre des données sensibles"""
        encrypted = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Déchiffre des données"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def generate_nonce(self, length: int = 32) -> str:
        """Génère un nonce cryptographiquement sécurisé"""
        return secrets.token_urlsafe(length)
    
    def generate_api_key(self) -> str:
        """Génère une clé API sécurisée"""
        return f"ored_{secrets.token_urlsafe(32)}"
    
    def hash_sha256(self, data: str) -> str:
        """Hash SHA256 d'une chaîne"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_signature(self, data: str, signature: str, public_key: str) -> bool:
        """Vérifie une signature RSA"""
        try:
            # Charge la clé publique
            key = serialization.load_pem_public_key(public_key.encode())
            
            # Vérifie la signature
            key.verify(
                base64.b64decode(signature),
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False


class JWTService:
    """Service de gestion des tokens JWT"""
    
    def __init__(self):
        self.algorithm = settings.jwt_algorithm
        self.private_key = settings.jwt_private_key
        self.public_key = settings.jwt_public_key
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = settings.jwt_refresh_token_expire_days
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Crée un token d'accès JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        return jwt.encode(to_encode, self.private_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Crée un token de rafraîchissement JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        return jwt.encode(to_encode, self.private_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, self.public_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def decode_token_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """Décode un token sans vérification (pour debug uniquement)"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except jwt.DecodeError:
            return None


class SecurityValidator:
    """Validateur de sécurité pour les requêtes"""
    
    @staticmethod
    def validate_node_id(node_id: str) -> bool:
        """Valide le format d'un ID de node"""
        if not node_id or len(node_id) < 8 or len(node_id) > 64:
            return False
        
        # Doit être alphanumerique avec tirets et underscores autorisés
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
        return all(c in allowed_chars for c in node_id)
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Valide une URL de serveur"""
        if not url:
            return False
        
        # Doit commencer par https:// en production
        if settings.is_production and not url.startswith('https://'):
            return False
        
        # Autorise http:// en développement
        if settings.is_development and not url.startswith(('http://', 'https://')):
            return False
        
        # Vérifie la longueur
        if len(url) > 2048:
            return False
        
        return True
    
    @staticmethod
    def validate_public_key(public_key: str) -> bool:
        """Valide une clé publique RSA"""
        try:
            # Tente de charger la clé
            serialization.load_pem_public_key(public_key.encode())
            return True
        except Exception:
            return False
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Nettoie et valide une entrée utilisateur"""
        if not text:
            return ""
        
        # Limite la longueur
        text = text[:max_length]
        
        # Supprime les caractères de contrôle
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        return text.strip()


# Instances globales des services
crypto_service = CryptoService()
jwt_service = JWTService()
security_validator = SecurityValidator()
