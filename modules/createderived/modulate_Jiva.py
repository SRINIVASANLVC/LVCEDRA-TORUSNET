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

            pdata["washer_semantic_city_role"] = washer_info.get("washer_semantic_city_role")
            pdata["washer_semantic_family_role"] = washer_info.get("washer_semantic_family_role")
    return dallas_chart


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
            # Enrich with geometry sets from semantic units
            # planet_data = enrich_geometry_sets_from_semantic_units(planet_data, semantic_24_sets)

            update_planetary_json(planet_data, name)
            # for body, info in planet_data.items():
            #     print(f"{body}: {info['longitude']}°, Direction: {info['retrograde_status']}, {info}")
            # print(f"[INFO] Ascendant: {ascendant}, Thumbprint: {thumbprint}")
    # trace_all_variables()