#!/usr/bin/env python3
"""
generate_routes.py
Reads kibi_exits_master.csv and outputs one JSON file per route into routes/.
Filter strategy: highway partial match + state + bounding box (primary),
fall back to state + bounding box only if primary yields < 5 exits.
"""

import os
import json
import pandas as pd

CSV_PATH = "../kibi_exits_master.csv"
OUT_DIR  = "routes"

ROUTES = [
    {
        "slug": "chicago-to-atlanta",
        "origin": "Chicago, IL",
        "destination": "Atlanta, GA",
        "highway": "I-65",
        "states": ["IL", "IN", "KY", "TN", "AL", "GA"],
        "lat": (33.5, 41.9),
        "lng": (-88.5, -85.5),
    },
    {
        "slug": "new-york-to-miami",
        "origin": "New York, NY",
        "destination": "Miami, FL",
        "highway": "I-95",
        "states": ["NY", "NJ", "DE", "MD", "VA", "NC", "SC", "GA", "FL"],
        "lat": (25.7, 40.7),
        "lng": (-80.5, -73.9),
    },
    {
        "slug": "los-angeles-to-las-vegas",
        "origin": "Los Angeles, CA",
        "destination": "Las Vegas, NV",
        "highway": "I-15",
        "states": ["CA", "NV"],
        "lat": (34.0, 36.2),
        "lng": (-117.5, -115.1),
    },
    {
        "slug": "dallas-to-houston",
        "origin": "Dallas, TX",
        "destination": "Houston, TX",
        "highway": "I-45",
        "states": ["TX"],
        "lat": (29.7, 32.8),
        "lng": (-97.0, -95.3),
    },
    {
        "slug": "atlanta-to-nashville",
        "origin": "Atlanta, GA",
        "destination": "Nashville, TN",
        "highway": "I-24",
        "states": ["GA", "TN"],
        "lat": (33.7, 36.2),
        "lng": (-86.8, -84.3),
    },
    {
        "slug": "chicago-to-nashville",
        "origin": "Chicago, IL",
        "destination": "Nashville, TN",
        "highway": "I-65",
        "states": ["IL", "IN", "KY", "TN"],
        "lat": (36.1, 41.9),
        "lng": (-87.5, -85.5),
    },
    {
        "slug": "new-york-to-washington-dc",
        "origin": "New York, NY",
        "destination": "Washington, DC",
        "highway": "I-95",
        "states": ["NY", "NJ", "DE", "MD", "DC"],
        "lat": (38.8, 40.7),
        "lng": (-77.1, -73.9),
    },
    {
        "slug": "los-angeles-to-san-francisco",
        "origin": "Los Angeles, CA",
        "destination": "San Francisco, CA",
        "highway": "US-101",
        "states": ["CA"],
        "lat": (34.0, 37.8),
        "lng": (-122.5, -118.2),
    },
    {
        "slug": "denver-to-las-vegas",
        "origin": "Denver, CO",
        "destination": "Las Vegas, NV",
        "highway": "I-70",
        "states": ["CO", "UT", "NV"],
        "lat": (36.1, 39.7),
        "lng": (-115.2, -104.9),
    },
    {
        "slug": "atlanta-to-orlando",
        "origin": "Atlanta, GA",
        "destination": "Orlando, FL",
        "highway": "I-75",
        "states": ["GA", "FL"],
        "lat": (28.5, 33.7),
        "lng": (-82.5, -81.3),
    },
]


def bbox_state_filter(df, route):
    lat_min, lat_max = route["lat"]
    lng_min, lng_max = route["lng"]
    mask = (
        df["state"].isin(route["states"])
        & df["lat"].between(lat_min, lat_max)
        & df["lng"].between(lng_min, lng_max)
    )
    return df[mask].copy()


def highway_filter(df, route):
    hw = route["highway"].upper()
    hw_mask = df["highway"].str.upper().str.startswith(hw, na=False)
    return df[hw_mask].copy()


def prioritize_and_trim(df, top_n=20):
    # Sort by lat ascending, but float non-empty stop_type to the top
    # within each approximate lat band (every 0.5 degrees)
    df = df.copy()
    df["_has_type"] = df["stop_type"].notna() & (df["stop_type"].str.strip() != "")
    df = df.sort_values(["lat", "_has_type"], ascending=[True, False])
    df = df.drop(columns=["_has_type"])
    return df.head(top_n)


def row_to_dict(row):
    return {
        "exit_id":     str(row["exit_id"]) if pd.notna(row["exit_id"]) else "",
        "exit_number": str(row["exit_number"]) if pd.notna(row["exit_number"]) else "",
        "exit_name":   str(row["exit_name"]) if pd.notna(row["exit_name"]) else "",
        "state":       str(row["state"]) if pd.notna(row["state"]) else "",
        "lat":         round(float(row["lat"]), 6),
        "lng":         round(float(row["lng"]), 6),
        "stop_type":   str(row["stop_type"]) if pd.notna(row["stop_type"]) and str(row["stop_type"]).strip() else "",
    }


def main():
    print(f"Loading {CSV_PATH} …")
    df = pd.read_csv(CSV_PATH, dtype=str, low_memory=False)

    # Cast lat/lng to float for numeric filtering
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    df = df.dropna(subset=["lat", "lng"])

    os.makedirs(OUT_DIR, exist_ok=True)

    skipped = []
    generated = []

    for route in ROUTES:
        slug = route["slug"]

        # Primary filter: highway + state + bbox
        primary = bbox_state_filter(highway_filter(df, route), route)
        if len(primary) >= 5:
            result = prioritize_and_trim(primary)
            method = "highway+state+bbox"
        else:
            # Fallback: state + bbox only
            fallback = bbox_state_filter(df, route)
            if len(fallback) >= 5:
                result = prioritize_and_trim(fallback)
                method = "bbox+state (fallback — highway col sparse)"
                print(f"  ⚠  {slug}: primary={len(primary)} exits → fallback bbox+state={len(fallback)} exits")
            else:
                print(f"  ✗  SKIPPED {slug}: only {len(fallback)} exits after fallback (need ≥5)")
                skipped.append({"slug": slug, "exits_found": len(fallback)})
                continue

        exits = [row_to_dict(r) for _, r in result.iterrows()]
        payload = {
            "route_slug":    slug,
            "origin":        route["origin"],
            "destination":   route["destination"],
            "highway":       route["highway"],
            "filter_method": method,
            "exit_count":    len(exits),
            "exits":         exits,
        }

        out_path = os.path.join(OUT_DIR, f"{slug}.json")
        with open(out_path, "w") as f:
            json.dump(payload, f, indent=2)

        print(f"  ✓  {slug}: {len(exits)} exits  [{method}]  → {out_path}")
        generated.append({"slug": slug, "exit_count": len(exits), "method": method})

    print()
    print(f"Generated: {len(generated)} JSON files")
    if skipped:
        print(f"Skipped ({len(skipped)}):")
        for s in skipped:
            print(f"  - {s['slug']} ({s['exits_found']} exits found)")
    else:
        print("No routes skipped.")


if __name__ == "__main__":
    main()
