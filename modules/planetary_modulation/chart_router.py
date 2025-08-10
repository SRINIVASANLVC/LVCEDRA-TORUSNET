def route_chart(chart_data, geometry_shapes, semantic_fractal_48):
    """
    Routes a planetary chart into canonical geometry and semantic fractal roles.
    """

    def has_signature(planets, sign):
        # Check if all planets are present and sign appears in any of their data
        return all(p in chart_data for p in planets) and any(
            isinstance(v, dict) and v.get("sign") == sign for v in chart_data.values()
        )

    # Example routing logic (expand as needed)
    if has_signature(["Moon", "Venus"], "Scorpio"):
        return geometry_shapes["hexagram_24"]
    elif has_signature(["Mars", "Jupiter"], "Leo"):
        return geometry_shapes["octagram_36"]
    else:
        # Default routing based on semantic fractal fallback
        return semantic_fractal_48.get("default_geometry", {})
