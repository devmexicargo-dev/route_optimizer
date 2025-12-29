import os
import googlemaps
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)


def get_time_matrix(addresses: list[str]):
    """
    Devuelve una matriz NxN con tiempos de viaje en segundos
    """
    matrix = []

    for origin in addresses:
        row = []
        response = gmaps.distance_matrix(
            origins=[origin],
            destinations=addresses,
            mode="driving",
            departure_time="now",
            traffic_model="best_guess"
        )

        elements = response["rows"][0]["elements"]

        for e in elements:
            if e["status"] == "OK":
                row.append(e["duration_in_traffic"]["value"])
            else:
                row.append(999999)

        matrix.append(row)

    return matrix
