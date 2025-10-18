#!/usr/bin/env python3
"""
🪟 OpenRed Network - Module Fort: Fenêtres
Système de fenêtres publiques et privées pour les forts
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .identite import IdentiteFort


@dataclass
class VisiteurFenetre:
    """Information d'un visiteur regardant par une fenêtre"""
    id_fort: str
    nom: str
    timestamp: float
    duree_regard: float = 0.0
    actions: List[str] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []


class FenetrePublique:
    """
    🪟 Fenêtre Publique - Visible par tous les forts du réseau
    Permet de consulter le profil public sans accéder au fort
    """
    
    def __init__(self, proprietaire: IdentiteFort):
        self.proprietaire = proprietaire
        self.id_fenetre = f"pub_{uuid.uuid4().hex[:8]}"
        self.type_fenetre = "publique"
        
        # Contenu visible par la fenêtre
        self.profil_public = {
            "nom": proprietaire.nom,
            "description": "Fort sur OpenRed Network",
            "statut": "En ligne",
            "derniere_activite": datetime.now().isoformat(),
            "publications_publiques": [],
            "statistiques": {
                "visiteurs_total": 0,
                "regards_aujourd_hui": 0
            }
        }
        
        # Surveillance des visiteurs
        self.visiteurs_recents: List[VisiteurFenetre] = []
        self.visiteurs_autorises: List[str] = []  # Tous autorisés pour fenêtre publique
        self.historique_regards = []
    
    def autoriser_regard(self, fort_demandeur: str, nom_demandeur: str = "") -> Dict:
        """Autorise un fort à regarder par cette fenêtre publique"""
        visiteur = VisiteurFenetre(
            id_fort=fort_demandeur,
            nom=nom_demandeur or fort_demandeur,
            timestamp=time.time()
        )
        
        self.visiteurs_recents.append(visiteur)
        self.profil_public["statistiques"]["visiteurs_total"] += 1
        self.profil_public["statistiques"]["regards_aujourd_hui"] += 1
        
        # Nettoyage visiteurs anciens (plus de 1h)
        maintenant = time.time()
        self.visiteurs_recents = [v for v in self.visiteurs_recents 
                                 if maintenant - v.timestamp < 3600]
        
        print(f"👁️ {nom_demandeur} regarde par la fenêtre publique de {self.proprietaire.nom}")
        
        return {
            "statut": "autorise",
            "contenu": self.profil_public,
            "id_session": f"session_{uuid.uuid4().hex[:8]}",
            "permissions": ["lecture"]
        }
    
    def ajouter_publication(self, contenu: str, type_pub: str = "annonce"):
        """Ajoute une publication visible par la fenêtre"""
        publication = {
            "id": f"pub_{uuid.uuid4().hex[:8]}",
            "contenu": contenu,
            "type": type_pub,
            "timestamp": datetime.now().isoformat(),
            "auteur": self.proprietaire.nom
        }
        
        self.profil_public["publications_publiques"].append(publication)
        
        # Garder seulement les 10 dernières publications
        if len(self.profil_public["publications_publiques"]) > 10:
            self.profil_public["publications_publiques"] = \
                self.profil_public["publications_publiques"][-10:]
    
    def obtenir_statistiques(self) -> Dict:
        """Obtient les statistiques de la fenêtre"""
        return {
            "visiteurs_actuels": len(self.visiteurs_recents),
            "visiteurs_total": self.profil_public["statistiques"]["visiteurs_total"],
            "regards_aujourd_hui": self.profil_public["statistiques"]["regards_aujourd_hui"],
            "derniers_visiteurs": [
                {"nom": v.nom, "timestamp": v.timestamp} 
                for v in self.visiteurs_recents[-5:]
            ]
        }


