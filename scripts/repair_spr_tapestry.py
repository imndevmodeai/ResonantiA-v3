import json
import re

def repair_and_merge_tapestry(file_path):
    """
    Recovers a malformed spr_definitions_tv.json file by fixing its string
    representation and then performing a proper merge.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return

    # --- Step 1: Fix the broken JSON string ---
    # The core issue is a "][ " structure instead of a comma.
    # Also, the outer structure might be duplicated.
    
    # Let's find all dictionary objects using a more robust regex
    # that can handle nested brackets. This is a common advanced regex problem.
    # This regex is complex but necessary for this kind of recovery.
    json_objects = re.findall(r'(?=\{)(?:[^{}]|(?R))*\}', content)

    if not json_objects:
        print("Error: Could not find any JSON objects in the file.")
        return

    all_definitions = []
    for obj_str in json_objects:
        try:
            # We assume any top-level object is a definition
            all_definitions.append(json.loads(obj_str))
        except json.JSONDecodeError:
            # Ignore smaller, nested objects that fail to parse
            continue
            
    # --- Step 2: Perform the intelligent merge ---
    merged_defs = []
    # Use spr_id as the primary key, fall back to term or name for uniqueness
    lookup = {}

    for definition in all_definitions:
        key = definition.get('spr_id') or definition.get('term') or definition.get('name')
        if key:
            # The last definition found for a given key will overwrite previous ones.
            # This correctly prioritizes the newly supplied definitions.
            lookup[key] = definition

    merged_defs = list(lookup.values())

    # --- Step 3: Write the final, correct data structure ---
    final_data = {"spr_definitions": merged_defs}

    try:
        with open(file_path, 'w') as f:
            json.dump(final_data, f, indent=2)
        print(f"Successfully REPAIRED, merged, and overwrote {file_path}")
        print(f"Final total of SPRs in tapestry: {len(merged_defs)}")
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")


if __name__ == "__main__":
    target_file = 'knowledge_graph/spr_definitions_tv.json'
    print(f"Attempting to repair and merge {target_file}...")
    repair_and_merge_tapestry(target_file) 