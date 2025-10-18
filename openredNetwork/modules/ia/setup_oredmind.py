#!/usr/bin/env python3
"""
O-RedMind Setup et Configuration
===============================

Script d'installation et configuration complète pour O-RedMind
avec intégration Ollama optimisée.

Auteur: Système OpenRed 2025
Licence: MIT - Souveraineté Numérique Totale
"""

import os
import sys
import json
import time
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional

def print_header():
    """Affiche l'en-tête de setup"""
    print("🧠 O-RedMind Setup & Configuration")
    print("=" * 50)
    print("🔒 100% Local • 🦙 Powered by Ollama • 🎯 Souveraineté Totale")
    print()

def check_ollama_status():
    """Vérifie le status d'Ollama"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return True, models
    except:
        pass
    return False, []

def get_recommended_models():
    """Retourne les modèles recommandés pour O-RedMind"""
    return {
        'phi3': {
            'size': '2.3GB',
            'description': 'Modèle Microsoft Phi-3, excellent pour conversations',
            'use_case': 'Chat général, raisonnement',
            'ram_required': '4GB'
        },
        'llama3.2': {
            'size': '2.0GB', 
            'description': 'Meta Llama 3.2 compact et performant',
            'use_case': 'Chat, créativité, analyse',
            'ram_required': '4GB'
        },
        'mistral': {
            'size': '4.1GB',
            'description': 'Mistral 7B, excellent équilibre performance/taille',
            'use_case': 'Chat avancé, raisonnement complexe',
            'ram_required': '8GB'
        },
        'codellama': {
            'size': '3.8GB',
            'description': 'Spécialisé programmation et code',
            'use_case': 'Développement, debugging, explication code',
            'ram_required': '8GB'
        }
    }

def suggest_models_for_system():
    """Suggère des modèles selon les ressources système"""
    import psutil
    
    # Mémoire RAM disponible (en GB)
    ram_gb = psutil.virtual_memory().total / (1024**3)
    
    print(f"💾 RAM système détectée: {ram_gb:.1f}GB")
    
    if ram_gb >= 16:
        return ['mistral', 'codellama', 'phi3']
    elif ram_gb >= 8:
        return ['phi3', 'llama3.2', 'mistral']
    else:
        return ['phi3', 'llama3.2']

def install_model(model_name: str):
    """Installe un modèle Ollama"""
    print(f"🦙 Installation de {model_name}...")
    
    try:
        process = subprocess.Popen(
            ['ollama', 'pull', model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"   {output.strip()}")
        
        if process.returncode == 0:
            print(f"   ✅ {model_name} installé avec succès")
            return True
        else:
            print(f"   ❌ Erreur installation {model_name}")
            return False
            
    except FileNotFoundError:
        print("   ❌ Ollama non trouvé dans le PATH")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def create_oredmind_config():
    """Crée la configuration O-RedMind"""
    config_dir = Path.home() / ".openred" / "config"
    config_dir.mkdir(exist_ok=True, parents=True)
    
    config = {
        'oredmind': {
            'version': '1.0.0',
            'mode': 'ollama_enhanced',
            'ollama': {
                'enabled': True,
                'base_url': 'http://localhost:11434',
                'preferred_model': None,
                'fallback_enabled': True
            },
            'privacy': {
                'learning_mode': 'private_only',
                'data_retention_days': 365,
                'consent_required': True
            },
            'profiles': {
                'default': 'Professionnel',
                'adaptation_enabled': True
            }
        }
    }
    
    config_file = config_dir / "oredmind.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuration sauvée: {config_file}")
    return config

def main():
    """Setup principal"""
    print_header()
    
    # 1. Vérification Ollama
    print("1️⃣ Vérification d'Ollama...")
    ollama_connected, current_models = check_ollama_status()
    
    if not ollama_connected:
        print("❌ Ollama non connecté")
        print("\n💡 Instructions:")
        print("   1. Vérifiez qu'Ollama est installé: https://ollama.ai")
        print("   2. Démarrez Ollama: ollama serve")
        print("   3. Relancez ce script")
        return False
    
    print("✅ Ollama connecté")
    print(f"📚 Modèles actuels: {len(current_models)}")
    
    for model in current_models:
        print(f"   • {model['name']}")
    
    # 2. Suggestion de modèles
    print("\n2️⃣ Recommandations de modèles...")
    
    try:
        suggested = suggest_models_for_system()
        recommended = get_recommended_models()
        
        print("🎯 Modèles recommandés pour votre système:")
        for model_name in suggested:
            if model_name in recommended:
                info = recommended[model_name]
                print(f"   ⭐ {model_name} ({info['size']}) - {info['description']}")
                print(f"      Usage: {info['use_case']}")
        
        # Vérification des modèles déjà installés
        current_model_names = [m['name'] for m in current_models]
        missing_models = []
        
        for model_name in suggested:
            model_found = any(model_name in name for name in current_model_names)
            if not model_found:
                missing_models.append(model_name)
        
        if missing_models:
            print(f"\n📥 Modèles manquants recommandés: {', '.join(missing_models)}")
            
            install_choice = input(f"\n🤔 Installer les modèles manquants ? (o/N): ").lower()
            
            if install_choice in ['o', 'oui', 'y', 'yes']:
                print("\n📦 Installation en cours...")
                
                for model_name in missing_models:
                    if install_model(model_name):
                        time.sleep(1)  # Pause entre installations
                    else:
                        print(f"⚠️  Installation de {model_name} échouée")
            else:
                print("⏭️  Installation des modèles ignorée")
        else:
            print("✅ Tous les modèles recommandés sont disponibles")
    
    except ImportError:
        print("⚠️  psutil non disponible, suggestion automatique impossible")
    
    # 3. Configuration O-RedMind
    print("\n3️⃣ Configuration O-RedMind...")
    config = create_oredmind_config()
    
    # Détection du meilleur modèle disponible
    ollama_connected, updated_models = check_ollama_status()
    if updated_models:
        # Priorité aux modèles recommandés
        preferred_model = None
        for model_name in ['phi3', 'mistral', 'llama3.2']:
            for model in updated_models:
                if model_name in model['name']:
                    preferred_model = model['name']
                    break
            if preferred_model:
                break
        
        if not preferred_model:
            preferred_model = updated_models[0]['name']
        
        config['oredmind']['ollama']['preferred_model'] = preferred_model
        print(f"🎯 Modèle préféré configuré: {preferred_model}")
    
    # 4. Test de fonctionnement
    print("\n4️⃣ Test de fonctionnement...")
    
    try:
        from ollama_integration import OllamaIntegration
        
        ollama = OllamaIntegration()
        
        if ollama.is_connected:
            print("✅ Intégration Ollama fonctionnelle")
            
            # Test avec le modèle configuré
            recommended = ollama.get_recommended_model(['chat'])
            if recommended:
                ollama.set_model(recommended)
                
                print(f"🧪 Test avec {recommended}...")
                test_response = ollama.simple_chat(
                    "Dis bonjour en français en une phrase.",
                    "Tu es O-RedMind, réponds de manière concise."
                )
                
                if test_response and not test_response.startswith('❌'):
                    print(f"   ✅ Test réussi: {test_response[:50]}...")
                else:
                    print("   ⚠️  Test de réponse échoué")
            else:
                print("   ⚠️  Aucun modèle recommandé disponible")
        else:
            print("❌ Intégration Ollama non fonctionnelle")
    
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    
    # 5. Instructions finales
    print("\n🎉 Setup O-RedMind terminé !")
    print("\n🚀 Prochaines étapes:")
    print("   1. Lancez O-RedMind: python interface_web.py")
    print("   2. Ouvrez: http://localhost:5000")
    print("   3. Commencez à chatter avec votre IA souveraine !")
    
    print("\n💡 Conseils:")
    print("   • O-RedMind fonctionne 100% en local")
    print("   • Vos données restent sur votre machine")
    print("   • Aucune connexion internet requise après setup")
    print("   • Adaptez votre profil dans les paramètres")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ O-RedMind est prêt à révolutionner votre IA personnelle !")
        else:
            print("\n❌ Setup incomplet, consultez les instructions ci-dessus")
    except KeyboardInterrupt:
        print("\n\n⏸️  Setup interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("📞 Consultez la documentation ou créez une issue GitHub")