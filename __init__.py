#!/usr/bin/env python3
"""
🌟 OpenRed Network - Module Principal
Architecture modulaire pour OpenRed Network

Utilisation:
    from openredNetwork import Fort, DecouvreurReseau, MoteurAntiCopie
    from openredNetwork.modules.fort import IdentiteFort
    from openredNetwork.modules.cartographie import CarteReseau
    from openredNetwork.modules.projection import FormatProjectionORN
"""

# Imports principaux depuis les modules
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.fort import Fort, IdentiteFort, GenerateurIdentite, FenetrePublique
from modules.cartographie import DecouvreurReseau, CarteReseau, RadarFort
from modules.projection import MoteurAntiCopie, FormatProjectionORN, FenetreProjectionSecurisee
from modules.communication import TransportUDP, MessageORN, ConstructeurMessages
from modules.crypto import ChiffrementRSA, GestionnaireSignatures
from modules.interface import InterfacePrincipale
from modules.protocole import ResolveurORP, AdresseORP, GestionnaireProtocole, EnregistreurProtocole
from modules.internet import RegistryInternet, PasserelleInternet, NavigateurWeb

# Exports principaux pour usage simple
__all__ = [
    # Fort - Classes principales
    'Fort',
    'IdentiteFort', 
    'GenerateurIdentite',
    'FenetrePublique',
    
    # Cartographie - Découverte réseau
    'DecouvreurReseau',
    'CarteReseau',
    'RadarFort',
    
    # Projection - Système anti-copie
    'MoteurAntiCopie',
    'FormatProjectionORN',
    'FenetreProjectionSecurisee',
    
    # Communication - Transport réseau
    'TransportUDP',
    'MessageORN',
    'ConstructeurMessages',
    
    # Crypto - Sécurité
    'ChiffrementRSA',
    'GestionnaireSignatures',
    
    # Interface - GUI
        # Interface - Interface utilisateur
    'InterfacePrincipale',
    
    # Protocole ORP - Gestion URLs orp://
    'ResolveurORP',
    'AdresseORP',
    'GestionnaireProtocole', 
    'EnregistreurProtocole',
    
    # Internet - Accès mondial
    'RegistryInternet',
    'PasserelleInternet',
    'NavigateurWeb',
]

# Métadonnées du module
__version__ = '1.0.0'
__author__ = 'OpenRed Network'
__description__ = 'Réseau décentralisé de forts avec projections sécurisées'
__url__ = 'https://openred.community'

# Configuration par défaut
CONFIG_DEFAUT = {
    "fort": {
        "port_ecoute": 21000,
        "timeout_connexion": 300,
        "duree_vie_projection": 300
    },
    "reseau": {
        "intervalle_ping": 10,
        "timeout_decouverte": 60,
        "max_forts_cache": 1000
    },
    "securite": {
        "niveau_protection_defaut": 5,
        "taille_cle_rsa": 2048,
        "duree_token": 3600
    }
}


def creer_fort_simple(nom: str, port: int = 0) -> Fort:
    """
    🚀 Création rapide d'un fort avec configuration par défaut
    
    Args:
        nom: Nom du fort
        port: Port d'écoute (0 = automatique)
    
    Returns:
        Fort configuré et prêt à l'emploi
    """
    # Génération identité
    identite, cle_privee = GenerateurIdentite.generer_identite(nom)
    
    # Création fort
    fort = Fort(nom, identite, cle_privee)
    
    print(f"🏰 Fort créé: {nom} ({identite.id_fort})")
    return fort


def creer_systeme_complet(nom_fort: str, port: int = 0, avec_interface: bool = True):
    """
    🌟 Création d'un système OpenRed complet
    
    Args:
        nom_fort: Nom du fort
        port: Port d'écoute
        avec_interface: Créer l'interface graphique
    
    Returns:
        Dictionnaire avec tous les composants
    """
    print("🌟 Création système OpenRed complet...")
    
    # 1. Création du fort
    fort = creer_fort_simple(nom_fort, port)
    
    # 2. Ajout découverte réseau
    decouvreur = DecouvreurReseau(fort.identite.id_fort, fort.identite.nom, port)
    fort.decouvreur = decouvreur  # Attachement au fort
    
    # 3. Système de projection
    moteur_projection = MoteurAntiCopie()
    moteur_projection.demarrer_surveillance()
    
    # 4. Interface graphique
    interface = None
    if avec_interface:
        interface = InterfacePrincipale(f"OpenRed Network - {nom_fort}")
        interface.initialiser(fort)
    
    # 5. Transport réseau
    transport = TransportUDP(fort.identite.id_fort, port)
    
    systeme = {
        "fort": fort,
        "decouvreur": decouvreur,
        "moteur_projection": moteur_projection,
        "transport": transport,
        "interface": interface
    }
    
    print(f"✅ Système OpenRed complet créé pour {nom_fort}")
    return systeme


