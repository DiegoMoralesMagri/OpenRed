#!/usr/bin/env python3
"""
Galerie de Projections Virtuelles
=================================
Interface galerie pour visualiser et "sauvegarder" des écrans virtuels.
Les "sauvegardes" sont des raccourcis vers les projections phantom,
pas les images elles-mêmes !
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import asyncio
import websockets
import json
import base64
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io
from datetime import datetime
import threading
import logging
import os
from pathlib import Path
import pickle
import uuid

# Import du format .orp
from orp_format import OrpFormat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VirtualScreenGallery:
    def __init__(self, server_url: str = "ws://localhost:8001/ws"):
        self.server_url = server_url
        self.websocket = None
        self.root = None
        
        # État connexion
        self.connection_alive = False
        
        # Projections disponibles sur le serveur
        self.server_phantoms: dict = {}
        
        # Écrans virtuels sauvegardés (raccourcis vers projections)
        self.saved_virtual_screens: dict = {}
        self.screens_folder = Path("mes-ecrans-virtuels")
        self.screens_folder.mkdir(exist_ok=True)
        
        # Interface
        self.setup_gui()
        self.load_saved_screens()
        
        # WebSocket
        self.ws_thread = None
        self.running = False
        
    def setup_gui(self):
        """Interface galerie"""
        self.root = tk.Tk()
        self.root.title("🖼️ Galerie de Projections Virtuelles")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')
        
        # Style sombre moderne
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Gallery.TFrame', background='#1a1a1a')
        style.configure('Gallery.TLabel', background='#1a1a1a', foreground='#ffffff')
        
        # Header
        header_frame = ttk.Frame(self.root, style='Gallery.TFrame')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = ttk.Label(
            header_frame,
            text="🖼️ GALERIE DE PROJECTIONS VIRTUELLES",
            style='Gallery.TLabel',
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side='left')
        
        self.connection_status = ttk.Label(
            header_frame,
            text="🔴 SERVEUR DÉCONNECTÉ",
            style='Gallery.TLabel',
            font=('Arial', 12)
        )
        self.connection_status.pack(side='right')
        
        # Notebook pour onglets
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Onglet 1: Projections Serveur
        self.server_frame = ttk.Frame(notebook, style='Gallery.TFrame')
        notebook.add(self.server_frame, text="📡 Projections Serveur")
        
        # Onglet 2: Mes Écrans Virtuels
        self.saved_frame = ttk.Frame(notebook, style='Gallery.TFrame')
        notebook.add(self.saved_frame, text="💾 Mes Écrans Virtuels")
        
        self.setup_server_tab()
        self.setup_saved_tab()
        
        # Contrôles
        control_frame = ttk.Frame(self.root, style='Gallery.TFrame')
        control_frame.pack(fill='x', padx=10, pady=5)
        
        connect_btn = tk.Button(
            control_frame,
            text="🔗 Connecter au Serveur",
            command=self.connect_to_server,
            bg='#2d5a2d', fg='white',
            font=('Arial', 10, 'bold')
        )
        connect_btn.pack(side='left', padx=5)
        
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Actualiser",
            command=self.refresh_gallery,
            bg='#2d4a5a', fg='white',
            font=('Arial', 10, 'bold')
        )
        refresh_btn.pack(side='left', padx=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_server_tab(self):
        """Onglet des projections serveur"""
        # Titre
        server_title = ttk.Label(
            self.server_frame,
            text="📡 Projections Disponibles sur le Serveur",
            style='Gallery.TLabel',
            font=('Arial', 14, 'bold')
        )
        server_title.pack(pady=10)
        
        # Zone scrollable pour miniatures
        canvas_frame = ttk.Frame(self.server_frame, style='Gallery.TFrame')
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.server_canvas = tk.Canvas(canvas_frame, bg='#2a2a2a', highlightthickness=0)
        server_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.server_canvas.yview)
        self.server_scrollable = ttk.Frame(self.server_canvas, style='Gallery.TFrame')
        
        self.server_scrollable.bind(
            "<Configure>",
            lambda e: self.server_canvas.configure(scrollregion=self.server_canvas.bbox("all"))
        )
        
        self.server_canvas.create_window((0, 0), window=self.server_scrollable, anchor="nw")
        self.server_canvas.configure(yscrollcommand=server_scrollbar.set)
        
        self.server_canvas.pack(side="left", fill="both", expand=True)
        server_scrollbar.pack(side="right", fill="y")
    
    def setup_saved_tab(self):
        """Onglet des écrans sauvegardés"""
        # Titre
        saved_title = ttk.Label(
            self.saved_frame,
            text="💾 Mes Écrans Virtuels Sauvegardés",
            style='Gallery.TLabel',
            font=('Arial', 14, 'bold')
        )
        saved_title.pack(pady=10)
        
        # Zone scrollable
        canvas_frame = ttk.Frame(self.saved_frame, style='Gallery.TFrame')
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.saved_canvas = tk.Canvas(canvas_frame, bg='#2a2a2a', highlightthickness=0)
        saved_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.saved_canvas.yview)
        self.saved_scrollable = ttk.Frame(self.saved_canvas, style='Gallery.TFrame')
        
        self.saved_scrollable.bind(
            "<Configure>",
            lambda e: self.saved_canvas.configure(scrollregion=self.saved_canvas.bbox("all"))
        )
        
        self.saved_canvas.create_window((0, 0), window=self.saved_scrollable, anchor="nw")
        self.saved_canvas.configure(yscrollcommand=saved_scrollbar.set)
        
        self.saved_canvas.pack(side="left", fill="both", expand=True)
        saved_scrollbar.pack(side="right", fill="y")
    
    def create_server_thumbnail(self, phantom_data: dict):
        """Crée une miniature pour projection serveur"""
        phantom_id = phantom_data['id']
        
        try:
            # Miniature de la projection
            image_data = base64.b64decode(phantom_data['data'])
            pil_image = Image.open(io.BytesIO(image_data))
            pil_image.thumbnail((150, 150), Image.Resampling.LANCZOS)
            thumbnail = ImageTk.PhotoImage(pil_image)
            
            # Cadre pour la miniature
            thumb_frame = tk.Frame(self.server_scrollable, bg='#3a3a3a', relief='raised', bd=2)
            thumb_frame.pack(side='left', padx=5, pady=5)
            
            # Image miniature
            img_label = tk.Label(thumb_frame, image=thumbnail, bg='#3a3a3a')
            img_label.pack(pady=5)
            
            # Nom
            name_label = tk.Label(
                thumb_frame,
                text=phantom_data['name'][:20],
                bg='#3a3a3a', fg='white',
                font=('Arial', 9, 'bold')
            )
            name_label.pack()
            
            # Boutons d'action
            btn_frame = tk.Frame(thumb_frame, bg='#3a3a3a')
            btn_frame.pack(pady=5)
            
            # Bouton "Voir"
            view_btn = tk.Button(
                btn_frame,
                text="👁️ Voir",
                command=lambda: self.open_phantom_viewer(phantom_data),
                bg='#4a6a4a', fg='white',
                font=('Arial', 8)
            )
            view_btn.pack(side='left', padx=2)
            
            # Bouton "Sauver Écran"
            save_btn = tk.Button(
                btn_frame,
                text="💾 Sauver",
                command=lambda: self.save_virtual_screen(phantom_data),
                bg='#6a4a6a', fg='white',
                font=('Arial', 8)
            )
            save_btn.pack(side='left', padx=2)
            
            # Bouton "Créer .orp"
            orp_btn = tk.Button(
                btn_frame,
                text="📄 .orp",
                command=lambda: self.create_orp_file(phantom_data),
                bg='#6a6a4a', fg='white',
                font=('Arial', 8)
            )
            orp_btn.pack(side='left', padx=2)
            
            # Garder référence pour éviter garbage collection
            img_label.image = thumbnail
            
        except Exception as e:
            logger.error(f"Erreur création miniature: {e}")
    
    def create_saved_thumbnail(self, screen_data: dict):
        """Crée une miniature pour écran sauvegardé"""
        try:
            # Tenter de récupérer l'image depuis le serveur
            phantom_id = screen_data['phantom_id']
            
            if phantom_id in self.server_phantoms and self.connection_alive:
                # Image disponible
                phantom_data = self.server_phantoms[phantom_id]
                image_data = base64.b64decode(phantom_data['data'])
                pil_image = Image.open(io.BytesIO(image_data))
                pil_image.thumbnail((150, 150), Image.Resampling.LANCZOS)
                thumbnail = ImageTk.PhotoImage(pil_image)
                status_color = '#4a6a4a'
                status_text = "🟢 Disponible"
            else:
                # Écran noir (projection non disponible)
                black_screen = Image.new('RGB', (150, 150), color='#000000')
                draw = ImageDraw.Draw(black_screen)
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except:
                    font = ImageFont.load_default()
                
                draw.text((75, 60), "⚫", fill='#666666', font=font, anchor='mm')
                draw.text((75, 90), "ÉCRAN NOIR", fill='#666666', font=font, anchor='mm')
                thumbnail = ImageTk.PhotoImage(black_screen)
                status_color = '#6a4a4a'
                status_text = "⚫ Hors ligne"
            
            # Cadre
            thumb_frame = tk.Frame(self.saved_scrollable, bg='#3a3a3a', relief='raised', bd=2)
            thumb_frame.pack(side='left', padx=5, pady=5)
            
            # Image
            img_label = tk.Label(thumb_frame, image=thumbnail, bg='#3a3a3a')
            img_label.pack(pady=5)
            
            # Nom sauvegardé
            name_label = tk.Label(
                thumb_frame,
                text=screen_data['saved_name'][:20],
                bg='#3a3a3a', fg='white',
                font=('Arial', 9, 'bold')
            )
            name_label.pack()
            
            # Statut
            status_label = tk.Label(
                thumb_frame,
                text=status_text,
                bg='#3a3a3a', fg=status_color,
                font=('Arial', 8)
            )
            status_label.pack()
            
            # Boutons
            btn_frame = tk.Frame(thumb_frame, bg='#3a3a3a')
            btn_frame.pack(pady=5)
            
            # Bouton "Ouvrir Écran"
            open_btn = tk.Button(
                btn_frame,
                text="📺 Ouvrir",
                command=lambda: self.open_virtual_screen(screen_data),
                bg='#4a5a6a', fg='white',
                font=('Arial', 8)
            )
            open_btn.pack(side='left', padx=2)
            
            # Bouton "Supprimer"
            delete_btn = tk.Button(
                btn_frame,
                text="🗑️",
                command=lambda: self.delete_virtual_screen(screen_data['screen_id']),
                bg='#6a4a4a', fg='white',
                font=('Arial', 8)
            )
            delete_btn.pack(side='left', padx=2)
            
            img_label.image = thumbnail
            
        except Exception as e:
            logger.error(f"Erreur miniature sauvegardée: {e}")
    
    def save_virtual_screen(self, phantom_data: dict):
        """Sauvegarde un écran virtuel (raccourci vers projection)"""
        # Demander nom de sauvegarde
        name = tk.simpledialog.askstring(
            "Sauvegarder Écran Virtuel",
            f"Nom pour l'écran '{phantom_data['name']}':",
            initialvalue=phantom_data['name']
        )
        
        if name:
            screen_id = str(uuid.uuid4())
            
            # Données de l'écran virtuel (PAS l'image !)
            screen_data = {
                'screen_id': screen_id,
                'saved_name': name,
                'phantom_id': phantom_data['id'],
                'original_name': phantom_data['name'],
                'server_url': self.server_url,
                'saved_at': datetime.now().isoformat(),
                'size': phantom_data.get('size', 0)
            }
            
            # Sauvegarde du raccourci
            screen_file = self.screens_folder / f"{screen_id}.vscreen"
            with open(screen_file, 'wb') as f:
                pickle.dump(screen_data, f)
            
            self.saved_virtual_screens[screen_id] = screen_data
            
            logger.info(f"💾 Écran virtuel sauvé: {name}")
            messagebox.showinfo("Sauvegarde", f"Écran virtuel '{name}' sauvegardé!")
            
            self.refresh_saved_gallery()
    
    def create_orp_file(self, phantom_data: dict):
        """Crée un fichier .orp pour une projection phantom"""
        # Demander nom et emplacement
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder comme fichier .orp",
            defaultextension=".orp",
            filetypes=[
                ("Fichiers OpenRed Phantom", "*.orp"),
                ("Tous les fichiers", "*.*")
            ],
            initialfile=f"{phantom_data['name']}.orp"
        )
        
        if filename:
            try:
                # Créer le fichier .orp
                orp = OrpFormat.create_phantom_file(
                    phantom_id=phantom_data['id'],
                    phantom_name=phantom_data['name'],
                    server_url=self.server_url.replace("ws://", "http://").replace("/ws", ""),
                    phantom_size=(400, 300),  # Taille par défaut, sera ajustée
                    mime_type=phantom_data.get('mime_type', 'image/jpeg')
                )
                
                # Métadonnées additionnelles
                orp.metadata["original_size"] = phantom_data.get('size', 0)
                orp.metadata["created_from_gallery"] = True
                orp.metadata["gallery_version"] = "1.0.0"
                
                # Sauvegarde
                orp.save_to_file(Path(filename))
                
                logger.info(f"📄 Fichier .orp créé: {filename}")
                messagebox.showinfo("Succès", f"Fichier .orp créé avec succès !\n\n{Path(filename).name}\n\nVous pouvez maintenant l'ouvrir avec orp_viewer.py ou l'associer à l'extension .orp")
                
            except Exception as e:
                logger.error(f"Erreur création .orp: {e}")
                messagebox.showerror("Erreur", f"Impossible de créer le fichier .orp:\n{e}")
    
    def open_virtual_screen(self, screen_data: dict):
        """Ouvre un écran virtuel (fenêtre de projection)"""
        phantom_id = screen_data['phantom_id']
        
        if phantom_id in self.server_phantoms and self.connection_alive:
            # Projection disponible
            phantom_data = self.server_phantoms[phantom_id]
            self.create_screen_window(phantom_data, screen_data['saved_name'])
        else:
            # Écran noir
            self.create_black_screen_window(screen_data['saved_name'])
    
    def create_screen_window(self, phantom_data: dict, window_title: str):
        """Crée une fenêtre écran pour la projection"""
        try:
            # Décoder l'image
            image_data = base64.b64decode(phantom_data['data'])
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Fenêtre sans bordure, taille de l'image
            screen_window = tk.Toplevel(self.root)
            screen_window.title(window_title)
            screen_window.configure(bg='black')
            
            # Taille exacte de l'image
            img_width, img_height = pil_image.size
            screen_window.geometry(f"{img_width}x{img_height}")
            screen_window.resizable(False, False)
            
            # Option: supprimer bordures (décommenter si souhaité)
            # screen_window.overrideredirect(True)
            
            # Affichage de l'image
            tk_image = ImageTk.PhotoImage(pil_image)
            img_label = tk.Label(screen_window, image=tk_image, bg='black')
            img_label.pack()
            
            # Garder référence
            img_label.image = tk_image
            
            # Surveillance de la connexion
            def check_connection():
                if not self.connection_alive or phantom_data['id'] not in self.server_phantoms:
                    # Remplacer par écran noir
                    black_img = Image.new('RGB', (img_width, img_height), color='#000000')
                    draw = ImageDraw.Draw(black_img)
                    
                    try:
                        font = ImageFont.truetype("arial.ttf", 24)
                    except:
                        font = ImageFont.load_default()
                    
                    draw.text((img_width//2, img_height//2), "⚫ SIGNAL PERDU", 
                             fill='#666666', font=font, anchor='mm')
                    
                    black_tk = ImageTk.PhotoImage(black_img)
                    img_label.configure(image=black_tk)
                    img_label.image = black_tk
                
                # Vérifier toutes les 2 secondes
                screen_window.after(2000, check_connection)
            
            check_connection()
            
            logger.info(f"📺 Écran virtuel ouvert: {window_title}")
            
        except Exception as e:
            logger.error(f"Erreur ouverture écran: {e}")
            self.create_black_screen_window(window_title)
    
    def create_black_screen_window(self, window_title: str):
        """Crée une fenêtre écran noir"""
        screen_window = tk.Toplevel(self.root)
        screen_window.title(f"{window_title} - SIGNAL PERDU")
        screen_window.configure(bg='black')
        screen_window.geometry("400x300")
        
        # Écran noir avec message
        black_img = Image.new('RGB', (400, 300), color='#000000')
        draw = ImageDraw.Draw(black_img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((200, 120), "⚫ ÉCRAN NOIR", fill='#666666', font=font, anchor='mm')
        draw.text((200, 160), "Projection non disponible", fill='#444444', font=font, anchor='mm')
        
        black_tk = ImageTk.PhotoImage(black_img)
        img_label = tk.Label(screen_window, image=black_tk, bg='black')
        img_label.pack()
        img_label.image = black_tk
        
        logger.info(f"⚫ Écran noir ouvert: {window_title}")
    
    def open_phantom_viewer(self, phantom_data: dict):
        """Ouvre un viewer temporaire pour une projection"""
        self.create_screen_window(phantom_data, f"Projection: {phantom_data['name']}")
    
    def load_saved_screens(self):
        """Charge les écrans virtuels sauvegardés"""
        for screen_file in self.screens_folder.glob("*.vscreen"):
            try:
                with open(screen_file, 'rb') as f:
                    screen_data = pickle.load(f)
                    self.saved_virtual_screens[screen_data['screen_id']] = screen_data
            except Exception as e:
                logger.error(f"Erreur chargement écran {screen_file}: {e}")
    
    def delete_virtual_screen(self, screen_id: str):
        """Supprime un écran virtuel sauvegardé"""
        if messagebox.askyesno("Supprimer", "Supprimer cet écran virtuel ?"):
            # Supprimer fichier
            screen_file = self.screens_folder / f"{screen_id}.vscreen"
            if screen_file.exists():
                screen_file.unlink()
            
            # Supprimer de la mémoire
            if screen_id in self.saved_virtual_screens:
                del self.saved_virtual_screens[screen_id]
            
            self.refresh_saved_gallery()
    
    def refresh_gallery(self):
        """Actualise toute la galerie"""
        self.refresh_server_gallery()
        self.refresh_saved_gallery()
    
    def refresh_server_gallery(self):
        """Actualise la galerie serveur"""
        # Nettoyer
        for widget in self.server_scrollable.winfo_children():
            widget.destroy()
        
        # Recréer miniatures
        for phantom_data in self.server_phantoms.values():
            self.create_server_thumbnail(phantom_data)
    
    def refresh_saved_gallery(self):
        """Actualise la galerie sauvegardée"""
        # Nettoyer
        for widget in self.saved_scrollable.winfo_children():
            widget.destroy()
        
        # Recréer miniatures
        for screen_data in self.saved_virtual_screens.values():
            self.create_saved_thumbnail(screen_data)
    
    async def websocket_handler(self):
        """Gestionnaire WebSocket"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.connection_alive = True
            
            self.root.after(0, lambda: self.connection_status.configure(
                text="🟢 SERVEUR CONNECTÉ"
            ))
            
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_phantom_message(data)
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            logger.error(f"Erreur WebSocket: {e}")
            self.connection_alive = False
            self.root.after(0, lambda: self.connection_status.configure(
                text="🔴 SERVEUR DÉCONNECTÉ"
            ))
        finally:
            self.websocket = None
            self.connection_alive = False
    
    async def handle_phantom_message(self, data: dict):
        """Traitement messages phantom"""
        msg_type = data.get('type')
        
        if msg_type == 'phantom_list':
            self.server_phantoms.clear()
            for phantom in data.get('phantoms', []):
                self.server_phantoms[phantom['id']] = phantom
            self.root.after(0, self.refresh_server_gallery)
            
        elif msg_type == 'phantom_created':
            phantom_data = data.get('phantom_data')
            if phantom_data:
                self.server_phantoms[phantom_data['id']] = phantom_data
                self.root.after(0, self.refresh_gallery)
                
        elif msg_type == 'phantom_deleted':
            phantom_id = data.get('phantom_id')
            if phantom_id and phantom_id in self.server_phantoms:
                del self.server_phantoms[phantom_id]
                self.root.after(0, self.refresh_gallery)
    
    def connect_to_server(self):
        """Connexion au serveur"""
        if not self.running:
            self.running = True
            self.ws_thread = threading.Thread(target=self.run_websocket)
            self.ws_thread.daemon = True
            self.ws_thread.start()
    
    def run_websocket(self):
        """Exécution WebSocket"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.websocket_handler())
        except Exception as e:
            logger.error(f"Erreur boucle WebSocket: {e}")
        finally:
            loop.close()
    
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
        """Démarrage de la galerie"""
        logger.info("🖼️ Démarrage Galerie de Projections Virtuelles")
        self.root.mainloop()

def main():
    import sys
    
    server_url = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8001/ws"
    
    gallery = VirtualScreenGallery(server_url)
    gallery.run()

if __name__ == "__main__":
    main()