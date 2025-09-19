# FR: Fichier: main.py — Entrypoint du client nœud P2P
# EN: File: main.py — Entry point for the P2P node client
# ES: Archivo: main.py — Punto de entrada del cliente nodo P2P
# ZH: 文件: main.py — P2P 节点客户端入口

# Client Nœud P2P O-Red - Point d'entrée principal

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional
import uvloop  # Pour de meilleures performances asyncio

from .config import NodeConfig, load_config
from .p2p.node import ORedP2PNode
from .crypto.identity import ORedIdentityManager
from .ai.local_mind import LocalAIMind
from .storage.secure_storage import SecureStorage
from .protocols.ored_protocol import ORedProtocolHandler

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("ored-node.log")
    ]
)
logger = logging.getLogger(__name__)

class ORedNodeClient:
    """Client nœud P2P pour le réseau O-Red décentralisé"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = load_config(config_path)
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Composants principaux
        self.identity_manager: Optional[ORedIdentityManager] = None
        self.p2p_node: Optional[ORedP2PNode] = None
        self.local_ai: Optional[LocalAIMind] = None
        self.secure_storage: Optional[SecureStorage] = None
        self.protocol_handler: Optional[ORedProtocolHandler] = None
    
    async def initialize(self):
        """Initialise tous les composants du nœud"""
        try:
            logger.info("🚀 Initialisation du nœud O-Red...")
            
            # 1. Gestionnaire d'identité O-RedID
            self.identity_manager = ORedIdentityManager(self.config)
            await self.identity_manager.initialize()
            logger.info("✅ Gestionnaire d'identité O-RedID initialisé")
            
            # 2. Stockage sécurisé
            self.secure_storage = SecureStorage(
                self.config.storage_path,
                self.identity_manager.get_encryption_key()
            )
            await self.secure_storage.initialize()
            logger.info("✅ Stockage sécurisé initialisé")
            
            # 3. IA locale O-RedMind
            if self.config.ai_enabled:
                self.local_ai = LocalAIMind(
                    self.config.ai_config,
                    self.secure_storage
                )
                await self.local_ai.initialize()
                logger.info("✅ IA locale O-RedMind initialisée")
            
            # 4. Gestionnaire de protocoles O-Red
            self.protocol_handler = ORedProtocolHandler(
                self.identity_manager,
                self.secure_storage,
                self.local_ai
            )
            await self.protocol_handler.initialize()
            logger.info("✅ Gestionnaire de protocoles O-Red initialisé")
            
            # 5. Nœud P2P
            self.p2p_node = ORedP2PNode(
                self.config,
                self.identity_manager,
                self.protocol_handler
            )
            await self.p2p_node.initialize()
            logger.info("✅ Nœud P2P initialisé")
            
            logger.info("🌟 Nœud O-Red initialisé avec succès!")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation: {e}")
            raise
    
    async def start(self):
        """Démarre le nœud et tous ses services"""
        try:
            logger.info("🔄 Démarrage du nœud O-Red...")
            
            # Démarrage du nœud P2P
            await self.p2p_node.start()
            logger.info("✅ Nœud P2P démarré")
            
            # Enregistrement sur l'API centrale
            await self.p2p_node.register_with_central_api()
            logger.info("✅ Nœud enregistré sur l'API centrale")
            
            # Démarrage des services
            tasks = []
            
            # Service de heartbeat
            tasks.append(asyncio.create_task(self._heartbeat_service()))
            
            # Service de découverte de pairs
            tasks.append(asyncio.create_task(self._peer_discovery_service()))
            
            # Service de synchronisation
            tasks.append(asyncio.create_task(self._synchronization_service()))
            
            # Service de maintenance
            tasks.append(asyncio.create_task(self._maintenance_service()))
            
            # Si IA activée, démarrage des services IA
            if self.local_ai:
                tasks.append(asyncio.create_task(self._ai_service()))
            
            self.is_running = True
            logger.info("🌐 Nœud O-Red opérationnel et connecté au réseau")
            
            # Affichage des informations du nœud
            await self._display_node_info()
            
            # Attente de l'arrêt
            await self.shutdown_event.wait()
            
            # Arrêt propre
            logger.info("🔄 Arrêt des services...")
            for task in tasks:
                task.cancel()
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage: {e}")
            raise
    
    async def shutdown(self):
        """Arrêt propre du nœud"""
        try:
            logger.info("🛑 Arrêt du nœud O-Red...")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Désenregistrement de l'API centrale
            if self.p2p_node:
                await self.p2p_node.unregister_from_central_api()
            
            # Arrêt des composants dans l'ordre inverse
            if self.p2p_node:
                await self.p2p_node.stop()
            
            if self.local_ai:
                await self.local_ai.shutdown()
            
            if self.secure_storage:
                await self.secure_storage.close()
            
            logger.info("✅ Nœud O-Red arrêté proprement")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'arrêt: {e}")
    
    async def _heartbeat_service(self):
        """Service de heartbeat vers l'API centrale"""
        while self.is_running:
            try:
                await self.p2p_node.send_heartbeat()
                await asyncio.sleep(self.config.heartbeat_interval)
            except Exception as e:
                logger.error(f"❌ Erreur heartbeat: {e}")
                await asyncio.sleep(60)  # Retry dans 1 minute
    
    async def _peer_discovery_service(self):
        """Service de découverte et connexion aux pairs"""
        while self.is_running:
            try:
                await self.p2p_node.discover_and_connect_peers()
                await asyncio.sleep(self.config.peer_discovery_interval)
            except Exception as e:
                logger.error(f"❌ Erreur découverte pairs: {e}")
                await asyncio.sleep(300)  # Retry dans 5 minutes
    
    async def _synchronization_service(self):
        """Service de synchronisation des données"""
        while self.is_running:
            try:
                await self.p2p_node.synchronize_data()
                await asyncio.sleep(self.config.sync_interval)
            except Exception as e:
                logger.error(f"❌ Erreur synchronisation: {e}")
                await asyncio.sleep(600)  # Retry dans 10 minutes
    
    async def _maintenance_service(self):
        """Service de maintenance du nœud"""
        while self.is_running:
            try:
                # Nettoyage des connexions fermées
                await self.p2p_node.cleanup_dead_connections()
                
                # Mise à jour des métriques
                await self.p2p_node.update_metrics()
                
                # Optimisation des performances
                await self._optimize_performance()
                
                await asyncio.sleep(self.config.maintenance_interval)
            except Exception as e:
                logger.error(f"❌ Erreur maintenance: {e}")
                await asyncio.sleep(3600)  # Retry dans 1 heure
    
    async def _ai_service(self):
        """Service de traitement IA distribué"""
        while self.is_running:
            try:
                # Traitement des requêtes IA en attente
                await self.local_ai.process_pending_requests()
                
                # Participation au calcul distribué
                await self.local_ai.participate_in_distributed_computing()
                
                # Mise à jour des modèles
                await self.local_ai.update_models_if_needed()
                
                await asyncio.sleep(30)  # Vérification toutes les 30 secondes
            except Exception as e:
                logger.error(f"❌ Erreur service IA: {e}")
                await asyncio.sleep(60)
    
    async def _optimize_performance(self):
        """Optimise les performances du nœud"""
        try:
            # Optimisation mémoire
            if self.secure_storage:
                await self.secure_storage.optimize_cache()
            
            # Optimisation réseau
            if self.p2p_node:
                await self.p2p_node.optimize_connections()
            
            # Optimisation IA
            if self.local_ai:
                await self.local_ai.optimize_models()
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation: {e}")
    
    async def _display_node_info(self):
        """Affiche les informations du nœud"""
        try:
            node_info = await self.p2p_node.get_node_info()
            
            logger.info("📊 Informations du nœud O-Red:")
            logger.info(f"   🆔 ID: {node_info['node_id']}")
            logger.info(f"   🌐 Adresse: {node_info['address']}")
            logger.info(f"   🔗 Pairs connectés: {node_info['connected_peers']}")
            logger.info(f"   💾 Stockage disponible: {node_info['storage_available']} GB")
            logger.info(f"   🤖 IA activée: {'Oui' if self.local_ai else 'Non'}")
            logger.info(f"   🔒 Niveau sécurité: {self.config.security_level}")
            
        except Exception as e:
            logger.error(f"❌ Erreur affichage infos: {e}")

def setup_signal_handlers(node_client: ORedNodeClient):
    """Configure les gestionnaires de signaux pour un arrêt propre"""
    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} reçu, arrêt en cours...")
        asyncio.create_task(node_client.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Point d'entrée principal"""
    try:
        # Installation d'uvloop pour de meilleures performances
        if sys.platform != 'win32':
            uvloop.install()
        
        # Création du client nœud
        config_path = sys.argv[1] if len(sys.argv) > 1 else None
        node_client = ORedNodeClient(config_path)
        
        # Configuration des gestionnaires de signaux
        setup_signal_handlers(node_client)
        
        # Initialisation et démarrage
        await node_client.initialize()
        await node_client.start()
        
    except KeyboardInterrupt:
        logger.info("Interruption clavier détectée")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        sys.exit(1)
    finally:
        if 'node_client' in locals():
            await node_client.shutdown()

if __name__ == "__main__":
    asyncio.run(main())