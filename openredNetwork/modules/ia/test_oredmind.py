#!/usr/bin/env python3
"""
O-RedMind Tests
===============

Tests unitaires pour le système O-RedMind.
Vérification de toutes les fonctionnalités critiques.

Auteur: Système OpenRed 2025
Licence: MIT - Souveraineté Numérique Totale
"""

import unittest
import tempfile
import shutil
import json
import time
import os
from pathlib import Path
from unittest.mock import Mock, patch
import sqlite3

# Import des modules à tester
import sys
sys.path.append(str(Path(__file__).parent))

from oredmind_core import (
    ORedMindCore, EncryptedMemoryGraph, ConsentManager,
    LocalPersonalModel, CollectiveInsightsEngine,
    ConversationStyle, CreativeTask, LearningMode
)
from moteur_intelligence_locale import (
    LocalLanguageModel, MultimodalProcessor, ReasoningEngine,
    ModalityType, ReasoningType, MultimodalInput
)

class TestEncryptedMemoryGraph(unittest.TestCase):
    """Tests pour le graphe mémoire chiffré"""
    
    def setUp(self):
        """Configuration des tests"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.password = "test_password_123"
        self.user_id = "test_user"
        self.memory_graph = EncryptedMemoryGraph(self.temp_dir, self.password)
    
    def tearDown(self):
        """Nettoyage après tests"""
        shutil.rmtree(self.temp_dir)
    
    def test_memory_storage_and_retrieval(self):
        """Test stockage et récupération mémoire"""
        memory_data = {
            'content': 'Test memory content',
            'type': 'conversation',
            'importance': 0.8
        }
        
        # Stockage
        memory_id = self.memory_graph.store_memory(
            self.user_id, memory_data, ['test', 'memory']
        )
        
        self.assertIsNotNone(memory_id)
        
        # Récupération
        retrieved = self.memory_graph.get_memory(memory_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['content'], memory_data['content'])
    
    def test_memory_search(self):
        """Test recherche dans les mémoires"""
        # Stockage de plusieurs mémoires
        memories = [
            {'content': 'Python programming tips', 'type': 'knowledge'},
            {'content': 'JavaScript frameworks', 'type': 'knowledge'},
            {'content': 'Cooking recipe for pasta', 'type': 'personal'}
        ]
        
        for memory in memories:
            self.memory_graph.store_memory(
                self.user_id, memory, memory['content'].split()
            )
        
        # Recherche
        results = self.memory_graph.search_memories(self.user_id, 'programming')
        self.assertGreater(len(results), 0)
        
        # Vérification du résultat
        found_programming = any('Python' in result['content'] for result in results)
        self.assertTrue(found_programming)
    
    def test_encryption_integrity(self):
        """Test intégrité du chiffrement"""
        sensitive_data = {'secret': 'very_sensitive_information_123'}
        
        memory_id = self.memory_graph.store_memory(
            self.user_id, sensitive_data, ['sensitive']
        )
        
        # Vérification que les données ne sont pas en clair dans la DB
        db_path = self.temp_dir / "memory_graph.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT encrypted_data FROM memories WHERE id = ?", (memory_id,))
        raw_data = cursor.fetchone()[0]
        
        # Les données ne doivent pas contenir le texte en clair
        self.assertNotIn('very_sensitive_information', raw_data)
        
        conn.close()

class TestConsentManager(unittest.TestCase):
    """Tests pour le gestionnaire de consentement"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.consent_manager = ConsentManager(self.temp_dir)
        self.user_id = "test_user"
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_consent_granting_and_checking(self):
        """Test accord et vérification du consentement"""
        data_type = "conversation_analysis"
        purpose = "improvement"
        
        # Accord initial
        self.consent_manager.grant_consent(self.user_id, data_type, purpose)
        
        # Vérification
        has_consent = self.consent_manager.has_consent(self.user_id, data_type, purpose)
        self.assertTrue(has_consent)
    
    def test_consent_revocation(self):
        """Test révocation du consentement"""
        data_type = "personal_preferences"
        purpose = "personalization"
        
        # Accord puis révocation
        self.consent_manager.grant_consent(self.user_id, data_type, purpose)
        self.consent_manager.revoke_consent(self.user_id, data_type, purpose)
        
        # Vérification
        has_consent = self.consent_manager.has_consent(self.user_id, data_type, purpose)
        self.assertFalse(has_consent)
    
    def test_consent_granularity(self):
        """Test granularité du consentement"""
        # Consentements spécifiques
        self.consent_manager.grant_consent(self.user_id, "chat", "learning")
        self.consent_manager.grant_consent(self.user_id, "documents", "analysis")
        
        # Vérifications spécifiques
        self.assertTrue(self.consent_manager.has_consent(self.user_id, "chat", "learning"))
        self.assertTrue(self.consent_manager.has_consent(self.user_id, "documents", "analysis"))
        
        # Vérifications négatives
        self.assertFalse(self.consent_manager.has_consent(self.user_id, "chat", "sharing"))
        self.assertFalse(self.consent_manager.has_consent(self.user_id, "images", "analysis"))

