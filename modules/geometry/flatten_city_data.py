
def flatten_city_data(city_data: dict) -> dict:
    flattened = {}

    # 1. Flatten birth_choice fields
    birth_fields = [
        "Ascendant", "Thumbprint", "SemanticDrift", "HealingBias",
        "MythicLineage", "FoundingIntentCanonical", "FoundingIntentNarrative"
    ]
    birth_choice = city_data.get("birth_choice", [{}])[0]
    for field in birth_fields:
        flattened[f"birth_{field}"] = birth_choice.get(field, "N/A")

    # 2. Flatten planetary fields
    for planet_name, planet_data in city_data.items():
        if planet_name == "birth_choice":
            continue

        prefix = planet_name
        def get(field): return planet_data.get(field, "N/A")

        # Core planetary fields
        flattened.update({
            f"planet_{prefix}_number": get("planet_number"),
            f"planet_{prefix}_mythic_lineage": get("planet_mythic_lineage"),
            f"planet_{prefix}_healing_bias": get("planet_healing_bias"),
            f"planet_{prefix}_semantic_function": get("planet_semantic_function"),
            f"planet_{prefix}_role_description": get("planet_role_description"),
            f"planet_{prefix}_civic_roles": get("planet_civic_roles"),
            f"planet_{prefix}_sign_ruler": get("sign_ruler"),
            f"planet_{prefix}_role": get("role"),
            f"planet_{prefix}_deity": get("deity"),
            f"planet_{prefix}_vibhakti": get("vibhakti"),
            f"planet_{prefix}_sign": get("sign"),
            f"planet_{prefix}_nakshatra": get("nakshatra"),
            f"planet_{prefix}_nakshatra_ruler": get("nakshatra_ruler"),
            f"planet_{prefix}_zone": get("zone"),
            f"planet_{prefix}_zodiac_number": get("zodiac_number"),
            f"planet_{prefix}_longitude": get("longitude"),
            f"planet_{prefix}_mythic_tags": get("mythic_tags"),
            f"planet_{prefix}_retrograde_status": get("retrograde_status")
        })

        # Civic fields — default to "N/A" if missing
        civic_fields = [
            "civic_role", "civic_function", "civic_opposite",
            "civic_lineage", "civic_description"
        ]
        for cf in civic_fields:
            flattened[f"{cf.replace('civic_', 'civic_' + prefix + '_')}"] = get(cf)

        # Washer fields — default to "N/A" if missing
        washer_fields = [
            "washer_ring", "washer_force", "washer_force_type",
            "washer_semantic_city_role", "washer_semantic_family_role" , "washer_number"
        ]
        for wf in washer_fields:
            flattened[f"{wf.replace('washer_', 'washer_' + prefix + '_')}"] = get(wf)

        # Modulation and containment
        flattened.update({
            f"modulation_{prefix}_stage": get("modulation_stage"),
            f"containment_{prefix}_flag": get("containment_flag"),
            f"template_{prefix}_House": get("template_House")
        })

    return flattened