import json
import sys
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

def geocode_locations(locations):
    """
    Converts a list of location names into geographic coordinates.

    Args:
        locations (list): A list of strings, where each string is a location.

    Returns:
        A dictionary mapping each location name to its coordinates.
    """
    geolocator = Nominatim(user_agent="arche_tsp_solver")
    # Use a rate limiter to avoid overwhelming the geocoding service
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, error_wait_seconds=5)
    
    coordinates = {}
    for location in locations:
        try:
            loc_data = geocode(location)
            if loc_data:
                coordinates[location] = {
                    "latitude": loc_data.latitude,
                    "longitude": loc_data.longitude
                }
                print(f"Successfully geocoded: {location}")
            else:
                print(f"Warning: Could not geocode '{location}'. It will be excluded.")
        except Exception as e:
            print(f"Error geocoding '{location}': {e}. It will be excluded.")
        time.sleep(1) # Be respectful of the API usage terms

    return coordinates

def main():
    if len(sys.argv) != 3:
        print("Usage: python geocode_solver.py <input_json_path> <output_json_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    locations_to_geocode = data.get("locations", [])
    if not locations_to_geocode:
        print("No locations found in input file.")
        sys.exit(0)

    geocoded_data = geocode_locations(locations_to_geocode)

    try:
        with open(output_path, 'w') as f:
            json.dump(geocoded_data, f, indent=2)
        print(f"Geocoded data saved to {output_path}")
    except IOError as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 