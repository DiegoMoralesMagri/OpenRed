#!/usr/bin/env python3
"""
📡 OpenRed Network - Module Cartographie: Radar de Découverte
Système de radar pour découvrir automatiquement les forts du réseau
"""

import socket
import json
import time
import threading
import uuid
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime

from .carte import CarteReseau, FortSurCarte, PositionFort


class MessageRadar:
    """
    📡 Message radar pour la découverte de forts
    """
    
    @staticmethod
    def creer_ping(id_fort: str, nom_fort: str, port_ecoute: int) -> Dict:
        """Crée un message ping de découverte"""
        return {
            "type": "radar_ping",
            "id_fort": id_fort,
            "nom_fort": nom_fort,
            "port_ecoute": port_ecoute,
            "timestamp": time.time(),
            "id_message": f"ping_{uuid.uuid4().hex[:8]}"
        }
    
    @staticmethod
    def creer_pong(ping_msg: Dict, id_fort: str, nom_fort: str, port_ecoute: int) -> Dict:
        """Crée un message pong en réponse à un ping"""
        return {
            "type": "radar_pong",
            "id_fort": id_fort,
            "nom_fort": nom_fort,
            "port_ecoute": port_ecoute,
            "timestamp": time.time(),
            "reponse_a": ping_msg.get("id_message"),
            "id_message": f"pong_{uuid.uuid4().hex[:8]}"
        }
    
    @staticmethod
    def valider_message(msg: Dict) -> bool:
        """Valide la structure d'un message radar"""
        champs_requis = ["type", "id_fort", "nom_fort", "timestamp"]
        return all(champ in msg for champ in champs_requis)


