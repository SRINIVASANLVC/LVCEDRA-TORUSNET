import csv
import sys
from datetime import datetime
import os
import time
import json

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from modules.planetary_modulation.compute_planetary_info import compute_planetary_info
# from modules.planetary_modulation.match_geometry import match_geometry
from modules.planetary_modulation.chart_router import route_chart
from modules.planetary_modulation.chart_decomposer import decompose_chart


from modules.planetary_modulation.load_modulation_zones import load_modulation_zones


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
    with open("templates/geometry_shapes.json", "r") as f:
        geometry_shapes_raw = json.load(f)
    geometry_shapes = {
        shape["name"]: shape
        for shape in geometry_shapes_raw
        if "name" in shape

    }

    with open("templates/semantic_fractal_48.json", "r") as f:
        semantic_fractal_48 = json.load(f)
    with open("templates/composite_configurations.json", "r") as f:
        composite_configurations = json.load(f)
    with open("templates/geometry_crossmap.json", "r") as f:
        geometry_crossmap = json.load(f)
    with open("templates/aspect_pattern_router.json", "r") as f:
        aspect_pattern_router = json.load(f)
    with open("templates/semantic_dna.json", "r") as f:
        semantic_dna = json.load(f)
    with open("templates/admitted_configurations.json", "r") as f:
        admitted_configurations = json.load(f)
    with open("templates/fractal_cycle_map.json", "r") as f:
        fractal_cycle_map = json.load(f)



    if not cities:
        print("[WARN] No valid cities found.")
    else:
        print("[INFO] Parsed Cities:")
        for city, utc_time,FoundingIntentCanonical in cities:
            
            print(f"[INFO] Computing planetary modulation for {city} at {utc_time}")
            planet_data = compute_planetary_info(utc_time, modulation_zones)
            planet_data["incorp_choice"] = [{
                "FoundingIntentCanonical": FoundingIntentCanonical
            }]
            routed_chart = route_chart(planet_data, geometry_shapes, semantic_fractal_48)
            print(f"[DEBUG] Routed Chart: {routed_chart}")
            decomposed = decompose_chart(routed_chart, composite_configurations)
            print(f"[DEBUG] Decomposed Chart: {decomposed}")




            # matches = match_geometry(planet_data, geometry_patterns, top_n=3)
            # planet_data["geometry_matches"] = matches 
            update_planetary_json(planet_data, city)


            # for body, info in planet_data.items():
            #     print(f"{body}: {info['longitude']}°, Direction: {info['retrograde_status']}, {info}")
            # update_planetary_json(planet_data, city)
        # trace_all_variables()
    
