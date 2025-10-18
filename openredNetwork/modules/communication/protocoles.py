#!/usr/bin/env python3
"""
📡 OpenRed Network - Module Communication: Protocoles
Protocoles de communication pour OpenRed Network
"""

import json
import time
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class TypeMessage(Enum):
    """Types de messages du protocole OpenRed"""
    PING = "ping"
    PONG = "pong"
    HELLO = "hello"
    HELLO_ACK = "hello_ack"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    PROJECTION = "projection"
    PROJECTION_ACK = "projection_ack"


@dataclass
class MessageORN:
    """
    Message du protocole OpenRed Network (ORN)
    Structure standardisée pour tous les échanges
    """
    type_message: str
    id_message: str
    expediteur: str
    destinataire: str
    timestamp: float
    data: Dict[str, Any]
    signature: Optional[str] = None
    ttl: int = 300  # Time To Live en secondes
    
    def to_dict(self) -> Dict:
        """Convertit le message en dictionnaire"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MessageORN':
        """Crée un message depuis un dictionnaire"""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convertit le message en JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MessageORN':
        """Crée un message depuis du JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def est_expire(self) -> bool:
        """Vérifie si le message est expiré"""
        return time.time() > (self.timestamp + self.ttl)
    
    def calculer_checksum(self) -> str:
        """Calcule un checksum du message pour vérification intégrité"""
        data_str = f"{self.type_message}{self.expediteur}{self.destinataire}{self.timestamp}"
        return hashlib.md5(data_str.encode()).hexdigest()


class ConstructeurMessages:
    """
    🏗️ Constructeur de messages ORN
    Facilite la création de messages standardisés
    """
    
    @staticmethod
    def creer_ping(expediteur: str, destinataire: str = "broadcast", 
                   data_supplementaires: Dict = None) -> MessageORN:
        """Crée un message ping"""
        return MessageORN(
            type_message=TypeMessage.PING.value,
            id_message=f"ping_{uuid.uuid4().hex[:8]}",
            expediteur=expediteur,
            destinataire=destinataire,
            timestamp=time.time(),
            data=data_supplementaires or {},
            ttl=60  # Ping expire rapidement
        )
    
    @staticmethod
    def creer_pong(message_ping: MessageORN, expediteur: str, 
                   data_supplementaires: Dict = None) -> MessageORN:
        """Crée un message pong en réponse à un ping"""
        data = data_supplementaires or {}
        data["reponse_a"] = message_ping.id_message
        
        return MessageORN(
            type_message=TypeMessage.PONG.value,
            id_message=f"pong_{uuid.uuid4().hex[:8]}",
            expediteur=expediteur,
            destinataire=message_ping.expediteur,
            timestamp=time.time(),
            data=data,
            ttl=60
        )
    
    @staticmethod
    def creer_hello(expediteur: str, destinataire: str, 
                    informations_fort: Dict) -> MessageORN:
        """Crée un message hello pour présenter un fort"""
        return MessageORN(
            type_message=TypeMessage.HELLO.value,
            id_message=f"hello_{uuid.uuid4().hex[:8]}",
            expediteur=expediteur,
            destinataire=destinataire,
            timestamp=time.time(),
            data={
                "fort_info": informations_fort,
                "protocole_version": "1.0.0",
                "capabilities": ["projection", "cartographie", "messaging"]
            },
            ttl=300
        )
    
    @staticmethod
    def creer_hello_ack(message_hello: MessageORN, expediteur: str,
                       informations_fort: Dict) -> MessageORN:
        """Crée un accusé de réception hello"""
        return MessageORN(
            type_message=TypeMessage.HELLO_ACK.value,
            id_message=f"hello_ack_{uuid.uuid4().hex[:8]}",
            expediteur=expediteur,
            destinataire=message_hello.expediteur,
            timestamp=time.time(),
            data={
                "reponse_a": message_hello.id_message,
                "fort_info": informations_fort,
                "accepted": True
            },
            ttl=300
        )
    
    @staticmethod
    def creer_request(expediteur: str, destinataire: str, action: str, 
                     parametres: Dict = None) -> MessageORN:
        """Crée un message de requête"""
        return MessageORN(
            type_message=TypeMessage.REQUEST.value,
            id_message=f"req_{uuid.uuid4().hex[:8]}",
            expediteur=expediteur,
            destinataire=destinataire,
            timestamp=time.time(),
            data={
                "action": action,
                "parametres": parametres or {}
            },
            ttl=600
        )
    
    @staticmethod
    def creer_response(message_request: MessageORN, expediteur: str,
                      resultat: Any, succes: bool = True) -> MessageORN:
        """Crée un message de réponse"""
        return MessageORN(
            type_message=TypeMessage.RESPONSE.value,
            id_message=f"resp_{uuid.uuid4().hex[:8]}",
            expediteur=expediteur,
            destinataire=message_request.expediteur,
            timestamp=time.time(),
            data={
                "reponse_a": message_request.id_message,
                "succes": succes,
                "resultat": resultat
            },
            ttl=600
        )
    
    @staticmethod
    def creer_notification(expediteur: str, destinataire: str, evenement: str,
                          details: Dict = None) -> MessageORN:
        """Crée un message de notification"""
        return MessageORN(
            type_message=TypeMessage.NOTIFICATION.value,
            id_message=f"notif_{uuid.uuid4().hex[:8]}",
            expediteur=expediteur,
            destinataire=destinataire,
            timestamp=time.time(),
            data={
                "evenement": evenement,
                "details": details or {}
            },
            ttl=3600
        )
    
    @staticmethod
    def creer_error(expediteur: str, destinataire: str, code_erreur: str,
                   message_erreur: str, message_origine: MessageORN = None) -> MessageORN:
        """Crée un message d'erreur"""
        data = {
            "code_erreur": code_erreur,
            "message": message_erreur
        }
        
        if message_origine:
            data["message_origine"] = message_origine.id_message
        
        return MessageORN(
            type_message=TypeMessage.ERROR.value,
            id_message=f"err_{uuid.uuid4().hex[:8]}",
            expediteur=expediteur,
            destinataire=destinataire,
            timestamp=time.time(),
            data=data,
            ttl=300
        )
    
    @staticmethod
    def creer_projection(expediteur: str, destinataire: str, 
                        id_projection: str, metadata: Dict = None) -> MessageORN:
        """Crée un message pour partager une projection"""
        return MessageORN(
            type_message=TypeMessage.PROJECTION.value,
            id_message=f"proj_{uuid.uuid4().hex[:8]}",
            expediteur=expediteur,
            destinataire=destinataire,
            timestamp=time.time(),
            data={
                "id_projection": id_projection,
                "metadata": metadata or {}
            },
            ttl=900
        )