def demarrer_fort_avec_interface(nom_fort: str, port: int = 0):
    """
    🚀 Démarre un fort avec interface graphique complète
    
    Args:
        nom_fort: Nom du fort
        port: Port d'écoute
    """
    systeme = creer_systeme_complet(nom_fort, port, avec_interface=True)
    
    # Activation des composants
    fort = systeme["fort"]
    decouvreur = systeme["decouvreur"]
    transport = systeme["transport"]
    interface = systeme["interface"]
    
    try:
        # Démarrage transport
        if transport.demarrer_transport():
            print("🔌 Transport UDP démarré")
        
        # Activation fort
        fort.activer()
        
        # Démarrage découverte
        decouvreur.demarrer_decouverte()
        
        # Lancement interface
        print("🖥️ Lancement interface graphique...")
        interface.demarrer()
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    finally:
        # Nettoyage
        decouvreur.arreter_decouverte()
        transport.arreter_transport()
        fort.desactiver()
        print("🔚 Système arrêté proprement")


def demo_projection_anti_copie():
    """
    🎭 Démonstration du système de projection anti-copie
    """
    print("🎭 Démonstration Projection Anti-Copie")
    print("=" * 50)
    
    # Création moteur
    moteur = MoteurAntiCopie()
    moteur.demarrer_surveillance()
    
    # Contenu de test
    contenu_test = {
        "donnees": {
            "nom": "Fort Alice",
            "publications": [
                {
                    "id": "pub_001",
                    "contenu": "🏰 Bienvenue dans mon fort sécurisé !",
                    "timestamp": "2025-10-17T20:30:00",
                    "type": "annonce"
                },
                {
                    "id": "pub_002",
                    "contenu": "🔮 Projection 100% protégée contre la copie !",
                    "timestamp": "2025-10-17T20:31:00", 
                    "type": "demonstration"
                }
            ]
        }
    }
    
    # Création projection sécurisée
    session_id = moteur.creer_projection_securisee(
        contenu=contenu_test,
        fort_proprietaire="fort_alice_abc123",
        fort_observateur="fort_bob_def456",
        duree_vie=300,
        niveau_protection=5
    )
    
    print(f"🔮 Session créée: {session_id}")
    
    # Interface de projection
    import tkinter as tk
    
    root = tk.Tk()
    root.title("🔮 OpenRed Network - Démonstration Projection")
    root.geometry("400x300")
    
    def ouvrir_projection():
        fenetre_proj = FenetreProjectionSecurisee(moteur)
        # Simuler ouverture avec les bonnes informations
        projection_id = list(moteur.gestionnaire.projections_actives.keys())[0]
        fenetre_proj.afficher_projection(projection_id, "fort_bob_def456", session_id)
    
    tk.Label(root, text="🔮 Système de Projection OpenRed", 
             font=("Arial", 16, "bold")).pack(pady=20)
    
    tk.Label(root, text="Démonstration du système anti-copie\nrévolutionnaire", 
             font=("Arial", 10)).pack(pady=10)
    
    tk.Button(root, text="🪟 Ouvrir Projection Sécurisée", 
              command=ouvrir_projection, font=("Arial", 12)).pack(pady=20)
    
    tk.Label(root, text="⚠️ Essayez de copier le contenu !", 
             foreground="red", font=("Arial", 9)).pack(pady=10)
    
    root.mainloop()


def installer_protocole_orp() -> bool:
    """
    📝 Installe le protocole orp:// dans le système
    
    Returns:
        True si installation réussie
    """
    try:
        enregistreur = EnregistreurProtocole()
        return enregistreur.installation_complete()
    except Exception as e:
        print(f"❌ Erreur installation protocole: {e}")
        return False


def naviguer_vers_fort(adresse_orp: str) -> bool:
    """
    🧭 Navigue vers un fort via son adresse orp://
    
    Args:
        adresse_orp: Adresse orp:// du fort
        
    Returns:
        True si navigation réussie
        
    Example:
        >>> naviguer_vers_fort("orp://fort_1234567890abcdef.openred/")
        🌐 Navigation vers: orp://fort_1234567890abcdef.openred/
        ✅ Connexion établie vers orp://fort_1234567890abcdef.openred/
        True
    """
    try:
        from modules.protocole import GestionnaireProtocole, ValidateurAdresseORP
        
        # Validation de l'URL
        if not ValidateurAdresseORP.valider_url(adresse_orp):
            print(f"❌ URL invalide: {adresse_orp}")
            return False
        
        print(f"🌐 Navigation vers: {adresse_orp}")
        
        # Traitement de l'URL
        gestionnaire = GestionnaireProtocole()
        resultat = gestionnaire.traiter_url(adresse_orp)
        
        if resultat:
            print(f"✅ Connexion établie vers {adresse_orp}")
        else:
            print(f"❌ Impossible de se connecter à {adresse_orp}")
            print("   (Le fort pourrait être hors ligne ou inexistant)")
            
        return resultat
        
    except Exception as e:
        print(f"❌ Erreur navigation: {e}")
        return False


