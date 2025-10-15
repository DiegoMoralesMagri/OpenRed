#!/usr/bin/env python3
"""
Test de vérification du statut du job asynchrone
"""

import requests
import sys

def check_job_status():
    """Vérifier le statut du job en cours"""
    
    print("🔍 Vérification statut job asynchrone")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    job_id = "c7e017ea-86f1-440f-a195-3f007cad3c8a"  # Job ID observé
    
    # Session avec auth
    session = requests.Session()
    login_data = {"username": "Diego", "password": "OpenRed"}
    login_response = session.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
    
    if login_response.status_code != 200:
        print("❌ Échec authentification")
        return False
    
    print("✅ Authentification réussie")
    
    # Vérifier le statut du job
    print(f"\n🔍 Vérification job {job_id}...")
    try:
        response = session.get(f"{base_url}/api/images/job-status/{job_id}", timeout=10)
        
        if response.status_code == 200:
            job = response.json()
            print(f"📊 Statut: {job['status']}")
            print(f"📈 Progrès: {job['progress']}%")
            print(f"📄 Fichier: {job['filename']}")
            print(f"⏰ Créé: {job['created_at']}")
            print(f"🏁 Démarré: {job.get('started_at', 'N/A')}")
            
            if job.get('error'):
                print(f"❌ Erreur: {job['error']}")
            
            if job.get('result'):
                print(f"✅ Résultat: {job['result']}")
                
            return True
            
        else:
            print(f"❌ Erreur récupération statut: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

    # Vérifier aussi mes jobs
    print(f"\n📋 Tous mes jobs...")
    try:
        response = session.get(f"{base_url}/api/images/my-jobs", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            print(f"📊 Nombre de jobs: {len(jobs)}")
            
            for job in jobs[-3:]:  # Les 3 derniers
                print(f"   Job {job['job_id'][:8]}: {job['status']} ({job['progress']}%)")
                
        else:
            print(f"❌ Erreur récupération jobs: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Exception jobs: {e}")

if __name__ == "__main__":
    check_job_status()