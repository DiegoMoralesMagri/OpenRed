#!/usr/bin/env python3
"""
🏰 OpenRed Network - Module Fort: Fort Principal
Classe principale représentant un fort complet
"""

import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime

from .identite import IdentiteFort, GenerateurIdentite, RegistreIdentites
from .fenetres import GestionnaireFenetres, FenetrePublique, FenetreCanal


class Fort:
    """
    🏰 Fort Principal - Représente un fort complet sur OpenRed Network
    
    Un fort est une entité autonome avec:
    - Une identité cryptographique unique
    - Des fenêtres publiques et privées
    - Un système de gestion des visiteurs
    - Des capacités de communication
    """
    
    def __init__(self, nom: str, identite: IdentiteFort = None, cle_privee = None):
        # Identité du fort
        if identite is None:
            self.identite, self.cle_privee = GenerateurIdentite.generer_identite(nom)
        else:
            self.identite = identite
            self.cle_privee = cle_privee
        
        # État du fort
        self.actif = False
        self.timestamp_creation = time.time()
        self.derniere_activite = time.time()
        
        # Gestionnaire des fenêtres
        self.gestionnaire_fenetres = GestionnaireFenetres(self.identite)
        
        # Registre des identités connues
        self.registre_identites = RegistreIdentites()
        self.registre_identites.ajouter_identite(self.identite, self.cle_privee)
        
        # Communications et réseau
        self.forts_connus: Dict[str, IdentiteFort] = {}
        self.connexions_actives: Dict[str, Dict] = {}
        
        # Thread de maintenance
        self.thread_maintenance = None
        self.maintenance_active = False
        
        print(f"🏰 Fort créé: {self.identite.nom} ({self.identite.id_fort})")
    
    def activer(self):
        """Active le fort et ses services"""
        if not self.actif:
            self.actif = True
            self.derniere_activite = time.time()
            
            # Création de la fenêtre publique
            self.gestionnaire_fenetres.creer_fenetre_publique()
            
            # Démarrage de la maintenance
            self._demarrer_maintenance()
            
            print(f"✅ Fort {self.identite.nom} activé")
    
    def desactiver(self):
        """Désactive le fort"""
        if self.actif:
            self.actif = False
            self.maintenance_active = False
            
            # Fermeture des canaux
            for canal in self.gestionnaire_fenetres.canaux_actifs.values():
                canal.fermer_canal()
            
            print(f"🔴 Fort {self.identite.nom} désactivé")
    
    def _demarrer_maintenance(self):
        """Démarre le thread de maintenance du fort"""
        if not self.maintenance_active:
            self.maintenance_active = True
            self.thread_maintenance = threading.Thread(target=self._boucle_maintenance, daemon=True)
            self.thread_maintenance.start()
    
    def _boucle_maintenance(self):
        """Boucle de maintenance du fort"""
        while self.maintenance_active and self.actif:
            try:
                # Nettoyage des fenêtres inactives
                self.gestionnaire_fenetres.nettoyer_fenetres_inactives()
                
                # Mise à jour activité
                self.derniere_activite = time.time()
                
                # Attente avant prochain cycle
                time.sleep(60)  # 1 minute
                
            except Exception as e:
                print(f"❌ Erreur maintenance fort {self.identite.nom}: {e}")
                time.sleep(10)
    
    # === GESTION DES FENÊTRES ===
    
    def obtenir_fenetre_publique(self) -> Optional[FenetrePublique]:
        """Obtient la fenêtre publique du fort"""
        return self.gestionnaire_fenetres.fenetre_publique
    
    def publier_annonce(self, contenu: str, type_annonce: str = "annonce"):
        """Publie une annonce sur la fenêtre publique"""
        fenetre_pub = self.obtenir_fenetre_publique()
        if fenetre_pub:
            fenetre_pub.ajouter_publication(contenu, type_annonce)
            print(f"📢 Annonce publiée sur {self.identite.nom}: {contenu[:50]}...")
    
    def ouvrir_canal(self, fort_cible: str) -> FenetreCanal:
        """Ouvre un canal vers un autre fort"""
        canal = self.gestionnaire_fenetres.creer_canal(fort_cible)
        canal.ouvrir_canal()
        return canal
    
    def envoyer_message(self, fort_cible: str, message: str) -> bool:
        """Envoie un message à un autre fort"""
        canal = self.gestionnaire_fenetres.canaux_actifs.get(fort_cible)
        
        if not canal:
            canal = self.ouvrir_canal(fort_cible)
        
        return canal.envoyer_message(message)
    
    # === GESTION DES IDENTITÉS ===
    
    def ajouter_fort_connu(self, identite: IdentiteFort):
        """Ajoute un fort à la liste des forts connus"""
        self.forts_connus[identite.id_fort] = identite
        self.registre_identites.ajouter_identite(identite)
        print(f"🤝 Fort ajouté aux connus: {identite.nom}")
    
    def obtenir_fort_connu(self, id_fort: str) -> Optional[IdentiteFort]:
        """Récupère un fort connu par son ID"""
        return self.forts_connus.get(id_fort)
    
    def lister_forts_connus(self) -> Dict[str, str]:
        """Liste tous les forts connus (ID -> Nom)"""
        return {id_fort: identite.nom for id_fort, identite in self.forts_connus.items()}
    
    # === INTERACTIONS AVEC VISITEURS ===
    
    def autoriser_visite(self, fort_visiteur: str, nom_visiteur: str = "") -> Dict:
        """Autorise un fort à visiter via la fenêtre publique"""
        fenetre_pub = self.obtenir_fenetre_publique()
        if fenetre_pub:
            return fenetre_pub.autoriser_regard(fort_visiteur, nom_visiteur)
        else:
            return {"statut": "refuse", "raison": "Fenêtre publique non disponible"}
    
    # === STATISTIQUES ET ÉTAT ===
    
    def obtenir_statistiques(self) -> Dict:
        """Obtient les statistiques complètes du fort"""
        stats_fenetres = self.gestionnaire_fenetres.obtenir_statistiques()
        
        return {
            "identite": {
                "nom": self.identite.nom,
                "id": self.identite.id_fort,
                "adresse": self.identite.adresse_orp
            },
            "etat": {
                "actif": self.actif,
                "uptime": time.time() - self.timestamp_creation,
                "derniere_activite": self.derniere_activite
            },
            "fenetres": stats_fenetres,
            "reseau": {
                "forts_connus": len(self.forts_connus),
                "connexions_actives": len(self.connexions_actives)
            }
        }
    
    def obtenir_etat_complet(self) -> Dict:
        """Obtient l'état complet du fort pour debug/admin"""
        return {
            "identite": self.identite.to_dict(),
            "statistiques": self.obtenir_statistiques(),
            "fenetres": self.gestionnaire_fenetres.lister_fenetres(),
            "forts_connus": self.lister_forts_connus()
        }
    
    # === SAUVEGARDE/CHARGEMENT ===
    
    def sauvegarder_etat(self, fichier: str):
        """Sauvegarde l'état du fort"""
        import json
        
        etat = {
            "identite": self.identite.to_dict(),
            "forts_connus": {id_fort: identite.to_dict() 
                            for id_fort, identite in self.forts_connus.items()},
            "timestamp_sauvegarde": time.time()
        }
        
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(etat, f, indent=2, ensure_ascii=False)
        
        print(f"💾 État du fort sauvegardé: {fichier}")
    
    def charger_etat(self, fichier: str):
        """Charge l'état du fort"""
        import json
        
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                etat = json.load(f)
            
            # Chargement des forts connus
            for id_fort, identite_data in etat.get("forts_connus", {}).items():
                identite = IdentiteFort.from_dict(identite_data)
                self.ajouter_fort_connu(identite)
            
            print(f"📂 État du fort chargé: {fichier}")
            
        except FileNotFoundError:
            print(f"📁 Fichier {fichier} non trouvé")
        except Exception as e:
            print(f"❌ Erreur chargement état: {e}")
    
    def __str__(self):
        return f"Fort({self.identite.nom}, {self.identite.id_fort}, actif={self.actif})"
    
    def __repr__(self):
        return self.__str__()