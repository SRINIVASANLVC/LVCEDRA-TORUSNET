import csv

def load_bodies(filepath="canonical/zodiac/bodies.csv"):
    bodies = []
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            body = row["body_name"].strip()
            planet_number = int(row["planet_number"].strip())
            # add these fields also like mythic_lineage,healing_bias,civic_roles,semantic_function,role_description
            mythic_lineage = row.get("mythic_lineage", "").strip()
            healing_bias = row.get("healing_bias", "").strip()
            civic_roles = row.get("civic_roles", "").strip()
            semantic_function = row.get("semantic_function", "").strip()
            role_description = row.get("role_description", "").strip()
            bodies.append((body, planet_number, mythic_lineage, healing_bias, civic_roles, semantic_function, role_description))
    return bodies
