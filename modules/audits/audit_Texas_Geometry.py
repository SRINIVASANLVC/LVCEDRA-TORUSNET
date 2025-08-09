import json

# Load planetary data
with open("data/regions/NorthAmerica/USA/Texas/incorp_Texas.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Define required semantic fields
semantic_fields = ["modulation_logic", "action_flow", "karmic_balance", "epistemic_validated", "civic_resonance"]

def audit_city(city_name, city_data):
    report = {
        "city": city_name,
        "score": None,
        "mismatches": [],
        "missing_semantics": [],
        "retrograde_roles_expected": [],
        "retrograde_roles_matched": []
    }

    matches = city_data.get("geometry_matches", [])
    if not matches:
        report["score"] = 0
        report["mismatches"].append("No geometry_matches found")
        return report

    top_match = matches[0]
    report["score"] = top_match.get("score", 0)
    report["mismatches"] = top_match.get("mismatches", [])

    # Check semantic fields
    pattern = top_match.get("pattern", {})
    for field in semantic_fields:
        if field not in pattern:
            report["missing_semantics"].append(field)

    # Check retrograde amplification
    expected_retro_roles = pattern.get("retrograde_roles", [])
    matched_retro_roles = top_match.get("retrograde_roles", [])
    report["retrograde_roles_expected"] = expected_retro_roles
    report["retrograde_roles_matched"] = matched_retro_roles

    return report

# Run audit across all cities
audit_results = []
for city_name, city_data in data.items():
    if city_name == "geometry_matches":
        continue
    audit_results.append(audit_city(city_name, city_data))

# Print summary
for result in audit_results:
    print(f"\n📍 {result['city']}")
    print(f"  Score: {result['score']}")
    print(f"  Mismatches: {len(result['mismatches'])}")
    if result["missing_semantics"]:
        print(f"  ❌ Missing semantic fields: {result['missing_semantics']}")
    if result["retrograde_roles_expected"] and not result["retrograde_roles_matched"]:
        print(f"  ⚠️ Retrograde roles expected but not matched: {result['retrograde_roles_expected']}")