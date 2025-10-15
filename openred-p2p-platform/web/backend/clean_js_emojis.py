#!/usr/bin/env python3
"""
Remplacer tous les emojis par du texte dans le JavaScript
"""

import re

def clean_javascript():
    """Nettoyer le JavaScript de tous les emojis"""
    
    # Mapping des emojis vers du texte
    emoji_replacements = {
        '🔐': '[AUTH]',
        '❌': '[ERROR]',
        '✅': '[OK]',
        '⚠️': '[WARNING]',
        '📋': '[FILES]',
        '📄': '[FILE]', 
        '🔥': '[BURN]',
        '📤': '[UPLOAD]',
        '📥': '[RESPONSE]',
        '🌀': '[PHOENIX]',
        '💎': '[URN]',
        '⚛️': '[ATOMIC]',
        '🔑': '[KEY]',
        '👻': '[ORP]',
        '🎭': '[PROJECTION]',
        '📡': '[STREAM]',
        '🖱️': '[CLICK]',
        '🎯': '[TARGET]',
        '🚀': '[INIT]',
        '🌐': '[SERVER]'
    }
    
    # Lire le fichier web_api.py
    with open('web_api.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Compter les remplacements
    total_replacements = 0
    
    # Remplacer chaque emoji
    for emoji, replacement in emoji_replacements.items():
        count = content.count(emoji)
        if count > 0:
            content = content.replace(emoji, replacement)
            total_replacements += count
            print(f"✓ Remplacé {count}x '{emoji}' par '{replacement}'")
    
    # Sauvegarder
    with open('web_api.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n📊 Total: {total_replacements} emojis remplacés")
    print("✅ Fichier nettoyé et sauvegardé")

if __name__ == "__main__":
    clean_javascript()