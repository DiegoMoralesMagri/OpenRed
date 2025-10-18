#!/usr/bin/env python3
"""
O-RedMind - Intelligence Artificielle Personnelle Révolutionnaire
================================================================

Architecture bicouche révolutionnaire conforme au Manifeste OpenRed :
- Niveau 1 : Apprentissage privé exclusivement local
- Niveau 2 : Enrichissement public avec consentement granulaire

Auteur: Système OpenRed 2025
Licence: MIT - Souveraineté Numérique Totale
"""

import json
import time
import logging
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import uuid
import secrets

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LearningLevel(Enum):
    """Niveaux d'apprentissage selon l'architecture bicouche"""
    PRIVATE = "private"      # Niveau 1 : Données privées locales uniquement
    PUBLIC_CONSENTED = "public_consented"  # Niveau 2 : Données publiques consenties

class ProfileContext(Enum):
    """Contextes de profils pour adaptation de l'IA"""
    FAMILLE = "famille"
    AMIS = "amis" 
    PROFESSIONNEL = "professionnel"
    PUBLIC = "public"

@dataclass
class ConversationStyle:
    """Style de conversation pour l'adaptation personnalisée"""
    formality: float = 0.7          # Niveau de formalité (0.0 = très familier, 1.0 = très formel)
    creativity: float = 0.6         # Niveau de créativité (0.0 = factuel, 1.0 = très créatif)
    detail_level: float = 0.8       # Niveau de détail (0.0 = concis, 1.0 = très détaillé)
    empathy: float = 0.7            # Niveau d'empathie (0.0 = neutre, 1.0 = très empathique)
    profile_adaptation: str = "professionnel"  # Profil d'adaptation

@dataclass
class CreativeTask:
    """Tâche créative pour O-RedMind"""
    task_type: str              # Type de tâche (writing, brainstorming, etc.)
    prompt: str                 # Prompt créatif
    context: Dict[str, Any]     # Contexte additionnel
    constraints: List[str]      # Contraintes créatives
    style_preferences: ConversationStyle  # Préférences de style

class LearningMode(Enum):
    """Modes d'apprentissage disponibles"""
    PRIVATE_ONLY = "private_only"           # Apprentissage privé uniquement
    CONSENTED_SHARING = "consented_sharing" # Partage avec consentement
    COLLECTIVE_INSIGHTS = "collective_insights"  # Insights collectifs

@dataclass
class ConsentRecord:
    """Enregistrement de consentement granulaire"""
    source_id: str
    source_name: str
    data_type: str
    consent_granted: bool
    timestamp: float
    revocable: bool = True
    expiry_date: Optional[float] = None

@dataclass
class LearningData:
    """Données d'apprentissage avec métadonnées de confidentialité"""
    content: str
    data_type: str  # text, image, audio, behavior
    learning_level: LearningLevel
    profile_context: ProfileContext
    timestamp: float
    source: str
    encrypted: bool = True

@dataclass
class PersonalInsight:
    """Insight personnel généré par l'IA"""
    insight_id: str
    profile_context: ProfileContext
    category: str  # preference, habit, goal, skill
    content: str
    confidence: float
    timestamp: float
    learning_sources: List[str]

