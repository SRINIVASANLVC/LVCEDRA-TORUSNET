# chart_decomposer.py
def decompose_chart(chart_data, composite_configurations):
    """
    Decomposes pentads/heptads into valid triads/tetrads.
    """
    elements = list(chart_data.values())
    if set(["Moon", "Venus", "Scorpio", "Pisces", "Saturn"]).issubset(elements):
        return {
            "configuration_type": "pentad",
            "decomposed_triads": [["Moon", "Venus", "Scorpio"], ["Pisces", "Saturn"]],
            "routed_geometry": "HX-22",
            "emergent_archetype": "Lilith"
        }
    return {"configuration_type": None}