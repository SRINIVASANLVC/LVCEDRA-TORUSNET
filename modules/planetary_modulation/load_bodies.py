import csv

def load_bodies(filepath="canonical/zodiac/bodies.csv"):
    bodies = []
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            body = row["body_name"].strip()
            planet_number = int(row["planet_number"].strip())
            bodies.append((body, planet_number))
    return bodies