class ValidateurMessages:
    """
    ✅ Validateur de messages ORN
    Vérifie la validité et l'intégrité des messages
    """
    
    @staticmethod
    def valider_structure(message: MessageORN) -> Tuple[bool, str]:
        """Valide la structure d'un message"""
        
        # Vérification des champs obligatoires
        champs_requis = ["type_message", "id_message", "expediteur", 
                        "destinataire", "timestamp", "data"]
        
        for champ in champs_requis:
            if not hasattr(message, champ) or getattr(message, champ) is None:
                return False, f"Champ manquant: {champ}"
        
        # Vérification type de message valide
        types_valides = [t.value for t in TypeMessage]
        if message.type_message not in types_valides:
            return False, f"Type de message invalide: {message.type_message}"
        
        # Vérification timestamp
        if not isinstance(message.timestamp, (int, float)) or message.timestamp <= 0:
            return False, "Timestamp invalide"
        
        # Vérification TTL
        if not isinstance(message.ttl, int) or message.ttl <= 0:
            return False, "TTL invalide"
        
        # Vérification data est un dict
        if not isinstance(message.data, dict):
            return False, "Data doit être un dictionnaire"
        
        return True, "Structure valide"
    
    @staticmethod
    def valider_expiration(message: MessageORN) -> Tuple[bool, str]:
        """Valide que le message n'est pas expiré"""
        if message.est_expire():
            return False, "Message expiré"
        return True, "Message valide"
    
    @staticmethod
    def valider_coherence(message: MessageORN) -> Tuple[bool, str]:
        """Valide la cohérence interne du message"""
        
        # Vérification cohérence type/data pour certains types
        if message.type_message == TypeMessage.PONG.value:
            if "reponse_a" not in message.data:
                return False, "Pong doit contenir 'reponse_a'"
        
        elif message.type_message == TypeMessage.HELLO_ACK.value:
            if "reponse_a" not in message.data:
                return False, "Hello ACK doit contenir 'reponse_a'"
        
        elif message.type_message == TypeMessage.RESPONSE.value:
            if "reponse_a" not in message.data or "succes" not in message.data:
                return False, "Response doit contenir 'reponse_a' et 'succes'"
        
        elif message.type_message == TypeMessage.REQUEST.value:
            if "action" not in message.data:
                return False, "Request doit contenir 'action'"
        
        elif message.type_message == TypeMessage.ERROR.value:
            if "code_erreur" not in message.data or "message" not in message.data:
                return False, "Error doit contenir 'code_erreur' et 'message'"
        
        return True, "Cohérence valide"
    
    @staticmethod
    def valider_complet(message: MessageORN) -> Tuple[bool, List[str]]:
        """Validation complète d'un message"""
        erreurs = []
        
        # Validation structure
        valide, erreur = ValidateurMessages.valider_structure(message)
        if not valide:
            erreurs.append(erreur)
        
        # Validation expiration
        valide, erreur = ValidateurMessages.valider_expiration(message)
        if not valide:
            erreurs.append(erreur)
        
        # Validation cohérence
        valide, erreur = ValidateurMessages.valider_coherence(message)
        if not valide:
            erreurs.append(erreur)
        
        return len(erreurs) == 0, erreurs


