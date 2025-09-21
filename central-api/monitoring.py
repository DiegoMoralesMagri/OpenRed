#!/usr/bin/env python3
"""
Système de Monitoring et Métriques - OpenRed Central API v2.0
Monitoring and Metrics System - OpenRed Central API v2.0
Sistema de Monitoreo y Métricas - OpenRed Central API v2.0
监控和指标系统 - OpenRed 中央 API v2.0

Collecte et affichage des métriques de performance et de santé
Collection and display of performance and health metrics
Recopilación y visualización de métricas de rendimiento y salud
性能和健康指标的收集和显示
"""

import asyncio
import psutil
import time
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Configuration | Configuration | Configuración | 配置
API_BASE_URL = "http://127.0.0.1:8000"
MONITORING_INTERVAL = 5  # secondes | seconds | segundos | 秒
DB_PATH = "openred_dev.db"


class SystemMonitor:
    """
    Monitoring des ressources système
    System resource monitoring
    Monitoreo de recursos del sistema
    系统资源监控
    """
    
    def __init__(self):
        self.start_time = time.time()
        
    def get_system_metrics(self):
        """
        Récupérer les métriques système
        Get system metrics
        Obtener métricas del sistema
        获取系统指标
        """
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Mémoire
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_total_mb = memory.total / (1024 * 1024)
            
            # Disque
            disk = psutil.disk_usage('.')
            disk_percent = (disk.used / disk.total) * 100
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_total_gb = disk.total / (1024 * 1024 * 1024)
            
            # Réseau
            network = psutil.net_io_counters()
            
            # Uptime
            uptime = time.time() - self.start_time
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": round(cpu_percent, 2),
                    "count": cpu_count
                },
                "memory": {
                    "percent": round(memory_percent, 2),
                    "used_mb": round(memory_used_mb, 2),
                    "total_mb": round(memory_total_mb, 2)
                },
                "disk": {
                    "percent": round(disk_percent, 2),
                    "used_gb": round(disk_used_gb, 2),
                    "total_gb": round(disk_total_gb, 2)
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "uptime_seconds": round(uptime, 2)
            }
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


class DatabaseMonitor:
    """Monitoring de la base de données"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        
    def get_database_metrics(self):
        """Récupérer les métriques de la base de données"""
        try:
            if not Path(self.db_path).exists():
                return {"error": "Database file not found", "timestamp": datetime.now().isoformat()}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Taille de la base
            db_size_bytes = Path(self.db_path).stat().st_size
            db_size_mb = db_size_bytes / (1024 * 1024)
            
            # Compter les enregistrements
            tables = {}
            
            # Nodes
            try:
                cursor.execute("SELECT COUNT(*) FROM nodes")
                tables["nodes"] = cursor.fetchone()[0]
            except:
                tables["nodes"] = 0
            
            # Messages
            try:
                cursor.execute("SELECT COUNT(*) FROM messages")
                tables["messages"] = cursor.fetchone()[0]
            except:
                tables["messages"] = 0
            
            # Auth sessions
            try:
                cursor.execute("SELECT COUNT(*) FROM auth_sessions")
                tables["auth_sessions"] = cursor.fetchone()[0]
            except:
                tables["auth_sessions"] = 0
            
            # Audit logs
            try:
                cursor.execute("SELECT COUNT(*) FROM audit_logs")
                tables["audit_logs"] = cursor.fetchone()[0]
            except:
                tables["audit_logs"] = 0
            
            # Activité récente (dernières 24h)
            recent_activity = {}
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM nodes 
                    WHERE created_at > datetime('now', '-1 day')
                """)
                recent_activity["new_nodes_24h"] = cursor.fetchone()[0]
            except:
                recent_activity["new_nodes_24h"] = 0
            
            conn.close()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "database": {
                    "size_mb": round(db_size_mb, 2),
                    "size_bytes": db_size_bytes,
                    "tables": tables,
                    "total_records": sum(tables.values()),
                    "recent_activity": recent_activity
                }
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


