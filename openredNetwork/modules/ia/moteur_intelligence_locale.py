#!/usr/bin/env python3
"""
O-RedMind - Moteur d'Intelligence Locale Multimodale
==================================================

Moteur d'IA local avec capacités multimodales (texte, vision, audio)
et apprentissage personnalisé respectant le Manifeste OpenRed.

Auteur: Système OpenRed 2025
Licence: MIT - Souveraineté Numérique Totale
"""

import os
import json
import time
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import sqlite3
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import hashlib
import uuid

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModalityType(Enum):
    """Types de modalités supportées"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CODE = "code"
    DOCUMENT = "document"

class ReasoningType(Enum):
    """Types de raisonnement"""
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    LOGICAL = "logical"
    INTUITIVE = "intuitive"
    STRATEGIC = "strategic"

@dataclass
class MultimodalInput:
    """Entrée multimodale pour l'IA"""
    content: Union[str, bytes, np.ndarray]
    modality: ModalityType
    metadata: Dict[str, Any]
    timestamp: float
    user_id: str
    profile_context: str

@dataclass
class AIResponse:
    """Réponse de l'IA avec métadonnées"""
    content: str
    reasoning_type: ReasoningType
    confidence: float
    modalities_used: List[ModalityType]
    processing_time: float
    personalization_applied: bool
    sources: List[str]

