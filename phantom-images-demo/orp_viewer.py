#!/usr/bin/env python3
"""
Viewer OpenRed Phantom (.orp)
=============================
Application pour ouvrir et visualiser les fichiers .orp.
Peut être associée à l'extension .orp dans Windows/Linux/macOS.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import websockets
import json
import base64
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io
import sys
import threading
import time
from pathlib import Path
import logging

# Import du format .orp
from orp_format import OrpFormat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrpViewer:
    def __init__(self, orp_file_path: str = None):
        self.root = tk.Tk()
        self.orp_file_path = orp_file_path
        self.orp_data = None
        self.websocket = None
        self.connection_alive = False
        self.running = False
        self.phantom_image = None
        
        # Images de fallback
        self.loading_image = None
        self.error_image = None
        self.no_server_image = None
        
        self.setup_gui()
        self.create_fallback_images()
        
        # Si fichier fourni, l'ouvrir
        if self.orp_file_path:
            self.load_orp_file(self.orp_file_path)
            # Tentative de connexion automatique après chargement
            self.root.after(1000, self.auto_connect_phantom)
        
        # WebSocket
        self.ws_thread = None
        self.running = False
    
    def setup_gui(self):
        """Interface du viewer .orp"""
        self.root.title("OpenRed Phantom Viewer (.orp)")
        self.root.configure(bg='#1a1a1a')
        
        # Icône et style
        try:
            # Style sombre
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('Orp.TFrame', background='#1a1a1a')
            style.configure('Orp.TLabel', background='#1a1a1a', foreground='#ffffff')
        except:
            pass
        
        # Menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir .orp...", command=self.open_file_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)
        
        # Header info
        self.info_frame = ttk.Frame(self.root)
        self.info_frame.pack(fill='x', padx=10, pady=5)
        
        self.file_label = tk.Label(
            self.info_frame,
            text="Aucun fichier .orp ouvert",
            bg='#1a1a1a', fg='#cccccc',
            font=('Arial', 12, 'bold')
        )
        self.file_label.pack(side='left')
        
        self.status_label = tk.Label(
            self.info_frame,
            text="🔴 DÉCONNECTÉ",
            bg='#1a1a1a', fg='#ff4444',
            font=('Arial', 11)
        )
        self.status_label.pack(side='right')
        
        # Zone d'affichage principale
        self.display_frame = tk.Frame(self.root, bg='#000000', relief='sunken', bd=2)
        self.display_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Label pour l'image/message
        self.image_label = tk.Label(
            self.display_frame,
            bg='#000000',
            fg='#666666',
            font=('Arial', 14)
        )
        self.image_label.pack(expand=True)
        
        # Contrôles
        control_frame = tk.Frame(self.root, bg='#1a1a1a')
        control_frame.pack(fill='x', padx=10, pady=5)
        
        open_btn = tk.Button(
            control_frame,
            text="📂 Ouvrir .orp",
            command=self.open_file_dialog,
            bg='#2d4a5a', fg='white',
            font=('Arial', 10)
        )
        open_btn.pack(side='left', padx=5)
        
        self.connect_btn = tk.Button(
            control_frame,
            text="🔗 Connecter",
            command=self.connect_to_phantom,
            bg='#2d5a2d', fg='white',
            font=('Arial', 10),
            state='disabled'
        )
        self.connect_btn.pack(side='left', padx=5)
        
        # Info phantom
        self.info_text = tk.Text(
            control_frame,
            height=3, width=50,
            bg='#2a2a2a', fg='#cccccc',
            font=('Courier', 9)
        )
        self.info_text.pack(side='right', padx=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_fallback_images(self):
        """Crée les images de fallback"""
        
        # Image "Chargement"
        loading = Image.new('RGB', (400, 300), color='#1a1a3a')
        draw = ImageDraw.Draw(loading)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((200, 130), "⏳ CHARGEMENT...", fill='#6666ff', 
                 font=font, anchor='mm')
        draw.text((200, 170), "Connexion au serveur phantom", fill='#4444aa', 
                 font=font, anchor='mm')
        
        self.loading_image = ImageTk.PhotoImage(loading)
        
        # Image "Erreur"
        error = Image.new('RGB', (400, 300), color='#3a1a1a')
        draw = ImageDraw.Draw(error)
        
        draw.text((200, 100), "❌ ERREUR", fill='#ff6666', 
                 font=font, anchor='mm')
        draw.text((200, 140), "Impossible de charger", fill='#aa4444', 
                 font=font, anchor='mm')
        draw.text((200, 160), "la projection phantom", fill='#aa4444', 
                 font=font, anchor='mm')
        
        self.error_image = ImageTk.PhotoImage(error)
        
        # Image "Serveur non disponible"
        no_server = Image.new('RGB', (400, 300), color='#000000')
        draw = ImageDraw.Draw(no_server)
        
        draw.text((200, 100), "⚫ ÉCRAN NOIR", fill='#666666', 
                 font=font, anchor='mm')
        draw.text((200, 140), "Serveur phantom", fill='#444444', 
                 font=font, anchor='mm')
        draw.text((200, 160), "non disponible", fill='#444444', 
                 font=font, anchor='mm')
        draw.text((200, 200), "Fichier .orp valide mais", fill='#333333', 
                 font=font, anchor='mm')
        draw.text((200, 220), "projection inaccessible", fill='#333333', 
                 font=font, anchor='mm')
        
        self.no_server_image = ImageTk.PhotoImage(no_server)
    
    def open_file_dialog(self):
        """Ouvre un dialogue pour sélectionner un fichier .orp"""
        file_path = filedialog.askopenfilename(
            title="Ouvrir un fichier OpenRed Phantom",
            filetypes=[
                ("Fichiers OpenRed Phantom", "*.orp"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if file_path:
            self.load_orp_file(file_path)
    
    def load_orp_file(self, file_path: str):
        """Charge un fichier .orp"""
        try:
            self.orp_file_path = file_path
            self.orp_data = OrpFormat.load_from_file(Path(file_path))
            
            if not self.orp_data.is_valid():
                raise ValueError("Fichier .orp invalide")
            
            # Mise à jour interface
            info = self.orp_data.get_display_info()
            file_name = Path(file_path).name
            
            self.file_label.configure(text=f"📄 {file_name}")
            self.root.title(f"OpenRed Phantom Viewer - {info['name']}")
            
            # Informations dans le text widget
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Phantom: {info['name']}\n")
            self.info_text.insert(tk.END, f"Taille: {info['dimensions']['width']}x{info['dimensions']['height']}\n")
            self.info_text.insert(tk.END, f"Serveur: {info['server_url']}")
            
            # Activer connexion
            self.connect_btn.configure(state='normal')
            
            # Afficher image de chargement
            self.image_label.configure(image=self.loading_image, text="")
            
            # Adapter taille fenêtre
            window_width = max(600, info['dimensions']['width'] + 100)
            window_height = max(500, info['dimensions']['height'] + 200)
            self.root.geometry(f"{window_width}x{window_height}")
            
            logger.info(f"Fichier .orp chargé: {info['name']}")
            
        except Exception as e:
            logger.error(f"Erreur chargement .orp: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger le fichier .orp:\n{e}")
            self.image_label.configure(image=self.error_image, text="")
    
    def auto_connect_phantom(self):
        """Connexion automatique au phantom après chargement du fichier"""
        if self.orp_data and not self.connection_alive:
            logger.info("🔗 Tentative de connexion automatique...")
            self.status_label.configure(text="🔗 CONNEXION AUTO...", fg='#ffaa00')
            threading.Thread(target=self.connect_phantom_thread, daemon=True).start()
    
    def connect_to_phantom(self):
        """Connexion au serveur phantom"""
        if not self.orp_data:
            messagebox.showwarning("Attention", "Aucun fichier .orp chargé")
            return
        
        if not self.running:
            self.running = True
            self.ws_thread = threading.Thread(target=self.connect_phantom_thread, daemon=True)
            self.ws_thread.start()
            
            self.status_label.configure(text="🟡 CONNEXION...", fg='#ffaa00')
            self.connect_btn.configure(state='disabled')
    
    def connect_phantom_thread(self):
        """Thread de connexion phantom avec gestion d'erreur"""
        try:
            asyncio.run(self.websocket_handler())
        except Exception as e:
            logger.error(f"Erreur connexion phantom: {e}")
            # Gestion d'erreur dans le thread principal
            self.root.after(0, lambda: self.connection_failed(str(e)))
    
    def connection_failed(self, error_msg: str):
        """Gestion d'échec de connexion"""
        self.status_label.configure(text="❌ CONNEXION ÉCHOUÉE", fg='#ff4444')
        self.connect_btn.configure(state='normal')
        self.running = False
        
        # Afficher image d'erreur serveur
        self.image_label.configure(image=self.no_server_image, text="")
        
        # Message informatif pour l'utilisateur selon le type d'erreur
        # Mais seulement si c'est une tentative manuelle, pas depuis l'explorateur au démarrage
        if not hasattr(self, '_initial_connection_attempted'):
            self._initial_connection_attempted = True
            
            if ("Connection refused" in error_msg or 
                "ConnectCall" in error_msg or 
                "WinError 1225" in error_msg or
                "refused" in error_msg.lower()):
                messagebox.showinfo(
                    "Serveur non disponible", 
                    "Le serveur Phantom n'est pas démarré.\n\n" +
                    "Pour voir cette projection phantom:\n" +
                    "1. Démarrez le serveur phantom\n" +
                    "2. Cliquez sur 'Connecter' ou relancez le fichier .orp"
                )
            else:
                messagebox.showerror(
                    "Erreur de connexion",
                    f"Impossible de se connecter au serveur phantom:\n\n{error_msg}"
                )
    
    async def websocket_handler(self):
        """Gestionnaire WebSocket pour récupérer la projection"""
        try:
            server_url = self.orp_data.access_data['websocket_url']
            # Timeout de 5 secondes pour la connexion
            self.websocket = await asyncio.wait_for(
                websockets.connect(server_url), 
                timeout=5.0
            )
            self.connection_alive = True
            
            self.root.after(0, lambda: self.status_label.configure(
                text="🟢 CONNECTÉ", fg='#44ff44'
            ))
            
            # Rechercher notre phantom
            phantom_id = self.orp_data.metadata['phantom_id']
            logger.info(f"🔍 Recherche du phantom: {phantom_id}")
            
            # Attendre les messages avec timeout
            phantom_found = False
            timeout_seconds = 10.0
            
            try:
                await asyncio.wait_for(
                    self._process_messages(phantom_id), 
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Timeout ({timeout_seconds}s) - Phantom '{phantom_id}' non trouvé")
                self.root.after(0, self.phantom_not_found)
                
        except Exception as e:
            logger.error(f"Erreur WebSocket: {e}")
            self.connection_alive = False
            # Transmettre l'erreur au thread principal
            self.root.after(0, lambda: self.connection_failed(str(e)))
            self.root.after(0, lambda: self.image_label.configure(
                image=self.no_server_image, text=""
            ))
        finally:
            self.websocket = None
            self.connection_alive = False
            self.root.after(0, lambda: self.connect_btn.configure(state='normal'))
    
    async def _process_messages(self, target_phantom_id: str):
        """Traite les messages WebSocket jusqu'à trouver le phantom ou timeout"""
        async for message in self.websocket:
            try:
                data = json.loads(message)
                logger.info(f"📨 Message reçu: {data.get('type', 'unknown')}")
                
                await self.handle_phantom_message(data, target_phantom_id)
                
                # Si on a trouvé et affiché le phantom, on peut arrêter
                if hasattr(self, '_phantom_displayed') and self._phantom_displayed:
                    break
                    
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Message JSON invalide: {e}")
    
    async def handle_phantom_message(self, data: dict, target_phantom_id: str):
        """Traitement des messages phantom"""
        msg_type = data.get('type')
        
        if msg_type == 'phantom_list':
            logger.info(f"📋 Liste reçue avec {len(data.get('phantoms', []))} phantoms")
            # Rechercher notre phantom dans la liste
            for phantom in data.get('phantoms', []):
                logger.info(f"   - Phantom: {phantom['id']} ({phantom['name']})")
                if phantom['id'] == target_phantom_id:
                    logger.info(f"✅ Phantom trouvé! Affichage...")
                    self.root.after(0, lambda p=phantom: self.display_phantom(p))
                    self._phantom_displayed = True
                    return
            
            # Phantom non trouvé
            logger.warning(f"❌ Phantom '{target_phantom_id}' non trouvé dans la liste")
            self.root.after(0, self.phantom_not_found)
            
        elif msg_type == 'phantom_created':
            phantom_data = data.get('phantom_data')
            if phantom_data and phantom_data['id'] == target_phantom_id:
                self.root.after(0, lambda: self.display_phantom(phantom_data))
                self._phantom_displayed = True
                
        elif msg_type == 'phantom_deleted':
            phantom_id = data.get('phantom_id')
            if phantom_id == target_phantom_id:
                self.root.after(0, self.phantom_deleted)
    
    def display_phantom(self, phantom_data: dict):
        """Affiche la projection phantom"""
        try:
            # Décoder l'image
            image_data = base64.b64decode(phantom_data['data'])
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Conserver taille originale
            tk_image = ImageTk.PhotoImage(pil_image)
            
            self.image_label.configure(image=tk_image, text="")
            self.phantom_image = tk_image  # Garde référence
            
            logger.info(f"Projection affichée: {phantom_data['name']}")
            
        except Exception as e:
            logger.error(f"Erreur affichage phantom: {e}")
            self.image_label.configure(image=self.error_image, text="")
    
    def phantom_not_found(self):
        """Phantom non trouvé sur le serveur"""
        self.image_label.configure(image=self.no_server_image, text="")
        self.status_label.configure(text="❌ PHANTOM INTROUVABLE", fg='#ff4444')
        self.connect_btn.configure(state='normal')
        self.running = False
        
        # Message informatif pour l'utilisateur
        phantom_id = self.orp_data.metadata.get('phantom_id', 'inconnu') if self.orp_data else 'inconnu'
        messagebox.showwarning(
            "Phantom introuvable",
            f"Le phantom avec l'ID '{phantom_id}' n'a pas été trouvé sur le serveur.\n\n" +
            "Solutions possibles :\n" +
            "1. Vérifiez que le serveur phantom est démarré\n" +
            "2. Ajoutez le phantom manquant au serveur\n" +
            "3. Utilisez le script ajouter_phantoms_test.py\n\n" +
            "La fenêtre restera ouverte pour d'autres tests."
        )
    
    def phantom_deleted(self):
        """Phantom supprimé du serveur"""
        self.image_label.configure(image=self.no_server_image, text="")
        self.status_label.configure(text="💨 PHANTOM SUPPRIMÉ", fg='#ff4444')
    
    def show_about(self):
        """À propos"""
        about_text = """OpenRed Phantom Viewer v1.0.0

Viewer pour fichiers OpenRed Phantom (.orp)

Les fichiers .orp ne contiennent pas d'images,
mais des liens vers des projections phantom.

L'image n'est visible que si:
• Le serveur phantom est en ligne
• La projection existe
• Vous avez les autorisations

© 2025 OpenRed System"""
        
        messagebox.showinfo("À propos", about_text)
    
    def on_closing(self):
        """Fermeture propre"""
        self.running = False
        self.connection_alive = False
        
        if self.websocket:
            try:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.close(),
                    asyncio.get_event_loop()
                )
            except:
                pass
        
        self.root.destroy()
    
    def run(self):
        """Démarrage du viewer"""
        logger.info("🖼️ Démarrage OpenRed Phantom Viewer")
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    import sys
    
    # Fichier .orp fourni en argument ?
    orp_file = None
    if len(sys.argv) > 1:
        orp_file = sys.argv[1]
        if not orp_file.endswith('.orp'):
            print("❌ Erreur: Le fichier doit avoir l'extension .orp")
            return
    
    # Lancement du viewer
    viewer = OrpViewer(orp_file)
    viewer.run()

if __name__ == "__main__":
    main()