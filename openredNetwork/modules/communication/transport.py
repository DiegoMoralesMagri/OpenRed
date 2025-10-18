#!/usr/bin/env python3
"""
🔌 OpenRed Network - Module Communication: Transport UDP
Couche de transport UDP pour OpenRed Network
"""

import socket
import threading
import time
import json
from typing import Dict, List, Optional, Callable, Tuple
from queue import Queue, Empty

from .protocoles import MessageORN, RouteurMessages


class TransportUDP:
    """
    🔌 Transport UDP pour OpenRed Network
    Gère l'envoi et la réception de messages via UDP
    """
    
    def __init__(self, id_fort: str, port_ecoute: int = 0, adresse_locale: str = ""):
        self.id_fort = id_fort
        self.adresse_locale = adresse_locale or "0.0.0.0"
        self.port_ecoute = port_ecoute or self._obtenir_port_libre()
        
        # Socket UDP
        self.socket_udp = None
        self.transport_actif = False
        
        # Threads de traitement
        self.thread_reception = None
        self.thread_envoi = None
        
        # Files de messages
        self.file_envoi = Queue()
        self.file_reception = Queue()
        
        # Routeur de messages
        self.routeur = RouteurMessages(id_fort)
        
        # Statistiques
        self.stats = {
            "messages_envoyes": 0,
            "messages_recus": 0,
            "erreurs_envoi": 0,
            "erreurs_reception": 0,
            "bytes_envoyes": 0,
            "bytes_recus": 0,
            "debut_transport": 0
        }
        
        # Callbacks
        self.callbacks = {
            "message_recu": [],
            "message_envoye": [],
            "erreur_transport": []
        }
        
        print(f"🔌 Transport UDP initialisé pour {id_fort} sur port {self.port_ecoute}")
    
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
    
    def demarrer_transport(self) -> bool:
        """Démarre le transport UDP"""
        if self.transport_actif:
            return True
        
        try:
            # Création et configuration socket
            self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_udp.bind((self.adresse_locale, self.port_ecoute))
            self.socket_udp.settimeout(1.0)
            
            self.transport_actif = True
            self.stats["debut_transport"] = time.time()
            
            # Démarrage threads
            self.thread_reception = threading.Thread(target=self._boucle_reception, daemon=True)
            self.thread_envoi = threading.Thread(target=self._boucle_envoi, daemon=True)
            
            self.thread_reception.start()
            self.thread_envoi.start()
            
            print(f"🔌 Transport UDP démarré: {self.adresse_locale}:{self.port_ecoute}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur démarrage transport: {e}")
            self.transport_actif = False
            return False
    
    def arreter_transport(self):
        """Arrête le transport UDP"""
        if not self.transport_actif:
            return
        
        self.transport_actif = False
        
        if self.socket_udp:
            self.socket_udp.close()
        
        print(f"🔌 Transport UDP arrêté: {self.id_fort}")
    
    def _boucle_reception(self):
        """Boucle de réception des messages"""
        while self.transport_actif:
            try:
                data, addr = self.socket_udp.recvfrom(65536)  # 64KB max
                
                self.stats["messages_recus"] += 1
                self.stats["bytes_recus"] += len(data)
                
                # Décodage du message
                try:
                    message_json = data.decode('utf-8')
                    message = MessageORN.from_json(message_json)
                    
                    # Ajout adresse source au message
                    message.data["_source_addr"] = addr
                    
                    # Traitement par le routeur
                    self.routeur.traiter_message(message)
                    
                    # Notification callback
                    self._notifier_callback("message_recu", message, addr)
                    
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"❌ Message UDP mal formé de {addr}: {e}")
                    self.stats["erreurs_reception"] += 1
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.transport_actif:
                    print(f"❌ Erreur réception UDP: {e}")
                    self.stats["erreurs_reception"] += 1
                    self._notifier_callback("erreur_transport", "reception", e)
    
    def _boucle_envoi(self):
        """Boucle d'envoi des messages"""
        while self.transport_actif:
            try:
                # Attente d'un message à envoyer (timeout 1s)
                message, adresse = self.file_envoi.get(timeout=1.0)
                
                # Encodage et envoi
                message_json = message.to_json()
                data = message_json.encode('utf-8')
                
                self.socket_udp.sendto(data, adresse)
                
                self.stats["messages_envoyes"] += 1
                self.stats["bytes_envoyes"] += len(data)
                
                # Notification callback
                self._notifier_callback("message_envoye", message, adresse)
                
            except Empty:
                continue
            except Exception as e:
                if self.transport_actif:
                    print(f"❌ Erreur envoi UDP: {e}")
                    self.stats["erreurs_envoi"] += 1
                    self._notifier_callback("erreur_transport", "envoi", e)
    
    def envoyer_message(self, message: MessageORN, adresse: Tuple[str, int]) -> bool:
        """Envoie un message via UDP"""
        if not self.transport_actif:
            return False
        
        try:
            self.file_envoi.put((message, adresse), timeout=5.0)
            return True
        except:
            return False
    
    def envoyer_broadcast(self, message: MessageORN, port_cible: int = 21000) -> int:
        """Envoie un message en broadcast"""
        if not self.transport_actif:
            return 0
        
        # Adresses de broadcast courantes
        adresses_broadcast = [
            ('255.255.255.255', port_cible),  # Broadcast général
            ('192.168.1.255', port_cible),    # Réseau 192.168.1.x
            ('192.168.0.255', port_cible),    # Réseau 192.168.0.x
            ('10.0.0.255', port_cible)        # Réseau 10.0.0.x
        ]
        
        envois_reussis = 0
        
        for addr in adresses_broadcast:
            try:
                # Socket temporaire pour broadcast
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.settimeout(1.0)
                    
                    message_json = message.to_json()
                    data = message_json.encode('utf-8')
                    
                    sock.sendto(data, addr)
                    envois_reussis += 1
                    
            except:
                pass  # Ignore les erreurs de broadcast
        
        if envois_reussis > 0:
            self.stats["messages_envoyes"] += envois_reussis
            self.stats["bytes_envoyes"] += len(data) * envois_reussis
        
        return envois_reussis
    
    def enregistrer_handler_message(self, type_message: str, handler: Callable):
        """Enregistre un handler pour un type de message"""
        self.routeur.enregistrer_handler(type_message, handler)
    
    def obtenir_adresse_locale(self) -> Tuple[str, int]:
        """Obtient l'adresse locale d'écoute"""
        return (self.adresse_locale, self.port_ecoute)
    
    def obtenir_statistiques(self) -> Dict:
        """Obtient les statistiques du transport"""
        stats_routeur = self.routeur.obtenir_statistiques()
        
        uptime = time.time() - self.stats["debut_transport"] if self.stats["debut_transport"] else 0
        
        return {
            **self.stats,
            "transport_actif": self.transport_actif,
            "uptime": uptime,
            "throughput_envoi": self.stats["bytes_envoyes"] / max(1, uptime),
            "throughput_reception": self.stats["bytes_recus"] / max(1, uptime),
            "routeur": stats_routeur
        }
    
    def nettoyer_caches(self):
        """Nettoie les caches du routeur"""
        self.routeur.nettoyer_cache()
    
    def __del__(self):
        """Destructeur - arrête le transport"""
        if hasattr(self, 'transport_actif') and self.transport_actif:
            self.arreter_transport()