class LocalLanguageModel:
    """Modèle de langage local personnalisé"""
    
    def __init__(self, model_path: Path, user_profile: str):
        self.model_path = model_path
        self.user_profile = user_profile
        self.vocabulary = {}
        self.user_patterns = {}
        self.context_memory = []
        self.max_context_length = 1000
        
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Charge ou crée le modèle local"""
        model_file = self.model_path / f"llm_{self.user_profile}.json"
        
        if model_file.exists():
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.vocabulary = data.get('vocabulary', {})
                    self.user_patterns = data.get('user_patterns', {})
                logger.info(f"📚 Modèle de langage chargé pour {self.user_profile}")
            except Exception as e:
                logger.error(f"Erreur chargement modèle: {e}")
                self._create_base_model()
        else:
            self._create_base_model()
    
    def _create_base_model(self):
        """Crée un modèle de base"""
        self.vocabulary = {
            'tokens': {},
            'ngrams': {},
            'semantic_clusters': {}
        }
        self.user_patterns = {
            'frequent_topics': {},
            'communication_style': {},
            'preferred_responses': {}
        }
        logger.info(f"🆕 Nouveau modèle de langage créé pour {self.user_profile}")
    
    def update_with_interaction(self, user_input: str, ai_response: str, feedback: Optional[str] = None):
        """Met à jour le modèle avec une nouvelle interaction"""
        # Analyse du vocabulaire utilisateur
        self._update_vocabulary(user_input)
        
        # Apprentissage des patterns de communication
        self._learn_communication_patterns(user_input, ai_response, feedback)
        
        # Mise à jour de la mémoire contextuelle
        self._update_context_memory(user_input, ai_response)
        
        # Sauvegarde périodique
        self._save_model()
    
    def _update_vocabulary(self, text: str):
        """Met à jour le vocabulaire personnel"""
        words = text.lower().split()
        
        for word in words:
            if len(word) > 2:  # Ignorer les mots trop courts
                if word in self.vocabulary['tokens']:
                    self.vocabulary['tokens'][word] += 1
                else:
                    self.vocabulary['tokens'][word] = 1
        
        # Création de n-grammes personnalisés
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if bigram in self.vocabulary['ngrams']:
                self.vocabulary['ngrams'][bigram] += 1
            else:
                self.vocabulary['ngrams'][bigram] = 1
    
    def _learn_communication_patterns(self, user_input: str, ai_response: str, feedback: Optional[str]):
        """Apprend les patterns de communication personnels"""
        # Analyse de la longueur préférée des réponses
        response_length = len(ai_response.split())
        
        if feedback:
            if 'trop long' in feedback.lower():
                self._adjust_response_length('shorter')
            elif 'trop court' in feedback.lower():
                self._adjust_response_length('longer')
            elif 'parfait' in feedback.lower() or 'bien' in feedback.lower():
                self._reinforce_response_style(user_input, ai_response)
    
    def _adjust_response_length(self, direction: str):
        """Ajuste la longueur préférée des réponses"""
        if 'preferred_length' not in self.user_patterns['communication_style']:
            self.user_patterns['communication_style']['preferred_length'] = 100
        
        current_length = self.user_patterns['communication_style']['preferred_length']
        
        if direction == 'shorter':
            self.user_patterns['communication_style']['preferred_length'] = max(50, current_length * 0.8)
        elif direction == 'longer':
            self.user_patterns['communication_style']['preferred_length'] = min(300, current_length * 1.2)
    
    def _reinforce_response_style(self, user_input: str, ai_response: str):
        """Renforce un style de réponse apprécié"""
        style_signature = hashlib.md5(f"{user_input[:50]}{ai_response[:50]}".encode()).hexdigest()
        
        if style_signature in self.user_patterns['preferred_responses']:
            self.user_patterns['preferred_responses'][style_signature] += 1
        else:
            self.user_patterns['preferred_responses'][style_signature] = 1
    
    def _update_context_memory(self, user_input: str, ai_response: str):
        """Met à jour la mémoire contextuelle"""
        self.context_memory.append({
            'user': user_input,
            'ai': ai_response,
            'timestamp': time.time()
        })
        
        # Limite la taille de la mémoire contextuelle
        if len(self.context_memory) > self.max_context_length:
            self.context_memory = self.context_memory[-self.max_context_length:]
    
    def generate_response(self, prompt: str, reasoning_type: ReasoningType) -> str:
        """Génère une réponse personnalisée"""
        # Récupération du contexte récent
        recent_context = self._get_recent_context(5)
        
        # Adaptation selon le type de raisonnement
        base_response = self._generate_base_response(prompt, reasoning_type)
        
        # Personnalisation selon les patterns appris
        personalized_response = self._personalize_response(base_response, prompt)
        
        return personalized_response
    
    def _get_recent_context(self, num_interactions: int) -> List[Dict[str, str]]:
        """Récupère le contexte récent"""
        return self.context_memory[-num_interactions:] if self.context_memory else []
    
    def _generate_base_response(self, prompt: str, reasoning_type: ReasoningType) -> str:
        """Génère une réponse de base selon le type de raisonnement"""
        responses = {
            ReasoningType.ANALYTICAL: f"Analysons votre question '{prompt}' de manière méthodique...",
            ReasoningType.CREATIVE: f"Explorons créativement les possibilités autour de '{prompt}'...",
            ReasoningType.LOGICAL: f"Appliquons une logique rigoureuse à '{prompt}'...",
            ReasoningType.INTUITIVE: f"Mon intuition concernant '{prompt}' suggère que...",
            ReasoningType.STRATEGIC: f"Développons une approche stratégique pour '{prompt}'..."
        }
        
        return responses.get(reasoning_type, f"Concernant '{prompt}', voici ma réflexion...")
    
    def _personalize_response(self, response: str, prompt: str) -> str:
        """Personnalise la réponse selon les patterns appris"""
        # Ajustement de la longueur
        preferred_length = self.user_patterns['communication_style'].get('preferred_length', 100)
        words = response.split()
        
        if len(words) > preferred_length * 1.2:
            # Raccourcir la réponse
            response = ' '.join(words[:int(preferred_length)]) + "..."
        elif len(words) < preferred_length * 0.8:
            # Enrichir la réponse
            response += " Je peux développer davantage si vous le souhaitez."
        
        # Intégration du vocabulaire personnel
        personal_terms = self._get_relevant_personal_terms(prompt)
        if personal_terms:
            response += f" (En référence à vos termes habituels: {', '.join(personal_terms[:3])})"
        
        return response
    
    def _get_relevant_personal_terms(self, prompt: str) -> List[str]:
        """Récupère les termes personnels pertinents"""
        prompt_words = set(prompt.lower().split())
        relevant_terms = []
        
        for term, frequency in self.vocabulary['tokens'].items():
            if frequency > 3 and term in prompt_words:  # Termes fréquents et pertinents
                relevant_terms.append(term)
        
        return sorted(relevant_terms, key=lambda x: self.vocabulary['tokens'][x], reverse=True)
    
    def _save_model(self):
        """Sauvegarde le modèle"""
        model_file = self.model_path / f"llm_{self.user_profile}.json"
        
        try:
            with open(model_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'vocabulary': self.vocabulary,
                    'user_patterns': self.user_patterns,
                    'last_updated': time.time()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde modèle: {e}")

class MultimodalProcessor:
    """Processeur multimodal pour différents types de contenu"""
    
    def __init__(self, models_path: Path):
        self.models_path = models_path
        self.processors = {}
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Initialise les processeurs pour chaque modalité"""
        self.processors = {
            ModalityType.TEXT: self._process_text,
            ModalityType.IMAGE: self._process_image,
            ModalityType.AUDIO: self._process_audio,
            ModalityType.CODE: self._process_code,
            ModalityType.DOCUMENT: self._process_document
        }
        logger.info("🔄 Processeurs multimodaux initialisés")
    
    def process_input(self, input_data: MultimodalInput) -> Dict[str, Any]:
        """Traite une entrée multimodale"""
        processor = self.processors.get(input_data.modality)
        
        if not processor:
            raise ValueError(f"Modalité non supportée: {input_data.modality}")
        
        start_time = time.time()
        result = processor(input_data)
        processing_time = time.time() - start_time
        
        result['processing_time'] = processing_time
        result['modality'] = input_data.modality.value
        
        logger.info(f"✅ Traitement {input_data.modality.value} terminé en {processing_time:.2f}s")
        return result
    
    def _process_text(self, input_data: MultimodalInput) -> Dict[str, Any]:
        """Traite le texte"""
        text = input_data.content
        
        analysis = {
            'content_type': 'text',
            'length': len(text),
            'word_count': len(text.split()),
            'language': self._detect_language(text),
            'sentiment': self._analyze_sentiment(text),
            'topics': self._extract_topics(text),
            'complexity': self._assess_complexity(text)
        }
        
        return analysis
    
    def _process_image(self, input_data: MultimodalInput) -> Dict[str, Any]:
        """Traite les images"""
        try:
            if isinstance(input_data.content, str):
                # Décodage base64 si nécessaire
                image_data = base64.b64decode(input_data.content)
                image = Image.open(BytesIO(image_data))
            elif isinstance(input_data.content, bytes):
                image = Image.open(BytesIO(input_data.content))
            else:
                image = input_data.content
            
            analysis = {
                'content_type': 'image',
                'dimensions': image.size,
                'format': image.format,
                'mode': image.mode,
                'description': self._describe_image(image),
                'objects_detected': self._detect_objects(image),
                'text_in_image': self._extract_text_from_image(image)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur traitement image: {e}")
            return {'content_type': 'image', 'error': str(e)}
    
    def _process_audio(self, input_data: MultimodalInput) -> Dict[str, Any]:
        """Traite l'audio (simulation)"""
        # Simulation du traitement audio
        return {
            'content_type': 'audio',
            'duration': input_data.metadata.get('duration', 0),
            'format': input_data.metadata.get('format', 'unknown'),
            'transcription': self._transcribe_audio(input_data.content),
            'emotion_detected': 'neutral',
            'speech_rate': 'normal'
        }
    
    def _process_code(self, input_data: MultimodalInput) -> Dict[str, Any]:
        """Traite le code"""
        code = input_data.content
        
        analysis = {
            'content_type': 'code',
            'language': self._detect_programming_language(code),
            'lines_count': len(code.split('\n')),
            'complexity': self._assess_code_complexity(code),
            'functions_detected': self._extract_functions(code),
            'imports_detected': self._extract_imports(code),
            'suggestions': self._suggest_code_improvements(code)
        }
        
        return analysis
    
    def _process_document(self, input_data: MultimodalInput) -> Dict[str, Any]:
        """Traite les documents"""
        return {
            'content_type': 'document',
            'format': input_data.metadata.get('format', 'unknown'),
            'page_count': input_data.metadata.get('pages', 1),
            'text_extracted': self._extract_document_text(input_data.content),
            'structure': self._analyze_document_structure(input_data.content)
        }
    
    # Méthodes utilitaires de traitement
    
    def _detect_language(self, text: str) -> str:
        """Détecte la langue du texte (simplifié)"""
        french_words = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'à', 'un', 'une']
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of']
        
        text_lower = text.lower()
        french_count = sum(1 for word in french_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        return 'french' if french_count > english_count else 'english'
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyse le sentiment (simplifié)"""
        positive_words = ['bon', 'bien', 'super', 'génial', 'parfait', 'excellent', 'good', 'great', 'awesome']
        negative_words = ['mauvais', 'mal', 'nul', 'terrible', 'horrible', 'bad', 'awful', 'terrible']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extrait les sujets principaux"""
        # Simplification : mots les plus fréquents
        words = text.lower().split()
        word_freq = {}
        
        for word in words:
            if len(word) > 4:  # Mots significatifs
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Retourne les 5 mots les plus fréquents
        return sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:5]
    
    def _assess_complexity(self, text: str) -> str:
        """Évalue la complexité du texte"""
        words = text.split()
        if not words:
            return 'low'
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        avg_sentence_length = len(words) / max(sentence_count, 1)
        
        complexity_score = (avg_word_length * 0.3) + (avg_sentence_length * 0.7)
        
        if complexity_score < 10:
            return 'low'
        elif complexity_score < 20:
            return 'medium'
        else:
            return 'high'
    
    def _describe_image(self, image: Image.Image) -> str:
        """Décrit une image (simulation)"""
        width, height = image.size
        aspect_ratio = width / height
        
        if aspect_ratio > 1.5:
            orientation = "paysage"
        elif aspect_ratio < 0.7:
            orientation = "portrait"
        else:
            orientation = "carré"
        
        return f"Image en {orientation} de {width}x{height} pixels"
    
    def _detect_objects(self, image: Image.Image) -> List[str]:
        """Détecte les objets dans l'image (simulation)"""
        # Simulation basée sur les couleurs dominantes
        colors = image.getcolors(maxcolors=256)
        if colors:
            dominant_color = max(colors, key=lambda x: x[0])[1]
            if isinstance(dominant_color, tuple) and len(dominant_color) >= 3:
                r, g, b = dominant_color[:3]
                if r > 200 and g < 100 and b < 100:
                    return ['objet_rouge']
                elif g > 200 and r < 100 and b < 100:
                    return ['végétation']
                elif b > 200 and r < 100 and g < 100:
                    return ['ciel', 'eau']
        
        return ['objets_non_identifiés']
    
    def _extract_text_from_image(self, image: Image.Image) -> str:
        """Extrait le texte d'une image (simulation)"""
        # Simulation OCR
        return "Texte extrait simulé de l'image"
    
    def _transcribe_audio(self, audio_data: bytes) -> str:
        """Transcrit l'audio (simulation)"""
        return "Transcription audio simulée"
    
    def _detect_programming_language(self, code: str) -> str:
        """Détecte le langage de programmation"""
        if 'def ' in code and 'import ' in code:
            return 'python'
        elif 'function ' in code and 'var ' in code:
            return 'javascript'
        elif '#include' in code and 'int main' in code:
            return 'c++'
        elif 'public class' in code and 'System.out' in code:
            return 'java'
        else:
            return 'unknown'
    
    def _assess_code_complexity(self, code: str) -> str:
        """Évalue la complexité du code"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if len(non_empty_lines) < 10:
            return 'low'
        elif len(non_empty_lines) < 50:
            return 'medium'
        else:
            return 'high'
    
    def _extract_functions(self, code: str) -> List[str]:
        """Extrait les fonctions du code"""
        functions = []
        lines = code.split('\n')
        
        for line in lines:
            if 'def ' in line:
                # Extraction simple du nom de fonction Python
                parts = line.split('def ')
                if len(parts) > 1:
                    func_name = parts[1].split('(')[0].strip()
                    functions.append(func_name)
        
        return functions
    
    def _extract_imports(self, code: str) -> List[str]:
        """Extrait les imports du code"""
        imports = []
        lines = code.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        
        return imports
    
    def _suggest_code_improvements(self, code: str) -> List[str]:
        """Suggère des améliorations de code"""
        suggestions = []
        
        if 'print(' in code:
            suggestions.append("Utiliser logging au lieu de print pour le debugging")
        
        if len(code.split('\n')) > 50 and 'def ' not in code:
            suggestions.append("Considérer diviser le code en fonctions plus petites")
        
        if 'TODO' in code or 'FIXME' in code:
            suggestions.append("Compléter les TODOs et FIXMEs identifiés")
        
        return suggestions
    
    def _extract_document_text(self, document_content: Any) -> str:
        """Extrait le texte d'un document"""
        # Simulation
        return "Texte extrait du document"
    
    def _analyze_document_structure(self, document_content: Any) -> Dict[str, Any]:
        """Analyse la structure d'un document"""
        return {
            'headings': ['Introduction', 'Développement', 'Conclusion'],
            'paragraphs': 5,
            'images': 2,
            'tables': 1
        }

