#!/usr/bin/env python3
"""
fetch-exits.py — Query Supabase exits table along route corridors.

Reads routes-config.json, samples points every ~60 miles along each route,
queries find_exits_near RPC at each point, picks the best exit per interval,
and writes enriched JSON files to routes/.

Usage:
    python3 scripts/fetch-exits.py          # fetch all routes
    python3 scripts/fetch-exits.py chicago-to-atlanta  # fetch one route
"""

import json
import math
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────

INTERVAL_MILES = 60          # one recommended exit every ~60 miles
SEARCH_RADIUS_M = 30_000     # 30 km radius per sample point (captures exits near highways)
MILES_TO_METERS = 1_609.344
EARTH_RADIUS_MI = 3_958.8

ROOT = Path(__file__).resolve().parent.parent
ROUTES_DIR = ROOT / "routes"
CONFIG_PATH = Path(__file__).resolve().parent / "routes-config.json"


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


def interpolate_points(lat1, lng1, lat2, lng2, interval_miles):
    """
    Generate sample points along a great-circle path between two coordinates.
    Returns list of (lat, lng) tuples spaced ~interval_miles apart.
    Includes origin and destination.
    """
    # Haversine distance
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lng / 2) ** 2)
    total_miles = 2 * EARTH_RADIUS_MI * math.asin(math.sqrt(a))

    n_segments = max(1, round(total_miles / interval_miles))
    points = []
    for i in range(n_segments + 1):
        frac = i / n_segments
        lat = lat1 + frac * (lat2 - lat1)
        lng = lng1 + frac * (lng2 - lng1)
        points.append((lat, lng))
    return points, total_miles


def find_exits_near(lat, lng, radius_m, supabase_url, api_key):
    """Call the find_exits_near Supabase RPC function."""
    url = f"{supabase_url}/rest/v1/rpc/find_exits_near"
    payload = json.dumps({
        "p_lat": lat,
        "p_lng": lng,
        "p_radius": radius_m
    }).encode()
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  WARNING: RPC error at ({lat:.4f}, {lng:.4f}): {e.code} {body}")
        return []


def score_exit(exit_data):
    """
    Score an exit for quality. Higher = better.
    Prefer: named exits > generic, with exit_number > without, rest_area/service_plaza get bonus.
    """
    score = 0
    name = exit_data.get("exit_name", "")
    if name and name != "Highway Exit":
        score += 10
    if exit_data.get("exit_number"):
        score += 5
    stop_type = exit_data.get("stop_type", "")
    if stop_type == "service_plaza":
        score += 3
    elif stop_type == "rest_area":
        score += 2
    return score


def pick_best_exit(exits, already_used_ids):
    """Pick the highest-scored exit that hasn't been used yet."""
    candidates = [e for e in exits if e["exit_id"] not in already_used_ids]
    if not candidates:
        return None
    candidates.sort(key=score_exit, reverse=True)
    return candidates[0]


def build_corridor_points(route):
    """
    Build sample points along the route corridor using waypoints if available.
    Returns list of (lat, lng) tuples spaced ~INTERVAL_MILES apart.
    """
    # Build the full path: origin → waypoints → destination
    path = [(route["origin_lat"], route["origin_lng"])]
    for wp in route.get("waypoints", []):
        path.append((wp[0], wp[1]))
    path.append((route["destination_lat"], route["destination_lng"]))

    # Interpolate between each pair of path nodes
    all_points = [path[0]]
    for i in range(len(path) - 1):
        seg_points, _ = interpolate_points(
            path[i][0], path[i][1],
            path[i+1][0], path[i+1][1],
            INTERVAL_MILES
        )
        # Skip first point of each segment (already added)
        all_points.extend(seg_points[1:])

    return all_points


