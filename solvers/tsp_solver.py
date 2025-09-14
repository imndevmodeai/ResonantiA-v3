import json
import sys
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def solve_vrptw(problem):
    """Solves a generic VRPTW problem passed as a dictionary."""
    
    # Unpack problem data for clarity
    locations = problem['locations']
    num_locations = len(locations)
    num_vehicles = problem['num_vehicles']
    depot = problem['depot']
    time_matrix = problem['time_matrix']
    dwell_times = problem['dwell_times']
    vehicle_time_windows = problem['vehicle_time_windows']
    num_days_in_plan = problem.get('num_days_in_plan', 1) # Default to 1 if not provided

    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index, to_index):
        """Returns the total time between two nodes, including service time."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        
        # Service time is only added for non-depot locations
        service_time = dwell_times[to_node] if to_node != depot else 0
        
        travel_time = time_matrix[from_node][to_node]
        return travel_time + service_time

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    time_dimension_name = 'Time'
    routing.AddDimension(
        transit_callback_index,
        3600,  # Allow 1hr slack for waiting
        3600 * 24 * num_days_in_plan,  # Planning horizon
        False,  # Don't force start cumulative to zero
        time_dimension_name
    )
    time_dimension = routing.GetDimensionOrDie(time_dimension_name)

    # Add time window constraints for each vehicle (shift)
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        start_time, end_time = vehicle_time_windows[vehicle_id]
        time_dimension.CumulVar(index).SetRange(start_time, end_time)
        # Also apply to end node
        routing.AddVariableMaximizedByFinalizer(time_dimension.CumulVar(routing.End(vehicle_id)))


    # Ensure all locations are visited
    for node_idx in range(num_locations):
        if node_idx != depot:
            routing.AddDisjunction([manager.NodeToIndex(node_idx)], 10000000)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(25)
    search_parameters.solution_limit = 5 # Find a few good solutions and pick the best

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        return format_solution(solution, manager, routing, problem)
    else:
        return {'status': 'failure', 'reason': 'No solution found by the VRP solver.'}

def format_solution(solution, manager, routing, problem):
    """Formats the raw solver output into a structured JSON."""
    if not solution:
        return {"status": "no_solution", "reason": "Solver returned no solution."}

    time_dimension = routing.GetDimensionOrDie("Time")
    
    output = {
        "status": "success",
        "objective_seconds": solution.ObjectiveValue(),
        "num_days_in_plan": problem.get('num_days_in_plan', 0),
        "days": []
    }

    shifts_per_day = 2 # Based on the two-shift model
    
    for day_index in range(problem.get('num_days_in_plan', 0)):
        day_output = {
            "day": day_index + 1,
            "shifts": []
        }
        
        for shift_index in range(shifts_per_day):
            vehicle_id = day_index * shifts_per_day + shift_index
            
            if not routing.IsVehicleUsed(solution, vehicle_id):
                continue

            route_for_vehicle = []
            index = routing.Start(vehicle_id)
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                if node_index != problem['depot']:  # Exclude depot from the route list itself
                    route_for_vehicle.append(problem['locations'][node_index])
                index = solution.Value(routing.NextVar(index))

            # Add the final return to depot
            route_for_vehicle.append(problem['locations'][problem['depot']])


            shift_name = "AM" if shift_index == 0 else "PM"
            shift_output = {
                "shift": shift_name,
                "route": [problem['locations'][problem['depot']]] + route_for_vehicle,
            }
            day_output["shifts"].append(shift_output)
            
        if day_output["shifts"]:
            output["days"].append(day_output)

    if not output["days"]:
         return {"status": "no_solution", "reason": "No vehicles were used, likely infeasible."}

    return output

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python tsp_solver.py <problem_file> <solution_file>")
        sys.exit(1)

    problem_file, solution_file = sys.argv[1], sys.argv[2]

    try:
        with open(problem_file, 'r') as f:
            problem_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        error_msg = {'status': 'failure', 'reason': f"Error reading or parsing problem file: {e}"}
        with open(solution_file, 'w') as f:
            json.dump(error_msg, f)
        sys.exit(1)

    solution_data = solve_vrptw(problem_data)

    with open(solution_file, 'w') as f:
        json.dump(solution_data, f, indent=2)

    # A friendly message to the orchestration script's log
    if solution_data['status'] == 'success':
        print(f"VRP solver found a solution. Saved to {solution_file}")
    else:
        print(f"VRP solver could not find a solution. Reason: {solution_data.get('reason')}")