class ReasoningEngine:
    """Moteur de raisonnement adaptatif"""
    
    def __init__(self, user_profile: str):
        self.user_profile = user_profile
        self.reasoning_history = []
        self.success_patterns = {}
    
    def reason(self, query: str, context: Dict[str, Any], reasoning_type: ReasoningType) -> Dict[str, Any]:
        """Execute un raisonnement selon le type demandé"""
        reasoning_methods = {
            ReasoningType.ANALYTICAL: self._analytical_reasoning,
            ReasoningType.CREATIVE: self._creative_reasoning,
            ReasoningType.LOGICAL: self._logical_reasoning,
            ReasoningType.INTUITIVE: self._intuitive_reasoning,
            ReasoningType.STRATEGIC: self._strategic_reasoning
        }
        
        method = reasoning_methods.get(reasoning_type, self._analytical_reasoning)
        result = method(query, context)
        
        # Enregistrement du raisonnement
        self._record_reasoning(query, reasoning_type, result)
        
        return result
    
    def _analytical_reasoning(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Raisonnement analytique méthodique"""
        steps = [
            "Identification des éléments clés",
            "Analyse des relations entre éléments",
            "Évaluation des implications",
            "Synthèse des conclusions"
        ]
        
        return {
            'type': 'analytical',
            'steps': steps,
            'conclusion': f"Analyse méthodique de '{query}' complétée",
            'confidence': 0.8
        }
    
    def _creative_reasoning(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Raisonnement créatif divergent"""
        creative_approaches = [
            "Brainstorming d'idées alternatives",
            "Association libre de concepts",
            "Exploration de métaphores",
            "Génération de solutions innovantes"
        ]
        
        return {
            'type': 'creative',
            'approaches': creative_approaches,
            'conclusion': f"Exploration créative de '{query}' avec nouvelles perspectives",
            'confidence': 0.7
        }
    
    def _logical_reasoning(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Raisonnement logique formel"""
        logical_steps = [
            "Établissement des prémisses",
            "Application des règles logiques",
            "Déduction des conséquences",
            "Vérification de la cohérence"
        ]
        
        return {
            'type': 'logical',
            'steps': logical_steps,
            'conclusion': f"Raisonnement logique appliqué à '{query}'",
            'confidence': 0.9
        }
    
    def _intuitive_reasoning(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Raisonnement intuitif basé sur l'expérience"""
        intuitive_insights = [
            "Reconnaissance de patterns familiers",
            "Activation de l'expérience passée",
            "Synthèse intuitive",
            "Validation par le ressenti"
        ]
        
        return {
            'type': 'intuitive',
            'insights': intuitive_insights,
            'conclusion': f"Approche intuitive pour '{query}' basée sur l'expérience",
            'confidence': 0.6
        }
    
    def _strategic_reasoning(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Raisonnement stratégique orienté objectifs"""
        strategic_phases = [
            "Définition des objectifs",
            "Analyse de l'environnement",
            "Identification des options",
            "Planification de l'action"
        ]
        
        return {
            'type': 'strategic',
            'phases': strategic_phases,
            'conclusion': f"Stratégie développée pour '{query}'",
            'confidence': 0.8
        }
    
    def _record_reasoning(self, query: str, reasoning_type: ReasoningType, result: Dict[str, Any]):
        """Enregistre le raisonnement pour apprentissage"""
        record = {
            'query': query,
            'type': reasoning_type.value,
            'result': result,
            'timestamp': time.time()
        }
        
        self.reasoning_history.append(record)
        
        # Limite l'historique
        if len(self.reasoning_history) > 1000:
            self.reasoning_history = self.reasoning_history[-1000:]

def main():
    """Démonstration du moteur d'intelligence locale"""
    print("🧠 O-RedMind - Moteur d'Intelligence Locale")
    print("=" * 50)
    
    # Initialisation
    models_path = Path.home() / ".openred_demo" / "models"
    models_path.mkdir(exist_ok=True, parents=True)
    
    user_profile = "demo_user"
    
    # Test du modèle de langage local
    print("\n📚 Test du modèle de langage local:")
    llm = LocalLanguageModel(models_path, user_profile)
    
    # Simulation d'interactions
    interactions = [
        ("Bonjour, comment allez-vous ?", "Bonjour ! Je vais bien merci."),
        ("Pouvez-vous m'expliquer l'IA ?", "L'IA est une technologie fascinante..."),
        ("C'est trop long", None)  # Feedback
    ]
    
    for user_input, ai_response in interactions:
        if ai_response:
            llm.update_with_interaction(user_input, ai_response)
        else:
            llm.update_with_interaction(interactions[1][0], interactions[1][1], user_input)
    
    # Test de génération de réponse
    response = llm.generate_response("Parlez-moi de technologie", ReasoningType.ANALYTICAL)
    print(f"  Réponse générée: {response}")
    
    # Test du processeur multimodal
    print("\n🔄 Test du processeur multimodal:")
    processor = MultimodalProcessor(models_path)
    
    # Test texte
    text_input = MultimodalInput(
        content="Bonjour, ceci est un test de traitement de texte en français.",
        modality=ModalityType.TEXT,
        metadata={},
        timestamp=time.time(),
        user_id=user_profile,
        profile_context="demo"
    )
    
    text_result = processor.process_input(text_input)
    print(f"  Analyse texte: {text_result}")
    
    # Test code
    code_input = MultimodalInput(
        content="""def hello_world():
    print("Hello, World!")
    return "Success"

import os
hello_world()""",
        modality=ModalityType.CODE,
        metadata={},
        timestamp=time.time(),
        user_id=user_profile,
        profile_context="demo"
    )
    
    code_result = processor.process_input(code_input)
    print(f"  Analyse code: {code_result}")
    
    # Test du moteur de raisonnement
    print("\n🤔 Test du moteur de raisonnement:")
    reasoning_engine = ReasoningEngine(user_profile)
    
    for reasoning_type in ReasoningType:
        result = reasoning_engine.reason(
            "Comment améliorer la productivité au travail ?",
            {'context': 'workplace'},
            reasoning_type
        )
        print(f"  {reasoning_type.value}: {result['conclusion']}")
    
    print("\n✅ Tests du moteur d'intelligence locale terminés !")
    print("🔒 Toutes les données restent locales et personnalisées.")

if __name__ == "__main__":
    main()