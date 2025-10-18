# === OpenRed P2P : Helper pour Protocole Simple ===
# Intégration du protocole 3 phases convenu avec le système existant

import os
import sys
import json
import time
import socket
import threading

# Ajout du chemin pour les modules P2P
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'p2p_security'))
from simple_three_phase import SimpleThreePhase

# Ajout du chemin pour les modules principaux
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from openred_p2p_node import OpenRedP2PNode
from friendship_protocol import Friendship, FriendshipStatus, FriendshipPermissions, PermissionLevel

# Instance globale du protocole simple
simple_protocol = None
simple_server_socket = None
server_thread = None

def initialize_simple_protocol(p2p_node: OpenRedP2PNode):
    """Initialise le protocole simple avec les clés du nœud P2P"""
    global simple_protocol, simple_server_socket, server_thread
    
    if p2p_node and p2p_node.lighthouse:
        simple_protocol = SimpleThreePhase(
            node_id=p2p_node.lighthouse.fingerprint,
            private_key=p2p_node.lighthouse.private_key,
            public_key=p2p_node.lighthouse.public_key
        )
        print(f"✅ Simple protocol initialized for {p2p_node.lighthouse.fingerprint[:8]}...")
        
        # Démarrer serveur TCP simple en parallèle du serveur complexe
        start_simple_server(p2p_node.p2p_port + 1000)  # Port décalé pour éviter conflits
        return True
    else:
        print("❌ Cannot initialize simple protocol - no P2P node or lighthouse")
        return False

