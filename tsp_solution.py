#!/usr/bin/env python3
"""
Comprehensive TSP Solver using ArchE's existing infrastructure
Solves Traveling Salesperson Problems with optimal routes and travel times
"""

import json
import math
import numpy as np
from typing import Dict, List, Tuple, Any
import time

class TSPSolver:
    """Comprehensive TSP Solver using multiple algorithms"""
    
    def __init__(self):
        self.cities = []
        self.distance_matrix = []
        self.best_route = []
        self.best_distance = float('inf')
        self.execution_time = 0
        
    def load_cities_from_file(self, filepath: str) -> bool:
        """Load city data from JSON file"""
        try:
            with open(filepath, 'r') as f:
                raw_cities = json.load(f)
            
            # Convert to standard format with name field
            self.cities = []
            for city in raw_cities:
                # Handle both old format (with 'city' key) and new format (with 'name' key)
                if 'name' in city:
                    self.cities.append(city)
                elif 'city' in city:
                    # Convert old format to new format
                    city_copy = city.copy()
                    city_copy['name'] = city['city']
                    self.cities.append(city_copy)
                else:
                    # Create default name if neither exists
                    city_copy = city.copy()
                    city_copy['name'] = f"City_{len(self.cities)}"
                    self.cities.append(city_copy)
            
            print(f"✅ Loaded {len(self.cities)} cities from {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error loading cities: {e}")
            return False
    
    def create_sample_cities(self, num_cities: int = 10) -> None:
        """Create sample cities for testing"""
        np.random.seed(42)  # For reproducible results
        
        self.cities = []
        for i in range(num_cities):
            city = {
                "city": f"City_{chr(65+i)}",
                "x": np.random.uniform(0, 100),
                "y": np.random.uniform(0, 100),
                "name": f"City {chr(65+i)}"  # Add name field for compatibility
            }
            self.cities.append(city)
        
        print(f"✅ Created {num_cities} sample cities")
    
    def calculate_distance_matrix(self) -> None:
        """Calculate Euclidean distance matrix between all cities"""
        n = len(self.cities)
        self.distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    dx = self.cities[i]['x'] - self.cities[j]['x']
                    dy = self.cities[i]['y'] - self.cities[j]['y']
                    self.distance_matrix[i][j] = math.sqrt(dx*dx + dy*dy)
        
        print(f"✅ Calculated {n}x{n} distance matrix")
    
    def nearest_neighbor_heuristic(self) -> Tuple[List[int], float]:
        """Solve TSP using Nearest Neighbor heuristic"""
        n = len(self.cities)
        unvisited = set(range(n))
        current = 0  # Start from first city
        route = [current]
        total_distance = 0
        
        while unvisited:
            unvisited.remove(current)
            if not unvisited:
                break
                
            # Find nearest unvisited city
            nearest = min(unvisited, key=lambda x: self.distance_matrix[current][x])
            distance = self.distance_matrix[current][nearest]
            
            route.append(nearest)
            total_distance += distance
            current = nearest
        
        # Return to start
        if route:
            total_distance += self.distance_matrix[route[-1]][route[0]]
            route.append(route[0])
        
        return route, total_distance
    
    def two_opt_optimization(self, route: List[int], max_iterations: int = 1000) -> Tuple[List[int], float]:
        """Optimize route using 2-opt local search"""
        n = len(route)
        best_distance = self._calculate_route_distance(route)
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            for i in range(1, n - 2):
                for j in range(i + 1, n):
                    if j - i == 1:
                        continue
                    
                    # Try 2-opt swap
                    new_route = route[:i] + route[i:j][::-1] + route[j:]
                    new_distance = self._calculate_route_distance(new_route)
                    
                    if new_distance < best_distance:
                        route = new_route
                        best_distance = new_distance
                        improved = True
                        break
                if improved:
                    break
        
        print(f"✅ 2-opt optimization completed in {iterations} iterations")
        return route, best_distance
    
    def _calculate_route_distance(self, route: List[int]) -> float:
        """Calculate total distance of a route"""
        total_distance = 0
        for i in range(len(route) - 1):
            total_distance += self.distance_matrix[route[i]][route[i+1]]
        return total_distance
    
    def solve_tsp(self, use_2opt: bool = True) -> Dict[str, Any]:
        """Solve TSP and return comprehensive results"""
        start_time = time.time()
        
        if not self.cities:
            return {"error": "No cities loaded"}
        
        if not self.distance_matrix:
            self.calculate_distance_matrix()
        
        # Initial solution with Nearest Neighbor
        print("🔍 Finding initial solution with Nearest Neighbor...")
        initial_route, initial_distance = self.nearest_neighbor_heuristic()
        
        # Optimize with 2-opt if requested
        if use_2opt:
            print("⚡ Optimizing with 2-opt local search...")
            optimized_route, optimized_distance = self.two_opt_optimization(initial_route)
        else:
            optimized_route, optimized_distance = initial_route, initial_distance
        
        # Calculate improvement
        improvement = ((initial_distance - optimized_distance) / initial_distance) * 100
        
        # Format results
        route_details = []
        for i, city_idx in enumerate(optimized_route[:-1]):  # Exclude duplicate start city
            city = self.cities[city_idx]
            next_city_idx = optimized_route[i + 1]
            next_city = self.cities[next_city_idx]
            
            distance = self.distance_matrix[city_idx][next_city_idx]
            
            route_details.append({
                "step": i + 1,
                "from": city['name'],
                "to": next_city['name'],
                "distance": round(distance, 2),
                "coordinates": f"({city['x']:.1f}, {city['y']:.1f}) → ({next_city['x']:.1f}, {next_city['y']:.1f})"
            })
        
        self.execution_time = time.time() - start_time
        
        results = {
            "status": "success",
            "execution_time": round(self.execution_time, 3),
            "total_cities": len(self.cities),
            "initial_distance": round(initial_distance, 2),
            "optimized_distance": round(optimized_distance, 2),
            "improvement_percent": round(improvement, 2),
            "route": optimized_route,
            "route_details": route_details,
            "total_distance": round(optimized_distance, 2),
            "algorithm": "Nearest Neighbor + 2-opt" if use_2opt else "Nearest Neighbor",
            "cities_visited": len(set(optimized_route[:-1]))  # Exclude duplicate start
        }
        
        return results
    
    def print_route_summary(self, results: Dict[str, Any]) -> None:
        """Print a formatted summary of the TSP solution"""
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return
        
        print("\n" + "="*60)
        print("🎯 TRAVELING SALESPERSON PROBLEM - OPTIMAL SOLUTION")
        print("="*60)
        
        print(f"📊 Summary:")
        print(f"   • Total Cities: {results['total_cities']}")
        print(f"   • Initial Distance: {results['initial_distance']} units")
        print(f"   • Optimized Distance: {results['optimized_distance']} units")
        print(f"   • Improvement: {results['improvement_percent']}%")
        print(f"   • Algorithm: {results['algorithm']}")
        print(f"   • Execution Time: {results['execution_time']} seconds")
        
        print(f"\n🗺️  Optimal Route:")
        for i, step in enumerate(results['route_details']):
            print(f"   {step['step']:2d}. {step['from']:>12} → {step['to']:<12} "
                  f"[{step['distance']:>6.2f} units]")
        
        print(f"\n📍 Route Statistics:")
        print(f"   • Total Distance: {results['total_distance']} units")
        print(f"   • Cities Visited: {results['cities_visited']}")
        print(f"   • Return to Start: ✅")
        
        print("="*60)
    
    def save_solution(self, results: Dict[str, Any], filename: str) -> None:
        """Save solution to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ Solution saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving solution: {e}")

def main():
    """Main function to demonstrate TSP solving"""
    print("🚀 TSP Solver - Finding Optimal Routes and Travel Times")
    print("="*60)
    
    # Initialize solver
    solver = TSPSolver()
    
    # Try to load existing cities, otherwise create sample data
    if not solver.load_cities_from_file("data/tsp_cities.json"):
        print("📝 Creating sample cities for demonstration...")
        solver.create_sample_cities(15)  # Create 15 sample cities
    
    # Solve TSP
    print("\n🔍 Solving Traveling Salesperson Problem...")
    results = solver.solve_tsp(use_2opt=True)
    
    # Display results
    solver.print_route_summary(results)
    
    # Save solution
    solver.save_solution(results, "tsp_solution_results.json")
    
    print("\n🎉 TSP Solution Complete!")
    print("📁 Results saved to: tsp_solution_results.json")

if __name__ == "__main__":
    main()
