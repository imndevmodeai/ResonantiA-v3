import json
import sys
import numpy as np
from geopy.distance import great_circle

def calculate_time_matrix(coordinates, avg_speed_kmh=80):
    """
    Calculates a travel time matrix between a set of coordinates.

    Args:
        coordinates (dict): A dictionary of location data, including latitude and longitude.
        avg_speed_kmh (int): Average travel speed in km/h to estimate time.

    Returns:
        A dictionary containing the list of locations and the time matrix in hours.
    """
    locations = list(coordinates.keys())
    num_locations = len(locations)
    # Initialize a matrix of zeros
    time_matrix = np.zeros((num_locations, num_locations))

    for i in range(num_locations):
        for j in range(num_locations):
            if i == j:
                continue
            
            loc1 = locations[i]
            loc2 = locations[j]
            
            coords1 = (coordinates[loc1]['latitude'], coordinates[loc1]['longitude'])
            coords2 = (coordinates[loc2]['latitude'], coordinates[loc2]['longitude'])
            
            # Calculate distance in kilometers
            distance_km = great_circle(coords1, coords2).kilometers
            
            # Calculate time in hours
            travel_time_hours = distance_km / avg_speed_kmh
            time_matrix[i, j] = travel_time_hours

    return {"locations": locations, "time_matrix": time_matrix.tolist()}

def main():
    if len(sys.argv) != 3:
        print("Usage: python distance_solver.py <input_geocoded_json> <output_matrix_json>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        with open(input_path, 'r') as f:
            coordinates = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    if not coordinates:
        print("Input file contains no coordinate data.")
        sys.exit(0)

    time_matrix_data = calculate_time_matrix(coordinates)

    try:
        with open(output_path, 'w') as f:
            json.dump(time_matrix_data, f, indent=2)
        print(f"Time matrix data saved to {output_path}")
    except IOError as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 