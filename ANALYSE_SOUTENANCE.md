# Analyse du projet RideSharing — Préparation Soutenance

---

## 1. Analyse du projet

### Architecture globale

Le projet implémente un **service de covoiturage / VTC** en Python orienté objet.
Il est structuré autour de **5 design patterns** clairement identifiables :

| Pattern | Classe(s) concernée(s) |
|---|---|
| **Singleton** | `RideSharingService` |
| **Builder** | `Trip.TripBuilder` |
| **Strategy** | `PricingStrategy`, `DriverMatchingStrategy` |
| **State** | `TripState` (+ 4 états concrets) |
| **Observer** | `TripObserver` → `User` → `Rider`, `Driver` |

---

### Rôle des principales classes

| Classe | Rôle |
|---|---|
| `RideSharingService` | Façade principale / Singleton. Orchestre toutes les opérations. |
| `Trip` | Entité centrale. Représente un trajet avec ses états. |
| `Trip.TripBuilder` | Construit un `Trip` par étapes (Builder). |
| `TripState` / états | Gère le cycle de vie de `Trip` (State pattern). |
| `Rider` / `Driver` | Utilisateurs du système, héritent de `User`. |
| `User` | Classe abstraite commune : id, nom, contact, historique. |
| `TripObserver` | Interface Observer : notifié à chaque changement de `Trip`. |
| `PricingStrategy` | Calcul du tarif (Strategy). Deux implémentations. |
| `DriverMatchingStrategy` | Recherche de chauffeurs disponibles (Strategy). |
| `Location` | Coordonnées géographiques + calcul de distance. |
| `Vehicle` | Véhicule du chauffeur (modèle, immatriculation, type). |
| `RideSharingServiceDemo` | Classe de démonstration / point d'entrée. |

---

### Relations entre classes

```
TripObserver (ABC)
    └── User (abstract)
            ├── Rider
            └── Driver ──────── Vehicle ──── RideType (enum)
                    └── Location

Trip ──── TripStatus (enum)
     ──── TripState (ABC)
              ├── RequestedState
              ├── AssignedState
              ├── InProgressState
              └── CompletedState
     ──── Rider
     ──── Driver
     ──── Location (pickup + dropoff)
     ──── [TripObserver] (liste)

RideSharingService (Singleton)
     ──── [Rider]
     ──── [Driver]
     ──── [Trip]
     ──── PricingStrategy (ABC)
              ├── FlatRatePricingStrategy
              └── VehicleBasedPricingStrategy
     ──── DriverMatchingStrategy (ABC)
              └── NearestDriverMatchingStrategy
```

---

### Points forts du code

1. **Design patterns bien appliqués** : les 5 patterns sont proprement implémentés.
2. **Singleton thread-safe** : utilisation de `threading.Lock` avec double-check locking.
3. **Strategy interchangeable** : les stratégies de prix et de matching peuvent être changées à l'exécution.
4. **State pattern propre** : transitions d'état protégées, seuls les objets `TripState` appellent les setters de `Trip`.
5. **Observer découplé** : `TripObserver` est une ABC, `User` implémente l'interface sans couplage fort.
6. **Builder lisible** : syntaxe fluente `with_rider(...).with_pickup(...).build()`.
7. **TYPE_CHECKING** : utilisation correcte pour éviter les imports circulaires.

---

### Limites et problèmes potentiels

1. **`TripBuilder` est une classe interne de `Trip`** : viole le principe de **séparation des responsabilités (SRP)**. Le builder devrait être une classe indépendante.

2. **`TripStatus.CANCELLED` n'a pas d'état correspondant** : `CancelledState` est absent alors que l'enum prévoit `CANCELLED`.

3. **`RideSharingService` fait trop de choses** (God class) : enregistrement, recherche, création de Trip, gestion des statuts, historique... Ce n'est pas conforme au **SRP**.

4. **Pas d'interfaces explicites** : `TripObserver`, `PricingStrategy`, `DriverMatchingStrategy` sont des ABC. En Python, on préfère souvent `Protocol` pour plus de souplesse, ou des interfaces explicites pour respecter le **DIP** (Dependency Inversion Principle).

5. **Couplage fort sur les classes concrètes** : `RideSharingService` dépend directement de `Rider`, `Driver`, `Trip` (classes concrètes) plutôt que d'abstractions.

