#!/usr/bin/env python3
"""
O-RedMind Ollama Integration
============================

Intégration native avec Ollama pour des modèles de langage
100% locaux et souverains selon le Manifeste OpenRed.

Auteur: Système OpenRed 2025
Licence: MIT - Souveraineté Numérique Totale
"""

import requests
import json
import time
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass
import threading
import os
import platform

logger = logging.getLogger(__name__)

@dataclass
class OllamaModel:
    """Modèle Ollama disponible"""
    name: str
    size: str
    description: str
    capabilities: List[str]
    recommended_ram: str
    language_support: List[str]

@dataclass
class ChatMessage:
    """Message de chat pour Ollama"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float

class OllamaIntegration:
    """Intégration native avec Ollama pour O-RedMind"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.current_model = None
        self.available_models = []
        self.is_connected = False
        self.conversation_history = []
        
        # Modèles recommandés pour O-RedMind
        self.recommended_models = {
            'phi3': OllamaModel(
                name='phi3',
                size='2.3GB',
                description='Modèle Microsoft Phi-3 optimisé, excellent pour conversations',
                capabilities=['chat', 'raisonnement', 'code'],
                recommended_ram='4GB',
                language_support=['français', 'anglais', 'code']
            ),
            'llama3.2': OllamaModel(
                name='llama3.2',
                size='2.0GB',
                description='Meta Llama 3.2 compact et performant',
                capabilities=['chat', 'créativité', 'analyse'],
                recommended_ram='4GB',
                language_support=['français', 'anglais', 'multilingue']
            ),
            'mistral': OllamaModel(
                name='mistral',
                size='4.1GB',
                description='Mistral 7B, excellent équilibre performance/taille',
                capabilities=['chat', 'raisonnement', 'créativité', 'code'],
                recommended_ram='8GB',
                language_support=['français', 'anglais', 'code', 'multilingue']
            ),
            'codellama': OllamaModel(
                name='codellama',
                size='3.8GB',
                description='Spécialisé dans la programmation et le code',
                capabilities=['code', 'debugging', 'explication'],
                recommended_ram='8GB',
                language_support=['python', 'javascript', 'java', 'c++', 'rust']
            ),
            'qwen2': OllamaModel(
                name='qwen2',
                size='4.4GB',
                description='Alibaba Qwen2, multilingue et performant',
                capabilities=['chat', 'multilingue', 'raisonnement'],
                recommended_ram='8GB',
                language_support=['français', 'anglais', 'chinois', 'multilingue']
            )
        }
        
        self._check_ollama_status()
    
    def _check_ollama_status(self) -> bool:
        """Vérifie si Ollama est disponible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            self.is_connected = response.status_code == 200
            
            if self.is_connected:
                self.available_models = self._parse_available_models(response.json())
                logger.info(f"✅ Ollama connecté - {len(self.available_models)} modèles disponibles")
            else:
                logger.warning("⚠️  Ollama non accessible")
                
            return self.is_connected
            
        except requests.exceptions.RequestException as e:
            self.is_connected = False
            logger.warning(f"⚠️  Ollama non disponible: {e}")
            return False
    
    def _parse_available_models(self, response_data: Dict) -> List[str]:
        """Parse les modèles disponibles depuis la réponse Ollama"""
        models = []
        if 'models' in response_data:
            for model in response_data['models']:
                models.append(model['name'])
        return models
    
    def is_ollama_installed(self) -> bool:
        """Vérifie si Ollama est installé sur le système"""
        return shutil.which('ollama') is not None
    
    def install_ollama_instructions(self) -> Dict[str, str]:
        """Retourne les instructions d'installation d'Ollama"""
        system = platform.system().lower()
        
        instructions = {
            'windows': 'Téléchargez Ollama depuis https://ollama.ai et exécutez le programme d\'installation',
            'darwin': 'Téléchargez Ollama depuis https://ollama.ai ou utilisez: brew install ollama',
            'linux': 'curl -fsSL https://ollama.ai/install.sh | sh'
        }
        
        return {
            'system': system,
            'instruction': instructions.get(system, instructions['linux']),
            'url': 'https://ollama.ai',
            'recommended_models': list(self.recommended_models.keys())
        }
    
    def pull_model(self, model_name: str) -> Iterator[Dict[str, Any]]:
        """Télécharge un modèle Ollama avec suivi de progression"""
        if not self.is_connected:
            yield {'error': 'Ollama non connecté'}
            return
        
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={'name': model_name},
                stream=True,
                timeout=300
            )
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        yield data
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            yield {'error': f'Erreur téléchargement: {str(e)}'}
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Liste tous les modèles disponibles"""
        if not self.is_connected:
            return []
        
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = []
                
                for model in data.get('models', []):
                    model_info = {
                        'name': model['name'],
                        'size': model.get('size', 0),
                        'modified': model.get('modified', ''),
                        'is_recommended': any(rec in model['name'] for rec in self.recommended_models.keys())
                    }
                    
                    # Ajout des infos recommandées si disponibles
                    for rec_name, rec_model in self.recommended_models.items():
                        if rec_name in model['name']:
                            model_info.update({
                                'description': rec_model.description,
                                'capabilities': rec_model.capabilities,
                                'recommended_ram': rec_model.recommended_ram,
                                'language_support': rec_model.language_support
                            })
                            break
                    
                    models.append(model_info)
                
                return models
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur liste modèles: {e}")
            return []
    
    def set_model(self, model_name: str) -> bool:
        """Définit le modèle actuel"""
        if model_name in self.available_models:
            self.current_model = model_name
            logger.info(f"📝 Modèle sélectionné: {model_name}")
            return True
        else:
            logger.warning(f"⚠️  Modèle non disponible: {model_name}")
            return False
    
    def chat(self, message: str, system_prompt: Optional[str] = None, 
             temperature: float = 0.7, max_tokens: int = 2000) -> Iterator[str]:
        """Chat avec le modèle Ollama en streaming"""
        if not self.is_connected or not self.current_model:
            yield "❌ Ollama non connecté ou modèle non sélectionné"
            return
        
        # Préparation des messages
        messages = []
        
        # Ajout du prompt système si fourni
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # Ajout de l'historique récent (5 derniers messages)
        recent_history = self.conversation_history[-10:]  # 5 paires user/assistant
        messages.extend([
            {'role': msg.role, 'content': msg.content} 
            for msg in recent_history
        ])
        
        # Ajout du message actuel
        messages.append({
            'role': 'user',
            'content': message
        })
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    'model': self.current_model,
                    'messages': messages,
                    'stream': True,
                    'options': {
                        'temperature': temperature,
                        'num_predict': max_tokens
                    }
                },
                stream=True,
                timeout=60
            )
            
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        
                        if 'message' in data and 'content' in data['message']:
                            content = data['message']['content']
                            full_response += content
                            yield content
                        
                        if data.get('done', False):
                            # Sauvegarde dans l'historique
                            self.conversation_history.append(
                                ChatMessage('user', message, time.time())
                            )
                            self.conversation_history.append(
                                ChatMessage('assistant', full_response, time.time())
                            )
                            
                            # Limite l'historique
                            if len(self.conversation_history) > 20:
                                self.conversation_history = self.conversation_history[-20:]
                            
                            break
                            
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            yield f"❌ Erreur communication: {str(e)}"
    
    def simple_chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Chat simple non-streamé"""
        response_parts = []
        for chunk in self.chat(message, system_prompt):
            response_parts.append(chunk)
        return ''.join(response_parts)
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations détaillées d'un modèle"""
        if not self.is_connected:
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={'name': model_name}
            )
            
            if response.status_code == 200:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur info modèle: {e}")
            return None
    
    def delete_model(self, model_name: str) -> bool:
        """Supprime un modèle"""
        if not self.is_connected:
            return False
        
        try:
            response = requests.delete(
                f"{self.base_url}/api/delete",
                json={'name': model_name}
            )
            
            if response.status_code == 200:
                self.available_models = [m for m in self.available_models if m != model_name]
                if self.current_model == model_name:
                    self.current_model = None
                return True
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur suppression modèle: {e}")
            return False
    
    def get_recommended_model(self, capabilities: List[str] = None) -> Optional[str]:
        """Recommande un modèle selon les capacités demandées"""
        if not capabilities:
            capabilities = ['chat']
        
        # Recherche du meilleur modèle disponible
        for model_name, model_info in self.recommended_models.items():
            if model_name in self.available_models:
                if any(cap in model_info.capabilities for cap in capabilities):
                    return model_name
        
        # Fallback sur le premier modèle disponible
        return self.available_models[0] if self.available_models else None
    
    def clear_conversation(self):
        """Efface l'historique de conversation"""
        self.conversation_history.clear()
        logger.info("🗑️  Historique de conversation effacé")
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le status complet d'Ollama"""
        return {
            'connected': self.is_connected,
            'base_url': self.base_url,
            'current_model': self.current_model,
            'available_models': self.available_models,
            'recommended_models': list(self.recommended_models.keys()),
            'conversation_length': len(self.conversation_history),
            'ollama_installed': self.is_ollama_installed()
        }