def fetch_route(route, supabase_url, api_key):
    """Fetch exits along a single route and write JSON."""
    slug = route["slug"]
    print(f"\n{'='*60}")
    print(f"  {route['origin']} → {route['destination']} ({slug})")
    print(f"  ~{route['miles']} mi | highways: {', '.join(route['highways'])}")
    print(f"{'='*60}")

    points = build_corridor_points(route)
    print(f"  Sample points: {len(points)} (every ~{INTERVAL_MILES} mi)")

    # Skip origin and destination city centers (first and last point)
    search_points = points[1:-1] if len(points) > 2 else points

    selected_exits = []
    used_ids = set()

    for i, (lat, lng) in enumerate(search_points):
        exits = find_exits_near(lat, lng, SEARCH_RADIUS_M, supabase_url, api_key)
        best = pick_best_exit(exits, used_ids)
        if best:
            used_ids.add(best["exit_id"])
            exit_entry = {
                "exit_id": best["exit_id"],
                "exit_number": best.get("exit_number") or "",
                "exit_name": best.get("exit_name", "Highway Exit"),
                "state": best.get("state", ""),
                "lat": best["lat"],
                "lng": best["lng"],
                "stop_type": best.get("stop_type", "exit_ramp")
            }
            selected_exits.append(exit_entry)
            label = exit_entry["exit_number"] or "—"
            print(f"  [{i+1}/{len(search_points)}] Exit {label} · {exit_entry['exit_name']} · {exit_entry['state']} ({lat:.4f}, {lng:.4f})")
        else:
            print(f"  [{i+1}/{len(search_points)}] No exit found near ({lat:.4f}, {lng:.4f})")

    # Sort exits by latitude (north→south or south→north depending on direction)
    if route["origin_lat"] > route["destination_lat"]:
        selected_exits.sort(key=lambda e: e["lat"], reverse=True)
    else:
        selected_exits.sort(key=lambda e: e["lat"])

    # For east-west routes (small lat diff, large lng diff), sort by longitude
    lat_diff = abs(route["origin_lat"] - route["destination_lat"])
    lng_diff = abs(route["origin_lng"] - route["destination_lng"])
    if lng_diff > lat_diff * 1.5:
        if route["origin_lng"] < route["destination_lng"]:
            selected_exits.sort(key=lambda e: e["lng"])
        else:
            selected_exits.sort(key=lambda e: e["lng"], reverse=True)

    # Script-owned fields (overwritten on every run): route_slug, origin,
    # destination, highway, miles, exit_count, exits.
    # Anything else in an existing JSON file (has_tolls, tolls_summary,
    # route_narrative, tips_narrative, ev_narrative, top_exits_summary,
    # any future fields) is preserved by merging.
    route_data = {
        "route_slug": slug,
        "origin": route["origin"],
        "destination": route["destination"],
        "highway": ", ".join(route["highways"]),
        "miles": route["miles"],
        "exit_count": len(selected_exits),
        "exits": selected_exits
    }

    out_path = ROUTES_DIR / f"{slug}.json"
    if out_path.exists():
        existing = json.loads(out_path.read_text())
        existing.update(route_data)  # script-owned fields overwrite
        route_data = existing
    out_path.write_text(json.dumps(route_data, indent=2) + "\n")
    print(f"\n  ✓ Wrote {len(selected_exits)} exits → {out_path.name}")
    return route_data


def main():
    env = load_env()
    supabase_url = env.get("SUPABASE_URL")
    api_key = env.get("SUPABASE_ANON_KEY")
    if not supabase_url or not api_key:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        routes = json.load(f)

    # Optional: filter to a single route
    if len(sys.argv) > 1:
        slug_filter = sys.argv[1]
        routes = [r for r in routes if r["slug"] == slug_filter]
        if not routes:
            print(f"ERROR: No route found with slug '{slug_filter}'")
            sys.exit(1)

    print(f"Fetching exits for {len(routes)} route(s)...")
    print(f"Interval: ~{INTERVAL_MILES} mi | Search radius: {SEARCH_RADIUS_M/1000:.0f} km")

    for route in routes:
        fetch_route(route, supabase_url, api_key)

    print(f"\nDone. Run 'node scripts/build-routes.js' to generate HTML pages.")


if __name__ == "__main__":
    main()
