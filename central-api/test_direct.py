#!/usr/bin/env python3
"""
Test direct des endpoints sans serveur
Direct endpoint testing without server
"""

import sys
import os
import asyncio

# Ajout du répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_health_endpoints():
    """Test les endpoints de santé directement"""
    try:
        print("🔍 Test direct des endpoints de santé...")
        
        # Import des endpoints de santé
        from src.api.v1.endpoints.health import health_check, liveness_probe, readiness_probe
        
        # Test health_check
        print("📍 Test health_check...")
        result = await health_check()
        print(f"✅ health_check: {result}")
        
        # Test liveness_probe
        print("📍 Test liveness_probe...")
        result = await liveness_probe()
        print(f"✅ liveness_probe: {result}")
        
        # Test readiness_probe
        print("📍 Test readiness_probe...")
        result = await readiness_probe()
        print(f"✅ readiness_probe: {result}")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_database():
    """Test la connexion à la base de données"""
    try:
        print("\n🔍 Test de la base de données...")
        
        from src.database.connection import init_database, get_db_session
        
        # Initialisation
        print("📍 Initialisation de la base de données...")
        init_database()
        print("✅ Base de données initialisée")
        
        # Test de session
        print("📍 Test de session...")
        with get_db_session() as session:
            print("✅ Session de base de données obtenue")
            print(f"✅ Type de session: {type(session)}")
            # Ici on pourrait faire des requêtes de test
        
    except Exception as e:
        print(f"❌ Erreur base de données: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Tests principaux"""
    print("🚀 OpenRed Central API - Tests directs")
    print("=" * 50)
    
    await test_health_endpoints()
    await test_database()
    
    print("\n🏁 Tests directs terminés!")

if __name__ == "__main__":
    asyncio.run(main())
