# === Schrödinger Phoenix P2P : Distribution URN Révolutionnaire ===
# Intégration du système Schrödinger Phoenix avec réseau P2P pur
# Distribution et résurrection URN/Phantom via réseau décentralisé

import os
import sys
import json
import time
import hashlib
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Import du système Phantom URN révolutionnaire
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'phantom-images-demo'))
try:
    from schrodinger_phoenix_system import SchrodingerEngine, QuantumMatrix
    PHANTOM_URN_AVAILABLE = True
    print("✅ Phantom URN System with Schrödinger Phoenix component loaded")
except ImportError:
    print("⚠️ Phantom URN system not found - creating placeholder")
    PHANTOM_URN_AVAILABLE = False
    
    class QuantumMatrix:
        def __init__(self, data, metadata):
            self.data = data
            self.metadata = metadata
            
    class SchrodingerEngine:
        def __init__(self, cache_dir="./quantum_cache"):
            self.cache_dir = cache_dir
            
        async def generate_schrodinger_from_ashes(self, urn_file_path):
            print(f"⚠️ Placeholder: Would generate Schrödinger Phoenix from {urn_file_path}")
            return None
            
        async def resurrect_phoenix(self, quantum_matrix):
            print(f"⚠️ Placeholder: Would resurrect Phoenix from quantum matrix")
            return None

@dataclass
class P2PUrnRequest:
    """Requête URN via réseau P2P"""
    urn_id: str
    requester_fingerprint: str
    timestamp: float
    priority: int = 5  # 1-10
    resurrection_type: str = "full"  # "full", "preview", "metadata"
    
@dataclass
class P2PUrnResponse:
    """Réponse URN via réseau P2P"""
    urn_id: str
    provider_fingerprint: str
    available: bool
    quantum_matrix: Optional[Dict] = None
    metadata: Optional[Dict] = None
    timestamp: float = 0
    