def main():
    """Test de l'intégration Ollama"""
    print("🦙 O-RedMind Ollama Integration")
    print("=" * 45)
    
    ollama = OllamaIntegration()
    
    # Status
    status = ollama.get_status()
    print(f"📡 Connexion: {'✅ OK' if status['connected'] else '❌ NOK'}")
    print(f"🦙 Ollama installé: {'✅ Oui' if status['ollama_installed'] else '❌ Non'}")
    
    if not status['connected']:
        if not status['ollama_installed']:
            print("\n💡 Installation d'Ollama requise:")
            instructions = ollama.install_ollama_instructions()
            print(f"   Système: {instructions['system']}")
            print(f"   Commande: {instructions['instruction']}")
            print(f"   URL: {instructions['url']}")
        else:
            print("\n⚠️  Ollama installé mais non démarré. Lancez: ollama serve")
        return
    
    # Liste des modèles
    models = ollama.list_models()
    print(f"\n📚 Modèles disponibles: {len(models)}")
    
    for model in models:
        status_icon = "⭐" if model.get('is_recommended') else "📦"
        print(f"   {status_icon} {model['name']}")
        if 'description' in model:
            print(f"     {model['description']}")
    
    if not models:
        print("\n💡 Aucun modèle installé. Modèles recommandés:")
        for name, info in ollama.recommended_models.items():
            print(f"   ⭐ {name} ({info.size}) - {info.description}")
        print("\nPour installer un modèle: ollama pull phi3")
        return
    
    # Test de chat si modèle disponible
    if models:
        recommended = ollama.get_recommended_model(['chat'])
        if recommended:
            ollama.set_model(recommended)
            print(f"\n🤖 Test avec {recommended}:")
            
            response = ollama.simple_chat(
                "Bonjour ! Présente-toi en français en 2 phrases.",
                "Tu es O-RedMind, l'IA personnelle respectueuse de la souveraineté numérique."
            )
            print(f"   {response}")
    
    print("\n✅ Intégration Ollama prête pour O-RedMind !")

if __name__ == "__main__":
    main()