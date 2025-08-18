import csv
import sys
from datetime import datetime
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from modules.planetary_modulation.compute_planetary_info import compute_planetary_info
from modules.planetary_modulation.load_modulation_zones import load_modulation_zones
from modules.geometry.flatten_city_data import flatten_city_data
# from modules.geometry.enrich_geometry_sets_from_semantic_units import enrich_geometry_sets_from_semantic_units
sys.stdout.reconfigure(encoding='utf-8')


def load_jiva_file(filepath, target_name=None):
    results = []
    try:
        # with open(filepath, newline='') as csvfile:
        with open(filepath, mode="r", encoding="utf-8") as csvfile:

            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get("Name")
                raw_ts = row.get("DOB")
                Ascendant = row.get("Ascendant")
                Thumbprint = row.get("Thumbprint")
                FoundingIntentNarrative = row.get("FoundingIntentNarrative")
                FoundingIntentCanonical = row.get("FoundingIntentCanonical")
                HealingBias = row.get("HealingBias")
                SemanticDrift = row.get("SemanticDrift")
                MythicLineage = row.get("MythicLineage")    

                if name and raw_ts:
                    if target_name and name.strip().lower() != target_name.strip().lower():
                        continue
                    try:
                        dt = datetime.strptime(raw_ts, "%Y-%m-%dT%H:%MZ")
                        formatted_utc = dt.strftime("%Y/%m/%d %H:%M:%S")
                        results.append({
                            "Name": name,
                            "DOB": formatted_utc,
                            "Ascendant": Ascendant,
                            "Thumbprint": Thumbprint,
                            "FoundingIntentNarrative": FoundingIntentNarrative,
                            "MythicLineage": MythicLineage,
                            "SemanticDrift": SemanticDrift,
                            "HealingBias": HealingBias,
                            "FoundingIntentCanonical": FoundingIntentCanonical
                        })

                    except ValueError:
                        print(f"[WARN] Skipping invalid timestamp for {name}: {raw_ts}")
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
    # trace_all_variables()
    return results

def update_planetary_json(planet_data, name):
    # Extract Jiva name from file path
    jiva = os.path.basename(jiva_file).replace("utc_", "").replace(".csv", "")
    key = name
    base_folder = os.path.dirname(jiva_file)
    json_path = os.path.join(base_folder, f"incorp_{jiva}.json")

    # Load existing JSON safely
    planetary = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    planetary = json.loads(content)
                else:
                    print(f"[INFO] Empty JSON file at {json_path}. Initializing fresh structure.")
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON decode failed for {json_path}: {e}. Starting fresh.")

    # Update planetary data for the given key
    planetary[key] = planet_data

    # Write updated JSON back to file
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(planetary, f, indent=2, ensure_ascii=False)
        print(f"[OK] Updated planetary data for {key} in {json_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write JSON to {json_path}: {e}")

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

import json

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

def build_engine_geometry_enrichment(engine_map, geometry_matches):
    geom_lookup = {}
    for geom in geometry_matches:
        for num in geom.get("matched_numbers", []):
            geom_lookup.setdefault(num, []).append({
                "geometry_id": geom["geometry_id"],
                "semantic_role": geom.get("semantic_role", "")
            })

    engine_geometry = {}
    for engine_name, planets in engine_map.items():
        contributions = {}
        for planet_name, pdata in planets.items():
            pnum = pdata.get("planet_number")
            for geom in geom_lookup.get(pnum, []):
                gid = geom["geometry_id"]
                role = geom["semantic_role"]
                contributions.setdefault(gid, set()).add(role)

        engine_geometry[engine_name] = {
            gid: "; ".join(sorted(roles))
            for gid, roles in contributions.items()
        }

    return engine_geometry

def build_engine_semantic_enrichment(engine_map, semantic_unit_matches):
    semantic_lookup = {}
    for unit in semantic_unit_matches:
        for num in unit.get("matched_numbers", []):
            semantic_lookup.setdefault(num, []).append(unit["unit_id"])

    engine_semantic = {}
    for engine_name, planets in engine_map.items():
        unit_ids = set()
        for planet_name, pdata in planets.items():
            pnum = pdata.get("planet_number")
            unit_ids.update(semantic_lookup.get(pnum, []))
        engine_semantic[engine_name] = sorted(unit_ids)

    return engine_semantic


def enrich_engine_map_with_overlays(engine_map, semantic_unit_matches, geometry_matches):
    geometry_enrichment = build_engine_geometry_enrichment(engine_map, geometry_matches)
    semantic_enrichment = build_engine_semantic_enrichment(engine_map, semantic_unit_matches)

    for engine_name, planets in engine_map.items():
        for planet_name in planets:
            planets[planet_name].pop("geometry_roles", None)
            planets[planet_name].pop("semantic_units", None)

        planets["geometry_enrichment"] = geometry_enrichment.get(engine_name, {})
        planets["semantic_unit_enrichment"] = semantic_enrichment.get(engine_name, [])

    return engine_map