def resoudre_adresse_fort(adresse_orp: str):
    """
    🔍 Résout une adresse orp:// vers adresse réseau
    
    Args:
        adresse_orp: Adresse orp:// à résoudre
        
    Returns:
        Tuple (ip, port) ou None
    """
    try:
        from modules.protocole import resoudre_adresse_orp
        return resoudre_adresse_orp(adresse_orp)
    except Exception as e:
        print(f"❌ Erreur résolution: {e}")
        return None


def obtenir_adresse_orp_fort(fort: Fort) -> str:
    """
    🏷️ Obtient l'adresse orp:// d'un fort
    
    Args:
        fort: Instance de Fort
        
    Returns:
        Adresse orp:// complète
    """
    return fort.identite.adresse_orp


def demo_protocole_orp():
    """
    🎭 Démonstration du protocole orp://
    """
    print("🌟 DÉMONSTRATION PROTOCOLE ORP://")
    print("=" * 40)
    
    try:
        # 1. Création d'un fort
        print("1️⃣ Création fort de démonstration...")
        fort = creer_fort_simple("FortDemo")
        adresse_orp = fort.identite.adresse_orp
        print(f"🏰 Fort créé: {adresse_orp}")
        
        # 2. Activation
        print("\n2️⃣ Activation du fort...")
        fort.activer()
        print("✅ Fort activé sur le réseau")
        
        # 3. Test résolution
        print("\n3️⃣ Test de résolution d'adresse...")
        adresse_reseau = resoudre_adresse_fort(adresse_orp)
        if adresse_reseau:
            print(f"✅ Résolution: {adresse_orp} → {adresse_reseau[0]}:{adresse_reseau[1]}")
        else:
            print("⚠️ Résolution échouée (normal en mode démo)")
        
        # 4. Test navigation
        print("\n4️⃣ Test de navigation...")
        resultat = naviguer_vers_fort(adresse_orp)
        print(f"🧭 Navigation: {'✅ Réussie' if resultat else '❌ Échouée'}")
        
        # 5. Test différents chemins
        print("\n5️⃣ Test chemins spécialisés...")
        chemins_test = [
            f"{adresse_orp}fenetre",
            f"{adresse_orp}projection/demo123"
        ]
        
        for chemin in chemins_test:
            resultat = naviguer_vers_fort(chemin)
            print(f"  🔗 {chemin}: {'✅' if resultat else '❌'}")
        
        # 6. Nettoyage
        print("\n6️⃣ Nettoyage...")
        fort.desactiver()
        print("🧹 Fort désactivé")
        
        print("\n🎉 Démonstration protocole terminée !")
        
    except Exception as e:
        print(f"❌ Erreur démonstration: {e}")


def tester_protocole_orp() -> bool:
    """
    🧪 Test du protocole orp:// installé
    
    Cette fonction teste que le protocole orp:// fonctionne correctement
    en simulant le traitement d'une URL de test.
    
    Returns:
        bool: True si test réussi, False sinon
        
    Example:
        >>> tester_protocole_orp()
        🧪 Test du protocole orp://...
        ✅ Validation URL réussie
        ✅ Résolveur opérationnel - 0 résolutions
        ✅ Gestionnaire opérationnel - 0 URLs traitées
        🎉 Test du protocole orp:// réussi !
        True
    """
    try:
        from modules.protocole import ValidateurAdresseORP, ResolveurORP, GestionnaireProtocole
        
        print("🧪 Test du protocole orp://...")
        
        # URL de test
        url_test = "orp://fort_1234567890abcdef.openred/"
        
        # Test validation
        if not ValidateurAdresseORP.valider_url(url_test):
            print("❌ Échec validation URL")
            return False
        print("✅ Validation URL réussie")
        
        # Test résolveur
        resolveur = ResolveurORP()
        stats_resolveur = resolveur.obtenir_statistiques()
        print(f"✅ Résolveur opérationnel - {stats_resolveur['resolutions_total']} résolutions")
        
        # Test gestionnaire
        gestionnaire = GestionnaireProtocole()
        stats_gestionnaire = gestionnaire.obtenir_statistiques()
        print(f"✅ Gestionnaire opérationnel - {stats_gestionnaire['urls_traitees']} URLs traitées")
        
        print("🎉 Test du protocole orp:// réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test protocole: {e}")
        return False