class P2PPhantomUrnEngine:
    """
    Moteur Phantom URN distribué sur réseau P2P
    Le composant Schrödinger Phoenix permet la distribution et résurrection ultra-rapide d'URN
    """
    
    def __init__(self, node_fingerprint: str, p2p_network, cache_dir: str = "./p2p_quantum_cache"):
        self.node_fingerprint = node_fingerprint
        self.p2p_network = p2p_network
        self.cache_dir = cache_dir
        
        # Moteur Schrödinger Phoenix local (composant du système Phantom URN)
        self.local_engine = SchrodingerEngine(cache_dir)
        
        # Cache distribué URN
        self.local_urn_cache = {}      # URN disponibles localement
        self.network_urn_index = {}    # Index URN sur le réseau
        self.pending_requests = {}     # Requêtes en cours
        
        # Statistiques
        self.stats = {
            "local_resurrections": 0,
            "network_resurrections": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "network_queries": 0
        }
        
        os.makedirs(cache_dir, exist_ok=True)
        print(f"🔱 P2P Phantom URN Engine initialized")
        print(f"   Node: {node_fingerprint[:8]}...")
        print(f"   Cache: {cache_dir}")
        print(f"   🌐 Distributed Phantom URN with Schrödinger Phoenix ready!")
        
    async def index_local_urns(self, urn_directory: str):
        """Indexe les URN disponibles localement"""
        print(f"📋 Indexing local URNs from {urn_directory}...")
        
        if not os.path.exists(urn_directory):
            print(f"⚠️ URN directory not found: {urn_directory}")
            return
            
        urn_count = 0
        for filename in os.listdir(urn_directory):
            if filename.endswith('.orp'):
                urn_id = filename[:-4]  # Retirer .orp
                urn_path = os.path.join(urn_directory, filename)
                
                # Calcul hash pour vérification intégrité
                with open(urn_path, 'rb') as f:
                    content_hash = hashlib.sha256(f.read()).hexdigest()
                
                # Génération matrices quantiques si nécessaire
                try:
                    quantum_matrix = await self.local_engine.generate_schrodinger_from_ashes(urn_path)
                    
                    if quantum_matrix:
                        self.local_urn_cache[urn_id] = {
                            "file_path": urn_path,
                            "quantum_matrix": quantum_matrix,
                            "content_hash": content_hash,
                            "indexed_at": time.time(),
                            "resurrection_count": 0
                        }
                        urn_count += 1
                        
                except Exception as e:
                    print(f"⚠️ Error indexing URN {urn_id}: {e}")
                    
        print(f"✅ Indexed {urn_count} URNs for P2P distribution")
        
    async def resurrect_urn_p2p(self, urn_id: str, requester_info: Optional[Dict] = None) -> Optional[any]:
        """
        Résurrection URN via réseau P2P distribué
        Stratégie: Local d'abord, puis réseau P2P, puis génération
        """
        start_time = time.time()
        
        print(f"🔱 Resurrecting URN: {urn_id}")
        print(f"   Strategy: Local → P2P Network → Generation")
        
        # Étape 1: Vérification cache local
        if urn_id in self.local_urn_cache:
            print(f"⚡ Local cache HIT for {urn_id}")
            
            urn_data = self.local_urn_cache[urn_id]
            quantum_matrix = urn_data["quantum_matrix"]
            
            # Résurrection locale ultra-rapide
            try:
                result = await self.local_engine.resurrect_phoenix(quantum_matrix)
                
                if result:
                    urn_data["resurrection_count"] += 1
                    self.stats["local_resurrections"] += 1
                    self.stats["cache_hits"] += 1
                    
                    elapsed = time.time() - start_time
                    print(f"✅ Local resurrection completed in {elapsed:.2f}s")
                    return result
                    
            except Exception as e:
                print(f"⚠️ Local resurrection failed: {e}")
                
        # Étape 2: Recherche sur réseau P2P
        print(f"🌐 Searching URN {urn_id} on P2P network...")
        self.stats["network_queries"] += 1
        self.stats["cache_misses"] += 1
        
        network_result = await self._search_urn_on_network(urn_id)
        
        if network_result:
            print(f"🔍 URN found on network node: {network_result['provider'][:8]}...")
            
            # Demande de la matrice quantique
            quantum_matrix = await self._request_quantum_matrix(
                urn_id, 
                network_result['provider'],
                network_result['endpoint']
            )
            
            if quantum_matrix:
                # Cache local pour accès futurs
                self.local_urn_cache[urn_id] = {
                    "file_path": None,  # URN distant
                    "quantum_matrix": quantum_matrix,
                    "content_hash": network_result.get("content_hash"),
                    "indexed_at": time.time(),
                    "resurrection_count": 0,
                    "source": "p2p_network",
                    "provider": network_result['provider']
                }
                
                # Résurrection à partir de la matrice réseau
                try:
                    result = await self.local_engine.resurrect_phoenix(quantum_matrix)
                    
                    if result:
                        self.stats["network_resurrections"] += 1
                        elapsed = time.time() - start_time
                        print(f"✅ Network resurrection completed in {elapsed:.2f}s")
                        return result
                        
                except Exception as e:
                    print(f"⚠️ Network resurrection failed: {e}")
                    
        # Étape 3: Échec - URN introuvable
        print(f"❌ URN {urn_id} not found on P2P network")
        elapsed = time.time() - start_time
        print(f"   Search completed in {elapsed:.2f}s")
        return None
        
    async def _search_urn_on_network(self, urn_id: str) -> Optional[Dict]:
        """Recherche URN sur le réseau P2P"""
        # Création requête de recherche
        request = P2PUrnRequest(
            urn_id=urn_id,
            requester_fingerprint=self.node_fingerprint,
            timestamp=time.time()
        )
        
        # Diffusion requête à tous les nœuds connectés
        active_nodes = self.p2p_network.get_discovered_nodes()
        
        for node_fingerprint, node_info in active_nodes.items():
            try:
                # Envoi requête via connexion P2P directe
                response = await self._query_node_for_urn(node_info, request)
                
                if response and response.available:
                    return {
                        "provider": node_fingerprint,
                        "endpoint": node_info,
                        "content_hash": response.metadata.get("content_hash") if response.metadata else None
                    }
                    
            except Exception as e:
                print(f"⚠️ Error querying node {node_fingerprint[:8]}: {e}")
                
        return None
        
    async def _query_node_for_urn(self, node_info: Dict, request: P2PUrnRequest) -> Optional[P2PUrnResponse]:
        """Interroge un nœud spécifique pour un URN"""
        try:
            # Message de requête URN
            query_message = {
                "type": "urn_query",
                "urn_id": request.urn_id,
                "requester": request.requester_fingerprint,
                "timestamp": request.timestamp,
                "resurrection_type": request.resurrection_type
            }
            
            # Envoi via connexion P2P sécurisée
            # (Implémentation dépend du système de connexions P2P)
            # Pour cette version, simulation de la réponse
            
            # TODO: Intégrer avec le système de connexions P2P réel
            print(f"🔍 Querying node for URN {request.urn_id}...")
            
            # Simulation réponse (à remplacer par vraie communication P2P)
            return None
            
        except Exception as e:
            print(f"❌ Node query error: {e}")
            return None
            
    async def _request_quantum_matrix(self, urn_id: str, provider_fingerprint: str, provider_endpoint: Dict) -> Optional[QuantumMatrix]:
        """Demande la matrice quantique à un nœud fournisseur"""
        try:
            # Message de demande de matrice
            matrix_request = {
                "type": "quantum_matrix_request",
                "urn_id": urn_id,
                "requester": self.node_fingerprint,
                "timestamp": time.time()
            }
            
            # TODO: Intégrer avec le système de connexions P2P réel
            print(f"🔱 Requesting quantum matrix for {urn_id} from {provider_fingerprint[:8]}...")
            
            # Simulation (à remplacer par vraie communication P2P)
            return None
            
        except Exception as e:
            print(f"❌ Matrix request error: {e}")
            return None
            
    def handle_urn_query(self, query_message: Dict, requester_fingerprint: str) -> Dict:
        """Traite une requête URN d'un autre nœud"""
        urn_id = query_message.get("urn_id")
        
        if not urn_id:
            return {"available": False, "error": "missing_urn_id"}
            
        # Vérification disponibilité locale
        if urn_id in self.local_urn_cache:
            urn_data = self.local_urn_cache[urn_id]
            
            response = {
                "available": True,
                "urn_id": urn_id,
                "provider": self.node_fingerprint,
                "metadata": {
                    "content_hash": urn_data.get("content_hash"),
                    "indexed_at": urn_data.get("indexed_at"),
                    "resurrection_count": urn_data.get("resurrection_count", 0)
                },
                "timestamp": time.time()
            }
            
            print(f"📤 URN {urn_id} available - responding to {requester_fingerprint[:8]}...")
            return response
        else:
            return {
                "available": False,
                "urn_id": urn_id,
                "provider": self.node_fingerprint,
                "timestamp": time.time()
            }
            
    def handle_matrix_request(self, request_message: Dict, requester_fingerprint: str) -> Optional[Dict]:
        """Traite une demande de matrice quantique"""
        urn_id = request_message.get("urn_id")
        
        if not urn_id or urn_id not in self.local_urn_cache:
            return None
            
        urn_data = self.local_urn_cache[urn_id]
        quantum_matrix = urn_data["quantum_matrix"]
        
        # Sérialisation de la matrice pour envoi P2P
        try:
            matrix_data = {
                "urn_id": urn_id,
                "quantum_matrix": {
                    "data": quantum_matrix.data.tolist() if hasattr(quantum_matrix.data, 'tolist') else quantum_matrix.data,
                    "metadata": quantum_matrix.metadata if hasattr(quantum_matrix, 'metadata') else {}
                },
                "provider": self.node_fingerprint,
                "timestamp": time.time()
            }
            
            print(f"🔱 Sending quantum matrix for {urn_id} to {requester_fingerprint[:8]}...")
            return matrix_data
            
        except Exception as e:
            print(f"❌ Error serializing quantum matrix: {e}")
            return None
            
    def get_p2p_stats(self) -> Dict:
        """Statistiques du système P2P Schrödinger"""
        return {
            "node_fingerprint": self.node_fingerprint,
            "local_urns": len(self.local_urn_cache),
            "network_index": len(self.network_urn_index),
            "pending_requests": len(self.pending_requests),
            "statistics": self.stats,
            "cache_efficiency": (
                self.stats["cache_hits"] / 
                (self.stats["cache_hits"] + self.stats["cache_misses"])
                if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0 
                else 0
            )
        }
        
    def announce_new_urn(self, urn_id: str):
        """Annonce un nouvel URN au réseau P2P"""
        if urn_id in self.local_urn_cache:
            announcement = {
                "type": "urn_announcement",
                "urn_id": urn_id,
                "provider": self.node_fingerprint,
                "timestamp": time.time(),
                "metadata": {
                    "content_hash": self.local_urn_cache[urn_id].get("content_hash"),
                    "indexed_at": self.local_urn_cache[urn_id].get("indexed_at")
                }
            }
            
            # TODO: Diffuser l'annonce sur le réseau P2P
            print(f"📢 Announcing new URN {urn_id} to P2P network...")
            
