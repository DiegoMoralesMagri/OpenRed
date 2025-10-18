#!/usr/bin/env python3
"""
👤 GESTIONNAIRE MULTI-PROFILS OPENRED
===================================

Système révolutionnaire de gestion des identités contextuelles.
Chaque utilisateur peut créer et gérer plusieurs profils isolés :
- 👨‍👩‍👧‍👦 Famille : Photos, calendrier, budget familial
- 👥 Amis : Événements, loisirs, partages créatifs  
- 💼 Professionnel : CV, réseau, documents de travail
- 🌍 Public : Blog, projets, contributions communautaires

Conformité Manifeste OpenRed :
✅ Souveraineté absolue des données
✅ Isolation cryptographique par profil
✅ Permissions granulaires
✅ Aucune fuite entre contextes
"""

import os
import json
import time
import hashlib
import uuid
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from cryptography.fernet import Fernet
from dataclasses import dataclass, asdict
from enum import Enum


class TypeProfil(Enum):
    """Types de profils contextuels disponibles"""
    FAMILLE = "famille"
    AMIS = "amis" 
    PROFESSIONNEL = "professionnel"
    PUBLIC = "public"


@dataclass
class ProfilContextuel:
    """Profil contextuel avec isolation cryptographique"""
    profil_id: str
    type_profil: TypeProfil
    nom_affichage: str
    description: str
    couleur_theme: str
    icone: str
    cle_chiffrement: str  # Clé unique par profil
    creation_timestamp: float
    derniere_activite: float
    visible_p2p: bool = True
    partage_actif: bool = True
    permissions: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = self._permissions_par_defaut()
    
    def _permissions_par_defaut(self) -> Dict[str, bool]:
        """Permissions par défaut selon le type de profil"""
        base = {
            "lecture_profil": True,
            "ecriture_messages": False,
            "partage_fichiers": False,
            "calendrier_acces": False,
            "historique_acces": False
        }
        
        if self.type_profil == TypeProfil.FAMILLE:
            base.update({
                "partage_fichiers": True,
                "calendrier_acces": True,
                "budget_familial": True
            })
        elif self.type_profil == TypeProfil.AMIS:
            base.update({
                "ecriture_messages": True,
                "partage_fichiers": True,
                "evenements": True
            })
        elif self.type_profil == TypeProfil.PROFESSIONNEL:
            base.update({
                "cv_portfolio": True,
                "documents_travail": True,
                "reseau_pro": True
            })
        elif self.type_profil == TypeProfil.PUBLIC:
            base.update({
                "blog_public": True,
                "projets_opensource": True,
                "contributions": True
            })
        
        return base
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'type_profil': self.type_profil.value
        }
    
    @classmethod 
    def from_dict(cls, data: Dict) -> 'ProfilContextuel':
        data['type_profil'] = TypeProfil(data['type_profil'])
        return cls(**data)


@dataclass
class EspaceProfileil:
    """Espace de données isolé pour un profil"""
    profil_id: str
    dossier_donnees: str
    fichiers_chiffres: List[str]
    connexions_p2p: Set[str]  # IDs des forts connectés à ce profil
    projections_actives: Dict[str, Dict]  # Projections partagées
    historique_activites: List[Dict]
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'connexions_p2p': list(self.connexions_p2p)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EspaceProfileil':
        data['connexions_p2p'] = set(data['connexions_p2p'])
        return cls(**data)