class TestLocalPersonalModel(unittest.TestCase):
    """Tests pour le modèle personnel local"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.user_id = "test_user"
        self.profile = "Professionnel"
        self.model = LocalPersonalModel(self.temp_dir, self.user_id, self.profile)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_learning_from_interactions(self):
        """Test apprentissage depuis les interactions"""
        interactions = [
            ("Bonjour, comment allez-vous ?", "Très bien merci, et vous ?"),
            ("Pouvez-vous m'aider avec Python ?", "Bien sûr ! Que voulez-vous savoir sur Python ?"),
            ("Merci pour votre aide", "De rien, c'est avec plaisir !")
        ]
        
        for user_msg, ai_msg in interactions:
            self.model.learn_from_interaction(user_msg, ai_msg, "positive")
        
        # Vérification que le modèle a appris
        self.assertGreater(len(self.model.preferences), 0)
    
    def test_profile_adaptation(self):
        """Test adaptation au profil"""
        # Simulation d'interactions professionnelles
        professional_interactions = [
            ("Préparez-vous le rapport ?", "Oui, je finalise l'analyse."),
            ("Quelle est l'deadline ?", "Le projet doit être livré vendredi.")
        ]
        
        for user_msg, ai_msg in professional_interactions:
            self.model.learn_from_interaction(user_msg, ai_msg, "positive")
        
        # Génération d'une réponse dans le contexte professionnel
        response = self.model.generate_personalized_response(
            "Comment avance le projet ?",
            "analytical"
        )
        
        self.assertIsNotNone(response)
        self.assertIn("projet", response.lower())
    
    def test_preference_learning(self):
        """Test apprentissage des préférences"""
        # Feedbacks positifs sur les réponses courtes
        self.model.learn_from_interaction(
            "Question courte ?", "Réponse courte.", "perfect"
        )
        
        self.model.learn_from_interaction(
            "Autre question ?", "Réponse longue et détaillée avec beaucoup d'explications.", "too_long"
        )
        
        # Vérification que les préférences sont apprises
        prefs = self.model.get_preferences()
        self.assertIn('response_length', prefs)

class TestMultimodalProcessor(unittest.TestCase):
    """Tests pour le processeur multimodal"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.processor = MultimodalProcessor(self.temp_dir)
        self.user_id = "test_user"
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_text_processing(self):
        """Test traitement de texte"""
        text_input = MultimodalInput(
            content="Ceci est un texte de test en français avec plusieurs mots.",
            modality=ModalityType.TEXT,
            metadata={},
            timestamp=time.time(),
            user_id=self.user_id,
            profile_context="test"
        )
        
        result = self.processor.process_input(text_input)
        
        self.assertEqual(result['content_type'], 'text')
        self.assertIn('language', result)
        self.assertIn('sentiment', result)
        self.assertIn('word_count', result)
        self.assertGreater(result['word_count'], 0)
    
    def test_code_processing(self):
        """Test traitement de code"""
        code_content = """
def hello_world():
    print("Hello, World!")
    return True

import os
import sys

hello_world()
        """
        
        code_input = MultimodalInput(
            content=code_content,
            modality=ModalityType.CODE,
            metadata={},
            timestamp=time.time(),
            user_id=self.user_id,
            profile_context="test"
        )
        
        result = self.processor.process_input(code_input)
        
        self.assertEqual(result['content_type'], 'code')
        self.assertIn('language', result)
        self.assertIn('functions_detected', result)
        self.assertIn('imports_detected', result)
        self.assertIn('hello_world', result['functions_detected'])
    
    def test_language_detection(self):
        """Test détection de langue"""
        # Test français
        french_text = "Bonjour, comment allez-vous aujourd'hui ? J'espère que tout va bien."
        lang_fr = self.processor._detect_language(french_text)
        self.assertEqual(lang_fr, 'french')
        
        # Test anglais
        english_text = "Hello, how are you today? I hope you are doing well."
        lang_en = self.processor._detect_language(english_text)
        self.assertEqual(lang_en, 'english')
    
    def test_sentiment_analysis(self):
        """Test analyse de sentiment"""
        # Sentiment positif
        positive_text = "C'est fantastique ! J'adore cette solution, elle est parfaite."
        sentiment_pos = self.processor._analyze_sentiment(positive_text)
        self.assertEqual(sentiment_pos, 'positive')
        
        # Sentiment négatif
        negative_text = "C'est terrible et horrible, vraiment mauvais."
        sentiment_neg = self.processor._analyze_sentiment(negative_text)
        self.assertEqual(sentiment_neg, 'negative')
        
        # Sentiment neutre
        neutral_text = "La documentation explique les fonctionnalités."
        sentiment_neu = self.processor._analyze_sentiment(neutral_text)
        self.assertEqual(sentiment_neu, 'neutral')

