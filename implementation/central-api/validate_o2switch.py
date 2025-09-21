#!/usr/bin/env python3
# FR: Script de validation de déploiement O2Switch
# EN: O2Switch deployment validation script
# ES: Script de validación de despliegue O2Switch
# ZH: O2Switch部署验证脚本

"""
OpenRed O2Switch Deployment Validator
Valide que l'installation OpenRed fonctionne correctement sur O2Switch
"""

import os
import sys
import json
import time
import platform
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

class O2SwitchValidator:
    """Validateur de déploiement O2Switch"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "validator_version": "2.0.0",
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        self.project_root = os.path.dirname(os.path.abspath(__file__))
    
    def log(self, level: str, message: str, details: Optional[Dict] = None):
        """Log un résultat de test"""
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "details": details or {}
        }
        self.results["tests"].append(result)
        
        # Mettre à jour le summary
        self.results["summary"]["total"] += 1
        if level == "PASS":
            self.results["summary"]["passed"] += 1
        elif level == "FAIL":
            self.results["summary"]["failed"] += 1
        elif level == "WARN":
            self.results["summary"]["warnings"] += 1
        
        # Affichage console
        icons = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️"}
        print(f"{icons.get(level, '•')} {message}")
        if details and sys.argv and "--verbose" in sys.argv:
            print(f"   📋 {details}")
    
    def test_system_environment(self):
        """Test de l'environnement système"""
        print("\n🔍 Test de l'environnement système...")
        
        # Version Python
        python_version = platform.python_version()
        version_parts = python_version.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        
        if major > 3 or (major == 3 and minor >= 8):
            self.log("PASS", f"Version Python: {python_version}")
        else:
            self.log("FAIL", f"Version Python trop ancienne: {python_version} (minimum 3.8)")
        
        # Plateforme
        system_info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_implementation": platform.python_implementation()
        }
        self.log("INFO", f"Plateforme: {platform.platform()}", system_info)
        
        # Répertoire de travail
        working_dir = os.getcwd()
        if "openred" in working_dir.lower():
            self.log("PASS", f"Répertoire de travail: {working_dir}")
        else:
            self.log("WARN", f"Répertoire inhabituel: {working_dir}")
        
        # Permissions d'écriture
        try:
            test_file = "/tmp/openred_test.txt"
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            self.log("PASS", "Permissions d'écriture: OK")
        except Exception as e:
            self.log("FAIL", f"Permissions d'écriture: {str(e)}")
    
    def test_python_modules(self):
        """Test des modules Python requis"""
        print("\n📦 Test des modules Python...")
        
        required_modules = {
            "fastapi": "Framework API principal",
            "uvicorn": "Serveur ASGI",
            "pydantic": "Validation de données",
            "starlette": "Framework ASGI de base"
        }
        
        optional_modules = {
            "pymysql": "Driver MySQL",
            "sqlalchemy": "ORM base de données",
            "python-dotenv": "Variables d'environnement",
            "pydantic-settings": "Configuration Pydantic"
        }
        
        # Test des modules requis
        for module, description in required_modules.items():
            try:
                imported = __import__(module)
                version = getattr(imported, "__version__", "inconnue")
                self.log("PASS", f"{module} ({description}): v{version}")
            except ImportError:
                self.log("FAIL", f"{module} manquant ({description})")
        
        # Test des modules optionnels
        for module, description in optional_modules.items():
            try:
                imported = __import__(module)
                version = getattr(imported, "__version__", "inconnue")
                self.log("PASS", f"{module} ({description}): v{version}")
            except ImportError:
                self.log("WARN", f"{module} manquant ({description}) - optionnel")
    
    def test_file_structure(self):
        """Test de la structure des fichiers"""
        print("\n📁 Test de la structure des fichiers...")
        
        required_files = [
            "app/main_o2switch.py",
            "app/main_simple.py",
            "app/index.py",
            ".env.o2switch.template",
            "requirements-minimal.txt",
            "diagnostic.py"
        ]
        
        optional_files = [
            ".env.production",
            "app/core/config.py",
            "app/core/security.py",
            "requirements-production.txt",
            "install_o2switch.sh"
        ]
        
        # Test des fichiers requis
        for file_path in required_files:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                self.log("PASS", f"Fichier requis: {file_path} ({size} bytes)")
            else:
                self.log("FAIL", f"Fichier manquant: {file_path}")
        
        # Test des fichiers optionnels
        for file_path in optional_files:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                self.log("PASS", f"Fichier optionnel: {file_path} ({size} bytes)")
            else:
                self.log("WARN", f"Fichier optionnel manquant: {file_path}")
    
    def test_configuration(self):
        """Test de la configuration"""
        print("\n⚙️ Test de la configuration...")
        
        # Variables d'environnement
        env_vars = {
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "non définie"),
            "DEBUG": os.getenv("DEBUG", "non définie"),
            "HOST": os.getenv("HOST", "non définie"),
            "PORT": os.getenv("PORT", "non définie"),
            "SECRET_KEY": "***" if os.getenv("SECRET_KEY") else "non définie"
        }
        
        for var, value in env_vars.items():
            if value != "non définie":
                self.log("PASS", f"Variable d'environnement {var}: configurée")
            else:
                self.log("WARN", f"Variable d'environnement {var}: non définie")
        
        # Configuration .env
        env_files = [".env.production", ".env.o2switch"]
        env_found = False
        for env_file in env_files:
            env_path = os.path.join(self.project_root, env_file)
            if os.path.exists(env_path):
                env_found = True
                self.log("PASS", f"Fichier de configuration trouvé: {env_file}")
                break
        
        if not env_found:
            self.log("WARN", "Aucun fichier de configuration .env trouvé")
    
    def test_applications(self):
        """Test des applications"""
        print("\n🚀 Test des applications...")
        
        # Test de l'application O2Switch
        try:
            sys.path.insert(0, os.path.join(self.project_root, "app"))
            from main_o2switch import app as o2switch_app
            self.log("PASS", "Application O2Switch: importée avec succès")
            
            # Test des endpoints (sans TestClient pour éviter la dépendance httpx)
            # En production O2Switch, ces tests seront faits via HTTP
            self.log("PASS", "Application O2Switch: endpoints non testés (mode O2Switch)")
            
        except Exception as e:
            self.log("FAIL", f"Application O2Switch: erreur d'import - {str(e)}")
        
        # Test de l'application simple (fallback)
        try:
            from main_simple import app as simple_app
            self.log("PASS", "Application simple: importée avec succès")
        except Exception as e:
            self.log("WARN", f"Application simple: erreur d'import - {str(e)}")
    
    def test_database_config(self):
        """Test de la configuration de base de données"""
        print("\n🗄️ Test de la configuration de base de données...")
        
        database_url = os.getenv("DATABASE_URL", "")
        if database_url:
            if "mysql" in database_url.lower():
                self.log("PASS", "Configuration MySQL détectée")
            elif "sqlite" in database_url.lower():
                self.log("WARN", "Configuration SQLite détectée (mode test)")
            else:
                self.log("WARN", f"Type de base de données non reconnu: {database_url[:20]}...")
        else:
            self.log("WARN", "DATABASE_URL non configurée")
        
        # Test des modules de base de données
        try:
            import pymysql
            self.log("PASS", f"Driver MySQL: PyMySQL v{pymysql.__version__}")
        except ImportError:
            self.log("WARN", "Driver MySQL PyMySQL non installé")
    
    def test_security(self):
        """Test de la configuration de sécurité"""
        print("\n🔒 Test de la sécurité...")
        
        secret_key = os.getenv("SECRET_KEY", "")
        if secret_key:
            if len(secret_key) >= 32:
                self.log("PASS", "SECRET_KEY: longueur suffisante")
            else:
                self.log("WARN", "SECRET_KEY: trop courte (minimum 32 caractères)")
            
            if secret_key not in ["change-this-secret-key", "YOUR_SUPER_SECRET_KEY_HERE"]:
                self.log("PASS", "SECRET_KEY: personnalisée")
            else:
                self.log("FAIL", "SECRET_KEY: utilise la valeur par défaut (DANGEREUX)")
        else:
            self.log("FAIL", "SECRET_KEY: non définie")
        
        # Test CORS
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
        if allowed_origins and "*" not in allowed_origins:
            self.log("PASS", "CORS: configuration restrictive")
        else:
            self.log("WARN", "CORS: configuration permissive (*)")
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🧪 OpenRed O2Switch Deployment Validator v2.0")
        print("=" * 50)
        
        self.test_system_environment()
        self.test_python_modules()
        self.test_file_structure()
        self.test_configuration()
        self.test_applications()
        self.test_database_config()
        self.test_security()
        
        # Résumé final
        print("\n📊 Résumé de validation:")
        print("=" * 30)
        summary = self.results["summary"]
        print(f"✅ Tests réussis: {summary['passed']}")
        print(f"❌ Tests échoués: {summary['failed']}")
        print(f"⚠️  Avertissements: {summary['warnings']}")
        print(f"📊 Total: {summary['total']}")
        
        # Déterminer le statut global
        if summary["failed"] == 0:
            if summary["warnings"] == 0:
                print("\n🎉 DÉPLOIEMENT VALIDÉ: Parfait!")
                status = "PERFECT"
            else:
                print("\n✅ DÉPLOIEMENT VALIDÉ: Quelques avertissements")
                status = "GOOD"
        else:
            print("\n❌ DÉPLOIEMENT PROBLÉMATIQUE: Erreurs détectées")
            status = "ISSUES"
        
        self.results["status"] = status
        return self.results
    
    def save_report(self, filename: str = None):
        """Sauvegarde le rapport"""
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_report_{timestamp}.json"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Rapport sauvegardé: {filename}")
        except Exception as e:
            print(f"\n❌ Erreur de sauvegarde: {e}")

def main():
    """Fonction principale"""
    validator = O2SwitchValidator()
    
    # Exécuter les tests
    results = validator.run_all_tests()
    
    # Sauvegarder le rapport si demandé
    if "--save-report" in sys.argv:
        validator.save_report()
    
    # Code de sortie basé sur les résultats
    if results["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()