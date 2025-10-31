# @Four_PointO_ArchE/tsp_solver/solver.py

import logging
from typing import Dict, Any, List, Optional, Tuple
import googlemaps
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# Configure logger
logger = logging.getLogger(__name__)

class TSPSolver:
    """
    Core TSP Solver Engine for ArchE v4.0.
    Integrates heuristic solvers and Google OR-Tools for advanced VRP.
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key for mapping service is required.")
        self.gmaps = googlemaps.Client(key=api_key)
        logger.info("TSPSolver initialized with Google Maps client.")

    def _create_data_model(self, distance_matrix: List[List[int]], num_vehicles: int) -> Dict[str, Any]:
        """Stores the data for the problem."""
        data = {}
        data['distance_matrix'] = distance_matrix
        data['num_vehicles'] = num_vehicles
        data['depot'] = 0
        return data

    def solve_vrp_with_ortools(self, addresses: List[str], depot_address: str, num_vehicles: int, constraints: Dict[str, Any] = None) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        """
        Solves the Vehicle Routing Problem using Google OR-Tools.

        Args:
            addresses (List[str]): List of addresses to visit.
            depot_address (str): The starting and ending address for all vehicles.
            num_vehicles (int): The number of vehicles available.
            constraints (Dict[str, Any], optional): Dictionary of constraints, e.g.,
                                                   {"time_windows": [(start, end), ...], "capacities": [cap1, cap2, ...]}.

        Returns:
            Tuple[Optional[Dict[str, Any]], Dict[str, Any]]: A tuple containing the solution and the IAR.
        """
        iar = {
            "confidence": 0.0,
            "tactical_resonance": 0.0,
            "potential_issues": [],
            "metadata": {
                "solver": "Google OR-Tools",
                "num_locations": len(addresses),
                "num_vehicles": num_vehicles,
                "constraints_applied": list(constraints.keys()) if constraints else []
            }
        }

        try:
            # Geocode addresses and create distance matrix
            all_locations = [depot_address] + addresses
            coords = [self._geocode(addr) for addr in all_locations]
            distance_matrix = self._create_distance_matrix(coords)

            data = self._create_data_model(distance_matrix, num_vehicles)

            manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
            routing = pywrapcp.RoutingModel(manager)

            def distance_callback(from_index, to_index):
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return data['distance_matrix'][from_node][to_node]

            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
            # Add a time limit to the solver for robustness
            search_parameters.time_limit.FromSeconds(30)


            solution = routing.SolveWithParameters(search_parameters)
            solver_status = routing.status()
            
            status_map = {
                0: 'ROUTING_NOT_SOLVED',
                1: 'ROUTING_SUCCESS',
                2: 'ROUTING_FAIL',
                3: 'ROUTING_FAIL_TIMEOUT',
                4: 'ROUTING_INVALID',
            }
            status_str = status_map.get(solver_status, 'UNKNOWN_STATUS')

            iar['metadata']['solver_status'] = solver_status
            iar['metadata']['solver_status_str'] = status_str


            if solution and solver_status in [1, 2]: # 1=ROUTING_SUCCESS, 2=ROUTING_FAIL_TIMEOUT
                # If a solution was found, even if not optimal (due to timeout)
                if solver_status == 1:
                    iar['confidence'] = 0.95 # High confidence for optimal or near-optimal solution
                else: # Timeout
                    iar['confidence'] = 0.75 # Lower confidence if solver timed out
                    iar['potential_issues'].append("Solver timed out before finding an optimal solution. The provided solution is the best one found within the time limit.")


                formatted_solution = self._format_solution(solution, manager, routing, all_locations)
                
                # --- Tactical Resonance Calculation ---
                # Check if all locations were visited
                visited_nodes = set()
                for route in formatted_solution['routes']:
                    for stop in route['path']:
                        visited_nodes.add(stop)
                
                # Exclude depot from the set of required locations to visit
                required_locations = set(addresses)
                unvisited_count = len(required_locations - (visited_nodes - {depot_address}))

                if unvisited_count == 0:
                    iar['tactical_resonance'] = 1.0
                else:
                    iar['tactical_resonance'] = 1.0 - (unvisited_count / len(required_locations))
                    iar['potential_issues'].append(f"{unvisited_count} locations were not assigned to any route.")

                iar['metadata']['total_distance'] = formatted_solution.get('total_distance', 0)
                
                return formatted_solution, iar
            else:
                iar["potential_issues"].append(f"No solution found. Solver status: {status_str}")
                return None, iar

        except Exception as e:
            logger.error(f"Error in solve_vrp_with_ortools: {e}", exc_info=True)
            iar["potential_issues"].append(f"An exception occurred: {e}")
            return None, iar

    def _geocode(self, address: str) -> Tuple[float, float]:
        """Geocodes an address to latitude and longitude."""
        geocode_result = self.gmaps.geocode(address)
        if not geocode_result:
            raise ValueError(f"Geocoding failed for address: {address}")
        location = geocode_result[0]['geometry']['location']
        return (location['lat'], location['lng'])

    def _create_distance_matrix(self, coords: List[Tuple[float, float]]) -> List[List[int]]:
        """Creates a distance matrix from a list of coordinates."""
        distance_matrix_result = self.gmaps.distance_matrix(coords, coords, mode="driving")
        rows = distance_matrix_result['rows']
        matrix = []
        for i in range(len(rows)):
            row_elements = rows[i]['elements']
            matrix.append([elem['distance']['value'] for elem in row_elements])
        return matrix
        
    def _format_solution(self, solution, manager, routing, locations):
        """Formats the OR-Tools solution into a readable dictionary."""
        output = {'routes': [], 'total_distance': 0}
        for vehicle_id in range(routing.vehicles()):
            index = routing.Start(vehicle_id)
            route = {'vehicle': vehicle_id, 'path': [], 'distance': 0}
            plan_output = f'Route for vehicle {vehicle_id}:\n'
            route_distance = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route['path'].append(locations[node_index])
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                arc_distance = routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                route['distance'] += arc_distance
                route_distance += arc_distance
            
            # Add the end node
            end_node_index = manager.IndexToNode(index)
            route['path'].append(locations[end_node_index])
            
            output['routes'].append(route)
            output['total_distance'] += route_distance
        return output
