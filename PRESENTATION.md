# Ride Sharing — Analyse, UML & Améliorations

---

## 1. Rôle global du système

Le projet simule un service de **covoiturage / VTC type Uber**.  
Un **passager (Rider)** demande une course, le système trouve le **chauffeur (Driver)** le plus proche, calcule le **tarif**, crée un **Trip**, puis gère son cycle de vie jusqu'à la fin de la course.

---

## 2. Architecture & patterns utilisés

| Pattern | Classe(s) | Rôle |
|---|---|---|
| **Singleton** | `RideSharingService` | Point d'entrée unique, thread-safe |
| **Builder** | `Trip.TripBuilder` | Construction d'un `Trip` par étapes |
| **Strategy** | `PricingStrategy`, `DriverMatchingStrategy` | Algorithmes interchangeables à l'exécution |
| **State** | `TripState` + 4 états | Cycle de vie d'un `Trip` |
| **Observer** | `TripObserver` → `User` → `Rider`, `Driver` | Notification automatique à chaque changement |

---

## 3. UML — Code actuel

> Fichier : `diagramme_uml.puml` / `diagramme_uml.png`

```
[voir diagramme_uml.png]
```

### Classes principales et responsabilités

| Classe | Responsabilité |
|---|---|
| `RideSharingService` | Façade centrale : enregistrement, recherche, création de Trip |
| `Trip` | Entité métier principale — contient l'état, les acteurs, le tarif |
| `Trip.TripBuilder` | Construit un `Trip` de façon fluente et validée |
| `TripState` | Définit les transitions d'état du Trip |
| `TripObserver` | Interface ABC notifiée à chaque changement de Trip |
| `User` | Classe de base abstraite : id, nom, contact, historique |
| `Rider` | Passager — reçoit les notifications de course |
| `Driver` | Chauffeur — reçoit les nouvelles courses disponibles |
| `Vehicle` | Véhicule du chauffeur (modèle, immatriculation, type) |
| `Location` | Coordonnées géographiques + calcul de distance |
| `PricingStrategy` | Calcul du tarif (2 implémentations) |
| `DriverMatchingStrategy` | Recherche de chauffeurs disponibles |

### Relations importantes

| Relation | Type | Multiplicité |
|---|---|---|
| `Trip` → `TripState` | Composition | 1 — 1 |
| `Trip` → `TripObserver` | Agrégation | 1 — * |
| `Trip` → `Rider` | Association | 1 — 1 |
| `Trip` → `Driver` | Association | 1 — 0..1 |
| `Driver` → `Vehicle` | Composition | 1 — 1 |
| `RideSharingService` → `Rider/Driver/Trip` | Agrégation | 1 — * |
| `RideSharingService` → `PricingStrategy` | Agrégation | 1 — 1 |
| `RideSharingService` → `DriverMatchingStrategy` | Agrégation | 1 — 1 |

---

## 4. Points forts du code actuel

- ✅ **Singleton thread-safe** : double-check locking avec `threading.Lock`
- ✅ **5 patterns bien implémentés** : reconnaissables et fonctionnels
- ✅ **Strategies interchangeables** : `set_pricing_strategy()` et `set_driver_matching_strategy()` à l'exécution
- ✅ **State pattern propre** : seuls les objets `TripState` appellent les setters de `Trip`
- ✅ **Builder avec validation** : `ValueError` si champs manquants
- ✅ **`TYPE_CHECKING`** : évite les imports circulaires proprement

---

## 5. Améliorations proposées

---

### Amélioration 1 — `TripBuilder` sorti de `Trip` (SRP)

**Problème :** `TripBuilder` est une classe interne de `Trip`. Cela viole le **principe de responsabilité unique (SRP)** : `Trip` ne devrait pas gérer sa propre construction.

**Code original (`trip.py`) :**
```python
class Trip:
    # ... logique métier du Trip ...

    class TripBuilder:          # ← classe interne = violation du SRP
        def __init__(self):
            self._id = str(uuid.uuid4())
            self._rider = None
            self._pickup_location = None
            self._dropoff_location = None
            self._fare = 0.0

        def with_rider(self, rider):
            self._rider = rider
            return self
        # ...
        def build(self):
            if self._rider is None or ...:
                raise ValueError("...")
            return Trip(self)
```

