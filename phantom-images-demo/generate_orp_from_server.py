import requests
from pathlib import Path
from orp_format import OrpFormat

# Dossier de sortie
binary_orp_dir = Path('orp-files/BinaryPhantom')
binary_orp_dir.mkdir(exist_ok=True)

# Adresse du serveur PHANTOM
server_url = 'http://localhost:8001'
phantoms_api = f'{server_url}/phantoms'

# Récupérer la liste des phantoms
resp = requests.get(phantoms_api)
if resp.status_code != 200:
    print(f"❌ Impossible de récupérer la liste des phantoms: {resp.text}")
    exit(1)

phantoms = resp.json().get('phantoms', [])
if not phantoms:
    print("❌ Aucun phantom disponible sur le serveur.")
    exit(1)

for phantom in phantoms:
    phantom_id = phantom['id']
    phantom_name = phantom['name']
    phantom_size = (400, 300)  # À adapter si possible
    mime_type = phantom.get('mime_type', 'image/jpeg')
    server_url_ws = server_url.replace('http', 'ws')
    orp = OrpFormat.create_phantom_file(
        phantom_id=phantom_id,
        phantom_name=phantom_name,
        server_url=server_url_ws,
        phantom_size=phantom_size,
        mime_type=mime_type
    )
    out_path = binary_orp_dir / f"{phantom_id}.orp"
    orp.save_to_file(out_path)
    print(f"✅ .orp généré: {out_path}")

print("Opération terminée.")
