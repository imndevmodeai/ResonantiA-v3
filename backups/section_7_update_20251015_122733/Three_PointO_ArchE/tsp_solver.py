import logging
from typing import Dict, Any, List, Optional
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import numpy as np

logger = logging.getLogger(__name__)

class TSPSolver:
    """A TSP solver with multiple algorithms and real-world constraints."""

    def __init__(self):
        logger.info("TSPSolver initialized.")

    def solve_tsp(self, cities: List[Dict[str, Any]], use_2opt: bool = False) -> Dict[str, Any]:
        """Solves the TSP using nearest neighbor and optional 2-opt."""
        distance_matrix = self._compute_distance_matrix(cities)
        num_cities = len(cities)
        
        # Nearest Neighbor Heuristic
        route, total_distance = self.nearest_neighbor_heuristic(distance_matrix)
        
        if use_2opt:
            route, total_distance = self.two_opt_optimization(route, distance_matrix)
            
        return {
            "route": [cities[i]['name'] for i in route],
            "total_distance": total_distance
        }

    def nearest_neighbor_heuristic(self, distance_matrix: np.ndarray) -> (List[int], float):
        """Generates a TSP solution using the nearest neighbor heuristic."""
        num_cities = len(distance_matrix)
        unvisited = list(range(1, num_cities))
        route = [0]
        total_distance = 0
        
        current_city = 0
        while unvisited:
            nearest_city = min(unvisited, key=lambda city: distance_matrix[current_city][city])
            total_distance += distance_matrix[current_city][nearest_city]
            route.append(nearest_city)
            unvisited.remove(nearest_city)
            current_city = nearest_city
            
        total_distance += distance_matrix[route[-1]][0] # Return to start
        return route, total_distance

    def two_opt_optimization(self, route: List[int], distance_matrix: np.ndarray) -> (List[int], float):
        """Improves a TSP route using 2-opt optimization."""
        best_route = route
        improved = True
        while improved:
            improved = False
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route)):
                    if j - i == 1: continue
                    new_route = route[:]
                    new_route[i:j] = route[j - 1:i - 1:-1] # Reverse the segment
                    new_distance = self._calculate_route_distance(new_route, distance_matrix)
                    
                    if new_distance < self._calculate_route_distance(best_route, distance_matrix):
                        best_route = new_route
                        improved = True
            route = best_route
        
        return best_route, self._calculate_route_distance(best_route, distance_matrix)

    def solve_with_ortools(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Solves a VRP with constraints using OR-Tools."""
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                               data['num_vehicles'], data['depot'])
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add other constraints like time windows, capacities, etc. here

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            return self._format_ortools_solution(data, manager, routing, solution)
        else:
            return {"error": "No solution found."}

    def _compute_distance_matrix(self, cities: List[Dict[str, Any]]) -> np.ndarray:
        """Computes the Euclidean distance matrix for a list of cities."""
        num_cities = len(cities)
        distance_matrix = np.zeros((num_cities, num_cities))
        for i in range(num_cities):
            for j in range(num_cities):
                dist = np.sqrt((cities[i]['x'] - cities[j]['x'])**2 + 
                               (cities[i]['y'] - cities[j]['y'])**2)
                distance_matrix[i][j] = dist
        return distance_matrix

    def _calculate_route_distance(self, route: List[int], distance_matrix: np.ndarray) -> float:
        """Calculates the total distance of a route."""
        total_distance = 0
        for i in range(len(route) - 1):
            total_distance += distance_matrix[route[i]][route[i+1]]
        total_distance += distance_matrix[route[-1]][route[0]] # Return to start
        return total_distance
        
    def _format_ortools_solution(self, data, manager, routing, solution):
        """Formats the OR-Tools solution into a dictionary."""
        routes = []
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = [manager.IndexToNode(index)]
            route_distance = 0
            while not routing.IsEnd(index):
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route.append(manager.IndexToNode(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            routes.append({
                "vehicle_id": vehicle_id,
                "route": route,
                "distance": route_distance
            })
        return {"routes": routes}
