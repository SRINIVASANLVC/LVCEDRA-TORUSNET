import csv
import sys
from datetime import datetime
import os
import time
import json

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from modules.planetary_modulation.load_modulation_zones import load_modulation_zones
from modules.planetary_modulation.compute_planetary_info import compute_planetary_info
from modules.geometry.flatten_city_data import flatten_city_data



def load_utc_file(filepath, target_city=None):
    results = []
    try:
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                city = row.get("city_name")
                raw_ts = row.get("incorporation_timestamp_utc")
                FoundingIntentCanonical = row.get("FoundingIntentCanonical")
                if city and raw_ts:
                    if target_city and city.lower() != target_city.lower():
                        continue
                    try:
                        dt = datetime.strptime(raw_ts, "%Y-%m-%dT%H:%M:%SZ")
                        formatted_utc = dt.strftime("%Y/%m/%d %H:%M:%S")
                        results.append((city, formatted_utc, FoundingIntentCanonical))
                    except ValueError:
                        print(f"[WARN] Skipping invalid timestamp for {city}: {raw_ts}")
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
    return results

def update_planetary_json(planet_data, city):
        state = os.path.basename(utc_file).replace("utc_", "").replace(".csv", "")
        key = city
        base_folder = os.path.dirname(utc_file)  # Extracts: data/regions/NorthAmerica/USA/Texas
        json_path = os.path.join(base_folder, f"incorp_{state}.json")

        # Load and update planetary JSON
        if os.path.exists(json_path):
            with open(json_path) as f:
                planetary = json.load(f)
        else:
            planetary = {}

        planetary[key] = planet_data

        with open(json_path, "w") as f:
            json.dump(planetary, f, indent=2)


# def wait_for_file_stability(wait_seconds=2):
#     state = os.path.basename(utc_file).replace("utc_", "").replace(".csv", "")
#     base_folder = os.path.dirname(utc_file)  # Extracts: data/regions/NorthAmerica/USA/Texas
#     json_path = os.path.join(base_folder, f"incorp_{state}.json")
#     last_size = -1
#     while True:
#         current_size = os.path.getsize(json_path)
#         if current_size == last_size:
#             break
#         last_size = current_size
#         time.sleep(wait_seconds)

def enrich_roles_from_vibakthi(dallas_chart: dict, vibakthi_data: dict) -> dict:
    vmap = vibakthi_data.get("framework", {}).get("vibhakti_mapping", [])
    
    for entry in vmap:
        planet = entry["planet"]
        if planet in dallas_chart:
            dallas_chart[planet]["role"] = entry["role"]
            dallas_chart[planet]["deity"] = entry["deity"]
            dallas_chart[planet]["semantic_function"] = entry["semantic_function"]
            dallas_chart[planet]["vibhakti"] = entry["vibhakti"]
    
    return dallas_chart


def enrich_roles_from_civic_roles(dallas_chart: dict, civic_roles: dict) -> dict:
    for planet, pdata in dallas_chart.items():
        if planet in civic_roles and isinstance(pdata, dict):
            role_info = civic_roles[planet]
            pdata["civic_role"] = role_info["name"]
            pdata["civic_function"] = role_info["semantic_role"]
            pdata["civic_lineage"] = role_info["mythic_lineage"]
            pdata["civic_opposite"] = role_info["opposite"]
            pdata["civic_description"] = role_info["description"]
    return dallas_chart

def enrich_roles_from_template_washer(dallas_chart: dict, washer_roles: dict) -> dict:
    for planet, pdata in dallas_chart.items():
        if planet in washer_roles and isinstance(pdata, dict):
            washer_info = washer_roles[planet]
            pdata["washer_ring"] = washer_info.get("washer_ring")
            pdata["washer_force"] = washer_info.get("washer_force")
            pdata["washer_force_type"] = washer_info.get("washer_force_type")
            pdata["washer_number"] = washer_info.get("washer_number")
            pdata["washer_semantic_city_role"] = washer_info.get("washer_semantic_city_role")
            pdata["washer_semantic_family_role"] = washer_info.get("washer_semantic_family_role")
    return dallas_chart

def match_semantic_units(city_flat_data: dict, semantic_units: list) -> list:
    planet_keys = [k for k in city_flat_data if k.startswith("planet_") and k.endswith("_number")]
    city_numbers = [city_flat_data[k] for k in planet_keys if isinstance(city_flat_data[k], int)]

    matches = []
    for unit in semantic_units:
        pool = unit.get("number_pool", [])
        matched = sorted(set(city_numbers) & set(pool))
        if matched:
            matches.append({
                "unit_id": unit["unit_id"],
                "match_score": len(matched),
                "matched_numbers": matched
            })
    return sorted(matches, key=lambda x: (-x["match_score"], x["unit_id"]))

