# modules/planetary_modulation/match_geometry.py

def score_pattern(pattern, planetary_data, role_to_planet, role_weights=None, retrograde_multiplier=1.5):
    score = 0
    mismatches = []
    retrograde_roles = []

    for role, expected in pattern.items():
        planet = role_to_planet.get(role)        
        actual = planetary_data.get(planet)
        if not actual:
            mismatches.append((role, "missing planet"))
            continue

        zone_match = actual.get("zone") == expected.get("zone")
        house_match = actual.get("template_House") == expected.get("house")
        retrograde = actual.get("retrograde_status") == "Retrograde"

        base_weight = role_weights.get(role, 1) if role_weights else 1
        if retrograde:
            base_weight *= retrograde_multiplier
            retrograde_roles.append(role)

        if zone_match and house_match:
            score += base_weight
        else:
            mismatches.append((role, {
                "expected": expected,
                "actual": {
                    "zone": actual.get("zone"),
                    "house": actual.get("template_House")
                }
            }))

    return round(score, 2), mismatches, retrograde_roles


def match_geometry(planet_data, geometry_patterns, top_n=3):
    role_to_planet = {
        "Karta": "Sun", "Karma": "Moon", "Jnaata": "Mercury", "Prema": "Venus",
        "Yoddha": "Mars", "Guru": "Jupiter", "Shani": "Saturn", "Antariksha": "Uranus",
        "Samudra": "Neptune", "Mrityu": "Pluto", "Chhaaya": "Rahu", "Vimochana": "Ketu",
        "Avidya": "Lilith"
    }

    role_weights = {
        "Karta": 3, "Karma": 3, "Guru": 2, "Shani": 2, "Jnaata": 2, "Prema": 2,
        "Yoddha": 2, "Antariksha": 1, "Samudra": 1, "Mrityu": 1,
        "Chhaaya": 1, "Vimochana": 1, "Avidya": 1
    }

    matches = []
    for archetype_id, pattern in geometry_patterns.items():
        score, mismatches, retrograde_roles = score_pattern(
            pattern, planetary_data=planet_data,
            role_to_planet=role_to_planet,
            role_weights=role_weights,
            retrograde_multiplier=1.5
        )
        matches.append({
            "archetype_id": archetype_id,
            "score": score,
            "pattern": pattern,
            "retrograde_roles": retrograde_roles,
            "mismatches": mismatches
        })

    sorted_matches = sorted(matches, key=lambda x: x["score"], reverse=True)
    return sorted_matches[:top_n]