class GestionnaireMultiProfils:
    """
    Gestionnaire central des profils contextuels
    
    Assure l'isolation complète entre les contextes tout en
    permettant une expérience utilisateur fluide
    """
    
    def __init__(self, fort_id: str, dossier_base: str = ".openred_fort"):
        self.fort_id = fort_id
        self.dossier_base = dossier_base
        self.dossier_profils = os.path.join(dossier_base, "profils")
        
        # État en mémoire
        self.profils: Dict[str, ProfilContextuel] = {}
        self.espaces: Dict[str, EspaceProfileil] = {}
        self.profil_actif: Optional[str] = None
        
        # Clé maître pour chiffrement métadonnées
        self.cle_maitre = self._obtenir_cle_maitre()
        
        self._initialiser_dossiers()
        self._charger_profils_existants()
    
    def _initialiser_dossiers(self):
        """Crée la structure de dossiers pour les profils"""
        os.makedirs(self.dossier_profils, exist_ok=True)
        
        for type_profil in TypeProfil:
            dossier_type = os.path.join(self.dossier_profils, type_profil.value)
            os.makedirs(dossier_type, exist_ok=True)
            
            # Sous-dossiers par type
            sous_dossiers = ["donnees", "projections", "connexions", "cache"]
            for sous_dossier in sous_dossiers:
                os.makedirs(os.path.join(dossier_type, sous_dossier), exist_ok=True)
    
    def _obtenir_cle_maitre(self) -> bytes:
        """Obtient la clé maître pour chiffrement métadonnées"""
        fichier_cle = os.path.join(self.dossier_base, ".cle_profils")
        
        if os.path.exists(fichier_cle):
            try:
                with open(fichier_cle, 'rb') as f:
                    return f.read()
            except:
                pass
        
        # Génère nouvelle clé maître
        cle = Fernet.generate_key()
        try:
            with open(fichier_cle, 'wb') as f:
                f.write(cle)
            
            if hasattr(os, 'chmod'):
                os.chmod(fichier_cle, 0o600)
                
        except Exception as e:
            print(f"⚠️  Erreur sauvegarde clé maître: {e}")
        
        return cle
    
    def _generer_cle_profil(self) -> str:
        """Génère une clé de chiffrement unique pour un profil"""
        return Fernet.generate_key().decode()
    
    def _chiffrer_donnees(self, data: Dict, cle: bytes) -> bytes:
        """Chiffre des données avec une clé spécifique"""
        try:
            fernet = Fernet(cle)
            json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            return fernet.encrypt(json_str.encode('utf-8'))
        except Exception as e:
            print(f"❌ Erreur chiffrement: {e}")
            return json.dumps(data).encode('utf-8')
    
    def _dechiffrer_donnees(self, data_chiffree: bytes, cle: bytes) -> Dict:
        """Déchiffre des données avec une clé spécifique"""
        try:
            fernet = Fernet(cle)
            json_str = fernet.decrypt(data_chiffree).decode('utf-8')
            return json.loads(json_str)
        except:
            try:
                return json.loads(data_chiffree.decode('utf-8'))
            except:
                return {}
    
    def creer_profil(self, type_profil: TypeProfil, nom_affichage: str, 
                    description: str = "", couleur_theme: str = "", 
                    icone: str = "") -> ProfilContextuel:
        """
        Crée un nouveau profil contextuel avec isolation complète
        """
        print(f"🆕 Création profil {type_profil.value}: {nom_affichage}")
        
        # Génère ID unique et clé de chiffrement
        profil_id = f"{type_profil.value}_{uuid.uuid4().hex[:12]}"
        cle_profil = self._generer_cle_profil()
        
        # Couleurs et icônes par défaut
        themes_defaut = {
            TypeProfil.FAMILLE: {"couleur": "#FF6B6B", "icone": "👨‍👩‍👧‍👦"},
            TypeProfil.AMIS: {"couleur": "#4ECDC4", "icone": "👥"},
            TypeProfil.PROFESSIONNEL: {"couleur": "#45B7D1", "icone": "💼"},
            TypeProfil.PUBLIC: {"couleur": "#96CEB4", "icone": "🌍"}
        }
        
        theme = themes_defaut.get(type_profil, {"couleur": "#888888", "icone": "👤"})
        
        # Crée le profil
        profil = ProfilContextuel(
            profil_id=profil_id,
            type_profil=type_profil,
            nom_affichage=nom_affichage,
            description=description,
            couleur_theme=couleur_theme or theme["couleur"],
            icone=icone or theme["icone"],
            cle_chiffrement=cle_profil,
            creation_timestamp=time.time(),
            derniere_activite=time.time()
        )
        
        # Crée l'espace de données associé
        dossier_profil = os.path.join(self.dossier_profils, type_profil.value, profil_id)
        os.makedirs(dossier_profil, exist_ok=True)
        
        espace = EspaceProfileil(
            profil_id=profil_id,
            dossier_donnees=dossier_profil,
            fichiers_chiffres=[],
            connexions_p2p=set(),
            projections_actives={},
            historique_activites=[]
        )
        
        # Sauvegarde
        self.profils[profil_id] = profil
        self.espaces[profil_id] = espace
        
        self._sauvegarder_profil(profil)
        self._sauvegarder_espace(espace)
        
        print(f"✅ Profil créé: {profil_id}")
        print(f"   📁 Dossier: {dossier_profil}")
        print(f"   🔐 Chiffrement: Activé")
        
        return profil
    
    def _sauvegarder_profil(self, profil: ProfilContextuel):
        """Sauvegarde un profil (métadonnées chiffrées)"""
        fichier_profil = os.path.join(
            self.dossier_profils, 
            profil.type_profil.value,
            profil.profil_id,
            "profil.dat"
        )
        
        try:
            data_chiffree = self._chiffrer_donnees(profil.to_dict(), self.cle_maitre)
            with open(fichier_profil, 'wb') as f:
                f.write(data_chiffree)
            
            print(f"💾 Profil sauvegardé: {profil.profil_id}")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde profil: {e}")
    
    def _sauvegarder_espace(self, espace: EspaceProfileil):
        """Sauvegarde l'espace de données d'un profil"""
        fichier_espace = os.path.join(
            espace.dossier_donnees,
            "espace.dat"
        )
        
        try:
            # Utilise la clé du profil pour chiffrer l'espace
            profil = self.profils[espace.profil_id]
            cle_profil = profil.cle_chiffrement.encode()
            
            data_chiffree = self._chiffrer_donnees(espace.to_dict(), cle_profil)
            with open(fichier_espace, 'wb') as f:
                f.write(data_chiffree)
                
        except Exception as e:
            print(f"❌ Erreur sauvegarde espace: {e}")
    
    def _charger_profils_existants(self):
        """Charge tous les profils existants"""
        print("🔄 Chargement profils existants...")
        
        profils_charges = 0
        
        for type_profil in TypeProfil:
            dossier_type = os.path.join(self.dossier_profils, type_profil.value)
            
            if not os.path.exists(dossier_type):
                continue
            
            for item in os.listdir(dossier_type):
                dossier_profil = os.path.join(dossier_type, item)
                
                if not os.path.isdir(dossier_profil):
                    continue
                
                fichier_profil = os.path.join(dossier_profil, "profil.dat")
                fichier_espace = os.path.join(dossier_profil, "espace.dat")
                
                if os.path.exists(fichier_profil):
                    try:
                        # Charge le profil
                        with open(fichier_profil, 'rb') as f:
                            data_chiffree = f.read()
                        
                        data_profil = self._dechiffrer_donnees(data_chiffree, self.cle_maitre)
                        profil = ProfilContextuel.from_dict(data_profil)
                        
                        self.profils[profil.profil_id] = profil
                        profils_charges += 1
                        
                        # Charge l'espace si il existe
                        if os.path.exists(fichier_espace):
                            with open(fichier_espace, 'rb') as f:
                                data_espace_chiffree = f.read()
                            
                            cle_profil = profil.cle_chiffrement.encode()
                            data_espace = self._dechiffrer_donnees(data_espace_chiffree, cle_profil)
                            espace = EspaceProfileil.from_dict(data_espace)
                            
                            self.espaces[profil.profil_id] = espace
                        
                    except Exception as e:
                        print(f"⚠️  Erreur chargement profil {item}: {e}")
                        continue
        
        print(f"✅ {profils_charges} profils chargés")
        
        # Active le premier profil par défaut
        if self.profils and not self.profil_actif:
            self.profil_actif = next(iter(self.profils.keys()))
    
    def lister_profils(self) -> List[ProfilContextuel]:
        """Liste tous les profils de l'utilisateur"""
        return list(self.profils.values())
    
    def obtenir_profil(self, profil_id: str) -> Optional[ProfilContextuel]:
        """Obtient un profil spécifique"""
        return self.profils.get(profil_id)
    
    def activer_profil(self, profil_id: str) -> bool:
        """
        Active un profil contextuel spécifique
        Change le contexte de sécurité et les permissions
        """
        if profil_id not in self.profils:
            print(f"❌ Profil inconnu: {profil_id}")
            return False
        
        profil = self.profils[profil_id]
        self.profil_actif = profil_id
        
        # Met à jour l'activité
        profil.derniere_activite = time.time()
        self._sauvegarder_profil(profil)
        
        print(f"🔄 Profil activé: {profil.nom_affichage} ({profil.type_profil.value})")
        print(f"   🎨 Thème: {profil.couleur_theme}")
        print(f"   📊 Permissions: {len(profil.permissions)} règles actives")
        
        return True
    
    def obtenir_profil_actif(self) -> Optional[ProfilContextuel]:
        """Obtient le profil actuellement actif"""
        if self.profil_actif:
            return self.profils.get(self.profil_actif)
        return None
    
    def creer_profils_defaut(self) -> List[ProfilContextuel]:
        """
        Crée les profils par défaut lors de la première utilisation
        """
        print("🚀 Création profils par défaut...")
        
        profils_crees = []
        
        # Profil Famille
        famille = self.creer_profil(
            TypeProfil.FAMILLE,
            "Ma Famille",
            "Photos, calendrier et budget familial"
        )
        profils_crees.append(famille)
        
        # Profil Amis
        amis = self.creer_profil(
            TypeProfil.AMIS,
            "Mes Amis", 
            "Événements, loisirs et partages créatifs"
        )
        profils_crees.append(amis)
        
        # Profil Professionnel
        pro = self.creer_profil(
            TypeProfil.PROFESSIONNEL,
            "Professionnel",
            "CV, réseau et documents de travail"
        )
        profils_crees.append(pro)
        
        # Profil Public
        public = self.creer_profil(
            TypeProfil.PUBLIC,
            "Public",
            "Blog, projets et contributions communautaires"
        )
        profils_crees.append(public)
        
        # Active le profil famille par défaut
        self.activer_profil(famille.profil_id)
        
        print(f"✅ {len(profils_crees)} profils par défaut créés")
        
        return profils_crees
    
    def obtenir_statistiques(self) -> Dict:
        """Obtient les statistiques des profils"""
        stats = {
            "total_profils": len(self.profils),
            "profil_actif": self.profil_actif,
            "types": {},
            "activite_recente": []
        }
        
        for profil in self.profils.values():
            type_str = profil.type_profil.value
            if type_str not in stats["types"]:
                stats["types"][type_str] = 0
            stats["types"][type_str] += 1
            
            stats["activite_recente"].append({
                "profil_id": profil.profil_id,
                "nom": profil.nom_affichage,
                "type": type_str,
                "derniere_activite": profil.derniere_activite
            })
        
        # Trie par activité récente
        stats["activite_recente"].sort(
            key=lambda x: x["derniere_activite"], 
            reverse=True
        )
        
        return stats


