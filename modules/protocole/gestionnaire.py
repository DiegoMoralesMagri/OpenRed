#!/usr/bin/env python3
"""
🎛️ OpenRed Network - Gestionnaire de Protocole ORP
Gestionnaire principal pour les URLs orp:// et actions associées
"""

import sys
import subprocess
import webbrowser
from typing import Dict, Optional, Callable, Any, List
from urllib.parse import urlparse

from .resolveur import AdresseORP, ResolveurORP


class GestionnaireProtocole:
    """
    🎛️ Gestionnaire principal du protocole orp://
    """
    
    def __init__(self):
        self.resolveur = ResolveurORP()
        
        # Handlers pour différents types d'actions
        self.handlers = {
            'racine': self._handle_racine,
            'fenetre': self._handle_fenetre,
            'projection': self._handle_projection,
            'connexion': self._handle_connexion
        }
        
        # Cache des forts connectés
        self.forts_connectes = {}
        
        # Statistiques
        self.stats = {
            'urls_traitees': 0,
            'connexions_etablies': 0,
            'projections_ouvertes': 0,
            'erreurs': 0
        }
    
    def traiter_url(self, url: str) -> bool:
        """
        🎯 Traite une URL orp:// complète
        
        Args:
            url: URL orp:// à traiter
            
        Returns:
            True si traité avec succès, False sinon
        """
        try:
            print(f"🌐 Traitement URL: {url}")
            
            # Parse de l'adresse
            adresse = AdresseORP.from_url(url)
            
            # Résolution de l'adresse réseau
            adresse_reseau = self.resolveur.resoudre(url)
            if not adresse_reseau:
                print(f"❌ Impossible de résoudre: {url}")
                self.stats['erreurs'] += 1
                return False
            
            # Détermination du type d'action
            type_action = self._determiner_type_action(adresse)
            
            # Exécution du handler approprié
            if type_action in self.handlers:
                resultat = self.handlers[type_action](adresse, adresse_reseau)
                if resultat:
                    self.stats['urls_traitees'] += 1
                    print(f"✅ URL traitée avec succès: {url}")
                    return True
            
            print(f"❌ Aucun handler pour: {type_action}")
            self.stats['erreurs'] += 1
            return False
            
        except Exception as e:
            print(f"❌ Erreur traitement URL {url}: {e}")
            self.stats['erreurs'] += 1
            return False
    
    def _determiner_type_action(self, adresse: AdresseORP) -> str:
        """Détermine le type d'action à effectuer"""
        if adresse.est_racine():
            return 'racine'
        elif adresse.est_fenetre():
            return 'fenetre'
        elif adresse.est_projection():
            return 'projection'
        else:
            return 'connexion'
    
    def _handle_racine(self, adresse: AdresseORP, adresse_reseau: tuple) -> bool:
        """Traite accès à la racine d'un fort"""
        try:
            print(f"🏰 Connexion à la racine du fort: {adresse.fort_id}")
            
            # Établissement connexion avec le fort
            fort_distant = self._etablir_connexion_fort(adresse.fort_id, adresse_reseau)
            if not fort_distant:
                return False
            
            # Affichage informations de base du fort
            self._afficher_informations_fort(fort_distant)
            
            # Ouverture interface de connexion
            self._ouvrir_interface_connexion(fort_distant)
            
            self.stats['connexions_etablies'] += 1
            return True
            
        except Exception as e:
            print(f"❌ Erreur connexion racine: {e}")
            return False
    
    def _handle_fenetre(self, adresse: AdresseORP, adresse_reseau: tuple) -> bool:
        """Traite accès à la fenêtre publique d'un fort"""
        try:
            print(f"🪟 Ouverture fenêtre publique: {adresse.fort_id}")
            
            # Récupération fenêtre publique
            fenetre_publique = self._recuperer_fenetre_publique(
                adresse.fort_id, adresse_reseau
            )
            if not fenetre_publique:
                return False
            
            # Affichage fenêtre publique
            self._afficher_fenetre_publique(fenetre_publique)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur ouverture fenêtre: {e}")
            return False
    
    def _handle_projection(self, adresse: AdresseORP, adresse_reseau: tuple) -> bool:
        """Traite accès à une projection"""
        try:
            id_projection = adresse.obtenir_id_projection()
            print(f"🔮 Ouverture projection: {id_projection}")
            
            # Vérification permissions
            if not self._verifier_permissions_projection(id_projection, adresse.fort_id):
                print("❌ Permissions insuffisantes pour cette projection")
                return False
            
            # Ouverture projection sécurisée
            resultat = self._ouvrir_projection_securisee(
                id_projection, adresse.fort_id, adresse_reseau, adresse.parametres
            )
            
            if resultat:
                self.stats['projections_ouvertes'] += 1
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Erreur ouverture projection: {e}")
            return False
    
    def _handle_connexion(self, adresse: AdresseORP, adresse_reseau: tuple) -> bool:
        """Traite connexion générique"""
        try:
            print(f"🔗 Connexion générique: {adresse.chemin}")
            
            # Traitement chemin personnalisé
            # TODO: Implémenter selon besoins spécifiques
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur connexion générique: {e}")
            return False
    
    def _etablir_connexion_fort(self, fort_id: str, adresse_reseau: tuple) -> Optional[Dict]:
        """Établit connexion avec un fort distant"""
        try:
            # Import dynamique pour éviter circular imports
            import __init__ as openredNetwork
            
            # Création client de connexion
            transport = openredNetwork.TransportUDP("client_temp", 0)
            
            # Message de connexion
            message_ping = openredNetwork.ConstructeurMessages.creer_ping(
                "client_temp", fort_id
            )
            
            # Envoi ping
            if transport.envoyer_message(message_ping, adresse_reseau):
                print(f"✅ Connexion établie avec {fort_id}")
                
                # Cache de la connexion
                fort_info = {
                    'id': fort_id,
                    'adresse': adresse_reseau,
                    'transport': transport,
                    'derniere_activite': "2025-10-17T21:00:00"
                }
                self.forts_connectes[fort_id] = fort_info
                
                return fort_info
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur établissement connexion: {e}")
            return None
    
    def _recuperer_fenetre_publique(self, fort_id: str, adresse_reseau: tuple) -> Optional[Dict]:
        """Récupère la fenêtre publique d'un fort"""
        try:
            # TODO: Implémentation récupération fenêtre publique
            # Message de demande de fenêtre publique
            
            # Simulation pour l'instant
            fenetre_publique = {
                'fort_id': fort_id,
                'profil': {
                    'nom': f"Fort {fort_id[-8:]}",
                    'description': "Fort OpenRed découvert",
                    'services': ['chat', 'projection']
                },
                'publications': [
                    {
                        'timestamp': "2025-10-17T21:00:00",
                        'contenu': "Bienvenue sur mon fort OpenRed !"
                    }
                ]
            }
            
            return fenetre_publique
            
        except Exception as e:
            print(f"❌ Erreur récupération fenêtre: {e}")
            return None
    
    def _verifier_permissions_projection(self, id_projection: str, fort_proprietaire: str) -> bool:
        """Vérifie permissions d'accès à une projection"""
        # TODO: Implémentation vérification permissions
        # - Vérification session active
        # - Contrôle des droits d'accès
        # - Validation des signatures
        
        # Pour l'instant, autorisation simple
        return True
    
    def _ouvrir_projection_securisee(self, id_projection: str, fort_id: str, 
                                   adresse_reseau: tuple, parametres: Dict) -> bool:
        """Ouvre une projection sécurisée"""
        try:
            # Import du moteur de projection
            import __init__ as openredNetwork
            
            # Simulation ouverture projection
            print(f"🔮 Ouverture projection sécurisée: {id_projection}")
            print(f"🏰 Fort propriétaire: {fort_id}")
            print(f"📋 Paramètres: {parametres}")
            
            # TODO: Intégration avec MoteurAntiCopie
            # moteur = openredNetwork.MoteurAntiCopie()
            # resultat = moteur.acceder_projection_securisee(
            #     id_projection, "fort_observateur", session_id
            # )
            
            print("✅ Projection ouverte (simulation)")
            return True
            
        except Exception as e:
            print(f"❌ Erreur ouverture projection: {e}")
            return False
    
    def _afficher_informations_fort(self, fort_info: Dict):
        """Affiche informations d'un fort connecté"""
        print("🏰 INFORMATIONS DU FORT")
        print("=" * 30)
        print(f"🆔 ID: {fort_info['id']}")
        print(f"🌐 Adresse: {fort_info['adresse'][0]}:{fort_info['adresse'][1]}")
        print(f"⏰ Connexion: {fort_info['derniere_activite']}")
        print()
    
    def _afficher_fenetre_publique(self, fenetre: Dict):
        """Affiche contenu fenêtre publique"""
        print("🪟 FENÊTRE PUBLIQUE")
        print("=" * 30)
        print(f"🏰 Fort: {fenetre['profil']['nom']}")
        print(f"📝 Description: {fenetre['profil']['description']}")
        print(f"🛠️ Services: {', '.join(fenetre['profil']['services'])}")
        print()
        
        if fenetre.get('publications'):
            print("📢 Publications:")
            for pub in fenetre['publications']:
                print(f"  • {pub['contenu']} ({pub['timestamp']})")
        print()
    
    def _ouvrir_interface_connexion(self, fort_info: Dict):
        """Ouvre interface de connexion au fort"""
        # TODO: Ouverture interface graphique spécialisée
        print(f"💻 Interface de connexion disponible pour {fort_info['id']}")
    
    def obtenir_statistiques(self) -> Dict:
        """Retourne statistiques du gestionnaire"""
        return {
            'urls_traitees': self.stats['urls_traitees'],
            'connexions_etablies': self.stats['connexions_etablies'],
            'projections_ouvertes': self.stats['projections_ouvertes'],
            'erreurs': self.stats['erreurs'],
            'forts_connectes': len(self.forts_connectes),
            'resolution_stats': self.resolveur.obtenir_statistiques()
        }
    
    def lister_connexions_actives(self) -> List[Dict]:
        """Liste les connexions actives"""
        return list(self.forts_connectes.values())


