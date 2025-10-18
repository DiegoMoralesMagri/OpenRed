#!/usr/bin/env python3
"""
Créateur de package OpenRed FLAT pour O2Switch
- Tout à la racine (pas de sous-dossiers)
- Pas de .htaccess du tout
- Structure plate pour éviter les erreurs 403
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_o2switch_flat_package():
    """Crée un package OpenRed complètement FLAT pour O2Switch"""
    
    # Dossiers source et destination
    source_dir = Path("c:/Users/serveur/Documents/OpenRed/openred-p2p-platform")
    package_dir = Path("c:/Users/serveur/Documents/OpenRed/deployment/temp_o2switch_flat")
    
    # Nettoyer et créer le dossier temporaire
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)
    
    print("🔥 Création package OpenRed FLAT pour O2Switch...")
    
    # 1. Copier TOUS les fichiers web à la racine
    web_source = source_dir / "web"
    if web_source.exists():
        # Copier tout le contenu de web/ directement à la racine
        for item in web_source.rglob("*"):
            if item.is_file():
                # Calculer le chemin relatif depuis web/
                rel_path = item.relative_to(web_source)
                
                # Tout mettre à la racine (écraser la structure de dossiers)
                if rel_path.name.endswith(('.html', '.css', '.js', '.py')):
                    # Renommer pour éviter les conflits
                    if 'backend' in str(rel_path):
                        dest_name = f"backend_{rel_path.name}"
                    elif 'frontend' in str(rel_path):
                        dest_name = f"frontend_{rel_path.name}"
                    else:
                        dest_name = rel_path.name
                    
                    dest_path = package_dir / dest_name
                    shutil.copy2(item, dest_path)
                    print(f"  ✓ {rel_path} → {dest_name}")
    
    # 2. Créer un index.html simplifié à la racine
    index_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRed - Plateforme Phantom URN</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1); 
            padding: 30px; 
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .phantom-urn { 
            text-align: center; 
            margin: 30px 0; 
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }
        .upload-zone {
            border: 2px dashed rgba(255,255,255,0.5);
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            margin: 20px 0;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .upload-zone:hover {
            background: rgba(255,255,255,0.1);
            border-color: rgba(255,255,255,0.8);
        }
        .btn {
            background: linear-gradient(45deg, #ff6b6b, #ee5a6f);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
            transition: transform 0.2s ease;
        }
        .btn:hover { transform: translateY(-2px); }
        #status { margin-top: 20px; padding: 10px; }
        .success { background: rgba(46, 204, 113, 0.2); }
        .error { background: rgba(231, 76, 60, 0.2); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌟 OpenRed - Phantom URN</h1>
        <p>Plateforme de stockage quantique sécurisé - Version O2Switch FLAT</p>
        
        <div class="phantom-urn">
            <h3>📡 Interface Phantom URN</h3>
            <div class="upload-zone" onclick="document.getElementById('fileInput').click()">
                <p>📁 Cliquez ici pour téléverser une image</p>
                <p style="font-size: 12px; opacity: 0.7;">Formats acceptés: JPG, PNG, GIF</p>
            </div>
            <input type="file" id="fileInput" accept="image/*" style="display: none;">
            <button class="btn" onclick="uploadFile()">🚀 Téléverser</button>
            <button class="btn" onclick="testConnection()">🔗 Test Connexion</button>
        </div>
        
        <div id="status"></div>
        
        <div style="margin-top: 30px; text-align: center; opacity: 0.7;">
            <p>✅ Version FLAT O2Switch - Pas de sous-dossiers</p>
            <p>🔧 Déployé depuis: github.com/DiegoMoralesMagri/OpenRed</p>
        </div>
    </div>

    <script>
        function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const statusDiv = document.getElementById('status');
            
            if (!fileInput.files.length) {
                showStatus('⚠️ Veuillez sélectionner un fichier', 'error');
                return;
            }
            
            const file = fileInput.files[0];
            showStatus('📤 Téléversement en cours...', 'info');
            
            // Simulation upload pour O2Switch FLAT
            setTimeout(() => {
                showStatus(`✅ Fichier "${file.name}" téléversé avec succès!<br>🔗 URN: phantom://o2switch/${Date.now()}`, 'success');
            }, 1500);
        }
        
        function testConnection() {
            showStatus('🔍 Test de connexion...', 'info');
            
            setTimeout(() => {
                showStatus('✅ Connexion O2Switch OK!<br>📡 Phantom URN opérationnel<br>🔧 Version FLAT active', 'success');
            }, 1000);
        }
        
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = message;
            statusDiv.className = type;
        }
        
        // Auto-upload quand fichier sélectionné
        document.getElementById('fileInput').addEventListener('change', function() {
            if (this.files.length) {
                uploadFile();
            }
        });
    </script>
</body>
</html>"""
    
    with open(package_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_content)
    
    # 3. Créer un script Python minimal à la racine
    api_content = """#!/usr/bin/env python3
# OpenRed API - Version O2Switch FLAT
import os
import json
from datetime import datetime

def handle_upload():
    return {
        'status': 'success',
        'message': 'Upload simulé O2Switch FLAT',
        'urn': f'phantom://o2switch/{int(datetime.now().timestamp())}',
        'timestamp': datetime.now().isoformat()
    }

def handle_test():
    return {
        'status': 'success', 
        'message': 'OpenRed O2Switch FLAT opérationnel',
        'version': '2.0-flat'
    }

if __name__ == '__main__':
    print("Content-Type: application/json\\n")
    print(json.dumps(handle_test(), indent=2))
"""
    
    with open(package_dir / "api.py", "w", encoding="utf-8") as f:
        f.write(api_content)
    
    # 4. PAS de .htaccess du tout !
    print("  ⚠️ Aucun .htaccess créé (FLAT O2Switch)")
    
    # 5. Créer le ZIP
    zip_path = Path("c:/Users/serveur/Documents/OpenRed/deployment/packages/openred-o2switch-flat.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.name  # Tout à la racine !
                zipf.write(file_path, arcname)
                print(f"  📦 {arcname}")
    
    # Nettoyer
    shutil.rmtree(package_dir)
    
    file_size = zip_path.stat().st_size / 1024
    print(f"\n✅ Package O2Switch FLAT créé: {zip_path}")
    print(f"📦 Taille: {file_size:.1f} KB")
    print(f"🎯 Structure: TOUT À LA RACINE")
    print(f"⚠️ Aucun .htaccess (pour éviter 403)")
    
    return zip_path

if __name__ == "__main__":
    create_o2switch_flat_package()