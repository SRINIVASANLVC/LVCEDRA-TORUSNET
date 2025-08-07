import csv
import sys
from datetime import datetime
from modules.planetary_modulation.compute_planetary_info import compute_planetary_info

def load_utc_file(filepath, target_city=None):
    results = []
    try:
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                city = row.get("city_name")
                raw_ts = row.get("incorporation_timestamp_utc")
                if city and raw_ts:
                    if target_city and city.lower() != target_city.lower():
                        continue
                    try:
                        dt = datetime.strptime(raw_ts, "%Y-%m-%dT%H:%M:%SZ")
                        formatted_utc = dt.strftime("%Y/%m/%d %H:%M:%S")
                        results.append((city, formatted_utc))
                    except ValueError:
                        print(f"[WARN] Skipping invalid timestamp for {city}: {raw_ts}")
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
    return results

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

    if not cities:
        print("[WARN] No valid cities found.")
    else:
        print("[INFO] Parsed Cities:")
        for city, utc_time in cities:
            print(f"[INFO] Computing planetary modulation for {city} at {utc_time}")
            planet_data = compute_planetary_info(utc_time)
            for body, info in planet_data.items():
                print(f"{body}: {info['longitude']}°, Direction: {info['retrograde_status']}, {info}")