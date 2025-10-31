import json
import re

def integrate_sprs(artifacts_file, main_spr_file):
    """
    Integrates SPR definitions from a markdown file into the main SPR JSON file.

    It extracts JSON blocks from the markdown, identifies SPR definitions,
    and then adds them to the main definitions file, updating any existing
    SPRs with the same spr_id.
    """
    try:
        with open(artifacts_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"Error: Artifacts file not found at {artifacts_file}")
        return

    # Find all json blocks
    json_blocks_str = re.findall(r"```json\n(.*?)\n```", md_content, re.DOTALL)
    
    new_sprs = []
    for block_str in json_blocks_str:
        try:
            data = json.loads(block_str)
            # Check if it's an SPR definition
            if isinstance(data, dict) and 'spr_id' in data:
                new_sprs.append(data)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode a JSON block in {artifacts_file}.")
            continue

    if not new_sprs:
        print(f"No valid SPR definitions found in {artifacts_file}.")
        return

    print(f"Found {len(new_sprs)} SPRs to integrate from {artifacts_file}.")

    try:
        with open(main_spr_file, 'r', encoding='utf-8') as f:
            main_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Warning: Could not read or decode {main_spr_file}. Starting with a new structure.")
        main_data = {}
    
    # Ensure 'spr_definitions' key exists and is a list
    if 'spr_definitions' not in main_data or not isinstance(main_data['spr_definitions'], list):
        main_data['spr_definitions'] = []

    # Create a dictionary for quick lookup of existing SPRs by spr_id
    existing_sprs_map = {spr.get('spr_id'): index for index, spr in enumerate(main_data['spr_definitions']) if isinstance(spr, dict) and 'spr_id' in spr}

    added_count = 0
    updated_count = 0

    for spr_to_add in new_sprs:
        spr_id = spr_to_add.get('spr_id')
        if not spr_id:
            continue

        if spr_id in existing_sprs_map:
            # Update existing entry
            index = existing_sprs_map[spr_id]
            main_data['spr_definitions'][index] = spr_to_add
            updated_count += 1
        else:
            # Add new entry
            main_data['spr_definitions'].append(spr_to_add)
            added_count += 1

    try:
        with open(main_spr_file, 'w', encoding='utf-8') as f:
            json.dump(main_data, f, indent=2)
            f.write('\n') # Add trailing newline for POSIX compliance
    except IOError as e:
        print(f"Error writing to {main_spr_file}: {e}")
        return

    print(f"Integration complete for {main_spr_file}.")
    print(f" - Added: {added_count} SPR(s)")
    print(f" - Updated: {updated_count} SPR(s)")


if __name__ == "__main__":
    # This allows the script to be run directly for this specific task
    integrate_sprs('CRYSTALLIZED_ARTIFACTS_OUTPUT.md', 'knowledge_graph/spr_definitions_tv.json') 