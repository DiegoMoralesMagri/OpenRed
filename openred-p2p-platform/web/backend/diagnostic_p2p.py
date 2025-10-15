# === OpenRed P2P Platform - Diagnostic Tool ===
# Script pour tester la découverte et communication P2P

import os
import sys
import time
import asyncio

# Ajouter le path du projet
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from openred_p2p_node import OpenRedP2PNode

async def test_p2p_discovery():
    """Test de découverte P2P"""
    print("🔍 === Test de Découverte P2P ===")
    
    # Configuration test
    node_id = "diagnostic_node"
    p2p_port = 8090
    
    # Créer nœud de test
    print(f"📡 Création nœud diagnostic sur port {p2p_port}")
    test_node = OpenRedP2PNode(
        node_id=node_id,
        sector="diagnostic",
        p2p_port=p2p_port
    )
    
    try:
        # Démarrer le nœud
        print("🚀 Démarrage nœud diagnostic...")
        await test_node.start_node()
        
        # Attendre quelques secondes pour la découverte
        print("⏱️ Attente découverte (10 secondes)...")
        for i in range(10):
            await asyncio.sleep(1)
            discovered = test_node.lighthouse.get_discovered_nodes()
            print(f"   {i+1}s: {len(discovered)} nœuds découverts")
            
            if discovered:
                for fp, info in discovered.items():
                    beacon = info["beacon"]
                    p2p_port = beacon.p2p_endpoint["port"]  # Extraire du dictionnaire
                    print(f"      - {beacon.node_id} ({fp[:12]}...) sur {info['ip']}:{p2p_port}")
        
        # Test final
        final_discovered = test_node.lighthouse.get_discovered_nodes()
        print(f"\n✅ Découverte terminée: {len(final_discovered)} nœuds trouvés")
        
        if len(final_discovered) >= 2:
            print("🎉 SUCCESS: Au moins 2 nœuds se découvrent !")
            
            # Test de connexion
            for fp, info in final_discovered.items():
                beacon = info["beacon"]
                print(f"\n🔗 Test connexion vers {beacon.node_id}...")
                
                try:
                    target_ip = info["ip"]
                    target_port = beacon.p2p_endpoint["port"]  # Extraire du dictionnaire
                    
                    print(f"   Tentative connexion {target_ip}:{target_port}")
                    session_id = test_node.p2p_connection.connect_to_peer(target_ip, target_port, fp)
                    
                    if session_id:
                        print(f"   ✅ Connexion réussie: {session_id}")
                        
                        # Test envoi message
                        test_message = {
                            "type": "diagnostic_test",
                            "message": "Hello from diagnostic tool!",
                            "timestamp": time.time()
                        }
                        
                        success = test_node.p2p_connection.send_secure_message(session_id, test_message)
                        print(f"   📤 Message test envoyé: {success}")
                        
                    else:
                        print(f"   ❌ Connexion échouée")
                        
                except Exception as e:
                    print(f"   ❌ Erreur connexion: {e}")
                    
        else:
            print("❌ ÉCHEC: Pas assez de nœuds découverts")
            print("   Vérifiez que les autres nœuds sont actifs")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🛑 Arrêt nœud diagnostic...")
        if hasattr(test_node, 'stop_node'):
            await test_node.stop_node()

if __name__ == "__main__":
    print("🚀 OpenRed P2P Diagnostic Tool")
    print("   Ce script teste la découverte et communication P2P")
    print("   Assurez-vous que les autres nœuds sont actifs !\n")
    
    asyncio.run(test_p2p_discovery())