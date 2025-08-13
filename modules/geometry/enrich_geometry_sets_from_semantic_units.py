import json 
def enrich_geometry_sets_from_semantic_units(city_chart: dict, semantic_units: list) -> dict:
    """
    Enriches each planet in the city chart with triangle and square geometries
    from semantic_24_sets.json based on planet_number.

    Args:
        city_chart (dict): Planet-level data for a city (e.g., Dallas)
        semantic_units (list): Parsed JSON list from semantic_24_sets.json

    Returns:
        dict: Enriched city chart with 'semantic_geometry_sets' per planet
    """
    for planet, pdata in city_chart.items():
        if isinstance(pdata, dict) and "planet_number" in pdata:
            pnum = pdata["planet_number"]
            geometry_sets = []

            for unit in semantic_units:
                unit_id = unit.get("unit_id")

                # Triangles from hexagons
                for hexagon in unit.get("hexagons", []):
                    if len(hexagon) == 3 and pnum in hexagon:
                        geometry_sets.append({
                            "geometry_type": "Triangle",
                            "partners": hexagon,
                            "unit_id": unit_id
                        })

                # Squares from octagons
                for octagon in unit.get("octagons", []):
                    for half in octagon:
                        if len(half) == 4 and pnum in half:
                            geometry_sets.append({
                                "geometry_type": "Square",
                                "partners": half,
                                "unit_id": unit_id
                            })

            if geometry_sets:
                pdata["semantic_geometry_sets"] = geometry_sets

    return city_chart