class RadarFort:
    """
    📡 Radar de découverte de forts
    Émet des pings et écoute les réponses pour cartographier le réseau
    """
    
    def __init__(self, id_fort: str, nom_fort: str, port_ecoute: int = 0):
        self.id_fort = id_fort
        self.nom_fort = nom_fort
        self.port_ecoute = port_ecoute or self._obtenir_port_libre()
        
        # Socket UDP pour le radar
        self.socket_radar = None
        self.radar_actif = False
        
        # Threads de fonctionnement
        self.thread_ecoute = None
        self.thread_ping = None
        
        # Statistiques de découverte
        self.pings_envoyes = 0
        self.pongs_recus = 0
        self.forts_decouverts = {}
        
        # Callbacks pour événements
        self.callbacks = {
            "fort_decouvert": [],
            "fort_perdu": [],
            "ping_recu": [],
            "pong_recu": []
        }
        
        print(f"📡 Radar initialisé pour {self.nom_fort} sur port {self.port_ecoute}")
    
    def _obtenir_port_libre(self) -> int:
        """Trouve un port UDP libre"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def ajouter_callback(self, evenement: str, callback: Callable):
        """Ajoute un callback pour un événement"""
        if evenement in self.callbacks:
            self.callbacks[evenement].append(callback)
    
    def _notifier_callback(self, evenement: str, *args):
        """Notifie les callbacks d'un événement"""
        for callback in self.callbacks.get(evenement, []):
            try:
                callback(*args)
            except Exception as e:
                print(f"❌ Erreur callback {evenement}: {e}")
    
    def demarrer_radar(self):
        """Démarre le radar de découverte"""
        if self.radar_actif:
            return
        
        try:
            # Création socket UDP
            self.socket_radar = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_radar.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_radar.bind(('', self.port_ecoute))
            self.socket_radar.settimeout(1.0)
            
            self.radar_actif = True
            
            # Démarrage threads
            self.thread_ecoute = threading.Thread(target=self._boucle_ecoute, daemon=True)
            self.thread_ping = threading.Thread(target=self._boucle_ping, daemon=True)
            
            self.thread_ecoute.start()
            self.thread_ping.start()
            
            print(f"📡 Radar démarré: {self.nom_fort} écoute sur {self.port_ecoute}")
            
        except Exception as e:
            print(f"❌ Erreur démarrage radar: {e}")
            self.radar_actif = False
    
    def arreter_radar(self):
        """Arrête le radar"""
        if not self.radar_actif:
            return
        
        self.radar_actif = False
        
        if self.socket_radar:
            self.socket_radar.close()
        
        print(f"📡 Radar arrêté: {self.nom_fort}")
    
    def _boucle_ecoute(self):
        """Boucle d'écoute des messages radar"""
        while self.radar_actif:
            try:
                data, addr = self.socket_radar.recvfrom(4096)
                message = json.loads(data.decode('utf-8'))
                
                if MessageRadar.valider_message(message):
                    self._traiter_message_radar(message, addr)
                
            except socket.timeout:
                continue
            except json.JSONDecodeError:
                print("❌ Message radar mal formé reçu")
            except Exception as e:
                if self.radar_actif:  # Ne pas logger si arrêt en cours
                    print(f"❌ Erreur écoute radar: {e}")
    
    def _boucle_ping(self):
        """Boucle d'émission de pings périodiques"""
        while self.radar_actif:
            try:
                self._envoyer_ping_broadcast()
                time.sleep(10)  # Ping toutes les 10 secondes
            except Exception as e:
                if self.radar_actif:
                    print(f"❌ Erreur ping radar: {e}")
    
    def _traiter_message_radar(self, message: Dict, addr: Tuple[str, int]):
        """Traite un message radar reçu"""
        type_msg = message.get("type")
        id_fort_distant = message.get("id_fort")
        
        # Ignorer ses propres messages
        if id_fort_distant == self.id_fort:
            return
        
        if type_msg == "radar_ping":
            self._traiter_ping(message, addr)
        elif type_msg == "radar_pong":
            self._traiter_pong(message, addr)
    
    def _traiter_ping(self, ping_msg: Dict, addr: Tuple[str, int]):
        """Traite un ping reçu et envoie un pong"""
        # Enregistrer le fort découvert
        self._enregistrer_fort_decouvert(ping_msg, addr)
        
        # Créer et envoyer pong
        pong = MessageRadar.creer_pong(
            ping_msg, self.id_fort, self.nom_fort, self.port_ecoute
        )
        
        self._envoyer_message(pong, addr)
        
        # Notification callback
        self._notifier_callback("ping_recu", ping_msg, addr)
        
        print(f"📡 Ping reçu de {ping_msg.get('nom_fort')} -> Pong envoyé")
    
    def _traiter_pong(self, pong_msg: Dict, addr: Tuple[str, int]):
        """Traite un pong reçu"""
        self.pongs_recus += 1
        
        # Enregistrer le fort découvert
        self._enregistrer_fort_decouvert(pong_msg, addr)
        
        # Notification callback
        self._notifier_callback("pong_recu", pong_msg, addr)
        
        print(f"📡 Pong reçu de {pong_msg.get('nom_fort')}")
    
    def _enregistrer_fort_decouvert(self, message: Dict, addr: Tuple[str, int]):
        """Enregistre un fort découvert"""
        id_fort = message.get("id_fort")
        nom_fort = message.get("nom_fort")
        port_fort = message.get("port_ecoute", addr[1])
        
        if id_fort not in self.forts_decouverts:
            # Nouveau fort découvert
            fort_info = {
                "id_fort": id_fort,
                "nom_fort": nom_fort,
                "addr_ip": addr[0],
                "port": port_fort,
                "premiere_decouverte": time.time(),
                "derniere_activite": time.time(),
                "messages_recus": 1
            }
            
            self.forts_decouverts[id_fort] = fort_info
            
            # Notification callback
            self._notifier_callback("fort_decouvert", fort_info)
            
            print(f"🎯 Nouveau fort découvert: {nom_fort} ({addr[0]}:{port_fort})")
        else:
            # Mise à jour fort existant
            fort_info = self.forts_decouverts[id_fort]
            fort_info["derniere_activite"] = time.time()
            fort_info["messages_recus"] += 1
            fort_info["addr_ip"] = addr[0]  # IP peut changer
            fort_info["port"] = port_fort
    
    def _envoyer_ping_broadcast(self):
        """Envoie un ping en broadcast"""
        ping = MessageRadar.creer_ping(self.id_fort, self.nom_fort, self.port_ecoute)
        
        # Broadcast sur différents réseaux
        adresses_broadcast = [
            ('255.255.255.255', 21000),  # Broadcast général
            ('192.168.1.255', 21000),    # Réseau local 192.168.1.x
            ('192.168.0.255', 21000),    # Réseau local 192.168.0.x
            ('10.0.0.255', 21000)        # Réseau local 10.0.0.x
        ]
        
        for addr in adresses_broadcast:
            try:
                self._envoyer_message(ping, addr, broadcast=True)
            except:
                pass  # Ignore les erreurs de broadcast
        
        self.pings_envoyes += 1
    
    def _envoyer_message(self, message: Dict, addr: Tuple[str, int], broadcast: bool = False):
        """Envoie un message radar"""
        try:
            if broadcast:
                # Socket temporaire pour broadcast
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    data = json.dumps(message).encode('utf-8')
                    sock.sendto(data, addr)
            else:
                # Utilisation socket principal
                data = json.dumps(message).encode('utf-8')
                self.socket_radar.sendto(data, addr)
                
        except Exception as e:
            print(f"❌ Erreur envoi message radar: {e}")
    
    def obtenir_forts_decouverts(self) -> List[Dict]:
        """Obtient la liste des forts découverts"""
        return list(self.forts_decouverts.values())
    
    def obtenir_statistiques(self) -> Dict:
        """Obtient les statistiques du radar"""
        return {
            "radar_actif": self.radar_actif,
            "port_ecoute": self.port_ecoute,
            "pings_envoyes": self.pings_envoyes,
            "pongs_recus": self.pongs_recus,
            "forts_decouverts": len(self.forts_decouverts),
            "uptime": time.time() - getattr(self, 'debut_radar', time.time())
        }
    
    def nettoyer_forts_inactifs(self, timeout: float = 300):
        """Nettoie les forts inactifs (plus de timeout secondes)"""
        maintenant = time.time()
        forts_a_supprimer = []
        
        for id_fort, fort_info in self.forts_decouverts.items():
            if maintenant - fort_info["derniere_activite"] > timeout:
                forts_a_supprimer.append(id_fort)
        
        for id_fort in forts_a_supprimer:
            fort_info = self.forts_decouverts[id_fort]
            del self.forts_decouverts[id_fort]
            
            # Notification callback
            self._notifier_callback("fort_perdu", fort_info)
            
            print(f"🧹 Fort inactif supprimé: {fort_info['nom_fort']}")
    
    def __del__(self):
        """Destructeur - arrête le radar"""
        if hasattr(self, 'radar_actif') and self.radar_actif:
            self.arreter_radar()