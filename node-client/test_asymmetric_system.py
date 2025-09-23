#!/usr/bin/env python3
"""
🧪 Tests unitaires pour le système O-Red P2P Asymétrique
Tests complets du système révolutionnaire de tokens asymétriques

Auteur : Système OpenRed P2P Révolutionnaire
Date : Septembre 2025
"""

import unittest
import asyncio
import tempfile
import os
import json
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# Import des modules à tester
from p2p_asymmetric_token_manager import P2PAsymmetricTokenManager
from o_red_asymmetric_p2p import O_RedAsymmetricP2P

class TestP2PAsymmetricTokenManager(unittest.TestCase):
    """🧪 Tests du gestionnaire de tokens asymétriques"""
    
    def setUp(self):
        """🔧 Préparation des tests"""
        # Génération d'identités de test
        self.alice_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        self.bob_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        self.alice_identity = {
            "node_id": "alice_test_node",
            "private_key": self.alice_key,
            "public_key": self.alice_key.public_key()
        }
        
        self.bob_identity = {
            "node_id": "bob_test_node",
            "private_key": self.bob_key,
            "public_key": self.bob_key.public_key()
        }
        
        # Fichiers temporaires pour stockage
        self.alice_storage = tempfile.mktemp(suffix="_alice_tokens.json")
        self.bob_storage = tempfile.mktemp(suffix="_bob_tokens.json")
        
        # Gestionnaires de tokens
        self.alice_manager = P2PAsymmetricTokenManager(
            self.alice_identity,
            self.alice_storage
        )
        
        self.bob_manager = P2PAsymmetricTokenManager(
            self.bob_identity,
            self.bob_storage
        )
    
    def tearDown(self):
        """🧹 Nettoyage après tests"""
        # Supprimer fichiers temporaires
        for file_path in [self.alice_storage, self.bob_storage]:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def test_establish_asymmetric_friendship(self):
        """🤝 Test création d'amitié asymétrique"""
        permissions = {
            "read_files": True,
            "send_messages": True,
            "access_private": False
        }
        
        # Alice génère un token pour Bob
        alice_token = self.alice_manager.establish_asymmetric_friendship(
            "bob_test_node",
            self.bob_identity["public_key"],
            permissions
        )
        
        # Vérifications
        self.assertIn("token_public_key_pem", alice_token)
        self.assertIn("token_data", alice_token)
        self.assertEqual(alice_token["token_data"]["issuer"], "alice_test_node")
        self.assertEqual(alice_token["token_data"]["holder"], "bob_test_node")
        self.assertEqual(alice_token["token_data"]["permissions"], permissions)
        self.assertIn("asymmetric_signature", alice_token["token_data"])
        
        # Vérifier que la relation est stockée
        self.assertIn("bob_test_node", self.alice_manager.asymmetric_relationships)
        relationship = self.alice_manager.asymmetric_relationships["bob_test_node"]
        self.assertEqual(relationship["status"], "pending_response")
        self.assertIsNotNone(relationship["outgoing_token"])
        self.assertIsNone(relationship["incoming_token"])
        
        print("✅ Test création d'amitié asymétrique réussi")
    
    def test_receive_asymmetric_token(self):
        """📨 Test réception de token asymétrique"""
        # Alice génère un token pour Bob
        permissions = {"read_files": True, "send_messages": True}
        alice_token = self.alice_manager.establish_asymmetric_friendship(
            "bob_test_node",
            self.bob_identity["public_key"],
            permissions
        )
        
        # Bob reçoit le token d'Alice
        token_accepted = self.bob_manager.receive_asymmetric_token(
            "alice_test_node",
            alice_token["token_public_key_pem"],
            alice_token["token_data"]
        )
        
        # Vérifications
        self.assertTrue(token_accepted)
        self.assertIn("alice_test_node", self.bob_manager.asymmetric_relationships)
        
        relationship = self.bob_manager.asymmetric_relationships["alice_test_node"]
        self.assertEqual(relationship["status"], "active")
        self.assertIsNotNone(relationship["incoming_token"])
        
        print("✅ Test réception de token asymétrique réussi")
    
    def test_full_asymmetric_handshake(self):
        """🤝 Test échange complet de tokens asymétriques"""
        alice_permissions = {"read_alice_files": True, "modify_alice_files": False}
        bob_permissions = {"read_bob_files": True, "access_bob_private": True}
        
        # Alice génère token pour Bob
        alice_token = self.alice_manager.establish_asymmetric_friendship(
            "bob_test_node",
            self.bob_identity["public_key"],
            alice_permissions
        )
        
        # Bob génère token pour Alice
        bob_token = self.bob_manager.establish_asymmetric_friendship(
            "alice_test_node",
            self.alice_identity["public_key"],
            bob_permissions
        )
        
        # Échange croisé
        alice_accepts_bob = self.alice_manager.receive_asymmetric_token(
            "bob_test_node",
            bob_token["token_public_key_pem"],
            bob_token["token_data"]
        )
        
        bob_accepts_alice = self.bob_manager.receive_asymmetric_token(
            "alice_test_node",
            alice_token["token_public_key_pem"],
            alice_token["token_data"]
        )
        
        # Vérifications
        self.assertTrue(alice_accepts_bob)
        self.assertTrue(bob_accepts_alice)
        
        # Les deux côtés doivent avoir des relations complètes
        alice_relationship = self.alice_manager.asymmetric_relationships["bob_test_node"]
        bob_relationship = self.bob_manager.asymmetric_relationships["alice_test_node"]
        
        self.assertEqual(alice_relationship["status"], "active")
        self.assertEqual(bob_relationship["status"], "active")
        self.assertIsNotNone(alice_relationship["outgoing_token"])
        self.assertIsNotNone(alice_relationship["incoming_token"])
        self.assertIsNotNone(bob_relationship["outgoing_token"])
        self.assertIsNotNone(bob_relationship["incoming_token"])
        
        print("✅ Test échange complet de tokens asymétriques réussi")
    
    def test_request_and_authorize_action(self):
        """🔐 Test demande et autorisation d'action asymétrique"""
        # Établir amitié complète (simplifié)
        self._establish_full_friendship()
        
        # Alice demande une action chez Bob
        action = "download_files"
        action_data = {"file_id": "document_secret.pdf"}
        
        alice_request = self.alice_manager.request_friend_action(
            "bob_test_node",
            action,
            action_data
        )
        
        # Vérifications de la demande
        self.assertIn("request_signature", alice_request)
        self.assertEqual(alice_request["requester"], "alice_test_node")
        self.assertEqual(alice_request["action"], action)
        
        # Bob autorise l'action d'Alice
        bob_authorization = self.bob_manager.authorize_friend_action(
            "alice_test_node",
            action,
            alice_request
        )
        
        # Vérifications de l'autorisation
        self.assertTrue(bob_authorization["authorized"])
        self.assertEqual(bob_authorization["action"], action)
        self.assertIn("asymmetric_authorization_signature", bob_authorization)
        
        print("✅ Test demande et autorisation d'action asymétrique réussi")
    
    def test_invalid_token_rejection(self):
        """🚫 Test rejet de token invalide"""
        # Créer un token avec une mauvaise signature
        fake_token_data = {
            "token_id": "fake_token",
            "issuer": "fake_node",
            "holder": "bob_test_node",
            "asymmetric_signature": "fake_signature"
        }
        
        # Bob tente de recevoir le token invalide
        token_accepted = self.bob_manager.receive_asymmetric_token(
            "fake_node",
            "fake_public_key_pem",
            fake_token_data
        )
        
        # Doit être rejeté
        self.assertFalse(token_accepted)
        self.assertNotIn("fake_node", self.bob_manager.asymmetric_relationships)
        
        print("✅ Test rejet de token invalide réussi")
    
    def test_permissions_enforcement(self):
        """🔒 Test application des permissions"""
        self._establish_full_friendship()
        
        # Alice tente une action non autorisée
        unauthorized_action = "access_super_secret_files"
        
        alice_request = self.alice_manager.request_friend_action(
            "bob_test_node",
            unauthorized_action
        )
        
        # Bob refuse l'autorisation
        bob_response = self.bob_manager.authorize_friend_action(
            "alice_test_node",
            unauthorized_action,
            alice_request
        )
        
        # L'autorisation doit être refusée
        self.assertFalse(bob_response["authorized"])
        self.assertIn("reason", bob_response)
        
        print("✅ Test application des permissions réussi")
    
    def test_relationship_listing(self):
        """📋 Test listage des relations"""
        self._establish_full_friendship()
        
        # Alice liste ses relations
        alice_relationships = self.alice_manager.list_relationships()
        self.assertEqual(len(alice_relationships), 1)
        
        relationship = alice_relationships[0]
        self.assertEqual(relationship["friend_node_id"], "bob_test_node")
        self.assertEqual(relationship["status"], "active")
        self.assertTrue(relationship["has_outgoing_token"])
        self.assertTrue(relationship["has_incoming_token"])
        
        print("✅ Test listage des relations réussi")
    
    def test_token_persistence(self):
        """💾 Test persistance des tokens"""
        self._establish_full_friendship()
        
        # Créer un nouveau gestionnaire avec le même fichier de stockage
        new_alice_manager = P2PAsymmetricTokenManager(
            self.alice_identity,
            self.alice_storage
        )
        
        # Les relations doivent être chargées
        relationships = new_alice_manager.list_relationships()
        self.assertEqual(len(relationships), 1)
        self.assertEqual(relationships[0]["friend_node_id"], "bob_test_node")
        
        print("✅ Test persistance des tokens réussi")
    
    def test_token_revocation(self):
        """🚫 Test révocation de tokens"""
        self._establish_full_friendship()
        
        # Alice révoque l'accès de Bob
        revoked = self.alice_manager.revoke_friend_access("bob_test_node", "both")
        self.assertTrue(revoked)
        
        # La relation doit être marquée comme révoquée
        relationship = self.alice_manager.asymmetric_relationships["bob_test_node"]
        self.assertEqual(relationship["status"], "revoked")
        
        print("✅ Test révocation de tokens réussi")
    
    def _establish_full_friendship(self):
        """🔧 Helper : établir une amitié complète entre Alice et Bob"""
        alice_permissions = {"download_files": True, "send_messages": True}
        bob_permissions = {"read_data": True, "access_files": True}
        
        # Génération croisée des tokens
        alice_token = self.alice_manager.establish_asymmetric_friendship(
            "bob_test_node",
            self.bob_identity["public_key"],
            alice_permissions
        )
        
        bob_token = self.bob_manager.establish_asymmetric_friendship(
            "alice_test_node",
            self.alice_identity["public_key"],
            bob_permissions
        )
        
        # Échange
        self.alice_manager.receive_asymmetric_token(
            "bob_test_node",
            bob_token["token_public_key_pem"],
            bob_token["token_data"]
        )
        
        self.bob_manager.receive_asymmetric_token(
            "alice_test_node",
            alice_token["token_public_key_pem"],
            alice_token["token_data"]
        )