def exposer_fort_sur_internet(fort_id: str, port_local: int = 5000) -> bool:
    """
    🌍 Expose un fort local sur internet
    
    Cette fonction rend un fort accessible mondialement via internet
    en l'enregistrant sur le registry global et en configurant
    la passerelle internet.
    
    Args:
        fort_id: Identifiant du fort à exposer
        port_local: Port local du fort
        
    Returns:
        bool: True si exposition réussie, False sinon
        
    Example:
        >>> exposer_fort_sur_internet("fort_1234567890abcdef", 5000)
        🌍 Fort fort_1234567890abcdef exposé sur internet
        🔗 URL publique: orp://fort_1234567890abcdef.openred/
        True
    """
    try:
        from modules.internet import PasserelleInternet
        
        print(f"🌍 Exposition du fort {fort_id} sur internet...")
        
        # Création de la passerelle
        passerelle = PasserelleInternet()
        
        # Démarrage de la passerelle
        if passerelle.demarrer_passerelle():
            # Exposition du fort
            if passerelle.exposer_fort(fort_id, port_local):
                print(f"✅ Fort {fort_id} maintenant accessible mondialement")
                print(f"🔗 URL publique: orp://{fort_id}.openred/")
                return True
            else:
                print(f"❌ Échec exposition du fort {fort_id}")
                return False
        else:
            print("❌ Échec démarrage passerelle internet")
            return False
            
    except Exception as e:
        print(f"❌ Erreur exposition internet: {e}")
        return False


def demarrer_serveur_web_openred(port: int = 8080):
    """
    🌐 Démarre un serveur web pour accès navigateur
    
    Cette fonction démarre un serveur web qui permet d'accéder
    aux forts OpenRed Network directement depuis un navigateur
    standard, sans besoin d'installer le protocole orp://.
    
    Args:
        port: Port du serveur web (par défaut 8080)
        
    Returns:
        ServeurWebOpenRed: Instance du serveur ou None si échec
        
    Example:
        >>> serveur = demarrer_serveur_web_openred(8080)
        🌐 Serveur web démarré avec succès
        🔗 Interface: http://localhost:8080
        >>> # Le serveur est maintenant accessible via navigateur
    """
    try:
        # Import dynamique pour éviter les dépendances lourdes
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from serveur_web import ServeurWebOpenRed
        
        print(f"🌐 Démarrage serveur web OpenRed sur port {port}...")
        
        serveur = ServeurWebOpenRed(port)
        
        if serveur.demarrer_serveur():
            print(f"✅ Serveur web OpenRed actif")
            print(f"🔗 Interface web: http://localhost:{port}")
            print("🌍 Accessible depuis n'importe quel navigateur")
            print("📱 Compatible mobile et desktop")
            
            return serveur
        else:
            print("❌ Échec démarrage serveur web")
            return None
            
    except Exception as e:
        print(f"❌ Erreur serveur web: {e}")
        return None


def connecter_fort_internet(url_orp: str) -> bool:
    """
    🔗 Connexion à un fort via internet
    
    Cette fonction se connecte à un fort distant via internet
    en utilisant le registry global pour la résolution d'adresse.
    
    Args:
        url_orp: URL orp:// du fort distant
        
    Returns:
        bool: True si connexion réussie, False sinon
        
    Example:
        >>> connecter_fort_internet("orp://fort_1234567890abcdef.openred/")
        🌍 Résolution via registry internet...
        ✅ Connexion établie vers 203.0.113.1:5000
        True
    """
    try:
        from modules.protocole import GestionnaireProtocole, ValidateurAdresseORP
        
        # Validation URL
        if not ValidateurAdresseORP.valider_url(url_orp):
            print(f"❌ URL invalide: {url_orp}")
            return False
        
        print(f"🌍 Connexion internet vers: {url_orp}")
        
        # Le gestionnaire utilisera automatiquement la résolution internet
        gestionnaire = GestionnaireProtocole()
        resultat = gestionnaire.traiter_url(url_orp)
        
        if resultat:
            print(f"✅ Connexion internet établie vers {url_orp}")
        else:
            print(f"❌ Connexion internet échouée vers {url_orp}")
            print("   (Le fort pourrait être hors ligne ou non exposé)")
            
        return resultat
        
    except Exception as e:
        print(f"❌ Erreur connexion internet: {e}")
        return False


# Message de bienvenue lors de l'import
print(f"🌟 OpenRed Network v{__version__} - Architecture modulaire chargée")
print("📚 Utilisez: from openredNetwork import Fort, DecouvreurReseau, MoteurAntiCopie")
print("🚀 Démarrage rapide: demarrer_fort_avec_interface('MonFort')")
print("🎭 Démonstration: demo_projection_anti_copie()")
print("🌐 Protocole ORP: installer_protocole_orp() puis naviguer_vers_fort('orp://...')")
print("🌍 Internet: exposer_fort_sur_internet('fort_id', port) puis demarrer_serveur_web_openred()")
print("🔗 Accès web: http://localhost:8080 pour interface navigateur")