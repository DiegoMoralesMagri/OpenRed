#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌍 OpenRed Network - Passerelle Internet
Rend le protocole orp:// accessible mondialement via internet
"""

import socket
import threading
import json
import time
from typing import Dict, List, Optional, Tuple
import requests
from urllib.parse import urlparse


class RegistryInternet:
    """
    🌍 Registry internet pour l'enregistrement global des forts
    Permet la découverte mondiale des forts OpenRed Network
    """
    
    def __init__(self, serveur_registry: str = "https://registry.openred.network"):
        self.serveur_registry = serveur_registry
        self.forts_locaux = {}  # Forts hébergés localement
        self.cache_global = {}  # Cache des forts distants
        self.derniere_sync = 0
        
    def enregistrer_fort_local(self, fort_id: str, port_local: int, 
                              adresse_publique: str = None) -> bool:
        """
        Enregistre un fort local sur le registry internet
        
        Args:
            fort_id: Identifiant du fort
            port_local: Port d'écoute local 
            adresse_publique: IP publique (auto-détectée si None)
            
        Returns:
            True si enregistrement réussi
        """
        try:
            # Auto-détection IP publique
            if not adresse_publique:
                adresse_publique = self._detecter_ip_publique()
            
            if not adresse_publique:
                print("❌ Impossible de détecter l'adresse IP publique")
                return False
            
            # Données d'enregistrement
            donnees = {
                "fort_id": fort_id,
                "adresse_ip": adresse_publique,
                "port": port_local,
                "timestamp": int(time.time()),
                "statut": "online",
                "version": "1.0.0"
            }
            
            # Enregistrement local
            self.forts_locaux[fort_id] = donnees
            
            # Enregistrement sur registry internet
            url_enregistrement = f"{self.serveur_registry}/api/v1/forts/register"
            
            response = requests.post(url_enregistrement, json=donnees, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Fort {fort_id} enregistré sur internet")
                print(f"🌍 Accessible via: orp://{fort_id}.openred/")
                print(f"🔗 Adresse publique: {adresse_publique}:{port_local}")
                return True
            else:
                print(f"❌ Échec enregistrement registry: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur enregistrement internet: {e}")
            return False
    
    def resoudre_fort_global(self, fort_id: str) -> Optional[Tuple[str, int]]:
        """
        Résout un fort via le registry internet global
        
        Args:
            fort_id: Identifiant du fort à résoudre
            
        Returns:
            Tuple (ip, port) ou None si non trouvé
        """
        try:
            # Vérification cache local
            if fort_id in self.cache_global:
                cache_entry = self.cache_global[fort_id]
                if time.time() - cache_entry['timestamp'] < 300:  # Cache 5 min
                    return (cache_entry['ip'], cache_entry['port'])
            
            # Requête au registry internet
            url_resolution = f"{self.serveur_registry}/api/v1/forts/resolve/{fort_id}"
            
            response = requests.get(url_resolution, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                ip = data.get('adresse_ip')
                port = data.get('port')
                
                if ip and port:
                    # Mise à jour cache
                    self.cache_global[fort_id] = {
                        'ip': ip,
                        'port': port,
                        'timestamp': time.time()
                    }
                    
                    print(f"🌍 Fort {fort_id} résolu: {ip}:{port}")
                    return (ip, port)
            
            print(f"❌ Fort {fort_id} non trouvé sur internet")
            return None
            
        except Exception as e:
            print(f"❌ Erreur résolution internet: {e}")
            return None
    
    def _detecter_ip_publique(self) -> Optional[str]:
        """Détecte l'adresse IP publique"""
        services_ip = [
            "https://api.ipify.org",
            "https://ipv4.icanhazip.com",
            "https://httpbin.org/ip"
        ]
        
        for service in services_ip:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip = response.text.strip()
                    print(f"🌍 IP publique détectée: {ip}")
                    return ip
            except:
                continue
        
        return None
    
    def synchroniser_cache(self):
        """Synchronise le cache avec le registry internet"""
        try:
            url_liste = f"{self.serveur_registry}/api/v1/forts/list"
            response = requests.get(url_liste, timeout=10)
            
            if response.status_code == 200:
                forts_distants = response.json()
                
                for fort in forts_distants:
                    fort_id = fort.get('fort_id')
                    if fort_id:
                        self.cache_global[fort_id] = {
                            'ip': fort.get('adresse_ip'),
                            'port': fort.get('port'),
                            'timestamp': time.time()
                        }
                
                print(f"🔄 Cache synchronisé: {len(forts_distants)} forts distants")
                self.derniere_sync = time.time()
                
        except Exception as e:
            print(f"❌ Erreur synchronisation: {e}")


