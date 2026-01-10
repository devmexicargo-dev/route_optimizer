from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def optimize_routes(time_matrix, time_windows, service_times, num_vehicles):
    num_locations = len(time_matrix)

    starts = [0] * num_vehicles
    ends = [0] * num_vehicles

    manager = pywrapcp.RoutingIndexManager(
        num_locations,
        num_vehicles,
        starts,
        ends
    )

    routing = pywrapcp.RoutingModel(manager)

    # ⏱️ Callback de tiempo (viaje + servicio)
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return time_matrix[from_node][to_node] + service_times[from_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # ⏱️ Dimensión de tiempo
    routing.AddDimension(
        transit_callback_index,
        6 * 60 * 60,      # slack (espera)
        17 * 60 * 60,     # jornada máxima
        False,
        "Time"
    )

    time_dimension = routing.GetDimensionOrDie("Time")

    # Permitir omitir clientes (excepto acopio)
    PENALTY = 10_000_000
    for node in range(1, num_locations):
        routing.AddDisjunction([manager.NodeToIndex(node)], PENALTY)

    # Ventanas horarias
    for node, window in enumerate(time_windows):
        index = manager.NodeToIndex(node)
        time_dimension.CumulVar(index).SetRange(window[0], window[1])

    for vehicle_id in range(num_vehicles):
        start_index = routing.Start(vehicle_id)
        time_dimension.CumulVar(start_index).SetRange(
            time_windows[0][0],
            time_windows[0][1]
        )

    # Parámetros de búsqueda
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 10

    solution = routing.SolveWithParameters(search_parameters)
    if solution is None:
        return None

    # 🔹 EXTRAER RUTAS + TIEMPOS
    routes = []

    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        vehicle_route = []

        while True:
            node = manager.IndexToNode(index)
            arrival_time = solution.Value(
                time_dimension.CumulVar(index)
            )

            vehicle_route.append({
                "node": node,
                "arrival": arrival_time,
                "service": service_times[node]
            })

            if routing.IsEnd(index):
                break

            index = solution.Value(routing.NextVar(index))

        routes.append(vehicle_route)

    return routes
