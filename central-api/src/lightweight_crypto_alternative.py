# === Alternative ULTRA-LÉGÈRE pour O-RedSearch ===
# Sans dépendances externes, crypto natif Python

import hashlib
import secrets
import hmac
import base64
import time
from typing import Dict, Any

class LightweightCrypto:
    """Cryptographie légère sans dépendances externes"""
    
    @staticmethod
    def generate_key_from_passphrase(passphrase: str, salt: bytes = None) -> bytes:
        """Génère clé 256-bit depuis passphrase avec PBKDF2 natif"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # PBKDF2 avec hashlib natif (100k iterations)
        key = hashlib.pbkdf2_hmac('sha256', passphrase.encode(), salt, 100000)
        return salt + key  # 64 bytes total
    
    @staticmethod  
    def symmetric_encrypt(data: str, key: bytes) -> str:
        """Chiffrement symétrique avec XOR + HMAC"""
        # Extraire salt et clé
        salt = key[:32]
        enc_key = key[32:]
        
        # Générer nonce
        nonce = secrets.token_bytes(16)
        
        # XOR stream cipher
        data_bytes = data.encode()
        stream = hashlib.sha256(enc_key + nonce).digest()
        
        encrypted = bytes(a ^ b for a, b in zip(data_bytes, stream[:len(data_bytes)]))
        
        # HMAC pour authentification
        mac = hmac.new(enc_key, salt + nonce + encrypted, hashlib.sha256).digest()
        
        # Format: salt(32) + nonce(16) + mac(32) + data(N)
        result = salt + nonce + mac + encrypted
        return base64.b64encode(result).decode()
    
    @staticmethod
    def generate_simple_token(node_id: str, lifetime_seconds: int = 300) -> Dict[str, Any]:
        """Token simplifié sans RSA"""
        token_id = secrets.token_urlsafe(32)
        timestamp = int(time.time())
        expiry = timestamp + lifetime_seconds
        
        # Hash mathématique simple
        combined = f"{token_id}:{node_id}:{timestamp}"
        signature = hashlib.sha256(combined.encode()).hexdigest()
        
        return {
            "token_id": token_id,
            "node_id": node_id, 
            "created_at": timestamp,
            "expires_at": expiry,
            "signature": signature
        }

# Usage: 0 dépendances externes, ~50 lignes, compatible partout