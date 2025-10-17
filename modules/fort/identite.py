#!/usr/bin/env python3
"""
🏰 OpenRed Network - Module Fort: Identités
Gestion des identités cryptographiques des forts
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


@dataclass
class IdentiteFort:
    """Identité unique et cryptographique d'un Fort"""
    id_fort: str
    nom: str
    adresse_orp: str  # orp://identifiant.domain
    cle_publique: str
    timestamp_creation: str
    version_protocole: str = "1.0.0"
    
    def to_dict(self) -> Dict:
        """Convertit l'identité en dictionnaire"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'IdentiteFort':
        """Crée une identité depuis un dictionnaire"""
        return cls(**data)
    
    def get_hash_unique(self) -> str:
        """Génère un hash unique basé sur l'identité"""
        data_str = f"{self.id_fort}_{self.cle_publique}_{self.timestamp_creation}"
        return hashlib.sha256(data_str.encode()).hexdigest()


class GenerateurIdentite:
    """
    🔐 Générateur d'identités cryptographiques pour les forts
    """
    
    @staticmethod
    def generer_identite(nom_fort: str) -> IdentiteFort:
        """Génère une nouvelle identité cryptographique"""
        
        # Génération clés RSA
        cle_privee = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        cle_publique = cle_privee.public_key()
        
        # Sérialisation clé publique
        cle_publique_pem = cle_publique.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        # ID fort basé sur hash de la clé publique
        hash_cle = hashlib.sha256(cle_publique_pem.encode()).hexdigest()
        id_fort = f"fort_{hash_cle[:16]}"
        
        # Adresse ORP (OpenRed Protocol)
        adresse_orp = f"orp://{id_fort}.openred"
        
        # Timestamp création
        timestamp = datetime.now().isoformat()
        
        identite = IdentiteFort(
            id_fort=id_fort,
            nom=nom_fort,
            adresse_orp=adresse_orp,
            cle_publique=cle_publique_pem,
            timestamp_creation=timestamp
        )
        
        return identite, cle_privee
    
    @staticmethod
    def valider_identite(identite: IdentiteFort) -> bool:
        """Valide la cohérence d'une identité"""
        try:
            # Vérifier que l'ID correspond à la clé publique
            hash_cle = hashlib.sha256(identite.cle_publique.encode()).hexdigest()
            id_attendu = f"fort_{hash_cle[:16]}"
            
            if identite.id_fort != id_attendu:
                return False
            
            # Vérifier que l'adresse ORP est cohérente
            adresse_attendue = f"orp://{identite.id_fort}.openred"
            if identite.adresse_orp != adresse_attendue:
                return False
            
            # Vérifier que la clé publique est valide
            serialization.load_pem_public_key(identite.cle_publique.encode())
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur validation identité: {e}")
            return False


class RegistreIdentites:
    """
    📋 Registre local des identités connues
    """
    
    def __init__(self):
        self.identites: Dict[str, IdentiteFort] = {}
        self.cles_privees: Dict[str, any] = {}  # Stockage local des clés privées
    
    def ajouter_identite(self, identite: IdentiteFort, cle_privee=None):
        """Ajoute une identité au registre"""
        if GenerateurIdentite.valider_identite(identite):
            self.identites[identite.id_fort] = identite
            if cle_privee:
                self.cles_privees[identite.id_fort] = cle_privee
            print(f"✅ Identité ajoutée: {identite.nom} ({identite.id_fort})")
        else:
            print(f"❌ Identité invalide: {identite.nom}")
    
    def obtenir_identite(self, id_fort: str) -> Optional[IdentiteFort]:
        """Récupère une identité par son ID"""
        return self.identites.get(id_fort)
    
    def obtenir_cle_privee(self, id_fort: str):
        """Récupère la clé privée associée (si disponible)"""
        return self.cles_privees.get(id_fort)
    
    def lister_identites(self) -> Dict[str, str]:
        """Liste toutes les identités (ID -> Nom)"""
        return {id_fort: identite.nom for id_fort, identite in self.identites.items()}
    
    def sauvegarder(self, fichier: str):
        """Sauvegarde les identités publiques (sans clés privées)"""
        data = {
            "identites": {id_fort: identite.to_dict() 
                         for id_fort, identite in self.identites.items()}
        }
        
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def charger(self, fichier: str):
        """Charge les identités depuis un fichier"""
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for id_fort, identite_data in data.get("identites", {}).items():
                identite = IdentiteFort.from_dict(identite_data)
                self.ajouter_identite(identite)
                
        except FileNotFoundError:
            print(f"📁 Fichier {fichier} non trouvé, registre vide")
        except Exception as e:
            print(f"❌ Erreur chargement registre: {e}")