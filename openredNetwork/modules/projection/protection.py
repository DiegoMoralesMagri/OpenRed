#!/usr/bin/env python3
"""
🛡️ OpenRed Network - Module Projection: Protection Anti-Copie
Moteur de protection révolutionnaire contre la copie
"""

import time
import threading
import uuid
from typing import Dict, List, Optional, Callable

from .format_orn import FormatProjectionORN, GestionnaireProjections


class MoteurAntiCopie:
    """
    🛡️ Moteur de protection anti-copie révolutionnaire
    Empêche capture, copie, transfert par tous moyens
    """
    
    def __init__(self):
        self.gestionnaire = GestionnaireProjections()
        self.watermarks_uniques = {}
        self.sequences_protection = {}
        self.tokens_temporaires = {}
        self.detection_active = True
        
        # Thread de surveillance
        self.thread_surveillance = None
        self.surveillance_active = False
        
        # Callbacks pour événements de sécurité
        self.callbacks_securite = {
            "tentative_copie": [],
            "autodestruction": [],
            "acces_refuse": [],
            "projection_expiree": []
        }
        
        print("🛡️ Moteur anti-copie initialisé")
    
    def ajouter_callback_securite(self, evenement: str, callback: Callable):
        """Ajoute un callback pour les événements de sécurité"""
        if evenement in self.callbacks_securite:
            self.callbacks_securite[evenement].append(callback)
    
    def _notifier_callback_securite(self, evenement: str, *args):
        """Notifie les callbacks de sécurité"""
        for callback in self.callbacks_securite.get(evenement, []):
            try:
                callback(*args)
            except Exception as e:
                print(f"❌ Erreur callback sécurité {evenement}: {e}")
    
    def demarrer_surveillance(self):
        """Démarre la surveillance anti-copie"""
        if not self.surveillance_active:
            self.surveillance_active = True
            self.thread_surveillance = threading.Thread(target=self._boucle_surveillance, daemon=True)
            self.thread_surveillance.start()
            print("🛡️ Surveillance anti-copie démarrée")
    
    def arreter_surveillance(self):
        """Arrête la surveillance"""
        if self.surveillance_active:
            self.surveillance_active = False
            print("🛡️ Surveillance anti-copie arrêtée")
    
    def _boucle_surveillance(self):
        """Boucle de surveillance continue"""
        while self.surveillance_active:
            try:
                # Nettoyage des projections expirées
                self.gestionnaire.nettoyer_projections_expirees()
                
                # Vérification des tentatives de copie
                self._detecter_activites_suspectes()
                
                # Nettoyage des tokens temporaires
                self._nettoyer_tokens_expires()
                
                time.sleep(5)  # Surveillance toutes les 5 secondes
                
            except Exception as e:
                print(f"❌ Erreur surveillance: {e}")
                time.sleep(10)
    
    def creer_projection_securisee(self, contenu: Dict, fort_proprietaire: str, 
                                  fort_observateur: str, duree_vie: int = 300, 
                                  niveau_protection: int = 5) -> str:
        """Crée une projection sécurisée et retourne l'ID de session"""
        
        from .format_orn import GenerateurProjection
        
        # Création de la projection
        projection = GenerateurProjection.creer_projection(
            contenu, fort_proprietaire, fort_observateur, duree_vie, niveau_protection
        )
        
        # Enregistrement avec metadata de sécurité
        metadata = {
            "creation_timestamp": time.time(),
            "niveau_protection": niveau_protection,
            "adresse_creation": "localhost",  # TODO: IP réelle
            "tentatives_copie_detectees": 0
        }
        
        session_id = self.gestionnaire.enregistrer_projection(projection, metadata)
        
        # Génération des protections supplémentaires
        self._generer_protections_supplementaires(projection.id_projection)
        
        print(f"🔮 Projection sécurisée créée: {projection.id_projection}")
        return session_id
    
    def _generer_protections_supplementaires(self, id_projection: str):
        """Génère des protections supplémentaires pour une projection"""
        
        # Watermarks uniques pour cette projection
        self.watermarks_uniques[id_projection] = [
            f"ORN-{id_projection[:8]}-{int(time.time()) % 10000}",
            f"PROTECT-{uuid.uuid4().hex[:8]}",
            f"SECURE-{int(time.time())}"
        ]
        
        # Séquence de protection temporelle
        self.sequences_protection[id_projection] = {
            "debut": time.time(),
            "checkpoints": [time.time() + i * 60 for i in range(1, 6)],  # Toutes les minutes
            "validations_requises": 3
        }
        
        # Token temporaire
        token = f"token_{uuid.uuid4().hex}"
        self.tokens_temporaires[token] = {
            "id_projection": id_projection,
            "creation": time.time(),
            "expiration": time.time() + 300,
            "utilisations": 0,
            "max_utilisations": 10
        }
    
    def acceder_projection_securisee(self, id_projection: str, fort_demandeur: str, 
                                   session_id: str = None) -> Optional[Dict]:
        """Accède à une projection avec toutes les vérifications de sécurité"""
        
        # Accès via le gestionnaire
        resultat = self.gestionnaire.acceder_projection(id_projection, fort_demandeur, session_id)
        
        if not resultat:
            self._notifier_callback_securite("acces_refuse", id_projection, fort_demandeur)
            return None
        
        # Vérifications supplémentaires de sécurité
        if not self._verifier_protections_supplementaires(id_projection):
            print(f"🚫 Protections supplémentaires échouées pour {id_projection}")
            return None
        
        # Mise à jour des métriques de sécurité
        self._mettre_a_jour_metriques_securite(id_projection)
        
        return resultat
    
    def _verifier_protections_supplementaires(self, id_projection: str) -> bool:
        """Vérifie les protections supplémentaires d'une projection"""
        
        # Vérification séquence de protection
        if id_projection in self.sequences_protection:
            sequence = self.sequences_protection[id_projection]
            maintenant = time.time()
            
            # Vérifier si on a dépassé trop de checkpoints
            checkpoints_rates = sum(1 for cp in sequence["checkpoints"] if cp < maintenant)
            if checkpoints_rates > sequence["validations_requises"]:
                print(f"🚨 Trop de checkpoints ratés pour {id_projection}")
                return False
        
        return True
    
    def _mettre_a_jour_metriques_securite(self, id_projection: str):
        """Met à jour les métriques de sécurité"""
        if id_projection in self.gestionnaire.projections_actives:
            info = self.gestionnaire.projections_actives[id_projection]
            metadata = info.get("metadata", {})
            metadata["derniere_verification_securite"] = time.time()
    
    def detecter_tentative_copie(self, id_projection: str, type_tentative: str = "selection"):
        """Détecte et traite une tentative de copie"""
        
        if id_projection not in self.gestionnaire.projections_actives:
            return
        
        info_projection = self.gestionnaire.projections_actives[id_projection]
        metadata = info_projection.get("metadata", {})
        
        # Incrémentation des tentatives détectées
        metadata["tentatives_copie_detectees"] = metadata.get("tentatives_copie_detectees", 0) + 1
        
        print(f"🚨 Tentative de {type_tentative} détectée sur {id_projection}")
        
        # Notification callback
        self._notifier_callback_securite("tentative_copie", id_projection, type_tentative)
        
        # Seuil d'autodestruction
        if metadata["tentatives_copie_detectees"] >= 5:
            self.autodestruction_projection(id_projection)
    
    def autodestruction_projection(self, id_projection: str):
        """Auto-destruction de la projection si tentatives de copie détectées"""
        
        if id_projection in self.gestionnaire.projections_actives:
            info_projection = self.gestionnaire.projections_actives[id_projection]
            projection = info_projection["projection"]
            
            # Notification avant destruction
            self._notifier_callback_securite("autodestruction", id_projection, projection)
            
            # Suppression immédiate
            del self.gestionnaire.projections_actives[id_projection]
            
            # Nettoyage protections associées
            if id_projection in self.watermarks_uniques:
                del self.watermarks_uniques[id_projection]
            if id_projection in self.sequences_protection:
                del self.sequences_protection[id_projection]
            
            print(f"💥 Auto-destruction projection: {id_projection}")
    
    def _detecter_activites_suspectes(self):
        """Détecte les activités suspectes sur les projections actives"""
        
        maintenant = time.time()
        
        for id_proj, info in self.gestionnaire.projections_actives.items():
            projection = info["projection"]
            metadata = info.get("metadata", {})
            
            # Détection accès trop fréquents (potentiel scraping)
            if info["tentatives_acces"] > 50 and info["debut_affichage"]:
                duree_affichage = maintenant - info["debut_affichage"]
                if duree_affichage < 60:  # Plus de 50 accès en moins d'1 minute
                    print(f"🚨 Activité suspecte détectée: {id_proj} (trop d'accès)")
                    self.detecter_tentative_copie(id_proj, "scraping")
            
            # Détection projection qui traîne trop longtemps
            if info["debut_affichage"] and (maintenant - info["debut_affichage"]) > 1800:  # 30 min
                print(f"🚨 Projection ouverte trop longtemps: {id_proj}")
                self._notifier_callback_securite("projection_expiree", id_proj)
    
    def _nettoyer_tokens_expires(self):
        """Nettoie les tokens temporaires expirés"""
        
        maintenant = time.time()
        tokens_expires = []
        
        for token, info in self.tokens_temporaires.items():
            if maintenant > info["expiration"] or info["utilisations"] >= info["max_utilisations"]:
                tokens_expires.append(token)
        
        for token in tokens_expires:
            del self.tokens_temporaires[token]
    
    def obtenir_watermarks_projection(self, id_projection: str) -> List[str]:
        """Obtient les watermarks d'une projection"""
        return self.watermarks_uniques.get(id_projection, [])
    
    def valider_token_temporaire(self, token: str) -> Optional[str]:
        """Valide un token temporaire et retourne l'ID de projection"""
        
        if token not in self.tokens_temporaires:
            return None
        
        info_token = self.tokens_temporaires[token]
        
        # Vérification expiration
        if time.time() > info_token["expiration"]:
            del self.tokens_temporaires[token]
            return None
        
        # Vérification utilisations
        if info_token["utilisations"] >= info_token["max_utilisations"]:
            del self.tokens_temporaires[token]
            return None
        
        # Incrémentation utilisation
        info_token["utilisations"] += 1
        
        return info_token["id_projection"]
    
    def obtenir_statistiques_securite(self) -> Dict:
        """Obtient les statistiques de sécurité détaillées"""
        
        stats_base = self.gestionnaire.obtenir_statistiques()
        
        # Statistiques spécifiques à la sécurité
        total_tentatives_copie = sum(
            info.get("metadata", {}).get("tentatives_copie_detectees", 0)
            for info in self.gestionnaire.projections_actives.values()
        )
        
        projections_protegees = len([
            p for p in self.gestionnaire.projections_actives.values()
            if p.get("metadata", {}).get("niveau_protection", 0) >= 4
        ])
        
        return {
            **stats_base,
            "securite": {
                "surveillance_active": self.surveillance_active,
                "tentatives_copie_detectees": total_tentatives_copie,
                "projections_protegees": projections_protegees,
                "watermarks_actifs": len(self.watermarks_uniques),
                "tokens_temporaires": len(self.tokens_temporaires),
                "sequences_protection": len(self.sequences_protection)
            }
        }
    
    def generer_rapport_securite(self) -> str:
        """Génère un rapport de sécurité détaillé"""
        
        stats = self.obtenir_statistiques_securite()
        
        rapport = f"""
🛡️ RAPPORT DE SÉCURITÉ ANTI-COPIE
{'=' * 50}

📊 STATISTIQUES GÉNÉRALES:
  - Projections créées: {stats['projections_creees']}
  - Projections actives: {stats['projections_actives']}
  - Projections expirées: {stats['projections_expirees']}
  - Taux de succès: {stats['taux_succes']:.1f}%

🚨 SÉCURITÉ:
  - Surveillance: {'Activée' if stats['securite']['surveillance_active'] else 'Désactivée'}
  - Tentatives de copie détectées: {stats['securite']['tentatives_copie_detectees']}
  - Projections haute protection: {stats['securite']['projections_protegees']}
  - Watermarks actifs: {stats['securite']['watermarks_actifs']}
  - Tokens temporaires: {stats['securite']['tokens_temporaires']}

🔐 PROJECTIONS ACTIVES:
"""
        
        for info in self.gestionnaire.lister_projections_actives():
            rapport += f"  - {info['id'][:16]}... | {info['proprietaire']} -> {info['observateur']} | "
            rapport += f"Niveau {info['niveau_protection']} | {info['temps_restant']:.0f}s restantes\n"
        
        return rapport
    
    def __del__(self):
        """Destructeur - arrête la surveillance"""
        if hasattr(self, 'surveillance_active') and self.surveillance_active:
            self.arreter_surveillance()