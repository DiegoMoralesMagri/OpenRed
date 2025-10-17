#!/usr/bin/env python3
"""
🌐 SERVEUR WEB MULTI-PROFILS OPENRED
===================================

Serveur web intégré pour l'interface multi-profils révolutionnaire.
Interface fluide pour gérer vos identités contextuelles avec 
sécurité cryptographique et expérience utilisateur optimale.

Fonctionnalités :
- API REST pour gestion des profils
- Interface web responsive
- Intégration avec le fort existant
- Chiffrement bout-en-bout
- Basculement contextuel fluide
"""

import os
import json
import time
from typing import Dict, List, Optional
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import sys

# Import du gestionnaire multi-profils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.profils.gestionnaire_multi_profils import GestionnaireMultiProfils, TypeProfil


class ServeurMultiProfils:
    """
    Serveur web pour l'interface multi-profils OpenRed
    """
    
    def __init__(self, fort_id: str, port: int = 8081):
        self.fort_id = fort_id
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialise le gestionnaire de profils
        self.gestionnaire = GestionnaireMultiProfils(fort_id)
        
        # Crée les profils par défaut si nécessaire
        if not self.gestionnaire.profils:
            self.gestionnaire.creer_profils_defaut()
        
        self._configurer_routes()
    
    def _configurer_routes(self):
        """Configure toutes les routes de l'API"""
        
        @self.app.route('/')
        def index():
            """Page d'accueil de l'interface multi-profils"""
            fichier_html = os.path.join(os.path.dirname(__file__), 'interface_multi_profils.html')
            return send_file(fichier_html)
        
        @self.app.route('/api/profils', methods=['GET'])
        def lister_profils():
            """Liste tous les profils de l'utilisateur"""
            try:
                profils = []
                for profil in self.gestionnaire.lister_profils():
                    profil_data = profil.to_dict()
                    # Ajoute des infos supplémentaires
                    profil_data['actif'] = (profil.profil_id == self.gestionnaire.profil_actif)
                    
                    # Obtient les stats de l'espace
                    espace = self.gestionnaire.espaces.get(profil.profil_id)
                    if espace:
                        profil_data['connexions_p2p'] = len(espace.connexions_p2p)
                        profil_data['projections_actives'] = len(espace.projections_actives)
                        profil_data['fichiers_chiffres'] = len(espace.fichiers_chiffres)
                    else:
                        profil_data['connexions_p2p'] = 0
                        profil_data['projections_actives'] = 0
                        profil_data['fichiers_chiffres'] = 0
                    
                    profils.append(profil_data)
                
                return jsonify({
                    'success': True,
                    'profils': profils,
                    'profil_actif': self.gestionnaire.profil_actif
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'erreur': str(e)
                }), 500
        
        @self.app.route('/api/profils/<profil_id>/activer', methods=['POST'])
        def activer_profil(profil_id: str):
            """Active un profil spécifique"""
            try:
                success = self.gestionnaire.activer_profil(profil_id)
                
                if success:
                    profil = self.gestionnaire.obtenir_profil(profil_id)
                    return jsonify({
                        'success': True,
                        'profil_actif': profil_id,
                        'profil': profil.to_dict() if profil else None
                    })
                else:
                    return jsonify({
                        'success': False,
                        'erreur': 'Profil introuvable'
                    }), 404
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'erreur': str(e)
                }), 500
        
        @self.app.route('/api/profils/creer', methods=['POST'])
        def creer_profil():
            """Crée un nouveau profil"""
            try:
                data = request.get_json()
                
                # Validation des données
                if not data or 'type_profil' not in data or 'nom_affichage' not in data:
                    return jsonify({
                        'success': False,
                        'erreur': 'Données manquantes'
                    }), 400
                
                # Convertit le type
                try:
                    type_profil = TypeProfil(data['type_profil'])
                except ValueError:
                    return jsonify({
                        'success': False,
                        'erreur': 'Type de profil invalide'
                    }), 400
                
                # Crée le profil
                profil = self.gestionnaire.creer_profil(
                    type_profil=type_profil,
                    nom_affichage=data['nom_affichage'],
                    description=data.get('description', ''),
                    couleur_theme=data.get('couleur_theme', ''),
                    icone=data.get('icone', '')
                )
                
                return jsonify({
                    'success': True,
                    'profil': profil.to_dict()
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'erreur': str(e)
                }), 500
        
        @self.app.route('/api/profils/<profil_id>', methods=['GET'])
        def obtenir_profil(profil_id: str):
            """Obtient les détails d'un profil spécifique"""
            try:
                profil = self.gestionnaire.obtenir_profil(profil_id)
                
                if not profil:
                    return jsonify({
                        'success': False,
                        'erreur': 'Profil introuvable'
                    }), 404
                
                # Ajoute les données de l'espace
                espace = self.gestionnaire.espaces.get(profil_id)
                profil_data = profil.to_dict()
                
                if espace:
                    profil_data['espace'] = {
                        'dossier_donnees': espace.dossier_donnees,
                        'connexions_p2p': list(espace.connexions_p2p),
                        'projections_actives': espace.projections_actives,
                        'fichiers_chiffres': len(espace.fichiers_chiffres),
                        'historique_activites': espace.historique_activites[-10:]  # 10 dernières
                    }
                
                return jsonify({
                    'success': True,
                    'profil': profil_data
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'erreur': str(e)
                }), 500
        
        @self.app.route('/api/statistiques', methods=['GET'])
        def obtenir_statistiques():
            """Obtient les statistiques globales"""
            try:
                stats = self.gestionnaire.obtenir_statistiques()
                
                # Ajoute des métriques supplémentaires
                stats['fort_id'] = self.fort_id
                stats['serveur_port'] = self.port
                stats['chiffrement_actif'] = True
                stats['derniere_mise_a_jour'] = time.time()
                
                # Stats détaillées par profil
                stats['details_profils'] = []
                for profil in self.gestionnaire.lister_profils():
                    espace = self.gestionnaire.espaces.get(profil.profil_id)
                    stats['details_profils'].append({
                        'profil_id': profil.profil_id,
                        'type': profil.type_profil.value,
                        'nom': profil.nom_affichage,
                        'derniere_activite': profil.derniere_activite,
                        'connexions_p2p': len(espace.connexions_p2p) if espace else 0,
                        'projections': len(espace.projections_actives) if espace else 0
                    })
                
                return jsonify({
                    'success': True,
                    'statistiques': stats
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'erreur': str(e)
                }), 500
        
        @self.app.route('/api/profils/<profil_id>/connexions', methods=['GET'])
        def lister_connexions_profil(profil_id: str):
            """Liste les connexions P2P d'un profil"""
            try:
                espace = self.gestionnaire.espaces.get(profil_id)
                
                if not espace:
                    return jsonify({
                        'success': False,
                        'erreur': 'Profil introuvable'
                    }), 404
                
                return jsonify({
                    'success': True,
                    'connexions': list(espace.connexions_p2p),
                    'total': len(espace.connexions_p2p)
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'erreur': str(e)
                }), 500
        
        @self.app.route('/api/profils/<profil_id>/projections', methods=['GET'])
        def lister_projections_profil(profil_id: str):
            """Liste les projections actives d'un profil"""
            try:
                espace = self.gestionnaire.espaces.get(profil_id)
                
                if not espace:
                    return jsonify({
                        'success': False,
                        'erreur': 'Profil introuvable'
                    }), 404
                
                return jsonify({
                    'success': True,
                    'projections': espace.projections_actives,
                    'total': len(espace.projections_actives)
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'erreur': str(e)
                }), 500
        
        @self.app.route('/api/sante', methods=['GET'])
        def verifier_sante():
            """Vérifie la santé du serveur"""
            return jsonify({
                'success': True,
                'serveur': 'OpenRed Multi-Profils',
                'version': '1.0.0',
                'fort_id': self.fort_id,
                'profils_charges': len(self.gestionnaire.profils),
                'profil_actif': self.gestionnaire.profil_actif,
                'timestamp': time.time()
            })
    
    def demarrer(self, debug: bool = False):
        """Démarre le serveur web"""
        print(f"🌐 === SERVEUR MULTI-PROFILS OPENRED ===")
        print(f"🏰 Fort ID: {self.fort_id}")
        print(f"👤 Profils chargés: {len(self.gestionnaire.profils)}")
        print(f"🌍 Interface: http://localhost:{self.port}")
        print(f"🔐 Chiffrement: Activé")
        print()
        
        try:
            self.app.run(
                host='0.0.0.0',
                port=self.port,
                debug=debug,
                threaded=True
            )
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur multi-profils")
        except Exception as e:
            print(f"❌ Erreur serveur: {e}")


def demo_serveur_multi_profils():
    """Démonstration du serveur multi-profils"""
    print("🎭 === DÉMONSTRATION SERVEUR MULTI-PROFILS ===")
    
    # Utilise le fort existant ou crée un demo
    fort_id = "fort_d8734d527171c583"  # ID du fort créé précédemment
    
    # Vérifie si le fort existe
    if not os.path.exists(".openred_fort"):
        print("⚠️  Aucun fort détecté - création fort demo")
        fort_id = "fort_demo_profils"
    
    # Démarre le serveur
    serveur = ServeurMultiProfils(fort_id, port=8081)
    
    print("🚀 Démarrage du serveur...")
    print()
    print("📋 ROUTES DISPONIBLES:")
    print("   🏠 Interface:          http://localhost:8081/")
    print("   📋 API Profils:        http://localhost:8081/api/profils")
    print("   📊 Statistiques:       http://localhost:8081/api/statistiques")
    print("   ❤️  Santé:             http://localhost:8081/api/sante")
    print()
    print("💡 Utilisez Ctrl+C pour arrêter le serveur")
    print("="*60)
    
    serveur.demarrer(debug=False)


if __name__ == "__main__":
    demo_serveur_multi_profils()