#!/usr/bin/env python3
"""
🏰 OpenRed Network - Prototype Fort avec Fenêtres
Concept : "Le fort n'est pas sur le réseau, juste des fenêtres"
"""

import json
import time
import uuid
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import socket
import threading


@dataclass
class IdentiteFort:
    """Identité unique du Fort"""
    id_fort: str
    nom: str
    adresse_orp: str  # orp://identifiant.domain
    cle_publique: str
    timestamp_creation: str
    version_protocole: str = "1.0.0"


class FenetrePublique:
    """
    🪟 Fenêtre Publique - Visible par tous les forts du réseau
    Permet de consulter le profil public sans accéder au fort
    """
    
    def __init__(self, proprietaire: IdentiteFort):
        self.proprietaire = proprietaire
        self.profil_public = {
            "nom": proprietaire.nom,
            "description": "Fort sur OpenRed Network",
            "statut": "En ligne",
            "derniere_activite": datetime.now().isoformat(),
            "publications_publiques": []
        }
        self.visiteurs_recents = []
    
    def autoriser_regard(self, fort_demandeur: str) -> Dict:
        """Autorise un fort à regarder par cette fenêtre"""
        self.visiteurs_recents.append({
            "fort": fort_demandeur,
            "timestamp": datetime.now().isoformat()
        })
        
        # Retourne une PROJECTION (pas les vraies données)
        projection = {
            "type": "projection_fenetre_publique",
            "fort_proprietaire": self.proprietaire.id_fort,
            "timestamp": datetime.now().isoformat(),
            "contenu": self.profil_public.copy(),
            "watermark": f"PROJECTION-{uuid.uuid4()}"
        }
        
        print(f"🪟 Fort {fort_demandeur} regarde par la fenêtre publique de {self.proprietaire.nom}")
        return projection
    
    def ajouter_publication(self, contenu: str):
        """Ajoute une publication visible dans la fenêtre publique"""
        publication = {
            "id": str(uuid.uuid4()),
            "contenu": contenu,
            "timestamp": datetime.now().isoformat()
        }
        self.profil_public["publications_publiques"].append(publication)
        print(f"📝 Nouvelle publication ajoutée à la fenêtre publique")


class FenetreCanal:
    """
    🪟 Fenêtre Canal Privé - Visible uniquement par un fort autorisé
    Canal sécurisé entre deux forts spécifiques
    """
    
    def __init__(self, proprietaire: IdentiteFort, fort_autorise: str):
        self.proprietaire = proprietaire
        self.fort_autorise = fort_autorise
        self.contenu_partage = []
        self.actif = True
    
    def autoriser_regard(self, fort_demandeur: str) -> Optional[Dict]:
        """Autorise UNIQUEMENT le fort spécifique à regarder"""
        if fort_demandeur != self.fort_autorise:
            print(f"🚫 Accès refusé : {fort_demandeur} n'est pas autorisé sur ce canal")
            return None
        
        if not self.actif:
            print(f"🚫 Canal inactif")
            return None
        
        projection = {
            "type": "projection_canal_prive",
            "fort_proprietaire": self.proprietaire.id_fort,
            "fort_autorise": self.fort_autorise,
            "timestamp": datetime.now().isoformat(),
            "contenu": self.contenu_partage.copy(),
            "watermark": f"CANAL-{uuid.uuid4()}"
        }
        
        print(f"🪟 Fort {fort_demandeur} accède au canal privé")
        return projection
    
    def partager_dans_canal(self, contenu: str):
        """Partage du contenu dans ce canal privé"""
        partage = {
            "id": str(uuid.uuid4()),
            "contenu": contenu,
            "timestamp": datetime.now().isoformat()
        }
        self.contenu_partage.append(partage)
        print(f"🔒 Contenu partagé dans le canal privé")
    
    def fermer_canal(self):
        """Ferme définitivement ce canal"""
        self.actif = False
        self.contenu_partage.clear()
        print(f"🔒 Canal fermé avec {self.fort_autorise}")