class GestionnaireConnexions:
    """
    🔗 Gestionnaire de connexions UDP
    Gère les connexions vers les différents forts
    """
    
    def __init__(self, transport: TransportUDP):
        self.transport = transport
        self.connexions = {}  # id_fort -> infos connexion
        self.mutex = threading.Lock()
        
        # Configuration callbacks
        self.transport.ajouter_callback("message_recu", self._callback_message_recu)
    
    def _callback_message_recu(self, message: MessageORN, addr: Tuple[str, int]):
        """Callback pour mise à jour des connexions"""
        if message.expediteur != self.transport.id_fort:
            self.mettre_a_jour_connexion(message.expediteur, addr)
    
    def enregistrer_connexion(self, id_fort: str, adresse: Tuple[str, int], 
                            metadata: Dict = None):
        """Enregistre une connexion vers un fort"""
        with self.mutex:
            self.connexions[id_fort] = {
                "adresse": adresse,
                "derniere_activite": time.time(),
                "messages_envoyes": 0,
                "messages_recus": 0,
                "metadata": metadata or {}
            }
            print(f"🔗 Connexion enregistrée: {id_fort} @ {adresse[0]}:{adresse[1]}")
    
    def mettre_a_jour_connexion(self, id_fort: str, adresse: Tuple[str, int]):
        """Met à jour une connexion existante"""
        with self.mutex:
            if id_fort in self.connexions:
                connexion = self.connexions[id_fort]
                connexion["derniere_activite"] = time.time()
                connexion["messages_recus"] += 1
                
                # Mise à jour adresse si changée
                if connexion["adresse"] != adresse:
                    print(f"🔄 Adresse mise à jour pour {id_fort}: {adresse[0]}:{adresse[1]}")
                    connexion["adresse"] = adresse
            else:
                # Nouvelle connexion détectée
                self.enregistrer_connexion(id_fort, adresse)
    
    def envoyer_vers_fort(self, id_fort: str, message: MessageORN) -> bool:
        """Envoie un message vers un fort spécifique"""
        with self.mutex:
            if id_fort not in self.connexions:
                return False
            
            connexion = self.connexions[id_fort]
            adresse = connexion["adresse"]
            
            if self.transport.envoyer_message(message, adresse):
                connexion["messages_envoyes"] += 1
                return True
            
            return False
    
    def obtenir_connexions_actives(self, timeout: int = 300) -> List[str]:
        """Obtient la liste des connexions actives"""
        maintenant = time.time()
        connexions_actives = []
        
        with self.mutex:
            for id_fort, connexion in self.connexions.items():
                if maintenant - connexion["derniere_activite"] < timeout:
                    connexions_actives.append(id_fort)
        
        return connexions_actives
    
    def nettoyer_connexions_inactives(self, timeout: int = 600):
        """Nettoie les connexions inactives"""
        maintenant = time.time()
        connexions_a_supprimer = []
        
        with self.mutex:
            for id_fort, connexion in self.connexions.items():
                if maintenant - connexion["derniere_activite"] > timeout:
                    connexions_a_supprimer.append(id_fort)
            
            for id_fort in connexions_a_supprimer:
                del self.connexions[id_fort]
                print(f"🧹 Connexion inactive supprimée: {id_fort}")
    
    def obtenir_statistiques_connexions(self) -> Dict:
        """Obtient les statistiques des connexions"""
        with self.mutex:
            return {
                "total_connexions": len(self.connexions),
                "connexions_actives": len(self.obtenir_connexions_actives()),
                "detail_connexions": [
                    {
                        "id_fort": id_fort,
                        "adresse": f"{conn['adresse'][0]}:{conn['adresse'][1]}",
                        "derniere_activite": conn["derniere_activite"],
                        "messages_envoyes": conn["messages_envoyes"],
                        "messages_recus": conn["messages_recus"]
                    }
                    for id_fort, conn in self.connexions.items()
                ]
            }