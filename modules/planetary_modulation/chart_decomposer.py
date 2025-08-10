import json
import os

GEOMETRY_PATH = os.path.join("templates", "geometry_shapes.json")

def load_geometry_shapes():
    """Load and index geometry shapes by geometry_id."""
    with open(GEOMETRY_PATH, "r") as f:
        raw_shapes = json.load(f)

    return {
        shape["geometry_id"]: shape
        for shape in raw_shapes
        if "geometry_id" in shape
    }

def decompose_geometry(geometry_id):
    """Decompose a geometry into its internal structures and oppositional links."""
    shapes = load_geometry_shapes()

    if geometry_id not in shapes:
        raise ValueError(f"Geometry ID '{geometry_id}' not found.")

    shape = shapes[geometry_id]
    internal = shape.get("internal_structure", {})
    oppositional = shape.get("oppositional_links", [])
    aspects = shape.get("aspect_compatibility", [])
    checksum = shape.get("checksum_anchor", None)

    return {
        "geometry_id": geometry_id,
        "triads": internal.get("triads", []),
        "dyads": internal.get("dyads", []),
        "squares": internal.get("squares", []),
        "oppositional_links": oppositional,
        "aspect_compatibility": aspects,
        "checksum_anchor": checksum,
        "semantic_function": shape.get("semantic_function", "")
    }

# Example usage
if __name__ == "__main__":
    geometry_data = decompose_geometry("HX-22")
    print(json.dumps(geometry_data, indent=2))