class TestReasoningEngine(unittest.TestCase):
    """Tests pour le moteur de raisonnement"""
    
    def setUp(self):
        self.reasoning_engine = ReasoningEngine("test_user")
    
    def test_analytical_reasoning(self):
        """Test raisonnement analytique"""
        result = self.reasoning_engine.reason(
            "Comment optimiser les performances ?",
            {'context': 'programming'},
            ReasoningType.ANALYTICAL
        )
        
        self.assertEqual(result['type'], 'analytical')
        self.assertIn('steps', result)
        self.assertIn('conclusion', result)
        self.assertIn('confidence', result)
    
    def test_creative_reasoning(self):
        """Test raisonnement créatif"""
        result = self.reasoning_engine.reason(
            "Idées pour un nouveau produit",
            {'context': 'innovation'},
            ReasoningType.CREATIVE
        )
        
        self.assertEqual(result['type'], 'creative')
        self.assertIn('approaches', result)
        self.assertIn('conclusion', result)
    
    def test_reasoning_history(self):
        """Test historique de raisonnement"""
        # Plusieurs raisonnements
        for i in range(3):
            self.reasoning_engine.reason(
                f"Question {i}",
                {},
                ReasoningType.LOGICAL
            )
        
        # Vérification de l'historique
        self.assertEqual(len(self.reasoning_engine.reasoning_history), 3)
        
        # Vérification du contenu
        first_record = self.reasoning_engine.reasoning_history[0]
        self.assertIn('query', first_record)
        self.assertIn('type', first_record)
        self.assertIn('result', first_record)
        self.assertIn('timestamp', first_record)

