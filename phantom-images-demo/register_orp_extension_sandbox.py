#!/usr/bin/env python3
"""
register_orp_extension_sandbox.py
=================================
Version de test pour associer l'extension .orp à orp_viewer_sandbox.py dans Windows.
"""

import os
import sys
import winreg
from pathlib import Path
import subprocess

def register_orp_extension_sandbox():
    """Enregistre l'extension .orp pour le viewer sandbox"""
    current_dir = Path(__file__).parent
    viewer_path = current_dir / "orp_viewer_sandbox.py"
    python_exe = sys.executable
    if not viewer_path.exists():
        print("❌ Erreur: orp_viewer_sandbox.py non trouvé")
        return False
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.orp") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "OpenRedPhantomSandbox")
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantomSandbox") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Fichier OpenRed PHANTOM (Sandbox)")
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantomSandbox\DefaultIcon") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"{python_exe},0")
        command = f'"{python_exe}" "{viewer_path}" "%1"'
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantomSandbox\shell\open\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
        print("✅ Extension .orp associée au viewer sandbox !")
        print(f"📂 Viewer: {viewer_path}")
        print(f"🐍 Python: {python_exe}")
        print(f"💻 Commande: {command}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'association: {e}")
        return False

def unregister_orp_extension_sandbox():
    """Supprime l'association sandbox .orp"""
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.orp")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantomSandbox\shell\open\command")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantomSandbox\DefaultIcon")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\OpenRedPhantomSandbox")
        print("✅ Association sandbox supprimée !")
        return True
    except Exception as e:
        print(f"❌ Erreur suppression: {e}")
        return False

def main():
    print("🔧 ASSOCIATION EXTENSION .ORP (SANDBOX)")
    print("=====================================")
    print("1. Associer l'extension .orp au viewer sandbox")
    print("2. Supprimer l'association sandbox")
    print("3. Quitter")
    choix = input("Choisissez une option (1-3): ").strip()
    if choix == "1":
        register_orp_extension_sandbox()
    elif choix == "2":
        unregister_orp_extension_sandbox()
    else:
        print("Fin.")

if __name__ == "__main__":
    main()
