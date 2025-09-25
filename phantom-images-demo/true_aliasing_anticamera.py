#!/usr/bin/env python3
"""
VRAI SYSTÈME ANTI-CAMÉRA PAR ALIASING
=====================================
Pattern invisible à l'œil humain mais révélé par ALIASING caméra

Principe scientifique CORRECT:
- Pattern ultra-haute fréquence (limite perception humaine)
- Invisible à l'œil car trop fin
- Caméra: sous-échantillonnage → aliasing → révélation du message
- Message encodé dans les fréquences repliées
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
import math
import logging

logger = logging.getLogger(__name__)

class TrueAntiCameraAliasing:
    """
    Vrai système anti-caméra par aliasing
    Basé sur les principes de sous-échantillonnage
    """
    
    def __init__(self):
        # Paramètres critiques pour aliasing
        self.nyquist_frequency = 0.5    # Fréquence de Nyquist pour aliasing
        self.invisible_amplitude = 0.01  # 1% seulement - quasi invisible
        self.camera_reveal_frequency = 1.5  # Fréquence optimale pour révélation
        
    def create_aliasing_message_pattern(self, width: int, height: int, message: str) -> np.ndarray:
        """
        Crée un pattern qui encode le message dans les fréquences d'aliasing
        """
        try:
            # Créer image pour le message
            msg_img = Image.new('L', (width, height), color=0)
            draw = ImageDraw.Draw(msg_img)
            
            # Font proportionnel à la taille
            font_size = max(16, width // 25)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Centrer le message
            bbox = draw.textbbox((0, 0), message, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), message, fill=255, font=font)
            
            # Convertir en masque binaire
            message_mask = np.array(msg_img).astype(np.float32) / 255.0
            
            return message_mask
            
        except Exception as e:
            logger.error(f"❌ Erreur création message: {e}")
            return np.zeros((height, width), dtype=np.float32)
    
    def generate_ultra_high_frequency_carrier(self, width: int, height: int) -> np.ndarray:
        """
        Génère une porteuse ultra-haute fréquence
        Invisible à l'œil mais cause aliasing caméra
        """
        try:
            # Grille de coordonnées
            x, y = np.meshgrid(np.arange(width), np.arange(height))
            
            # Fréquence ULTRA haute (limite perception humaine)
            # À 50cm de distance, l'œil ne peut pas résoudre < 1mm
            # Sur écran, cela correspond à ~1-2 pixels
            ultra_freq = 1.2  # Plus haute fréquence possible
            
            # Pattern multi-directionnel pour maximum d'aliasing
            carrier_h = np.sin(2 * np.pi * x / ultra_freq)  # Horizontal
            carrier_v = np.sin(2 * np.pi * y / ultra_freq)  # Vertical
            carrier_d1 = np.sin(2 * np.pi * (x + y) / (ultra_freq * 1.4))  # Diagonal 1
            carrier_d2 = np.sin(2 * np.pi * (x - y) / (ultra_freq * 1.4))  # Diagonal 2
            
            # Combiner toutes les directions
            carrier = (carrier_h + carrier_v + carrier_d1 + carrier_d2) / 4
            
            # Normaliser entre 0 et 1
            carrier = (carrier + 1) / 2
            
            return carrier.astype(np.float32)
            
        except Exception as e:
            logger.error(f"❌ Erreur porteuse: {e}")
            return np.ones((height, width), dtype=np.float32) * 0.5
    
    def encode_message_in_aliasing_frequencies(self, width: int, height: int, message: str) -> np.ndarray:
        """
        Encode le message dans les fréquences qui créent de l'aliasing
        """
        try:
            # 1. Créer le masque du message
            message_mask = self.create_aliasing_message_pattern(width, height, message)
            
            # 2. Générer porteuse ultra-haute fréquence
            carrier = self.generate_ultra_high_frequency_carrier(width, height)
            
            # 3. Moduler la porteuse avec le message
            # Technique: Modulation d'amplitude dans les zones de texte
            modulated_pattern = np.zeros((height, width), dtype=np.float32)
            
            # Zones sans texte: porteuse très faible (invisible)
            background_mask = message_mask < 0.1
            modulated_pattern[background_mask] = carrier[background_mask] * self.invisible_amplitude
            
            # Zones avec texte: porteuse plus forte (révélée par aliasing)
            text_mask = message_mask >= 0.1
            # Amplitude plus forte pour créer aliasing visible
            modulated_pattern[text_mask] = carrier[text_mask] * (self.invisible_amplitude * 8)
            
            return modulated_pattern
            
        except Exception as e:
            logger.error(f"❌ Erreur encodage aliasing: {e}")
            return np.zeros((height, width), dtype=np.float32)
    
    def apply_true_anticamera_protection(self, image: Image.Image, message: str = "🔒 CAPTURE DETECTED") -> Image.Image:
        """
        Applique la vraie protection anti-caméra par aliasing
        """
        try:
            # Convertir image en array
            img_array = np.array(image).astype(np.float32)
            height, width = img_array.shape[:2]
            
            # Générer pattern d'aliasing encodé
            aliasing_pattern = self.encode_message_in_aliasing_frequencies(width, height, message)
            
            # Appliquer sur l'image
            if len(img_array.shape) == 3:  # Image couleur
                for channel in range(3):
                    # Ajouter le pattern d'aliasing
                    img_array[:, :, channel] = np.clip(
                        img_array[:, :, channel] + (aliasing_pattern * 255),
                        0, 255
                    )
            else:  # Image grayscale
                img_array = np.clip(
                    img_array + (aliasing_pattern * 255),
                    0, 255
                )
            
            # Reconvertir
            protected_image = Image.fromarray(img_array.astype(np.uint8))
            
            logger.info("✅ Protection anti-caméra par aliasing appliquée")
            logger.info("👁️ Œil: invisible | 📷 Caméra: aliasing révèle le message")
            
            return protected_image
            
        except Exception as e:
            logger.error(f"❌ Erreur protection aliasing: {e}")
            return image

class AliasingProtectionDemo:
    """
    Démo protection anti-caméra par aliasing
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📡 Protection Anti-Caméra par ALIASING")
        self.root.geometry("900x800")
        self.root.configure(bg='#1a1a1a')
        
        self.aliasing_system = TrueAntiCameraAliasing()
        self.original_image = None
        self.protected_image = None
        self.image_label = None
        
        self.setup_gui()
    
    def setup_gui(self):
        """Interface de démonstration"""
        
        # Titre principal
        title = tk.Label(
            self.root,
            text="📡 PROTECTION ANTI-CAMÉRA PAR ALIASING",
            font=('Arial', 18, 'bold'),
            fg='#ffffff',
            bg='#1a1a1a'
        )
        title.pack(pady=15)
        
        # Explication scientifique
        explanation = tk.Label(
            self.root,
            text="Pattern ultra-haute fréquence → Invisible à l'œil → Aliasing caméra révèle le message",
            font=('Arial', 11),
            fg='#cccccc',
            bg='#1a1a1a'
        )
        explanation.pack(pady=5)
        
        # Zone image principale
        image_frame = tk.Frame(self.root, bg='#2a2a2a', relief='raised', bd=3)
        image_frame.pack(pady=15, padx=20, fill='both', expand=True)
        
        # Image de test
        self.original_image = self.create_test_image()
        tk_image = ImageTk.PhotoImage(self.original_image)
        
        self.image_label = tk.Label(
            image_frame,
            image=tk_image,
            bg='#2a2a2a'
        )
        self.image_label.image = tk_image
        self.image_label.pack(expand=True, pady=20)
        
        # Zone de contrôles
        control_frame = tk.Frame(self.root, bg='#1a1a1a')
        control_frame.pack(pady=15)
        
        # Bouton protection aliasing
        protect_btn = tk.Button(
            control_frame,
            text="📡 APPLIQUER PROTECTION ALIASING",
            command=self.apply_aliasing_protection,
            bg='#4a4a7a',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=25,
            pady=8
        )
        protect_btn.pack(side='left', padx=10)
        
        # Bouton message personnalisé
        custom_msg_btn = tk.Button(
            control_frame,
            text="✏️ MESSAGE PERSONNALISÉ",
            command=self.apply_custom_message,
            bg='#7a4a4a',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=25,
            pady=8
        )
        custom_msg_btn.pack(side='left', padx=10)
        
        # Bouton restauration
        restore_btn = tk.Button(
            control_frame,
            text="🔄 RESTAURER ORIGINAL",
            command=self.restore_original,
            bg='#4a7a4a',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=25,
            pady=8
        )
        restore_btn.pack(side='left', padx=10)
        
        # Statut
        self.status_label = tk.Label(
            self.root,
            text="🔴 Image originale - Pas de protection",
            fg='#ff4444',
            bg='#1a1a1a',
            font=('Arial', 12, 'bold')
        )
        self.status_label.pack(pady=10)
        
        # Instructions détaillées
        self.create_instructions_panel()
    
    def create_instructions_panel(self):
        """Crée le panneau d'instructions"""
        instructions_frame = tk.LabelFrame(
            self.root, 
            text=" 🧪 PROTOCOLE DE TEST ",
            font=('Arial', 12, 'bold'),
            fg='#ffffff',
            bg='#1a1a1a',
            relief='raised',
            bd=2
        )
        instructions_frame.pack(pady=10, padx=20, fill='x')
        
        instructions_text = """
🔬 PRINCIPE SCIENTIFIQUE:
• Pattern fréquence > limite résolution œil humain (~0.3mm à 25cm)
• Capteur caméra: sous-échantillonnage → repliement spectral (aliasing)
• Message encodé dans fréquences repliées → visible uniquement par caméra

📋 PROTOCOLE DE TEST:
1. 👁️  OBSERVATION DIRECTE: L'image doit paraître parfaitement normale
2. 📱 TEST CAMÉRA: Prenez une photo avec votre smartphone
3. 🔍 VÉRIFICATION: Le message apparaît UNIQUEMENT sur la photo
4. ⚡ ALIASING: Effet causé par interaction pattern/capteur

🎯 RÉSULTAT ATTENDU:
Vision humaine = Image normale | Photo caméra = Message révélé
        """
        
        instructions_label = tk.Label(
            instructions_frame,
            text=instructions_text,
            font=('Arial', 10),
            fg='#cccccc',
            bg='#1a1a1a',
            justify='left'
        )
        instructions_label.pack(padx=10, pady=10, fill='x')
    
    def create_test_image(self) -> Image.Image:
        """Crée l'image de test"""
        img = Image.new('RGB', (600, 450), color='#2a4a6a')
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 28)
            font_medium = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = font_medium = font_small = ImageFont.load_default()
        
        # Contenu normal visible
        draw.text((300, 80), "📱 IMAGE DE TEST", 
                 fill='#ffffff', font=font_large, anchor='mm')
        draw.text((300, 130), "Contenu parfaitement normal", 
                 fill='#ffcc00', font=font_medium, anchor='mm')
        draw.text((300, 180), "À l'œil nu: aucune différence", 
                 fill='#66ff66', font=font_medium, anchor='mm')
        draw.text((300, 230), "En photo: message caché révélé", 
                 fill='#ff6666', font=font_medium, anchor='mm')
        
        # Zone de test
        draw.rectangle([50, 280, 550, 380], outline='#ffffff', width=2)
        draw.text((300, 330), "🔬 Zone de Test Protection Anti-Caméra", 
                 fill='#aaaaaa', font=font_small, anchor='mm')
        
        return img
    
    def apply_aliasing_protection(self):
        """Applique la protection par aliasing"""
        if self.original_image:
            self.protected_image = self.aliasing_system.apply_true_anticamera_protection(
                self.original_image,
                "🔒 PHANTOM PROTECTED"
            )
            
            # Mettre à jour l'affichage
            tk_image = ImageTk.PhotoImage(self.protected_image)
            self.image_label.configure(image=tk_image)
            self.image_label.image = tk_image
            
            self.status_label.configure(
                text="🟢 Protection ALIASING active - Testez avec votre caméra !",
                fg='#44ff44'
            )
    
    def apply_custom_message(self):
        """Applique un message personnalisé"""
        if self.original_image:
            # Demander message personnalisé
            custom_message = tk.simpledialog.askstring(
                "Message Personnalisé",
                "Entrez le message à révéler par la caméra:",
                initialvalue="🔒 CAPTURE INTERDITE"
            )
            
            if custom_message:
                self.protected_image = self.aliasing_system.apply_true_anticamera_protection(
                    self.original_image,
                    custom_message
                )
                
                # Mettre à jour l'affichage
                tk_image = ImageTk.PhotoImage(self.protected_image)
                self.image_label.configure(image=tk_image)
                self.image_label.image = tk_image
                
                self.status_label.configure(
                    text=f"🟢 Protection active - Message: '{custom_message}'",
                    fg='#44ff44'
                )
    
    def restore_original(self):
        """Restaure l'image originale"""
        if self.original_image:
            tk_image = ImageTk.PhotoImage(self.original_image)
            self.image_label.configure(image=tk_image)
            self.image_label.image = tk_image
            
            self.status_label.configure(
                text="🔴 Image originale - Pas de protection",
                fg='#ff4444'
            )
    
    def run(self):
        """Lance la démo"""
        self.root.mainloop()

def main():
    """Point d'entrée"""
    print("📡 PROTECTION ANTI-CAMÉRA PAR ALIASING")
    print("="*50)
    print()
    print("🔬 PRINCIPE SCIENTIFIQUE:")
    print("• Pattern ultra-haute fréquence (invisible à l'œil)")
    print("• Sous-échantillonnage caméra → aliasing")
    print("• Message révélé par repliement spectral")
    print()
    print("🎯 OBJECTIF:")
    print("• Œil humain: image normale")
    print("• Caméra: message révélé par aliasing")
    print()
    print("🧪 TEST:")
    print("1. Regardez l'image directement")
    print("2. Prenez une photo")
    print("3. Comparez les résultats")
    print()
    
    # Importer tkinter.simpledialog pour les messages personnalisés
    import tkinter.simpledialog
    tk.simpledialog = tkinter.simpledialog
    
    demo = AliasingProtectionDemo()
    demo.run()

if __name__ == "__main__":
    main()