def start_simple_server(port: int):
    """Démarre un serveur TCP simple pour le protocole 3 phases"""
    global simple_server_socket, server_thread
    
    def server_loop():
        global simple_server_socket
        try:
            simple_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            simple_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            simple_server_socket.bind(("0.0.0.0", port))
            simple_server_socket.listen(5)
            
            print(f"🔐 Simple Protocol server listening on port {port}")
            
            while True:
                try:
                    client_socket, client_address = simple_server_socket.accept()
                    print(f"📥 Simple Protocol connection from {client_address}")
                    
                    # Gérer dans un thread séparé
                    client_thread = threading.Thread(
                        target=handle_incoming_simple_message,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except Exception as e:
                    print(f"❌ Error accepting simple connection: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Error starting simple server: {e}")
    
    server_thread = threading.Thread(target=server_loop, daemon=True)
    server_thread.start()

async def send_friendship_request_simple(target_fingerprint: str, target_ip: str, target_port: int, request_data: dict) -> bool:
    """
    Envoie une demande d'amitié en utilisant le protocole simple 3 phases
    """
    global simple_protocol
    
    if not simple_protocol:
        print("❌ Simple protocol not initialized")
        return False
    
    try:
        # Prépare le message selon le format demande d'amitié
        friendship_message = {
            "type": "friendship_request",
            "data": request_data
        }
        
        print(f"📤 Sending friendship request via Simple Protocol")
        print(f"   From: {simple_protocol.node_id[:8]}...")
        print(f"   To: {target_fingerprint[:8]}...")
        print(f"   Target: {target_ip}:{target_port + 1000}")  # Port décalé
        
        # Utilise le protocole simple pour envoyer (port décalé pour simple)
        success = simple_protocol.send_simple_message(
            target_ip=target_ip,
            target_port=target_port + 1000,  # Port décalé
            target_node=target_fingerprint,
            message_data=friendship_message
        )
        
        if success:
            print(f"✅ Friendship request sent successfully via Simple Protocol")
        else:
            print(f"❌ Failed to send friendship request via Simple Protocol")
            
        return success
        
    except Exception as e:
        print(f"❌ Error sending friendship request via Simple Protocol: {e}")
        return False

def handle_incoming_simple_message(client_socket, client_address):
    """
    Gère les messages entrants selon le protocole simple
    """
    global simple_protocol
    
    if not simple_protocol:
        print("❌ Simple protocol not initialized for incoming message")
        client_socket.close()
        return
        
    try:
        print(f"📥 Handling incoming message via Simple Protocol from {client_address}")
        simple_protocol.handle_incoming_message(client_socket, client_address)
    except Exception as e:
        print(f"❌ Error handling incoming simple message: {e}")
        client_socket.close()

def get_simple_protocol_status():
    """Retourne le statut du protocole simple"""
    global simple_protocol
    
    if not simple_protocol:
        return {"status": "not_initialized"}
        
    return {
        "status": "active",
        "node_id": simple_protocol.node_id,
        "active_connections": len(simple_protocol.active_links),
        "connections": list(simple_protocol.active_links.keys()),
        "pending_friendship_requests": len(simple_protocol.get_pending_friendship_requests())
    }

def get_pending_friendship_requests():
    """Récupère les demandes d'amitié en attente du protocole simple"""
    global simple_protocol
    
    if not simple_protocol:
        return []
        
    return simple_protocol.get_pending_friendship_requests()

def process_pending_friendship_requests(friendship_system):
    """Traite les demandes d'amitié en attente et les intègre au système"""
    global simple_protocol
    import time  # Import au début de la fonction pour toutes les utilisations
    
    if not simple_protocol or not friendship_system:
        return 0
        
    processed_count = 0
    
    # Traiter les demandes d'amitié
    pending_requests = simple_protocol.get_pending_friendship_requests()
    
    for req_info in pending_requests:
        try:
            sender = req_info["sender"]
            friendship_data = req_info["data"]
            
            print(f"🔄 Processing pending message from {sender}")
            print(f"🔍 Message type: {friendship_data.get('type', 'unknown')}")
            
            # Vérifier le type de message
            message_type = friendship_data.get("type", "friendship_request")
            
            if message_type == "friendship_accepted":
                # Traiter notification d'acceptation
                acceptance_data = friendship_data.get("data", {})
                request_id = acceptance_data.get("request_id", "")
                accepted_by = acceptance_data.get("accepted_by_fingerprint", sender)
                accepted_by_node = acceptance_data.get("accepted_by_node_id", "")
                granted_permissions = acceptance_data.get("granted_permissions", {})
                
                print(f"🎉 Friendship accepted by {accepted_by} (node: {accepted_by_node}) for request {request_id}")
                
                # Créer l'amitié directement dans le système local
                try:
                    # Construire les permissions accordées
                    perms = FriendshipPermissions(
                        messaging=granted_permissions.get("messaging", True),
                        urn_access=granted_permissions.get("urn_access", False),
                        photo_sharing=granted_permissions.get("photo_sharing", False),
                        file_sharing=granted_permissions.get("file_sharing", False),
                        presence_info=granted_permissions.get("presence_info", False)
                    )
                    
                    # Créer la relation d'amitié directement
                    
                    friendship = Friendship(
                        fingerprint=accepted_by,
                        node_id=accepted_by_node,
                        status=FriendshipStatus.ACCEPTED,
                        permissions_granted=perms,  # Permissions qu'on nous accorde
                        permissions_received=FriendshipPermissions.from_level(PermissionLevel.BASIC),  # Permissions qu'on a demandées
                        first_interaction=time.time(),
                        last_interaction=time.time(),
                        notes=f"Friendship established via P2P protocol - request {request_id}"
                    )
                    
                    # Ajouter directement à la liste des amis
                    friendship_system.friendships[accepted_by] = friendship
                    friendship_system._save_friendships()
                    
                    print(f"✅ Friendship established with {accepted_by_node} ({accepted_by})")
                    print(f"   Granted permissions: {perms}")
                        
                except Exception as create_error:
                    print(f"❌ Error creating friendship: {create_error}")
                    import traceback
                    traceback.print_exc()
                
                # Marquer comme traité
                simple_protocol.mark_friendship_request_processed(sender, request_id)
                processed_count += 1
                
            else:
                # Traiter demande d'amitié normale
                print(f"🔄 Processing friendship request from {sender}")
                
                # Vérifier les permissions dans le bon format
                req_perms = friendship_data.get("requested_permissions", {})
                print(f"🔍 DEBUG: Raw permissions: {req_perms}")
                
                # Construire le request_data compatible avec friendship_protocol
                request_data = {
                    "request_id": friendship_data.get("request_id", ""),
                    "from_fingerprint": friendship_data.get("from_fingerprint", sender),
                    "to_fingerprint": friendship_data.get("to_fingerprint", ""),
                    "from_node_id": friendship_data.get("from_node_id", sender),
                    "to_node_id": friendship_data.get("to_node_id", ""),
                    "message": friendship_data.get("message", ""),
                    "timestamp": friendship_data.get("timestamp", time.time()),
                    "signature": friendship_data.get("signature", ""),
                    "requested_permissions": req_perms
                }
                print(f"🔍 DEBUG: Constructed request_data: {request_data}")
                
                # Appeler directement receive_friendship_request avec le Dict
                print(f"🔍 DEBUG: Calling receive_friendship_request with data: {request_data}")
                
                try:
                    result = friendship_system.receive_friendship_request(request_data)
                    print(f"🔍 DEBUG: receive_friendship_request returned: {result}")
                    
                    if result:
                        print(f"✅ Successfully integrated friendship request from {sender}")
                        
                        # Marquer comme traité
                        simple_protocol.mark_friendship_request_processed(
                            sender, 
                            friendship_data.get("request_id", "")
                        )
                        processed_count += 1
                    else:
                        print(f"❌ Failed to integrate friendship request from {sender} - function returned False")
                        
                except Exception as receive_error:
                    print(f"❌ Exception in receive_friendship_request: {receive_error}")
                    import traceback
                    traceback.print_exc()
                    print(f"❌ Failed to integrate friendship request from {sender}")
                    
        except Exception as e:
            print(f"❌ Error processing message from {req_info.get('sender', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()
    
    # Traiter les acceptations d'amitié
    pending_acceptances = simple_protocol.get_pending_friendship_acceptances()
    
    for acc_info in pending_acceptances:
        try:
            sender = acc_info["sender"]
            acceptance_data = acc_info["data"]
            
            print(f"🎉 Processing friendship acceptance from {sender}")
            
            # Récupérer les informations de l'acceptation
            request_id = acceptance_data.get("request_id", "")
            accepted_by_fingerprint = acceptance_data.get("accepted_by_fingerprint", sender)
            accepted_by_node_id = acceptance_data.get("accepted_by_node_id", sender)
            granted_permissions = acceptance_data.get("granted_permissions", {})
            
            # Créer une amitié automatiquement côté expéditeur
            # Car sa demande a été acceptée par l'autre nœud
            if accepted_by_fingerprint not in friendship_system.friendships:
                from friendship_protocol import Friendship, FriendshipStatus, FriendshipPermissions, PermissionLevel
                
                # Créer les permissions à partir des données reçues
                perms = FriendshipPermissions(
                    messaging=PermissionLevel(granted_permissions.get("messaging", "none")),
                    urn_access=PermissionLevel(granted_permissions.get("urn_access", "none")),
                    photo_sharing=PermissionLevel(granted_permissions.get("photo_sharing", "none")),
                    file_sharing=PermissionLevel(granted_permissions.get("file_sharing", "none")),
                    presence_info=PermissionLevel(granted_permissions.get("presence_info", "none"))
                )
                
                # Créer l'amitié acceptée
                friendship = Friendship(
                    friend_fingerprint=accepted_by_fingerprint,
                    friend_node_id=accepted_by_node_id,
                    status=FriendshipStatus.ACCEPTED,
                    permissions_granted=FriendshipPermissions.from_level(PermissionLevel.BASIC),
                    permissions_received=perms,
                    created_at=time.time(),
                    last_interaction=time.time()
                )
                
                friendship_system.friendships[accepted_by_fingerprint] = friendship
                friendship_system._save_friendships()
                
                print(f"✅ Automatically created friendship with {accepted_by_node_id}")
                processed_count += 1
                
            # Marquer comme traité
            simple_protocol.mark_friendship_acceptance_processed(
                sender, 
                request_id
            )
                
        except Exception as e:
            print(f"❌ Error processing friendship acceptance from {acc_info.get('sender', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()
            
    if processed_count > 0:
        print(f"🎉 Processed {processed_count} pending friendship requests/acceptances")
        
    return processed_count

def stop_simple_server():
    """Arrête le serveur simple"""
    global simple_server_socket
    if simple_server_socket:
        simple_server_socket.close()
        print("🛑 Simple Protocol server stopped")