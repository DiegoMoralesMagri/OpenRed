# FR: Fichier: security.py — Fonctions de sécurité (auth, hashing)
# EN: File: security.py — Security functions (auth, hashing)
# ES: Archivo: security.py — Funciones de seguridad (auth, hashing)
# ZH: 文件: security.py — 安全功能（认证，哈希）

# Sécurité et authentification O-Red

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import base64
import hashlib
from jose import JWTError, jwt as jose_jwt

from .config import settings

# Contexte de hachage pour les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ORedSecurity:
    """Gestionnaire de sécurité pour O-Red"""
    
    def __init__(self):
        self.algorithm = settings.ALGORITHM
        self.secret_key = settings.SECRET_KEY
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token d'accès JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": settings.ORED_ID_ISSUER,
            "type": "access_token"
        })
        
        encoded_jwt = jose_jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """Crée un token de rafraîchissement"""
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": settings.ORED_ID_ISSUER,
            "type": "refresh_token"
        }
        
        encoded_jwt = jose_jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jose_jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                issuer=settings.ORED_ID_ISSUER
            )
            return payload
        except JWTError:
            return None
    
    def hash_password(self, password: str) -> str:
        """Hache un mot de passe"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe"""
        return pwd_context.verify(plain_password, hashed_password)

class ORedID:
    """Système d'identité décentralisée O-RedID"""
    
    def __init__(self):
        self.key_size = settings.ORED_ID_KEY_SIZE
        self.curve = settings.ORED_ID_CURVE
    
    def generate_keypair(self) -> Dict[str, bytes]:
        """Génère une paire de clés Ed25519 pour O-RedID"""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Sérialisation des clés
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            "private_key": private_pem,
            "public_key": public_pem
        }
    
    def create_identity(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une identité O-RedID"""
        keypair = self.generate_keypair()
        
        # Génération de l'ID unique
        identity_hash = hashlib.sha256(keypair["public_key"]).hexdigest()
        ored_id = f"ored:{identity_hash[:32]}"
        
        # Métadonnées d'identité
        identity = {
            "ored_id": ored_id,
            "public_key": base64.b64encode(keypair["public_key"]).decode(),
            "created_at": datetime.utcnow().isoformat(),
            "issuer": settings.ORED_ID_ISSUER,
            "version": "1.0",
            "user_data": user_data  # Données chiffrées côté client
        }
        
        return {
            "identity": identity,
            "private_key": base64.b64encode(keypair["private_key"]).decode()
        }
    
    def verify_identity(self, identity_data: Dict[str, Any], signature: str) -> bool:
        """Vérifie une identité O-RedID"""
        try:
            # Reconstitution de la clé publique
            public_key_bytes = base64.b64decode(identity_data["public_key"])
            public_key = serialization.load_pem_public_key(public_key_bytes)
            
            # Vérification de la signature
            signature_bytes = base64.b64decode(signature)
            message = str(identity_data).encode()
            
            public_key.verify(signature_bytes, message)
            return True
        except Exception:
            return False

class PostQuantumCrypto:
    """Cryptographie post-quantique pour O-Red"""
    
    def __init__(self):
        self.signature_alg = settings.PQ_SIGNATURE_ALGORITHM
        self.kem_alg = settings.PQ_KEM_ALGORITHM
        # Note: Implémentation avec liboqs en production
    
    def generate_pq_keypair(self) -> Dict[str, bytes]:
        """Génère une paire de clés post-quantique"""
        # Simulation - remplacer par liboqs en production
        private_key = secrets.token_bytes(32)
        public_key = hashlib.sha256(private_key).digest()
        
        return {
            "private_key": private_key,
            "public_key": public_key
        }
    
    def pq_sign(self, message: bytes, private_key: bytes) -> bytes:
        """Signature post-quantique"""
        # Simulation - remplacer par Dilithium en production
        return hashlib.sha256(message + private_key).digest()
    
    def pq_verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Vérification de signature post-quantique"""
        # Simulation - remplacer par Dilithium en production
        return True  # Logique de vérification simplifiée

class RateLimiter:
    """Limiteur de débit pour l'API"""
    
    def __init__(self):
        self.requests = {}
        self.window = settings.RATE_LIMIT_WINDOW
        self.max_requests = settings.RATE_LIMIT_REQUESTS
    
    def is_allowed(self, identifier: str) -> bool:
        """Vérifie si une requête est autorisée"""
        now = datetime.utcnow()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Nettoyage des anciennes requêtes
        cutoff = now - timedelta(seconds=self.window)
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] 
            if req_time > cutoff
        ]
        
        # Vérification du limite
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Ajout de la nouvelle requête
        self.requests[identifier].append(now)
        return True

# Instances globales
security = ORedSecurity()
ored_id = ORedID()
pq_crypto = PostQuantumCrypto()
rate_limiter = RateLimiter()

# Fonctions utilitaires d'authentification
async def verify_ored_token(token: str) -> Optional[Dict[str, Any]]:
    """Vérifie un token O-Red"""
    return security.verify_token(token)

async def create_ored_token(user_data: Dict[str, Any]) -> str:
    """Crée un token O-Red"""
    return security.create_access_token(user_data)

def generate_secure_random(length: int = 32) -> str:
    """Génère une chaîne aléatoire sécurisée"""
    return secrets.token_urlsafe(length)

def hash_data(data: str) -> str:
    """Hache des données avec SHA-256"""
    return hashlib.sha256(data.encode()).hexdigest()