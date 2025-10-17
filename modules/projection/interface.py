#!/usr/bin/env python3
"""
🪟 OpenRed Network - Module Projection: Interface Sécurisée
Interface utilisateur pour afficher projections non-copiables
"""

import tkinter as tk
from tkinter import ttk
import time
import threading
from typing import Dict, List, Optional, Callable

from .format_orn import FormatProjectionORN
from .protection import MoteurAntiCopie


class FenetreProjectionSecurisee:
    """
    🪟 Fenêtre de projection sécurisée
    Interface utilisateur pour afficher projections non-copiables
    """
    
    def __init__(self, moteur_anti_copie: MoteurAntiCopie):
        self.moteur = moteur_anti_copie
        self.fenetre = None
        self.projection_active = None
        self.session_id = None
        self.thread_surveillance = None
        self.widgets_proteges = {}
        
        # Protection contre captures
        self.watermarks_actifs = []
        self.derniere_validation = 0
        self.tentatives_capture = 0
        
        # Callbacks pour événements
        self.callbacks = {
            "fermeture": [],
            "tentative_copie": [],
            "expiration": []
        }
    
    def ajouter_callback(self, evenement: str, callback: Callable):
        """Ajoute un callback pour un événement"""
        if evenement in self.callbacks:
            self.callbacks[evenement].append(callback)
    
    def _notifier_callback(self, evenement: str, *args):
        """Notifie les callbacks d'un événement"""
        for callback in self.callbacks.get(evenement, []):
            try:
                callback(*args)
            except Exception as e:
                print(f"❌ Erreur callback {evenement}: {e}")
    
    def afficher_projection(self, id_projection: str, fort_demandeur: str, session_id: str = None):
        """Affiche une projection dans une fenêtre sécurisée"""
        
        # Accès sécurisé à la projection
        resultat = self.moteur.acceder_projection_securisee(id_projection, fort_demandeur, session_id)
        
        if not resultat:
            print("🚫 Impossible d'afficher la projection")
            return False
        
        self.projection_active = resultat["projection"]
        self.session_id = resultat["session_id"]
        contenu = resultat["contenu"]
        
        # Création fenêtre sécurisée
        self._creer_fenetre_securisee(contenu)
        
        # Démarrage surveillance anti-copie
        self._demarrer_surveillance()
        
        print(f"🪟 Projection affichée: {id_projection}")
        return True
    
    def _creer_fenetre_securisee(self, contenu: Dict):
        """Crée la fenêtre d'affichage sécurisée"""
        
        self.fenetre = tk.Toplevel()
        self.fenetre.title("🔮 Projection OpenRed Network - PROTÉGÉE")
        self.fenetre.geometry("800x600")
        
        # Configuration sécurité fenêtre
        self.fenetre.attributes('-topmost', True)  # Toujours au-dessus
        self.fenetre.protocol("WM_DELETE_WINDOW", self._fermeture_securisee)
        
        # Désactiver menu contextuel
        self.fenetre.bind("<Button-3>", lambda e: self._detecter_tentative_selection(e))
        self.fenetre.bind("<Control-c>", lambda e: self._detecter_tentative_copie(e))
        self.fenetre.bind("<Control-a>", lambda e: self._detecter_tentative_copie(e))
        self.fenetre.bind("<Control-s>", lambda e: self._detecter_tentative_copie(e))
        
        # Style sécurisé
        style = ttk.Style()
        style.configure("Secure.TFrame", background="#0a0a0a")
        
        # Frame principal
        main_frame = ttk.Frame(self.fenetre, style="Secure.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header de sécurité
        self._creer_header_securite(main_frame)
        
        # Zone de contenu avec protection
        self._afficher_contenu_protege(main_frame, contenu)
        
        # Footer de sécurité
        self._creer_footer_securite(main_frame)
        
        # Focus sur fenêtre pour capturer événements clavier
        self.fenetre.focus_set()
    
    def _creer_header_securite(self, parent: ttk.Frame):
        """Crée le header avec informations de sécurité"""
        
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="🔮 PROJECTION SÉCURISÉE OPENRED", 
                 font=("Arial", 16, "bold"), foreground="#00ff00").pack()
        
        ttk.Label(header_frame, text=f"Fort: {self.projection_active.fort_proprietaire}", 
                 font=("Arial", 10), foreground="#888888").pack()
        
        ttk.Label(header_frame, text="⚠️ CONTENU PROTÉGÉ - COPIE IMPOSSIBLE", 
                 font=("Arial", 10, "bold"), foreground="#ff0000").pack()
        
        # Niveau de protection
        niveau = self.projection_active.protection_niveau
        etoiles = "★" * niveau + "☆" * (5 - niveau)
        ttk.Label(header_frame, text=f"🔒 Protection: {etoiles} (Niveau {niveau})", 
                 font=("Arial", 9), foreground="#ffaa00").pack()
    
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
        
        # Binding pour détecter tentatives de sélection/copie
        self.canvas.bind("<Button-1>", self._detecter_tentative_selection)
        self.canvas.bind("<B1-Motion>", self._detecter_tentative_selection)
        self.canvas.bind("<Double-Button-1>", self._detecter_tentative_selection)
        
        # Désactiver sélection de texte
        self.canvas.bind("<Button-1>", lambda e: "break", add="+")
    
    def _dessiner_contenu_avec_watermarks(self, contenu: Dict):
        """Dessine le contenu avec watermarks intégrés"""
        
        # Effacement canvas
        self.canvas.delete("all")
        
        # Dimensions canvas
        width = self.canvas.winfo_width() or 800
        height = self.canvas.winfo_height() or 400
        
        # Watermarks de fond
        self._dessiner_watermarks_fond(width, height)
        
        # Contenu principal
        y_position = 50
        
        if "donnees" in contenu and "publications" in contenu["donnees"]:
            for pub in contenu["donnees"]["publications"]:
                # Texte de la publication avec protection
                text = pub.get("contenu", "")
                timestamp = pub.get("timestamp", "")
                
                self._dessiner_texte_protege(text, 50, y_position, width-100)
                self._dessiner_texte_protege(f"📅 {timestamp}", 50, y_position + 25, width-100, 
                                           couleur="#888888", taille=8)
                
                y_position += 80
        else:
            # Affichage générique du contenu
            for key, value in contenu.items():
                if isinstance(value, str):
                    self._dessiner_texte_protege(f"{key}: {value}", 50, y_position, width-100)
                    y_position += 30
        
        # Watermarks dynamiques par-dessus
        self._dessiner_watermarks_dynamiques(width, height)
    
    def _dessiner_watermarks_fond(self, width: int, height: int):
        """Dessine watermarks de fond semi-transparents"""
        
        # Watermarks du moteur anti-copie
        watermarks_moteur = self.moteur.obtenir_watermarks_projection(self.projection_active.id_projection)
        
        # Watermarks de base
        watermarks_base = [
            f"ORN-{self.projection_active.id_projection[:8]}",
            f"SECURE-{int(time.time()) % 10000}",
            f"PROTECT-{self.projection_active.fort_observateur[:8]}"
        ]
        
        tous_watermarks = watermarks_moteur + watermarks_base
        
        # Affichage en grille
        for i in range(0, width, 200):
            for j in range(0, height, 150):
                if tous_watermarks:
                    watermark = tous_watermarks[(i + j) % len(tous_watermarks)]
                    self.canvas.create_text(i + 100, j + 75, text=watermark, fill="#333333", 
                                          font=("Arial", 10), angle=45, anchor="center")
    
    def _dessiner_watermarks_dynamiques(self, width: int, height: int):
        """Dessine watermarks dynamiques qui changent"""
        
        # Watermark principal mobile basé sur le temps
        timestamp = int(time.time()) % 10
        x = 100 + timestamp * 60
        y = 100 + timestamp * 30
        
        watermark_principal = f"🔮 PROTÉGÉ-{self.projection_active.fort_observateur[:8]}"
        self.canvas.create_text(x, y, text=watermark_principal, fill="#ff0000", 
                              font=("Arial", 14, "bold"), angle=timestamp * 36)
        
        # Watermarks aux coins
        coins = [(50, 50), (width-50, 50), (50, height-50), (width-50, height-50)]
        for i, (cx, cy) in enumerate(coins):
            watermark_coin = f"ORN-{(timestamp + i) % 1000:03d}"
            self.canvas.create_text(cx, cy, text=watermark_coin, fill="#660000", 
                                  font=("Arial", 8), angle=i * 90)
    
    def _dessiner_texte_protege(self, texte: str, x: int, y: int, max_width: int, 
                               couleur: str = "#00ff00", taille: int = 12):
        """Dessine du texte avec protection intégrée"""
        
        # Texte principal
        self.canvas.create_text(x, y, text=texte, fill=couleur, anchor="w",
                              font=("Arial", taille), width=max_width)
        
        # Micro-watermarks dans le texte (tous les 10 caractères)
        for i in range(0, len(texte), 10):
            micro_x = x + i * 6
            micro_watermark = "•"
            self.canvas.create_text(micro_x, y - 3, text=micro_watermark, 
                                  fill="#440000", font=("Arial", 4))
    
    def _creer_footer_securite(self, parent: ttk.Frame):
        """Crée le footer avec informations de sécurité"""
        
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Separator(footer_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 5))
        
        # Statut de sécurité
        self.label_statut = ttk.Label(footer_frame, text="🛡️ Protection active", 
                                     foreground="#00ff00", font=("Arial", 10))
        self.label_statut.pack(side=tk.LEFT)
        
        # Compteur tentatives
        self.label_tentatives = ttk.Label(footer_frame, text="Tentatives: 0", 
                                        foreground="#ffaa00", font=("Arial", 9))
        self.label_tentatives.pack(side=tk.LEFT, padx=(20, 0))
        
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
        
        # Mise à jour affichage
        if hasattr(self, 'label_tentatives'):
            self.label_tentatives.config(text=f"Tentatives: {self.tentatives_capture}")
        
        # Notification au moteur anti-copie
        self.moteur.detecter_tentative_copie(self.projection_active.id_projection, "selection")
        
        # Callback
        self._notifier_callback("tentative_copie", "selection")
        
        print(f"🚨 Tentative de sélection détectée ({self.tentatives_capture})")
        
        # Protection progressive
        if self.tentatives_capture > 10:
            self._declencher_protection_avancee("Trop de tentatives de sélection")
        
        return "break"  # Bloque l'événement
    
    def _detecter_tentative_copie(self, event):
        """Détecte tentatives de copie (Ctrl+C, Ctrl+A, etc.)"""
        
        type_tentative = "copie"
        if event.keysym == "a":
            type_tentative = "selection_tout"
        elif event.keysym == "s":
            type_tentative = "sauvegarde"
        
        print(f"🚨 ALERTE: Tentative de {type_tentative} détectée!")
        
        # Notification au moteur anti-copie
        self.moteur.detecter_tentative_copie(self.projection_active.id_projection, type_tentative)
        
        # Callback
        self._notifier_callback("tentative_copie", type_tentative)
        
        # Protection immédiate pour les tentatives de copie
        self._declencher_protection_avancee(f"Tentative de {type_tentative}")
        
        return "break"  # Bloque l'événement
    
    def _declencher_protection_avancee(self, raison: str):
        """Déclenche protections avancées en cas de tentative de copie"""
        
        # Effacement du contenu
        if hasattr(self, 'canvas'):
            self.canvas.delete("all")
            self.canvas.create_text(400, 300, text=f"🚨 PROTECTION ACTIVÉE\n\n"
                                                  f"Raison: {raison}\n\n"
                                                  f"ACCÈS RÉVOQUÉ", 
                                  fill="#ff0000", font=("Arial", 20, "bold"), justify=tk.CENTER)
        
        # Mise à jour statut
        if hasattr(self, 'label_statut'):
            self.label_statut.config(text="🚨 PROTECTION DÉCLENCHÉE", foreground="#ff0000")
        
        # Programmer fermeture automatique
        if self.fenetre:
            self.fenetre.after(3000, self._fermeture_securisee)
    
    def _demarrer_surveillance(self):
        """Démarre la surveillance anti-copie en arrière-plan"""
        
        def surveiller():
            while (self.projection_active and self.fenetre and 
                   hasattr(self.fenetre, 'winfo_exists') and 
                   self.fenetre.winfo_exists()):
                try:
                    # Vérification expiration
                    if self.projection_active.est_expire():
                        print("⏰ Projection expirée")
                        self._notifier_callback("expiration")
                        self.fenetre.after(0, self._fermeture_securisee)
                        break
                    
                    # Mise à jour timer
                    temps_restant = int(self.projection_active.temps_restant())
                    if hasattr(self, 'label_timer'):
                        self.fenetre.after(0, lambda: self.label_timer.config(
                            text=f"⏰ Expire dans {temps_restant}s"))
                    
                    # Redessiner watermarks dynamiques
                    if hasattr(self, 'canvas') and self.canvas.winfo_exists():
                        width = self.canvas.winfo_width()
                        height = self.canvas.winfo_height()
                        if width > 1 and height > 1:  # Canvas initialisé
                            self.fenetre.after(0, lambda: self._dessiner_watermarks_dynamiques(width, height))
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Erreur surveillance: {e}")
                    break
        
        self.thread_surveillance = threading.Thread(target=surveiller, daemon=True)
        self.thread_surveillance.start()
    
    def _fermeture_securisee(self):
        """Fermeture sécurisée de la projection"""
        
        if self.projection_active:
            print(f"🔒 Fermeture sécurisée: {self.projection_active.id_projection}")
            
            # Callback de fermeture
            self._notifier_callback("fermeture", self.projection_active.id_projection)
        
        # Nettoyage sécurisé des variables sensibles
        self.projection_active = None
        self.session_id = None
        self.watermarks_actifs.clear()
        
        # Fermeture fenêtre
        if self.fenetre:
            self.fenetre.destroy()
            self.fenetre = None
    
    def forcer_fermeture(self):
        """Force la fermeture de la projection"""
        if self.fenetre:
            self._fermeture_securisee()
    
    def est_active(self) -> bool:
        """Vérifie si la fenêtre de projection est active"""
        return (self.fenetre is not None and 
                hasattr(self.fenetre, 'winfo_exists') and 
                self.fenetre.winfo_exists())