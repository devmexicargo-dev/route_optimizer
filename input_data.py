import csv

def load_addresses(file_path="addresses.csv"):
    addresses = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            addresses.append(row["direccion"])
    return addresses