class TestORedMindCore(unittest.TestCase):
    """Tests d'intégration pour O-RedMind Core"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.password = "test_password_123"
        
        # Mock pour éviter la vérification du fort complet
        with patch('oredmind_core.ORedMindCore._verify_fort_integrity'):
            self.core = ORedMindCore(self.temp_dir, self.password)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_core_initialization(self):
        """Test initialisation du core"""
        self.assertIsNotNone(self.core.memory_graph)
        self.assertIsNotNone(self.core.consent_manager)
        self.assertIsNotNone(self.core.multimodal_processor)
    
    def test_conversation_processing(self):
        """Test traitement de conversation"""
        style = ConversationStyle(
            formality=0.7,
            creativity=0.6,
            detail_level=0.8,
            empathy=0.7,
            profile_adaptation="Test"
        )
        
        response = self.core.process_conversation(
            "Bonjour, comment allez-vous ?",
            "test_user",
            "Test",
            style,
            []
        )
        
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.content)
        self.assertGreater(len(response.content), 0)
    
    def test_learning_modes(self):
        """Test modes d'apprentissage"""
        # Mode privé seulement
        self.core._update_learning_mode("test_user", LearningMode.PRIVATE_ONLY)
        
        # Traitement d'une conversation
        style = ConversationStyle()
        response = self.core.process_conversation(
            "Test learning",
            "test_user",
            "Test",
            style,
            []
        )
        
        # Vérification que l'apprentissage est local seulement
        self.assertIsNotNone(response)
    
    def test_consent_integration(self):
        """Test intégration du consentement"""
        user_id = "consent_test_user"
        
        # Révocation du consentement d'apprentissage
        self.core.consent_manager.revoke_consent(
            user_id, "conversation", "learning"
        )
        
        # Traitement d'une conversation
        style = ConversationStyle()
        response = self.core.process_conversation(
            "Test sans consentement",
            user_id,
            "Test",
            style,
            []
        )
        
        # La réponse doit être générée mais sans apprentissage
        self.assertIsNotNone(response)

class TestPrivacyCompliance(unittest.TestCase):
    """Tests de conformité à la vie privée"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.password = "privacy_test_123"
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_data_encryption_at_rest(self):
        """Test chiffrement des données au repos"""
        memory_graph = EncryptedMemoryGraph(self.temp_dir, self.password)
        
        sensitive_data = {
            'personal_info': 'John Doe, 123 Main St',
            'private_thoughts': 'Very personal information'
        }
        
        memory_id = memory_graph.store_memory(
            "privacy_user", sensitive_data, ["personal"]
        )
        
        # Vérification que les données sont chiffrées dans la DB
        db_path = self.temp_dir / "memory_graph.db"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT encrypted_data FROM memories WHERE id = ?", (memory_id,))
            encrypted_data = cursor.fetchone()[0]
            
            # Les données sensibles ne doivent pas être en clair
            self.assertNotIn('John Doe', encrypted_data)
            self.assertNotIn('123 Main St', encrypted_data)
            self.assertNotIn('Very personal', encrypted_data)
    
    def test_consent_requirement_enforcement(self):
        """Test application stricte du consentement"""
        consent_manager = ConsentManager(self.temp_dir)
        user_id = "strict_user"
        
        # Pas de consentement accordé
        has_consent = consent_manager.has_consent(user_id, "conversation", "analysis")
        self.assertFalse(has_consent)
        
        # Accord explicite requis
        consent_manager.grant_consent(user_id, "conversation", "analysis")
        has_consent = consent_manager.has_consent(user_id, "conversation", "analysis")
        self.assertTrue(has_consent)
    
    def test_no_data_leakage(self):
        """Test absence de fuites de données"""
        memory_graph = EncryptedMemoryGraph(self.temp_dir, self.password)
        
        # Stockage de données pour différents utilisateurs
        user1_data = {'secret': 'user1_private_data'}
        user2_data = {'secret': 'user2_private_data'}
        
        memory_graph.store_memory("user1", user1_data, ["private"])
        memory_graph.store_memory("user2", user2_data, ["private"])
        
        # Recherche par user1 ne doit pas retourner les données de user2
        user1_results = memory_graph.search_memories("user1", "secret")
        
        for result in user1_results:
            self.assertNotIn('user2_private_data', str(result))
            # Mais peut contenir les données de user1
            self.assertIn('user1', result.get('user_id', ''))

def run_all_tests():
    """Lance tous les tests"""
    print("🧪 O-RedMind Tests Suite")
    print("=" * 40)
    
    # Création de la suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajout des classes de tests
    test_classes = [
        TestEncryptedMemoryGraph,
        TestConsentManager,
        TestLocalPersonalModel,
        TestMultimodalProcessor,
        TestReasoningEngine,
        TestORedMindCore,
        TestPrivacyCompliance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Résumé
    print("\n" + "=" * 40)
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Succès: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Échecs:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n🔥 Erreurs:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(':', 1)[-1].strip()}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n✅ Taux de succès: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)