class P2PUrnDistributionManager:
    """
    Gestionnaire de distribution URN sur réseau P2P
    Coordonne la réplication et la disponibilité des URN via le système Phantom URN
    """
    
    def __init__(self, p2p_phantom_urn: P2PPhantomUrnEngine):
        self.p2p_phantom_urn = p2p_phantom_urn
        self.replication_factor = 3  # Réplication sur 3 nœuds minimum
        self.distribution_strategy = "closest_nodes"  # ou "random", "sector_based"
        
    async def distribute_urn(self, urn_id: str, target_nodes: Optional[List[str]] = None):
        """Distribue un URN sur plusieurs nœuds pour redondance"""
        if urn_id not in self.p2p_phantom_urn.local_urn_cache:
            print(f"❌ URN {urn_id} not available locally for distribution")
            return False
            
        # Sélection nœuds cibles
        if not target_nodes:
            target_nodes = self._select_distribution_nodes()
            
        urn_data = self.p2p_phantom_urn.local_urn_cache[urn_id]
        quantum_matrix = urn_data["quantum_matrix"]
        
        distribution_success = 0
        
        for node_fingerprint in target_nodes[:self.replication_factor]:
            try:
                success = await self._send_urn_to_node(urn_id, quantum_matrix, node_fingerprint)
                if success:
                    distribution_success += 1
                    
            except Exception as e:
                print(f"⚠️ Distribution to {node_fingerprint[:8]} failed: {e}")
                
        print(f"📊 URN {urn_id} distributed to {distribution_success}/{self.replication_factor} nodes")
        return distribution_success >= 2  # Succès si au moins 2 réplications
        
    def _select_distribution_nodes(self) -> List[str]:
        """Sélectionne les nœuds pour distribution selon la stratégie"""
        active_nodes = self.p2p_phantom_urn.p2p_network.get_discovered_nodes()
        
        if self.distribution_strategy == "closest_nodes":
            # Sélection par proximité/latence (simplified)
            return list(active_nodes.keys())[:self.replication_factor]
        elif self.distribution_strategy == "random":
            import random
            nodes = list(active_nodes.keys())
            random.shuffle(nodes)
            return nodes[:self.replication_factor]
        else:
            return list(active_nodes.keys())[:self.replication_factor]
            
    async def _send_urn_to_node(self, urn_id: str, quantum_matrix, target_node: str) -> bool:
        """Envoie URN à un nœud spécifique"""
        try:
            # Message de distribution
            distribution_message = {
                "type": "urn_distribution",
                "urn_id": urn_id,
                "quantum_matrix": {
                    "data": quantum_matrix.data.tolist() if hasattr(quantum_matrix.data, 'tolist') else quantum_matrix.data,
                    "metadata": quantum_matrix.metadata if hasattr(quantum_matrix, 'metadata') else {}
                },
                "sender": self.p2p_phantom_urn.node_fingerprint,
                "timestamp": time.time()
            }
            
            # TODO: Envoyer via connexion P2P sécurisée
            print(f"📤 Distributing URN {urn_id} to {target_node[:8]}...")
            
            # Simulation succès (à remplacer par vraie communication)
            return True
            
        except Exception as e:
            print(f"❌ URN distribution error: {e}")
            return False