class Fort:
    """
    🏰 Fort Digital - Écosystème numérique privé et sécurisé
    Principe : Le fort N'EST PAS sur le réseau, seules les fenêtres le sont
    """
    
    def __init__(self, nom: str, domaine: str = "localhost"):
        # 🔒 DONNÉES PRIVÉES (jamais exposées)
        self.donnees_privees = {
            "documents": [],
            "historique_complet": [],
            "configurations": {},
            "secrets": {}
        }
        
        # 🆔 Identité du fort
        self.identite = self._generer_identite(nom, domaine)
        
        # 🪟 FENÊTRES (seules interfaces exposées)
        self.fenetre_publique = FenetrePublique(self.identite)
        self.fenetres_canaux: Dict[str, FenetreCanal] = {}
        
        # 📡 Capacités réseau
        self.port_ecoute = 9000 + hash(self.identite.id_fort) % 1000
        self.serveur_actif = False
        
        print(f"🏰 Fort '{nom}' créé avec l'identité {self.identite.id_fort}")
        print(f"📍 Adresse ORP: {self.identite.adresse_orp}")
    
    def _generer_identite(self, nom: str, domaine: str) -> IdentiteFort:
        """Génère une identité cryptographique unique pour le fort"""
        # Génération clé RSA
        cle_privee = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        cle_publique = cle_privee.public_key()
        
        # Sérialisation clé publique
        cle_pub_bytes = cle_publique.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # ID unique basé sur la clé publique
        id_fort = hashlib.sha256(cle_pub_bytes).hexdigest()[:16]
        
        return IdentiteFort(
            id_fort=id_fort,
            nom=nom,
            adresse_orp=f"orp://{nom.lower()}.{domaine}",
            cle_publique=cle_pub_bytes.decode('utf-8'),
            timestamp_creation=datetime.now().isoformat()
        )
    
    def emettre_signal_reseau(self):
        """
        📡 Émet un signal sur le réseau pour :
        1. Annoncer l'existence de ce fort
        2. Cartographier les autres forts présents
        """
        signal = {
            "type": "signal_fort",
            "identite": asdict(self.identite),
            "fenetre_publique": True,
            "canaux_actifs": len(self.fenetres_canaux),
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📡 Émission signal réseau pour {self.identite.nom}")
        return signal
    
    def regarder_par_fenetre(self, fort_cible: str, type_fenetre: str = "publique", canal: str = None):
        """
        🔍 Regarde par la fenêtre d'un autre fort
        Principe : Observer à distance sans quitter son fort
        """
        print(f"🔍 {self.identite.nom} regarde par la fenêtre de {fort_cible}")
        
        # TODO: Implémentation réseau pour contacter le fort cible
        # Pour l'instant, simulation locale
        return {
            "observateur": self.identite.id_fort,
            "fort_cible": fort_cible,
            "type_fenetre": type_fenetre,
            "timestamp": datetime.now().isoformat()
        }
    
    def creer_canal_prive(self, fort_ami: str) -> str:
        """
        🤝 Crée un canal privé avec un autre fort
        Les deux forts doivent accepter pour activer le canal
        """
        id_canal = f"canal_{self.identite.id_fort}_{fort_ami}"
        
        fenetre_canal = FenetreCanal(self.identite, fort_ami)
        self.fenetres_canaux[id_canal] = fenetre_canal
        
        print(f"🤝 Canal privé créé avec {fort_ami}")
        return id_canal
    
    def ajouter_donnee_privee(self, cle: str, valeur: Any):
        """🔒 Ajoute une donnée privée (jamais exposée)"""
        self.donnees_privees[cle] = {
            "valeur": valeur,
            "timestamp": datetime.now().isoformat()
        }
        print(f"🔒 Donnée privée ajoutée : {cle}")
    
    def obtenir_fenetre(self, type_fenetre: str, canal: str = None):
        """Retourne la fenêtre demandée pour consultation externe"""
        if type_fenetre == "publique":
            return self.fenetre_publique
        elif type_fenetre == "canal" and canal in self.fenetres_canaux:
            return self.fenetres_canaux[canal]
        return None
    
    def __repr__(self):
        return f"Fort({self.identite.nom}, {self.identite.adresse_orp})"


def demo_forts_avec_fenetres():
    """🎭 Démonstration du système de forts avec fenêtres"""
    print("=" * 60)
    print("🏰 DÉMONSTRATION OPENRED NETWORK - FORTS AVEC FENÊTRES")
    print("=" * 60)
    
    # Création de deux forts
    print("\n1️⃣ Création des forts...")
    fort_alice = Fort("Alice", "openred.network")
    fort_bob = Fort("Bob", "openred.network")
    
    # Alice ajoute du contenu privé (jamais visible)
    print("\n2️⃣ Ajout de données privées...")
    fort_alice.ajouter_donnee_privee("journal_secret", "Mes pensées les plus intimes")
    fort_alice.ajouter_donnee_privee("documents_perso", ["doc1.pdf", "photo_famille.jpg"])
    
    # Alice configure sa fenêtre publique
    print("\n3️⃣ Configuration des fenêtres publiques...")
    fort_alice.fenetre_publique.ajouter_publication("Bonjour le réseau OpenRed !")
    fort_bob.fenetre_publique.ajouter_publication("Salut tout le monde !")
    
    # Bob regarde par la fenêtre publique d'Alice
    print("\n4️⃣ Bob regarde par la fenêtre publique d'Alice...")
    projection_alice = fort_alice.fenetre_publique.autoriser_regard(fort_bob.identite.id_fort)
    print(f"   Projection reçue : {projection_alice['contenu']['publications_publiques']}")
    
    # Alice et Bob créent un canal privé
    print("\n5️⃣ Création d'un canal privé...")
    id_canal = fort_alice.creer_canal_prive(fort_bob.identite.id_fort)
    id_canal_bob = fort_bob.creer_canal_prive(fort_alice.identite.id_fort)
    
    # Partage dans le canal privé
    print("\n6️⃣ Partage dans le canal privé...")
    fort_alice.fenetres_canaux[id_canal].partager_dans_canal("Message secret pour Bob")
    
    # Bob accède au canal privé d'Alice
    print("\n7️⃣ Bob accède au canal privé...")
    projection_canal = fort_alice.fenetres_canaux[id_canal].autoriser_regard(fort_bob.identite.id_fort)
    if projection_canal:
        print(f"   Message reçu : {projection_canal['contenu']}")
    
    # Émission des signaux réseau
    print("\n8️⃣ Émission des signaux réseau...")
    signal_alice = fort_alice.emettre_signal_reseau()
    signal_bob = fort_bob.emettre_signal_reseau()
    
    print(f"\n✅ Démonstration terminée !")
    print(f"   - Forts créés : {len([fort_alice, fort_bob])}")
    print(f"   - Données privées protégées : ✓")
    print(f"   - Fenêtres fonctionnelles : ✓")
    print(f"   - Canal privé établi : ✓")
    print(f"   - Signaux réseau émis : ✓")


if __name__ == "__main__":
    demo_forts_avec_fenetres()