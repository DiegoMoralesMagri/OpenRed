#!/usr/bin/env python3
"""
🌐 OpenRed Network - Module Cartographie: Découverte Intégrée
Système intégré de découverte et cartographie automatique
"""

import time
import threading
from typing import Dict, List, Optional, Callable

from .carte import CarteReseau, FortSurCarte, PositionFort
from .radar import RadarFort


class DecouvreurReseau:
    """
    🌐 Découvreur de réseau intégré
    Combine radar et cartographie pour découverte automatique
    """
    
    def __init__(self, id_fort: str, nom_fort: str, port_ecoute: int = 0):
        self.id_fort = id_fort
        self.nom_fort = nom_fort
        
        # Composants principaux
        self.carte = CarteReseau()
        self.radar = RadarFort(id_fort, nom_fort, port_ecoute)
        
        # État de la découverte
        self.decouverte_active = False
        self.thread_integration = None
        
        # Statistiques
        self.stats_decouverte = {
            "debut": 0,
            "forts_decouverts": 0,
            "forts_integres": 0,
            "derniere_integration": 0
        }
        
        # Configuration callbacks radar
        self._configurer_callbacks_radar()
        
        print(f"🌐 Découvreur initialisé pour {self.nom_fort}")
    
    def _configurer_callbacks_radar(self):
        """Configure les callbacks du radar"""
        self.radar.ajouter_callback("fort_decouvert", self._callback_fort_decouvert)
        self.radar.ajouter_callback("fort_perdu", self._callback_fort_perdu)
    
    def _callback_fort_decouvert(self, fort_info: Dict):
        """Callback appelé quand un fort est découvert par le radar"""
        # Conversion en FortSurCarte pour la carte
        fort_sur_carte = FortSurCarte(
            id_fort=fort_info["id_fort"],
            nom=fort_info["nom_fort"],
            adresse_orp=f"orp://{fort_info['id_fort']}.openred",
            position=PositionFort(0, 0),  # Position calculée par la carte
            addr_reseau=(fort_info["addr_ip"], fort_info["port"]),
            derniere_activite=fort_info["derniere_activite"],
            statut="en_ligne"
        )
        
        # Ajout à la carte
        nouveau = self.carte.ajouter_fort(fort_sur_carte)
        
        if nouveau:
            self.stats_decouverte["forts_integres"] += 1
            self.stats_decouverte["derniere_integration"] = time.time()
            print(f"🗺️ Fort intégré à la carte: {fort_info['nom_fort']}")
    
    def _callback_fort_perdu(self, fort_info: Dict):
        """Callback appelé quand un fort n'est plus accessible"""
        print(f"📡 Fort perdu: {fort_info['nom_fort']}")
    
    def demarrer_decouverte(self):
        """Démarre la découverte automatique du réseau"""
        if self.decouverte_active:
            return
        
        self.decouverte_active = True
        self.stats_decouverte["debut"] = time.time()
        
        # Démarrage du radar
        self.radar.demarrer_radar()
        
        # Thread d'intégration et maintenance
        self.thread_integration = threading.Thread(target=self._boucle_integration, daemon=True)
        self.thread_integration.start()
        
        print(f"🌐 Découverte démarrée pour {self.nom_fort}")
    
    def arreter_decouverte(self):
        """Arrête la découverte"""
        if not self.decouverte_active:
            return
        
        self.decouverte_active = False
        
        # Arrêt du radar
        self.radar.arreter_radar()
        
        print(f"🌐 Découverte arrêtée pour {self.nom_fort}")
    
    def _boucle_integration(self):
        """Boucle d'intégration et maintenance"""
        while self.decouverte_active:
            try:
                # Nettoyage périodique
                self.radar.nettoyer_forts_inactifs()
                self.carte.nettoyer_forts_inactifs()
                
                # Mise à jour statistiques
                self.stats_decouverte["forts_decouverts"] = len(self.radar.forts_decouverts)
                
                time.sleep(30)  # Maintenance toutes les 30 secondes
                
            except Exception as e:
                print(f"❌ Erreur boucle intégration: {e}")
                time.sleep(10)
    
    def forcer_decouverte(self):
        """Force une nouvelle vague de découverte"""
        if self.radar.radar_actif:
            self.radar._envoyer_ping_broadcast()
            print("🔄 Découverte forcée déclenchée")
    
    def obtenir_carte_complete(self) -> Dict:
        """Obtient la carte complète du réseau"""
        return self.carte.obtenir_vue_globale()
    
    def obtenir_forts_proches(self, distance_max: float = 200) -> List[FortSurCarte]:
        """Obtient les forts proches de ce fort"""
        return self.carte.obtenir_forts_proches(self.id_fort, distance_max)
    
    def obtenir_statistiques_completes(self) -> Dict:
        """Obtient les statistiques complètes de découverte"""
        stats_radar = self.radar.obtenir_statistiques()
        stats_carte = self.carte.obtenir_statistiques()
        
        return {
            "decouverte": self.stats_decouverte,
            "radar": stats_radar,
            "carte": stats_carte,
            "resume": {
                "forts_visibles": len(self.radar.forts_decouverts),
                "forts_cartographies": len(self.carte.forts),
                "uptime": time.time() - self.stats_decouverte.get("debut", time.time()),
                "taux_integration": (
                    self.stats_decouverte["forts_integres"] / 
                    max(1, self.stats_decouverte["forts_decouverts"])
                ) * 100
            }
        }
    
    def rechercher_fort(self, critere: str) -> List[FortSurCarte]:
        """Recherche un fort par nom ou ID"""
        resultats = []
        
        for fort in self.carte.forts.values():
            if (critere.lower() in fort.nom.lower() or 
                critere.lower() in fort.id_fort.lower()):
                resultats.append(fort)
        
        return resultats
    
    def obtenir_route_vers(self, id_destination: str) -> Optional[List[str]]:
        """Obtient la route vers un fort de destination"""
        return self.carte.obtenir_route_optimale(self.id_fort, id_destination)
    
    def sauvegarder_decouverte(self, fichier: str):
        """Sauvegarde les données de découverte"""
        self.carte.sauvegarder_carte(fichier)
        print(f"💾 Découverte sauvegardée: {fichier}")
    
    def charger_decouverte(self, fichier: str):
        """Charge les données de découverte"""
        self.carte.charger_carte(fichier)
        print(f"📂 Découverte chargée: {fichier}")
    
    def obtenir_rapport_decouverte(self) -> str:
        """Génère un rapport textuel de découverte"""
        stats = self.obtenir_statistiques_completes()
        
        rapport = f"""
🌐 RAPPORT DE DÉCOUVERTE - {self.nom_fort}
{'=' * 50}

📡 RADAR:
  - Port d'écoute: {stats['radar']['port_ecoute']}
  - Pings envoyés: {stats['radar']['pings_envoyes']}
  - Pongs reçus: {stats['radar']['pongs_recus']}
  - Forts détectés: {stats['radar']['forts_decouverts']}

🗺️ CARTOGRAPHIE:
  - Forts cartographiés: {stats['carte']['forts']['total']}
  - Forts actifs: {stats['carte']['forts']['actifs']}
  - Routes calculées: {stats['carte']['routes']['total']}

📊 RÉSUMÉ:
  - Uptime: {stats['resume']['uptime']:.0f}s
  - Taux d'intégration: {stats['resume']['taux_integration']:.1f}%
  - Dernière découverte: {time.ctime(stats['carte']['derniere_decouverte']) if stats['carte']['derniere_decouverte'] else 'Jamais'}

🏰 FORTS DÉCOUVERTS:
"""
        
        for fort in self.carte.forts.values():
            if fort.id_fort != self.id_fort:
                rapport += f"  - {fort.nom} ({fort.statut}) @ {fort.addr_reseau[0]}:{fort.addr_reseau[1]}\n"
        
        return rapport
    
    def __str__(self):
        return f"DecouvreurReseau({self.nom_fort}, {len(self.carte.forts)} forts)"