class NavigateurORP:
    """
    🧭 Navigateur spécialisé pour URLs orp://
    """
    
    def __init__(self):
        self.gestionnaire = GestionnaireProtocole()
        self.historique = []
    
    def naviguer(self, url: str) -> bool:
        """Navigation vers une URL orp://"""
        try:
            # Validation URL
            if not url.startswith('orp://'):
                print(f"❌ URL invalide: {url} (doit commencer par orp://)")
                return False
            
            # Ajout à l'historique
            self.historique.append(url)
            
            # Traitement par le gestionnaire
            resultat = self.gestionnaire.traiter_url(url)
            
            if resultat:
                print(f"🧭 Navigation réussie vers: {url}")
            else:
                print(f"❌ Échec navigation vers: {url}")
            
            return resultat
            
        except Exception as e:
            print(f"❌ Erreur navigation: {e}")
            return False
    
    def obtenir_historique(self) -> List[str]:
        """Retourne l'historique de navigation"""
        return self.historique.copy()
    
    def vider_historique(self):
        """Vide l'historique de navigation"""
        self.historique.clear()
        print("🧹 Historique de navigation vidé")


# Instance globale du gestionnaire
gestionnaire_global = GestionnaireProtocole()
navigateur_global = NavigateurORP()


def traiter_url_orp(url: str) -> bool:
    """
    🎯 Fonction helper pour traitement simple d'URL orp://
    
    Args:
        url: URL orp:// à traiter
        
    Returns:
        True si traité avec succès
    """
    return gestionnaire_global.traiter_url(url)


def naviguer_vers(url: str) -> bool:
    """
    🧭 Fonction helper pour navigation
    
    Args:
        url: URL orp:// destination
        
    Returns:
        True si navigation réussie
    """
    return navigateur_global.naviguer(url)