6. **Stockage en mémoire dans le Service** : les dictionnaires `_riders`, `_drivers`, `_trips` sont directement dans le Service. Il n'y a pas de couche **Repository**, ce qui rendrait difficile le passage à une vraie base de données.

7. **`print()` utilisé pour les logs** : devrait être remplacé par le module `logging`.

8. **Pas de gestion des erreurs complète** : certaines méthodes lèvent `KeyError` directement, sans messages clairs.

9. **`Location.distance_to` utilise la distance euclidienne** : non réaliste pour des coordonnées GPS réelles (devrait utiliser la formule de Haversine).

---

## 2. Propositions d'améliorations

### A. Séparer le Builder (SRP)

```python
# PROPOSITION D'AMELIORATION
# CODE ORIGINAL :
class Trip:
    class TripBuilder:  # Classe interne dans Trip
        ...

# CODE PROPOSE :
# TripBuilder devient une classe de premier niveau (fichier trip_builder.py)
# Avantage : respect du SRP, meilleure testabilité, plus lisible
class TripBuilder:
    """
    # MODIFICATION : Déplacé hors de Trip pour respecter le SRP.
    # Chaque classe a une seule responsabilité.
    """
    def __init__(self):
        self._id = str(uuid.uuid4())
        self._rider = None
        self._pickup_location = None
        self._dropoff_location = None
        self._fare = 0.0

    def with_rider(self, rider: Rider) -> 'TripBuilder':
        self._rider = rider
        return self

    # ... etc (identique)

    def build(self) -> 'Trip':
        if not all([self._rider, self._pickup_location, self._dropoff_location]):
            raise ValueError("Rider, pickup et dropoff sont requis.")
        return Trip(self)
```

---

### B. Ajouter CancelledState (état manquant)

```python
# PROPOSITION D'AMELIORATION
# CODE ORIGINAL : CancelledState absent, TripStatus.CANCELLED défini mais inutilisé.

# CODE PROPOSE :
class CancelledState(TripState):
    """
    # MODIFICATION : Etat manquant correspondant à TripStatus.CANCELLED.
    # Empêche toute transition depuis un trip annulé.
    """
    def request(self, trip): print("Trip annulé, impossible de redemander.")
    def assign(self, trip, driver): print("Trip annulé.")
    def start(self, trip): print("Trip annulé.")
    def end(self, trip): print("Trip annulé.")
```

---

### C. Couche Repository (SRP / DIP)

```python
# PROPOSITION D'AMELIORATION
# CODE ORIGINAL : RideSharingService stocke directement les entités.
# self._riders: Dict[str, Rider] = {}
# self._drivers: Dict[str, Driver] = {}
# self._trips: Dict[str, Trip] = {}

# CODE PROPOSE :
from abc import ABC, abstractmethod

class ITripRepository(ABC):
    """
    # MODIFICATION : Interface Repository pour les Trips.
    # Permet de changer le stockage (mémoire → BDD) sans modifier le Service.
    # Respecte le DIP : le Service dépend d'une abstraction.
    """
    @abstractmethod
    def save(self, trip: Trip): pass

    @abstractmethod
    def find_by_id(self, trip_id: str) -> Optional[Trip]: pass

    @abstractmethod
    def find_all(self) -> List[Trip]: pass


class InMemoryTripRepository(ITripRepository):
    def __init__(self):
        self._trips: Dict[str, Trip] = {}

    def save(self, trip: Trip):
        self._trips[trip.get_id()] = trip

    def find_by_id(self, trip_id: str) -> Optional[Trip]:
        return self._trips.get(trip_id)

    def find_all(self) -> List[Trip]:
        return list(self._trips.values())
```

---

### D. Interfaces explicites (DIP)

```python
# PROPOSITION D'AMELIORATION
# CODE ORIGINAL : RideSharingService dépend des classes concrètes PricingStrategy, DriverMatchingStrategy (ABC)

# CODE PROPOSE :
from typing import Protocol

class IPricingStrategy(Protocol):
    """
    # MODIFICATION : Utilisation de Protocol (Python 3.8+) comme interface explicite.
    # Plus Pythonique que ABC pour les stratégies.
    """
    def calculate_fare(self, pickup: Location, dropoff: Location, ride_type: RideType) -> float: ...
```

---

### E. Logging au lieu de print()

