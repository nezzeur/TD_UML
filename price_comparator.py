import requests
import math
from typing import Optional

# ================================================================
# CONFIGURATION
# ================================================================
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjhlZmZjMjc0YzJlZDRkMzU4MGQyYWE5MjE2YWFiNzIyIiwiaCI6Im11cm11cjY0In0="

# ================================================================
# TRAJETS À COMPARER
# ================================================================
TRIPS = [
    {
        "label":     "Paris Centre → Champs-Élysées",
        "start_lat": 48.8566, "start_lon": 2.3522,
        "end_lat":   48.8738, "end_lon":   2.2950,
    },
    {
        "label":     "Gare du Nord → Tour Eiffel",
        "start_lat": 48.8809, "start_lon": 2.3553,
        "end_lat":   48.8584, "end_lon":   2.2945,
    },
    {
        "label":     "Paris Centre → CDG Aéroport",
        "start_lat": 48.8566, "start_lon": 2.3522,
        "end_lat":   49.0097, "end_lon":   2.5479,
    },
]

# ================================================================
# NOTRE MODELE DE PRICING
# ================================================================
BASE_FARE        = 1.50   # Prise en charge fixe (€)
RATE_PER_KM      = 1.00   # Prix par km (€)
RATE_PER_MIN     = 0.20   # Prix par minute (€)
FLOOR_PRICE      = 4.90   # Prix plancher absolu
DISCOUNT_VS_UBER = 0.92   # 8% sous la médiane Uber X


# ================================================================
# 1. OPENROUTESERVICE — Vraie distance et durée routière
# ================================================================

def get_route_info(start_lat, start_lon, end_lat, end_lon) -> dict:
    """
    Appelle OpenRouteService pour obtenir la vraie distance
    et durée routière (pas à vol d'oiseau).
    Fallback sur Haversine si l'API est inaccessible.
    """
    try:
        response = requests.get(
            "https://api.openrouteservice.org/v2/directions/driving-car",
            headers={"Authorization": ORS_API_KEY},
            params={
                "start": f"{start_lon},{start_lat}",
                "end":   f"{end_lon},{end_lat}",
            },
            timeout=8
        )

        if response.status_code == 200:
            data = response.json()
            segment = data["features"][0]["properties"]["segments"][0]
            dist_km      = round(segment["distance"] / 1000, 2)
            duration_min = round(segment["duration"] / 60, 1)
            print(f" Route réelle : {dist_km} km, {duration_min} min")
            return {"dist_km": dist_km, "duration_min": duration_min, "source": "ors"}
        else:
            print(f"  [ORS] ❌ Erreur {response.status_code} — fallback Haversine")

    except requests.exceptions.Timeout:
        print(" Timeout — fallback Haversine")
    except Exception as e:
        print(f" Erreur : {e} — fallback Haversine")

    # Fallback : distance à vol d'oiseau × 1.3 (correction route urbaine)
    dist_km      = round(_haversine(start_lat, start_lon, end_lat, end_lon) * 1.3, 2)
    duration_min = round(dist_km * 3.5, 1)
    print(f"  [Fallback] Distance estimée : {dist_km} km, {duration_min} min")
    return {"dist_km": dist_km, "duration_min": duration_min, "source": "haversine"}


# ================================================================
# 2. SIMULATION DES PRIX UBER (grilles Paris 2024)
# ================================================================

def get_uber_prices(dist_km: float, duration_min: float) -> list:
    """
    Simule les prix Uber Paris basés sur les vraies grilles tarifaires 2024.
    Uber X    : base 1.20€ + 1.45€/km + 0.28€/min  (min 5€)
    Uber Comfort : base 2.00€ + 1.85€/km + 0.35€/min (min 7€)
    Uber Van  : base 3.00€ + 2.25€/km + 0.40€/min  (min 10€)
    """
    def calc(base, rate_km, rate_min, minimum):
        return round(max(base + rate_km * dist_km + rate_min * duration_min, minimum), 2)

    uber_x_price       = calc(1.20, 1.45, 0.28, 5.00)
    uber_comfort_price = calc(2.00, 1.85, 0.35, 7.00)
    uber_van_price     = calc(3.00, 2.25, 0.40, 10.00)

    # Fourchette ±10% pour simuler la variabilité réelle
    return [
        {
            "name":  "Uber X",
            "low":   round(uber_x_price * 0.92, 2),
            "mid":   uber_x_price,
            "high":  round(uber_x_price * 1.10, 2),
        },
        {
            "name":  "Uber Comfort",
            "low":   round(uber_comfort_price * 0.92, 2),
            "mid":   uber_comfort_price,
            "high":  round(uber_comfort_price * 1.10, 2),
        },
        {
            "name":  "Uber Van",
            "low":   round(uber_van_price * 0.92, 2),
            "mid":   uber_van_price,
            "high":  round(uber_van_price * 1.10, 2),
        },
    ]


