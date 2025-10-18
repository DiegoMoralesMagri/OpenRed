
import os
import json
from pathlib import Path
from phantom_urn_system import PhantomAshSystem
from orp_format import OrpFormat

# Dossiers
shared_images = Path('shared-images')
binary_orp_dir = Path('orp-files/BinaryPhantom')
urn_orp_dir = Path('orp-files/UrnPhantom')
urns_dir = Path('urns')

# Lister les images
images = sorted([f for f in shared_images.iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']])

if len(images) < 6:
    print(f"❌ Il faut au moins 6 images dans {shared_images}")
    exit(1)

# 3 BinaryPhantom
for i, img_path in enumerate(images[:3]):
    phantom_id = f"phantom_{img_path.stem}"
    phantom_name = f"Phantom {img_path.stem}"
    server_url = "ws://localhost:8001"  # À adapter si besoin
    phantom_size = (400, 300)  # À adapter si besoin
    mime_type = img_path.suffix.replace('.', 'image/')
    orp = OrpFormat.create_phantom_file(
        phantom_id=phantom_id,
        phantom_name=phantom_name,
        server_url=server_url,
        phantom_size=phantom_size,
        mime_type=mime_type
    )
    out_path = binary_orp_dir / f"{phantom_id}.orp"
    orp.save_to_file(out_path)
    print(f"✅ .orp créé: {out_path}")

# 3 UrnPhantom
ash_system = PhantomAshSystem(urns_dir)
for i, img_path in enumerate(images[3:6]):

    urn_id = f"urn_{img_path.stem}"
    authorized_node = "urn_node_demo"
    burn_result = ash_system.create_urn(str(img_path), authorized_node, urn_id=urn_id)
    urn_dir = urns_dir / urn_id
    urn_json_path = urn_dir / "urn_config.json"

    # Générer le .orp pour l'urne au format JSON
    if urn_json_path.exists():
        with open(urn_json_path, 'r') as f:
            urn_config = json.load(f)

        phantom_id = urn_id
        phantom_name = f"UrnPhantom {img_path.stem}"
        server_url = "http://localhost:9300"  # À adapter si besoin
        phantom_size = urn_config.get('image_dimensions', [400, 300])
        mime_type = img_path.suffix.replace('.', 'image/')

        # Structure JSON URN
        urn_orp_json = {
            "format_version": "1.0.0",
            "phantom_id": phantom_id,
            "phantom_name": phantom_name,
            "mime_type": mime_type,
            "dimensions": {
                "width": phantom_size[0],
                "height": phantom_size[1]
            },
            "created_at": str(urn_config.get('creation_time', '')),
            "file_id": str(burn_result.get('urn_id', phantom_id)),
            "description": f"OpenRed Phantom: {phantom_name}",
            "urn_config": urn_config,
            "urn_dir": str(urn_dir),
            "burn_result": burn_result,
            "access_data": {
                "server_url": server_url,
                "phantom_endpoint": f"/phantom/{phantom_id}",
                "websocket_url": server_url.replace("http", "ws") + "/ws",
                "fallback_urls": [],
                "access_method": "http_primary"
            },
            "security_data": {
                "access_token": None,
                "permissions": {
                    "view": True,
                    "download": False,
                    "share": True,
                    "expires_at": None
                },
                "checksum": burn_result.get('urn_id', phantom_id),
                "requires_server": True,
                "anti_capture": True,
                "urn_type": "JSON_URN"
            }
        }

        out_path = urn_orp_dir / f"{phantom_id}.orp"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(urn_orp_json, f, indent=2)
        print(f"✅ .orp URN JSON créé: {out_path}")
    else:
        print(f"❌ urn_config.json introuvable pour {urn_id}")

print("Opération terminée.")
