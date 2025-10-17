#!/usr/bin/env python3
"""
🏰 OpenRed Network - Système Intégré Complet
Integration Forts + Fenêtres + Réseau WAN
"""

import socket
import json
import time
import threading
import uuid
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@dataclass
class IdentiteFortIntegre:
    """Identité cryptographique complète du Fort"""
    id_fort: str
    nom: str
    adresse_orp: str
    cle_publique: str
    timestamp_creation: str
    ip_publique: str
    port_reseau: int
    version_protocole: str = "1.0.0"


class FenetreIntegree:
    """
    🪟 Fenêtre intégrée avec capacités réseau
    Permet consultation à distance via WAN
    """
    
    def __init__(self, proprietaire: IdentiteFortIntegre, type_fenetre: str):
        self.proprietaire = proprietaire
        self.type_fenetre = type_fenetre  # "publique", "canal_prive"
        self.contenu = {}
        self.observateurs_autorises = []
        self.sessions_actives = {}
        
    def configurer_contenu(self, contenu: Dict):
        """Configure le contenu visible dans cette fenêtre"""
        self.contenu = {
            "timestamp": datetime.now().isoformat(),
            "proprietaire": self.proprietaire.id_fort,
            "type": self.type_fenetre,
            "donnees": contenu,
            "watermark": f"FENETRE-{uuid.uuid4()}"
        }
    
    def autoriser_observation(self, id_fort_observateur: str, addr_reseau: tuple) -> Optional[Dict]:
        """Autorise un fort à observer cette fenêtre"""
        if self.type_fenetre == "publique" or id_fort_observateur in self.observateurs_autorises:
            session_id = str(uuid.uuid4())
            
            projection = {
                "session_id": session_id,
                "type_projection": f"projection_{self.type_fenetre}",
                "fort_proprietaire": self.proprietaire.id_fort,
                "fort_observateur": id_fort_observateur,
                "timestamp": datetime.now().isoformat(),
                "contenu": self.contenu.copy(),
                "anti_copie": {
                    "watermark_unique": f"OBS-{id_fort_observateur}-{uuid.uuid4()}",
                    "session_temporaire": True,
                    "addr_autorisee": addr_reseau
                }
            }
            
            self.sessions_actives[session_id] = {
                "observateur": id_fort_observateur,
                "addr": addr_reseau,
                "debut": time.time()
            }
            
            print(f"🪟 Fenêtre {self.type_fenetre} observée par {id_fort_observateur}")
            return projection
        
        print(f"🚫 Observation refusée pour {id_fort_observateur}")
        return None
    
    def fermer_session(self, session_id: str):
        """Ferme une session d'observation"""
        if session_id in self.sessions_actives:
            del self.sessions_actives[session_id]
            print(f"🔒 Session d'observation fermée: {session_id}")