class EncryptedMemoryGraph:
    """Graphe de mémoire personnelle chiffrée"""
    
    def __init__(self, fort_path: Path, user_key: bytes):
        self.fort_path = fort_path
        self.memory_db = fort_path / ".oredmind" / "personal_memory.db"
        self.memory_db.parent.mkdir(exist_ok=True, parents=True)
        
        # Génération de la clé de chiffrement à partir de la clé du fort
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'oredmind_memory_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(user_key))
        self.cipher = Fernet(key)
        
        self._init_database()
    
    def _init_database(self):
        """Initialise la base de données de mémoire"""
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    profile_context TEXT NOT NULL,
                    category TEXT NOT NULL,
                    encrypted_content BLOB NOT NULL,
                    timestamp REAL NOT NULL,
                    confidence REAL NOT NULL,
                    source_hash TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_connections (
                    from_memory TEXT,
                    to_memory TEXT,
                    connection_type TEXT,
                    strength REAL,
                    FOREIGN KEY(from_memory) REFERENCES memories(id),
                    FOREIGN KEY(to_memory) REFERENCES memories(id)
                )
            """)
    
    def store_encrypted_memory(self, insight: PersonalInsight):
        """Stocke un insight chiffré en mémoire"""
        encrypted_content = self.cipher.encrypt(insight.content.encode())
        
        with sqlite3.connect(self.memory_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memories 
                (id, profile_context, category, encrypted_content, timestamp, confidence, source_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                insight.insight_id,
                insight.profile_context.value,
                insight.category,
                encrypted_content,
                insight.timestamp,
                insight.confidence,
                hashlib.sha256(str(insight.learning_sources).encode()).hexdigest()
            ))
    
    def retrieve_memories(self, profile_context: ProfileContext, category: Optional[str] = None) -> List[PersonalInsight]:
        """Récupère et déchiffre les mémoires pour un contexte"""
        query = "SELECT * FROM memories WHERE profile_context = ?"
        params = [profile_context.value]
        
        if category:
            query += " AND category = ?"
            params.append(category)
            
        query += " ORDER BY timestamp DESC LIMIT 100"
        
        memories = []
        with sqlite3.connect(self.memory_db) as conn:
            for row in conn.execute(query, params):
                try:
                    decrypted_content = self.cipher.decrypt(row[3]).decode()
                    memories.append(PersonalInsight(
                        insight_id=row[0],
                        profile_context=ProfileContext(row[1]),
                        category=row[2],
                        content=decrypted_content,
                        confidence=row[5],
                        timestamp=row[4],
                        learning_sources=[]  # Simplification pour l'exemple
                    ))
                except Exception as e:
                    logger.error(f"Erreur déchiffrement mémoire {row[0]}: {e}")
        
        return memories

class ConsentManager:
    """Gestionnaire de consentement granulaire pour l'apprentissage public"""
    
    def __init__(self, fort_path: Path):
        self.consent_file = fort_path / ".oredmind" / "consent_records.json"
        self.consent_file.parent.mkdir(exist_ok=True, parents=True)
        self.consents: Dict[str, ConsentRecord] = {}
        self.load_consents()
    
    def load_consents(self):
        """Charge les enregistrements de consentement"""
        if self.consent_file.exists():
            try:
                with open(self.consent_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for source_id, consent_data in data.items():
                        self.consents[source_id] = ConsentRecord(**consent_data)
            except Exception as e:
                logger.error(f"Erreur chargement consentements: {e}")
    
    def save_consents(self):
        """Sauvegarde les consentements"""
        try:
            data = {source_id: asdict(consent) for source_id, consent in self.consents.items()}
            with open(self.consent_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde consentements: {e}")
    
    def grant_consent(self, source_id: str, source_name: str, data_type: str, 
                     expiry_days: Optional[int] = None) -> bool:
        """Accorde un consentement granulaire"""
        expiry_date = None
        if expiry_days:
            expiry_date = time.time() + (expiry_days * 24 * 3600)
        
        consent = ConsentRecord(
            source_id=source_id,
            source_name=source_name,
            data_type=data_type,
            consent_granted=True,
            timestamp=time.time(),
            expiry_date=expiry_date
        )
        
        self.consents[source_id] = consent
        self.save_consents()
        
        logger.info(f"✅ Consentement accordé pour {source_name} ({data_type})")
        return True
    
    def revoke_consent(self, source_id: str) -> bool:
        """Révoque un consentement"""
        if source_id in self.consents:
            self.consents[source_id].consent_granted = False
            self.save_consents()
            logger.info(f"❌ Consentement révoqué pour {source_id}")
            return True
        return False
    
    def is_consent_valid(self, source_id: str) -> bool:
        """Vérifie si un consentement est valide"""
        if source_id not in self.consents:
            return False
        
        consent = self.consents[source_id]
        
        # Vérification de l'expiration
        if consent.expiry_date and time.time() > consent.expiry_date:
            consent.consent_granted = False
            self.save_consents()
            return False
        
        return consent.consent_granted
    
    def list_active_consents(self) -> List[ConsentRecord]:
        """Liste tous les consentements actifs"""
        return [consent for consent in self.consents.values() if consent.consent_granted]

class LocalPersonalModel:
    """Modèle d'IA personnel local (Niveau 1)"""
    
    def __init__(self, profile_context: ProfileContext):
        self.profile_context = profile_context
        self.personal_patterns = {}
        self.behavior_model = {}
        self.preferences = {}
        self.conversation_style = {}
    
    def learn_from_interaction(self, user_input: str, context: Dict[str, Any]):
        """Apprend d'une interaction utilisateur"""
        # Analyse des patterns personnels
        patterns = self._extract_patterns(user_input, context)
        self._update_personal_patterns(patterns)
        
        # Adaptation du style de conversation
        style_markers = self._analyze_communication_style(user_input)
        self._update_conversation_style(style_markers)
        
        logger.info(f"📚 Apprentissage personnel mis à jour pour profil {self.profile_context.value}")
    
    def _extract_patterns(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les patterns personnels du texte"""
        patterns = {
            'topics_of_interest': self._extract_topics(text),
            'preferred_time': context.get('timestamp', time.time()),
            'complexity_level': self._analyze_complexity(text),
            'emotional_tone': self._analyze_emotion(text)
        }
        return patterns
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extraction simple des sujets (à améliorer avec NLP)"""
        # Simplification pour l'exemple
        words = text.lower().split()
        topics = [word for word in words if len(word) > 4]
        return topics[:5]  # Top 5 mots significatifs
    
    def _analyze_complexity(self, text: str) -> float:
        """Analyse le niveau de complexité préféré"""
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        return min(avg_word_length / 10, 1.0)  # Normalisé entre 0 et 1
    
    def _analyze_emotion(self, text: str) -> str:
        """Analyse de l'émotion (simplifiée)"""
        positive_words = ['bon', 'bien', 'super', 'génial', 'parfait', 'excellent']
        negative_words = ['mauvais', 'mal', 'nul', 'terrible', 'horrible']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _update_personal_patterns(self, patterns: Dict[str, Any]):
        """Met à jour les patterns personnels"""
        for key, value in patterns.items():
            if key not in self.personal_patterns:
                self.personal_patterns[key] = []
            self.personal_patterns[key].append(value)
            
            # Garde seulement les 100 dernières entrées
            if len(self.personal_patterns[key]) > 100:
                self.personal_patterns[key] = self.personal_patterns[key][-100:]
    
    def _analyze_communication_style(self, text: str) -> Dict[str, float]:
        """Analyse le style de communication"""
        return {
            'formality': self._measure_formality(text),
            'enthusiasm': self._measure_enthusiasm(text),
            'directness': self._measure_directness(text)
        }
    
    def _measure_formality(self, text: str) -> float:
        """Mesure le niveau de formalité"""
        formal_markers = ['vous', 'veuillez', 'pourriez', 'souhaiteriez']
        informal_markers = ['tu', 'salut', 'ok', 'super', 'cool']
        
        text_lower = text.lower()
        formal_count = sum(1 for marker in formal_markers if marker in text_lower)
        informal_count = sum(1 for marker in informal_markers if marker in text_lower)
        
        if formal_count + informal_count == 0:
            return 0.5  # Neutre
        
        return formal_count / (formal_count + informal_count)
    
    def _measure_enthusiasm(self, text: str) -> float:
        """Mesure le niveau d'enthousiasme"""
        enthusiasm_markers = text.count('!') + text.count('super') + text.count('génial')
        return min(enthusiasm_markers / 10.0, 1.0)
    
    def _measure_directness(self, text: str) -> float:
        """Mesure le niveau de directness"""
        # Simplification : phrases plus courtes = plus direct
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.strip()) for s in sentences) / len(sentences) if sentences else 0
        return max(0, 1 - (avg_sentence_length / 100))
    
    def _update_conversation_style(self, style_markers: Dict[str, float]):
        """Met à jour le style de conversation"""
        for style_type, value in style_markers.items():
            if style_type not in self.conversation_style:
                self.conversation_style[style_type] = []
            
            self.conversation_style[style_type].append(value)
            
            # Moyenne mobile des 20 dernières interactions
            if len(self.conversation_style[style_type]) > 20:
                self.conversation_style[style_type] = self.conversation_style[style_type][-20:]
    
    def generate_personalized_response(self, query: str, context: Dict[str, Any]) -> str:
        """Génère une réponse personnalisée basée sur l'apprentissage"""
        # Récupération du style de conversation moyen
        avg_styles = {}
        for style_type, values in self.conversation_style.items():
            if values:
                avg_styles[style_type] = sum(values) / len(values)
            else:
                avg_styles[style_type] = 0.5
        
        # Génération de réponse adaptée (simplifiée pour l'exemple)
        base_response = self._generate_base_response(query, context)
        personalized_response = self._adapt_response_style(base_response, avg_styles)
        
        return personalized_response
    
    def _generate_base_response(self, query: str, context: Dict[str, Any]) -> str:
        """Génère une réponse de base"""
        # Simplification pour l'exemple
        if 'aide' in query.lower():
            return "Je suis là pour vous aider avec vos besoins spécifiques."
        elif 'comment' in query.lower():
            return "Laissez-moi vous expliquer en détail."
        else:
            return "Je comprends votre demande et voici ma réponse personnalisée."
    
    def _adapt_response_style(self, response: str, styles: Dict[str, float]) -> str:
        """Adapte le style de la réponse"""
        # Adaptation de la formalité
        if styles.get('formality', 0.5) < 0.3:
            response = response.replace('vous', 'tu').replace('votre', 'ton')
        
        # Adaptation de l'enthousiasme
        if styles.get('enthusiasm', 0.5) > 0.7:
            response += " !"
        
        # Adaptation de la directness
        if styles.get('directness', 0.5) > 0.7:
            response = response.split('.')[0] + '.'  # Raccourcit la réponse
        
        return response

class CollectiveInsightsEngine:
    """Moteur d'insights collectifs (Niveau 2) avec consentement"""
    
    def __init__(self, consent_manager: ConsentManager):
        self.consent_manager = consent_manager
        self.public_knowledge_base = {}
        
    def extract_collective_insights(self, source_id: str, public_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait des insights de données publiques consenties"""
        if not self.consent_manager.is_consent_valid(source_id):
            logger.warning(f"⚠️ Consentement non valide pour source {source_id}")
            return []
        
        insights = []
        
        # Extraction d'insights généraux (non personnels)
        if 'knowledge' in public_data:
            knowledge_insights = self._extract_knowledge_insights(public_data['knowledge'])
            insights.extend(knowledge_insights)
        
        if 'trends' in public_data:
            trend_insights = self._extract_trend_insights(public_data['trends'])
            insights.extend(trend_insights)
        
        logger.info(f"📊 {len(insights)} insights collectifs extraits de {source_id}")
        return insights
    
    def _extract_knowledge_insights(self, knowledge_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait des insights de connaissance générale"""
        insights = []
        
        # Exemple d'extraction de connaissances factuelles
        for topic, info in knowledge_data.items():
            insights.append({
                'type': 'factual_knowledge',
                'topic': topic,
                'content': info,
                'confidence': 0.8,
                'source_type': 'collective'
            })
        
        return insights
    
    def _extract_trend_insights(self, trend_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait des insights de tendances"""
        insights = []
        
        for trend_name, trend_info in trend_data.items():
            insights.append({
                'type': 'trend_insight',
                'trend': trend_name,
                'data': trend_info,
                'confidence': 0.6,
                'source_type': 'collective'
            })
        
        return insights

class ORedMindCore:
    """Cœur de l'IA O-RedMind - Architecture bicouche révolutionnaire"""
    
    def __init__(self, fort_path: Path, user_id: str, user_key: bytes):
        self.fort_path = fort_path
        self.user_id = user_id
        self.user_key = user_key
        
        # Initialisation des composants principaux
        self.memory_graph = EncryptedMemoryGraph(fort_path, user_key)
        self.consent_manager = ConsentManager(fort_path)
        self.collective_insights = CollectiveInsightsEngine(self.consent_manager)
        
        # Modèles personnels par profil
        self.personal_models = {
            profile: LocalPersonalModel(profile) for profile in ProfileContext
        }
        
        # État actuel
        self.current_profile = ProfileContext.PUBLIC
        self.learning_active = True
        
        logger.info(f"🤖 O-RedMind initialisé pour utilisateur {user_id}")
    
    def switch_profile(self, profile: ProfileContext):
        """Bascule vers un profil spécifique"""
        self.current_profile = profile
        logger.info(f"👤 Basculé vers profil {profile.value}")
    
    def process_user_interaction(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Traite une interaction utilisateur avec apprentissage bicouche"""
        if context is None:
            context = {'timestamp': time.time(), 'profile': self.current_profile.value}
        
        # Niveau 1 : Apprentissage privé obligatoire
        self._learn_private_level(user_input, context)
        
        # Niveau 2 : Enrichissement public si consenti
        self._enhance_with_public_data(user_input, context)
        
        # Génération de réponse personnalisée
        response = self.personal_models[self.current_profile].generate_personalized_response(
            user_input, context
        )
        
        # Stockage de l'interaction en mémoire chiffrée
        self._store_interaction_memory(user_input, response, context)
        
        return response
    
    def _learn_private_level(self, user_input: str, context: Dict[str, Any]):
        """Apprentissage de Niveau 1 : Données privées uniquement"""
        current_model = self.personal_models[self.current_profile]
        current_model.learn_from_interaction(user_input, context)
        
        # Génération d'insights personnels
        insight = self._generate_personal_insight(user_input, context)
        if insight:
            self.memory_graph.store_encrypted_memory(insight)
    
    def _enhance_with_public_data(self, user_input: str, context: Dict[str, Any]):
        """Enrichissement de Niveau 2 : Données publiques consenties"""
        active_consents = self.consent_manager.list_active_consents()
        
        for consent in active_consents:
            # Simulation de données publiques (à remplacer par de vraies sources)
            mock_public_data = self._get_mock_public_data(consent.source_id)
            
            if mock_public_data:
                collective_insights = self.collective_insights.extract_collective_insights(
                    consent.source_id, mock_public_data
                )
                
                # Intégration des insights collectifs au modèle personnel
                self._integrate_collective_insights(collective_insights)
    
    def _generate_personal_insight(self, user_input: str, context: Dict[str, Any]) -> Optional[PersonalInsight]:
        """Génère un insight personnel à partir de l'interaction"""
        # Détection d'une préférence exprimée
        if any(word in user_input.lower() for word in ['aime', 'préfère', 'déteste', 'adore']):
            insight = PersonalInsight(
                insight_id=str(uuid.uuid4()),
                profile_context=self.current_profile,
                category='preference',
                content=f"Expression de préférence détectée: {user_input[:100]}",
                confidence=0.7,
                timestamp=time.time(),
                learning_sources=['private_interaction']
            )
            return insight
        
        return None
    
    def _store_interaction_memory(self, user_input: str, response: str, context: Dict[str, Any]):
        """Stocke l'interaction en mémoire pour référence future"""
        interaction_insight = PersonalInsight(
            insight_id=str(uuid.uuid4()),
            profile_context=self.current_profile,
            category='interaction',
            content=f"Q: {user_input[:200]} | R: {response[:200]}",
            confidence=1.0,
            timestamp=time.time(),
            learning_sources=['direct_interaction']
        )
        
        self.memory_graph.store_encrypted_memory(interaction_insight)
    
    def _get_mock_public_data(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Données publiques simulées (à remplacer par de vraies sources)"""
        mock_sources = {
            'wikipedia_fr': {
                'knowledge': {
                    'intelligence_artificielle': 'IA est un domaine scientifique...',
                    'cryptographie': 'Science du chiffrement des données...'
                }
            },
            'trends_tech': {
                'trends': {
                    'blockchain': {'popularity': 0.8, 'growth': 0.15},
                    'quantum_computing': {'popularity': 0.6, 'growth': 0.25}
                }
            }
        }
        
        return mock_sources.get(source_id)
    
    def _integrate_collective_insights(self, insights: List[Dict[str, Any]]):
        """Intègre les insights collectifs au modèle personnel"""
        for insight in insights:
            # Pondération des insights collectifs (moins de poids que les données privées)
            weighted_insight = PersonalInsight(
                insight_id=str(uuid.uuid4()),
                profile_context=self.current_profile,
                category='collective_knowledge',
                content=f"Insight collectif: {insight['content']}",
                confidence=insight['confidence'] * 0.5,  # Pondération réduite
                timestamp=time.time(),
                learning_sources=['collective_consented']
            )
            
            self.memory_graph.store_encrypted_memory(weighted_insight)
    
    def get_personal_insights(self, category: Optional[str] = None) -> List[PersonalInsight]:
        """Récupère les insights personnels pour le profil actuel"""
        return self.memory_graph.retrieve_memories(self.current_profile, category)
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Retourne le statut d'apprentissage actuel"""
        return {
            'current_profile': self.current_profile.value,
            'learning_active': self.learning_active,
            'active_consents': len(self.consent_manager.list_active_consents()),
            'memory_count': len(self.get_personal_insights()),
            'privacy_level': 'bicouche_conforme_manifeste'
        }
    
    def generate_creative_content(self, prompt: str, content_type: str = 'text') -> str:
        """Génère du contenu créatif personnalisé"""
        # Récupération des insights pertinents
        relevant_memories = self.get_personal_insights('preference')
        
        # Adaptation du prompt selon les préférences personnelles
        personalized_prompt = self._personalize_creative_prompt(prompt, relevant_memories)
        
        # Génération créative (simulation pour l'exemple)
        if content_type == 'text':
            return self._generate_creative_text(personalized_prompt)
        elif content_type == 'code':
            return self._generate_creative_code(personalized_prompt)
        else:
            return f"Contenu créatif {content_type} généré pour: {personalized_prompt}"
    
    def _personalize_creative_prompt(self, prompt: str, memories: List[PersonalInsight]) -> str:
        """Personnalise un prompt créatif selon les préférences"""
        # Extraction des préférences des mémoires
        preferences = []
        for memory in memories[-5:]:  # 5 dernières préférences
            if 'préfère' in memory.content or 'aime' in memory.content:
                preferences.append(memory.content)
        
        if preferences:
            context = " | ".join(preferences[:3])
            return f"{prompt} (Contexte personnel: {context})"
        
        return prompt
    
    def _generate_creative_text(self, prompt: str) -> str:
        """Génération de texte créatif personnalisé"""
        # Simplification pour l'exemple
        style = self.personal_models[self.current_profile].conversation_style
        
        base_text = f"Voici un texte créatif basé sur '{prompt}'"
        
        # Adaptation du style
        if style.get('enthusiasm', [0.5])[-1] > 0.7:
            base_text += " avec enthousiasme !"
        
        if style.get('formality', [0.5])[-1] < 0.3:
            base_text = base_text.replace('Voici', 'Voilà')
        
        return base_text
    
    def _generate_creative_code(self, prompt: str) -> str:
        """Génération de code personnalisé"""
        return f"""# Code généré personnellement pour: {prompt}
def solution_personnalisee():
    '''Solution adaptée à vos préférences de codage'''
    # Votre style de code personnel sera respecté ici
    return "Code personnalisé généré"

# Utilisation
result = solution_personnalisee()
print(result)
"""

def main():
    """Démonstration de O-RedMind"""
    print("🤖 O-RedMind - IA Personnelle Révolutionnaire")
    print("=" * 50)
    
    # Simulation d'un fort OpenRed
    fort_path = Path.home() / ".openred_demo"
    fort_path.mkdir(exist_ok=True)
    
    user_id = "demo_user"
    user_key = secrets.token_bytes(32)  # Clé simulée
    
    # Initialisation de O-RedMind
    oredmind = ORedMindCore(fort_path, user_id, user_key)
    
    print(f"✅ O-RedMind initialisé pour {user_id}")
    print(f"📍 Données stockées dans: {fort_path}")
    
    # Démonstration du consentement granulaire
    print("\n🔐 Gestion des consentements:")
    oredmind.consent_manager.grant_consent(
        'wikipedia_fr', 
        'Wikipédia Français', 
        'knowledge',
        expiry_days=30
    )
    
    # Test d'interactions multi-profils
    print("\n👤 Test des profils contextuels:")
    for profile in [ProfileContext.FAMILLE, ProfileContext.PROFESSIONNEL]:
        oredmind.switch_profile(profile)
        
        response = oredmind.process_user_interaction(
            f"J'aime travailler sur des projets créatifs en {profile.value}",
            {'source': 'demo'}
        )
        
        print(f"  {profile.value}: {response}")
    
    # Démonstration créative
    print("\n🎨 Génération créative:")
    creative_text = oredmind.generate_creative_content(
        "Écris un poème sur la technologie", 
        "text"
    )
    print(f"  Texte: {creative_text}")
    
    creative_code = oredmind.generate_creative_content(
        "Fonction pour calculer Fibonacci",
        "code"
    )
    print(f"  Code:\n{creative_code}")
    
    # Statut final
    print("\n📊 Statut d'apprentissage:")
    status = oredmind.get_learning_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n🎉 Démonstration terminée avec succès !")
    print("🔒 Vos données restent 100% privées et chiffrées localement.")
    print("✨ O-RedMind respecte parfaitement le Manifeste OpenRed !")

if __name__ == "__main__":
    main()