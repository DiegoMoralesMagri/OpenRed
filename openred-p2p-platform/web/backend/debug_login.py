#!/usr/bin/env python3
"""Test de débogage pour l'authentification Diego"""

import requests
import json

# Configuration
API_BASE = "http://localhost:8000"
USERNAME = "Diego"
PASSWORD = "OpenRed"

def debug_login():
    """Déboguer la réponse de login"""
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(f"{API_BASE}/api/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Raw Response: {response.text}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"JSON Data: {json.dumps(data, indent=2)}")
            return data
        except json.JSONDecodeError as e:
            print(f"Erreur JSON: {e}")
    
    return None

if __name__ == "__main__":
    debug_login()