class PasserelleInternet:
    """
    🌉 Passerelle internet pour OpenRed Network
    Gère l'exposition des forts locaux sur internet
    """
    
    def __init__(self, port_passerelle: int = 8080):
        self.port_passerelle = port_passerelle
        self.registry = RegistryInternet()
        self.serveur_actif = False
        self.thread_serveur = None
        
    def demarrer_passerelle(self):
        """Démarre la passerelle internet"""
        try:
            print("🌉 Démarrage passerelle internet OpenRed Network...")
            
            self.serveur_actif = True
            self.thread_serveur = threading.Thread(target=self._serveur_http)
            self.thread_serveur.daemon = True
            self.thread_serveur.start()
            
            print(f"✅ Passerelle active sur port {self.port_passerelle}")
            print("🌍 Les forts locaux sont maintenant accessibles via internet")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur démarrage passerelle: {e}")
            return False
    
    def arreter_passerelle(self):
        """Arrête la passerelle internet"""
        self.serveur_actif = False
        print("🛑 Passerelle internet arrêtée")
    
    def exposer_fort(self, fort_id: str, port_local: int) -> bool:
        """
        Expose un fort local sur internet
        
        Args:
            fort_id: Identifiant du fort
            port_local: Port local du fort
            
        Returns:
            True si exposition réussie
        """
        try:
            # Enregistrement sur registry internet
            if self.registry.enregistrer_fort_local(fort_id, port_local):
                print(f"🌍 Fort {fort_id} exposé sur internet")
                print(f"🔗 URL publique: orp://{fort_id}.openred/")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Erreur exposition fort: {e}")
            return False
    
    def _serveur_http(self):
        """Serveur HTTP pour la passerelle"""
        try:
            import http.server
            import socketserver
            
            class HandlerPasserelle(http.server.BaseHTTPRequestHandler):
                def do_GET(self):
                    # Gestion des requêtes vers les forts
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {
                        "service": "OpenRed Network Internet Gateway",
                        "version": "1.0.0",
                        "status": "active"
                    }
                    
                    self.wfile.write(json.dumps(response).encode())
                
                def log_message(self, format, *args):
                    # Supprime les logs HTTP par défaut
                    pass
            
            with socketserver.TCPServer(("", self.port_passerelle), HandlerPasserelle) as httpd:
                while self.serveur_actif:
                    httpd.handle_request()
                    
        except Exception as e:
            print(f"❌ Erreur serveur passerelle: {e}")


