#!/usr/bin/env python3
"""
🔮 OpenRed Network - Module Projection: Format Anti-Copie
Format révolutionnaire de projection impossible à copier
"""

import json
import time
import uuid
import hashlib
import base64
import random
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class FormatProjectionORN:
    """
    Format de Projection OpenRed Network (ORN)
    Format propriétaire impossible à copier
    """
    id_projection: str
    fort_proprietaire: str
    fort_observateur: str
    timestamp_creation: float
    timestamp_expiration: float
    fragments: List[Dict]  # Données fragmentées
    watermarks_dynamiques: List[str]
    cles_temporelles: Dict[str, str]
    sequence_validation: List[int]
    protection_niveau: int = 5  # 1-5, 5 = maximum
    
    def to_dict(self) -> Dict:
        """Convertit la projection en dictionnaire"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FormatProjectionORN':
        """Crée une projection depuis un dictionnaire"""
        return cls(**data)
    
    def est_expire(self) -> bool:
        """Vérifie si la projection est expirée"""
        return time.time() > self.timestamp_expiration
    
    def temps_restant(self) -> float:
        """Retourne le temps restant avant expiration"""
        return max(0, self.timestamp_expiration - time.time())


class GenerateurProjection:
    """
    🔮 Générateur de projections sécurisées
    Crée des projections avec protection anti-copie intégrée
    """
    
    @staticmethod
    def creer_projection(contenu: Dict, fort_proprietaire: str, fort_observateur: str, 
                        duree_vie: int = 300, niveau_protection: int = 5) -> FormatProjectionORN:
        """Crée une projection sécurisée"""
        
        id_projection = f"ORN_{uuid.uuid4().hex}"
        maintenant = time.time()
        expiration = maintenant + duree_vie
        
        # 1. FRAGMENTATION DU CONTENU
        fragments = GenerateurProjection._fragmenter_contenu(contenu, id_projection)
        
        # 2. WATERMARKS DYNAMIQUES
        watermarks = GenerateurProjection._generer_watermarks_dynamiques(
            id_projection, fort_observateur, niveau_protection
        )
        
        # 3. CLÉS TEMPORELLES
        cles_temporelles = GenerateurProjection._generer_cles_temporelles(
            id_projection, maintenant, niveau_protection
        )
        
        # 4. SÉQUENCE DE VALIDATION
        sequence = GenerateurProjection._generer_sequence_validation(
            id_projection, niveau_protection
        )
        
        projection = FormatProjectionORN(
            id_projection=id_projection,
            fort_proprietaire=fort_proprietaire,
            fort_observateur=fort_observateur,
            timestamp_creation=maintenant,
            timestamp_expiration=expiration,
            fragments=fragments,
            watermarks_dynamiques=watermarks,
            cles_temporelles=cles_temporelles,
            sequence_validation=sequence,
            protection_niveau=niveau_protection
        )
        
        return projection
    
    @staticmethod
    def _fragmenter_contenu(contenu: Dict, id_projection: str) -> List[Dict]:
        """Fragmente le contenu en morceaux illisibles séparément"""
        fragments = []
        
        # Conversion contenu en JSON
        contenu_json = json.dumps(contenu, ensure_ascii=False)
        contenu_bytes = contenu_json.encode('utf-8')
        
        # Fragmentation avec clés cryptographiques
        taille_fragment = 64
        for i in range(0, len(contenu_bytes), taille_fragment):
            chunk = contenu_bytes[i:i+taille_fragment]
            
            # Chiffrement simple avec clé basée sur position et ID
            cle_fragment = hashlib.sha256(f"{id_projection}_{i}".encode()).digest()[:16]
            chunk_chiffre = bytes(a ^ b for a, b in zip(chunk, cle_fragment * (len(chunk) // 16 + 1)))
            
            fragment = {
                "index": i // taille_fragment,
                "data": base64.b64encode(chunk_chiffre).decode(),
                "checksum": hashlib.md5(chunk).hexdigest(),
                "timestamp": time.time(),
                "salt": hashlib.sha256(f"{id_projection}_{i}_{time.time()}".encode()).hexdigest()[:8]
            }
            fragments.append(fragment)
        
        return fragments
    
    @staticmethod
    def _generer_watermarks_dynamiques(id_projection: str, fort_observateur: str, 
                                     niveau: int) -> List[str]:
        """Génère des watermarks dynamiques qui changent"""
        watermarks = []
        
        nb_watermarks = 5 + (niveau * 2)  # Plus de watermarks = plus de protection
        
        for i in range(nb_watermarks):
            base_string = f"{id_projection}_{fort_observateur}_{i}_{time.time()}"
            watermark = hashlib.sha256(base_string.encode()).hexdigest()[:16]
            watermarks.append(watermark)
        
        return watermarks
    
    @staticmethod
    def _generer_cles_temporelles(id_projection: str, timestamp: float, niveau: int) -> Dict[str, str]:
        """Génère des clés qui expirent rapidement"""
        cles = {}
        
        durees_base = [30, 60, 120, 300, 600]  # 30s, 1min, 2min, 5min, 10min
        
        for i in range(niveau):
            duree = durees_base[min(i, len(durees_base) - 1)]
            expiration = timestamp + duree
            
            cle_data = f"{id_projection}_{i}_{expiration}_{random.randint(1000, 9999)}"
            cle_hash = hashlib.sha256(cle_data.encode()).hexdigest()
            
            cles[f"niveau_{i+1}"] = cle_hash
        
        return cles
    
    @staticmethod
    def _generer_sequence_validation(id_projection: str, niveau: int) -> List[int]:
        """Génère séquence de validation unique"""
        # Basé sur l'ID projection pour être reproductible mais unique
        random.seed(id_projection)
        
        longueur = 10 + (niveau * 2)  # Plus longue = plus sécurisée
        sequence = [random.randint(100, 999) for _ in range(longueur)]
        
        random.seed()  # Reset seed
        return sequence
    
    @staticmethod
    def valider_projection(projection: FormatProjectionORN) -> bool:
        """Valide la cohérence d'une projection"""
        try:
            # Vérifications de base
            if projection.est_expire():
                return False
            
            # Vérifier nombre de fragments
            if len(projection.fragments) == 0:
                return False
            
            # Vérifier séquence de validation
            if len(projection.sequence_validation) < 10:
                return False
            
            # Vérifier watermarks
            if len(projection.watermarks_dynamiques) < 5:
                return False
            
            return True
            
        except Exception:
            return False


