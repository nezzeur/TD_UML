# DynamicPricingStrategy - Analyse & Adaptation UML

## Structure du Fichier `DynamicPriceStrategy.py`

Le fichier contient **5 composants**:

### 1. **Classe Principale: DynamicPricingStrategy**
```python
class DynamicPricingStrategy(PricingStrategy):
    # Hérite de PricingStrategy (pattern Strategy)
    # Implémente calculate_fare()
```

**Attributs de classe (statiques)**:
- `BASE_FARE = 2.50` : Prise en charge fixe (€)
- `RATE_PER_KM` : Dict[RideType, float] — tarif par km selon type
- `RATE_PER_MIN = 0.20` : Prix par minute
- `FLOOR_PRICE = 4.90` : Prix plancher absolu
- `MAX_SURGE = 3.0` : Multiplicateur max de surge
- `SURGE_THRESHOLD = 0.7` : Ratio min pour activer surge

**Attributs d'instance**:
- `_active_requests` : int — trajets demandés actuellement
- `_available_drivers` : int — chauffeurs disponibles
- `_surge_multiplier` : float — multiplicateur courant

**Méthodes clés**:
- `update_demand(active_requests, available_drivers)` → met à jour surge
- `calculate_fare(pickup, dropoff, ride_type)` → tarif avec surge
- `get_surge_multiplier()` → retourne le multiplicateur
- `_calculate_surge_multiplier()` → calcul interne (privé)

### 2. **Utilitaires de Distance**

```python
def get_route_info(start_lat, start_lon, end_lat, end_lon) -> dict
```
- Appelle **OpenRouteService** pour vraie distance routière
- Fallback sur **Haversine** si API indisponible
- Retourne : `{"dist_km": float, "duration_min": float, "source": str}`

```python
def _haversine(lat1, lon1, lat2, lon2) -> float
```
- Distance géographique avec formule de Haversine
- Corrige les distances GPS (meilleur que euclidienne)

### 3. **Simulation Tarifs Uber Paris 2024**

```python
def get_uber_prices(dist_km, duration_min) -> list
```
- Simule grilles Uber réelles (X, Comfort, Van)
- Retourne fourchette avec min/mid/high (±10%)

```python
def calculate_our_price(dist_km, duration_min, uber_prices) -> dict
```
- Calcule notre prix optimal
- Logique: `max(coût réel, 92% de Uber X, plancher)`

### 4. **Script de Comparaison**

```python
def run_comparison()
```
- Exécute 3 trajets réels de Paris
- Compare nos prix vs Uber (X, Comfort, Van)
- Affichage tabulaire avec barres de visualisation

### 5. **Helpers d'Affichage**
- `_fmt(price)` → Format monétaire (€)
- `_bar(val, max_val, width)` → Barre de progression unicode
- `_sep(c, w)` → Séparateur

---

## Logique du Surge Pricing

### Calcul du Multiplicateur
```
ratio = active_requests / available_drivers

if ratio < 0.7:        → x1.0 (pas de surge)
if 0.7 <= ratio < 1.0: → interpolation linéaire
if ratio >= 1.0:       → x3.0 (surge maximum)
```

### Formule du Tarif Final
```
prix = (BASE_FARE + RATE_PER_KM * dist + RATE_PER_MIN * durée) * surge_multiplier
prix = max(prix, FLOOR_PRICE)
```

---

## Adaptation du Diagramme UML

### Changements Apportés

| Élément | Avant | Après |
|---------|-------|-------|
| **RATE_PER_KM** | Instance | `{static}` (attribut classe) |
| **Attributs** | `_active_requests`, `_available_drivers` | Ajoutés `_surge_multiplier` |
| **Méthode** | Pas d'`__init__` | Ajoutée (initialise à 1.0) |
| **Constantes** | BASE_FARE, MAX_SURGE | Ajoutées RATE_PER_MIN, FLOOR_PRICE |
| **Note** | Brève | Détaillée avec formules |

### UML Généré

La classe `DynamicPricingStrategy` dans `diagramme_ameliore_v2.puml` reflète maintenant:

✅ Héritage de `PricingStrategy`  
✅ Tous les attributs statiques (constantes tarifaires)  
✅ Tous les attributs d'instance (state du surge)  
✅ Les 4 méthodes principales  
✅ Utilitaires documentés dans une note annexe  
✅ Lien avec `Location`, `RideType` (dépendances)  

---

## Points Clés à Retenir

1. **DynamicPricingStrategy est une vraie stratégie** : 
   - Implémente l'interface `PricingStrategy`
   - Peut être switchée avec `FlatRate` ou `VehicleBasedPricingStrategy`

2. **État stateful** : 
   - `_active_requests` et `_available_drivers` changent en temps réel
   - Mise à jour via `update_demand()`

3. **Distance réelle** :
   - OpenRouteService API pour vraie distance routière
   - Fallback Haversine si API down (robustesse)

4. **Tarification compétitive** :
   - Comparaison vs Uber Paris 2024 (données réelles)
   - Positionné 8% sous médiane Uber X

5. **Script d'analyse** :
   - Démontre la stratégie sur 3 trajets réels
   - Compare avec grilles Uber simulées
