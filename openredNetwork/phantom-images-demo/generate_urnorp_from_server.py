import os
import json
from pathlib import Path

# Dossier des urns
urns_dir = Path('urns')
urn_orp_dir = Path('orp-files/UrnPhantom')
urn_orp_dir.mkdir(exist_ok=True)

for urn_folder in urns_dir.iterdir():
    if urn_folder.is_dir():
        urn_config_path = urn_folder / 'urn_config.json'
        if urn_config_path.exists():
            with open(urn_config_path, 'r') as f:
                urn_config = json.load(f)
            phantom_id = urn_folder.name
            phantom_name = f"UrnPhantom {phantom_id}"
            server_url = "http://localhost:9300"  # À adapter si besoin
            phantom_size = urn_config.get('image_dimensions', [400, 300])
            mime_type = 'image/jpg'  # À adapter si besoin
            # Structure JSON URN
            urn_orp_json = {
                "format_version": "1.0.0",
                "phantom_id": phantom_id,
                "urn_id": phantom_id,
                "phantom_name": phantom_name,
                "mime_type": mime_type,
                "dimensions": {
                    "width": phantom_size[0],
                    "height": phantom_size[1]
                },
                "created_at": str(urn_config.get('creation_time', '')),
                "file_id": phantom_id,
                "description": f"OpenRed Phantom: {phantom_name}",
                "urn_config": urn_config,
                "urn_dir": str(urn_folder),
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
                    "checksum": phantom_id,
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
            print(f"❌ urn_config.json introuvable dans {urn_folder}")
print("Opération terminée.")
