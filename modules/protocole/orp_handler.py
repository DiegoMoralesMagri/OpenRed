#!/usr/bin/env python3
"""
🎯 OpenRed Network - Handler URL orp://
Script appelé par le système pour traiter les URLs orp://
"""

import sys
import os

# Ajout du chemin du module OpenRed
script_dir = os.path.dirname(os.path.abspath(__file__))
openred_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, openred_dir)


def main():
    """Fonction principale du handler"""
    if len(sys.argv) < 2:
        print("❌ Usage: orp_handler.py <url_orp>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        # Import du gestionnaire de protocole
        from modules.protocole import GestionnaireProtocole
        
        print(f"🌐 Handler orp:// appelé avec: {url}")
        
        # Traitement de l'URL
        gestionnaire = GestionnaireProtocole()
        resultat = gestionnaire.traiter_url(url)
        
        if resultat:
            print("✅ URL traitée avec succès")
            sys.exit(0)
        else:
            print("❌ Échec traitement URL")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erreur handler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
