import json

def validate_overlay_instances(planet_data_flattened):
    with open("canonical/semantic/semantic_24_sets.json", encoding="utf-8") as f:
        semantic_sets = json.load(f)

    with open("canonical/modulation/aspectual_router.json", encoding="utf-8") as f:
        aspectual_router = json.load(f)

    for overlay_def in aspectual_router:
        overlay_name = overlay_def["aspectual_overlay"]
        geometry_id = overlay_def.get("routed_geometry", {}).get("geometry_id", "GXX")
        planets_required = overlay_def.get("planets", [])
        triangle_zones = overlay_def.get("routed_geometry", {}).get("triangle", [])

        match_count = 0

        for req in planets_required:
            secret_number = req["secret_number"]
            vibhakti_required = req["vibhakti_role"]
            washer_force_required = req["template_washer_force"]

            # Build keys
            semantic_key = f"planet_{secret_number}"
            vibhakti_key = f"planet_{semantic_key}_vibhakti"
            washer_force_key = f"washer_{semantic_key}_force_type"
            zone_key = f"planet_{semantic_key}_zone"

            # Check semantic match
            vibhakti_actual = planet_data_flattened.get(vibhakti_key, "N/A")
            washer_force_actual = planet_data_flattened.get(washer_force_key, "N/A")
            zone_actual = planet_data_flattened.get(zone_key, None)

            if (
                vibhakti_actual == vibhakti_required and
                washer_force_actual == washer_force_required and
                zone_actual in triangle_zones
            ):
                match_count += 1

        # Require all planets to match
        validated = match_count == len(planets_required)
        tag_key = f"overlay_{overlay_name}_{geometry_id}_validated"
        planet_data_flattened[tag_key] = validated

    return planet_data_flattened

