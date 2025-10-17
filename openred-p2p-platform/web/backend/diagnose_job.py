#!/usr/bin/env python3
"""
Diagnostic approfondi du job bloqué
"""

import requests
import time
import sys

def diagnose_stuck_job():
    """Diagnostiquer pourquoi le job est bloqué"""
    
    print("🔧 Diagnostic job bloqué")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    job_id = "c7e017ea-86f1-440f-a195-3f007cad3c8a"
    
    # Session avec auth
    session = requests.Session()
    login_data = {"username": "Diego", "password": "OpenRed"}
    session.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
    
    # Vérifier plusieurs fois le statut
    for i in range(5):
        print(f"\n🔍 Vérification #{i+1}...")
        try:
            response = session.get(f"{base_url}/api/images/job-status/{job_id}", timeout=10)
            
            if response.status_code == 200:
                job = response.json()
                
                # Calculer temps écoulé
                now = time.time()
                elapsed = now - job['created_at']
                processing_time = now - job.get('started_at', job['created_at'])
                
                print(f"   📊 Statut: {job['status']}")
                print(f"   📈 Progrès: {job['progress']}%")
                print(f"   ⏰ Temps total: {elapsed:.1f}s")
                print(f"   🔄 Temps traitement: {processing_time:.1f}s")
                
                # Si bloqué depuis plus de 5 minutes, c'est suspect
                if processing_time > 300 and job['progress'] == 50:
                    print("   🚨 ALERTE: Job probablement bloqué !")
                    
                    # Suggestion de solution
                    print("\n💡 Solutions possibles:")
                    print("   1. Redémarrer le serveur web_api.py")
                    print("   2. Le système Enhanced URN prend parfois plus de temps")
                    print("   3. Vérifier les logs du serveur")
                    
                    return False
                    
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
        
        if i < 4:  # Pas de pause après la dernière itération
            time.sleep(2)
    
    print("\n🎯 Conseil: Si le job reste bloqué, essayez un nouveau upload")
    print("   Le système asynchrone est fonctionnel même si ce job est coincé.")
    
    return True

if __name__ == "__main__":
    diagnose_stuck_job()