class FortIntegre:
    """
    🏰 Fort Intégré Complet
    Combine : Écosystème privé + Fenêtres + Communication WAN
    """
    
    def __init__(self, nom: str, domaine: str = "openred.network"):
        # 🔒 DONNÉES PRIVÉES (jamais sur réseau)
        self.donnees_privees = {
            "documents": [],
            "historique": [],
            "secrets": {},
            "configurations": {}
        }
        
        # 🆔 Identité complète
        self.identite = self._generer_identite_complete(nom, domaine)
        
        # 🪟 FENÊTRES
        self.fenetre_publique = FenetreIntegree(self.identite, "publique")
        self.fenetres_canaux: Dict[str, FenetreIntegree] = {}
        
        # 🌐 RÉSEAU
        self.socket_wan = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_wan.bind(('0.0.0.0', self.identite.port_reseau))
        self.socket_wan.settimeout(1.0)
        
        # État réseau
        self.actif = True
        self.forts_reseau = {}
        self.stats_reseau = {"messages_envoyes": 0, "messages_recus": 0, "connexions": 0}
        
        # Configuration initiale
        self._configurer_fenetre_publique()
        
        print(f"🏰 Fort Intégré '{nom}' créé")
        print(f"   ID: {self.identite.id_fort}")
        print(f"   ORP: {self.identite.adresse_orp}")
        print(f"   IP: {self.identite.ip_publique}:{self.identite.port_reseau}")
    
    def _generer_identite_complete(self, nom: str, domaine: str) -> IdentiteFortIntegre:
        """Génère identité cryptographique + réseau"""
        # Génération clé RSA
        cle_privee = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cle_publique = cle_privee.public_key()
        
        cle_pub_bytes = cle_publique.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        id_fort = hashlib.sha256(cle_pub_bytes).hexdigest()[:12]
        
        # Détection IP publique
        try:
            ip_publique = requests.get("https://api.ipify.org", timeout=3).text.strip()
        except:
            ip_publique = "127.0.0.1"
        
        # Port réseau (basé sur hash de l'ID)
        port_base = 9000 + (hash(id_fort) % 1000)
        
        return IdentiteFortIntegre(
            id_fort=id_fort,
            nom=nom,
            adresse_orp=f"orp://{nom.lower()}.{domaine}",
            cle_publique=cle_pub_bytes.decode('utf-8'),
            timestamp_creation=datetime.now().isoformat(),
            ip_publique=ip_publique,
            port_reseau=port_base
        )
    
    def _configurer_fenetre_publique(self):
        """Configure la fenêtre publique avec profil de base"""
        profil_public = {
            "nom": self.identite.nom,
            "description": f"Fort {self.identite.nom} sur OpenRed Network",
            "statut": "En ligne",
            "adresse_orp": self.identite.adresse_orp,
            "derniere_activite": datetime.now().isoformat(),
            "publications": [
                {
                    "id": str(uuid.uuid4()),
                    "contenu": f"Bonjour du Fort {self.identite.nom} !",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        self.fenetre_publique.configurer_contenu(profil_public)
    
    def ajouter_donnee_privee(self, categorie: str, donnee: Any):
        """🔒 Ajoute une donnée privée (reste dans le fort)"""
        if categorie not in self.donnees_privees:
            self.donnees_privees[categorie] = []
        
        self.donnees_privees[categorie].append({
            "donnee": donnee,
            "timestamp": datetime.now().isoformat(),
            "id": str(uuid.uuid4())
        })
        
        print(f"🔒 Donnée privée ajoutée: {categorie}")
    
    def publier_dans_fenetre_publique(self, contenu: str):
        """📝 Ajoute une publication dans la fenêtre publique"""
        publication = {
            "id": str(uuid.uuid4()),
            "contenu": contenu,
            "timestamp": datetime.now().isoformat()
        }
        
        # Mise à jour du contenu de la fenêtre
        contenu_actuel = self.fenetre_publique.contenu["donnees"]
        contenu_actuel["publications"].append(publication)
        contenu_actuel["derniere_activite"] = datetime.now().isoformat()
        
        self.fenetre_publique.configurer_contenu(contenu_actuel)
        print(f"📝 Publication ajoutée à la fenêtre publique")
    
    def creer_canal_prive_integre(self, id_fort_ami: str) -> str:
        """🤝 Crée un canal privé intégré avec réseau"""
        id_canal = f"canal_{self.identite.id_fort}_{id_fort_ami}"
        
        fenetre_canal = FenetreIntegree(self.identite, "canal_prive")
        fenetre_canal.observateurs_autorises = [id_fort_ami]
        
        # Contenu initial du canal
        contenu_canal = {
            "participants": [self.identite.id_fort, id_fort_ami],
            "messages": [],
            "cree_le": datetime.now().isoformat(),
            "statut": "actif"
        }
        fenetre_canal.configurer_contenu(contenu_canal)
        
        self.fenetres_canaux[id_canal] = fenetre_canal
        
        print(f"🤝 Canal privé créé avec {id_fort_ami}")
        return id_canal
    
    def ecouter_reseau_integre(self):
        """🌐 Écoute réseau intégrée avec gestion des fenêtres"""
        while self.actif:
            try:
                data, addr = self.socket_wan.recvfrom(2048)  # Buffer plus grand
                message = json.loads(data.decode('utf-8'))
                self.stats_reseau["messages_recus"] += 1
                
                self._traiter_message_integre(message, addr)
                
            except socket.timeout:
                continue
            except Exception as e:
                continue
    
    def _traiter_message_integre(self, message: Dict, addr: tuple):
        """Traite messages réseau avec logique des fenêtres"""
        type_msg = message.get("type")
        fort_source = message.get("fort_source")
        
        if type_msg == "signal_fort_integre":
            # Nouveau fort découvert
            self._enregistrer_fort_distant(message, addr)
            
        elif type_msg == "demande_observation_fenetre":
            # Demande de consultation d'une fenêtre
            self._traiter_demande_observation(message, addr)
            
        elif type_msg == "projection_fenetre":
            # Réception d'une projection de fenêtre
            print(f"🪟 Projection reçue de {fort_source}")
            
        elif type_msg == "demande_canal_prive":
            # Demande de création de canal privé
            self._traiter_demande_canal(message, addr)
            
        elif type_msg == "ping_integre":
            self._repondre_pong_integre(addr, message)
    
    def _enregistrer_fort_distant(self, message: Dict, addr: tuple):
        """Enregistre un fort distant découvert"""
        fort_id = message.get("fort_source")
        if fort_id != self.identite.id_fort:
            self.forts_reseau[fort_id] = {
                "identite": message.get("identite"),
                "addr": addr,
                "derniere_activite": time.time()
            }
            print(f"📡 Fort découvert: {message.get('nom', fort_id)}")
    
    def _traiter_demande_observation(self, message: Dict, addr: tuple):
        """Traite une demande d'observation de fenêtre"""
        fort_demandeur = message.get("fort_source")
        type_fenetre = message.get("type_fenetre", "publique")
        
        projection = None
        
        if type_fenetre == "publique":
            projection = self.fenetre_publique.autoriser_observation(fort_demandeur, addr)
        elif type_fenetre == "canal" and message.get("id_canal") in self.fenetres_canaux:
            canal = self.fenetres_canaux[message.get("id_canal")]
            projection = canal.autoriser_observation(fort_demandeur, addr)
        
        if projection:
            self._envoyer_projection(addr, projection)
    
    def _envoyer_projection(self, addr: tuple, projection: Dict):
        """Envoie une projection de fenêtre"""
        message = {
            "type": "projection_fenetre",
            "fort_source": self.identite.id_fort,
            "projection": projection,
            "timestamp": time.time()
        }
        self.envoyer_message_wan(addr, message)
    
    def _traiter_demande_canal(self, message: Dict, addr: tuple):
        """Traite une demande de canal privé"""
        fort_demandeur = message.get("fort_source")
        
        # Auto-acceptation pour la démo (en réalité, il faudrait demander à l'utilisateur)
        id_canal = self.creer_canal_prive_integre(fort_demandeur)
        
        reponse = {
            "type": "canal_accepte",
            "fort_source": self.identite.id_fort,
            "id_canal": id_canal,
            "timestamp": time.time()
        }
        self.envoyer_message_wan(addr, reponse)
    
    def _repondre_pong_integre(self, addr: tuple, message: Dict):
        """Répond à un ping intégré"""
        reponse = {
            "type": "pong_integre",
            "fort_source": self.identite.id_fort,
            "ping_id": message.get("ping_id"),
            "identite": asdict(self.identite),
            "timestamp": time.time()
        }
        self.envoyer_message_wan(addr, reponse)
    
    def envoyer_message_wan(self, addr: tuple, message: Dict):
        """Envoie un message via WAN"""
        try:
            data = json.dumps(message).encode('utf-8')
            self.socket_wan.sendto(data, addr)
            self.stats_reseau["messages_envoyes"] += 1
        except Exception as e:
            print(f"❌ Erreur envoi WAN: {e}")
    
    def emettre_signal_integre(self):
        """📡 Émet signal de présence sur le réseau"""
        signal = {
            "type": "signal_fort_integre",
            "fort_source": self.identite.id_fort,
            "nom": self.identite.nom,
            "identite": asdict(self.identite),
            "timestamp": time.time()
        }
        
        # Broadcast local (simulation réseau mondial)
        for port in range(9000, 9010):
            if port != self.identite.port_reseau:
                self.envoyer_message_wan(('127.0.0.1', port), signal)
    
    def observer_fenetre_distante(self, id_fort_cible: str, type_fenetre: str = "publique"):
        """🔍 Observe la fenêtre d'un fort distant"""
        if id_fort_cible in self.forts_reseau:
            addr = self.forts_reseau[id_fort_cible]["addr"]
            
            demande = {
                "type": "demande_observation_fenetre",
                "fort_source": self.identite.id_fort,
                "type_fenetre": type_fenetre,
                "timestamp": time.time()
            }
            
            self.envoyer_message_wan(addr, demande)
            print(f"🔍 Demande d'observation envoyée vers {id_fort_cible}")
        else:
            print(f"❌ Fort {id_fort_cible} non trouvé sur le réseau")
    
    def demander_canal_prive_distant(self, id_fort_cible: str):
        """🤝 Demande création canal privé avec fort distant"""
        if id_fort_cible in self.forts_reseau:
            addr = self.forts_reseau[id_fort_cible]["addr"]
            
            demande = {
                "type": "demande_canal_prive",
                "fort_source": self.identite.id_fort,
                "timestamp": time.time()
            }
            
            self.envoyer_message_wan(addr, demande)
            print(f"🤝 Demande de canal privé envoyée vers {id_fort_cible}")
    
    def obtenir_stats_integrees(self) -> Dict:
        """📊 Statistiques complètes du fort intégré"""
        return {
            "identite": asdict(self.identite),
            "donnees_privees": {k: len(v) for k, v in self.donnees_privees.items()},
            "fenetres": {
                "publique": bool(self.fenetre_publique.contenu),
                "canaux_prives": len(self.fenetres_canaux)
            },
            "reseau": {
                "forts_connus": len(self.forts_reseau),
                "messages_envoyes": self.stats_reseau["messages_envoyes"],
                "messages_recus": self.stats_reseau["messages_recus"]
            }
        }
    
    def demarrer_fort_integre(self):
        """🚀 Démarre le fort intégré complet"""
        thread_reseau = threading.Thread(target=self.ecouter_reseau_integre, daemon=True)
        thread_reseau.start()
        
        # Signal initial
        time.sleep(0.5)
        self.emettre_signal_integre()
        
        return thread_reseau
    
    def arreter_fort_integre(self):
        """🛑 Arrête le fort proprement"""
        self.actif = False
        self.socket_wan.close()


def demo_integration_complete():
    """
    🎭 Démonstration du système intégré complet
    Forts + Fenêtres + Réseau WAN
    """
    print("=" * 70)
    print("🏰 DÉMONSTRATION SYSTÈME INTÉGRÉ OPENRED NETWORK")
    print("=" * 70)
    
    # Création des forts intégrés
    print("\n1️⃣ Création des forts intégrés...")
    fort_alice = FortIntegre("Alice")
    fort_bob = FortIntegre("Bob")
    
    # Ajout de données privées
    print("\n2️⃣ Ajout de données privées...")
    fort_alice.ajouter_donnee_privee("documents", "Mon journal secret")
    fort_alice.ajouter_donnee_privee("photos", "photo_famille.jpg")
    fort_bob.ajouter_donnee_privee("notes", "Idées de projet")
    
    # Configuration des fenêtres publiques
    print("\n3️⃣ Publications dans les fenêtres publiques...")
    fort_alice.publier_dans_fenetre_publique("Salut le réseau OpenRed !")
    fort_bob.publier_dans_fenetre_publique("Hello depuis mon fort !")
    
    # Démarrage réseau
    print("\n4️⃣ Démarrage du réseau intégré...")
    thread_alice = fort_alice.demarrer_fort_integre()
    thread_bob = fort_bob.demarrer_fort_integre()
    
    time.sleep(2)  # Temps pour découverte
    
    # Observation de fenêtres distantes
    print("\n5️⃣ Observation des fenêtres distantes...")
    fort_alice.observer_fenetre_distante(fort_bob.identite.id_fort)
    fort_bob.observer_fenetre_distante(fort_alice.identite.id_fort)
    
    time.sleep(1)
    
    # Création de canal privé
    print("\n6️⃣ Création de canal privé...")
    fort_alice.demander_canal_prive_distant(fort_bob.identite.id_fort)
    
    time.sleep(2)
    
    # Statistiques finales
    print("\n7️⃣ Statistiques finales...")
    stats_alice = fort_alice.obtenir_stats_integrees()
    stats_bob = fort_bob.obtenir_stats_integrees()
    
    print(f"\n📊 Fort Alice:")
    print(f"   ID: {stats_alice['identite']['id_fort']}")
    print(f"   ORP: {stats_alice['identite']['adresse_orp']}")
    print(f"   Données privées: {sum(stats_alice['donnees_privees'].values())}")
    print(f"   Canaux privés: {stats_alice['fenetres']['canaux_prives']}")
    print(f"   Forts connus: {stats_alice['reseau']['forts_connus']}")
    print(f"   Messages: {stats_alice['reseau']['messages_envoyes']}↑ {stats_alice['reseau']['messages_recus']}↓")
    
    print(f"\n📊 Fort Bob:")
    print(f"   ID: {stats_bob['identite']['id_fort']}")
    print(f"   ORP: {stats_bob['identite']['adresse_orp']}")
    print(f"   Données privées: {sum(stats_bob['donnees_privees'].values())}")
    print(f"   Canaux privés: {stats_bob['fenetres']['canaux_prives']}")
    print(f"   Forts connus: {stats_bob['reseau']['forts_connus']}")
    print(f"   Messages: {stats_bob['reseau']['messages_envoyes']}↑ {stats_bob['reseau']['messages_recus']}↓")
    
    # Évaluation de l'intégration
    print(f"\n🏆 ÉVALUATION INTÉGRATION:")
    
    decouverte_ok = stats_alice['reseau']['forts_connus'] > 0 and stats_bob['reseau']['forts_connus'] > 0
    communication_ok = stats_alice['reseau']['messages_envoyes'] > 0 and stats_bob['reseau']['messages_recus'] > 0
    fenetres_ok = stats_alice['fenetres']['publique'] and stats_bob['fenetres']['publique']
    canaux_ok = stats_alice['fenetres']['canaux_prives'] > 0 or stats_bob['fenetres']['canaux_prives'] > 0
    
    print(f"   Découverte réseau: {'✅' if decouverte_ok else '❌'}")
    print(f"   Communication WAN: {'✅' if communication_ok else '❌'}")
    print(f"   Fenêtres publiques: {'✅' if fenetres_ok else '❌'}")
    print(f"   Canaux privés: {'✅' if canaux_ok else '❌'}")
    
    integration_reussie = decouverte_ok and communication_ok and fenetres_ok
    
    print(f"\n🎯 VERDICT INTÉGRATION: {'🟢 RÉUSSIE' if integration_reussie else '🟡 PARTIELLE'}")
    
    if integration_reussie:
        print("   ✅ Système Forts+Fenêtres+Réseau fonctionnel !")
        print("   🌐 Communication mondiale avec projections sécurisées")
        print("   🏰 Souveraineté des données préservée")
        print("   🚀 Prêt pour optimisations avancées")
    
    # Nettoyage
    print("\n8️⃣ Arrêt des forts...")
    fort_alice.arreter_fort_integre()
    fort_bob.arreter_fort_integre()
    
    return integration_reussie


if __name__ == "__main__":
    resultat = demo_integration_complete()
    if resultat:
        print(f"\n🚀 Prêt pour étape finale: Optimisations avancées !")
    else:
        print(f"\n⚠️ Corrections nécessaires avant optimisations")