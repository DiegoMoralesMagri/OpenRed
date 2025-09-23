# Analyse de l'architecture de vérification périodique OpenRed
# Calculs de performance et ressources

## Paramètres de base
- 100,000 nœuds enregistrés maximum par instance
- Vérifications : 1-2 fois par an
- Retry logic : 24h → 1 semaine → 1 mois → coma (2 ans) → suppression

## Calcul du trafic réseau

### Scénario 1 : Vérification annuelle (1 fois/an)
```
100,000 nœuds × 1 vérification/an = 100,000 requêtes/an
= 274 requêtes/jour = 11 requêtes/heure = 0.003 requêtes/seconde
```

### Scénario 2 : Vérification bi-annuelle (2 fois/an)  
```
100,000 nœuds × 2 vérifications/an = 200,000 requêtes/an
= 548 requêtes/jour = 23 requêtes/heure = 0.006 requêtes/seconde
```

### Trafic total avec retry logic
```
Estimation pessimiste (10% de nœuds inactifs nécessitant retry) :
- Vérification initiale : 0.006 req/sec
- Retry 24h : 0.0006 req/sec  
- Retry 1 semaine : 0.0001 req/sec
- Retry 1 mois : 0.00003 req/sec

TOTAL : ~0.007 requêtes/seconde en continu
```

## Comparaison avec l'ancien système
```
Ancien (heartbeat horaire) : 27 req/sec
Nouveau (vérification annuelle) : 0.007 req/sec
RÉDUCTION : 99.97% du trafic réseau ! 🎉
```

## Impact mémoire
```
Nœud actif : ~500 bytes
Nœud en "coma" : ~200 bytes (infos essentielles)
Nœud "mort" : 0 bytes (supprimé)

100,000 nœuds actifs : 50MB
+ 20,000 nœuds en coma : 4MB  
TOTAL : 54MB par instance (très acceptable)
```

## Avantages techniques
1. **Trafic réseau minimal** : 3,850x moins que heartbeat
2. **Découvrabilité maximale** : Tous les nœuds visibles
3. **Résilience humaine** : Tolère les aléas de la vie
4. **Évolutivité** : Scale naturellement
5. **P2P pur** : API centrale = simple annuaire