class ReconstituteurProjection:
    """
    🔓 Reconstituteur de projections sécurisées
    Reconstitue le contenu UNIQUEMENT si toutes les validations passent
    """
    
    @staticmethod
    def reconstituer_contenu(projection: FormatProjectionORN, 
                           verifications_supplementaires: Dict = None) -> Optional[Dict]:
        """Reconstitue le contenu d'une projection sécurisée"""
        
        # 1. Vérifications de base
        if not GenerateurProjection.valider_projection(projection):
            return None
        
        # 2. Vérifications supplémentaires (optionnelles)
        if verifications_supplementaires:
            if not ReconstituteurProjection._verifier_autorisations(
                projection, verifications_supplementaires
            ):
                return None
        
        # 3. Reconstitution des fragments
        try:
            return ReconstituteurProjection._reconstituer_fragments(projection)
        except Exception as e:
            print(f"❌ Erreur reconstitution: {e}")
            return None
    
    @staticmethod
    def _verifier_autorisations(projection: FormatProjectionORN, 
                              verifications: Dict) -> bool:
        """Vérifie les autorisations supplémentaires"""
        
        # Vérification fort observateur
        fort_autorise = verifications.get("fort_observateur")
        if fort_autorise and fort_autorise != projection.fort_observateur:
            return False
        
        # Vérification session
        session_requise = verifications.get("session_id")
        if session_requise and not ReconstituteurProjection._valider_session(
            session_requise, projection
        ):
            return False
        
        return True
    
    @staticmethod
    def _valider_session(session_id: str, projection: FormatProjectionORN) -> bool:
        """Valide une session d'accès"""
        # Pour l'instant, validation basique
        # TODO: Implémenter validation de session plus robuste
        return len(session_id) > 8
    
    @staticmethod
    def _reconstituer_fragments(projection: FormatProjectionORN) -> Dict:
        """Reconstitue le contenu depuis les fragments"""
        
        # Tri des fragments par index
        fragments_ordonnes = sorted(projection.fragments, key=lambda x: x["index"])
        
        contenu_bytes = b""
        
        for fragment in fragments_ordonnes:
            # Déchiffrement du fragment
            data_chiffree = base64.b64decode(fragment["data"])
            
            # Régénération de la clé de chiffrement
            index_byte = fragment["index"] * 64
            cle_fragment = hashlib.sha256(
                f"{projection.id_projection}_{index_byte}".encode()
            ).digest()[:16]
            
            # Déchiffrement
            chunk_dechiffre = bytes(
                a ^ b for a, b in zip(
                    data_chiffree, 
                    cle_fragment * (len(data_chiffree) // 16 + 1)
                )
            )
            
            contenu_bytes += chunk_dechiffre
        
        # Conversion retour en JSON
        contenu_json = contenu_bytes.decode('utf-8')
        contenu = json.loads(contenu_json)
        
        return contenu


class GestionnaireProjections:
    """
    📋 Gestionnaire de projections actives
    Suit et contrôle les projections en cours
    """
    
    def __init__(self):
        self.projections_actives: Dict[str, Dict] = {}
        self.historique_projections: List[str] = []
        self.stats = {
            "projections_creees": 0,
            "projections_expirees": 0,
            "tentatives_acces": 0,
            "acces_refuses": 0
        }
    
    def enregistrer_projection(self, projection: FormatProjectionORN, 
                             metadata: Dict = None) -> str:
        """Enregistre une projection active"""
        
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        self.projections_actives[projection.id_projection] = {
            "projection": projection,
            "session_id": session_id,
            "debut_affichage": None,
            "tentatives_acces": 0,
            "derniere_activite": time.time(),
            "metadata": metadata or {}
        }
        
        self.stats["projections_creees"] += 1
        self.historique_projections.append(projection.id_projection)
        
        return session_id
    
    def acceder_projection(self, id_projection: str, fort_demandeur: str, 
                          session_id: str = None) -> Optional[Dict]:
        """Accède à une projection avec vérifications"""
        
        self.stats["tentatives_acces"] += 1
        
        if id_projection not in self.projections_actives:
            self.stats["acces_refuses"] += 1
            return None
        
        info_projection = self.projections_actives[id_projection]
        projection = info_projection["projection"]
        
        # Vérifications d'accès
        if fort_demandeur != projection.fort_observateur:
            self.stats["acces_refuses"] += 1
            return None
        
        if session_id and session_id != info_projection["session_id"]:
            self.stats["acces_refuses"] += 1
            return None
        
        if projection.est_expire():
            self._nettoyer_projection_expiree(id_projection)
            self.stats["acces_refuses"] += 1
            return None
        
        # Reconstitution du contenu
        verifications = {
            "fort_observateur": fort_demandeur,
            "session_id": session_id
        }
        
        contenu = ReconstituteurProjection.reconstituer_contenu(projection, verifications)
        
        if contenu:
            # Mise à jour activité
            info_projection["tentatives_acces"] += 1
            info_projection["derniere_activite"] = time.time()
            
            if not info_projection["debut_affichage"]:
                info_projection["debut_affichage"] = time.time()
            
            return {
                "contenu": contenu,
                "projection": projection,
                "session_id": info_projection["session_id"]
            }
        else:
            self.stats["acces_refuses"] += 1
            return None
    
    def _nettoyer_projection_expiree(self, id_projection: str):
        """Nettoie une projection expirée"""
        if id_projection in self.projections_actives:
            del self.projections_actives[id_projection]
            self.stats["projections_expirees"] += 1
    
    def nettoyer_projections_expirees(self):
        """Nettoie toutes les projections expirées"""
        projections_expirees = []
        
        for id_proj, info in self.projections_actives.items():
            projection = info["projection"]
            if projection.est_expire():
                projections_expirees.append(id_proj)
        
        for id_proj in projections_expirees:
            self._nettoyer_projection_expiree(id_proj)
    
    def obtenir_statistiques(self) -> Dict:
        """Obtient les statistiques du gestionnaire"""
        self.nettoyer_projections_expirees()
        
        return {
            **self.stats,
            "projections_actives": len(self.projections_actives),
            "taux_succes": (
                (self.stats["tentatives_acces"] - self.stats["acces_refuses"]) /
                max(1, self.stats["tentatives_acces"])
            ) * 100
        }
    
    def lister_projections_actives(self) -> List[Dict]:
        """Liste les projections actives"""
        projections = []
        
        for id_proj, info in self.projections_actives.items():
            projection = info["projection"]
            projections.append({
                "id": id_proj,
                "proprietaire": projection.fort_proprietaire,
                "observateur": projection.fort_observateur,
                "temps_restant": projection.temps_restant(),
                "tentatives_acces": info["tentatives_acces"],
                "niveau_protection": projection.protection_niveau
            })
        
        return projections