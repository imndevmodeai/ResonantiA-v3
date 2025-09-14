# @Four_PointO_ArchE/tools/tsp_tools.py

from typing import List, Tuple
from datetime import datetime, timedelta

def create_time_windows(locations: List[str], business_hours: str = "09:00-17:00") -> List[Tuple[int, int]]:
    """
    Creates a list of time windows for a list of locations.

    For simplicity, this function currently assigns the same time window to all locations
    based on the business_hours string. A more advanced implementation would
    fetch specific hours for each location.

    Args:
        locations (List[str]): A list of addresses. The number of locations
                               determines how many time windows are created. The depot is assumed to be the first element.
        business_hours (str, optional): A string in "HH:MM-HH:MM" format. Defaults to "09:00-17:00".

    Returns:
        List[Tuple[int, int]]: A list of tuples, where each tuple is a (start_time, end_time)
                                window in seconds from the beginning of the day. The first entry is for the depot (0, 86400).
    """
    
    # Depot has an open time window
    time_windows = [(0, 86400)] 

    try:
        start_str, end_str = business_hours.split('-')
        start_hour, start_minute = map(int, start_str.split(':'))
        end_hour, end_minute = map(int, end_str.split(':'))

        start_seconds = start_hour * 3600 + start_minute * 60
        end_seconds = end_hour * 3600 + end_minute * 60

        # Assign the same window to all other locations
        for _ in range(len(locations) -1):
            time_windows.append((start_seconds, end_seconds))
            
    except ValueError:
        # Fallback if business_hours format is wrong
        # Assign an open window to all locations
        for _ in range(len(locations) - 1):
            time_windows.append((0, 86400))
    
    return time_windows
