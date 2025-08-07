import csv

def load_bodies(filepath="templates/bodies.csv"):
    bodies = []
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bodies.append(row["body_name"].strip())
    return bodies