import re
import logging

logger = logging.getLogger(__name__)

def tsplib_to_abm_data(filepath: str) -> dict:
    """
    Parses a TSPLIB .tsp file and extracts city coordinates.
    Converts them into a dictionary format suitable for ABM or other tools.

    Expected format for ABM data:
    {
        'name': 'instance_name',
        'dimension': 51,
        'cities': [
            {'id': 1, 'x': 37.0, 'y': 52.0},
            {'id': 2, 'x': 49.0, 'y': 49.0},
            ...
        ],
        'edge_weight_type': 'EUC_2D' # or other types
    }
    """
    data = {
        'name': None,
        'type': None,
        'comment': None,
        'dimension': None,
        'edge_weight_type': None,
        'cities': []
    }
    in_node_coord_section = False

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("COMMENT"):
                    if data['comment'] is None and line.startswith("COMMENT"):
                        data['comment'] = line.split(":", 1)[1].strip() if ":" in line else line
                    elif data['comment'] is not None and line.startswith("COMMENT"):
                         data['comment'] += "\\n" + (line.split(":", 1)[1].strip() if ":" in line else line)
                    continue

                if "EOF" in line:
                    break
                if "NODE_COORD_SECTION" in line:
                    in_node_coord_section = True
                    continue
                
                if in_node_coord_section:
                    parts = re.split(r'\\s+', line)
                    if len(parts) >= 3:
                        try:
                            node_id = int(parts[0])
                            x = float(parts[1])
                            y = float(parts[2])
                            data['cities'].append({'id': node_id, 'x': x, 'y': y})
                        except ValueError:
                            logger.warning(f"Could not parse node coordinate line: {line}")
                    else:
                        logger.warning(f"Node coordinate line has too few parts: {line}")
                else:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if key == 'name':
                            data['name'] = value
                        elif key == 'type':
                            data['type'] = value
                        elif key == 'dimension':
                            try:
                                data['dimension'] = int(value)
                            except ValueError:
                                logger.error(f"Could not parse DIMENSION: {value}")
                        elif key == 'edge_weight_type':
                            data['edge_weight_type'] = value
                        # Add other TSPLIB keywords as needed
            
        if not data['cities'] and data['dimension'] is not None:
            logger.warning(f"No NODE_COORD_SECTION found or parsed in {filepath}, but dimension was {data['dimension']}.")
        elif data['dimension'] is not None and len(data['cities']) != data['dimension']:
            logger.warning(f"Mismatch between DIMENSION ({data['dimension']}) and number of cities parsed ({len(data['cities'])}) in {filepath}.")
            # Fallback: update dimension if cities were parsed but dimension was not, or vice-versa if dimension makes more sense
            if not data['cities'] and data['dimension']:
                 pass # Dimension from file is likely correct if no coords found
            elif data['cities'] and not data['dimension']:
                 data['dimension'] = len(data['cities'])


    except FileNotFoundError:
        logger.error(f"TSPLIB file not found: {filepath}")
        return {'error': f"File not found: {filepath}", 'cities': []}
    except Exception as e:
        logger.error(f"Error parsing TSPLIB file {filepath}: {e}", exc_info=True)
        return {'error': f"Error parsing file: {e}", 'cities': []}

    if data['dimension'] is None and data['cities']: # If dimension wasn't in file, set it from parsed cities
        data['dimension'] = len(data['cities'])

    logger.info(f"Successfully parsed {len(data['cities'])} cities from {data.get('name', filepath)}.")
    return data

if __name__ == '__main__':
    # Example usage:
    # Create a dummy test.tsp file for basic testing
    dummy_tsp_content = """NAME : dummy_example
TYPE : TSP
COMMENT : A small dummy example for testing
DIMENSION : 3
EDGE_WEIGHT_TYPE : EUC_2D
NODE_COORD_SECTION
1 10.0 10.0
2 20.0 20.0
3 10.0 30.0
EOF
"""
    dummy_filepath = "dummy_test.tsp"
    with open(dummy_filepath, 'w') as f:
        f.write(dummy_tsp_content)

    parsed_data = tsplib_to_abm_data(dummy_filepath)
    print("Parsed Data:")
    import json
    print(json.dumps(parsed_data, indent=2))

    if parsed_data and not parsed_data.get('error'):
        assert parsed_data['name'] == 'dummy_example'
        assert parsed_data['dimension'] == 3
        assert len(parsed_data['cities']) == 3
        assert parsed_data['cities'][0] == {'id': 1, 'x': 10.0, 'y': 10.0}
        print("\\nDummy test passed.")
    else:
        print("\\nDummy test failed or error in parsing.")
    
    # Clean up dummy file
    import os
    os.remove(dummy_filepath) 