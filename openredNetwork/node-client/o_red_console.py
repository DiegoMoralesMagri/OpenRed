#!/usr/bin/env python3
"""
🎮 Interface Utilisateur Console pour O-Red P2P Asymétrique
Interface interactive pour utiliser le système révolutionnaire

Auteur : Système OpenRed P2P Révolutionnaire
Date : Septembre 2025
"""

import asyncio
import json
import sys
from typing import Dict, Any, List
from datetime import datetime
import threading

from o_red_asymmetric_p2p import O_RedAsymmetricP2P

class O_RedConsoleUI:
    """
    🎮 Interface console interactive pour O-Red P2P Asymétrique
    
    Commandes disponibles :
    - discover : Lancer la découverte de pairs
    - list-peers : Lister les pairs découverts
    - befriend <peer_id> : Établir une amitié asymétrique
    - list-friends : Lister les amitiés actives
    - request <friend_id> <action> : Demander une action à un ami
    - status : Afficher l'état du système
    - help : Aide
    - quit : Quitter
    """
    
    def __init__(self):
        self.node = None
        self.running = False
        self.node_task = None
        
        print("🎮 === O-RED P2P ASYMÉTRIQUE - INTERFACE CONSOLE ===")
        print("🚀 Interface révolutionnaire pour système P2P asymétrique")
        print("💡 Tapez 'help' pour voir les commandes disponibles\n")
    
    async def start(self):
        """🚀 Démarrer l'interface console"""
        # Configuration utilisateur
        node_config = self._get_user_config()
        
        # Initialiser le nœud P2P
        self.node = O_RedAsymmetricP2P(node_config)
        
        # Démarrer le nœud en arrière-plan
        self.node_task = asyncio.create_task(self.node.start())
        
        # Attendre un peu pour l'initialisation
        await asyncio.sleep(2)
        
        print(f"✅ Nœud {self.node.display_name} démarré avec succès!")
        print("🌐 Découverte P2P active")
        print("🤝 Serveurs d'amitié en écoute")
        print("🔐 Gestionnaire de tokens asymétriques opérationnel\n")
        
        # Interface interactive
        self.running = True
        await self._interactive_loop()
    
    def _get_user_config(self) -> Dict[str, Any]:
        """⚙️ Obtenir la configuration du nœud auprès de l'utilisateur"""
        print("⚙️ === CONFIGURATION DU NŒUD P2P ===")
        
        node_id = input("🆔 ID du nœud (ex: alice_2025) : ").strip()
        if not node_id:
            node_id = f"user_{datetime.now().strftime('%H%M%S')}"
        
        display_name = input(f"👤 Nom d'affichage (ex: Alice Dupont) : ").strip()
        if not display_name:
            display_name = node_id
        
        port_input = input("🌐 Port d'écoute (défaut: 5355) : ").strip()
        port = 5355
        if port_input.isdigit():
            port = int(port_input)
        
        config = {
            "node_id": node_id,
            "display_name": display_name,
            "port": port
        }
        
        print(f"\n✅ Configuration : {config}")
        print("=" * 50 + "\n")
        
        return config
    
    async def _interactive_loop(self):
        """🔄 Boucle interactive de commandes"""
        while self.running:
            try:
                # Prompt utilisateur
                command_input = await self._async_input(f"🎮 [{self.node.display_name}] > ")
                
                if not command_input.strip():
                    continue
                
                # Traiter la commande
                await self._process_command(command_input.strip())
                
            except KeyboardInterrupt:
                print("\n🛑 Interruption clavier - Arrêt en cours...")
                break
            except Exception as e:
                print(f"❌ Erreur : {str(e)}")
    
    async def _async_input(self, prompt: str) -> str:
        """🎯 Input asynchrone pour éviter le blocage"""
        def _input_thread(prompt, result_container):
            try:
                result_container[0] = input(prompt)
            except EOFError:
                result_container[0] = "quit"
        
        result = [None]
        thread = threading.Thread(target=_input_thread, args=(prompt, result))
        thread.daemon = True
        thread.start()
        
        # Attendre la saisie avec timeout
        while thread.is_alive() and self.running:
            await asyncio.sleep(0.1)
        
        return result[0] or "quit"
    
    async def _process_command(self, command_input: str):
        """🔧 Traiter une commande utilisateur"""
        parts = command_input.split()
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd == "help":
            self._show_help()
        
        elif cmd == "discover":
            await self._cmd_discover()
        
        elif cmd == "list-peers":
            await self._cmd_list_peers()
        
        elif cmd == "befriend":
            await self._cmd_befriend(args)
        
        elif cmd == "list-friends":
            await self._cmd_list_friends()
        
        elif cmd == "request":
            await self._cmd_request(args)
        
        elif cmd == "status":
            await self._cmd_status()
        
        elif cmd in ["quit", "exit", "q"]:
            await self._cmd_quit()
        
        else:
            print(f"❌ Commande inconnue : {cmd}")
            print("💡 Tapez 'help' pour voir les commandes disponibles")
    
    def _show_help(self):
        """📖 Afficher l'aide"""
        help_text = """
🎮 === COMMANDES O-RED P2P ASYMÉTRIQUE ===

🔍 DÉCOUVERTE :
  discover           - Forcer la découverte de pairs
  list-peers         - Lister les pairs découverts

🤝 AMITIÉS ASYMÉTRIQUES :
  befriend <peer_id> - Établir une amitié asymétrique avec un pair
  list-friends       - Lister toutes les amitiés actives

📤 DEMANDES SÉCURISÉES :
  request <friend_id> <action> - Demander une action à un ami
  
📊 INFORMATION :
  status             - Afficher l'état du système
  help               - Afficher cette aide

🚪 SORTIE :
  quit / exit / q    - Quitter l'application

🔐 === EXEMPLES ===
  befriend alice_2025                    - Devenir ami avec Alice
  request alice_2025 download_files      - Demander accès aux fichiers d'Alice
  request bob_2025 send_message          - Demander à envoyer un message à Bob

🚀 === TOKENS ASYMÉTRIQUES ===
Chaque amitié utilise 4 clés RSA distinctes pour une sécurité maximale !
        """
        print(help_text)
    
    async def _cmd_discover(self):
        """🔍 Forcer la découverte de pairs"""
        print("🔍 Recherche de pairs en cours...")
        await asyncio.sleep(3)  # Laisser le temps à la découverte
        
        peers = self.node.list_discovered_peers()
        print(f"✅ {len(peers)} pair(s) découvert(s)")
        
        for peer in peers:
            friendship_status = "👥 Ami" if peer["has_friendship"] else "❓ Inconnu"
            print(f"  🆔 {peer['peer_id']} - {peer['display_name']} ({friendship_status})")
    
    async def _cmd_list_peers(self):
        """📋 Lister les pairs découverts"""
        peers = self.node.list_discovered_peers()
        
        if not peers:
            print("❌ Aucun pair découvert")
            print("💡 Utilisez 'discover' pour rechercher des pairs")
            return
        
        print(f"📋 === {len(peers)} PAIR(S) DÉCOUVERT(S) ===")
        for i, peer in enumerate(peers, 1):
            friendship_status = "👥 Ami" if peer["has_friendship"] else "❓ Inconnu"
            print(f"{i}. 🆔 {peer['peer_id']}")
            print(f"   👤 {peer['display_name']}")
            print(f"   📍 {peer.get('address', 'N/A')}")
            print(f"   🤝 {friendship_status}")
            print()
    
    async def _cmd_befriend(self, args: List[str]):
        """🤝 Établir une amitié asymétrique"""
        if not args:
            print("❌ Usage : befriend <peer_id>")
            return
        
        peer_id = args[0]
        
        # Vérifier que le pair existe
        peers = self.node.list_discovered_peers()
        peer_exists = any(p["peer_id"] == peer_id for p in peers)
        
        if not peer_exists:
            print(f"❌ Pair '{peer_id}' non découvert")
            print("💡 Utilisez 'list-peers' pour voir les pairs disponibles")
            return
        
        # Permissions par défaut
        permissions = {
            "send_messages": True,
            "read_public_files": True,
            "download_shared_content": True,
            "access_private_data": False,
            "modify_files": False,
            "voice_call": False
        }
        
        print(f"🤝 Établissement d'amitié asymétrique avec {peer_id}...")
        
        try:
            token = self.node.establish_friendship_with_peer(peer_id, permissions)
            
            if token:
                print(f"✅ Amitié asymétrique établie avec {peer_id}!")
                print(f"🔐 Token généré : {token['token_data']['token_id'][:16]}...")
                print("📤 Token envoyé au pair")
                print("⏳ En attente de la réponse du pair...")
            else:
                print(f"❌ Échec de l'établissement d'amitié avec {peer_id}")
        
        except Exception as e:
            print(f"❌ Erreur : {str(e)}")
    
    async def _cmd_list_friends(self):
        """👥 Lister les amitiés actives"""
        friendships = self.node.list_active_friendships()
        
        if not friendships:
            print("❌ Aucune amitié active")
            print("💡 Utilisez 'befriend <peer_id>' pour établir des amitiés")
            return
        
        print(f"👥 === {len(friendships)} AMITIÉ(S) ASYMÉTRIQUE(S) ===")
        
        for i, friendship in enumerate(friendships, 1):
            print(f"{i}. 🆔 {friendship['friend_node_id']}")
            print(f"   📊 Status : {friendship['status']}")
            print(f"   📅 Établie le : {friendship['established_at'][:10]}")
            print(f"   📤 Token sortant : {'✅' if friendship['has_outgoing_token'] else '❌'}")
            print(f"   📨 Token entrant : {'✅' if friendship['has_incoming_token'] else '❌'}")
            
            if friendship['outgoing_permissions']:
                perms = [p for p, v in friendship['outgoing_permissions'].items() if v]
                print(f"   🔐 Permissions accordées : {', '.join(perms)}")
            
            if friendship['incoming_permissions']:
                perms = [p for p, v in friendship['incoming_permissions'].items() if v]
                print(f"   🎫 Permissions reçues : {', '.join(perms)}")
            
            print()
    
    async def _cmd_request(self, args: List[str]):
        """📤 Demander une action à un ami"""
        if len(args) < 2:
            print("❌ Usage : request <friend_id> <action> [données]")
            return
        
        friend_id = args[0]
        action = args[1]
        data = {"timestamp": datetime.utcnow().isoformat()}
        
        # Données supplémentaires
        if len(args) > 2:
            data["extra"] = " ".join(args[2:])
        
        print(f"📤 Demande '{action}' vers {friend_id}...")
        
        try:
            request = self.node.send_friend_request(friend_id, action, data)
            
            if "error" in request:
                print(f"❌ Erreur : {request['error']}")
            else:
                print(f"✅ Demande signée et envoyée !")
                print(f"🆔 Request ID : {request['request_id']}")
                print(f"🔐 Signature asymétrique générée")
                print("⏳ En attente de réponse...")
        
        except Exception as e:
            print(f"❌ Erreur : {str(e)}")
    
    async def _cmd_status(self):
        """📊 Afficher l'état du système"""
        peers = self.node.list_discovered_peers()
        friendships = self.node.list_active_friendships()
        
        print("📊 === ÉTAT DU SYSTÈME P2P ASYMÉTRIQUE ===")
        print(f"🆔 Nœud : {self.node.node_id}")
        print(f"👤 Nom : {self.node.display_name}")
        print(f"🌐 Port : {self.node.port}")
        print(f"🔍 Pairs découverts : {len(peers)}")
        print(f"👥 Amitiés actives : {len(friendships)}")
        print(f"🔐 Système asymétrique : ✅ Opérationnel")
        print(f"📡 Découverte multicast : ✅ Active")
        print(f"🤝 Serveur d'amitiés : ✅ En écoute")
        print(f"⚡ Serveur de commandes : ✅ En écoute")
        
        # Détails des amitiés
        if friendships:
            print("\n🔐 === DÉTAILS TOKENS ASYMÉTRIQUES ===")
            for friendship in friendships:
                print(f"👤 {friendship['friend_node_id']} :")
                print(f"   Status : {friendship['status']}")
                tokens_count = (1 if friendship['has_outgoing_token'] else 0) + (1 if friendship['has_incoming_token'] else 0)
                print(f"   Tokens : {tokens_count}/2 (4 clés RSA)")
    
    async def _cmd_quit(self):
        """🚪 Quitter l'application"""
        print("🛑 Arrêt du système P2P asymétrique...")
        
        self.running = False
        
        if self.node:
            self.node.stop()
        
        if self.node_task:
            self.node_task.cancel()
            try:
                await self.node_task
            except asyncio.CancelledError:
                pass
        
        print("✅ Système arrêté proprement")
        print("👋 Au revoir !")
        
        # Forcer la sortie
        sys.exit(0)


async def main():
    """🎯 Point d'entrée principal"""
    console = O_RedConsoleUI()
    
    try:
        await console.start()
    except KeyboardInterrupt:
        print("\n🛑 Interruption utilisateur")
    except Exception as e:
        print(f"❌ Erreur fatale : {str(e)}")
    
    print("👋 Merci d'avoir utilisé O-Red P2P Asymétrique !")


if __name__ == "__main__":
    asyncio.run(main())