def enrich_geometry_matches(planet_data):
    geometry_enrichment = {}

    for city_name, planetary_map in planet_data.items():
        geo = planetary_map.get("geometry_matches", {})
        hexes = geo.get("hexes", [])
        modulation = geo.get("modulation", "unknown")

        enrichment = {
            "hex_count": len(hexes),
            "modulation_type": modulation,
            "containment_flags": [],
            "mythic_tags": []
        }

        # Containment logic based on hexes
        if any(h in [4, 8, 12] for h in hexes):
            enrichment["containment_flags"].append("containment breach")
        if any(h in [1, 5, 9] for h in hexes):
            enrichment["containment_flags"].append("semantic emergence")

        # Mythic resonance (example logic)
        if set(hexes) & {3, 6, 12}:
            enrichment["mythic_tags"].append("triple resonance")
        if 7 in hexes:
            enrichment["mythic_tags"].append("Ketu shadow")
        if 10 in hexes:
            enrichment["mythic_tags"].append("Saturn gate")

        geometry_enrichment[city_name] = enrichment

    return {"geometry_enrichment": geometry_enrichment}

# def derive_containment(planet_data):
#     planet_data["geometry_enrichment"] =  enrich_geometry_matches(planet_data)
#     containment_profile = {}

#     for planet, details in planet_data.items():
#         print(f"[DEBUG] Processing planet: {planet} with details: {details}")
#         if planet in ["geometry_enrichment", "birth_choice"]:
#             continue

#         containment = []

#         # Nakshatra ruler logic
#         ruler = details.get("nakshatra_ruler")
#         if ruler == "Rahu":
#             containment.append("amplification")
#         elif ruler == "Ketu":
#             containment.append("thinning")
#         elif ruler == "Saturn":
#             containment.append("stabilization")
#         elif ruler == "Mercury":
#             containment.append("reflection")
#         elif ruler == "Venus":
#             containment.append("softening")
#         elif ruler == "Mars":
#             containment.append("assertion")
#         elif ruler == "Jupiter":
#             containment.append("expansion")
#         elif ruler == "Moon":
#             containment.append("dissolution")
#         elif ruler == "Sun":
#             containment.append("illumination")

#         # Retrograde polarity
#         if details.get("retrograde_status") == "Retrograde":
#             containment.append("volatility")

#         # Template house overlays
#         house = details.get("template_House")
#         if house in [4, 8, 12]:
#             containment.append("containment breach")
#         elif house in [1, 5, 9]:
#             containment.append("semantic emergence")

#         containment_profile[planet] = {
#             "containment_logic": list(set(containment)),  # remove duplicates
#             "zone": details.get("zone"),
#             "house": house
#         }

#     return {"containment_synthesis": containment_profile}

def derive_containment(planet_data):
    # Enrich geometry first
    planet_data["geometry_enrichment"] = enrich_geometry_matches({"entity": planet_data})["geometry_enrichment"].get("entity", {})

    containment_profile = {}

    for planet, details in planet_data.items():
        if planet in ["geometry_enrichment", "birth_choice"]:
            continue

        containment = []

        # Nakshatra ruler logic
        ruler = details.get("nakshatra_ruler")
        if ruler == "Rahu":
            containment.append("amplification")
        elif ruler == "Ketu":
            containment.append("thinning")
        elif ruler == "Saturn":
            containment.append("stabilization")
        elif ruler == "Mercury":
            containment.append("reflection")
        elif ruler == "Venus":
            containment.append("softening")
        elif ruler == "Mars":
            containment.append("assertion")
        elif ruler == "Jupiter":
            containment.append("expansion")
        elif ruler == "Moon":
            containment.append("dissolution")
        elif ruler == "Sun":
            containment.append("illumination")

        # Retrograde polarity
        if details.get("retrograde_status") == "Retrograde":
            containment.append("volatility")

        # Template house overlays
        house = details.get("template_House")
        if house in [4, 8, 12]:
            containment.append("containment breach")
        elif house in [1, 5, 9]:
            containment.append("semantic emergence")
        elif house == 2:
            containment.append("semantic anchoring")
        elif house == 3:
            containment.append("narrative branching")
        elif house == 6:
            containment.append("healing crucible")
        elif house == 7:
            containment.append("oppositional containment")
        elif house == 10:
            containment.append("semantic projection")
        elif house == 11:
            containment.append("modular expansion")

        containment_profile[planet] = {
            "containment_logic": list(set(containment)),
            "zone": details.get("zone"),
            "house": house
        }

    # Optional: enrich with birth_choice
    birth = planet_data.get("birth_choice", [])
    if birth and isinstance(birth, list):
        birth_info = birth[0]
        containment_profile["birth_choice"] = {
            "Ascendant": birth_info.get("Ascendant"),
            "FoundingIntentCanonical": birth_info.get("FoundingIntentCanonical"),
            "SemanticDrift": birth_info.get("SemanticDrift"),
            "HealingBias": birth_info.get("HealingBias"),
            "MythicLineage": birth_info.get("MythicLineage")
        }

    return {"containment_synthesis": containment_profile}