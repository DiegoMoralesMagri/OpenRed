# === OpenRed P2P Platform - Social Messaging Helper ===
# Helper simple pour envoi de messages sociaux via P2P

import json


async def send_friendship_request_p2p_simple(p2p_node, target_fingerprint: str, request) -> bool:
    """Envoie demande d'amitié via P2P avec mise en queue"""
    
    if not p2p_node:
        print(f"❌ P2P node not available")
        return False
    
    try:
        print(f"🔍 Attempting to send friendship request to {target_fingerprint}")
        
        # Vérifier si le nœud cible est découvert
        discovered = p2p_node.lighthouse.get_discovered_nodes()
        print(f"🔍 Discovered nodes: {list(discovered.keys())}")
        
        if target_fingerprint not in discovered:
            print(f"❌ Target node {target_fingerprint} not discovered")
            return False
        
        # Préparer données de la demande
        request_data = {
            "type": "friendship_request",
            "request_id": request.request_id,
            "from_fingerprint": request.from_fingerprint,
            "to_fingerprint": request.to_fingerprint,
            "from_node_id": request.from_node_id,
            "to_node_id": request.to_node_id,
            "message": request.message,
            "timestamp": request.timestamp,
            "signature": request.signature,
            "requested_permissions": {
                "messaging": request.requested_permissions.messaging,
                "urn_access": request.requested_permissions.urn_access,
                "photo_sharing": request.requested_permissions.photo_sharing,
                "file_sharing": request.requested_permissions.file_sharing,
                "presence_info": request.requested_permissions.presence_info
            }
        }
        
        print(f"📬 Queuing friendship request for {target_fingerprint}")
        
        # Utiliser le nouveau système de mise en queue
        p2p_node.queue_social_message(target_fingerprint, request_data)
        
        print(f"✅ Friendship request queued and connection initiated")
        return True
        
    except Exception as e:
        print(f"❌ Error sending friendship request P2P: {e}")
        import traceback
        traceback.print_exc()
        return False