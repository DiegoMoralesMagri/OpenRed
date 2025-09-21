#!/usr/bin/env python3
"""
Direct authentication endpoints testing
Comprehensive testing of authentication API endpoints
"""

import sys
import os
import asyncio
from datetime import datetime

# Add src directory to PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_auth_endpoints():
    """Test authentication endpoints directly"""
    try:
        print("🔍 Direct authentication endpoints testing...")
        
        # Import authentication endpoints
        from src.api.v1.endpoints.auth import register_node, login, refresh_token, logout
        from src.api.v1.endpoints.auth import LoginRequest, RegisterRequest
        from src.database.connection import init_database
        
        # Initialize database
        print("📍 Database initialization...")
        init_database()
        print("✅ Database initialized")
        
        # Test 1: Register
        print("\n📍 Test register...")
        register_data = RegisterRequest(
            node_id="test_node_001",
            name="Test Node",
            type="node",
            public_key="test_public_key_here",
            endpoint="http://localhost:3000",
            capabilities=["messaging", "routing"]
        )
        try:
            register_result = await register_node(register_data)
            print(f"✅ register_node: {register_result}")
        except Exception as e:
            print(f"⚠️ register_node error: {str(e)}")
        
        # Test 2: Login
        print("\n📍 Test login...")
        login_data = LoginRequest(
            node_id="test_node_001",
            challenge_response="challenge_response_here"
        )
        try:
            login_result = await login(login_data)
            print(f"✅ login: {login_result}")
            
            # Extraction du token pour les tests suivants
            access_token = login_result.get("access_token") if isinstance(login_result, dict) else None
            refresh_token_value = login_result.get("refresh_token") if isinstance(login_result, dict) else None
            
        except Exception as e:
            print(f"⚠️ login error: {str(e)}")
            access_token = None
            refresh_token_value = None
        
        # Test 3: Refresh Token (si nous avons un refresh token)
        if refresh_token_value:
            print("\n📍 Test refresh token...")
            try:
                refresh_result = await refresh_token(refresh_token_value)
                print(f"✅ refresh_token: {refresh_result}")
            except Exception as e:
                print(f"⚠️ refresh_token error: {str(e)}")
        
        # Test 4: Logout (si nous avons un access token)
        if access_token:
            print("\n📍 Test logout...")
            try:
                logout_result = await logout(access_token)
                print(f"✅ logout: {logout_result}")
            except Exception as e:
                print(f"⚠️ logout error: {str(e)}")
        
    except Exception as e:
        print(f"❌ Erreur lors du test auth: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_models():
    """Test les modèles de données"""
    try:
        print("\n🔍 Test des modèles de données...")
        
        from src.api.v1.endpoints.auth import LoginRequest, RegisterRequest, LoginResponse
        from src.models.schemas import NodeRegistration, NodeResponse
        
        # Test RegisterRequest
        print("📍 Test RegisterRequest...")
        register_req = RegisterRequest(
            node_id="test_node_002",
            name="Test Node 2",
            type="node",
            public_key="test_public_key",
            endpoint="http://localhost:3001",
            capabilities=["messaging"]
        )
        print(f"✅ RegisterRequest: {register_req}")
        
        # Test LoginRequest  
        print("📍 Test LoginRequest...")
        login_req = LoginRequest(
            node_id="test_node_002",
            challenge_response="test_challenge"
        )
        print(f"✅ LoginRequest: {login_req}")
        
        # Test NodeRegistration from schemas
        print("📍 Test NodeRegistration...")
        node_reg = NodeRegistration(
            username="test_username",
            server_url="https://example.com",
            public_key="test_public_key_data"
        )
        print(f"✅ NodeRegistration: {node_reg}")
        
    except Exception as e:
        print(f"❌ Erreur lors du test models: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_database_models():
    """Test les modèles de base de données"""
    try:
        print("\n🔍 Test des modèles de base de données...")
        
        from src.database.connection import init_database, get_db_session
        from src.models.database import Node, Message
        
        # Initialisation
        init_database()
        
        print("📍 Test création de node...")
        with get_db_session() as session:
            # Créer un node de test
            test_node = Node(
                node_id="db_test_node_001",
                display_name="Database Test Node",
                server_url="https://test.example.com",
                public_key="test_public_key_database",
                version="1.0.0"
            )
            session.add(test_node)
            session.commit()
            
            # Vérifier que le node a été créé
            node_count = session.query(Node).filter(Node.node_id == "db_test_node_001").count()
            print(f"✅ Node créé: {node_count} trouvé(s)")
            
        print("📍 Test modèle Message...")
        print("✅ Modèles de base de données importés avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors du test database models: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Tests principaux"""
    print("🚀 OpenRed Central API - Tests d'authentification directs")
    print("=" * 60)
    
    await test_models()
    await test_database_models()
    await test_auth_endpoints()
    
    print("\n🏁 Tests d'authentification terminés!")

if __name__ == "__main__":
    asyncio.run(main())
