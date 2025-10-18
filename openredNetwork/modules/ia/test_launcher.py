#!/usr/bin/env python3
"""
Test Launcher O-RedMind
=======================

Test direct du launcher sans problèmes d'imports.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

print("🚀 Test Launcher O-RedMind")
print("=" * 45)

# Configuration des chemins
fort_path = Path.home() / ".openred"
config_path = fort_path / "config"
logs_path = fort_path / "logs"
models_path = fort_path / "models"

# Création des dossiers
print("📁 Création des dossiers...")
directories = [fort_path, config_path, logs_path, models_path]

for directory in directories:
    directory.mkdir(exist_ok=True, parents=True)
    print(f"   ✅ {directory}")

# Test des modules disponibles
print("\n📦 Vérification des modules...")

modules_status = {}

# Test oredmind_core
try:
    import oredmind_core
    modules_status['oredmind_core'] = True
    print("   ✅ O-RedMind Core")
except Exception as e:
    modules_status['oredmind_core'] = False
    print(f"   ❌ O-RedMind Core: {e}")

# Test moteur_intelligence_locale
try:
    import moteur_intelligence_locale
    modules_status['moteur_intelligence_locale'] = True
    print("   ✅ Moteur Intelligence Locale")
except Exception as e:
    modules_status['moteur_intelligence_locale'] = False
    print(f"   ❌ Moteur Intelligence Locale: {e}")

# Test interface_web
try:
    import interface_web
    modules_status['interface_web'] = True
    print("   ✅ Interface Web")
except Exception as e:
    modules_status['interface_web'] = False
    print(f"   ❌ Interface Web: {e}")

# Test Flask et SocketIO
try:
    import flask
    import flask_socketio
    modules_status['web_deps'] = True
    print("   ✅ Dépendances Web (Flask/SocketIO)")
except Exception as e:
    modules_status['web_deps'] = False
    print(f"   ❌ Dépendances Web: {e}")

# Status système
print("\n🧠 Status Système O-RedMind")
print("=" * 35)
print(f"📍 Fort OpenRed: {fort_path}")
print(f"🔧 Core O-RedMind: {'✅ OK' if modules_status.get('oredmind_core') else '❌ NOK'}")
print(f"🌐 Interface Web: {'✅ OK' if modules_status.get('interface_web') else '❌ NOK'}")
print(f"🧠 Moteur IA: {'✅ OK' if modules_status.get('moteur_intelligence_locale') else '❌ NOK'}")
print(f"💾 Stockage: {'✅ OK' if fort_path.exists() and os.access(fort_path, os.W_OK) else '❌ NOK'}")
print(f"🌍 Mode Réseau: Local")
print(f"⏰ Vérification: {datetime.now().strftime('%H:%M:%S')}")

# Compte des modèles
model_files = list(models_path.glob("*.json"))
print(f"📚 Modèles trouvés: {len(model_files)}")

# Test de performance
print("\n⚡ Test de performance...")
start_time = time.time()

# Test création fichier temporaire
test_file = fort_path / "test_perf.tmp"
try:
    with open(test_file, 'w') as f:
        f.write("test" * 1000)
    test_file.unlink()
    write_time = time.time() - start_time
    print(f"   Écriture disque: ✅ {write_time:.3f}s")
except Exception as e:
    print(f"   Écriture disque: ❌ {e}")

# Test mémoire
try:
    test_data = list(range(100000))
    memory_time = time.time() - start_time - write_time
    print(f"   Allocation mémoire: ✅ {memory_time:.3f}s")
except Exception as e:
    print(f"   Allocation mémoire: ❌ {e}")

total_time = time.time() - start_time
print(f"\n⏱️  Tests terminés en {total_time:.2f}s")

# Recommandations
print("\n💡 Recommandations:")
all_modules_ok = all(modules_status.values())

if all_modules_ok:
    print("   ✅ Système complètement opérationnel !")
    print("   🚀 Prêt pour le lancement de l'interface web")
else:
    if not modules_status.get('oredmind_core'):
        print("   ⚠️  Problème avec O-RedMind Core")
    if not modules_status.get('interface_web'):
        print("   ⚠️  Problème avec l'Interface Web")
    if not modules_status.get('moteur_intelligence_locale'):
        print("   ⚠️  Problème avec le Moteur IA")

if total_time > 2.0:
    print("   ⚠️  Performance système lente")
else:
    print("   ✅ Performance système optimale")

# Instructions de lancement
if all_modules_ok:
    print("\n🎯 Instructions de lancement:")
    print("   python interface_web.py     # Interface web directe")
    print("   python oredmind_launcher.py --web --no-browser  # Via launcher")
    print("\n🌐 URL d'accès: http://localhost:5000")

print(f"\n🎉 O-RedMind prêt à révolutionner votre IA personnelle !")