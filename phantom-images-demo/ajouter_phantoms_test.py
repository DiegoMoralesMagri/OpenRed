#!/usr/bin/env python3
"""
Ajout de phantoms de test au serveur
===================================
Ajoute quelques phantoms avec les mêmes IDs que les fichiers .orp existants
"""

import requests
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import json

def creer_image_test(texte: str, couleur: str = 'blue', taille: tuple = (400, 300)):
    """Crée une image de test avec du texte"""
    img = Image.new('RGB', taille, color=couleur)
    draw = ImageDraw.Draw(img)
    
    # Essayer d'utiliser une police, sinon utiliser la police par défaut
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Centrer le texte
    bbox = draw.textbbox((0, 0), texte, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (taille[0] - text_width) // 2
    y = (taille[1] - text_height) // 2
    
    draw.text((x, y), texte, fill='white', font=font)
    
    # Convertir en base64
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    return base64.b64encode(img_bytes.getvalue()).decode()

def ajouter_phantom(phantom_id: str, nom: str, image_data: str, serveur_url: str = "http://localhost:8001"):
    """Ajoute un phantom au serveur"""
    try:
        response = requests.post(f'{serveur_url}/phantom', json={
            'id': phantom_id,
            'name': nom,
            'data': image_data,
            'mime_type': 'image/jpeg'
        }, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Phantom '{nom}' ajouté avec succès (ID: {phantom_id})")
            return True
        else:
            print(f"❌ Erreur ajout '{nom}': {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur connexion pour '{nom}': {e}")
        return False

def main():
    """Ajoute les phantoms de test correspondant aux fichiers .orp"""
    print("🖼️ === AJOUT DE PHANTOMS DE TEST ===\n")
    
    # Vérifier que le serveur répond
    try:
        response = requests.get("http://localhost:8001/phantoms", timeout=5)
        print(f"📡 Serveur accessible - {len(response.json().get('phantoms', []))} phantoms actuels")
    except Exception as e:
        print(f"❌ Serveur inaccessible: {e}")
        print("💡 Assurez-vous que le serveur phantom est démarré")
        return
    
    # Phantoms correspondant aux fichiers .orp existants
    phantoms_a_creer = [
        {
            'id': 'phantom_ocean_demo',  # ID correspondant à ocean_virtuel.orp
            'nom': 'Océan Virtuel',
            'couleur': 'darkblue',
            'texte': 'OCÉAN\nVIRTUEL'
        },
        {
            'id': 'phantom_cosmos_demo',  # ID correspondant à cosmos_phantom.orp
            'nom': 'Cosmos Phantom',
            'couleur': 'darkviolet',
            'texte': 'COSMOS\nPHANTOM'
        },
        {
            'id': 'phantom_nature_demo',  # ID correspondant à nature_pixel.orp
            'nom': 'Nature Pixel',
            'couleur': 'darkgreen',
            'texte': 'NATURE\nPIXEL'
        }
    ]
    
    # Phantoms additionnels pour la galerie
    phantoms_bonus = [
        {
            'id': 'phantom_test_1',
            'nom': 'Test Rouge',
            'couleur': 'darkred',
            'texte': 'TEST\nROUGE'
        },
        {
            'id': 'phantom_test_2',
            'nom': 'Test Orange',
            'couleur': 'darkorange',
            'texte': 'TEST\nORANGE'
        }
    ]
    
    tous_phantoms = phantoms_a_creer + phantoms_bonus
    
    print(f"📸 Création de {len(tous_phantoms)} phantoms...\n")
    
    succes = 0
    for phantom_info in tous_phantoms:
        # Créer image
        image_data = creer_image_test(
            phantom_info['texte'], 
            phantom_info['couleur']
        )
        
        # Ajouter au serveur
        if ajouter_phantom(
            phantom_info['id'], 
            phantom_info['nom'], 
            image_data
        ):
            succes += 1
    
    print(f"\n🎉 === RÉSULTAT ===")
    print(f"✅ {succes}/{len(tous_phantoms)} phantoms ajoutés avec succès")
    
    if succes > 0:
        print(f"\n🧪 TESTS POSSIBLES:")
        print(f"   1. Relancer la galerie : python virtual_screen_gallery.py")
        print(f"   2. Tester fichier .orp : python orp_viewer.py fichiers-orp-demo/ocean_virtuel.orp")
        print(f"   3. Double-clic sur fichier .orp dans l'explorateur")
    else:
        print(f"\n❌ Aucun phantom ajouté - vérifiez le serveur")

if __name__ == "__main__":
    main()