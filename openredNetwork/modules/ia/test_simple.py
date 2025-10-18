#!/usr/bin/env python3
"""
Test Simple O-RedMind
=====================

Test rapide des composants O-RedMind sans imports complexes.
"""

import sys
from pathlib import Path
import tempfile
import shutil
import time

print("🧠 Test Simple O-RedMind")
print("=" * 40)

# Test 1: Import des modules
print("\n📦 Test des imports...")

try:
    import oredmind_core
    print("   ✅ oredmind_core importé")
except Exception as e:
    print(f"   ❌ oredmind_core: {e}")

try:
    import moteur_intelligence_locale
    print("   ✅ moteur_intelligence_locale importé")
except Exception as e:
    print(f"   ❌ moteur_intelligence_locale: {e}")

try:
    import interface_web
    print("   ✅ interface_web importé")
except Exception as e:
    print(f"   ❌ interface_web: {e}")

# Test 2: Dépendances critiques
print("\n🔧 Test des dépendances...")

critical_deps = [
    ("cryptography", "Chiffrement"),
    ("numpy", "Calculs numériques"),
    ("PIL", "Traitement d'images"),
    ("flask", "Framework web"),
    ("flask_socketio", "WebSockets"),
    ("sqlite3", "Base de données")
]

for dep, desc in critical_deps:
    try:
        __import__(dep)
        print(f"   ✅ {desc} ({dep})")
    except ImportError:
        print(f"   ❌ {desc} ({dep}) manquant")

# Test 3: Création des dossiers
print("\n📁 Test création dossiers...")

fort_path = Path.home() / ".openred_test"
try:
    fort_path.mkdir(exist_ok=True)
    (fort_path / "models").mkdir(exist_ok=True)
    (fort_path / "logs").mkdir(exist_ok=True)
    (fort_path / "uploads").mkdir(exist_ok=True)
    print("   ✅ Dossiers créés avec succès")
    
    # Nettoyage
    shutil.rmtree(fort_path)
    print("   ✅ Nettoyage effectué")
    
except Exception as e:
    print(f"   ❌ Erreur dossiers: {e}")

# Test 4: SQLite
print("\n💾 Test SQLite...")

try:
    import sqlite3
    test_db = tempfile.mktemp(suffix='.db')
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE test (
            id INTEGER PRIMARY KEY,
            data TEXT
        )
    ''')
    
    cursor.execute("INSERT INTO test (data) VALUES (?)", ("test_data",))
    conn.commit()
    
    cursor.execute("SELECT data FROM test WHERE id = 1")
    result = cursor.fetchone()
    
    conn.close()
    Path(test_db).unlink()
    
    if result and result[0] == "test_data":
        print("   ✅ SQLite opérationnel")
    else:
        print("   ❌ Problème avec SQLite")
        
except Exception as e:
    print(f"   ❌ Erreur SQLite: {e}")

# Test 5: Chiffrement simple
print("\n🔒 Test chiffrement...")

try:
    from cryptography.fernet import Fernet
    
    key = Fernet.generate_key()
    cipher = Fernet(key)
    
    message = "Message secret de test"
    encrypted = cipher.encrypt(message.encode())
    decrypted = cipher.decrypt(encrypted).decode()
    
    if decrypted == message:
        print("   ✅ Chiffrement opérationnel")
    else:
        print("   ❌ Problème de chiffrement")
        
except Exception as e:
    print(f"   ❌ Erreur chiffrement: {e}")

# Test 6: Performance simple
print("\n⚡ Test performance...")

try:
    start_time = time.time()
    
    # Test calcul
    import numpy as np
    data = np.random.random((1000, 100))
    result = np.mean(data)
    
    calc_time = time.time() - start_time
    
    # Test I/O
    start_io = time.time()
    test_file = tempfile.mktemp()
    with open(test_file, 'w') as f:
        f.write("test" * 1000)
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    Path(test_file).unlink()
    io_time = time.time() - start_io
    
    print(f"   ✅ Calcul: {calc_time:.3f}s")
    print(f"   ✅ I/O: {io_time:.3f}s")
    
except Exception as e:
    print(f"   ❌ Erreur performance: {e}")

print("\n🎯 Test terminé !")
print("Si toutes les vérifications sont ✅, O-RedMind est prêt !")