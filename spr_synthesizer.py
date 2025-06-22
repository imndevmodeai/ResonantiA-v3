import json
from typing import List, Dict, Any

def synthesize_spr_definitions(primary_file: str, secondary_file: str, output_file: str):
    """
    Intelligently merges two spr_definitions_tv.json files, preserving enhancements.
    """
    with open(primary_file, 'r', encoding='utf-8') as f:
        primary_sprs: List[Dict[str, Any]] = json.load(f)
    with open(secondary_file, 'r', encoding='utf-8') as f:
        secondary_sprs: List[Dict[str, Any]] = json.load(f)

    primary_map = {spr['spr_id']: spr for spr in primary_sprs}
    secondary_map = {spr['spr_id']: spr for spr in secondary_sprs}

    synthesized_sprs: Dict[str, Any] = {}
    all_ids = set(primary_map.keys()) | set(secondary_map.keys())

    for spr_id in sorted(list(all_ids)):
        in_primary = spr_id in primary_map
        in_secondary = spr_id in secondary_map

        if in_primary and not in_secondary:
            synthesized_sprs[spr_id] = primary_map[spr_id]
            print(f"INFO: Added unique SPR from primary: {spr_id}")
        elif not in_primary and in_secondary:
            synthesized_sprs[spr_id] = secondary_map[spr_id]
            print(f"INFO: Added unique SPR from secondary: {spr_id}")
        else: # Exists in both, potential conflict
            spr_primary = primary_map[spr_id]
            spr_secondary = secondary_map[spr_id]

            if spr_primary == spr_secondary:
                synthesized_sprs[spr_id] = spr_primary
            else:
                # Intelligent merge logic
                print(f"CONFLICT: Merging changes for {spr_id}")
                merged_spr = dict(spr_primary) # Start with primary as base
                
                # Prioritize more detailed definitions or non-empty ones
                if len(spr_secondary.get('definition', '')) > len(spr_primary.get('definition', '')):
                    merged_spr['definition'] = spr_secondary['definition']

                # Combine relationships (unique items from both)
                primary_rels = spr_primary.get('relationships', {})
                secondary_rels = spr_secondary.get('relationships', {})
                merged_rels = dict(primary_rels)
                for key, value in secondary_rels.items():
                    if key not in merged_rels:
                        merged_rels[key] = value
                    elif isinstance(value, list) and isinstance(merged_rels.get(key), list):
                        # Combine lists and remove duplicates, preserving order
                        combined = merged_rels.get(key, []) + value
                        merged_rels[key] = sorted(list(set(combined)))
                    else:
                        # For non-list values, prefer the secondary (incoming) branch's value
                        merged_rels[key] = value


                merged_spr['relationships'] = merged_rels
                synthesized_sprs[spr_id] = merged_spr

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(list(synthesized_sprs.values()), f, indent=2, ensure_ascii=False)
    print(f"\nSynthesis complete. Merged {len(synthesized_sprs)} SPRs into {output_file}")

# Usage Instructions:
# This script is designed to be run during a git merge conflict on the spr_definitions_tv.json file.
# 1. When git reports a conflict, it stores different versions of the file in its index.
#    You can extract them using the following commands from your project's root directory:
#
#    git show :2:knowledge_graph/spr_definitions_tv.json > primary_sprs.json
#    git show :3:knowledge_graph/spr_definitions_tv.json > secondary_sprs.json
#
# 2. After extracting the files, run this script to perform the intelligent merge:
#
#    python spr_synthesizer.py
#
# 3. This will create the resolved 'knowledge_graph/spr_definitions_tv.json' file.
#    You can then add it to your staging area to resolve the conflict:
#
#    git add knowledge_graph/spr_definitions_tv.json
#
# 4. Finally, you can delete the temporary files:
#
#    rm primary_sprs.json secondary_sprs.json

if __name__ == "__main__":
    # Default filenames assume you've followed the usage instructions.
    primary_file = 'primary_sprs.json'
    secondary_file = 'secondary_sprs.json'
    output_file = 'knowledge_graph/spr_definitions_tv.json'
    
    import os
    if not os.path.exists(primary_file) or not os.path.exists(secondary_file):
        print("ERROR: 'primary_sprs.json' or 'secondary_sprs.json' not found.")
        print("Please follow the usage instructions in the script's comments to extract them from the git index during a merge conflict.")
    elif not os.path.exists('knowledge_graph'):
        print("ERROR: The 'knowledge_graph' directory does not exist. Please run this script from the project root.")
    else:
        synthesize_spr_definitions(primary_file, secondary_file, output_file) 