def prune_city_for_synthesis(city_data):
    pruned = {}
    pruned["FoundingIntentCanonical"] = city_data.get("birth_FoundingIntentCanonical")
    pruned["birth_Ascendant"] = city_data.get("birth_Ascendant")
    pruned["birth_Thumbprint"] = city_data.get("birth_Thumbprint")
    pruned["birth_SemanticDrift"] = city_data.get("birth_SemanticDrift")
    pruned["birth_HealingBias"] = city_data.get("birth_HealingBias")
    pruned["birth_MythicLineage"] = city_data.get("birth_MythicLineage")
    pruned["FoundingIntentNarrative"] = city_data.get("birth_FoundingIntentNarrative")
    

    pruned["EngineMap"] = {}
    for engine, planets in city_data.get("engine_map", {}).items():
        pruned["EngineMap"][engine] = {}

        # Filter out non-planet keys
        for planet_name, planet_data in planets.items():
            if planet_name in ["geometry_enrichment", "semantic_unit_enrichment"]:
                continue

            pruned["EngineMap"][engine][planet_name] = {
                "semantic": planet_data.get("semantic"),
                "civic": planet_data.get("civic"),
                "modulation": planet_data.get("modulation"),
                "zone": planet_data.get("zone"),
                "planet_number": planet_data.get("planet_number"),
                "zodiac_number": planet_data.get("zodiac_number")
            }

        # Add engine-level overlays
        if "geometry_enrichment" in planets:
            pruned["EngineMap"][engine]["geometry_enrichment"] = planets["geometry_enrichment"]
        if "semantic_unit_enrichment" in planets:
            pruned["EngineMap"][engine]["semantic_unit_enrichment"] = planets["semantic_unit_enrichment"]

    return pruned

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
        print("Usage: python modulate_jiva.py <path_to_utc_Jiva.csv> [--name JivaName]")
        sys.exit(1)

    jiva_file = sys.argv[1]
    target_name = None
    if len(sys.argv) == 4 and sys.argv[2] == "--name":
        target_name = sys.argv[3]

    print(f"[OK] Received Jiva file: {jiva_file}")
    if target_name:
        print(f"[INFO] Filtering for jiva: {target_name}")

    jivas = load_jiva_file(jiva_file, target_name)
    modulation_zones = load_modulation_zones()

    with open("canonical/geometry/geometry_7_sets.json", "r") as f:
        geometry_sets = json.load(f)

    with open("canonical/roles/vibakthi.json", encoding="utf-8") as f:
        vibakthi = json.load(f)
    
    with open("canonical/roles/civic_roles.json", encoding="utf-8") as f:
        civic_roles = json.load(f)
    
    with open("canonical/zodiac/template_washer.json", encoding="utf-8") as f:
        template_washer = json.load(f)

    with open("canonical/semantic/semantic_24_sets.json", encoding="utf-8") as f:
        semantic_24_sets = json.load(f)
    



    if not jivas:
        print("[WARN] No valid jivas found.")
    else:
        print("[INFO] Parsed Jivas:")
        for row in jivas:
            print(f"[DEBUG] Processing Jiva:{row}")
            
            name = row["Name"]
            utc_time = row["DOB"]
            Ascendant = row["Ascendant"]
            Thumbprint = row["Thumbprint"]
            FoundingIntentNarrative = row["FoundingIntentNarrative"]
            MythicLineage = row["MythicLineage"]
            SemanticDrift = row["SemanticDrift"]
            HealingBias = row["HealingBias"]
            FoundingIntentCanonical = row["FoundingIntentCanonical"]
                                    
            print(f"[INFO] Computing planetary modulation for {name} at {utc_time}")
            planet_data = compute_planetary_info(utc_time, modulation_zones)
            # Add birth_choice as a list containing one dictionary
            planet_data["birth_choice"] = [{
                "Ascendant": Ascendant,
                "Thumbprint": Thumbprint,
                "FoundingIntentNarrative": FoundingIntentNarrative,
                "MythicLineage": MythicLineage,
                "SemanticDrift": SemanticDrift,
                "HealingBias": HealingBias,
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
            synthesis_ready = prune_city_for_synthesis(planet_data)
            update_planetary_json(synthesis_ready, name)
            # Enrich with geometry sets from semantic units
            # planet_data = enrich_geometry_sets_from_semantic_units(planet_data, semantic_24_sets)

            # update_planetary_json(planet_data, name)
            # for body, info in planet_data.items():
            #     print(f"{body}: {info['longitude']}°, Direction: {info['retrograde_status']}, {info}")
            # print(f"[INFO] Ascendant: {ascendant}, Thumbprint: {thumbprint}")
    # trace_all_variables()