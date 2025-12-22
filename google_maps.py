import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

print("API KEY CARGADA:", bool(API_KEY))


def get_time_matrix(addresses):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    locations = "|".join(addresses)

    params = {
        "origins": locations,
        "destinations": locations,
        "mode": "driving",
        "departure_time": "now",
        "traffic_model": "best_guess",
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    matrix = []
    for row in data["rows"]:
        matrix_row = []
        for element in row["elements"]:
            # tiempo con tráfico (segundos → minutos)
            time_sec = element["duration_in_traffic"]["value"]
            matrix_row.append(int(time_sec / 60))
        matrix.append(matrix_row)

    return matrix
