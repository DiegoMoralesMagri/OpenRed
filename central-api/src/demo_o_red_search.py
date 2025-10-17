#!/usr/bin/env python3
"""
O-RedSearch Demo Complet
Démonstration du système de découverte passive révolutionnaire
"""

import time
import threading
from o_red_search import NodeBeacon, BeaconBroadcaster, PassiveBeaconScanner, ORedSearch
from web_visibility import WebVisibilityEngine

def create_demo_node(node_id: str, sector: str, services: list, lat: float, lng: float, activity: int, web_port: int):
    """Crée un nœud de démo complet"""
    
    # Configuration nœud
    node = NodeBeacon(
        node_id=node_id,
        location={"lat": lat, "lng": lng, "elevation": 35},
        services=services,
        activity_level=activity,
        sector=sector,
        connection_info={
            "ip": f"192.168.1.{web_port - 8000}",
            "ports": {"http": web_port, "p2p": web_port + 1000},
            "protocols": ["tcp", "udp", "webrtc"]
        }
    )
    
    # Démarrer beacon
    broadcaster = BeaconBroadcaster(node, broadcast_interval=10)  # Plus fréquent pour demo
    broadcaster.start_broadcasting()
    
    # Démarrer scanner
    scanner = PassiveBeaconScanner(cache_duration=60)  # Cache plus court pour demo
    scanner.start_scanning()
    
    # Démarrer moteur de recherche
    search_engine = ORedSearch(scanner)
    
    # Démarrer visibilité web
    web_engine = WebVisibilityEngine(node, port=web_port)
    web_engine.start_web_server()
    
    return {
        "node": node,
        "broadcaster": broadcaster, 
        "scanner": scanner,
        "search": search_engine,
        "web": web_engine
    }

def demo_multi_nodes():
    """Démonstration avec plusieurs nœuds"""
    
    print("🚀 O-RedSearch Multi-Node Demo")
    print("=" * 50)
    
    # Créer plusieurs nœuds
    nodes = []
    
    # Nœud Paris Tech
    nodes.append(create_demo_node(
        "node_paris_tech_001", 
        "tech", 
        ["storage", "compute", "ai"],
        48.8566, 2.3522, 
        95, 8081
    ))
    
    # Nœud Lyon Health  
    nodes.append(create_demo_node(
        "node_lyon_health_001",
        "health",
        ["storage", "backup", "analysis"], 
        45.7640, 4.8357,
        87, 8082
    ))
    
    # Nœud Marseille Education
    nodes.append(create_demo_node(
        "node_marseille_edu_001",
        "education", 
        ["content", "streaming", "storage"],
        43.2965, 5.3698,
        92, 8083
    ))
    
    # Nœud Bordeaux Finance
    nodes.append(create_demo_node(
        "node_bordeaux_fin_001",
        "finance",
        ["compute", "security", "audit"],
        44.8378, -0.5792,
        89, 8084
    ))
    
    print(f"✅ {len(nodes)} nœuds créés et démarrés")
    print("\n🌐 Pages web disponibles:")
    for i, node_data in enumerate(nodes):
        port = 8081 + i
        print(f"  - {node_data['node'].node_id}: http://localhost:{port}/")
    
    # Attendre découvertes
    print(f"\n⏳ Attente des découvertes (30 secondes)...")
    time.sleep(30)
    
    # Tests de recherche
    print(f"\n🔍 TESTS DE RECHERCHE")
    print("=" * 30)
    
    search_engine = nodes[0]["search"]  # Utiliser le premier nœud pour chercher
    
    # Test 1: Secteur tech
    print(f"\n1️⃣ Recherche: Secteur 'tech'")
    results = search_engine.search(sector="tech")
    print(f"   Résultats: {len(results)} nœuds")
    for node in results:
        print(f"   - {node['node_id']}: {node['activity_level']}%")
    
    # Test 2: Services storage
    print(f"\n2️⃣ Recherche: Service 'storage'")
    results = search_engine.search(services=["storage"])
    print(f"   Résultats: {len(results)} nœuds")
    for node in results:
        print(f"   - {node['node_id']}: {node['services']}")
    
    # Test 3: Activité élevée
    print(f"\n3️⃣ Recherche: Activité > 90%")
    results = search_engine.search(min_activity=90)
    print(f"   Résultats: {len(results)} nœuds") 
    for node in results:
        print(f"   - {node['node_id']}: {node['activity_level']}%")
    
    # Test 4: Recherche géographique (près de Paris)
    print(f"\n4️⃣ Recherche: Dans 500km de Paris")
    results = search_engine.search(
        max_distance_km=500,
        my_location={"lat": 48.8566, "lng": 2.3522}
    )
    print(f"   Résultats: {len(results)} nœuds")
    for node in results:
        print(f"   - {node['node_id']}: {node.get('location', {})}")
    
    # Test 5: Recherche combinée
    print(f"\n5️⃣ Recherche: Tech + Storage + Activité > 85%")
    results = search_engine.search(
        sector="tech",
        services=["storage"],
        min_activity=85
    )
    print(f"   Résultats: {len(results)} nœuds")
    for node in results:
        print(f"   - {node['node_id']}: {node['sector']} | {node['services']} | {node['activity_level']}%")
    
    # Statistiques globales
    print(f"\n📊 STATISTIQUES GLOBALES")
    print("=" * 30)
    
    for i, node_data in enumerate(nodes):
        stats = node_data["search"].get_stats()
        web_stats = node_data["web"].get_web_stats()
        
        print(f"\n🔸 {node_data['node'].node_id}:")
        print(f"   Cache: {stats['nodes_in_cache']} nœuds")
        print(f"   Scanner: {dict(stats['scanner_stats'])}")
        print(f"   Web: {web_stats['page_views']} vues, {len(web_stats['bot_visits'])} bots")
    
    print(f"\n✨ Démonstration terminée!")
    print(f"💡 O-RedSearch révolutionne la découverte P2P!")
    print(f"🌐 Visitez les pages web pour voir l'indexation automatique")
    
    return nodes

if __name__ == "__main__":
    try:
        demo_nodes = demo_multi_nodes()
        
        print(f"\n🎯 Demo interactive - Tapez 'q' pour quitter")
        while True:
            cmd = input(f"\n> ").strip().lower()
            if cmd == 'q':
                break
            elif cmd == 'stats':
                for node_data in demo_nodes:
                    stats = node_data["search"].get_stats()
                    print(f"{node_data['node'].node_id}: {stats['nodes_in_cache']} nœuds en cache")
            elif cmd.startswith('search '):
                sector = cmd.split(' ', 1)[1] if len(cmd.split(' ', 1)) > 1 else "tech"
                results = demo_nodes[0]["search"].search(sector=sector)
                print(f"Nœuds {sector}: {len(results)}")
                for node in results[:3]:
                    print(f"  - {node['node_id']}")
            else:
                print("Commandes: 'stats', 'search <secteur>', 'q'")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Arrêt de la démonstration...")
    
    print(f"🏁 Demo terminée!")