class RouteurMessages:
    """
    🚦 Routeur de messages ORN
    Gère le routage et la distribution des messages
    """
    
    def __init__(self, id_fort_local: str):
        self.id_fort_local = id_fort_local
        self.handlers = {}  # type_message -> handler function
        self.cache_messages = {}  # id_message -> message (éviter doublons)
        self.statistiques = {
            "messages_recus": 0,
            "messages_envoyes": 0,
            "messages_ignores": 0,
            "messages_invalides": 0
        }
    
    def enregistrer_handler(self, type_message: str, handler_function):
        """Enregistre un handler pour un type de message"""
        self.handlers[type_message] = handler_function
        print(f"📡 Handler enregistré pour {type_message}")
    
    def traiter_message(self, message: MessageORN) -> bool:
        """Traite un message reçu"""
        
        self.statistiques["messages_recus"] += 1
        
        # Validation du message
        valide, erreurs = ValidateurMessages.valider_complet(message)
        if not valide:
            self.statistiques["messages_invalides"] += 1
            print(f"❌ Message invalide: {', '.join(erreurs)}")
            return False
        
        # Vérification doublons
        if message.id_message in self.cache_messages:
            self.statistiques["messages_ignores"] += 1
            return False
        
        # Mise en cache
        self.cache_messages[message.id_message] = time.time()
        
        # Vérification destination
        if (message.destinataire != self.id_fort_local and 
            message.destinataire != "broadcast"):
            # Message pas pour nous, ignorer ou relayer
            self.statistiques["messages_ignores"] += 1
            return False
        
        # Routage vers le handler approprié
        handler = self.handlers.get(message.type_message)
        if handler:
            try:
                handler(message)
                return True
            except Exception as e:
                print(f"❌ Erreur handler {message.type_message}: {e}")
                return False
        else:
            print(f"⚠️ Pas de handler pour {message.type_message}")
            self.statistiques["messages_ignores"] += 1
            return False
    
    def nettoyer_cache(self, age_max: int = 3600):
        """Nettoie le cache des messages anciens"""
        maintenant = time.time()
        messages_a_supprimer = []
        
        for id_msg, timestamp in self.cache_messages.items():
            if maintenant - timestamp > age_max:
                messages_a_supprimer.append(id_msg)
        
        for id_msg in messages_a_supprimer:
            del self.cache_messages[id_msg]
        
        if messages_a_supprimer:
            print(f"🧹 Cache nettoyé: {len(messages_a_supprimer)} messages supprimés")
    
    def obtenir_statistiques(self) -> Dict:
        """Obtient les statistiques du routeur"""
        return {
            **self.statistiques,
            "handlers_actifs": len(self.handlers),
            "cache_size": len(self.cache_messages)
        }