def match_geometry_units(city_flat_data: dict, geometry_sets: list) -> list:
    planet_keys = [k for k in city_flat_data if k.startswith("planet_") and k.endswith("_number")]
    city_numbers = [city_flat_data[k] for k in planet_keys if isinstance(city_flat_data[k], int)]

    matches = []
    for geo in geometry_sets:
        pool = geo.get("number_pool", [])
        matched = sorted(set(city_numbers) & set(pool))
        if matched:
            matches.append({
                "geometry_id": geo["geometry_id"],
                "matched_units": [uid for uid in geo.get("unit_ids", []) if uid in city_flat_data.get("semantic_unit_matches", [])],
                "match_score": len(matched),
                "matched_numbers": matched,
                "semantic_role": geo.get("semantic_role", "")
            })
    return sorted(matches, key=lambda x: (-x["match_score"], x["geometry_id"]))

def enrich_geometry_matches_with_units(city_flat_data: dict) -> list:
    geometry_matches = city_flat_data.get("geometry_matches", [])
    semantic_units = city_flat_data.get("semantic_unit_matches", [])

    enriched = []
    for geo in geometry_matches:
        geo_numbers = set(geo.get("matched_numbers", []))
        matched_units = [
            unit["unit_id"]
            for unit in semantic_units
            if geo_numbers & set(unit.get("matched_numbers", []))
        ]
        enriched.append({
            **geo,
            "matched_units": sorted(matched_units)
        })
    return enriched

def regroup_engines(city_flat_data: dict) -> dict:
    engines = {}

    for key, value in city_flat_data.items():
        if key.startswith("planet_") and key.endswith("_ZoneEngine"):
            planet_name = key.split("_")[1]
            engine_name = value

            # Initialize engine block
            if engine_name not in engines:
                engines[engine_name] = {}

            # Build planet block
            planet_block = {
                "planet_number": city_flat_data.get(f"planet_{planet_name}_number"),
                "zodiac_number": city_flat_data.get(f"planet_{planet_name}_zodiac_number"),
                "semantic": {
                    "function": city_flat_data.get(f"planet_{planet_name}_semantic_function"),
                    "healing_bias": city_flat_data.get(f"planet_{planet_name}_healing_bias"),
                    "mythic_lineage": city_flat_data.get(f"planet_{planet_name}_mythic_lineage"),
                    "role_description": city_flat_data.get(f"planet_{planet_name}_role_description"),
                    "mythic_tags": city_flat_data.get(f"planet_{planet_name}_mythic_tags")
                },
                "civic": {
                    "role": city_flat_data.get(f"civic_{planet_name}_role"),
                    "function": city_flat_data.get(f"civic_{planet_name}_function"),
                    "lineage": city_flat_data.get(f"civic_{planet_name}_lineage"),
                    "description": city_flat_data.get(f"civic_{planet_name}_description"),
                    "opposite": city_flat_data.get(f"civic_{planet_name}_opposite")
                },
                "washer": {
                    "force": city_flat_data.get(f"washer_{planet_name}_force"),
                    "force_type": city_flat_data.get(f"washer_{planet_name}_force_type"),
                    "semantic_city_role": city_flat_data.get(f"washer_{planet_name}_semantic_city_role"),
                    "semantic_family_role": city_flat_data.get(f"washer_{planet_name}_semantic_family_role"),
                    "ring": city_flat_data.get(f"washer_{planet_name}_ring"),
                    "number": city_flat_data.get(f"washer_{planet_name}_number")
                },
                "modulation": {
                    "stage": city_flat_data.get(f"modulation_{planet_name}_stage"),
                    "containment_flag": city_flat_data.get(f"containment_{planet_name}_flag")
                },
                "zone": {
                    "number": city_flat_data.get(f"planet_{planet_name}_zone"),
                    "category": city_flat_data.get(f"planet_{planet_name}_ZoneCategory"),
                    "collective_meaning": city_flat_data.get(f"planet_{planet_name}_ZoneCollectiveMeaning"),
                    "essence": city_flat_data.get(f"planet_{planet_name}_zoneEssence")
                }
            }

            engines[engine_name][planet_name] = planet_block

    return engines

def enrich_engine_map_with_overlays(engine_map, semantic_unit_matches, geometry_matches):
    # Build reverse lookup maps
    semantic_lookup = {}
    for unit in semantic_unit_matches:
        for num in unit["matched_numbers"]:
            semantic_lookup.setdefault(num, []).append(unit["unit_id"])

    geometry_lookup = {}
    for geom in geometry_matches:
        for num in geom["matched_numbers"]:
            geometry_lookup.setdefault(num, []).append({
                "geometry_id": geom["geometry_id"],
                "semantic_role": geom["semantic_role"]
            })

    # Enrich each planet in each engine
    for engine_name, planets in engine_map.items():
        for planet_name, planet_data in planets.items():
            pnum = planet_data.get("planet_number")
            planet_data["semantic_units"] = semantic_lookup.get(pnum, [])
            planet_data["geometry_roles"] = geometry_lookup.get(pnum, [])

    return engine_map

