import json

def is_triangle_valid(partners: list, chart: dict) -> bool:
    planet_nums = [p for p in partners if str(p) in chart]
    sign_nums = [p for p in partners if str(p) not in chart]

    if len(planet_nums) == 3:
        return validate_angular_spacing([chart[str(p)]["longitude"] for p in planet_nums], 120, 10)

    if len(planet_nums) == 1 and len(sign_nums) == 2:
        return is_mixed_triangle_valid(partners, chart)

    return False

def is_square_valid(partners: list, chart: dict) -> bool:
    try:
        longitudes = [chart[str(p)]["longitude"] for p in partners]
    except KeyError:
        return False
    return validate_angular_spacing(longitudes, 90, 10)

def validate_angular_spacing(degrees: list, expected: int, tolerance: int) -> bool:
    degrees.sort()
    spacings = [(degrees[(i+1)%len(degrees)] - degrees[i]) % 360 for i in range(len(degrees))]
    return all(abs(s - expected) <= tolerance for s in spacings)

def is_mixed_triangle_valid(partners: list, chart: dict) -> bool:
    planet_nums = [p for p in partners if str(p) in chart]
    sign_nums = [p for p in partners if str(p) not in chart]

    if len(planet_nums) != 1 or len(sign_nums) != 2:
        return False

    planet = chart[str(planet_nums[0])]
    planet_sign_num = zodiac_name_to_number(planet["sign"])
    planet_long = planet["longitude"]

    if planet_sign_num not in sign_nums:
        return False

    other_sign = [s for s in sign_nums if s != planet_sign_num][0]
    other_sign_center = zodiac_number_to_center_longitude(other_sign)

    angle = abs((planet_long - other_sign_center) % 360)
    return any(abs(angle - asp) <= 10 for asp in [60, 90, 120, 180])

def enrich_geometry_sets_with_validation(city_chart: dict, semantic_units: list) -> dict:
    """
    Enriches each planet with validated semantic geometry sets based on actual chart placements.

    Args:
        city_chart (dict): Full planetary chart with longitudes, zones, signs
        semantic_units (list): Parsed semantic_24_sets.json

    Returns:
        dict: Enriched chart with validated semantic_geometry_sets
    """
    for planet_name, pdata in city_chart.items():
        if not isinstance(pdata, dict) or "planet_number" not in pdata:
            continue

        pnum = pdata["planet_number"]
        geometry_sets = []

        for unit in semantic_units:
            unit_id = unit.get("unit_id")

            # 🔺 Triangles
            for hexagon in unit.get("hexagons", []):
                if len(hexagon) == 3 and pnum in hexagon:
                    if is_triangle_valid(hexagon, city_chart):
                        geometry_sets.append({
                            "geometry_type": "Triangle",
                            "partners": hexagon,
                            "unit_id": unit_id,
                            "validation_type": "geometric"
                        })

            # ◼️ Squares
            for octagon in unit.get("octagons", []):
                for square in octagon:
                    if len(square) == 4 and pnum in square:
                        if is_square_valid(square, city_chart):
                            geometry_sets.append({
                                "geometry_type": "Square",
                                "partners": square,
                                "unit_id": unit_id,
                                "validation_type": "geometric"
                            })

        if geometry_sets:
            pdata["semantic_geometry_sets"] = geometry_sets

    return city_chart