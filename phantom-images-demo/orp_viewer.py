#!/usr/bin/env python3
"""
Viewer OpenRed Phantom (.orp)
==============================
Application officielle pour ouvrir et visualiser les fichiers .orp
Format propriétaire OpenRed pour images sécurisées temporaires.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import websockets
import json
import base64
from PIL import Image, ImageTk
import io
import sys
import threading
import time
from pathlib import Path
import logging

# Import du format .orp officiel
from orp_format import OrpFormat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrpViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Viewer OpenRed Phantom (.orp) - Version Officielle")
        self.root.geometry("800x600")
        
        self.current_image = None
        self.current_orp_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Interface utilisateur simple et propre"""
        # Menu principal
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir .orp...", command=self.open_orp_file)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Zone d'affichage
        self.image_frame = ttk.Frame(self.root)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.image_label = ttk.Label(self.image_frame, text="Aucune image chargée")
        self.image_label.pack(expand=True)
        
        # Barre de statut
        self.status_bar = ttk.Label(self.root, text="Prêt", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def open_orp_file(self):
        """Ouvrir un fichier .orp"""
        file_path = filedialog.askopenfilename(
            title="Ouvrir un fichier OpenRed Phantom",
            filetypes=[("Fichiers OpenRed Phantom", "*.orp"), ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            self.load_orp_file(file_path)
            
    def load_orp_file(self, file_path: str):
        """Charger et afficher un fichier .orp"""
        try:
            self.status_bar.config(text="Chargement...")
            
            # Charger le fichier .orp
            orp_data = OrpFormat.load_orp_file(file_path)
            self.current_orp_data = orp_data
            
            # Décoder l'image
            image_data = base64.b64decode(orp_data['image_data'])
            image = Image.open(io.BytesIO(image_data))
            
            # Redimensionner si nécessaire
            display_image = self.resize_image_for_display(image)
            
            # Convertir pour Tkinter
            self.current_image = ImageTk.PhotoImage(display_image)
            self.image_label.config(image=self.current_image, text="")
            
            # Mettre à jour le statut
            filename = Path(file_path).name
            self.status_bar.config(text=f"Chargé: {filename}")
            
            # Mettre à jour le titre
            self.root.title(f"Viewer OpenRed Phantom - {filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier .orp:\n{str(e)}")
            self.status_bar.config(text="Erreur de chargement")
            logger.error(f"Erreur lors du chargement: {e}")
            
    def resize_image_for_display(self, image: Image.Image) -> Image.Image:
        """Redimensionner l'image pour l'affichage"""
        frame_width = self.image_frame.winfo_width() or 750
        frame_height = self.image_frame.winfo_height() or 500
        
        # Garder les proportions
        image_ratio = image.width / image.height
        frame_ratio = frame_width / frame_height
        
        if image_ratio > frame_ratio:
            # Image plus large que le cadre
            new_width = frame_width
            new_height = int(frame_width / image_ratio)
        else:
            # Image plus haute que le cadre
            new_height = frame_height
            new_width = int(frame_height * image_ratio)
            
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
    def run(self):
        """Démarrer l'application"""
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1:
        # Fichier passé en argument
        viewer = OrpViewer()
        viewer.load_orp_file(sys.argv[1])
        viewer.run()
    else:
        # Mode normal
        viewer = OrpViewer()
        viewer.run()

if __name__ == "__main__":
    main()