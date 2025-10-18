"""
🔐 OpenRed Authentication System
Système d'authentification simple pour sécuriser l'interface OpenRed
"""

import hashlib
import secrets
import time
import json
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

@dataclass
class UserAuth:
    """Informations d'authentification utilisateur"""
    username: str
    password_hash: str
    salt: str
    created_at: float
    last_login: Optional[float] = None
    session_token: Optional[str] = None
    session_expires: Optional[float] = None

class OpenRedAuth:
    """Gestionnaire d'authentification OpenRed"""
    
    def __init__(self, data_dir: str = "./user_data"):
        self.data_dir = data_dir
        self.auth_file = os.path.join(data_dir, "auth.json")
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 24 * 60 * 60  # 24 heures
        
        # Créer le répertoire si nécessaire
        os.makedirs(data_dir, exist_ok=True)
        
        # Charger les données d'auth existantes
        self.user_auth: Optional[UserAuth] = self._load_auth()
    
    def _load_auth(self) -> Optional[UserAuth]:
        """Charge les données d'authentification depuis le fichier"""
        try:
            if os.path.exists(self.auth_file):
                with open(self.auth_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return UserAuth(**data)
        except Exception as e:
            print(f"⚠️ Erreur chargement auth: {e}")
        return None
    
    def _save_auth(self):
        """Sauvegarde les données d'authentification"""
        if self.user_auth:
            try:
                with open(self.auth_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(self.user_auth), f, indent=2)
            except Exception as e:
                print(f"❌ Erreur sauvegarde auth: {e}")
    
    def _hash_password(self, password: str, salt: bytes) -> str:
        """Hash un mot de passe avec PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode('utf-8'))
        return base64.b64encode(key).decode('utf-8')
    
    def create_user(self, username: str, password: str) -> bool:
        """Crée un nouvel utilisateur"""
        if self.user_auth:
            print("⚠️ Utilisateur déjà existant")
            return False
        
        # Générer salt aléatoire
        salt = os.urandom(32)
        password_hash = self._hash_password(password, salt)
        
        self.user_auth = UserAuth(
            username=username,
            password_hash=password_hash,
            salt=base64.b64encode(salt).decode('utf-8'),
            created_at=time.time()
        )
        
        self._save_auth()
        print(f"✅ Utilisateur '{username}' créé avec succès")
        return True
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authentifie un utilisateur et retourne un token de session"""
        if not self.user_auth or self.user_auth.username != username:
            print(f"❌ Utilisateur '{username}' non trouvé")
            return None
        
        # Vérifier le mot de passe
        salt = base64.b64decode(self.user_auth.salt.encode('utf-8'))
        password_hash = self._hash_password(password, salt)
        
        if password_hash != self.user_auth.password_hash:
            print(f"❌ Mot de passe incorrect pour '{username}'")
            return None
        
        # Générer token de session
        session_token = secrets.token_urlsafe(32)
        session_expires = time.time() + self.session_timeout
        
        # Mettre à jour les informations utilisateur
        self.user_auth.last_login = time.time()
        self.user_auth.session_token = session_token
        self.user_auth.session_expires = session_expires
        self._save_auth()
        
        # Enregistrer la session
        self.sessions[session_token] = {
            "username": username,
            "created_at": time.time(),
            "expires_at": session_expires
        }
        
        print(f"✅ Authentification réussie pour '{username}'")
        return session_token
    
    def verify_session(self, session_token: str) -> bool:
        """Vérifie si un token de session est valide"""
        if not session_token:
            return False
        
        # Vérifier en mémoire d'abord
        if session_token in self.sessions:
            session = self.sessions[session_token]
            if time.time() < session["expires_at"]:
                return True
            else:
                # Session expirée
                del self.sessions[session_token]
                return False
        
        # Vérifier avec les données persistantes
        if (self.user_auth and 
            self.user_auth.session_token == session_token and
            self.user_auth.session_expires and
            time.time() < self.user_auth.session_expires):
            
            # Restaurer en mémoire
            self.sessions[session_token] = {
                "username": self.user_auth.username,
                "created_at": self.user_auth.last_login or time.time(),
                "expires_at": self.user_auth.session_expires
            }
            return True
        
        return False
    
    def logout(self, session_token: str) -> bool:
        """Déconnecte une session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
        
        if (self.user_auth and 
            self.user_auth.session_token == session_token):
            self.user_auth.session_token = None
            self.user_auth.session_expires = None
            self._save_auth()
        
        print("✅ Déconnexion réussie")
        return True
    
    def get_username(self, session_token: str) -> Optional[str]:
        """Récupère le nom d'utilisateur depuis un token de session"""
        if self.verify_session(session_token):
            return self.sessions.get(session_token, {}).get("username")
        return None
    
    def has_user(self) -> bool:
        """Vérifie si un utilisateur est configuré"""
        return self.user_auth is not None
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """Change le mot de passe utilisateur"""
        if not self.user_auth:
            return False
        
        # Vérifier l'ancien mot de passe
        salt = base64.b64decode(self.user_auth.salt.encode('utf-8'))
        old_hash = self._hash_password(old_password, salt)
        
        if old_hash != self.user_auth.password_hash:
            print("❌ Ancien mot de passe incorrect")
            return False
        
        # Nouveau hash avec nouveau salt
        new_salt = os.urandom(32)
        new_hash = self._hash_password(new_password, new_salt)
        
        self.user_auth.password_hash = new_hash
        self.user_auth.salt = base64.b64encode(new_salt).decode('utf-8')
        
        # Invalider toutes les sessions existantes
        self.sessions.clear()
        self.user_auth.session_token = None
        self.user_auth.session_expires = None
        
        self._save_auth()
        print("✅ Mot de passe changé avec succès")
        return True
    
    def get_auth_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'authentification"""
        if not self.user_auth:
            return {"configured": False}
        
        return {
            "configured": True,
            "username": self.user_auth.username,
            "created_at": self.user_auth.created_at,
            "last_login": self.user_auth.last_login,
            "active_sessions": len(self.sessions),
            "session_timeout_hours": self.session_timeout / 3600
        }