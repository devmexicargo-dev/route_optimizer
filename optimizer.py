from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def optimize_routes(time_matrix, num_vehicles=1):
    """
    Optimización de rutas con:
    - Origen común (acopio)
    - Regreso obligatorio al acopio
    - Múltiples vehículos
    - Minimización de TIEMPO
    - Límite de tiempo por vehículo
    - Ventanas horarias
    """

    num_locations = len(time_matrix)

    # 🔹 Rutas CERRADAS: inicio y fin en el acopio (nodo 0)
    starts = [0] * num_vehicles
    ends = [0] * num_vehicles

    manager = pywrapcp.RoutingIndexManager(
        num_locations,
        num_vehicles,
        starts,
        ends
    )

    routing = pywrapcp.RoutingModel(manager)

    # ⏱️ Callback de tiempo
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return time_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # ⏱️ DIMENSIÓN DE TIEMPO
    MAX_TIME_PER_VEHICLE = 2 * 60 * 60  # 2 horas

    routing.AddDimension(
        transit_callback_index,
        30 * 60,              # slack (espera permitida)
        MAX_TIME_PER_VEHICLE, # máximo por vehículo
        False,
        "Time"
    )

    time_dimension = routing.GetDimensionOrDie("Time")

    # 🕒 VENTANAS HORARIAS (en segundos)
    # Nodo 0 = acopio
    time_windows = []

    # Acopio: disponible toda la jornada
    time_windows.append((0, MAX_TIME_PER_VEHICLE))

    # Clientes: ejemplo 9:00 AM – 5:00 PM
    for _ in range(num_locations - 1):
        time_windows.append((60 * 60, 9 * 60 * 60))

    # Aplicar ventanas a cada nodo
    for node, window in enumerate(time_windows):
        index = manager.NodeToIndex(node)
        time_dimension.CumulVar(index).SetRange(window[0], window[1])

    # Aplicar también al inicio de cada vehículo
    for vehicle_id in range(num_vehicles):
        start_index = routing.Start(vehicle_id)
        time_dimension.CumulVar(start_index).SetRange(
            time_windows[0][0], time_windows[0][1]
        )

    # 🔍 PARÁMETROS DE BÚSQUEDA
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 10

    solution = routing.SolveWithParameters(search_parameters)

    routes = [[] for _ in range(num_vehicles)]

    if solution:
        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            while True:
                node = manager.IndexToNode(index)
                routes[vehicle_id].append(node)
                if routing.IsEnd(index):
                    break
                index = solution.Value(routing.NextVar(index))

    return routes
