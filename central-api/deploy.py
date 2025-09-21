#!/usr/bin/env python3
"""
Utilitaire de Déploiement Automatisé - OpenRed Central API v2.0
Script pour automatiser le déploiement en production
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
import argparse
from datetime import datetime


class DeploymentManager:
    """Gestionnaire de déploiement automatisé"""
    
    def __init__(self, environment="production"):
        self.environment = environment
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / f"config_{environment}.json"
        self.backup_dir = self.project_root / "backups"
        
    def load_config(self):
        """Charger la configuration de déploiement"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Configuration par défaut
            default_config = {
                "database": {
                    "type": "sqlite",
                    "path": "openred_prod.db"
                },
                "server": {
                    "host": "0.0.0.0",
                    "port": 8000,
                    "workers": 4
                },
                "security": {
                    "cors_enabled": False,
                    "https_only": True
                },
                "monitoring": {
                    "enabled": True,
                    "log_level": "INFO"
                }
            }
            
            # Sauvegarder la config par défaut
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config):
        """Sauvegarder la configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def run_command(self, command, description, check=True):
        """Exécuter une commande avec gestion d'erreur"""
        print(f"🔄 {description}...")
        print(f"   Commande: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            
            if result.stdout:
                print(f"   Sortie: {result.stdout.strip()}")
            
            print(f"   ✅ {description} terminé")
            return result
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Erreur lors de {description}")
            print(f"   Code d'erreur: {e.returncode}")
            if e.stdout:
                print(f"   Sortie: {e.stdout.strip()}")
            if e.stderr:
                print(f"   Erreur: {e.stderr.strip()}")
            
            if check:
                sys.exit(1)
            return None
    
    def check_prerequisites(self):
        """Vérifier les prérequis pour le déploiement"""
        print("🔍 Vérification des prérequis...")
        
        # Vérifier Python
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ requis")
            return False
        
        print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Vérifier les fichiers requis
        required_files = [
            "main_new.py",
            "requirements.txt"
        ]
        
        for file in required_files:
            if not (self.project_root / file).exists():
                print(f"❌ Fichier manquant: {file}")
                return False
            print(f"   ✅ {file}")
        
        # Vérifier les dépendances système (optionnel)
        system_deps = {
            "git": "git --version",
            "nginx": "nginx -v"  # Optionnel pour la production
        }
        
        for dep, cmd in system_deps.items():
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {dep} disponible")
            else:
                print(f"   ⚠️ {dep} non disponible (optionnel)")
        
        return True
    
    def create_backup(self):
        """Créer une sauvegarde avant déploiement"""
        print("💾 Création de la sauvegarde...")
        
        # Créer le dossier de backup
        self.backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{self.environment}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # Sauvegarder la base de données
        db_files = list(self.project_root.glob("*.db"))
        if db_files:
            backup_path.mkdir(exist_ok=True)
            for db_file in db_files:
                shutil.copy2(db_file, backup_path / db_file.name)
                print(f"   ✅ Sauvegarde de {db_file.name}")
        
        # Sauvegarder les fichiers de configuration
        config_files = list(self.project_root.glob("config_*.json"))
        if config_files and backup_path.exists():
            for config_file in config_files:
                shutil.copy2(config_file, backup_path / config_file.name)
                print(f"   ✅ Sauvegarde de {config_file.name}")
        
        if backup_path.exists():
            print(f"   ✅ Sauvegarde créée: {backup_path}")
            return backup_path
        else:
            print("   ⚠️ Aucune sauvegarde nécessaire")
            return None
    
    def setup_environment(self):
        """Configurer l'environnement Python"""
        print("🐍 Configuration de l'environnement Python...")
        
        # Vérifier si un venv existe
        venv_path = self.project_root.parent / ".venv"
        if not venv_path.exists():
            print("   Création de l'environnement virtuel...")
            self.run_command(
                f"python -m venv {venv_path}",
                "Création du venv"
            )
        
        # Activation du venv et installation des dépendances
        if os.name == 'nt':  # Windows
            pip_cmd = str(venv_path / "Scripts" / "pip.exe")
            python_cmd = str(venv_path / "Scripts" / "python.exe")
        else:  # Unix/Linux
            pip_cmd = str(venv_path / "bin" / "pip")
            python_cmd = str(venv_path / "bin" / "python")
        
        # Installer les dépendances
        self.run_command(
            f"{pip_cmd} install --upgrade pip",
            "Mise à jour de pip"
        )
        
        self.run_command(
            f"{pip_cmd} install -r requirements.txt",
            "Installation des dépendances"
        )
        
        return python_cmd
    
    def setup_database(self):
        """Configurer la base de données"""
        print("🗄️ Configuration de la base de données...")
        
        config = self.load_config()
        db_config = config.get("database", {})
        
        if db_config.get("type") == "sqlite":
            db_path = self.project_root / db_config.get("path", "openred_prod.db")
            
            if not db_path.exists():
                print(f"   Création de la base de données: {db_path}")
                # La base sera créée automatiquement par l'application
            else:
                print(f"   ✅ Base de données existante: {db_path}")
        
        elif db_config.get("type") == "postgresql":
            print("   Configuration PostgreSQL détectée")
            print("   ⚠️ Assurez-vous que PostgreSQL est configuré séparément")
        
        print("   ✅ Configuration de la base de données terminée")
    
    def setup_systemd_service(self, python_cmd):
        """Créer un service systemd (Linux uniquement)"""
        if os.name == 'nt':
            print("   ⚠️ Service systemd non disponible sur Windows")
            return
        
        print("🔧 Configuration du service systemd...")
        
        service_content = f"""[Unit]
Description=OpenRed Central API v2.0
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={self.project_root}
Environment=PATH={Path(python_cmd).parent}
ExecStart={python_cmd} main_new.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path(f"/tmp/openred-central-api.service")
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"   ✅ Fichier de service créé: {service_file}")
        print(f"   📋 Pour installer le service:")
        print(f"      sudo cp {service_file} /etc/systemd/system/")
        print(f"      sudo systemctl daemon-reload")
        print(f"      sudo systemctl enable openred-central-api")
        print(f"      sudo systemctl start openred-central-api")
    
    def setup_nginx_config(self):
        """Créer la configuration nginx"""
        print("🌐 Configuration nginx...")
        
        config = self.load_config()
        server_config = config.get("server", {})
        port = server_config.get("port", 8000)
        
        nginx_content = f"""server {{
    listen 80;
    server_name your-domain.com;  # Remplacez par votre domaine
    
    # Redirection vers HTTPS
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name your-domain.com;  # Remplacez par votre domaine
    
    # Certificats SSL (à configurer)
    # ssl_certificate /path/to/certificate.crt;
    # ssl_certificate_key /path/to/private.key;
    
    # Configuration SSL sécurisée
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Sécurité
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Proxy vers l'API
    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }}
    
    # Logs
    access_log /var/log/nginx/openred_access.log;
    error_log /var/log/nginx/openred_error.log;
}}
"""
        
        nginx_file = Path("/tmp/openred-nginx.conf")
        with open(nginx_file, 'w') as f:
            f.write(nginx_content)
        
        print(f"   ✅ Configuration nginx créée: {nginx_file}")
        print(f"   📋 Pour installer la configuration:")
        print(f"      sudo cp {nginx_file} /etc/nginx/sites-available/openred")
        print(f"      sudo ln -s /etc/nginx/sites-available/openred /etc/nginx/sites-enabled/")
        print(f"      sudo nginx -t")
        print(f"      sudo systemctl reload nginx")
    
    def run_tests(self, python_cmd):
        """Exécuter les tests avant déploiement"""
        print("🧪 Exécution des tests...")
        
        # Tests basiques
        test_files = list(self.project_root.glob("test_*.py"))
        
        if test_files:
            for test_file in test_files:
                self.run_command(
                    f"{python_cmd} {test_file}",
                    f"Test {test_file.name}",
                    check=False  # Ne pas arrêter en cas d'échec
                )
        else:
            print("   ⚠️ Aucun fichier de test trouvé")
        
        # Test de démarrage
        print("   Test de démarrage de l'API...")
        result = self.run_command(
            f"{python_cmd} -c \"import main_new; print('Import réussi')\"",
            "Test d'import",
            check=False
        )
        
        if result and result.returncode == 0:
            print("   ✅ Test de démarrage réussi")
        else:
            print("   ❌ Échec du test de démarrage")
    
    def deploy(self):
        """Exécuter le déploiement complet"""
        print("🚀 DÉMARRAGE DU DÉPLOIEMENT")
        print(f"Environnement: {self.environment}")
        print(f"Dossier: {self.project_root}")
        print("=" * 60)
        
        # 1. Vérification des prérequis
        if not self.check_prerequisites():
            print("❌ Prérequis non satisfaits")
            return False
        
        print()
        
        # 2. Sauvegarde
        backup_path = self.create_backup()
        print()
        
        # 3. Configuration de l'environnement
        python_cmd = self.setup_environment()
        print()
        
        # 4. Configuration de la base de données
        self.setup_database()
        print()
        
        # 5. Tests
        self.run_tests(python_cmd)
        print()
        
        # 6. Configuration des services (production)
        if self.environment == "production":
            self.setup_systemd_service(python_cmd)
            print()
            
            self.setup_nginx_config()
            print()
        
        # 7. Résumé final
        print("✅ DÉPLOIEMENT TERMINÉ")
        print("=" * 60)
        print(f"🐍 Commande Python: {python_cmd}")
        print(f"📁 Dossier du projet: {self.project_root}")
        print(f"⚙️ Configuration: {self.config_file}")
        
        if backup_path:
            print(f"💾 Sauvegarde: {backup_path}")
        
        print("\n📋 ÉTAPES SUIVANTES:")
        print("1. Tester l'API manuellement:")
        print(f"   {python_cmd} main_new.py")
        
        if self.environment == "production":
            print("2. Configurer SSL/TLS pour nginx")
            print("3. Installer et démarrer les services systemd")
            print("4. Configurer les sauvegardes automatiques")
            print("5. Mettre en place le monitoring")
        
        print("\n🎉 Déploiement réussi!")
        return True


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Utilitaire de déploiement OpenRed Central API v2.0")
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default="production",
        help="Environnement de déploiement"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Ignorer l'exécution des tests"
    )
    
    args = parser.parse_args()
    
    # Créer le gestionnaire de déploiement
    deployer = DeploymentManager(environment=args.env)
    
    # Confirmation pour la production
    if args.env == "production":
        response = input("⚠️ Déploiement en PRODUCTION. Continuer? (oui/non): ")
        if response.lower() not in ["oui", "yes", "y", "o"]:
            print("Déploiement annulé.")
            return
    
    # Lancer le déploiement
    success = deployer.deploy()
    
    if success:
        sys.exit(0)
    else:
        print("❌ Échec du déploiement")
        sys.exit(1)


if __name__ == "__main__":
    main()
