import json
import sys

WORKFLOW_FILE = 'workflows/asf_master_protocol_generation.json'

def add_language_to_workflow():
    try:
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {WORKFLOW_FILE} was not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {WORKFLOW_FILE}: {e}")
        return

    tasks_updated = []
    for task_name, task_data in workflow_data.get('tasks', {}).items():
        if task_data.get('action') == 'execute_code':
            if 'action_config' in task_data:
                if 'language' not in task_data['action_config']:
                    task_data['action_config']['language'] = 'python'
                    tasks_updated.append(task_name)
            else:
                task_data['action_config'] = {'language': 'python'}
                tasks_updated.append(task_name)


    if tasks_updated:
        try:
            with open(WORKFLOW_FILE, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            print(f"Successfully added language to tasks in '{WORKFLOW_FILE}': {', '.join(tasks_updated)}")
        except Exception as e:
            print(f"Error writing to {WORKFLOW_FILE}: {e}")
    else:
        print("No tasks requiring the language key were found or updated.")

def merge_spr_definitions(existing_file, new_defs_str):
    """
    Merges new SPR definitions into an existing SPR definitions file.

    - Updates existing SPRs if spr_id or name matches.
    - Appends new SPRs that don't exist.
    """
    try:
        with open(existing_file, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {"spr_definitions": []}

    try:
        new_defs = json.loads(new_defs_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding new SPR definitions JSON: {e}")
        return

    existing_defs_list = existing_data.get("spr_definitions", [])
    
    # Create a lookup map for existing definitions by spr_id and name for efficient searching
    existing_defs_map_id = {d.get('spr_id'): d for d in existing_defs_list if 'spr_id' in d}
    existing_defs_map_name = {d.get('name'): d for d in existing_defs_list if 'name' in d}

    for new_def in new_defs:
        found = False
        # Check by spr_id first
        spr_id = new_def.get('spr_id')
        if spr_id and spr_id in existing_defs_map_id:
            # Update existing entry by replacing it
            for i, existing_def in enumerate(existing_defs_list):
                if existing_def.get('spr_id') == spr_id:
                    existing_defs_list[i] = new_def
                    found = True
                    break
        
        if found:
            continue

        # If not found by spr_id, check by name
        name = new_def.get('name') or new_def.get('term')
        if name and name in existing_defs_map_name:
             for i, existing_def in enumerate(existing_defs_list):
                if existing_def.get('name') == name:
                    existing_defs_list[i] = new_def
                    found = True
                    break
        
        if found:
            continue

        # If not found by either, it's a new definition
        if not found:
            existing_defs_list.append(new_def)

    existing_data["spr_definitions"] = existing_defs_list

    # Write the merged data back to the file
    with open(existing_file, 'w') as f:
        json.dump(existing_data, f, indent=2)
    print(f"Successfully merged new definitions into {existing_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_language_key.py <path_to_existing_json_file> '<new_json_definitions_string>'")
        sys.exit(1)
    
    file_path = sys.argv[1]
    json_string = sys.argv[2]
    
    merge_spr_definitions(file_path, json_string)

    add_language_to_workflow() 