class APIMonitor:
    """Monitoring de l'API"""
    
    def __init__(self, api_url):
        self.api_url = api_url
        self.request_history = []
        
    def test_api_health(self):
        """Tester la santé de l'API"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            # Enregistrer dans l'historique
            self.request_history.append({
                "timestamp": datetime.now().isoformat(),
                "endpoint": "/health",
                "status_code": response.status_code,
                "response_time_ms": round(response_time * 1000, 2),
                "success": response.status_code == 200
            })
            
            # Garder seulement les 100 dernières requêtes
            if len(self.request_history) > 100:
                self.request_history = self.request_history[-100:]
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "timestamp": datetime.now().isoformat(),
                    "api": {
                        "status": data.get("status", "unknown"),
                        "response_time_ms": round(response_time * 1000, 2),
                        "version": data.get("version", "unknown"),
                        "uptime_seconds": data.get("uptime_seconds", 0)
                    }
                }
            else:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "api": {
                        "status": "unhealthy",
                        "status_code": response.status_code,
                        "response_time_ms": round(response_time * 1000, 2)
                    }
                }
                
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "api": {
                    "status": "error",
                    "error": str(e)
                }
            }
    
    def get_performance_stats(self):
        """Statistiques de performance basées sur l'historique"""
        if not self.request_history:
            return {"error": "No request history available"}
        
        # Statistiques des 10 dernières requêtes
        recent_requests = self.request_history[-10:]
        
        response_times = [req["response_time_ms"] for req in recent_requests]
        success_count = sum(1 for req in recent_requests if req["success"])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "performance": {
                "total_requests": len(self.request_history),
                "recent_requests": len(recent_requests),
                "success_rate_percent": round((success_count / len(recent_requests)) * 100, 2),
                "avg_response_time_ms": round(sum(response_times) / len(response_times), 2),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times)
            }
        }