```python
# PROPOSITION D'AMELIORATION
# CODE ORIGINAL : print(f"Driver {self.get_name()} is now {status.value}")

# CODE PROPOSE :
import logging
logger = logging.getLogger(__name__)

# MODIFICATION : Remplacement de print() par logging.
# Permet de configurer le niveau de log, de rediriger vers un fichier, etc.
logger.info(f"Driver {self.get_name()} is now {status.value}")
```

---

## 3. Diagrammes UML

Les deux diagrammes PlantUML sont disponibles dans le fichier `diagramme_uml.puml` :

- **Diagramme 1** : `@startuml RideSharing_Actuel` — Code tel qu'il existe
- **Diagramme 2** : `@startuml RideSharing_Ameliore` — Version avec améliorations

Pour les visualiser :
```bash
# Option 1 : PlantUML en ligne → https://www.plantuml.com/plantuml/uml/
# Option 2 : Plugin IntelliJ/PyCharm PlantUML Integration
# Option 3 : CLI
java -jar plantuml.jar diagramme_uml.puml
```

---

## 4. Structure pour la présentation orale

### Plan suggéré (30 min)

---

**1. Introduction (3 min)**
- Contexte : simulation d'un service VTC type Uber
- Objectif : illustrer les design patterns en Python
- Technologies : Python 3, POO, ABC, typing

---

**2. Architecture actuelle (5 min)**
- Présenter les 3 couches : Domaine (Trip, User...), Stratégies, Service
- Montrer le schéma de dépendances entre fichiers
- Souligner l'utilisation de `TYPE_CHECKING` pour éviter les imports circulaires

---

**3. UML du projet actuel (5 min)**
- Présenter le diagramme `RideSharing_Actuel`
- Identifier les 5 patterns visuellement
- Expliquer les relations clés (composition vs agrégation vs dépendance)

---

**4. Analyse des patterns (8 min)**

| Pattern | Comment l'expliquer |
|---|---|
| **Singleton** | `_instance + _lock` → une seule instance du service |
| **Builder** | `Trip.TripBuilder` → construction par étapes fluente |
| **Strategy** | `PricingStrategy` + `DriverMatchingStrategy` → algorithmes interchangeables |
| **State** | `TripState` → comportement de `Trip` change selon l'état courant |
| **Observer** | `TripObserver` → `Rider` et `Driver` notifiés automatiquement |

---

**5. Analyse critique (4 min)**
- Points forts : thread-safety, patterns propres, découplage Observer
- Limites : God class `RideSharingService`, Builder interne, `CancelledState` manquant, `print()` au lieu de `logging`

---

**6. Améliorations proposées + UML amélioré (5 min)**
- Présenter le diagramme `RideSharing_Ameliore`
- Montrer les nouvelles interfaces (`ITripRepository`, `IUser`, `IPricingStrategy`)
- Expliquer l'apport des principes SOLID (SRP, DIP)

---

**7. Discussion technique (questions) (5 min)**

Questions probables :
- *Pourquoi Singleton et pas un module Python ?* → Thread-safety, compatibilité POO
- *Quelle différence entre Strategy et State ?* → Strategy = algorithme interchangeable, State = comportement lié à l'état interne
- *Comment tester `RideSharingService` ?* → Injection de dépendances + repositories mockables
- *Pourquoi `TYPE_CHECKING` ?* → Éviter les imports circulaires tout en gardant les annotations de type

---

## 5. Résumé des fichiers

| Fichier | Pattern(s) | Rôle |
|---|---|---|
| `ride_sharing_service.py` | Singleton, Strategy | Service principal |
| `trip.py` | Builder, State, Observer | Entité Trip + Builder interne |
| `trip_states.py` | State | 4 états du cycle de vie |
| `trip_observer.py` | Observer | Interface ABC Observer |
| `pricing_strategy.py` | Strategy | 2 algorithmes de tarification |
| `driver_matching_strategy.py` | Strategy | 1 algorithme de matching |
| `user.py` | Observer | Classe de base User |
| `rider.py` | Observer | Passager |
| `driver.py` | Observer | Chauffeur |
| `vehicle.py` | — | Véhicule du chauffeur |
| `location.py` | — | Coordonnées + distance |
| `enums.py` | — | 3 enums : RideType, TripStatus, DriverStatus |
| `ride_sharing_demo.py` | — | Démonstration du système |