**Code proposé — `trip_builder.py` (nouveau fichier) :**
```python
# trip_builder.py
import uuid
from typing import Optional, TYPE_CHECKING
from rider import Rider
from location import Location

if TYPE_CHECKING:
    from trip import Trip

class TripBuilder:
    """
    Séparé de Trip pour respecter le SRP.
    Chaque classe a une seule responsabilité.
    """
    def __init__(self):
        self._id: str = str(uuid.uuid4())
        self._rider: Optional[Rider] = None
        self._pickup_location: Optional[Location] = None
        self._dropoff_location: Optional[Location] = None
        self._fare: float = 0.0

    def with_rider(self, rider: Rider) -> 'TripBuilder':
        self._rider = rider
        return self

    def with_pickup_location(self, loc: Location) -> 'TripBuilder':
        self._pickup_location = loc
        return self

    def with_dropoff_location(self, loc: Location) -> 'TripBuilder':
        self._dropoff_location = loc
        return self

    def with_fare(self, fare: float) -> 'TripBuilder':
        self._fare = fare
        return self

    def build(self) -> 'Trip':
        if not all([self._rider, self._pickup_location, self._dropoff_location]):
            raise ValueError("Rider, pickup et dropoff sont requis.")
        from trip import Trip
        return Trip(self)
```

**Usage dans `ride_sharing_service.py` :**
```python
# AVANT
trip = Trip.TripBuilder() \
    .with_rider(rider) \
    .with_pickup_location(pickup) \
    .with_dropoff_location(dropoff) \
    .with_fare(fare) \
    .build()

# APRÈS
from trip_builder import TripBuilder
trip = TripBuilder() \
    .with_rider(rider) \
    .with_pickup_location(pickup) \
    .with_dropoff_location(dropoff) \
    .with_fare(fare) \
    .build()
```

---

### Amélioration 2 — `CancelledState` manquant (cohérence State/Enum)

**Problème :** `TripStatus.CANCELLED` est défini dans l'enum mais **aucun état `CancelledState` n'existe** dans `trip_states.py`. Le cycle de vie est donc incomplet — impossible d'annuler une course proprement.

**Code original (`enums.py`) :**
```python
class TripStatus(Enum):
    REQUESTED  = "REQUESTED"
    ASSIGNED   = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED  = "COMPLETED"
    CANCELLED  = "CANCELLED"   # ← défini mais jamais utilisé !
```

**Code proposé — ajout dans `trip_states.py` :**
```python
class CancelledState(TripState):
    """
    Etat manquant. Correspond à TripStatus.CANCELLED.
    Bloque toute transition ultérieure.
    """
    def request(self, trip: 'Trip'):
        print("Ce trip a été annulé, impossible de le redemander.")

    def assign(self, trip: 'Trip', driver: 'Driver'):
        print("Impossible d'assigner un chauffeur à un trip annulé.")

    def start(self, trip: 'Trip'):
        print("Impossible de démarrer un trip annulé.")

    def end(self, trip: 'Trip'):
        print("Impossible de terminer un trip annulé.")
```

**Ajout de la méthode `cancel()` dans `Trip` :**
```python
# Dans trip.py
def cancel(self):
    """Annule le trip si l'état le permet (REQUESTED ou ASSIGNED)."""
    self._current_state.cancel(self)
    self._notify_observers()
```

**Ajout de `cancel()` dans `TripState` et états concernés :**
```python
# Dans TripState (abstract)
@abstractmethod
def cancel(self, trip: 'Trip'):
    pass

# Dans RequestedState — annulation autorisée
def cancel(self, trip: 'Trip'):
    trip.set_status(TripStatus.CANCELLED)
    trip.set_state(CancelledState())

# Dans AssignedState — annulation autorisée
def cancel(self, trip: 'Trip'):
    trip.set_status(TripStatus.CANCELLED)
    trip.set_state(CancelledState())

# Dans InProgressState — annulation interdite
def cancel(self, trip: 'Trip'):
    print("Impossible d'annuler un trip en cours.")
```

---

### Amélioration 3 — `Location.distance_to()` : distance euclidienne → Haversine

**Problème :** La distance est calculée avec la formule **euclidienne** (`sqrt(dx²+dy²)`). Sur des coordonnées GPS réelles (latitude/longitude), cette formule est **fausse** — elle ne tient pas compte de la courbure de la Terre.

**Code original (`location.py`) :**
```python
def distance_to(self, other: 'Location') -> float:
    dx = self._latitude - other._latitude
    dy = self._longitude - other._longitude
    return math.sqrt(dx * dx + dy * dy)  # Euclidean for simplicity
```

**Code proposé :**
```python
def distance_to(self, other: 'Location') -> float:
    """
    Formule de Haversine — distance réelle entre deux points GPS en km.
    Remplace la distance euclidienne incorrecte pour des coords GPS.
    """
    R = 6371.0  # rayon de la Terre en km
    lat1, lon1 = math.radians(self._latitude),  math.radians(self._longitude)
    lat2, lon2 = math.radians(other._latitude), math.radians(other._longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    return R * 2 * math.asin(math.sqrt(a))
```

---

### Amélioration 4 — Remplacer `print()` par `logging`

**Problème :** Le projet utilise `print()` partout pour les logs. En production, cela empêche de :
- filtrer par niveau (DEBUG / INFO / WARNING / ERROR)
- rediriger vers un fichier
- désactiver les logs facilement

