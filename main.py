print(">>> INICIANDO PROGRAMA <<<")

from optimizer import optimize_routes
from google_maps import get_time_matrix
from input_data import load_addresses

addresses = load_addresses()

time_matrix = get_time_matrix(addresses)

print("Matriz de tiempos:")
for row in time_matrix:
    print(row)


data = {
    "time_matrix": time_matrix,
    "num_vehicles": 2,  # por ahora fijo
    "depot": 0
}

routes = optimize_routes(data)

print("\nRutas óptimas (por TIEMPO real):")
for vehicle, route in routes.items():
    print(f"Vehículo {vehicle + 1}:")
    for stop in route:
        print(f"  - {addresses[stop]}")