class FenetreCanal:
    """
    📡 Fenêtre Canal - Communication directe entre forts spécifiques
    Permet échange de messages privés et sécurisés
    """
    
    def __init__(self, proprietaire: IdentiteFort, fort_cible: str):
        self.proprietaire = proprietaire
        self.fort_cible = fort_cible
        self.id_fenetre = f"canal_{uuid.uuid4().hex[:8]}"
        self.type_fenetre = "canal"
        
        # État du canal
        self.canal_ouvert = False
        self.derniere_activite = time.time()
        self.messages_echanges = []
        self.cle_session = None
        
        # Permissions et sécurité
        self.chiffrement_actif = True
        self.signature_requise = True
    
    def ouvrir_canal(self, cle_session: str = None) -> bool:
        """Ouvre le canal de communication"""
        self.canal_ouvert = True
        self.cle_session = cle_session or f"session_{uuid.uuid4().hex}"
        self.derniere_activite = time.time()
        
        print(f"📡 Canal ouvert: {self.proprietaire.nom} <-> {self.fort_cible}")
        return True
    
    def fermer_canal(self):
        """Ferme le canal de communication"""
        self.canal_ouvert = False
        self.cle_session = None
        print(f"📡 Canal fermé: {self.proprietaire.nom} <-> {self.fort_cible}")
    
    def envoyer_message(self, contenu: str, type_message: str = "texte") -> bool:
        """Envoie un message par le canal"""
        if not self.canal_ouvert:
            return False
        
        message = {
            "id": f"msg_{uuid.uuid4().hex[:8]}",
            "expediteur": self.proprietaire.id_fort,
            "destinataire": self.fort_cible,
            "contenu": contenu,
            "type": type_message,
            "timestamp": time.time(),
            "chiffre": self.chiffrement_actif
        }
        
        self.messages_echanges.append(message)
        self.derniere_activite = time.time()
        
        return True
    
    def recevoir_messages(self, depuis_timestamp: float = 0) -> List[Dict]:
        """Récupère les messages depuis un timestamp"""
        return [msg for msg in self.messages_echanges 
                if msg["timestamp"] > depuis_timestamp]


class GestionnaireFenetres:
    """
    🎛️ Gestionnaire centralisé des fenêtres d'un fort
    """
    
    def __init__(self, proprietaire: IdentiteFort):
        self.proprietaire = proprietaire
        self.fenetres: Dict[str, Any] = {}
        self.fenetre_publique: Optional[FenetrePublique] = None
        self.canaux_actifs: Dict[str, FenetreCanal] = {}
    
    def creer_fenetre_publique(self) -> FenetrePublique:
        """Crée la fenêtre publique du fort"""
        if not self.fenetre_publique:
            self.fenetre_publique = FenetrePublique(self.proprietaire)
            self.fenetres[self.fenetre_publique.id_fenetre] = self.fenetre_publique
            print(f"🪟 Fenêtre publique créée pour {self.proprietaire.nom}")
        
        return self.fenetre_publique
    
    def creer_canal(self, fort_cible: str) -> FenetreCanal:
        """Crée un canal vers un fort spécifique"""
        if fort_cible not in self.canaux_actifs:
            canal = FenetreCanal(self.proprietaire, fort_cible)
            self.canaux_actifs[fort_cible] = canal
            self.fenetres[canal.id_fenetre] = canal
            print(f"📡 Canal créé vers {fort_cible}")
        
        return self.canaux_actifs[fort_cible]
    
    def obtenir_fenetre(self, id_fenetre: str):
        """Récupère une fenêtre par son ID"""
        return self.fenetres.get(id_fenetre)
    
    def lister_fenetres(self) -> Dict[str, Dict]:
        """Liste toutes les fenêtres avec leurs infos"""
        infos = {}
        
        for id_fenetre, fenetre in self.fenetres.items():
            if isinstance(fenetre, FenetrePublique):
                infos[id_fenetre] = {
                    "type": "publique",
                    "visiteurs": len(fenetre.visiteurs_recents),
                    "publications": len(fenetre.profil_public["publications_publiques"])
                }
            elif isinstance(fenetre, FenetreCanal):
                infos[id_fenetre] = {
                    "type": "canal",
                    "cible": fenetre.fort_cible,
                    "ouvert": fenetre.canal_ouvert,
                    "messages": len(fenetre.messages_echanges)
                }
        
        return infos
    
    def nettoyer_fenetres_inactives(self):
        """Nettoie les fenêtres inactives"""
        maintenant = time.time()
        
        # Fermeture canaux inactifs (plus de 30 minutes)
        canaux_a_fermer = []
        for fort_cible, canal in self.canaux_actifs.items():
            if maintenant - canal.derniere_activite > 1800:  # 30 min
                canaux_a_fermer.append(fort_cible)
        
        for fort_cible in canaux_a_fermer:
            canal = self.canaux_actifs[fort_cible]
            canal.fermer_canal()
            del self.canaux_actifs[fort_cible]
            del self.fenetres[canal.id_fenetre]
            print(f"🧹 Canal inactif fermé: {fort_cible}")
    
    def obtenir_statistiques(self) -> Dict:
        """Obtient les statistiques globales des fenêtres"""
        stats = {
            "total_fenetres": len(self.fenetres),
            "fenetre_publique_active": self.fenetre_publique is not None,
            "canaux_actifs": len(self.canaux_actifs),
            "visiteurs_actuels": 0
        }
        
        if self.fenetre_publique:
            stats_pub = self.fenetre_publique.obtenir_statistiques()
            stats["visiteurs_actuels"] = stats_pub["visiteurs_actuels"]
            stats["visiteurs_total"] = stats_pub["visiteurs_total"]
        
        return stats