**Code original (exemple dans `driver.py`) :**
```python
def set_status(self, status: DriverStatus):
    self._status = status
    print(f"Driver {self.get_name()} is now {status.value}")  # ← print()
```

**Code proposé :**
```python
import logging
logger = logging.getLogger(__name__)

def set_status(self, status: DriverStatus):
    self._status = status
    logger.info("Driver %s is now %s", self.get_name(), status.value)
```

**Configuration centralisée (à ajouter dans `ride_sharing_demo.py`) :**
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
```

---

## Amélioration 5 — RideSharingService trop grande (SRP / couche Repository)

### Problème

La classe `RideSharingService` gère actuellement **plusieurs responsabilités** :

- la **logique métier** :
  - créer un trajet (`createTrip`)
  - accepter une course
  - associer un driver et un rider

- le **stockage des données** :
  - `_riders`
  - `_drivers`
  - `_trips` (stockés dans des dictionnaires)

Cela constitue une **violation du principe SRP (Single Responsibility Principle)**.

Une classe ne devrait avoir **qu’une seule responsabilité**, c’est-à-dire **une seule raison de changer**.

Dans ce cas, si l’on souhaite :
- modifier la **logique métier**
- changer la **méthode de stockage** (par exemple utiliser une base de données)

il faudra modifier **la même classe**, ce qui rend le code **moins maintenable et moins évolutif**.

De plus, cette conception empêche de **remplacer facilement les dictionnaires par une vraie base de données** sans modifier `RideSharingService`.

### Solution

La solution consiste à **séparer les responsabilités** en introduisant une **couche Repository** chargée de la gestion des données.

On obtient alors :

- `RideSharingService` → responsable de la **logique métier**
- `RiderRepository`, `DriverRepository`, `TripRepository` → responsables du **stockage et de l'accès aux données**

Cette séparation permet de :

- respecter le **principe SRP**
- rendre le code **plus modulaire**
- **faciliter les tests unitaires**
- permettre de **changer facilement le système de stockage** (ex : base de données) sans modifier la logique métier.

**Code original (`ride_sharing_service.py`) :**
```python
class RideSharingService:
    def __init__(self):
        self._riders: Dict[str, Rider]  = {}   # ← stockage mélangé
        self._drivers: Dict[str, Driver] = {}  #   avec la logique
        self._trips: Dict[str, Trip]    = {}
```

**Code proposé — interface `TripRepository` :**
```python
# trip_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from trip import Trip

class TripRepository(ABC):
    """
    Interface de stockage des Trips.
    Respecte le DIP : le Service dépend d'une abstraction,
    pas d'un dict en dur.
    """
    @abstractmethod
    def save(self, trip: Trip) -> None: ...

    @abstractmethod
    def find_by_id(self, trip_id: str) -> Optional[Trip]: ...

    @abstractmethod
    def find_all(self) -> List[Trip]: ...


class InMemoryTripRepository(TripRepository):
    """Implémentation en mémoire (remplaçable par SQLTripRepository)."""
    def __init__(self):
        self._trips: dict = {}

    def save(self, trip: Trip) -> None:
        self._trips[trip.get_id()] = trip

    def find_by_id(self, trip_id: str) -> Optional[Trip]:
        return self._trips.get(trip_id)

    def find_all(self) -> List[Trip]:
        return list(self._trips.values())
```

**`RideSharingService` allégé :**
```python
class RideSharingService:
    def __init__(self, trip_repo: TripRepository, ...):
        self._trip_repository = trip_repo   # ← injection de dépendance
        # plus de dict internes
```

---

## 6. UML — Version améliorée

> Fichier : `diagramme_ameliore.puml` / `diagramme_ameliore.png`

```
[voir diagramme_ameliore.png]
```

### Différences clés par rapport au code actuel

| Élément | Avant | Après |
|---|---|---|
| `TripBuilder` | Classe **interne** de `Trip` | Classe **indépendante** (`trip_builder.py`) |
| `CancelledState` | **Absent** | **Ajouté** — cohérent avec `TripStatus.CANCELLED` |
| Stockage dans `RideSharingService` | `Dict` directement dans le service | Délégué à `TripRepository` / `UserRepository` |
| Interfaces | ABC implicites | Interfaces explicites (`ITripRepository`, `IUserRepository`) |
| `PriorityDriverMatchingStrategy` | Absente | Ajoutée comme exemple de nouvelle stratégie |

---

## 7. Résumé des améliorations

| # | Amélioration | Principe SOLID | Impact |
|---|---|---|---|
| 1 | `TripBuilder` → classe indépendante | **SRP** | Meilleure séparation, testabilité |
| 2 | Ajout de `CancelledState` | Cohérence métier | Cycle de vie complet |
| 3 | Distance Haversine | Correction fonctionnelle | Distances GPS réalistes |
| 4 | `print()` → `logging` | Bonne pratique | Logs configurables en prod |
| 5 | Couche `Repository` | **SRP + DIP** | Stockage découplé, extensible |