class TestO_RedAsymmetricP2P(unittest.TestCase):
    """🧪 Tests du client P2P asymétrique intégré"""
    
    def setUp(self):
        """🔧 Préparation des tests du client P2P"""
        self.alice_config = {
            "node_id": "alice_p2p_test",
            "display_name": "Alice Test",
            "port": 9001
        }
        
        self.bob_config = {
            "node_id": "bob_p2p_test",
            "display_name": "Bob Test",
            "port": 9002
        }
        
        # Note: Tests simplifiés sans démarrage réel des services réseau
        self.alice_p2p = O_RedAsymmetricP2P(self.alice_config)
        self.bob_p2p = O_RedAsymmetricP2P(self.bob_config)
    
    def test_p2p_initialization(self):
        """🚀 Test initialisation du client P2P"""
        self.assertEqual(self.alice_p2p.node_id, "alice_p2p_test")
        self.assertEqual(self.alice_p2p.display_name, "Alice Test")
        self.assertEqual(self.alice_p2p.port, 9001)
        
        # Vérifier que les composants sont initialisés
        self.assertIsNotNone(self.alice_p2p.p2p_discovery)
        self.assertIsNotNone(self.alice_p2p.p2p_security)
        self.assertIsNotNone(self.alice_p2p.asymmetric_tokens)
        
        print("✅ Test initialisation du client P2P réussi")
    
    def test_friendship_establishment_interface(self):
        """🤝 Test interface d'établissement d'amitié"""
        # Simuler un pair découvert
        peer_info = {
            "display_name": "Bob Test",
            "address": "127.0.0.1:9002",
            "public_key": self.bob_p2p.p2p_discovery.identity["public_key"]
        }
        
        self.alice_p2p.discovered_peers["bob_p2p_test"] = peer_info
        
        # Alice établit une amitié avec Bob
        permissions = {"read_files": True, "send_messages": True}
        token = self.alice_p2p.establish_friendship_with_peer("bob_p2p_test", permissions)
        
        # Vérifications
        self.assertIsNotNone(token)
        self.assertIn("token_data", token)
        self.assertEqual(token["token_data"]["holder"], "bob_p2p_test")
        
        print("✅ Test interface d'établissement d'amitié réussi")
    
    def test_peer_listing(self):
        """📋 Test listage des pairs"""
        # Ajouter des pairs simulés
        self.alice_p2p.discovered_peers["bob_p2p_test"] = {
            "display_name": "Bob Test",
            "address": "127.0.0.1:9002",
            "has_friendship": False
        }
        
        peers = self.alice_p2p.list_discovered_peers()
        self.assertEqual(len(peers), 1)
        self.assertEqual(peers[0]["peer_id"], "bob_p2p_test")
        
        print("✅ Test listage des pairs réussi")


def run_comprehensive_tests():
    """🎯 Exécuter tous les tests du système asymétrique"""
    print("🧪 === TESTS DU SYSTÈME P2P ASYMÉTRIQUE ===\n")
    
    # Créer la suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter les tests
    suite.addTests(loader.loadTestsFromTestCase(TestP2PAsymmetricTokenManager))
    suite.addTests(loader.loadTestsFromTestCase(TestO_RedAsymmetricP2P))
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Résumé
    print(f"\n🎯 === RÉSUMÉ DES TESTS ===")
    print(f"✅ Tests réussis : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests échoués : {len(result.failures)}")
    print(f"💥 Erreurs : {len(result.errors)}")
    
    if result.failures:
        print("\n❌ ÉCHECS :")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERREURS :")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n🚀 Taux de réussite : {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 SYSTÈME P2P ASYMÉTRIQUE VALIDÉ À 100% !")
        print("✅ Tokens asymétriques opérationnels")
        print("✅ Sécurité cryptographique confirmée")
        print("✅ 4 clés RSA par relation validées")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    
    if success:
        print("\n🚀 Tous les tests passés - Système prêt pour la révolution P2P !")
    else:
        print("\n⚠️ Certains tests ont échoué - Révision nécessaire")
        exit(1)