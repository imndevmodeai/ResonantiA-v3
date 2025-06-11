import subprocess
import json
import os

# --- Configuration ---
PROBLEM_DIR = "/tmp/tsp_problem"
LOCATIONS_FILE = os.path.join(PROBLEM_DIR, "locations.json")
GEOCODED_FILE = os.path.join(PROBLEM_DIR, "geocoded.json")
MATRIX_FILE = os.path.join(PROBLEM_DIR, "matrix.json")
SOLUTION_FILE = os.path.join(PROBLEM_DIR, "solution.json")
VRP_PROBLEM_FILE = os.path.join(PROBLEM_DIR, "vrp_problem.json")

# The list of towns for the salesperson to visit
CUSTOMER_LOCATIONS = [
    "Decatur, MI", "Cassopolis, MI", "Eau Claire, MI", "Niles, MI",
    "Vandalia, MI", "Edwardsburg, MI", "Hartford, MI", "Benton Harbor, MI",
    "Watervliet, MI", "Marcellus, MI", "Lawrence, MI", "Lawton, MI",
    "Granger, IN"
]
HOME_BASE = "Dowagiac, MI"

def run_command(command):
    """Executes a command and returns its output."""
    print(f"▶️  Executing: {command}")
    try:
        process = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(process.stdout)
        return process.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing command: {command}")
        print(f"   Return Code: {e.returncode}")
        print(f"   Output: {e.stdout}")
        print(f"   Error: {e.stderr}")
        raise

def setup_problem():
    """Create the directory and initial locations file."""
    os.makedirs(PROBLEM_DIR, exist_ok=True)
    all_locations = [HOME_BASE] + CUSTOMER_LOCATIONS
    with open(LOCATIONS_FILE, 'w') as f:
        json.dump({"locations": all_locations}, f)
    print(f"Problem setup in {PROBLEM_DIR}")

def register_solvers():
    """Registers the solver instances with the ArchE collective."""
    print("\n--- Registering Solver Instances ---")
    run_command(f"arche-cli instance register geocode-solver-01 '[\"geolocation_services\"]'")
    run_command(f"arche-cli instance register distance-solver-01 '[\"distance_calculation\"]'")
    # Register the new, advanced VRP solver
    run_command(f"arche-cli instance register vrp-solver-01 '[\"vrp_time_window_optimization\"]'")

def create_and_run_roadmap():
    """Creates the tasks and executes the solvers iteratively to find the minimum number of days."""
    print("\n--- Creating and Executing Roadmap ---")
    
    # --- Preamble Tasks (Geocoding and Distance Matrix) ---
    print("\n--- Step 1: Geocoding Locations ---")
    run_command(f"echo 'y' | arche-cli task create --desc 'Geocode city names' --cap 'geolocation_services'")
    run_command(f"python solvers/geocode_solver.py {LOCATIONS_FILE} {GEOCODED_FILE}")
    print("Geocoding task marked as complete (simulation).")

    print("\n--- Step 2: Calculating Distance Matrix ---")
    run_command(f"echo 'y' | arche-cli task create --desc 'Calculate travel time matrix' --cap 'distance_calculation'")
    run_command(f"python solvers/distance_solver.py {GEOCODED_FILE} {MATRIX_FILE}")
    print("Distance matrix calculation task marked as complete (simulation).")

    # --- Iterative VRP Solving ---
    print("\n--- Step 3: Iteratively Solving for Minimum Days (Two-Shift Model) ---")
    max_days_to_try = 10 # Set a reasonable upper limit
    solution_found = False
    for num_days in range(1, max_days_to_try + 1):
        solution = solve_for_n_days(num_days)
        
        if solution and solution.get("status") == "success" and solution.get("days"):
            print(f"\nSUCCESS: Found a valid plan for {num_days} day(s).")
            print_solution(solution)
            solution_found = True
            break
        else:
            reason = solution.get('reason', 'Unknown error') if solution else "Solver script failed"
            print(f"FAILURE: Could not find a solution for {num_days} day(s). Reason: {reason}")
    
    if not solution_found:
        print("\n--- FINAL RESULT ---")
        print(f"Could not find a feasible solution within the maximum limit of {max_days_to_try} days.")
        print("This suggests the constraints (number of locations vs. available time) are too tight.")

def solve_for_n_days(num_days):
    """Prepares the problem and calls the VRP solver for a specific number of days."""
    print(f"\n--- Attempting to solve for {num_days} day(s) ---")
    
    with open(MATRIX_FILE, 'r') as f:
        problem_data = json.load(f)

    # Your model: 2 shifts per day, AM and PM.
    # This translates to 2 "vehicles" per day in the VRP.
    num_vehicles = num_days * 2
    
    # Define time windows for each shift (vehicle)
    # Morning: 10am to 1pm (3 hours) = 10*3600 to 13*3600
    # Afternoon: 2pm to 6pm (4 hours) = 14*3600 to 18*3600
    vehicle_time_windows = []
    for day in range(num_days):
        # Morning shift
        vehicle_time_windows.append([36000, 46800])
        # Afternoon shift
        vehicle_time_windows.append([50400, 64800])

    # Find the depot index (Dowagiac, MI)
    try:
        depot_index = problem_data['locations'].index(HOME_BASE)
    except ValueError:
        print(f"Error: Home base '{HOME_BASE}' not found in locations list.")
        return None

    # Define average dwell time (service time) at each location
    min_dwell_minutes = 2
    max_dwell_minutes = 15
    avg_dwell_seconds = int(((min_dwell_minutes + max_dwell_minutes) / 2) * 60)
    dwell_times = [avg_dwell_seconds] * len(problem_data['locations'])


    # Assemble the final problem payload for the solver
    solver_problem = {
        "locations": problem_data['locations'],
        "time_matrix": problem_data['time_matrix'],
        "num_vehicles": num_vehicles,
        "vehicle_time_windows": vehicle_time_windows,
        "num_days_in_plan": num_days,
        "depot": depot_index,
        "dwell_times": dwell_times
    }

    with open(VRP_PROBLEM_FILE, 'w') as f:
        json.dump(solver_problem, f, indent=2)

    # Call the specialized VRP solver instance
    run_command(f"python solvers/tsp_solver.py {VRP_PROBLEM_FILE} {SOLUTION_FILE}")

    # Check the result
    with open(SOLUTION_FILE, 'r') as f:
        solution_data = json.load(f)
    
    return solution_data

def print_solution(solution):
    """Prints the final solution in a readable format."""
    if solution.get("status") == "success" and solution.get("days"):
        print("✅ Optimized multi-day route found!")
        for day in solution["days"]:
            print(f"\n--- Day {day['day']} ---")
            for shift in day["shifts"]:
                route_str = " -> ".join(shift['route'])
                print(f"  Shift: {shift['shift']}")
                print(f"    Route: {route_str}")
    else:
        print("❌ Solution data is missing or invalid.")
        print(f"   Solver status: {solution.get('status')}")

def cleanup():
    """Unregister instances."""
    print("\n--- Unregistering Instances ---")
    run_command("arche-cli instance unregister geocode-solver-01")
    run_command("arche-cli instance unregister distance-solver-01")
    run_command("arche-cli instance unregister vrp-solver-01")

def main():
    """Main execution function."""
    try:
        register_solvers()
        create_and_run_roadmap()

    except Exception as e:
        print(f"\nAn unexpected error occurred in the main script: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main() 