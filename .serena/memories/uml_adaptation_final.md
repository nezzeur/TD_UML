# Adaptation UML - DynamicPriceStrategy.py

## État Réel du Code

Le fichier `DynamicPriceStrategy.py` **NE CONTIENT PAS DE CLASSE** d'implémentation de pricing.
C'est un **module d'analyse et comparaison** avec :
- ✅ Constantes tarifaires
- ✅ Fonctions utilitaires
- ✅ Script de démonstration

## Modifications UML Effectuées

### ✅ Suppression
- Supprimé la classe `DynamicPricingStrategy <<NEW>>`
- Supprimé l'héritage `PricingStrategy <|-- DynamicPricingStrategy`
- Supprimé les références dans `RideSharingService`

### ✅ Ajout
- Note de bas de page expliquant le module réel
- Description détaillée des 5 composants
- Formule tarifaire documentée

## Structure du Module

| Composant | Type | Rôle |
|-----------|------|------|
| `BASE_FARE` | Constante | 1.50€ (prise en charge) |
| `RATE_PER_KM` | Constante | 1.00€/km |
| `RATE_PER_MIN` | Constante | 0.20€/min |
| `FLOOR_PRICE` | Constante | 4.90€ (minimum) |
| `DISCOUNT_VS_UBER` | Constante | 0.92 (8% moins cher) |
| `get_route_info()` | Fonction | Distance réelle (ORS + Haversine) |
| `get_uber_prices()` | Fonction | Simulation grilles Uber Paris |
| `calculate_our_price()` | Fonction | Tarif optimal |
| `_haversine()` | Fonction | Distance géographique |
| `run_comparison()` | Fonction | Script démo (3 trajets Paris) |
| `_fmt()`, `_bar()`, `_sep()` | Fonctions | Helpers d'affichage |

## Formule de Tarification

```
prix = BASE_FARE + (distance * RATE_PER_KM) + (durée * RATE_PER_MIN)
prix = max(prix, FLOOR_PRICE)
prix = min(prix par rapport à Uber X * 0.92)
```

## Logique: Position Compétitive

1. Calcule le tarif réel basé sur coûts
2. Compare avec Uber X (grille réelle Paris 2024)
3. Position à 8% sous Uber X (DISCOUNT_VS_UBER = 0.92)
4. Respecte le prix plancher (FLOOR_PRICE = 4.90€)
5. Démontre sur 3 trajets réels de Paris

## Résultat UML

Le diagramme reflète maintenant la réalité :
- ✅ Pas de classe `DynamicPricingStrategy` 
- ✅ Module documenté comme outil d'analyse
- ✅ Pas d'intégration au pattern Strategy (c'est un standalone)
- ✅ Utilitaires clairement listés

Le diagramme UML reste centré sur l'architecture du **service ride-sharing** réel.