def trace_all_variables():
    print("\n--- Variable Trace (locals) ---")
    for name, val in locals().items():
        if not name.startswith("__"):
            print(f"{name} = {val} ({type(val).__name__})")

    print("\n--- Variable Trace (globals) ---")
    for name, val in globals().items():
        if not name.startswith("__") and not callable(val):
            print(f"{name} = {val} ({type(val).__name__})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python modulate_city.py <path_to_utc_file.csv> [--city CityName]")
        sys.exit(1)

    utc_file = sys.argv[1]
    target_city = None

    if len(sys.argv) == 4 and sys.argv[2] == "--city":
        target_city = sys.argv[3]

    print(f"[OK] Received UTC file: {utc_file}")
    if target_city:
        print(f"[INFO] Filtering for city: {target_city}")

    cities = load_utc_file(utc_file, target_city)
    modulation_zones = load_modulation_zones()

#     {
#   "001": {
#     "Karta": {"zone": 35, "house": 12},       // Sun
#     "Karma": {"zone": 29, "house": 10},       // Moon
#     "Jnaata": {"zone": 1, "house": 1},        // Mercury
#     "Prema": {"zone": 32, "house": 11},       // Venus
#     "Yoddha": {"zone": 24, "house": 8},       // Mars
#     "Guru": {"zone": 2, "house": 1},          // Jupiter
#     "Shani": {"zone": 12, "house": 4},        // Saturn
#     "Antariksha": {"zone": 8, "house": 3},    // Uranus
#     "Samudra": {"zone": 2, "house": 1},       // Neptune
#     "Mrityu": {"zone": 8, "house": 3},        // Pluto
#     "Chhaaya": {"zone": 6, "house": 2},       // Rahu
#     "Vimochana": {"zone": 24, "house": 8},    // Ketu
#     "Avidya": {"zone": 21, "house": 7}        // Lilith
#   },
    with open("canonical/geometry/geometry_7_sets.json", "r") as f:
        geometry_sets = json.load(f)


    with open("canonical/modulation/aspectual_router.json", encoding="utf-8") as f:
        aspectual_router = json.load(f)

    with open("canonical/roles/vibakthi.json", encoding="utf-8") as f:
        vibakthi = json.load(f)
    
    with open("canonical/roles/civic_roles.json", encoding="utf-8") as f:
        civic_roles = json.load(f)

    with open("canonical/zodiac/template_washer.json", encoding="utf-8") as f:
        template_washer = json.load(f)

    with open("canonical/semantic/semantic_24_sets.json", encoding="utf-8") as f:
        semantic_24_sets = json.load(f)

    with open("canonical/modulation/aspectual_router.json", encoding="utf-8") as f:
        aspectual_router = json.load(f)

    if not cities:
        print("[WARN] No valid cities found.")
    else:
        print("[INFO] Parsed Cities:")
        for city, utc_time,FoundingIntentCanonical in cities:
            
            print(f"[INFO] Computing planetary modulation for {city} at {utc_time}")
            planet_data = compute_planetary_info(utc_time, modulation_zones)
            planet_data["birth_choice"] = [{
                "FoundingIntentCanonical": FoundingIntentCanonical
            }]
            planet_data = enrich_roles_from_vibakthi(planet_data, vibakthi)
            # Enrich with civic roles
            planet_data = enrich_roles_from_civic_roles(planet_data, civic_roles) 
            # Enrich with template washer roles
            planet_data = enrich_roles_from_template_washer(planet_data, template_washer)   
            planet_data = flatten_city_data(planet_data)  
            planet_data["semantic_unit_matches"] = match_semantic_units(planet_data, semantic_24_sets)
            planet_data["geometry_matches"] = match_geometry_units(planet_data, geometry_sets)
            planet_data["geometry_matches"] = enrich_geometry_matches_with_units(planet_data)
            planet_data["engine_map"] = regroup_engines(planet_data)
            planet_data["engine_map"] = enrich_engine_map_with_overlays(
                planet_data["engine_map"],
                planet_data["semantic_unit_matches"],
                planet_data["geometry_matches"]
            )
            # Validate Yod overlay
            # planet_data = validate_yod_overlay(planet_data, aspectual_router) 
            # Enrich with geometry sets from semantic units
            # planet_data = enrich_geometry_sets_from_semantic_units(planet_data, semantic_24_sets)


            # routed_chart = route_chart(planet_data, geometry_shapes, semantic_fractal_48)
            # print(f"[DEBUG] Routed Chart: {routed_chart}")
            # decomposed = decompose_chart(routed_chart, composite_configurations)
            # print(f"[DEBUG] Decomposed Chart: {decomposed}")




            # matches = match_geometry(planet_data, geometry_patterns, top_n=3)
            # planet_data["geometry_matches"] = matches 
            update_planetary_json(planet_data, city)


            # for body, info in planet_data.items():
            #     print(f"{body}: {info['longitude']}°, Direction: {info['retrograde_status']}, {info}")
            # update_planetary_json(planet_data, city)
        # trace_all_variables()
    
