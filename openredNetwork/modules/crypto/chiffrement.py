#!/usr/bin/env python3
"""
🔐 OpenRed Network - Module Crypto: Chiffrement
Système de chiffrement et signatures pour OpenRed Network
"""

import hashlib
import base64
import secrets
from typing import Tuple, Optional, Dict, Any
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json


class ChiffrementRSA:
    """
    🔐 Chiffrement RSA pour OpenRed Network
    Gère les clés RSA et le chiffrement asymétrique
    """
    
    @staticmethod
    def generer_paire_cles(taille_cle: int = 2048) -> Tuple[any, any]:
        """Génère une paire de clés RSA"""
        cle_privee = rsa.generate_private_key(
            public_exponent=65537,
            key_size=taille_cle
        )
        cle_publique = cle_privee.public_key()
        
        return cle_privee, cle_publique
    
    @staticmethod
    def serialiser_cle_publique(cle_publique) -> str:
        """Sérialise une clé publique en PEM"""
        pem_bytes = cle_publique.public_key_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem_bytes.decode('utf-8')
    
    @staticmethod
    def serialiser_cle_privee(cle_privee, mot_de_passe: Optional[str] = None) -> str:
        """Sérialise une clé privée en PEM (optionnellement chiffrée)"""
        encryption_algorithm = serialization.NoEncryption()
        
        if mot_de_passe:
            encryption_algorithm = serialization.BestAvailableEncryption(
                mot_de_passe.encode('utf-8')
            )
        
        pem_bytes = cle_privee.private_key_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        return pem_bytes.decode('utf-8')
    
    @staticmethod
    def charger_cle_publique(pem_str: str):
        """Charge une clé publique depuis PEM"""
        return serialization.load_pem_public_key(pem_str.encode('utf-8'))
    
    @staticmethod
    def charger_cle_privee(pem_str: str, mot_de_passe: Optional[str] = None):
        """Charge une clé privée depuis PEM"""
        password_bytes = mot_de_passe.encode('utf-8') if mot_de_passe else None
        return serialization.load_pem_private_key(pem_str.encode('utf-8'), password_bytes)
    
    @staticmethod
    def chiffrer(message: bytes, cle_publique) -> bytes:
        """Chiffre un message avec une clé publique RSA"""
        return cle_publique.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    @staticmethod
    def dechiffrer(message_chiffre: bytes, cle_privee) -> bytes:
        """Déchiffre un message avec une clé privée RSA"""
        return cle_privee.decrypt(
            message_chiffre,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    @staticmethod
    def signer(message: bytes, cle_privee) -> bytes:
        """Signe un message avec une clé privée RSA"""
        return cle_privee.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    
    @staticmethod
    def verifier_signature(message: bytes, signature: bytes, cle_publique) -> bool:
        """Vérifie une signature avec une clé publique RSA"""
        try:
            cle_publique.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False


class ChiffrementAES:
    """
    🔒 Chiffrement AES pour OpenRed Network
    Chiffrement symétrique pour les données volumineuses
    """
    
    @staticmethod
    def generer_cle(taille: int = 256) -> bytes:
        """Génère une clé AES aléatoire"""
        return secrets.token_bytes(taille // 8)
    
    @staticmethod
    def generer_iv() -> bytes:
        """Génère un vecteur d'initialisation aléatoire"""
        return secrets.token_bytes(16)  # 128 bits pour AES
    
    @staticmethod
    def chiffrer(message: bytes, cle: bytes) -> Tuple[bytes, bytes]:
        """Chiffre un message avec AES-GCM"""
        iv = ChiffrementAES.generer_iv()
        
        cipher = Cipher(
            algorithms.AES(cle),
            modes.GCM(iv)
        )
        
        encryptor = cipher.encryptor()
        message_chiffre = encryptor.update(message) + encryptor.finalize()
        
        # Concaténation IV + tag + message chiffré
        return iv + encryptor.tag + message_chiffre, iv
    
    @staticmethod
    def dechiffrer(message_chiffre: bytes, cle: bytes) -> bytes:
        """Déchiffre un message AES-GCM"""
        # Extraction IV (16 bytes) + tag (16 bytes) + message
        iv = message_chiffre[:16]
        tag = message_chiffre[16:32]
        message_crypte = message_chiffre[32:]
        
        cipher = Cipher(
            algorithms.AES(cle),
            modes.GCM(iv, tag)
        )
        
        decryptor = cipher.decryptor()
        return decryptor.update(message_crypte) + decryptor.finalize()
    
    @staticmethod
    def deriver_cle_depuis_mot_de_passe(mot_de_passe: str, sel: bytes = None) -> Tuple[bytes, bytes]:
        """Dérive une clé AES depuis un mot de passe"""
        if sel is None:
            sel = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=sel,
            iterations=100000
        )
        
        cle = kdf.derive(mot_de_passe.encode('utf-8'))
        return cle, sel


class GestionnaireSignatures:
    """
    ✍️ Gestionnaire de signatures numériques
    Gère la signature et vérification des messages ORN
    """
    
    def __init__(self, cle_privee=None, cle_publique=None):
        self.cle_privee = cle_privee
        self.cle_publique = cle_publique
        self.signatures_cache = {}  # Cache des signatures récentes
    
    def definir_cles(self, cle_privee, cle_publique=None):
        """Définit les clés de signature"""
        self.cle_privee = cle_privee
        if cle_publique:
            self.cle_publique = cle_publique
        else:
            self.cle_publique = cle_privee.public_key() if cle_privee else None
    
    def signer_message(self, message_dict: Dict) -> str:
        """Signe un message ORN"""
        if not self.cle_privee:
            raise ValueError("Clé privée non définie")
        
        # Préparation des données à signer
        donnees_signature = {
            "type_message": message_dict.get("type_message"),
            "expediteur": message_dict.get("expediteur"),
            "destinataire": message_dict.get("destinataire"),
            "timestamp": message_dict.get("timestamp"),
            "data": message_dict.get("data")
        }
        
        # Sérialisation canonique
        donnees_json = json.dumps(donnees_signature, sort_keys=True, ensure_ascii=False)
        donnees_bytes = donnees_json.encode('utf-8')
        
        # Signature
        signature_bytes = ChiffrementRSA.signer(donnees_bytes, self.cle_privee)
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
        
        # Cache de la signature
        message_id = message_dict.get("id_message")
        if message_id:
            self.signatures_cache[message_id] = signature_b64
        
        return signature_b64
    
    def verifier_signature(self, message_dict: Dict, signature: str, 
                          cle_publique_expediteur=None) -> bool:
        """Vérifie la signature d'un message ORN"""
        
        cle_verification = cle_publique_expediteur or self.cle_publique
        if not cle_verification:
            return False
        
        try:
            # Préparation des données à vérifier
            donnees_signature = {
                "type_message": message_dict.get("type_message"),
                "expediteur": message_dict.get("expediteur"),
                "destinataire": message_dict.get("destinataire"),
                "timestamp": message_dict.get("timestamp"),
                "data": message_dict.get("data")
            }
            
            # Sérialisation canonique
            donnees_json = json.dumps(donnees_signature, sort_keys=True, ensure_ascii=False)
            donnees_bytes = donnees_json.encode('utf-8')
            
            # Décodage signature
            signature_bytes = base64.b64decode(signature)
            
            # Vérification
            return ChiffrementRSA.verifier_signature(
                donnees_bytes, signature_bytes, cle_verification
            )
            
        except Exception as e:
            print(f"❌ Erreur vérification signature: {e}")
            return False
    
    def obtenir_signature_cache(self, message_id: str) -> Optional[str]:
        """Récupère une signature du cache"""
        return self.signatures_cache.get(message_id)
    
    def nettoyer_cache_signatures(self, age_max: int = 3600):
        """Nettoie le cache des signatures anciennes"""
        # Pour l'instant, simple vidage du cache
        # TODO: Implémenter nettoyage basé sur l'âge
        if len(self.signatures_cache) > 1000:
            self.signatures_cache.clear()


class HasheurSecurise:
    """
    🔒 Hasheur sécurisé pour OpenRed Network
    Génère des hash sécurisés pour l'intégrité des données
    """
    
    @staticmethod
    def sha256(data: bytes) -> str:
        """Calcule un hash SHA-256"""
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def sha256_str(texte: str) -> str:
        """Calcule un hash SHA-256 d'une chaîne"""
        return HasheurSecurise.sha256(texte.encode('utf-8'))
    
    @staticmethod
    def sha512(data: bytes) -> str:
        """Calcule un hash SHA-512"""
        return hashlib.sha512(data).hexdigest()
    
    @staticmethod
    def blake2b(data: bytes, taille: int = 64) -> str:
        """Calcule un hash BLAKE2b"""
        return hashlib.blake2b(data, digest_size=taille).hexdigest()
    
    @staticmethod
    def hash_fichier(chemin_fichier: str, algorithme: str = "sha256") -> str:
        """Calcule le hash d'un fichier"""
        hash_obj = hashlib.new(algorithme)
        
        with open(chemin_fichier, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def verifier_integrite(data: bytes, hash_attendu: str, 
                          algorithme: str = "sha256") -> bool:
        """Vérifie l'intégrité des données"""
        if algorithme == "sha256":
            hash_calcule = HasheurSecurise.sha256(data)
        elif algorithme == "sha512":
            hash_calcule = HasheurSecurise.sha512(data)
        elif algorithme.startswith("blake2b"):
            taille = int(algorithme.split("-")[1]) if "-" in algorithme else 64
            hash_calcule = HasheurSecurise.blake2b(data, taille)
        else:
            return False
        
        return hash_calcule.lower() == hash_attendu.lower()


class GenerateurSecurise:
    """
    🎲 Générateur sécurisé pour OpenRed Network
    Génère des valeurs cryptographiquement sécurisées
    """
    
    @staticmethod
    def generer_token(longueur: int = 32) -> str:
        """Génère un token aléatoire sécurisé"""
        return secrets.token_hex(longueur)
    
    @staticmethod
    def generer_uuid_securise() -> str:
        """Génère un UUID cryptographiquement sécurisé"""
        return secrets.token_hex(16)
    
    @staticmethod
    def generer_salt(longueur: int = 32) -> bytes:
        """Génère un sel cryptographique"""
        return secrets.token_bytes(longueur)
    
    @staticmethod
    def generer_mot_de_passe(longueur: int = 16, 
                           inclure_symboles: bool = True) -> str:
        """Génère un mot de passe sécurisé"""
        import string
        
        caracteres = string.ascii_letters + string.digits
        if inclure_symboles:
            caracteres += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        return ''.join(secrets.choice(caracteres) for _ in range(longueur))
    
    @staticmethod
    def generer_nombre_securise(min_val: int, max_val: int) -> int:
        """Génère un nombre entier cryptographiquement sécurisé"""
        return secrets.randbelow(max_val - min_val + 1) + min_val