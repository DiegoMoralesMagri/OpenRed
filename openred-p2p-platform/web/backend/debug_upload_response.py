#!/usr/bin/env python3
"""Debug de la réponse d'upload"""

import requests
import io
from PIL import Image
import json

# Configuration
API_BASE = "http://localhost:8000"
USERNAME = "Diego"
PASSWORD = "OpenRed"

def test_upload_debug():
    # Login
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(f"{API_BASE}/api/auth/login", json=login_data)
    token = response.json().get('token')
    
    # Upload
    img = Image.new('RGB', (50, 50), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("debug.png", img_bytes.getvalue(), "image/png")}
    data = {"title": "Debug", "description": "Test"}
    
    response = requests.post(f"{API_BASE}/api/images/upload", headers=headers, files=files, data=data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_upload_debug()