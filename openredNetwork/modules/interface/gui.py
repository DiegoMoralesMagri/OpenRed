#!/usr/bin/env python3
"""
🖥️ OpenRed Network - Module Interface: Interface Graphique
Interface utilisateur Tkinter pour OpenRed Network
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from typing import Dict, List, Optional, Callable, Any


class InterfacePrincipale:
    """
    🖥️ Interface principale OpenRed Network
    Interface utilisateur complète pour gérer un fort
    """
    
    def __init__(self, titre: str = "OpenRed Network"):
        self.titre = titre
        self.root = None
        self.fort = None
        self.callbacks = {}
        
        # Widgets principaux
        self.widgets = {}
        self.threads_actifs = []
        
        # État de l'interface
        self.interface_active = False
        
    def initialiser(self, fort=None):
        """Initialise l'interface graphique"""
        self.fort = fort
        
        # Création fenêtre principale
        self.root = tk.Tk()
        self.root.title(self.titre)
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self._fermeture_interface)
        
        # Configuration style
        self._configurer_styles()
        
        # Création interface
        self._creer_interface()
        
        # Démarrage mises à jour
        self._demarrer_mises_a_jour()
        
        self.interface_active = True
        print(f"🖥️ Interface initialisée: {self.titre}")
    
    def _configurer_styles(self):
        """Configure les styles de l'interface"""
        style = ttk.Style()
        
        # Styles personnalisés
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        style.configure("Info.TLabel", font=("Arial", 10))
        style.configure("Status.TLabel", font=("Arial", 9))
    
    def _creer_interface(self):
        """Crée l'interface utilisateur complète"""
        
        # Menu principal
        self._creer_menu()
        
        # Notebook avec onglets
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet Fort
        self._creer_onglet_fort(notebook)
        
        # Onglet Réseau
        self._creer_onglet_reseau(notebook)
        
        # Onglet Projections
        self._creer_onglet_projections(notebook)
        
        # Onglet Logs
        self._creer_onglet_logs(notebook)
        
        # Barre de statut
        self._creer_barre_statut()
    
    def _creer_menu(self):
        """Crée le menu principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fort
        menu_fort = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fort", menu=menu_fort)
        menu_fort.add_command(label="Activer Fort", command=self._activer_fort)
        menu_fort.add_command(label="Désactiver Fort", command=self._desactiver_fort)
        menu_fort.add_separator()
        menu_fort.add_command(label="Statistiques", command=self._afficher_statistiques)
        
        # Menu Réseau
        menu_reseau = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Réseau", menu=menu_reseau)
        menu_reseau.add_command(label="Découvrir Forts", command=self._forcer_decouverte)
        menu_reseau.add_command(label="Carte Réseau", command=self._afficher_carte)
        
        # Menu Aide
        menu_aide = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=menu_aide)
        menu_aide.add_command(label="À propos", command=self._afficher_a_propos)
    
    def _creer_onglet_fort(self, notebook: ttk.Notebook):
        """Crée l'onglet de gestion du fort"""
        frame_fort = ttk.Frame(notebook)
        notebook.add(frame_fort, text="🏰 Fort")
        
        # Informations du fort
        info_frame = ttk.LabelFrame(frame_fort, text="Informations du Fort")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if self.fort:
            ttk.Label(info_frame, text=f"Nom: {self.fort.identite.nom}", 
                     style="Info.TLabel").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=f"ID: {self.fort.identite.id_fort}", 
                     style="Info.TLabel").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=f"Adresse: {self.fort.identite.adresse_orp}", 
                     style="Info.TLabel").pack(anchor=tk.W, padx=5, pady=2)
        
        # État du fort
        etat_frame = ttk.LabelFrame(frame_fort, text="État")
        etat_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.widgets["label_etat"] = ttk.Label(etat_frame, text="🔴 Inactif", 
                                              style="Status.TLabel")
        self.widgets["label_etat"].pack(anchor=tk.W, padx=5, pady=2)
        
        # Boutons de contrôle
        controle_frame = ttk.Frame(frame_fort)
        controle_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controle_frame, text="Activer Fort", 
                  command=self._activer_fort).pack(side=tk.LEFT, padx=5)
        ttk.Button(controle_frame, text="Désactiver Fort", 
                  command=self._desactiver_fort).pack(side=tk.LEFT, padx=5)
        
        # Publications
        pub_frame = ttk.LabelFrame(frame_fort, text="Publications")
        pub_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Zone de saisie publication
        saisie_frame = ttk.Frame(pub_frame)
        saisie_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.widgets["entry_publication"] = ttk.Entry(saisie_frame)
        self.widgets["entry_publication"].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(saisie_frame, text="Publier", 
                  command=self._publier_annonce).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Liste des publications
        self.widgets["listbox_publications"] = tk.Listbox(pub_frame)
        self.widgets["listbox_publications"].pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _creer_onglet_reseau(self, notebook: ttk.Notebook):
        """Crée l'onglet de gestion réseau"""
        frame_reseau = ttk.Frame(notebook)
        notebook.add(frame_reseau, text="🌐 Réseau")
        
        # Découverte
        decouverte_frame = ttk.LabelFrame(frame_reseau, text="Découverte")
        decouverte_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(decouverte_frame, text="Forcer Découverte", 
                  command=self._forcer_decouverte).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.widgets["label_forts_decouverts"] = ttk.Label(decouverte_frame, 
                                                          text="Forts découverts: 0")
        self.widgets["label_forts_decouverts"].pack(side=tk.LEFT, padx=20)
        
        # Liste des forts
        forts_frame = ttk.LabelFrame(frame_reseau, text="Forts Découverts")
        forts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview pour les forts
        colonnes = ("Nom", "ID", "Adresse", "Statut", "Dernière Activité")
        self.widgets["tree_forts"] = ttk.Treeview(forts_frame, columns=colonnes, show="headings")
        
        for col in colonnes:
            self.widgets["tree_forts"].heading(col, text=col)
            self.widgets["tree_forts"].column(col, width=120)
        
        self.widgets["tree_forts"].pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar pour le treeview
        scrollbar_forts = ttk.Scrollbar(forts_frame, orient=tk.VERTICAL, 
                                       command=self.widgets["tree_forts"].yview)
        scrollbar_forts.pack(side=tk.RIGHT, fill=tk.Y)
        self.widgets["tree_forts"].configure(yscrollcommand=scrollbar_forts.set)
    
    def _creer_onglet_projections(self, notebook: ttk.Notebook):
        """Crée l'onglet de gestion des projections"""
        frame_proj = ttk.Frame(notebook)
        notebook.add(frame_proj, text="🔮 Projections")
        
        # Contrôles projections
        controle_frame = ttk.LabelFrame(frame_proj, text="Contrôles")
        controle_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controle_frame, text="Créer Projection Test", 
                  command=self._creer_projection_test).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(controle_frame, text="Ouvrir Projection", 
                  command=self._ouvrir_projection).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Liste des projections
        proj_frame = ttk.LabelFrame(frame_proj, text="Projections Actives")
        proj_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        colonnes_proj = ("ID", "Propriétaire", "Observateur", "Temps Restant", "Protection")
        self.widgets["tree_projections"] = ttk.Treeview(proj_frame, columns=colonnes_proj, show="headings")
        
        for col in colonnes_proj:
            self.widgets["tree_projections"].heading(col, text=col)
            self.widgets["tree_projections"].column(col, width=100)
        
        self.widgets["tree_projections"].pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _creer_onglet_logs(self, notebook: ttk.Notebook):
        """Crée l'onglet des logs"""
        frame_logs = ttk.Frame(notebook)
        notebook.add(frame_logs, text="📋 Logs")
        
        # Zone de texte pour les logs
        self.widgets["text_logs"] = scrolledtext.ScrolledText(frame_logs, height=20)
        self.widgets["text_logs"].pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Boutons de contrôle logs
        log_controle_frame = ttk.Frame(frame_logs)
        log_controle_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_controle_frame, text="Effacer Logs", 
                  command=self._effacer_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_controle_frame, text="Sauvegarder Logs", 
                  command=self._sauvegarder_logs).pack(side=tk.LEFT, padx=5)
    
    def _creer_barre_statut(self):
        """Crée la barre de statut"""
        self.widgets["barre_statut"] = ttk.Frame(self.root)
        self.widgets["barre_statut"].pack(fill=tk.X, side=tk.BOTTOM)
        
        self.widgets["label_statut"] = ttk.Label(self.widgets["barre_statut"], 
                                               text="Prêt", style="Status.TLabel")
        self.widgets["label_statut"].pack(side=tk.LEFT, padx=5)
        
        self.widgets["label_heure"] = ttk.Label(self.widgets["barre_statut"], 
                                              text="", style="Status.TLabel")
        self.widgets["label_heure"].pack(side=tk.RIGHT, padx=5)
    
    # === CALLBACKS INTERFACE ===
    
    def _activer_fort(self):
        """Callback pour activer le fort"""
        if self.fort and not self.fort.actif:
            self.fort.activer()
            self._mettre_a_jour_etat_fort()
            self._ajouter_log("🟢 Fort activé")
    
    def _desactiver_fort(self):
        """Callback pour désactiver le fort"""
        if self.fort and self.fort.actif:
            self.fort.desactiver()
            self._mettre_a_jour_etat_fort()
            self._ajouter_log("🔴 Fort désactivé")
    
    def _publier_annonce(self):
        """Callback pour publier une annonce"""
        if not self.fort or not self.fort.actif:
            messagebox.showwarning("Avertissement", "Le fort doit être activé")
            return
        
        entry = self.widgets.get("entry_publication")
        if not entry:
            return
        
        contenu = entry.get().strip()
        if contenu:
            self.fort.publier_annonce(contenu)
            entry.delete(0, tk.END)
            self._mettre_a_jour_publications()
            self._ajouter_log(f"📢 Publication: {contenu[:50]}...")
    
    def _forcer_decouverte(self):
        """Callback pour forcer la découverte"""
        if hasattr(self.fort, 'decouvreur'):
            self.fort.decouvreur.forcer_decouverte()
            self._ajouter_log("🔍 Découverte forcée")
    
    def _creer_projection_test(self):
        """Callback pour créer une projection test"""
        self._ajouter_log("🔮 Création projection test...")
        # TODO: Implémenter création projection
    
    def _ouvrir_projection(self):
        """Callback pour ouvrir une projection"""
        self._ajouter_log("🪟 Ouverture projection...")
        # TODO: Implémenter ouverture projection
    
    def _afficher_statistiques(self):
        """Callback pour afficher les statistiques"""
        if self.fort:
            stats = self.fort.obtenir_statistiques()
            # TODO: Créer fenêtre de statistiques détaillées
            messagebox.showinfo("Statistiques", f"Fort: {stats['identite']['nom']}\n"
                                              f"Actif: {stats['etat']['actif']}\n"
                                              f"Forts connus: {stats['reseau']['forts_connus']}")
    
    def _afficher_carte(self):
        """Callback pour afficher la carte réseau"""
        self._ajouter_log("🗺️ Affichage carte réseau...")
        # TODO: Implémenter visualisation carte
    
    def _afficher_a_propos(self):
        """Callback pour afficher les informations"""
        messagebox.showinfo("À propos", 
                           "OpenRed Network v1.0.0\n\n"
                           "Réseau décentralisé de forts\n"
                           "avec projections sécurisées")
    
    def _effacer_logs(self):
        """Callback pour effacer les logs"""
        if "text_logs" in self.widgets:
            self.widgets["text_logs"].delete(1.0, tk.END)
    
    def _sauvegarder_logs(self):
        """Callback pour sauvegarder les logs"""
        # TODO: Implémenter sauvegarde logs
        self._ajouter_log("💾 Sauvegarde des logs...")
    
    # === MISES À JOUR INTERFACE ===
    
    def _demarrer_mises_a_jour(self):
        """Démarre les mises à jour périodiques de l'interface"""
        def mettre_a_jour():
            while self.interface_active:
                try:
                    # Mise à jour heure
                    if "label_heure" in self.widgets:
                        heure = time.strftime("%H:%M:%S")
                        self.root.after(0, lambda: self.widgets["label_heure"].config(text=heure))
                    
                    # Mise à jour état fort
                    self.root.after(0, self._mettre_a_jour_etat_fort)
                    
                    # Mise à jour liste forts
                    self.root.after(0, self._mettre_a_jour_forts_decouverts)
                    
                    time.sleep(2)  # Mise à jour toutes les 2 secondes
                    
                except Exception as e:
                    print(f"❌ Erreur mise à jour interface: {e}")
                    time.sleep(5)
        
        thread_maj = threading.Thread(target=mettre_a_jour, daemon=True)
        thread_maj.start()
        self.threads_actifs.append(thread_maj)
    
    def _mettre_a_jour_etat_fort(self):
        """Met à jour l'affichage de l'état du fort"""
        if not self.fort or "label_etat" not in self.widgets:
            return
        
        if self.fort.actif:
            texte = "🟢 Actif"
            couleur = "green"
        else:
            texte = "🔴 Inactif"
            couleur = "red"
        
        self.widgets["label_etat"].config(text=texte, foreground=couleur)
    
    def _mettre_a_jour_publications(self):
        """Met à jour la liste des publications"""
        if not self.fort or "listbox_publications" not in self.widgets:
            return
        
        listbox = self.widgets["listbox_publications"]
        listbox.delete(0, tk.END)
        
        fenetre_pub = self.fort.obtenir_fenetre_publique()
        if fenetre_pub:
            for pub in fenetre_pub.profil_public["publications_publiques"]:
                listbox.insert(tk.END, f"{pub['timestamp']}: {pub['contenu']}")
    
    def _mettre_a_jour_forts_decouverts(self):
        """Met à jour la liste des forts découverts"""
        if not hasattr(self.fort, 'decouvreur') or "tree_forts" not in self.widgets:
            return
        
        tree = self.widgets["tree_forts"]
        
        # Vider le tree
        for item in tree.get_children():
            tree.delete(item)
        
        # Ajouter les forts découverts
        if hasattr(self.fort, 'decouvreur'):
            for fort_info in self.fort.decouvreur.obtenir_forts_decouverts():
                tree.insert("", tk.END, values=(
                    fort_info.get("nom_fort", "N/A"),
                    fort_info.get("id_fort", "N/A")[:16] + "...",
                    f"{fort_info.get('addr_ip', 'N/A')}:{fort_info.get('port', 'N/A')}",
                    "En ligne",
                    time.strftime("%H:%M:%S", time.localtime(fort_info.get("derniere_activite", 0)))
                ))
        
        # Mise à jour compteur
        if "label_forts_decouverts" in self.widgets:
            nb_forts = len(tree.get_children())
            self.widgets["label_forts_decouverts"].config(text=f"Forts découverts: {nb_forts}")
    
    def _ajouter_log(self, message: str):
        """Ajoute un message aux logs"""
        if "text_logs" in self.widgets:
            timestamp = time.strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            
            text_widget = self.widgets["text_logs"]
            text_widget.insert(tk.END, log_message)
            text_widget.see(tk.END)  # Scroll vers le bas
    
    def _fermeture_interface(self):
        """Callback de fermeture de l'interface"""
        self.interface_active = False
        
        if self.fort and self.fort.actif:
            self.fort.desactiver()
        
        self.root.destroy()
    
    # === MÉTHODES PUBLIQUES ===
    
    def demarrer(self):
        """Démarre l'interface graphique"""
        if self.root:
            self.root.mainloop()
    
    def ajouter_callback(self, evenement: str, callback: Callable):
        """Ajoute un callback pour un événement"""
        if evenement not in self.callbacks:
            self.callbacks[evenement] = []
        self.callbacks[evenement].append(callback)
    
    def obtenir_widget(self, nom: str):
        """Obtient un widget par son nom"""
        return self.widgets.get(nom)
    
    def mettre_a_jour_statut(self, message: str):
        """Met à jour le message de statut"""
        if "label_statut" in self.widgets:
            self.widgets["label_statut"].config(text=message)