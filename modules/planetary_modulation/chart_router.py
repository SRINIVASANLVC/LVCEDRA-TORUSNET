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

def route_by_geometry_id(geometry_id):
    """Route directly by geometry_id."""
    shapes = load_geometry_shapes()
    if geometry_id not in shapes:
        raise ValueError(f"Geometry ID '{geometry_id}' not found.")
    return shapes[geometry_id]

def route_by_semantic_function(target_function):
    """Route by semantic_function."""
    shapes = load_geometry_shapes()
    for shape in shapes.values():
        if shape.get("semantic_function") == target_function:
            return shape
    raise ValueError(f"No geometry found for semantic function: {target_function}")

def route_by_checksum_anchor(checksum):
    """Route by checksum_anchor."""
    shapes = load_geometry_shapes()
    for shape in shapes.values():
        if shape.get("checksum_anchor") == checksum:
            return shape
    raise ValueError(f"No geometry found for checksum anchor: {checksum}")

def route_by_planetary_triad(triad):
    """Route by planetary triad match."""
    shapes = load_geometry_shapes()
    for shape in shapes.values():
        triads = shape.get("internal_structure", {}).get("triads", [])
        if triad in triads:
            return shape
    raise ValueError(f"No geometry found for triad: {triad}")

def canonical_geometry_router(criteria: dict):
    """Generic router using multiple canonical fields."""
    shapes = load_geometry_shapes()
    for shape in shapes.values():
        match = True
        for key, value in criteria.items():
            if key in shape and shape[key] == value:
                continue
            elif key in shape.get("internal_structure", {}) and value in shape["internal_structure"][key]:
                continue
            else:
                match = False
                break
        if match:
            return shape
    raise ValueError(f"No geometry matches criteria: {criteria}")

# Example usage
if __name__ == "__main__":
    # Replace with dynamic inputs from civic/jiva pipeline
    geometry = canonical_geometry_router({
        "semantic_function": "Contains feminine-mystical archetypes and routes Lilith emergence safely",
        "checksum_anchor": "Saturn-63"
    })
    print(json.dumps(geometry, indent=2))