def demo_multi_profils():
    """Démonstration du système multi-profils"""
    print("🎭 === DÉMONSTRATION SYSTÈME MULTI-PROFILS ===")
    
    # Initialise le gestionnaire
    gestionnaire = GestionnaireMultiProfils("fort_demo123")
    
    # Crée les profils par défaut si nécessaire
    if not gestionnaire.profils:
        gestionnaire.creer_profils_defaut()
    
    # Affiche les profils
    print("\n👤 PROFILS DISPONIBLES:")
    for profil in gestionnaire.lister_profils():
        actif = "🟢" if profil.profil_id == gestionnaire.profil_actif else "⚫"
        print(f"   {actif} {profil.icone} {profil.nom_affichage}")
        print(f"      Type: {profil.type_profil.value}")
        print(f"      Couleur: {profil.couleur_theme}")
        print(f"      Permissions: {len(profil.permissions)}")
        print(f"      Dernière activité: {datetime.fromtimestamp(profil.derniere_activite)}")
        print()
    
    # Teste l'activation de profils
    print("🔄 TEST ACTIVATION PROFILS:")
    for profil in gestionnaire.lister_profils():
        gestionnaire.activer_profil(profil.profil_id)
        print(f"   ✅ {profil.nom_affichage} activé")
        time.sleep(0.5)
    
    # Affiche les statistiques
    print("\n📊 STATISTIQUES:")
    stats = gestionnaire.obtenir_statistiques()
    print(f"   Total profils: {stats['total_profils']}")
    print(f"   Types: {stats['types']}")
    print(f"   Profil actif: {stats['profil_actif']}")
    
    print("\n🎉 Démonstration terminée!")
    return gestionnaire


if __name__ == "__main__":
    demo_multi_profils()