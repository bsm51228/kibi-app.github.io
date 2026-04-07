#!/usr/bin/env python3
"""
enrich-pois.py — Enrich route JSON exits with Google Places POI data.

For each exit in each route JSON, calls Google Places (New) Nearby Search
to find gas stations, restaurants, and coffee shops within 1 mile (1600m).
Writes POI data directly into the route JSON files.

Usage:
    python3 scripts/enrich-pois.py                     # enrich all routes
    python3 scripts/enrich-pois.py chicago-to-atlanta   # enrich one route

Cost: ~1 API call per exit (~66 exits total = ~$1-2 at current pricing).
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────

SEARCH_RADIUS_M = 1_600      # 1 mile radius around each exit
MAX_RESULTS = 10              # top 10 places per exit
DELAY_BETWEEN_CALLS = 0.3    # seconds between API calls (avoid rate limits)

PLACE_TYPES = [
    "gas_station",
    "fast_food_restaurant",
    "restaurant",
    "cafe",
    "convenience_store"
]

FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.rating",
    "places.userRatingCount",
    "places.types",
    "places.nationalPhoneNumber",
    "places.regularOpeningHours"
])

ROOT = Path(__file__).resolve().parent.parent
ROUTES_DIR = ROOT / "routes"
PLACES_API_URL = "https://places.googleapis.com/v1/places:searchNearby"


def load_env():
    """Load .env from repo root."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        print("ERROR: .env not found at", env_path)
        sys.exit(1)
    env = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip()
    return env


def search_nearby(lat, lng, api_key):
    """Call Google Places (New) Nearby Search for all place types at once."""
    payload = json.dumps({
        "includedTypes": PLACE_TYPES,
        "maxResultCount": MAX_RESULTS,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": SEARCH_RADIUS_M
            }
        }
    }).encode()

    req = urllib.request.Request(PLACES_API_URL, data=payload, method="POST", headers={
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK
    })

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data.get("places", [])
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"    WARNING: Places API error: {e.code} {body[:200]}")
        return []


def simplify_place(place):
    """Extract the fields we want for the route JSON."""
    result = {
        "name": place.get("displayName", {}).get("text", "Unknown"),
        "types": categorize_types(place.get("types", [])),
        "rating": place.get("rating"),
        "review_count": place.get("userRatingCount"),
    }

    address = place.get("formattedAddress")
    if address:
        result["address"] = address

    phone = place.get("nationalPhoneNumber")
    if phone:
        result["phone"] = phone

    hours = place.get("regularOpeningHours", {})
    if hours.get("openNow") is not None:
        result["open_now"] = hours["openNow"]

    return result


def categorize_types(raw_types):
    """Map Google place types to simple categories."""
    categories = []
    type_set = set(raw_types)

    if "gas_station" in type_set or "truck_stop" in type_set:
        categories.append("gas")
    if type_set & {"fast_food_restaurant", "restaurant", "meal_takeaway"}:
        categories.append("food")
    if "cafe" in type_set or "coffee_shop" in type_set:
        categories.append("coffee")
    if "convenience_store" in type_set:
        categories.append("convenience")

    return categories if categories else ["other"]


def enrich_route(json_path, api_key):
    """Enrich a single route JSON with POI data."""
    data = json.loads(json_path.read_text())
    slug = data["route_slug"]

    print(f"\n{'='*60}")
    print(f"  {data['origin']} → {data['destination']} ({slug})")
    print(f"  {data['exit_count']} exits to enrich")
    print(f"{'='*60}")

    total_pois = 0
    for i, exit_data in enumerate(data["exits"]):
        label = exit_data.get("exit_number") or "—"
        name = exit_data.get("exit_name", "")

        # Skip if already enriched
        if exit_data.get("places"):
            print(f"  [{i+1}/{len(data['exits'])}] Exit {label} · {name} — already enriched, skipping")
            total_pois += len(exit_data["places"])
            continue

        places = search_nearby(exit_data["lat"], exit_data["lng"], api_key)
        simplified = [simplify_place(p) for p in places]
        exit_data["places"] = simplified
        total_pois += len(simplified)

        # Summary
        gas = sum(1 for p in simplified if "gas" in p["types"])
        food = sum(1 for p in simplified if "food" in p["types"])
        coffee = sum(1 for p in simplified if "coffee" in p["types"])
        print(f"  [{i+1}/{len(data['exits'])}] Exit {label} · {name} — {len(simplified)} places (gas:{gas} food:{food} coffee:{coffee})")

        time.sleep(DELAY_BETWEEN_CALLS)

    json_path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"\n  ✓ Wrote {total_pois} total POIs → {json_path.name}")
    return total_pois


def main():
    env = load_env()
    api_key = env.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_PLACES_API_KEY must be set in .env")
        sys.exit(1)

    # Find route JSON files
    json_files = sorted(ROUTES_DIR.glob("*.json"))
    if not json_files:
        print("ERROR: No JSON files found in routes/")
        sys.exit(1)

    # Optional: filter to a single route
    if len(sys.argv) > 1:
        slug_filter = sys.argv[1]
        json_files = [f for f in json_files if f.stem == slug_filter]
        if not json_files:
            print(f"ERROR: No route found with slug '{slug_filter}'")
            sys.exit(1)

    total_exits = sum(
        len(json.loads(f.read_text()).get("exits", []))
        for f in json_files
    )
    print(f"Enriching {len(json_files)} route(s) with {total_exits} total exits...")
    print(f"Estimated API calls: ~{total_exits} (~${total_exits * 0.02:.2f})")

    grand_total = 0
    for json_path in json_files:
        grand_total += enrich_route(json_path, api_key)

    print(f"\nDone. {grand_total} total POIs across all routes.")
    print("Run 'node scripts/build-routes.js' to regenerate HTML pages.")


if __name__ == "__main__":
    main()
