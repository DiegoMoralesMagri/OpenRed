#!/usr/bin/env python3
"""
O-RedMind Launcher
==================

Lanceur principal pour O-RedMind avec interface de sélection
et gestion complète du système d'IA personnel.

Auteur: Système OpenRed 2025
Licence: MIT - Souveraineté Numérique Totale
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
import webbrowser
from dataclasses import dataclass

# Ajout du path pour les imports locaux
sys.path.append(str(Path(__file__).parent))

try:
    import oredmind_core
    from oredmind_core import ORedMindCore
    import moteur_intelligence_locale
    from moteur_intelligence_locale import LocalLanguageModel, MultimodalProcessor, ReasoningType
    import interface_web
    from interface_web import ORedMindWebInterface, main as web_main
except ImportError as e:
    print(f"⚠️  Modules O-RedMind non trouvés: {e}")
    print("   Certaines fonctionnalités seront limitées.")
    oredmind_core = None
    moteur_intelligence_locale = None
    interface_web = None

# Configuration des logs
log_dir = Path.home() / ".openred" / "logs"
log_dir.mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "oredmind.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """Status du système O-RedMind"""
    core_available: bool
    web_interface: bool
    models_loaded: bool
    storage_ok: bool
    network_mode: str
    last_update: float

class ORedMindLauncher:
    """Lanceur principal pour O-RedMind"""
    
    def __init__(self):
        self.fort_path = Path.home() / ".openred"
        self.config_path = self.fort_path / "config"
        self.logs_path = self.fort_path / "logs"
        self.models_path = self.fort_path / "models"
        
        self.oredmind_core = None
        self.web_interface = None
        self.system_status = SystemStatus(
            core_available=False,
            web_interface=False,
            models_loaded=False,
            storage_ok=False,
            network_mode="local",
            last_update=time.time()
        )
        
        self._ensure_directories()
        self._check_system_status()
    
    def _ensure_directories(self):
        """Assure que tous les dossiers nécessaires existent"""
        directories = [
            self.fort_path,
            self.config_path,
            self.logs_path,
            self.models_path,
            self.fort_path / "uploads",
            self.fort_path / "exports",
            self.fort_path / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"📁 Dossiers O-RedMind initialisés dans {self.fort_path}")
    
    def _check_system_status(self):
        """Vérifie le status du système"""
        try:
            # Vérification du stockage
            self.system_status.storage_ok = self.fort_path.exists() and os.access(self.fort_path, os.W_OK)
            
            # Vérification du core O-RedMind
            try:
                from oredmind_core import ORedMindCore
                self.oredmind_core = ORedMindCore(self.fort_path)
                self.system_status.core_available = True
                logger.info("✅ O-RedMind Core disponible")
            except Exception as e:
                logger.warning(f"⚠️  O-RedMind Core non disponible: {e}")
                self.system_status.core_available = False
            
            # Vérification des modèles
            model_files = list(self.models_path.glob("*.json"))
            self.system_status.models_loaded = len(model_files) > 0
            
            # Vérification de l'interface web
            try:
                from interface_web import ORedMindWebInterface
                self.system_status.web_interface = True
                logger.info("✅ Interface Web disponible")
            except Exception as e:
                logger.warning(f"⚠️  Interface Web non disponible: {e}")
                self.system_status.web_interface = False
            
            self.system_status.last_update = time.time()
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification système: {e}")
    
    def show_status(self):
        """Affiche le status du système"""
        print("\n🧠 O-RedMind - Status Système")
        print("=" * 50)
        print(f"📍 Fort OpenRed: {self.fort_path}")
        print(f"🔧 Core O-RedMind: {'✅ OK' if self.system_status.core_available else '❌ NOK'}")
        print(f"🌐 Interface Web: {'✅ OK' if self.system_status.web_interface else '❌ NOK'}")
        print(f"🧠 Modèles IA: {'✅ Chargés' if self.system_status.models_loaded else '⚠️  Non chargés'}")
        print(f"💾 Stockage: {'✅ OK' if self.system_status.storage_ok else '❌ NOK'}")
        print(f"🌍 Mode Réseau: {self.system_status.network_mode}")
        print(f"⏰ Dernière vérif: {datetime.fromtimestamp(self.system_status.last_update).strftime('%H:%M:%S')}")
        
        if self.system_status.models_loaded:
            model_files = list(self.models_path.glob("*.json"))
            print(f"📚 Modèles trouvés: {len(model_files)}")
            for model_file in model_files[:3]:  # Affiche les 3 premiers
                print(f"   - {model_file.name}")
            if len(model_files) > 3:
                print(f"   ... et {len(model_files) - 3} autres")
    
    def launch_web_interface(self, host: str = "localhost", port: int = 5000, open_browser: bool = True):
        """Lance l'interface web"""
        print("\n🌐 Lancement de l'Interface Web O-RedMind")
        print("=" * 50)
        
        if not self.system_status.web_interface:
            print("❌ Interface Web non disponible")
            print("   Vérifiez l'installation des dépendances (Flask, SocketIO)")
            return False
        
        url = f"http://{host}:{port}"
        print(f"🔗 URL: {url}")
        print(f"🔒 Mode: Local et Privé")
        print("📱 Compatible Desktop et Mobile")
        print("\n⚡ Fonctionnalités disponibles:")
        print("   • Chat intelligent multimodal")
        print("   • Upload et analyse de fichiers")
        print("   • Adaptation aux profils utilisateur")
        print("   • Apprentissage personnalisé")
        print("   • 100% privé et local")
        
        if open_browser:
            print(f"\n🚀 Ouverture automatique du navigateur...")
            # Délai pour laisser le serveur démarrer
            threading.Timer(2.0, lambda: webbrowser.open(url)).start()
        
        try:
            # Import et lancement de l'interface web
            from interface_web import main as web_main
            web_main()
            
        except KeyboardInterrupt:
            print("\n👋 Arrêt de l'interface web")
            return True
        except Exception as e:
            print(f"❌ Erreur lors du lancement: {e}")
            return False
    
    def launch_cli_interface(self):
        """Lance l'interface en ligne de commande"""
        print("\n💻 Interface CLI O-RedMind")
        print("=" * 40)
        print("Tapez 'aide' pour voir les commandes disponibles")
        print("Tapez 'quit' ou Ctrl+C pour quitter")
        print()
        
        if not self.system_status.core_available:
            print("⚠️  Mode CLI limité (Core non disponible)")
        
        try:
            while True:
                user_input = input("O-RedMind> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if user_input.lower() in ['aide', 'help', 'h']:
                    self._show_cli_help()
                    continue
                
                if user_input.lower() == 'status':
                    self.show_status()
                    continue
                
                if user_input.lower().startswith('profil '):
                    profile = user_input[7:].strip()
                    print(f"🎭 Profil changé vers: {profile}")
                    continue
                
                # Traitement avec O-RedMind
                if self.system_status.core_available:
                    response = self._process_cli_input(user_input)
                    print(f"🤖 {response}")
                else:
                    # Mode fallback simple
                    response = self._simple_response(user_input)
                    print(f"💬 {response}")
        
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
        except Exception as e:
            print(f"❌ Erreur CLI: {e}")
    
    def _show_cli_help(self):
        """Affiche l'aide CLI"""
        print("\n📋 Commandes disponibles:")
        print("  aide/help         - Affiche cette aide")
        print("  status            - Status du système")
        print("  profil <nom>      - Change de profil")
        print("  quit/exit         - Quitte l'interface")
        print("\n💬 Sinon, tapez simplement votre question ou demande.")
    
    def _process_cli_input(self, user_input: str) -> str:
        """Traite l'entrée utilisateur avec O-RedMind"""
        try:
            if self.oredmind_core:
                # Utilisation du core O-RedMind
                from oredmind_core import ConversationStyle
                
                style = ConversationStyle(
                    formality=0.7,
                    creativity=0.6,
                    detail_level=0.8,
                    empathy=0.7,
                    profile_adaptation="CLI"
                )
                
                response = self.oredmind_core.process_conversation(
                    user_input,
                    "cli_user",
                    "CLI",
                    style,
                    []
                )
                
                return f"{response.content}"
            else:
                return self._simple_response(user_input)
                
        except Exception as e:
            logger.error(f"Erreur traitement CLI: {e}")
            return f"Désolé, erreur de traitement: {str(e)}"
    
    def _simple_response(self, user_input: str) -> str:
        """Réponse simple en mode fallback"""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['bonjour', 'salut', 'hello']):
            return "Bonjour ! Comment puis-je vous aider aujourd'hui ?"
        
        elif any(word in user_lower for word in ['merci', 'thanks']):
            return "De rien ! N'hésitez pas si vous avez d'autres questions."
        
        elif any(word in user_lower for word in ['qui es-tu', 'qui êtes-vous', 'what are you']):
            return "Je suis O-RedMind, votre assistant IA personnel et privé, développé selon les principes OpenRed."
        
        elif any(word in user_lower for word in ['aide', 'help']):
            return "Je peux vous aider avec diverses tâches : répondre à des questions, analyser du contenu, générer du texte créatif, etc."
        
        elif any(word in user_lower for word in ['temps', 'heure', 'time']):
            return f"Il est actuellement {datetime.now().strftime('%H:%M:%S')}."
        
        elif any(word in user_lower for word in ['date', 'jour']):
            return f"Nous sommes le {datetime.now().strftime('%d/%m/%Y')}."
        
        else:
            return f"Vous avez dit : '{user_input}'. Je comprends votre message. En mode complet, je pourrais vous donner une réponse plus détaillée."
    
    def run_diagnostics(self):
        """Lance les diagnostics système"""
        print("\n🔧 Diagnostics Système O-RedMind")
        print("=" * 45)
        
        # Test des dossiers
        print("📁 Vérification des dossiers...")
        for path_name, path_obj in [
            ("Fort OpenRed", self.fort_path),
            ("Configuration", self.config_path),
            ("Logs", self.logs_path),
            ("Modèles", self.models_path)
        ]:
            exists = path_obj.exists()
            writable = os.access(path_obj, os.W_OK) if exists else False
            status = "✅ OK" if exists and writable else "❌ NOK"
            print(f"   {path_name}: {status} ({path_obj})")
        
        # Test des modules
        print("\n📦 Vérification des modules...")
        modules_to_test = [
            ("oredmind_core", "O-RedMind Core"),
            ("moteur_intelligence_locale", "Moteur Intelligence Locale"),
            ("interface_web", "Interface Web"),
            ("flask", "Flask (Web)"),
            ("flask_socketio", "SocketIO (WebSocket)"),
            ("PIL", "Pillow (Images)"),
            ("numpy", "NumPy (Calculs)")
        ]
        
        for module_name, display_name in modules_to_test:
            try:
                __import__(module_name)
                print(f"   {display_name}: ✅ OK")
            except ImportError:
                print(f"   {display_name}: ❌ Manquant")
        
        # Test de performance simple
        print("\n⚡ Test de performance...")
        start_time = time.time()
        
        # Test création de fichier temporaire
        test_file = self.fort_path / "test_perf.tmp"
        try:
            with open(test_file, 'w') as f:
                f.write("test" * 1000)
            test_file.unlink()
            write_time = time.time() - start_time
            print(f"   Écriture disque: ✅ {write_time:.3f}s")
        except Exception as e:
            print(f"   Écriture disque: ❌ {e}")
        
        # Test mémoire (simulation)
        try:
            test_data = list(range(100000))
            memory_time = time.time() - start_time - write_time
            print(f"   Allocation mémoire: ✅ {memory_time:.3f}s")
        except Exception as e:
            print(f"   Allocation mémoire: ❌ {e}")
        
        total_time = time.time() - start_time
        print(f"\n⏱️  Diagnostics terminés en {total_time:.2f}s")
        
        # Recommandations
        print("\n💡 Recommandations:")
        if not self.system_status.core_available:
            print("   - Installer les dépendances manquantes")
        if not self.system_status.models_loaded:
            print("   - Lancer une première session pour créer les modèles")
        if total_time > 2.0:
            print("   - Performance système lente, vérifier les ressources")
        else:
            print("   - Système optimisé pour O-RedMind ✅")

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="O-RedMind - Intelligence Artificielle Personnelle et Privée",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python oredmind_launcher.py                    # Interface de sélection
  python oredmind_launcher.py --web              # Interface web
  python oredmind_launcher.py --cli              # Interface CLI
  python oredmind_launcher.py --status           # Status système
  python oredmind_launcher.py --diagnostics      # Diagnostics complets
        """
    )
    
    parser.add_argument('--web', action='store_true',
                        help='Lance l\'interface web')
    parser.add_argument('--cli', action='store_true',
                        help='Lance l\'interface CLI')
    parser.add_argument('--status', action='store_true',
                        help='Affiche le status système')
    parser.add_argument('--diagnostics', action='store_true',
                        help='Lance les diagnostics système')
    parser.add_argument('--host', default='localhost',
                        help='Adresse pour l\'interface web (défaut: localhost)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port pour l\'interface web (défaut: 5000)')
    parser.add_argument('--no-browser', action='store_true',
                        help='Ne pas ouvrir le navigateur automatiquement')
    
    args = parser.parse_args()
    
    # Initialisation du lanceur
    launcher = ORedMindLauncher()
    
    # Gestion des arguments
    if args.status:
        launcher.show_status()
        return
    
    if args.diagnostics:
        launcher.run_diagnostics()
        return
    
    if args.cli:
        launcher.launch_cli_interface()
        return
    
    if args.web:
        launcher.launch_web_interface(
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser
        )
        return
    
    # Interface de sélection par défaut
    print("🧠 O-RedMind - Intelligence Artificielle Personnelle")
    print("=" * 55)
    print("🔒 100% Privé • 🎯 Personnalisé • 🚀 Multimodal")
    print()
    
    launcher.show_status()
    
    print("\n🎛️  Mode de lancement:")
    print("1. Interface Web (recommandé)")
    print("2. Interface CLI (ligne de commande)")
    print("3. Status et diagnostics")
    print("4. Quitter")
    
    try:
        while True:
            choice = input("\nVotre choix (1-4): ").strip()
            
            if choice == '1':
                launcher.launch_web_interface(
                    host=args.host,
                    port=args.port,
                    open_browser=not args.no_browser
                )
                break
            elif choice == '2':
                launcher.launch_cli_interface()
                break
            elif choice == '3':
                launcher.run_diagnostics()
                break
            elif choice == '4':
                print("👋 Au revoir !")
                break
            else:
                print("❌ Choix invalide, recommencez.")
    
    except KeyboardInterrupt:
        print("\n👋 Au revoir !")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()