# === OpenRed Spider Protocol Handler ===
# Gestion des requêtes de découverte spider

import json
import socket
import threading
import time
from typing import Dict, Any

class SpiderProtocolHandler:
    """Handler pour les requêtes du protocole spider"""
    
    def __init__(self, lighthouse_protocol, internet_spider):
        self.lighthouse = lighthouse_protocol
        self.spider = internet_spider
        
    def handle_spider_request(self, conn: socket.socket, addr: tuple, data: bytes):
        """Gère une requête spider entrante"""
        try:
            # Décoder la requête
            request = json.loads(data.decode('utf-8'))
            
            if "handshake" in request:
                handshake = request["handshake"]
                
                # Vérifier que c'est une requête spider valide
                if handshake.get("protocol") == "OpenRed-Spider-v1":
                    
                    if handshake.get("request_type") == "discover":
                        # Réponse simple de découverte
                        response = {
                            "protocol": "OpenRed-Spider-v1",
                            "status": "success",
                            "fingerprint": self.lighthouse.fingerprint,
                            "node_id": self.lighthouse.node_id,
                            "timestamp": time.time()
                        }
                        
                    elif handshake.get("request_type") == "exchange":
                        # Échange complet avec listes de nœuds
                        response = {
                            "protocol": "OpenRed-Spider-v1",
                            "status": "success",
                            "fingerprint": self.lighthouse.fingerprint,
                            "node_id": self.lighthouse.node_id,
                            "timestamp": time.time(),
                            "their_nodes": self.spider._get_shareable_nodes()
                        }
                        
                        # Traiter les nœuds reçus
                        if "my_nodes" in request:
                            self.spider._process_received_nodes(request["my_nodes"])
                            print(f"🔄 Node exchange with {addr[0]} - received {len(request['my_nodes'])} nodes")
                        
                    else:
                        response = {"status": "error", "message": "Unknown request type"}
                        
                    # Envoyer la réponse
                    response_data = json.dumps(response).encode('utf-8')
                    conn.send(len(response_data).to_bytes(4, 'big'))
                    conn.send(response_data)
                    
                else:
                    # Pas une requête spider OpenRed
                    conn.send(b'\x00\x00\x00\x00')  # Réponse vide
                    
        except Exception as e:
            print(f"🕷️ Spider handler error: {e}")
            try:
                conn.send(b'\x00\x00\x00\x00')  # Réponse d'erreur
            except:
                pass