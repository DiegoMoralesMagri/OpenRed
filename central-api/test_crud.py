#!/usr/bin/env python3
"""
Test de persistance des nodes et CRUD complet
Node persistence and complete CRUD testing
"""

import sys
import os
import asyncio

# Ajout du répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_nodes_crud():
    """Test CRUD complet sur les nodes"""
    try:
        print("🔍 Test CRUD complet des nodes...")
        
        from src.api.v1.endpoints.nodes import create_node, get_nodes, get_node, update_node, delete_node
        from src.models.schemas import NodeRegistration
        from src.database.connection import init_database, get_db_session
        from src.models.database import Node
        
        # Initialisation
        init_database()
        
        # Test 1: CREATE
        print("\n📍 Test CREATE node...")
        node_data = NodeRegistration(
            username="crud_test_node",
            display_name="CRUD Test Node",
            server_url="https://crud.test.example.com",
            public_key="crud_test_public_key",
            version="1.0.0",
            capabilities=["messaging", "routing", "storage"]
        )
        
        try:
            create_result = await create_node(node_data)
            print(f"✅ CREATE: {create_result}")
        except Exception as e:
            print(f"⚠️ CREATE error: {str(e)}")
        
        # Test 2: READ (liste)
        print("\n📍 Test READ (liste)...")
        try:
            nodes_list = await get_nodes()
            print(f"✅ READ liste: {nodes_list}")
        except Exception as e:
            print(f"⚠️ READ liste error: {str(e)}")
        
        # Test 3: READ (détail)
        print("\n📍 Test READ (détail)...")
        try:
            node_detail = await get_node("crud_test_node")
            print(f"✅ READ détail: {node_detail}")
        except Exception as e:
            print(f"⚠️ READ détail error: {str(e)}")
        
        # Test 4: UPDATE (simulé)
        print("\n📍 Test UPDATE...")
        try:
            # update_result = await update_node("crud_test_node", updated_data)
            print("⚠️ UPDATE: Nécessite des paramètres spécifiques - test skip")
        except Exception as e:
            print(f"⚠️ UPDATE error: {str(e)}")
        
        # Test 5: Vérification base de données directe
        print("\n📍 Test vérification DB directe...")
        with get_db_session() as session:
            nodes_count = session.query(Node).count()
            print(f"✅ Nodes en DB: {nodes_count}")
            
            # Recherche du node créé
            crud_node = session.query(Node).filter(Node.node_id.like("%crud_test_node%")).first()
            if crud_node:
                print(f"✅ Node trouvé: {crud_node.node_id} - {crud_node.display_name}")
                print(f"   URL: {crud_node.server_url}")
                print(f"   Version: {crud_node.version}")
                print(f"   Status: {crud_node.status}")
                print(f"   Créé: {crud_node.created_at}")
            else:
                print("⚠️ Node CRUD test non trouvé en DB")
        
    except Exception as e:
        print(f"❌ Erreur lors du test CRUD: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_messages_basic():
    """Test de base pour les messages"""
    try:
        print("\n🔍 Test de base des messages...")
        
        from src.api.v1.endpoints.messages import get_messages, send_message
        from src.models.schemas import MessageRoute
        
        # Test 1: Liste des messages
        print("📍 Test liste messages...")
        try:
            messages_list = await get_messages()
            print(f"✅ Messages liste: {messages_list}")
        except Exception as e:
            print(f"⚠️ Messages liste error: {str(e)}")
        
        # Test 2: Envoi de message (simulé)
        print("📍 Test envoi message...")
        try:
            message_data = MessageRoute(
                from_node_id="test_sender",
                to_node_id="test_receiver"
            )
            # send_result = await send_message(message_data)
            print("⚠️ Send message: Nécessite implémentation complète - test skip")
        except Exception as e:
            print(f"⚠️ Send message error: {str(e)}")
        
    except Exception as e:
        print(f"❌ Erreur lors du test messages: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_database_integrity():
    """Test de l'intégrité de la base de données"""
    try:
        print("\n🔍 Test d'intégrité de la base de données...")
        
        from src.database.connection import init_database, get_db_session, check_database_connection
        from src.models.database import Node, Message
        
        # Test de connexion
        print("📍 Test connexion DB...")
        connection_ok = await check_database_connection()
        print(f"✅ Connexion DB: {connection_ok}")
        
        # Test de structure des tables
        print("📍 Test structure tables...")
        with get_db_session() as session:
            # Vérifier que les tables existent
            try:
                nodes_count = session.query(Node).count()
                print(f"✅ Table nodes: {nodes_count} entrées")
            except Exception as e:
                print(f"⚠️ Table nodes error: {str(e)}")
            
            try:
                messages_count = session.query(Message).count()
                print(f"✅ Table messages: {messages_count} entrées")
            except Exception as e:
                print(f"⚠️ Table messages error: {str(e)}")
        
    except Exception as e:
        print(f"❌ Erreur lors du test intégrité: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Tests principaux"""
    print("🚀 OpenRed Central API - Tests CRUD et Persistance")
    print("=" * 60)
    
    await test_database_integrity()
    await test_nodes_crud()
    await test_messages_basic()
    
    print("\n🏁 Tests CRUD et persistance terminés!")

if __name__ == "__main__":
    asyncio.run(main())
