#!/usr/bin/env python3
"""
🗺️ OpenRed Network - Module Cartographie: Carte Réseau
Cartographie complète du réseau OpenRed avec positions et routes
"""

import socket
import json
import time
import threading
import hashlib
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict


@dataclass
class PositionFort:
    """Position logique d'un fort sur la carte réseau"""
    x: float
    y: float
    zone: str = "principale"
    
    def distance_vers(self, autre: 'PositionFort') -> float:
        """Calcule la distance vers une autre position"""
        return math.sqrt((self.x - autre.x)**2 + (self.y - autre.y)**2)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PositionFort':
        return cls(**data)


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
    distance_ping: float = 0.0  # Latence réseau en ms
    
    def __post_init__(self):
        if self.routes_directes is None:
            self.routes_directes = []
    
    def est_actif(self, timeout: float = 300) -> bool:
        """Vérifie si le fort est considéré comme actif"""
        return time.time() - self.derniere_activite < timeout
    
    def mettre_a_jour_activite(self):
        """Met à jour le timestamp d'activité"""
        self.derniere_activite = time.time()
        if self.statut == "hors_ligne":
            self.statut = "en_ligne"
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['position'] = self.position.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FortSurCarte':
        position_data = data.pop('position')
        position = PositionFort.from_dict(position_data)
        return cls(position=position, **data)


