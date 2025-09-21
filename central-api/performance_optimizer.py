#!/usr/bin/env python3
"""
Analyseur de Performance et Optimiseur - OpenRed Central API v2.0
Analyse les performances et propose des optimisations
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from pathlib import Path
import sqlite3


class PerformanceAnalyzer:
    """Analyseur de performance de l'API"""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.results = []
        
    async def test_endpoint_performance(self, session, endpoint, method="GET", payload=None, iterations=10):
        """Tester les performances d'un endpoint"""
        print(f"🔍 Test de performance: {method} {endpoint} ({iterations} itérations)")
        
        response_times = []
        errors = 0
        
        for i in range(iterations):
            try:
                start_time = time.time()
                
                if method == "GET":
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        await response.text()
                        status = response.status
                elif method == "POST":
                    async with session.post(f"{self.base_url}{endpoint}", json=payload) as response:
                        await response.text()
                        status = response.status
                
                response_time = (time.time() - start_time) * 1000  # en ms
                response_times.append(response_time)
                
                if status >= 400:
                    errors += 1
                    
                # Affichage du progrès
                if (i + 1) % 5 == 0:
                    print(f"   Progression: {i + 1}/{iterations}")
                    
            except Exception as e:
                errors += 1
                print(f"   ❌ Erreur lors de l'itération {i + 1}: {str(e)}")
        
        if response_times:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "errors": errors,
                "success_rate": ((iterations - errors) / iterations) * 100,
                "avg_response_time_ms": statistics.mean(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "median_response_time_ms": statistics.median(response_times),
                "std_dev_ms": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "response_times": response_times
            }
            
            print(f"   ✅ Résultats: Avg={stats['avg_response_time_ms']:.2f}ms, "
                  f"Min={stats['min_response_time_ms']:.2f}ms, "
                  f"Max={stats['max_response_time_ms']:.2f}ms, "
                  f"Succès={stats['success_rate']:.1f}%")
            
            return stats
        else:
            print(f"   ❌ Aucune réponse valide reçue")
            return None
    
    async def run_performance_tests(self):
        """Lancer une suite complète de tests de performance"""
        print("🚀 Démarrage de l'analyse de performance...")
        print(f"🌐 API testée: {self.base_url}")
        print()
        
        # Tests à effectuer
        test_cases = [
            {"endpoint": "/health", "method": "GET", "iterations": 20},
            {"endpoint": "/", "method": "GET", "iterations": 15},
            {"endpoint": "/nodes", "method": "GET", "iterations": 10},
            {"endpoint": "/api/discover", "method": "GET", "iterations": 10},
            {"endpoint": "/api/nodes", "method": "POST", "payload": {
                "node_id": f"test-node-{int(time.time())}",
                "host": "127.0.0.1",
                "port": 8001,
                "status": "active",
                "services": ["test"]
            }, "iterations": 5}
        ]
        
        async with aiohttp.ClientSession() as session:
            for test_case in test_cases:
                result = await self.test_endpoint_performance(
                    session,
                    test_case["endpoint"],
                    test_case["method"],
                    test_case.get("payload"),
                    test_case["iterations"]
                )
                
                if result:
                    self.results.append(result)
                
                print()  # Ligne vide entre les tests
        
        return self.results
    
    def analyze_results(self):
        """Analyser les résultats et proposer des optimisations"""
        if not self.results:
            return None
        
        print("📊 ANALYSE DES RÉSULTATS")
        print("=" * 60)
        
        total_tests = len(self.results)
        total_requests = sum(r["iterations"] for r in self.results)
        avg_success_rate = statistics.mean([r["success_rate"] for r in self.results])
        overall_avg_time = statistics.mean([r["avg_response_time_ms"] for r in self.results])
        
        print(f"📈 Vue d'ensemble:")
        print(f"   Endpoints testés: {total_tests}")
        print(f"   Requêtes totales: {total_requests}")
        print(f"   Taux de succès global: {avg_success_rate:.1f}%")
        print(f"   Temps de réponse moyen: {overall_avg_time:.2f}ms")
        print()
        
        # Détails par endpoint
        print("📋 Détails par endpoint:")
        for result in sorted(self.results, key=lambda x: x["avg_response_time_ms"]):
            status_emoji = "✅" if result["success_rate"] >= 95 else "⚠️" if result["success_rate"] >= 80 else "❌"
            speed_emoji = "🚀" if result["avg_response_time_ms"] < 50 else "🐌" if result["avg_response_time_ms"] > 200 else "⏱️"
            
            print(f"   {status_emoji} {speed_emoji} {result['method']} {result['endpoint']}")
            print(f"      Temps moyen: {result['avg_response_time_ms']:.2f}ms")
            print(f"      Min/Max: {result['min_response_time_ms']:.2f}ms / {result['max_response_time_ms']:.2f}ms")
            print(f"      Succès: {result['success_rate']:.1f}% ({result['iterations'] - result['errors']}/{result['iterations']})")
            print(f"      Écart-type: {result['std_dev_ms']:.2f}ms")
            print()
        
        # Recommandations
        print("💡 RECOMMANDATIONS D'OPTIMISATION")
        print("=" * 60)
        
        recommendations = []
        
        # Analyse des temps de réponse
        slow_endpoints = [r for r in self.results if r["avg_response_time_ms"] > 100]
        if slow_endpoints:
            recommendations.append({
                "type": "performance",
                "priority": "high",
                "message": f"Endpoints lents détectés ({len(slow_endpoints)} endpoints > 100ms)",
                "details": [f"- {r['method']} {r['endpoint']}: {r['avg_response_time_ms']:.2f}ms" for r in slow_endpoints]
            })
        
        # Analyse de la variabilité
        unstable_endpoints = [r for r in self.results if r["std_dev_ms"] > 50]
        if unstable_endpoints:
            recommendations.append({
                "type": "stability",
                "priority": "medium",
                "message": f"Endpoints instables détectés ({len(unstable_endpoints)} endpoints avec forte variabilité)",
                "details": [f"- {r['method']} {r['endpoint']}: écart-type {r['std_dev_ms']:.2f}ms" for r in unstable_endpoints]
            })
        
        # Analyse des erreurs
        error_endpoints = [r for r in self.results if r["success_rate"] < 95]
        if error_endpoints:
            recommendations.append({
                "type": "reliability",
                "priority": "high",
                "message": f"Endpoints avec erreurs détectés ({len(error_endpoints)} endpoints < 95% succès)",
                "details": [f"- {r['method']} {r['endpoint']}: {r['success_rate']:.1f}% succès" for r in error_endpoints]
            })
        
        # Affichage des recommandations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                priority_emoji = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
                print(f"{priority_emoji} {i}. {rec['message']}")
                for detail in rec["details"]:
                    print(f"      {detail}")
                print()
        else:
            print("✅ Aucune optimisation majeure nécessaire !")
            print("   Toutes les métriques sont dans les limites acceptables.")
        
        # Recommandations générales
        print("🔧 Recommandations générales:")
        print("   1. Mise en cache pour les endpoints fréquemment utilisés")
        print("   2. Optimisation des requêtes de base de données")
        print("   3. Compression des réponses JSON")
        print("   4. Mise en place d'un load balancer pour la scalabilité")
        print("   5. Monitoring continu avec alertes automatiques")
        
        return {
            "summary": {
                "total_tests": total_tests,
                "total_requests": total_requests,
                "avg_success_rate": avg_success_rate,
                "overall_avg_time": overall_avg_time
            },
            "results": self.results,
            "recommendations": recommendations
        }
    
    def save_results(self, filename=None):
        """Sauvegarder les résultats dans un fichier JSON"""
        if filename is None:
            filename = f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        analysis = self.analyze_results()
        if analysis:
            filepath = Path(filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Résultats sauvegardés dans: {filepath.absolute()}")
            return filepath
        
        return None


class DatabaseOptimizer:
    """Optimiseur de base de données"""
    
    def __init__(self, db_path="openred_dev.db"):
        self.db_path = db_path
    
    def analyze_database(self):
        """Analyser la base de données et proposer des optimisations"""
        print("🗄️ ANALYSE DE LA BASE DE DONNÉES")
        print("=" * 60)
        
        if not Path(self.db_path).exists():
            print("❌ Base de données non trouvée!")
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Informations générales
            db_size = Path(self.db_path).stat().st_size / (1024 * 1024)  # MB
            print(f"📊 Taille de la base: {db_size:.2f} MB")
            
            # Analyse des tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"📋 Tables ({len(tables)}):")
            
            table_stats = {}
            for table_name, in tables:
                try:
                    # Compter les enregistrements
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    
                    # Analyser la structure
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    
                    table_stats[table_name] = {
                        "count": count,
                        "columns": len(columns)
                    }
                    
                    print(f"   - {table_name}: {count} enregistrements, {len(columns)} colonnes")
                    
                except Exception as e:
                    print(f"   - {table_name}: Erreur lors de l'analyse ({str(e)})")
            
            # Analyse des index
            print("\n🔍 Index existants:")
            cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index';")
            indexes = cursor.fetchall()
            
            if indexes:
                for index_name, table_name in indexes:
                    if not index_name.startswith('sqlite_'):  # Ignorer les index système
                        print(f"   - {index_name} sur {table_name}")
            else:
                print("   Aucun index personnalisé trouvé")
            
            # Recommandations d'optimisation
            print("\n💡 RECOMMANDATIONS D'OPTIMISATION DB")
            print("=" * 60)
            
            recommendations = []
            
            # Vérifier les tables volumineuses sans index
            large_tables = [name for name, stats in table_stats.items() if stats["count"] > 1000]
            if large_tables:
                recommendations.append(f"Considérer des index pour les tables volumineuses: {', '.join(large_tables)}")
            
            # Recommandations générales
            recommendations.extend([
                "Ajouter des index sur les colonnes fréquemment utilisées dans les WHERE",
                "Utiliser EXPLAIN QUERY PLAN pour optimiser les requêtes lentes",
                "Considérer VACUUM pour récupérer l'espace libre",
                "Implémenter une stratégie de nettoyage des données anciennes"
            ])
            
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
            
            conn.close()
            
            return {
                "db_size_mb": db_size,
                "tables": table_stats,
                "indexes": len([idx for idx in indexes if not idx[0].startswith('sqlite_')]),
                "recommendations": recommendations
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse: {str(e)}")
            return None
    
    def optimize_database(self):
        """Appliquer des optimisations basiques à la base de données"""
        print("🔧 OPTIMISATION DE LA BASE DE DONNÉES")
        print("=" * 60)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print("1. Analyse de l'espace utilisé...")
            cursor.execute("PRAGMA page_count;")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA freelist_count;")
            free_pages = cursor.fetchone()[0]
            
            print(f"   Pages totales: {page_count}")
            print(f"   Pages libres: {free_pages}")
            
            if free_pages > page_count * 0.1:  # Plus de 10% de pages libres
                print("2. Exécution de VACUUM pour récupérer l'espace...")
                cursor.execute("VACUUM;")
                print("   ✅ VACUUM terminé")
            else:
                print("2. VACUUM non nécessaire (< 10% d'espace libre)")
            
            print("3. Mise à jour des statistiques...")
            cursor.execute("ANALYZE;")
            print("   ✅ ANALYZE terminé")
            
            print("4. Optimisation des paramètres de performance...")
            # Optimisations de performance
            cursor.execute("PRAGMA journal_mode = WAL;")  # Write-Ahead Logging
            cursor.execute("PRAGMA synchronous = NORMAL;")  # Balance performance/sécurité
            cursor.execute("PRAGMA cache_size = 10000;")  # Cache plus large
            cursor.execute("PRAGMA temp_store = MEMORY;")  # Tables temporaires en mémoire
            
            print("   ✅ Paramètres optimisés")
            
            conn.commit()
            conn.close()
            
            print("\n✅ Optimisation de la base de données terminée!")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'optimisation: {str(e)}")


async def main():
    """Fonction principale"""
    print("🎯 ANALYSEUR ET OPTIMISEUR DE PERFORMANCE")
    print("OpenRed Central API v2.0")
    print("=" * 60)
    print()
    
    # 1. Analyse de performance de l'API
    analyzer = PerformanceAnalyzer()
    
    print("Phase 1: Tests de performance de l'API")
    print("-" * 40)
    
    try:
        results = await analyzer.run_performance_tests()
        
        if results:
            print()
            analysis = analyzer.analyze_results()
            
            # Sauvegarder les résultats
            analyzer.save_results()
            
        else:
            print("❌ Aucun résultat de test disponible")
    
    except Exception as e:
        print(f"❌ Erreur lors des tests de performance: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # 2. Analyse et optimisation de la base de données
    print("Phase 2: Analyse et optimisation de la base de données")
    print("-" * 40)
    
    db_optimizer = DatabaseOptimizer()
    
    # Analyse
    db_analysis = db_optimizer.analyze_database()
    
    if db_analysis:
        print()
        # Optimisation
        db_optimizer.optimize_database()
    
    print("\n" + "=" * 60)
    print("✅ Analyse et optimisation terminées!")
    print("💡 Consultez les résultats sauvegardés pour plus de détails.")


if __name__ == "__main__":
    asyncio.run(main())