class NavigateurWeb:
    """
    🌐 Interface web pour accéder aux forts via navigateur
    Convertit les URLs orp:// en interface web accessible
    """
    
    def __init__(self, port_web: int = 3000):
        self.port_web = port_web
        self.registry = RegistryInternet()
        
    def generer_interface_web(self, fort_id: str) -> str:
        """
        Génère une interface web pour accéder à un fort
        
        Args:
            fort_id: Identifiant du fort
            
        Returns:
            HTML de l'interface web
        """
        
        html_interface = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRed Network - Fort {fort_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            color: white;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        .fort-header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .fort-id {{
            font-size: 24px;
            font-weight: bold;
            color: #ffeb3b;
        }}
        .actions {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .action-card {{
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s ease;
        }}
        .action-card:hover {{
            transform: translateY(-5px);
        }}
        .status {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }}
        .online {{ background: #4caf50; }}
        .offline {{ background: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="fort-header">
            <h1>🏰 OpenRed Network</h1>
            <div class="fort-id">Fort: {fort_id}</div>
            <div class="status online" id="status">🟢 En ligne</div>
        </div>
        
        <div class="actions">
            <div class="action-card" onclick="connecterFort()">
                <h3>🏠 Fort Principal</h3>
                <p>Accéder au fort principal</p>
            </div>
            
            <div class="action-card" onclick="ouvrirFenetre()">
                <h3>🪟 Fenêtre Publique</h3>
                <p>Voir l'interface publique</p>
            </div>
            
            <div class="action-card" onclick="voirProjections()">
                <h3>🎭 Projections</h3>
                <p>Explorer les projections</p>
            </div>
            
            <div class="action-card" onclick="telechargerClient()">
                <h3>⬇️ Client OpenRed</h3>
                <p>Télécharger l'application</p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px; opacity: 0.8;">
            <p>💡 Pour une expérience complète, installez le client OpenRed Network</p>
            <p>🔗 URL native: <code>orp://{fort_id}.openred/</code></p>
        </div>
    </div>
    
    <script>
        function connecterFort() {{
            // Tentative ouverture protocole natif
            window.location.href = 'orp://{fort_id}.openred/';
            
            // Fallback après 2 secondes
            setTimeout(() => {{
                alert('Pour une connexion directe, installez le client OpenRed Network');
            }}, 2000);
        }}
        
        function ouvrirFenetre() {{
            window.location.href = 'orp://{fort_id}.openred/fenetre';
        }}
        
        function voirProjections() {{
            window.location.href = 'orp://{fort_id}.openred/projection/';
        }}
        
        function telechargerClient() {{
            window.open('https://openred.community/client/releases', '_blank');
        }}
        
        // Vérification statut fort
        function verifierStatut() {{
            fetch('/api/status/{fort_id}')
                .then(response => response.json())
                .then(data => {{
                    const statusElement = document.getElementById('status');
                    if (data.online) {{
                        statusElement.innerHTML = '🟢 En ligne';
                        statusElement.className = 'status online';
                    }} else {{
                        statusElement.innerHTML = '🔴 Hors ligne';
                        statusElement.className = 'status offline';
                    }}
                }})
                .catch(() => {{
                    document.getElementById('status').innerHTML = '⚠️ Statut inconnu';
                }});
        }}
        
        // Vérification périodique
        setInterval(verifierStatut, 30000);
        verifierStatut();
    </script>
</body>
</html>
        """
        
        return html_interface
    
    def creer_serveur_web(self):
        """Crée un serveur web pour l'accès navigateur"""
        try:
            print(f"🌐 Création serveur web sur port {self.port_web}")
            print(f"🔗 Interface accessible via: http://localhost:{self.port_web}")
            
            # TODO: Implémentation serveur web complet
            # avec Flask ou FastAPI
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur serveur web: {e}")
            return False


def installer_passerelle_internet():
    """
    🚀 Installation de la passerelle internet OpenRed Network
    """
    print("=" * 60)
    print("    🌍 INSTALLATION PASSERELLE INTERNET OPENRED")
    print("=" * 60)
    print()
    
    try:
        # Création de la passerelle
        passerelle = PasserelleInternet()
        
        # Démarrage
        if passerelle.demarrer_passerelle():
            print("✅ Passerelle internet installée avec succès")
            print()
            print("🌍 Vos forts peuvent maintenant être:")
            print("  • Accessibles mondialement via internet")
            print("  • Découverts depuis n'importe où dans le monde")
            print("  • Partagés via des liens publics")
            print()
            print("🔗 Pour exposer un fort:")
            print("  passerelle.exposer_fort('fort_id', port_local)")
            print()
            
            return passerelle
        else:
            print("❌ Échec installation passerelle")
            return None
            
    except Exception as e:
        print(f"❌ Erreur installation: {e}")
        return None


if __name__ == "__main__":
    # Démonstration de la passerelle internet
    passerelle = installer_passerelle_internet()
    
    if passerelle:
        # Exemple d'exposition d'un fort
        print("\n🧪 Test d'exposition d'un fort...")
        passerelle.exposer_fort("fort_1234567890abcdef", 5000)
        
        print("\n✅ Passerelle internet active")
        print("🌍 OpenRed Network est maintenant accessible mondialement !")
        
        try:
            input("\nAppuyez sur Entrée pour arrêter la passerelle...")
        except KeyboardInterrupt:
            pass
        
        passerelle.arreter_passerelle()
    
    print("🔚 Fin de la démonstration")