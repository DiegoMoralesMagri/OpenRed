#!/usr/bin/env python3
"""
Système de traitement asynchrone pour les URN Phantom
"""

import asyncio
import uuid
import time
import threading
from typing import Dict, Optional
from enum import Enum
import json
import os

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class PhantomJob:
    def __init__(self, job_id: str, user_id: str, filename: str, file_path: str):
        self.job_id = job_id
        self.user_id = user_id
        self.filename = filename
        self.file_path = file_path
        self.status = JobStatus.PENDING
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.progress = 0
        self.result = None
        self.error = None
        
    def to_dict(self):
        return {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "filename": self.filename,
            "status": self.status.value,
            "progress": self.progress,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error
        }

class AsyncPhantomProcessor:
    def __init__(self, phantom_urn_system):
        self.phantom_urn_system = phantom_urn_system
        self.jobs: Dict[str, PhantomJob] = {}
        self.processing_queue = asyncio.Queue()
        self.is_running = False
        self.worker_task = None
        
    def submit_job(self, user_id: str, filename: str, file_path: str) -> str:
        """Soumettre un job de traitement URN"""
        job_id = str(uuid.uuid4())
        job = PhantomJob(job_id, user_id, filename, file_path)
        self.jobs[job_id] = job
        
        # Ajouter à la queue
        asyncio.create_task(self.processing_queue.put(job))
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Récupérer le statut d'un job"""
        job = self.jobs.get(job_id)
        return job.to_dict() if job else None
    
    def get_user_jobs(self, user_id: str) -> list:
        """Récupérer tous les jobs d'un utilisateur"""
        return [job.to_dict() for job in self.jobs.values() if job.user_id == user_id]
    
    async def start_worker(self):
        """Démarrer le worker de traitement en arrière-plan"""
        if self.is_running:
            return
            
        self.is_running = True
        self.worker_task = asyncio.create_task(self._process_jobs())
        print("🔥 AsyncPhantomProcessor worker started")
    
    async def stop_worker(self):
        """Arrêter le worker"""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        print("🛑 AsyncPhantomProcessor worker stopped")
    
    async def _process_jobs(self):
        """Worker qui traite les jobs en arrière-plan"""
        while self.is_running:
            try:
                # Attendre un job (avec timeout pour vérifier is_running)
                job = await asyncio.wait_for(self.processing_queue.get(), timeout=1.0)
                
                # Traiter le job
                await self._process_single_job(job)
                
            except asyncio.TimeoutError:
                # Timeout normal, continuer la boucle
                continue
            except Exception as e:
                print(f"❌ Erreur worker: {e}")
                await asyncio.sleep(1)
    
    async def _process_single_job(self, job: PhantomJob):
        """Traiter un job individuel"""
        try:
            print(f"🔥 Début traitement job {job.job_id}: {job.filename}")
            
            # Marquer comme en cours
            job.status = JobStatus.PROCESSING
            job.started_at = time.time()
            job.progress = 10
            
            # Simulation des étapes de traitement
            await asyncio.sleep(0.5)  # Lecture image
            job.progress = 30
            
            # Traitement URN (dans un thread pour éviter de bloquer)
            def burn_sync():
                return self.phantom_urn_system.burn_image_to_phantom_urn(
                    image_path=job.file_path,
                    phantom_name=job.filename,
                    authorized_node=job.user_id
                )
            
            # Exécuter le traitement lourd dans un thread
            loop = asyncio.get_event_loop()
            job.progress = 50
            
            burn_result = await loop.run_in_executor(None, burn_sync)
            job.progress = 90
            
            # Finaliser
            job.status = JobStatus.COMPLETED
            job.completed_at = time.time()
            job.progress = 100
            job.result = {
                "phantom_id": burn_result["phantom_id"],
                "total_fragments": burn_result["total_fragments"],
                "phoenix_key": burn_result.get("phoenix_key", ""),
                "schrodinger_matrix": burn_result.get("schrodinger_matrix", "encrypted_quantum_state"),
                "nck_enabled": burn_result.get("nck_enabled", True),
                "continuous_verification": burn_result.get("continuous_verification", True),
                "system_type": "enhanced_phantom_urn",
                "streaming_info": {
                    "phoenix_streaming": f"http://localhost:8002/phantom/{burn_result['phantom_id']}",
                    "quantum_state": "Schrödinger Phoenix activé",
                    "security": "NCK avec rotation automatique"
                }
            }
            
            print(f"✅ Job {job.job_id} terminé: {burn_result['total_fragments']} fragments")
            
        except Exception as e:
            print(f"❌ Erreur job {job.job_id}: {e}")
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = time.time()
        
        finally:
            # Nettoyer le fichier temporaire
            try:
                if os.path.exists(job.file_path):
                    os.unlink(job.file_path)
            except:
                pass

# Instance globale
async_processor = None

def initialize_async_processor(phantom_urn_system):
    """Initialiser le processeur asynchrone"""
    global async_processor
    async_processor = AsyncPhantomProcessor(phantom_urn_system)
    return async_processor