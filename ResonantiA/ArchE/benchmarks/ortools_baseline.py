import logging
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math

logger = logging.getLogger(__name__)

def solve_tsp_ortools(cities_data: list, time_limit_seconds: int = 30) -> tuple:
    """
    Solves the Traveling Salesman Problem for a given list of cities using Google OR-Tools.

    Args:
        cities_data (list): A list of dictionaries, where each dictionary represents a city
                            and has 'id', 'x', and 'y' keys.
                            Example: [{'id': 1, 'x': 10.0, 'y': 20.0}, ...]
        time_limit_seconds (int): Maximum time allowed for the solver.

    Returns:
        tuple: (route, distance)
               route (list): Ordered list of city IDs in the best tour found.
                             Returns None if no solution is found.
               distance (float): Total distance of the best tour found.
                                 Returns float('inf') if no solution is found.
    """
    if not cities_data:
        logger.warning("OR-Tools: No city data provided.")
        return None, float('inf')

    num_nodes = len(cities_data)
    if num_nodes == 0:
        logger.warning("OR-Tools: Empty city list.")
        return [], 0.0

    city_id_to_index = {city['id']: i for i, city in enumerate(cities_data)}
    index_to_city_id = {i: city['id'] for i, city in enumerate(cities_data)}

    manager = pywrapcp.RoutingIndexManager(num_nodes, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        city1 = cities_data[from_node]
        city2 = cities_data[to_node]
        return math.sqrt((city1['x'] - city2['x'])**2 + (city1['y'] - city2['y'])**2)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(time_limit_seconds)

    logger.info(f"OR-Tools: Starting TSP solve for {num_nodes} cities, time limit {time_limit_seconds}s.")
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        logger.info(f"OR-Tools: Solution found. Objective: {solution.ObjectiveValue()}")
        index = routing.Start(0)
        route_indices = []
        while not routing.IsEnd(index):
            route_indices.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route_indices.append(manager.IndexToNode(index)) # Add the depot (end node)
        
        final_route_city_ids = [index_to_city_id[node_idx] for node_idx in route_indices[:-1]]
        return final_route_city_ids, solution.ObjectiveValue()
    else:
        logger.warning("OR-Tools: No solution found.")
        return None, float('inf')

solve = solve_tsp_ortools

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sample_cities = [
        {'id': 1, 'x': 0, 'y': 0},
        {'id': 2, 'x': 0, 'y': 10},
        {'id': 3, 'x': 10, 'y': 10},
        {'id': 4, 'x': 10, 'y': 0}
    ]
    
    print(f"Solving for {len(sample_cities)} cities...")
    route, distance = solve(sample_cities, time_limit_seconds=5)

    if route:
        print(f"Route found: {route}")
        print(f"Distance: {distance}")
        assert distance == 40.0, f"Expected distance 40.0, got {distance}"
        assert len(route) == len(sample_cities), f"Expected route length {len(sample_cities)}, got {len(route)}"
        assert sorted(route) == sorted([c['id'] for c in sample_cities]), f"Route {route} does not contain all city IDs"
        print("Dummy OR-Tools test passed.")
    else:
        print("No solution found for dummy test.")

    one_city =  [{'id': 100, 'x': 5, 'y': 5}]
    print(f"\nSolving for {len(one_city)} city...")
    route_one, distance_one = solve(one_city, time_limit_seconds=5)
    if route_one:
        print(f"Route found: {route_one}")
        print(f"Distance: {distance_one}")
        assert distance_one == 0.0, f"Expected distance 0.0 for one city, got {distance_one}"
        assert route_one == [100], f"Expected route [100] for one city, got {route_one}"
        print("Dummy OR-Tools test for one city passed.")
    else:
        print("No solution found for one city dummy test.")

    no_cities = []
    print(f"\nSolving for {len(no_cities)} cities...")
    route_no, distance_no = solve(no_cities, time_limit_seconds=5)
    print(f"Route found: {route_no}") # Should be []
    print(f"Distance: {distance_no}") # Should be 0.0
    assert distance_no == 0.0, f"Expected distance 0.0 for no cities, got {distance_no}"
    assert route_no == [], f"Expected route [] for no cities, got {route_no}"
    print("Dummy OR-Tools test for no cities passed.") 