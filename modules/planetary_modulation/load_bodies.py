import csv

def load_bodies(filepath="canonical/zodiac/bodies.csv"):
    bodies = []
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bodies.append(row["body_name"].strip())
    return bodies