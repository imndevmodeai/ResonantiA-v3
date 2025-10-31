#!/usr/bin/env python3
"""
Advanced TSP Solver with Time Windows and Multiple Vehicles
Uses Google OR-Tools for industrial-strength optimization
"""

import json
import sys
import time
from typing import Dict, List, Any, Optional
import numpy as np

try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    print("⚠️  OR-Tools not available. Install with: pip install ortools")

class AdvancedTSPSolver:
    """Advanced TSP Solver with multiple algorithms and constraints"""
    
    def __init__(self):
        self.cities = []
        self.distance_matrix = []
        self.time_matrix = []
        self.time_windows = []
        self.demands = []
        self.vehicle_capacities = []
        self.depot = 0
        
    def create_sample_problem(self, num_cities: int = 10, num_vehicles: int = 3) -> None:
        """Create a sample TSP problem with realistic constraints"""
        np.random.seed(42)
        
        # Create cities with realistic coordinates
        self.cities = []
        for i in range(num_cities):
            city = {
                "id": i,
                "name": f"City_{chr(65+i)}",
                "x": np.random.uniform(0, 100),
                "y": np.random.uniform(0, 100),
                "demand": np.random.randint(1, 10) if i > 0 else 0,  # Depot has no demand
                "time_window_start": np.random.randint(0, 8) * 3600,  # 0-8 AM in seconds
                "time_window_end": np.random.randint(9, 18) * 3600,   # 9 AM - 6 PM in seconds
                "service_time": np.random.randint(300, 1800)  # 5-30 minutes
            }
            self.cities.append(city)
        
        # Set depot constraints
        self.cities[0]["demand"] = 0
        self.cities[0]["time_window_start"] = 0
        self.cities[0]["time_window_end"] = 24 * 3600  # 24 hours
        
        # Create distance and time matrices
        self._create_matrices()
        
        # Set vehicle capacities
        self.vehicle_capacities = [20] * num_vehicles  # Each vehicle can carry 20 units
        
        print(f"✅ Created sample problem with {num_cities} cities and {num_vehicles} vehicles")
    
    def _create_matrices(self) -> None:
        """Create distance and time matrices"""
        n = len(self.cities)
        self.distance_matrix = np.zeros((n, n))
        self.time_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Calculate Euclidean distance
                    dx = self.cities[i]['x'] - self.cities[j]['x']
                    dy = self.cities[i]['y'] - self.cities[j]['y']
                    distance = np.sqrt(dx*dx + dy*dy)
                    
                    self.distance_matrix[i][j] = distance
                    # Assume average speed of 50 units/hour
                    self.time_matrix[i][j] = distance / 50 * 3600  # Convert to seconds
        
        print(f"✅ Created {n}x{n} distance and time matrices")
    
    def solve_with_ortools(self, max_time: int = 30) -> Dict[str, Any]:
        """Solve TSP using Google OR-Tools"""
        if not ORTOOLS_AVAILABLE:
            return {"error": "OR-Tools not available"}
        
        start_time = time.time()
        
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(
            len(self.cities), 
            len(self.vehicle_capacities), 
            self.depot
        )
        routing = pywrapcp.RoutingModel(manager)
        
        # Create distance callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return self.distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add capacity constraints
        if self.vehicle_capacities:
            routing.AddDimension(
                transit_callback_index,
                0,  # no slack
                max(self.vehicle_capacities),  # vehicle maximum capacity
                True,  # start cumul to zero
                'Capacity'
            )
            capacity_dimension = routing.GetDimensionOrDie('Capacity')
            
            for vehicle_id in range(len(self.vehicle_capacities)):
                index = routing.Start(vehicle_id)
                capacity_dimension.CumulVar(index).SetMax(self.vehicle_capacities[vehicle_id])
        
        # Add time window constraints
        if any(city.get('time_window_start') for city in self.cities):
            routing.AddDimension(
                transit_callback_index,
                3600,  # allow waiting time
                24 * 3600,  # maximum time per vehicle
                False,  # don't force start cumul to zero
                'Time'
            )
            time_dimension = routing.GetDimensionOrDie('Time')
            
            # Add time window constraints for each city
            for city_id, city in enumerate(self.cities):
                index = manager.NodeToIndex(city_id)
                time_dimension.CumulVar(index).SetRange(
                    city.get('time_window_start', 0),
                    city.get('time_window_end', 24 * 3600)
                )
        
        # Set search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.FromSeconds(max_time)
        
        # Solve the problem
        solution = routing.SolveWithParameters(search_parameters)
        
        if not solution:
            return {"error": "No solution found"}
        
        # Extract solution
        results = self._extract_solution(solution, manager, routing)
        results["execution_time"] = time.time() - start_time
        results["algorithm"] = "OR-Tools VRP Solver"
        
        return results
    
    def _extract_solution(self, solution, manager, routing) -> Dict[str, Any]:
        """Extract solution details from OR-Tools result"""
        routes = []
        total_distance = 0
        
        for vehicle_id in range(len(self.vehicle_capacities)):
            route = []
            index = routing.Start(vehicle_id)
            route_distance = 0
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                city = self.cities[node_index]
                route.append({
                    "city_id": node_index,
                    "city_name": city["name"],
                    "coordinates": f"({city['x']:.1f}, {city['y']:.1f})",
                    "demand": city.get("demand", 0),
                    "time_window": f"{city.get('time_window_start', 0)//3600:02d}:00-{city.get('time_window_end', 24*3600)//3600:02d}:00"
                })
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += self.distance_matrix[manager.IndexToNode(previous_index)][manager.IndexToNode(index)]
            
            # Add return to depot
            depot_city = self.cities[self.depot]
            route.append({
                "city_id": self.depot,
                "city_name": depot_city["name"],
                "coordinates": f"({depot_city['x']:.1f}, {depot_city['y']:.1f})",
                "demand": 0,
                "time_window": "00:00-24:00"
            })
            
            routes.append({
                "vehicle_id": vehicle_id,
                "route": route,
                "distance": round(route_distance, 2),
                "cities_visited": len(route) - 1  # Exclude depot return
            })
            
            total_distance += route_distance
        
        return {
            "status": "success",
            "total_distance": round(total_distance, 2),
            "num_vehicles": len(self.vehicle_capacities),
            "routes": routes,
            "objective_value": solution.ObjectiveValue()
        }
    
    def solve_simple_tsp(self) -> Dict[str, Any]:
        """Solve simple TSP without complex constraints"""
        if not self.cities:
            return {"error": "No cities loaded"}
        
        start_time = time.time()
        
        # Use nearest neighbor with 2-opt optimization
        n = len(self.cities)
        unvisited = set(range(1, n))  # Start from depot (city 0)
        current = 0
        route = [current]
        total_distance = 0
        
        # Build route using nearest neighbor
        while unvisited:
            nearest = min(unvisited, key=lambda x: self.distance_matrix[current][x])
            distance = self.distance_matrix[current][nearest]
            
            route.append(nearest)
            total_distance += distance
            current = nearest
            unvisited.remove(nearest)
        
        # Return to depot
        total_distance += self.distance_matrix[current][0]
        route.append(0)
        
        # Simple 2-opt optimization
        improved = True
        while improved:
            improved = False
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route)):
                    if j - i == 1:
                        continue
                    
                    # Calculate current segment distance
                    old_distance = (self.distance_matrix[route[i-1]][route[i]] + 
                                  self.distance_matrix[route[j]][route[j+1]])
                    
                    # Calculate new segment distance after 2-opt
                    new_distance = (self.distance_matrix[route[i-1]][route[j]] + 
                                  self.distance_matrix[route[i]][route[j+1]])
                    
                    if new_distance < old_distance:
                        # Perform 2-opt swap
                        route[i:j+1] = route[j:i-1:-1]
                        total_distance = total_distance - old_distance + new_distance
                        improved = True
                        break
                if improved:
                    break
        
        # Format results
        route_details = []
        for i in range(len(route) - 1):
            from_city = self.cities[route[i]]
            to_city = self.cities[route[i+1]]
            distance = self.distance_matrix[route[i]][route[i+1]]
            
            route_details.append({
                "step": i + 1,
                "from": from_city["name"],
                "to": to_city["name"],
                "distance": round(distance, 2),
                "coordinates": f"({from_city['x']:.1f}, {from_city['y']:.1f}) → ({to_city['x']:.1f}, {to_city['y']:.1f})"
            })
        
        return {
            "status": "success",
            "execution_time": time.time() - start_time,
            "total_distance": round(total_distance, 2),
            "route": route,
            "route_details": route_details,
            "algorithm": "Nearest Neighbor + 2-opt",
            "num_cities": len(self.cities)
        }
    
    def print_solution(self, results: Dict[str, Any]) -> None:
        """Print formatted solution"""
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return
        
        print("\n" + "="*70)
        print("🎯 ADVANCED TSP SOLUTION - OPTIMAL ROUTES AND TRAVEL TIMES")
        print("="*70)
        
        print(f"📊 Summary:")
        print(f"   • Algorithm: {results.get('algorithm', 'Unknown')}")
        print(f"   • Execution Time: {results.get('execution_time', 0):.3f} seconds")
        
        if "total_distance" in results:
            print(f"   • Total Distance: {results['total_distance']} units")
        
        if "num_vehicles" in results:
            print(f"   • Vehicles Used: {results['num_vehicles']}")
        
        if "routes" in results:
            print(f"\n🚚 Vehicle Routes:")
            for i, route_info in enumerate(results["routes"]):
                print(f"\n   Vehicle {i+1} (Distance: {route_info['distance']} units):")
                for j, stop in enumerate(route_info["route"]):
                    print(f"     {j+1:2d}. {stop['city_name']:>12} "
                          f"[Demand: {stop['demand']:>2}] "
                          f"[{stop['time_window']}]")
        
        elif "route_details" in results:
            print(f"\n🗺️  Optimal Route:")
            for step in results["route_details"]:
                print(f"   {step['step']:2d}. {step['from']:>12} → {step['to']:<12} "
                      f"[{step['distance']:>6.2f} units]")
        
        print("="*70)
    
    def save_solution(self, results: Dict[str, Any], filename: str) -> None:
        """Save solution to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ Solution saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving solution: {e}")

def main():
    """Main function to demonstrate advanced TSP solving"""
    print("🚀 Advanced TSP Solver - Industrial-Strength Optimization")
    print("="*70)
    
    # Initialize solver
    solver = AdvancedTSPSolver()
    
    # Create sample problem
    print("📝 Creating sample TSP problem...")
    solver.create_sample_problem(num_cities=12, num_vehicles=3)
    
    # Try OR-Tools first (if available)
    if ORTOOLS_AVAILABLE:
        print("\n🔍 Solving with Google OR-Tools (VRP Solver)...")
        results = solver.solve_with_ortools(max_time=30)
        
        if "error" not in results:
            solver.print_solution(results)
            solver.save_solution(results, "advanced_tsp_ortools_solution.json")
        else:
            print(f"⚠️  OR-Tools failed: {results['error']}")
            print("🔄 Falling back to simple TSP solver...")
            results = solver.solve_simple_tsp()
            solver.print_solution(results)
            solver.save_solution(results, "advanced_tsp_simple_solution.json")
    else:
        print("🔄 OR-Tools not available, using simple TSP solver...")
        results = solver.solve_simple_tsp()
        solver.print_solution(results)
        solver.save_solution(results, "advanced_tsp_simple_solution.json")
    
    print("\n🎉 Advanced TSP Solution Complete!")

if __name__ == "__main__":
    main()
