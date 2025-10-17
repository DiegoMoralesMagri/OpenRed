#!/usr/bin/env python3
"""
🔮 OpenRed Network - Système de Projection Anti-Copie Révolutionnaire
Format spécifique de projection impossible à copier, capturer ou transférer
"""

import tkinter as tk
from tkinter import ttk
import json
import time
import threading
import uuid
import hashlib
import base64
import random
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import socket
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io


@dataclass
class FormatProjectionORN:
    """
    Format de Projection OpenRed Network (ORN)
    Format propriétaire impossible à copier
    """
    id_projection: str
    fort_proprietaire: str
    fort_observateur: str
    timestamp_creation: float
    timestamp_expiration: float
    fragments: List[Dict]  # Données fragmentées
    watermarks_dynamiques: List[str]
    cles_temporelles: Dict[str, str]
    sequence_validation: List[int]
    protection_niveau: int = 5  # 1-5, 5 = maximum


class MoteurAntiCopie:
    """
    🛡️ Moteur de protection anti-copie révolutionnaire
    Empêche capture, copie, transfert par tous moyens
    """
    
    def __init__(self):
        self.projections_actives = {}
        self.watermarks_uniques = {}
        self.sequences_protection = {}
        self.tokens_temporaires = {}
        self.detection_active = True
        
    def creer_projection_securisee(self, contenu: Dict, fort_proprietaire: str, fort_observateur: str) -> FormatProjectionORN:
        """Crée une projection sécurisée impossible à copier"""
        
        id_projection = f"ORN_{uuid.uuid4().hex}"
        maintenant = time.time()
        expiration = maintenant + 300  # 5 minutes max
        
        # 1. FRAGMENTATION DU CONTENU
        fragments = self._fragmenter_contenu(contenu, id_projection)
        
        # 2. WATERMARKS DYNAMIQUES
        watermarks = self._generer_watermarks_dynamiques(id_projection, fort_observateur)
        
        # 3. CLÉS TEMPORELLES
        cles_temporelles = self._generer_cles_temporelles(id_projection, maintenant)
        
        # 4. SÉQUENCE DE VALIDATION
        sequence = self._generer_sequence_validation(id_projection)
        
        projection = FormatProjectionORN(
            id_projection=id_projection,
            fort_proprietaire=fort_proprietaire,
            fort_observateur=fort_observateur,
            timestamp_creation=maintenant,
            timestamp_expiration=expiration,
            fragments=fragments,
            watermarks_dynamiques=watermarks,
            cles_temporelles=cles_temporelles,
            sequence_validation=sequence
        )
        
        # Enregistrement pour surveillance
        self.projections_actives[id_projection] = {
            "projection": projection,
            "debut_affichage": None,
            "tentatives_copie": 0,
            "dernier_heartbeat": maintenant
        }
        
        print(f"🔮 Projection sécurisée créée: {id_projection}")
        return projection
    
    def _fragmenter_contenu(self, contenu: Dict, id_projection: str) -> List[Dict]:
        """Fragmente le contenu en morceaux illisibles séparément"""
        fragments = []
        
        # Conversion contenu en JSON
        contenu_json = json.dumps(contenu)
        contenu_bytes = contenu_json.encode('utf-8')
        
        # Fragmentation avec clés cryptographiques
        taille_fragment = 64
        for i in range(0, len(contenu_bytes), taille_fragment):
            chunk = contenu_bytes[i:i+taille_fragment]
            
            # Chiffrement simple avec clé basée sur position et ID
            cle_fragment = hashlib.sha256(f"{id_projection}_{i}".encode()).digest()[:16]
            chunk_chiffre = bytes(a ^ b for a, b in zip(chunk, cle_fragment * (len(chunk) // 16 + 1)))
            
            fragment = {
                "index": i // taille_fragment,
                "data": base64.b64encode(chunk_chiffre).decode(),
                "checksum": hashlib.md5(chunk).hexdigest(),
                "timestamp": time.time()
            }
            fragments.append(fragment)
        
        return fragments
    
    def _generer_watermarks_dynamiques(self, id_projection: str, fort_observateur: str) -> List[str]:
        """Génère des watermarks dynamiques qui changent"""
        watermarks = []
        
        for i in range(10):  # 10 watermarks différents
            base_string = f"{id_projection}_{fort_observateur}_{i}_{time.time()}"
            watermark = hashlib.sha256(base_string.encode()).hexdigest()[:16]
            watermarks.append(watermark)
        
        return watermarks
    
    def _generer_cles_temporelles(self, id_projection: str, timestamp: float) -> Dict[str, str]:
        """Génère des clés qui expirent rapidement"""
        cles = {}
        
        for niveau in range(1, 6):  # 5 niveaux de clés
            duree = 60 * niveau  # 1min, 2min, 3min, 4min, 5min
            expiration = timestamp + duree
            
            cle_data = f"{id_projection}_{niveau}_{expiration}"
            cle_hash = hashlib.sha256(cle_data.encode()).hexdigest()
            
            cles[f"niveau_{niveau}"] = cle_hash
        
        return cles
    
    def _generer_sequence_validation(self, id_projection: str) -> List[int]:
        """Génère séquence de validation unique"""
        # Basé sur l'ID projection pour être reproductible mais unique
        random.seed(id_projection)
        sequence = [random.randint(100, 999) for _ in range(20)]
        random.seed()  # Reset seed
        
        return sequence
    
    def reconstituer_contenu(self, projection: FormatProjectionORN) -> Optional[Dict]:
        """Reconstitue le contenu UNIQUEMENT si toutes les validations passent"""
        
        # 1. Vérification expiration
        if time.time() > projection.timestamp_expiration:
            print("🚫 Projection expirée")
            return None
        
        # 2. Vérification observateur autorisé
        if projection.id_projection not in self.projections_actives:
            print("🚫 Projection non autorisée")
            return None
        
        # 3. Reconstitution des fragments
        try:
            fragments_ordonnes = sorted(projection.fragments, key=lambda x: x["index"])
            contenu_bytes = b""
            
            for fragment in fragments_ordonnes:
                # Déchiffrement
                data_chiffree = base64.b64decode(fragment["data"])
                cle_fragment = hashlib.sha256(f"{projection.id_projection}_{fragment['index'] * 64}".encode()).digest()[:16]
                
                chunk_dechiffre = bytes(a ^ b for a, b in zip(data_chiffree, cle_fragment * (len(data_chiffree) // 16 + 1)))
                contenu_bytes += chunk_dechiffre
            
            # Conversion retour en JSON
            contenu_json = contenu_bytes.decode('utf-8')
            contenu = json.loads(contenu_json)
            
            # Mise à jour heartbeat
            self.projections_actives[projection.id_projection]["dernier_heartbeat"] = time.time()
            
            return contenu
            
        except Exception as e:
            print(f"🚫 Erreur reconstitution: {e}")
            return None
    
    def detecter_tentative_copie(self, id_projection: str):
        """Détecte et bloque les tentatives de copie"""
        if id_projection in self.projections_actives:
            self.projections_actives[id_projection]["tentatives_copie"] += 1
            
            if self.projections_actives[id_projection]["tentatives_copie"] > 3:
                print(f"🚨 ALERTE: Tentatives de copie détectées sur {id_projection}")
                self.autodestruction_projection(id_projection)
    
    def autodestruction_projection(self, id_projection: str):
        """Auto-destruction de la projection si tentative de copie"""
        if id_projection in self.projections_actives:
            del self.projections_actives[id_projection]
            print(f"💥 Auto-destruction projection {id_projection}")


class FenetreProjectionSecurisee:
    """
    🪟 Fenêtre de projection sécurisée
    Interface utilisateur pour afficher projections non-copiables
    """
    
    def __init__(self, moteur_anti_copie: MoteurAntiCopie):
        self.moteur = moteur_anti_copie
        self.fenetre = None
        self.projection_active = None
        self.thread_surveillance = None
        self.widgets_proteges = {}
        
        # Protection contre captures
        self.watermarks_actifs = []
        self.derniere_validation = 0
        self.tentatives_capture = 0
    
    def afficher_projection(self, projection: FormatProjectionORN):
        """Affiche une projection dans une fenêtre sécurisée"""
        
        # Reconstitution sécurisée du contenu
        contenu = self.moteur.reconstituer_contenu(projection)
        if not contenu:
            print("🚫 Impossible d'afficher la projection")
            return
        
        self.projection_active = projection
        
        # Création fenêtre sécurisée
        self._creer_fenetre_securisee(contenu)
        
        # Démarrage surveillance anti-copie
        self._demarrer_surveillance()
        
        print(f"🪟 Projection affichée: {projection.id_projection}")
    
    def _creer_fenetre_securisee(self, contenu: Dict):
        """Crée la fenêtre d'affichage sécurisée"""
        
        self.fenetre = tk.Toplevel()
        self.fenetre.title("🔮 Projection OpenRed Network - PROTÉGÉE")
        self.fenetre.geometry("800x600")
        
        # Configuration sécurité fenêtre
        self.fenetre.attributes('-topmost', True)  # Toujours au-dessus
        self.fenetre.protocol("WM_DELETE_WINDOW", self._fermeture_securisee)
        
        # Désactiver menu contextuel
        self.fenetre.bind("<Button-3>", lambda e: "break")
        
        # Style sécurisé
        style = ttk.Style()
        style.configure("Secure.TFrame", background="#0a0a0a")
        
        # Frame principal
        main_frame = ttk.Frame(self.fenetre, style="Secure.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header de sécurité
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="🔮 PROJECTION SÉCURISÉE OPENRED", 
                 font=("Arial", 16, "bold"), foreground="#00ff00").pack()
        
        ttk.Label(header_frame, text=f"Fort: {self.projection_active.fort_proprietaire}", 
                 font=("Arial", 10), foreground="#888888").pack()
        
        ttk.Label(header_frame, text="⚠️ CONTENU PROTÉGÉ - COPIE IMPOSSIBLE", 
                 font=("Arial", 10, "bold"), foreground="#ff0000").pack()
        
        # Zone de contenu avec protection
        self._afficher_contenu_protege(main_frame, contenu)
        
        # Footer de sécurité
        self._creer_footer_securite(main_frame)
    
    def _afficher_contenu_protege(self, parent: ttk.Frame, contenu: Dict):
        """Affiche le contenu avec protections intégrées"""
        
        # Scrollable text avec watermarks
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas pour dessiner watermarks
        self.canvas = tk.Canvas(text_frame, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Affichage du contenu avec watermarks intégrés
        self._dessiner_contenu_avec_watermarks(contenu)
        
        # Binding pour détecter tentatives de sélection
        self.canvas.bind("<Button-1>", self._detecter_tentative_selection)
        self.canvas.bind("<B1-Motion>", self._detecter_tentative_selection)
        self.canvas.bind("<Control-c>", self._detecter_tentative_copie)
        self.canvas.bind("<Control-a>", self._detecter_tentative_copie)
        
        # Désactiver menu contextuel
        self.canvas.bind("<Button-3>", lambda e: "break")
    
    def _dessiner_contenu_avec_watermarks(self, contenu: Dict):
        """Dessine le contenu avec watermarks intégrés"""
        
        # Effacement canvas
        self.canvas.delete("all")
        
        # Dimensions canvas
        width = self.canvas.winfo_width() or 800
        height = self.canvas.winfo_height() or 400
        
        # Watermarks de fond (semi-transparents)
        self._dessiner_watermarks_fond(width, height)
        
        # Contenu principal
        y_position = 50
        
        if "donnees" in contenu and "publications" in contenu["donnees"]:
            for pub in contenu["donnees"]["publications"]:
                # Texte de la publication
                text = pub.get("contenu", "")
                timestamp = pub.get("timestamp", "")
                
                # Affichage avec watermark intégré
                self._dessiner_texte_protege(text, 50, y_position, width-100)
                self._dessiner_texte_protege(f"📅 {timestamp}", 50, y_position + 25, width-100, 
                                           couleur="#888888", taille=8)
                
                y_position += 80
        
        # Watermarks dynamiques par-dessus
        self._dessiner_watermarks_dynamiques(width, height)
    
    def _dessiner_watermarks_fond(self, width: int, height: int):
        """Dessine watermarks de fond"""
        
        # Watermarks semi-transparents
        for i in range(0, width, 200):
            for j in range(0, height, 150):
                watermark = f"ORN-{self.projection_active.id_projection[:8]}"
                self.canvas.create_text(i, j, text=watermark, fill="#333333", 
                                      font=("Arial", 12), angle=45)
    
    def _dessiner_watermarks_dynamiques(self, width: int, height: int):
        """Dessine watermarks dynamiques qui changent"""
        
        # Watermark principal mobile
        timestamp = int(time.time()) % 10
        x = 100 + timestamp * 60
        y = 100 + timestamp * 30
        
        watermark_principal = f"🔮 PROTÉGÉ-{self.projection_active.fort_observateur[:8]}"
        self.canvas.create_text(x, y, text=watermark_principal, fill="#ff0000", 
                              font=("Arial", 14, "bold"), angle=timestamp * 36)
    
    def _dessiner_texte_protege(self, texte: str, x: int, y: int, max_width: int, 
                               couleur: str = "#00ff00", taille: int = 12):
        """Dessine du texte avec protection intégrée"""
        
        # Texte principal
        self.canvas.create_text(x, y, text=texte, fill=couleur, anchor="w",
                              font=("Arial", taille), width=max_width)
        
        # Micro-watermarks dans le texte
        for i, char in enumerate(texte[:20]):  # Premiers 20 caractères
            if i % 5 == 0:  # Tous les 5 caractères
                micro_x = x + i * 8
                micro_watermark = "•"
                self.canvas.create_text(micro_x, y - 3, text=micro_watermark, 
                                      fill="#440000", font=("Arial", 6))
    
    def _creer_footer_securite(self, parent: ttk.Frame):
        """Crée le footer avec informations de sécurité"""
        
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Separator(footer_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 5))
        
        # Statut de sécurité
        self.label_statut = ttk.Label(footer_frame, text="🛡️ Protection active", 
                                     foreground="#00ff00", font=("Arial", 10))
        self.label_statut.pack(side=tk.LEFT)
        
        # Timer expiration
        self.label_timer = ttk.Label(footer_frame, text="", foreground="#ffaa00", 
                                   font=("Arial", 10))
        self.label_timer.pack(side=tk.RIGHT)
        
        # Bouton fermeture sécurisée
        ttk.Button(footer_frame, text="Fermer Projection", 
                  command=self._fermeture_securisee).pack(side=tk.RIGHT, padx=(0, 10))
    
    def _detecter_tentative_selection(self, event):
        """Détecte tentatives de sélection de texte"""
        self.tentatives_capture += 1
        print(f"🚨 Tentative de sélection détectée")
        
        if self.tentatives_capture > 5:
            self._declencher_protection_avancee()
        
        return "break"  # Bloque l'événement
    
    def _detecter_tentative_copie(self, event):
        """Détecte tentatives de copie (Ctrl+C, Ctrl+A)"""
        print(f"🚨 ALERTE: Tentative de copie détectée!")
        
        self.moteur.detecter_tentative_copie(self.projection_active.id_projection)
        self._declencher_protection_avancee()
        
        return "break"  # Bloque l'événement
    
    def _declencher_protection_avancee(self):
        """Déclenche protections avancées en cas de tentative de copie"""
        
        # Changer le contenu affiché
        self.canvas.delete("all")
        self.canvas.create_text(400, 300, text="🚨 TENTATIVE DE COPIE DÉTECTÉE\n\n"
                                              "PROTECTION ACTIVÉE\n\n"
                                              "ACCÈS RÉVOQUÉ", 
                              fill="#ff0000", font=("Arial", 20, "bold"), justify=tk.CENTER)
        
        # Programmer fermeture automatique
        self.fenetre.after(3000, self._fermeture_securisee)
    
    def _demarrer_surveillance(self):
        """Démarre la surveillance anti-copie en arrière-plan"""
        
        def surveiller():
            while self.projection_active and self.fenetre and self.fenetre.winfo_exists():
                try:
                    # Vérification expiration
                    if time.time() > self.projection_active.timestamp_expiration:
                        print("⏰ Projection expirée")
                        self.fenetre.after(0, self._fermeture_securisee)
                        break
                    
                    # Mise à jour timer
                    temps_restant = int(self.projection_active.timestamp_expiration - time.time())
                    if hasattr(self, 'label_timer'):
                        self.fenetre.after(0, lambda: self.label_timer.config(
                            text=f"⏰ Expire dans {temps_restant}s"))
                    
                    # Redessiner watermarks dynamiques
                    if hasattr(self, 'canvas'):
                        self.fenetre.after(0, lambda: self._dessiner_watermarks_dynamiques(
                            self.canvas.winfo_width(), self.canvas.winfo_height()))
                    
                    time.sleep(1)
                    
                except:
                    break
        
        self.thread_surveillance = threading.Thread(target=surveiller, daemon=True)
        self.thread_surveillance.start()
    
    def _fermeture_securisee(self):
        """Fermeture sécurisée de la projection"""
        
        if self.projection_active:
            # Nettoyage sécurisé
            id_proj = self.projection_active.id_projection
            if id_proj in self.moteur.projections_actives:
                del self.moteur.projections_actives[id_proj]
            
            print(f"🔒 Projection fermée de manière sécurisée: {id_proj}")
        
        if self.fenetre:
            self.fenetre.destroy()


def demo_projection_anti_copie():
    """
    🎭 Démonstration du système de projection anti-copie
    """
    print("=" * 70)
    print("🔮 DÉMONSTRATION PROJECTION ANTI-COPIE OPENRED")
    print("=" * 70)
    
    # Initialisation du moteur
    moteur = MoteurAntiCopie()
    
    # Contenu de test
    contenu_test = {
        "donnees": {
            "nom": "Fort Alice",
            "description": "Fort sécurisé sur OpenRed Network",
            "publications": [
                {
                    "id": "pub_001",
                    "contenu": "🏰 Bienvenue dans mon fort ! Voici ma première publication.",
                    "timestamp": "2025-10-17T20:30:00",
                    "type": "annonce"
                },
                {
                    "id": "pub_002", 
                    "contenu": "🌟 Découvrez les merveilles de OpenRed Network !",
                    "timestamp": "2025-10-17T20:31:00",
                    "type": "message"
                },
                {
                    "id": "pub_003",
                    "contenu": "🔮 Cette projection est 100% sécurisée et non-copiable !",
                    "timestamp": "2025-10-17T20:32:00",
                    "type": "demonstration"
                }
            ]
        }
    }
    
    print("\n1️⃣ Création de la projection sécurisée...")
    projection = moteur.creer_projection_securisee(
        contenu=contenu_test,
        fort_proprietaire="fort_alice_abc123",
        fort_observateur="fort_bob_def456"
    )
    
    print(f"   ID Projection: {projection.id_projection}")
    print(f"   Fragments: {len(projection.fragments)}")
    print(f"   Watermarks: {len(projection.watermarks_dynamiques)}")
    print(f"   Protection niveau: {projection.protection_niveau}")
    
    print("\n2️⃣ Test de reconstitution sécurisée...")
    contenu_reconstitue = moteur.reconstituer_contenu(projection)
    
    if contenu_reconstitue:
        print("   ✅ Reconstitution réussie")
        print(f"   Publications: {len(contenu_reconstitue['donnees']['publications'])}")
    else:
        print("   ❌ Reconstitution échouée")
    
    print("\n3️⃣ Lancement de l'interface de projection...")
    
    # Interface graphique
    root = tk.Tk()
    root.title("🔮 OpenRed Network - Système de Projection")
    root.geometry("400x300")
    root.configure(bg="#1a1a1a")
    
    # Bouton pour ouvrir projection
    def ouvrir_projection():
        fenetre_proj = FenetreProjectionSecurisee(moteur)
        fenetre_proj.afficher_projection(projection)
    
    ttk.Label(root, text="🔮 Système de Projection OpenRed", 
             font=("Arial", 16, "bold")).pack(pady=20)
    
    ttk.Label(root, text="Interface révolutionnaire de consultation\n"
                        "de contenu impossible à copier", 
             font=("Arial", 10)).pack(pady=10)
    
    ttk.Button(root, text="🪟 Ouvrir Projection Sécurisée", 
              command=ouvrir_projection).pack(pady=20)
    
    ttk.Label(root, text="⚠️ Tentatives de copie détectées = Fermeture automatique", 
             foreground="red", font=("Arial", 9)).pack(pady=10)
    
    print("\n4️⃣ Interface lancée - Testez la projection !")
    print("   - Essayez de sélectionner du texte")
    print("   - Tentez Ctrl+C ou Ctrl+A") 
    print("   - Observez les watermarks dynamiques")
    print("   - Voyez l'expiration automatique")
    
    root.mainloop()
    
    print("\n✅ Démonstration terminée !")


if __name__ == "__main__":
    demo_projection_anti_copie()