class MonitoringDashboard:
    """Dashboard de monitoring en temps réel"""
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.db_monitor = DatabaseMonitor(DB_PATH)
        self.api_monitor = APIMonitor(API_BASE_URL)
        
    def display_metrics(self, system_data, db_data, api_data, perf_data):
        """Afficher les métriques dans un format lisible"""
        # Clear screen (fonctionne sur Windows et Unix)
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print("🔍 MONITORING DASHBOARD - OpenRed Central API v2.0")
        print("=" * 80)
        print(f"⏰ Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Système
        if "error" not in system_data:
            sys_data = system_data
            print("💻 SYSTÈME")
            print(f"   CPU: {sys_data['cpu']['percent']}% ({sys_data['cpu']['count']} cores)")
            print(f"   RAM: {sys_data['memory']['percent']}% ({sys_data['memory']['used_mb']:.0f}MB / {sys_data['memory']['total_mb']:.0f}MB)")
            print(f"   Disque: {sys_data['disk']['percent']:.1f}% ({sys_data['disk']['used_gb']:.1f}GB / {sys_data['disk']['total_gb']:.1f}GB)")
            print(f"   Uptime: {sys_data['uptime_seconds']:.0f}s")
        else:
            print("💻 SYSTÈME: ❌ Erreur")
        
        print()
        
        # Base de données
        if "error" not in db_data:
            db_info = db_data["database"]
            print("🗄️ BASE DE DONNÉES")
            print(f"   Taille: {db_info['size_mb']:.2f} MB")
            print(f"   Tables:")
            for table, count in db_info['tables'].items():
                print(f"     - {table}: {count} enregistrements")
            print(f"   Total: {db_info['total_records']} enregistrements")
            print(f"   Nouveaux nœuds (24h): {db_info['recent_activity']['new_nodes_24h']}")
        else:
            print("🗄️ BASE DE DONNÉES: ❌ Erreur")
        
        print()
        
        # API
        if "error" not in api_data and "api" in api_data:
            api_info = api_data["api"]
            status_emoji = "✅" if api_info.get("status") == "healthy" else "❌"
            print(f"🌐 API {status_emoji}")
            print(f"   Statut: {api_info.get('status', 'unknown')}")
            if "response_time_ms" in api_info:
                print(f"   Temps de réponse: {api_info['response_time_ms']:.2f}ms")
            if "version" in api_info:
                print(f"   Version: {api_info['version']}")
            if "uptime_seconds" in api_info:
                print(f"   Uptime API: {api_info['uptime_seconds']:.0f}s")
        else:
            print("🌐 API: ❌ Non disponible ou erreur")
        
        print()
        
        # Performance
        if "error" not in perf_data and "performance" in perf_data:
            perf_info = perf_data["performance"]
            print("📊 PERFORMANCE")
            print(f"   Requêtes totales: {perf_info['total_requests']}")
            print(f"   Taux de succès: {perf_info['success_rate_percent']:.1f}%")
            print(f"   Temps moyen: {perf_info['avg_response_time_ms']:.2f}ms")
            print(f"   Min/Max: {perf_info['min_response_time_ms']:.0f}ms / {perf_info['max_response_time_ms']:.0f}ms")
        else:
            print("📊 PERFORMANCE: Pas encore de données")
        
        print()
        print("=" * 80)
        print("💡 Appuyez sur Ctrl+C pour arrêter le monitoring")
        print("=" * 80)
    
    async def run_monitoring(self):
        """Lancer le monitoring en temps réel"""
        print("🚀 Démarrage du monitoring OpenRed Central API v2.0...")
        print(f"📡 Monitoring de l'API sur: {API_BASE_URL}")
        print(f"🗄️ Monitoring de la DB: {DB_PATH}")
        print(f"⏱️ Intervalle: {MONITORING_INTERVAL}s")
        print()
        print("Appuyez sur Ctrl+C pour arrêter...")
        
        try:
            while True:
                # Collecter les métriques
                system_data = self.system_monitor.get_system_metrics()
                db_data = self.db_monitor.get_database_metrics()
                api_data = self.api_monitor.test_api_health()
                perf_data = self.api_monitor.get_performance_stats()
                
                # Afficher le dashboard
                self.display_metrics(system_data, db_data, api_data, perf_data)
                
                # Attendre
                await asyncio.sleep(MONITORING_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Arrêt du monitoring...")
            print("📊 Statistiques finales:")
            
            # Afficher les statistiques finales
            final_perf = self.api_monitor.get_performance_stats()
            if "performance" in final_perf:
                perf = final_perf["performance"]
                print(f"   Total de requêtes testées: {perf['total_requests']}")
                print(f"   Taux de succès global: {perf['success_rate_percent']:.1f}%")
                print(f"   Temps de réponse moyen: {perf['avg_response_time_ms']:.2f}ms")
            
            print("\n✅ Monitoring terminé.")


def run_single_check():
    """Lancer une vérification unique (non interactive)"""
    print("🔍 Vérification unique des métriques...")
    print()
    
    dashboard = MonitoringDashboard()
    
    # Collecter les métriques
    system_data = dashboard.system_monitor.get_system_metrics()
    db_data = dashboard.db_monitor.get_database_metrics()
    api_data = dashboard.api_monitor.test_api_health()
    
    # Afficher
    dashboard.display_metrics(system_data, db_data, api_data, {"performance": {
        "total_requests": 1,
        "recent_requests": 1,
        "success_rate_percent": 100.0 if "api" in api_data and api_data["api"].get("status") == "healthy" else 0.0,
        "avg_response_time_ms": api_data.get("api", {}).get("response_time_ms", 0),
        "min_response_time_ms": api_data.get("api", {}).get("response_time_ms", 0),
        "max_response_time_ms": api_data.get("api", {}).get("response_time_ms", 0)
    }})


def main():
    """Fonction principale"""
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_single_check()
    else:
        dashboard = MonitoringDashboard()
        asyncio.run(dashboard.run_monitoring())


if __name__ == "__main__":
    main()