# ================================================================
# 3. CALCUL DE NOTRE PRIX OPTIMAL
# ================================================================

def calculate_our_price(dist_km: float, duration_min: float, uber_prices: list) -> dict:
    """
    Prix final = max(coût réel, 8% sous Uber X, plancher absolu)
    """
    cost_based   = BASE_FARE + RATE_PER_KM * dist_km + RATE_PER_MIN * duration_min
    uber_x_mid   = uber_prices[0]["mid"]
    market_based = uber_x_mid * DISCOUNT_VS_UBER

    final = round(max(cost_based, market_based, FLOOR_PRICE), 2)

    return {
        "cost_based":     round(cost_based, 2),
        "market_based":   round(market_based, 2),
        "uber_x_mid":     uber_x_mid,
        "final":          final,
        "floor_applied":  final == FLOOR_PRICE,
        "saving":         round(uber_x_mid - final, 2),
        "saving_pct":     round((1 - final / uber_x_mid) * 100, 1),
    }


# ================================================================
# 4. UTILITAIRES
# ================================================================

def _haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return round(R * 2 * math.asin(math.sqrt(a)), 2)

def _fmt(p): return f"{p:.2f} €"
def _bar(val, max_val, width=20):
    filled = int(val / max_val * width)
    return "█" * filled + "░" * (width - filled)
def _sep(c="─", w=64): print(c * w)


# ================================================================
# 5. AFFICHAGE PRINCIPAL
# ================================================================

def run_comparison():
    print("\n" + "═" * 64)
    print("  COMPARATEUR DE PRIX — Notre App vs Uber  (Paris)")
    print("  Distances via OpenRouteService (routes réelles)")
    print("═" * 64)

    results = []

    for trip in TRIPS:
        print(f"\n {trip['label']}")
        _sep()

        # Vraie distance via ORS
        route = get_route_info(
            trip["start_lat"], trip["start_lon"],
            trip["end_lat"],   trip["end_lon"]
        )
        dist_km      = route["dist_km"]
        duration_min = route["duration_min"]
        src_tag      = "ORS" if route["source"] == "ors" else "Estimé"
        print(f"  {src_tag} → {dist_km} km  |  {duration_min:.0f} min en voiture")

        # Prix Uber simulés (grilles réelles)
        uber = get_uber_prices(dist_km, duration_min)

        # Notre prix
        our = calculate_our_price(dist_km, duration_min, uber)

        # Référence pour les barres
        max_price = uber[2]["high"]

        # Tableau comparatif
        print(f"\n  {'Offre':<20} {'Min':>7}  {'Médiane':>8}  {'Max':>7}  Visualisation")
        _sep("·", 64)

        for u in uber:
            bar = _bar(u["mid"], max_price)
            print(f"  {u['name']:<20} {_fmt(u['low']):>7}  {_fmt(u['mid']):>8}  {_fmt(u['high']):>7}  {bar}")

        # Notre prix avec mise en valeur
        our_bar = _bar(our["final"], max_price)
        print(f"  {'Notre App':<20} {'':>7}  {_fmt(our['final']):>8}  {'':>7}  {our_bar}  ← NOTRE PRIX")

        # Verdict
        print(f"\n Économie vs Uber X : -{_fmt(our['saving'])}  ({our['saving_pct']}% moins cher)")
        if our["floor_applied"]:
            print(f"Prix plancher appliqué ({_fmt(FLOOR_PRICE)})")

        results.append({
            "label": trip["label"],
            "dist":  dist_km,
            "uber_x": our["uber_x_mid"],
            "notre":  our["final"],
            "saving": our["saving"],
        })
        _sep()

    # Récapitulatif final
    print("\n" + "═" * 64)
    print("   📊  RÉCAPITULATIF")
    print("═" * 64)
    print(f"  {'Trajet':<35} {'Uber X':>8}  {'Nous':>8}  {'Écart':>8}")
    _sep("·", 64)
    total_saving = 0
    for r in results:
        label = r["label"][:34]
        print(f"  {label:<35} {_fmt(r['uber_x']):>8}  {_fmt(r['notre']):>8}  -{_fmt(r['saving']):>7}")
        total_saving += r["saving"]
    _sep()
    print(f"  {'Économie totale sur 3 trajets':<35} {'':>8}  {'':>8}  -{_fmt(total_saving):>7}")
    print("═" * 64)
    print("\n Analyse terminée — Notre app est systématiquement moins chère.\n")


# ================================================================
# POINT D'ENTRÉE
# ================================================================
if __name__ == "__main__":
    run_comparison()