#!/usr/bin/env python3
"""
🗺️ OpenRed Network - Système de Cartographie et Découverte
Cartographie réseau + Reconnaissance forts + Routes de communication
"""

import socket
import json
import time
import threading
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
import math


@dataclass
class PositionFort:
    """Position logique d'un fort sur la carte réseau"""
    x: float
    y: float
    zone: str = "principale"


@dataclass
class FortSurCarte:
    """Représentation d'un fort sur la carte réseau"""
    id_fort: str
    nom: str
    adresse_orp: str
    position: PositionFort
    addr_reseau: Tuple[str, int]
    derniere_activite: float
    statut: str = "en_ligne"  # en_ligne, hors_ligne, suspect
    routes_directes: List[str] = None
    
    def __post_init__(self):
        if self.routes_directes is None:
            self.routes_directes = []


class CarteReseau:
    """
    🗺️ Carte complète du réseau OpenRed
    Maintient la topologie et les routes entre forts
    """
    
    def __init__(self):
        self.forts: Dict[str, FortSurCarte] = {}
        self.routes: Dict[str, Dict[str, float]] = {}  # id_fort -> {destination: distance}
        self.zones = {
            "principale": {"x_min": 0, "x_max": 1000, "y_min": 0, "y_max": 1000}
        }
        self.derniere_mise_a_jour = time.time()
        self.mutex = threading.Lock()
    
    def ajouter_fort(self, fort: FortSurCarte) -> bool:
        """Ajoute un fort à la carte"""
        with self.mutex:
            if fort.id_fort not in self.forts:
                self.forts[fort.id_fort] = fort
                self._calculer_position_logique(fort)
                self._mettre_a_jour_routes(fort.id_fort)
                self.derniere_mise_a_jour = time.time()
                print(f"🗺️ Fort {fort.nom} ajouté à la carte ({fort.position.x:.0f},{fort.position.y:.0f})")
                return True
            else:
                # Mise à jour fort existant
                self.forts[fort.id_fort].derniere_activite = fort.derniere_activite
                self.forts[fort.id_fort].statut = fort.statut
                return False
    
    def _calculer_position_logique(self, fort: FortSurCarte):
        """Calcule une position logique basée sur l'ID du fort"""
        # Hash de l'ID pour position déterministe mais distribuée
        hash_obj = hashlib.md5(fort.id_fort.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        zone = self.zones["principale"]
        x = (hash_int % 1000000) / 1000000 * (zone["x_max"] - zone["x_min"]) + zone["x_min"]
        y = ((hash_int // 1000000) % 1000000) / 1000000 * (zone["y_max"] - zone["y_min"]) + zone["y_min"]
        
        fort.position = PositionFort(x, y, "principale")
    
    def _mettre_a_jour_routes(self, id_fort: str):
        """Met à jour les routes depuis/vers ce fort"""
        if id_fort not in self.routes:
            self.routes[id_fort] = {}
        
        fort_source = self.forts[id_fort]
        
        # Calculer distances vers tous les autres forts
        for autre_id, autre_fort in self.forts.items():
            if autre_id != id_fort:
                distance = self._calculer_distance(fort_source.position, autre_fort.position)
                self.routes[id_fort][autre_id] = distance
                
                # Route bidirectionnelle
                if autre_id not in self.routes:
                    self.routes[autre_id] = {}
                self.routes[autre_id][id_fort] = distance
    
    def _calculer_distance(self, pos1: PositionFort, pos2: PositionFort) -> float:
        """Calcule la distance logique entre deux positions"""
        return math.sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2)
    
    def obtenir_forts_proches(self, id_fort: str, rayon: float = 200) -> List[str]:
        """Retourne les forts dans un rayon donné"""
        if id_fort not in self.forts:
            return []
        
        forts_proches = []
        fort_centre = self.forts[id_fort]
        
        for autre_id, autre_fort in self.forts.items():
            if autre_id != id_fort:
                distance = self._calculer_distance(fort_centre.position, autre_fort.position)
                if distance <= rayon and autre_fort.statut == "en_ligne":
                    forts_proches.append(autre_id)
        
        return forts_proches
    
    def trouver_route_optimale(self, source: str, destination: str) -> Optional[List[str]]:
        """Trouve la route optimale entre deux forts (Dijkstra simplifié)"""
        if source not in self.forts or destination not in self.forts:
            return None
        
        if source == destination:
            return [source]
        
        # Pour simplicité, route directe si distance acceptable
        if source in self.routes and destination in self.routes[source]:
            distance = self.routes[source][destination]
            if distance < 500:  # Distance directe acceptable
                return [source, destination]
        
        # Sinon, chercher via un relais (algorithme simple)
        meilleure_route = None
        meilleure_distance = float('inf')
        
        for relais_id in self.forts.keys():
            if relais_id != source and relais_id != destination:
                if (source in self.routes and relais_id in self.routes[source] and
                    relais_id in self.routes and destination in self.routes[relais_id]):
                    
                    distance_totale = self.routes[source][relais_id] + self.routes[relais_id][destination]
                    if distance_totale < meilleure_distance:
                        meilleure_distance = distance_totale
                        meilleure_route = [source, relais_id, destination]
        
        return meilleure_route
    
    def nettoyer_forts_inactifs(self, timeout: float = 30.0):
        """Supprime les forts inactifs de la carte"""
        maintenant = time.time()
        forts_a_supprimer = []
        
        with self.mutex:
            for id_fort, fort in self.forts.items():
                if maintenant - fort.derniere_activite > timeout:
                    forts_a_supprimer.append(id_fort)
            
            for id_fort in forts_a_supprimer:
                del self.forts[id_fort]
                if id_fort in self.routes:
                    del self.routes[id_fort]
                # Nettoyer références dans autres routes
                for routes_fort in self.routes.values():
                    if id_fort in routes_fort:
                        del routes_fort[id_fort]
                
                print(f"🗺️ Fort {id_fort} supprimé de la carte (inactif)")
    
    def exporter_carte(self) -> Dict:
        """Exporte l'état actuel de la carte"""
        with self.mutex:
            return {
                "timestamp": self.derniere_mise_a_jour,
                "nombre_forts": len(self.forts),
                "forts": {id_fort: asdict(fort) for id_fort, fort in self.forts.items()},
                "routes": self.routes.copy(),
                "zones": self.zones.copy()
            }


class RadarFort:
    """
    📡 Système radar pour scanner et cartographier le réseau
    Chaque fort utilise son radar pour découvrir les autres
    """
    
    def __init__(self, id_fort: str, socket_reseau: socket.socket):
        self.id_fort = id_fort
        self.socket = socket_reseau
        self.carte_locale = CarteReseau()
        self.derniere_exploration = 0
        self.portee_radar = 300  # Portée du radar
        self.actif = True
        
        # Statistiques radar
        self.stats = {
            "scans_effectues": 0,
            "forts_decouverts": 0,
            "signaux_emis": 0,
            "reponses_recues": 0
        }
    
    def emettre_impulsion_radar(self, cibles: List[Tuple[str, int]] = None):
        """
        📡 Émet une impulsion radar pour scanner le réseau
        Principe: Signal qui révèle les forts ET cartographie en même temps
        """
        impulsion = {
            "type": "impulsion_radar",
            "fort_emetteur": self.id_fort,
            "timestamp": time.time(),
            "portee": self.portee_radar,
            "demande_reponse": True,
            "carte_partielle": self._generer_carte_partielle()
        }
        
        # Cibles par défaut (broadcast local)
        if cibles is None:
            cibles = [('127.0.0.1', port) for port in range(9000, 9020)]
        
        for addr in cibles:
            try:
                data = json.dumps(impulsion).encode('utf-8')
                self.socket.sendto(data, addr)
                self.stats["signaux_emis"] += 1
            except:
                pass
        
        self.stats["scans_effectues"] += 1
        self.derniere_exploration = time.time()
        print(f"📡 Impulsion radar émise par {self.id_fort} (portée: {self.portee_radar})")
    
    def _generer_carte_partielle(self) -> Dict:
        """Génère une carte partielle à partager"""
        carte_complete = self.carte_locale.exporter_carte()
        
        # Partager seulement les forts proches
        forts_proches = self.carte_locale.obtenir_forts_proches(self.id_fort, self.portee_radar)
        
        carte_partielle = {
            "forts_visibles": len(forts_proches),
            "zone_couverte": f"rayon_{self.portee_radar}",
            "derniere_maj": carte_complete["timestamp"]
        }
        
        return carte_partielle
    
    def traiter_impulsion_radar(self, impulsion: Dict, addr_source: tuple) -> bool:
        """
        Traite une impulsion radar reçue et répond avec ses informations
        """
        fort_emetteur = impulsion.get("fort_emetteur")
        
        if fort_emetteur == self.id_fort:
            return False  # Ignore sa propre impulsion
        
        # Créer réponse avec informations du fort
        reponse = {
            "type": "reponse_radar",
            "fort_repondeur": self.id_fort,
            "fort_destinataire": fort_emetteur,
            "timestamp": time.time(),
            "position_estimee": self._estimer_position(),
            "forts_visibles": len(self.carte_locale.forts),
            "statut": "en_ligne"
        }
        
        # Envoyer réponse
        try:
            data = json.dumps(reponse).encode('utf-8')
            self.socket.sendto(data, addr_source)
            print(f"📡 Réponse radar envoyée à {fort_emetteur}")
            return True
        except:
            return False
    
    def traiter_reponse_radar(self, reponse: Dict, addr_source: tuple):
        """Traite une réponse radar et met à jour la carte"""
        fort_repondeur = reponse.get("fort_repondeur")
        
        if fort_repondeur != self.id_fort:  # Pas sa propre réponse
            # Créer entrée fort pour la carte
            nouveau_fort = FortSurCarte(
                id_fort=fort_repondeur,
                nom=f"Fort_{fort_repondeur[:8]}",
                adresse_orp=f"orp://{fort_repondeur[:8]}.openred.network",
                position=PositionFort(0, 0),  # Sera calculée automatiquement
                addr_reseau=addr_source,
                derniere_activite=time.time(),
                statut="en_ligne"
            )
            
            est_nouveau = self.carte_locale.ajouter_fort(nouveau_fort)
            if est_nouveau:
                self.stats["forts_decouverts"] += 1
                print(f"🗺️ Nouveau fort découvert: {fort_repondeur}")
            
            self.stats["reponses_recues"] += 1
    
    def _estimer_position(self) -> Dict:
        """Estime la position du fort (simplifié)"""
        if self.id_fort in self.carte_locale.forts:
            pos = self.carte_locale.forts[self.id_fort].position
            return {"x": pos.x, "y": pos.y, "zone": pos.zone}
        return {"x": 0, "y": 0, "zone": "inconnue"}
    
    def exploration_continue(self, intervalle: float = 5.0):
        """Lance une exploration continue du réseau"""
        while self.actif:
            self.emettre_impulsion_radar()
            self.carte_locale.nettoyer_forts_inactifs()
            time.sleep(intervalle)
    
    def obtenir_statistiques_radar(self) -> Dict:
        """Retourne les statistiques du radar"""
        return {
            "fort": self.id_fort,
            "stats_radar": self.stats.copy(),
            "carte_locale": {
                "forts_connus": len(self.carte_locale.forts),
                "routes_calculees": len(self.carte_locale.routes),
                "derniere_maj": self.carte_locale.derniere_mise_a_jour
            }
        }


class FortAvecRadar:
    """
    🏰 Fort équipé d'un système radar pour cartographie réseau
    Combine fort basique + radar + cartographie
    """
    
    def __init__(self, nom: str, port: int = 0):
        self.nom = nom
        self.id_fort = f"{nom}_{uuid.uuid4().hex[:8]}"
        
        # Socket réseau
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', port))
        self.port = self.socket.getsockname()[1]
        self.socket.settimeout(0.5)
        
        # Système radar
        self.radar = RadarFort(self.id_fort, self.socket)
        
        # État
        self.actif = True
        self.stats = {"messages_traites": 0, "erreurs": 0}
        
        # Ajouter ce fort à sa propre carte
        fort_local = FortSurCarte(
            id_fort=self.id_fort,
            nom=self.nom,
            adresse_orp=f"orp://{nom.lower()}.openred.network",
            position=PositionFort(0, 0),
            addr_reseau=('127.0.0.1', self.port),
            derniere_activite=time.time(),
            statut="en_ligne"
        )
        self.radar.carte_locale.ajouter_fort(fort_local)
        
        print(f"🏰 Fort {nom} avec radar créé sur port {self.port}")
    
    def ecouter_reseau(self):
        """Écoute réseau avec traitement des messages radar"""
        while self.actif:
            try:
                data, addr = self.socket.recvfrom(2048)
                message = json.loads(data.decode('utf-8'))
                self.stats["messages_traites"] += 1
                
                type_msg = message.get("type")
                
                if type_msg == "impulsion_radar":
                    self.radar.traiter_impulsion_radar(message, addr)
                elif type_msg == "reponse_radar":
                    self.radar.traiter_reponse_radar(message, addr)
                elif type_msg == "demande_carte":
                    self._envoyer_carte(addr)
                
            except socket.timeout:
                continue
            except Exception as e:
                self.stats["erreurs"] += 1
                continue
    
    def _envoyer_carte(self, addr: tuple):
        """Envoie l'état de la carte locale"""
        carte = self.radar.carte_locale.exporter_carte()
        message = {
            "type": "carte_reseau",
            "fort_source": self.id_fort,
            "carte": carte,
            "timestamp": time.time()
        }
        
        try:
            data = json.dumps(message).encode('utf-8')
            self.socket.sendto(data, addr)
        except:
            pass
    
    def demarrer_exploration(self):
        """Démarre l'exploration radar en arrière-plan"""
        thread_ecoute = threading.Thread(target=self.ecouter_reseau, daemon=True)
        thread_radar = threading.Thread(target=self.radar.exploration_continue, daemon=True)
        
        thread_ecoute.start()
        thread_radar.start()
        
        return thread_ecoute, thread_radar
    
    def obtenir_vue_reseau(self) -> Dict:
        """Obtient une vue complète du réseau connu"""
        return {
            "fort": {
                "id": self.id_fort,
                "nom": self.nom,
                "port": self.port,
                "stats": self.stats
            },
            "radar": self.radar.obtenir_statistiques_radar(),
            "carte": self.radar.carte_locale.exporter_carte()
        }
    
    def trouver_route_vers(self, id_fort_cible: str) -> Optional[List[str]]:
        """Trouve une route vers un fort cible"""
        return self.radar.carte_locale.trouver_route_optimale(self.id_fort, id_fort_cible)
    
    def arreter(self):
        """Arrête le fort et son radar"""
        self.actif = False
        self.radar.actif = False
        self.socket.close()


def demo_cartographie_reseau():
    """
    🎭 Démonstration du système de cartographie réseau
    """
    print("=" * 60)
    print("🗺️ DÉMONSTRATION CARTOGRAPHIE RÉSEAU OPENRED")
    print("=" * 60)
    
    # Création des forts avec radar
    print("\n1️⃣ Création des forts avec radar...")
    forts = [
        FortAvecRadar("Alpha", 9001),
        FortAvecRadar("Beta", 9002), 
        FortAvecRadar("Gamma", 9003),
        FortAvecRadar("Delta", 9004)
    ]
    
    # Démarrage exploration
    print("\n2️⃣ Démarrage exploration radar...")
    threads = []
    for fort in forts:
        t_ecoute, t_radar = fort.demarrer_exploration()
        threads.extend([t_ecoute, t_radar])
    
    # Laisser le temps pour la découverte
    print("\n3️⃣ Exploration en cours...")
    for i in range(15):
        time.sleep(1)
        print(f"   Scan {i+1}/15...", end='\r')
    print("\n   ✅ Exploration terminée")
    
    # Analyse des résultats
    print("\n4️⃣ Analyse de la cartographie...")
    
    for fort in forts:
        vue = fort.obtenir_vue_reseau()
        
        print(f"\n📊 Fort {vue['fort']['nom']} ({vue['fort']['id']}):")
        print(f"   Messages traités: {vue['fort']['stats']['messages_traites']}")
        print(f"   Radar - Scans: {vue['radar']['stats_radar']['scans_effectues']}")
        print(f"   Radar - Découvertes: {vue['radar']['stats_radar']['forts_decouverts']}")
        print(f"   Carte - Forts connus: {vue['radar']['carte_locale']['forts_connus']}")
        
        # Test de routage
        autres_forts = [f.id_fort for f in forts if f.id_fort != fort.id_fort]
        if autres_forts:
            cible = autres_forts[0]
            route = fort.trouver_route_vers(cible)
            if route:
                print(f"   Route vers {cible[:8]}: {' -> '.join([r[:8] for r in route])}")
            else:
                print(f"   Route vers {cible[:8]}: Non trouvée")
    
    # Évaluation de la cartographie
    print(f"\n🏆 ÉVALUATION CARTOGRAPHIE:")
    
    total_decouvertes = sum(fort.radar.stats["forts_decouverts"] for fort in forts)
    total_forts = len(forts)
    taux_decouverte = total_decouvertes / (total_forts * (total_forts - 1)) * 100 if total_forts > 1 else 0
    
    communication_ok = all(fort.radar.stats["reponses_recues"] > 0 for fort in forts)
    cartographie_ok = all(len(fort.radar.carte_locale.forts) > 1 for fort in forts)
    routes_ok = any(fort.trouver_route_vers(autre.id_fort) for fort in forts for autre in forts if fort != autre)
    
    print(f"   Taux de découverte: {taux_decouverte:.1f}%")
    print(f"   Communication radar: {'✅' if communication_ok else '❌'}")
    print(f"   Cartographie active: {'✅' if cartographie_ok else '❌'}")
    print(f"   Routes calculées: {'✅' if routes_ok else '❌'}")
    
    cartographie_reussie = communication_ok and cartographie_ok and taux_decouverte > 50
    
    print(f"\n🎯 VERDICT CARTOGRAPHIE: {'🟢 RÉUSSIE' if cartographie_reussie else '🟡 PARTIELLE'}")
    
    if cartographie_reussie:
        print("   ✅ Système de cartographie fonctionnel !")
        print("   🗺️ Forts se découvrent et calculent routes")
        print("   📡 Radar efficace pour exploration réseau")
        print("   🚀 Prêt pour intégration avec fenêtres")
    
    # Nettoyage
    print(f"\n5️⃣ Arrêt des forts...")
    for fort in forts:
        fort.arreter()
    
    return cartographie_reussie


if __name__ == "__main__":
    resultat = demo_cartographie_reseau()
    if resultat:
        print(f"\n🚀 Système de cartographie validé ! Intégration avec fenêtres possible !")
    else:
        print(f"\n⚠️ Optimisations de cartographie nécessaires")