class CarteReseau:
    """
    🗺️ Carte complète du réseau OpenRed
    Maintient la topologie et les routes entre forts
    """
    
    def __init__(self):
        self.forts: Dict[str, FortSurCarte] = {}
        self.routes: Dict[str, Dict[str, float]] = {}  # id_fort -> {destination: distance}
        self.zones = {
            "principale": {"x_min": 0, "x_max": 1000, "y_min": 0, "y_max": 1000},
            "peripherie": {"x_min": 1000, "x_max": 2000, "y_min": 0, "y_max": 1000}
        }
        self.derniere_mise_a_jour = time.time()
        self.mutex = threading.Lock()
        
        # Statistiques
        self.stats = {
            "forts_total": 0,
            "forts_actifs": 0,
            "routes_calculees": 0,
            "derniere_decouverte": 0
        }
    
    def ajouter_fort(self, fort: FortSurCarte) -> bool:
        """Ajoute un fort à la carte"""
        with self.mutex:
            nouveau_fort = fort.id_fort not in self.forts
            
            if nouveau_fort:
                self.forts[fort.id_fort] = fort
                self._calculer_position_logique(fort)
                self._mettre_a_jour_routes(fort.id_fort)
                self.stats["forts_total"] += 1
                self.stats["derniere_decouverte"] = time.time()
                print(f"🗺️ Nouveau fort ajouté: {fort.nom} ({fort.position.x:.0f},{fort.position.y:.0f})")
            else:
                # Mise à jour fort existant
                fort_existant = self.forts[fort.id_fort]
                fort_existant.derniere_activite = fort.derniere_activite
                fort_existant.statut = fort.statut
                fort_existant.distance_ping = fort.distance_ping
                fort_existant.addr_reseau = fort.addr_reseau
            
            self.derniere_mise_a_jour = time.time()
            self._mettre_a_jour_statistiques()
            
            return nouveau_fort
    
    def _calculer_position_logique(self, fort: FortSurCarte):
        """Calcule une position logique basée sur l'ID du fort"""
        # Hash de l'ID pour position déterministe mais distribuée
        hash_obj = hashlib.md5(fort.id_fort.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Choisir la zone (90% principale, 10% périphérie)
        zone_nom = "principale" if (hash_int % 10) < 9 else "peripherie"
        zone = self.zones[zone_nom]
        
        # Position dans la zone
        x = (hash_int % 1000000) / 1000000 * (zone["x_max"] - zone["x_min"]) + zone["x_min"]
        y = ((hash_int // 1000000) % 1000000) / 1000000 * (zone["y_max"] - zone["y_min"]) + zone["y_min"]
        
        fort.position = PositionFort(x, y, zone_nom)
    
    def _mettre_a_jour_routes(self, id_fort: str):
        """Met à jour les routes depuis/vers ce fort"""
        if id_fort not in self.routes:
            self.routes[id_fort] = {}
        
        fort_source = self.forts[id_fort]
        
        # Calculer distances vers tous les autres forts
        for autre_id, autre_fort in self.forts.items():
            if autre_id != id_fort:
                distance = fort_source.position.distance_vers(autre_fort.position)
                self.routes[id_fort][autre_id] = distance
                
                # Route bidirectionnelle
                if autre_id not in self.routes:
                    self.routes[autre_id] = {}
                self.routes[autre_id][id_fort] = distance
        
        self.stats["routes_calculees"] = sum(len(routes) for routes in self.routes.values())
    
    def _mettre_a_jour_statistiques(self):
        """Met à jour les statistiques de la carte"""
        maintenant = time.time()
        self.stats["forts_actifs"] = sum(
            1 for fort in self.forts.values() 
            if fort.est_actif() and fort.statut == "en_ligne"
        )
    
    def obtenir_fort(self, id_fort: str) -> Optional[FortSurCarte]:
        """Récupère un fort par son ID"""
        return self.forts.get(id_fort)
    
    def obtenir_forts_proches(self, id_fort: str, distance_max: float = 200) -> List[FortSurCarte]:
        """Récupère les forts proches d'un fort donné"""
        fort_ref = self.forts.get(id_fort)
        if not fort_ref:
            return []
        
        forts_proches = []
        for autre_id, autre_fort in self.forts.items():
            if autre_id != id_fort:
                distance = fort_ref.position.distance_vers(autre_fort.position)
                if distance <= distance_max:
                    forts_proches.append(autre_fort)
        
        # Trier par distance
        forts_proches.sort(key=lambda f: fort_ref.position.distance_vers(f.position))
        return forts_proches
    
    def obtenir_route_optimale(self, id_source: str, id_destination: str) -> Optional[List[str]]:
        """Calcule la route optimale entre deux forts"""
        if id_source not in self.routes or id_destination not in self.routes[id_source]:
            return None
        
        # Pour l'instant, route directe uniquement
        # TODO: Implémenter algorithme de routage (Dijkstra)
        return [id_source, id_destination]
    
    def nettoyer_forts_inactifs(self, timeout: float = 600):
        """Nettoie les forts inactifs de la carte"""
        with self.mutex:
            forts_a_supprimer = []
            
            for id_fort, fort in self.forts.items():
                if not fort.est_actif(timeout):
                    fort.statut = "hors_ligne"
                    if not fort.est_actif(timeout * 2):  # Double timeout pour suppression
                        forts_a_supprimer.append(id_fort)
            
            for id_fort in forts_a_supprimer:
                del self.forts[id_fort]
                if id_fort in self.routes:
                    del self.routes[id_fort]
                
                # Nettoyer les routes vers ce fort
                for routes in self.routes.values():
                    if id_fort in routes:
                        del routes[id_fort]
                
                self.stats["forts_total"] -= 1
                print(f"🧹 Fort inactif supprimé: {id_fort}")
    
    def obtenir_statistiques(self) -> Dict:
        """Obtient les statistiques de la carte"""
        self._mettre_a_jour_statistiques()
        
        return {
            "forts": {
                "total": self.stats["forts_total"],
                "actifs": self.stats["forts_actifs"],
                "hors_ligne": self.stats["forts_total"] - self.stats["forts_actifs"]
            },
            "routes": {
                "total": self.stats["routes_calculees"],
                "moyenne_par_fort": self.stats["routes_calculees"] / max(1, self.stats["forts_total"])
            },
            "zones": {
                zone: len([f for f in self.forts.values() if f.position.zone == zone])
                for zone in self.zones.keys()
            },
            "derniere_mise_a_jour": self.derniere_mise_a_jour,
            "derniere_decouverte": self.stats["derniere_decouverte"]
        }
    
    def obtenir_vue_globale(self) -> Dict:
        """Obtient une vue globale de la carte pour affichage"""
        return {
            "forts": [
                {
                    "id": fort.id_fort,
                    "nom": fort.nom,
                    "position": fort.position.to_dict(),
                    "statut": fort.statut,
                    "ping": fort.distance_ping,
                    "derniere_activite": fort.derniere_activite
                }
                for fort in self.forts.values()
            ],
            "statistiques": self.obtenir_statistiques()
        }
    
    def sauvegarder_carte(self, fichier: str):
        """Sauvegarde la carte dans un fichier"""
        with self.mutex:
            data = {
                "forts": {id_fort: fort.to_dict() for id_fort, fort in self.forts.items()},
                "zones": self.zones,
                "statistiques": self.stats,
                "timestamp": time.time()
            }
            
            with open(fichier, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Carte sauvegardée: {fichier}")
    
    def charger_carte(self, fichier: str):
        """Charge la carte depuis un fichier"""
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with self.mutex:
                # Chargement des forts
                for id_fort, fort_data in data.get("forts", {}).items():
                    fort = FortSurCarte.from_dict(fort_data)
                    self.forts[id_fort] = fort
                
                # Reconstruction des routes
                for id_fort in self.forts.keys():
                    self._mettre_a_jour_routes(id_fort)
                
                # Chargement des zones et stats
                self.zones.update(data.get("zones", {}))
                self.stats.update(data.get("statistiques", {}))
            
            print(f"📂 Carte chargée: {fichier} ({len(self.forts)} forts)")
            
        except FileNotFoundError:
            print(f"📁 Fichier carte {fichier} non trouvé")
        except Exception as e:
            print(f"❌ Erreur chargement carte: {e}")
    
    def __len__(self):
        return len(self.forts)
    
    def __str__(self):
        return f"CarteReseau({len(self.forts)} forts, {self.stats['forts_actifs']} actifs)"