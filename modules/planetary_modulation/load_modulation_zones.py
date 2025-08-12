import csv

def load_modulation_zones(filepath="canonical/modulation/modulation_zones.csv"):
    modulation_zones = []
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            modulation_zones.append({
                "zone": int(row["zone"]),
                "sign": row["sign"].strip(),
                "ruler": row["ruler"].strip(),
                "house": int(row["house"]),
                "stage": row["stage"].strip(),
                "start": float(row["start"]),
                "end": float(row["end"]),
                "nakshatra": row["nakshatra"].strip(),
                "nak_ruler": row["nak_ruler"].strip()
            })
    return modulation_zones