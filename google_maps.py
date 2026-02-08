import os
import random
from datetime import datetime
import googlemaps

USE_GOOGLE = os.getenv("USE_GOOGLE_MAPS", "false").lower() == "true"
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# ======================================================
# 🚦 FUNCIÓN PRINCIPAL (usada por la API)
# ======================================================
def get_time_matrix(addresses):
    if USE_GOOGLE:
        print("🔴 MODO GOOGLE ACTIVO → Se usa Google Maps REAL")
        return real_google_time_matrix(addresses)
    else:
        print("🟢 MODO MOCK ACTIVO → Google Maps NO se usa")
        return fake_time_matrix(len(addresses))


# ======================================================
# 🟢 MATRIZ FALSA (DESARROLLO / $0)
# ======================================================
def fake_time_matrix(n):
    matrix = []

    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0)
            else:
                # tiempos realistas: 5 a 45 min
                row.append(random.randint(300, 2700))
        matrix.append(row)

    return matrix


# ======================================================
# 🔴 MATRIZ REAL (PRODUCCIÓN)
# ======================================================
def real_google_time_matrix(addresses):
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_MAPS_API_KEY no está configurada")

    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

    response = gmaps.distance_matrix(
        origins=addresses,
        destinations=addresses,
        mode="driving",
        departure_time=datetime.now(),
        traffic_model="best_guess"
    )

    matrix = []
    for row in response["rows"]:
        matrix.append([
            element["duration"]["value"]
            for element in row["elements"]
        ])

    return matrix
