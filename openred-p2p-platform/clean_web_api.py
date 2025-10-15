import re

# Lire le fichier
with open('web/backend/web_api.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
in_html_section = False

for i, line in enumerate(lines):
    # Détecter le début d'une section HTML/CSS problématique
    if any(keyword in line for keyword in ['body {', '<html>', '<head>', '<style>', 'font-family:', 'background:', '.container']):
        in_html_section = True
        continue
    
    # Détecter la fin (quand on arrive à une vraie fonction Python)
    if in_html_section and line.strip().startswith('@app.'):
        in_html_section = False
        new_lines.append(line)
        continue
    
    # Ignorer les lignes dans la section HTML
    if in_html_section:
        continue
    
    # Garder les lignes normales
    new_lines.append(line)

# Sauvegarder le fichier nettoyé
new_content = '\n'.join(new_lines)
with open('web/backend/web_api.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'Fichier nettoyé! Supprimé {len(lines) - len(new_lines)} lignes de HTML/CSS')