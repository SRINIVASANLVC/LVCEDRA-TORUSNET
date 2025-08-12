def enrich_geometry_shapes(geometry_data):
    enriched_data = {}

    for gid, gentry in geometry_data.items():
        units = gentry.get("units", [])
        digit_sums = gentry.get("digit_sums", [])
        mod_21 = gentry.get("mod_21", [])
        semantic_tags = gentry.get("semantic_tags", {})

        # Infer modulation type
        modulation_type = "triadic" if len(units) == 3 else "nested" if len(units) > 3 else "dyadic"

        # Infer zone-house anchor (placeholder logic)
        zone_house_anchor = {
            "zone": mod_21[0] if mod_21 else None,
            "house": digit_sums[0] % 12 if digit_sums else None
        }

        # Role overlay (mock logic based on unit codes)
        role_overlay = []
        for u in units:
            if "A01" in u:
                role_overlay.append("Karta")
            elif "B01" in u:
                role_overlay.append("Yoddha")
            elif "C01" in u:
                role_overlay.append("Bhogi")

        # Audit flags
        audit_flags = []
        if not semantic_tags.get("mythic_signature"):
            audit_flags.append("missing mythic signature")
        if not gentry.get("opposes"):
            audit_flags.append("no oppositional link")

        # Enrich entry
        enriched_data[gid] = {
            **gentry,
            "modulation_type": modulation_type,
            "zone_house_anchor": zone_house_anchor,
            "role_overlay": list(set(role_overlay)),
            "audit_flags": audit_flags
        }

    return enriched_data

import json


with open("canonical/geometry/geometry_7_sets.json", "r") as f:
    geometry_7_sets = json.load(f)

enriched_geometry = enrich_geometry_shapes(geometry_7_sets)

with open("canonical/geometry/geometry_shapes_enriched.json", "w") as f:
    json.dump(enriched_geometry, f, indent=2)