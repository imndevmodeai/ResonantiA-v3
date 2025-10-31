import json
import os
import networkx as nx
from networkx.readwrite import json_graph

def find_spr_files(root_dir):
    """Finds all SPR definition JSON files in the project."""
    spr_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.startswith('spr_definitions') and file.endswith('.json'):
                spr_files.append(os.path.join(root, file))
    return spr_files

def load_sprs(file_path):
    """Loads SPRs from a JSON file, handling different structures."""
    with open(file_path, 'r') as f:
        data = json.load(f)
        if isinstance(data, dict) and "spr_definitions" in data:
            return data["spr_definitions"]
        elif isinstance(data, list):
            return data
        else:
            print(f"Warning: Could not parse SPRs from {file_path}. Unexpected format.")
            return []

def build_spr_graph(spr_list):
    """Builds a NetworkX graph from a list of SPRs."""
    G = nx.DiGraph()
    spr_map = {spr['spr_id']: spr for spr in spr_list}

    for spr_id, spr_data in spr_map.items():
        G.add_node(spr_id, **spr_data)

    for spr_id, spr_data in spr_map.items():
        if 'relationships' in spr_data and spr_data['relationships']:
            for rel_type, rel_targets in spr_data['relationships'].items():
                if not isinstance(rel_targets, list):
                    rel_targets = [rel_targets]
                for target in rel_targets:
                    if target in spr_map:
                        G.add_edge(spr_id, target, type=rel_type)
                    else:
                        print(f"Warning: Dangling edge from '{spr_id}' to non-existent SPR '{target}'")
    return G

def main():
    """
    Main function to generate the SPR network graph.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print(f"Project Root: {project_root}")

    print("--- Finding SPR definition files...")
    spr_files = find_spr_files(project_root)
    if not spr_files:
        print("FATAL: No SPR definition files found. Cannot generate graph.")
        return
    print(f"Found files: {spr_files}")

    print("\n--- Loading and consolidating all SPRs...")
    all_sprs = {}
    for f in spr_files:
        sprs_from_file = load_sprs(f)
        for spr in sprs_from_file:
            if 'spr_id' in spr:
                if spr['spr_id'] not in all_sprs:
                    all_sprs[spr['spr_id']] = spr
                else:
                    print(f"Info: Duplicate SPR '{spr['spr_id']}' found. Keeping first encountered version.")
            else:
                print(f"Warning: Found an entry without 'spr_id' in {f}")

    consolidated_sprs = list(all_sprs.values())
    print(f"Total unique SPRs consolidated: {len(consolidated_sprs)}")

    print("\n--- Building SPR Network Graph...")
    spr_graph = build_spr_graph(consolidated_sprs)
    print(f"Graph created with {spr_graph.number_of_nodes()} nodes and {spr_graph.number_of_edges()} edges.")

    # Add the primer URL as a graph-level attribute
    primer_url = "https://bit.ly/Summers_eyeS"
    spr_graph.graph['primer_url'] = primer_url
    print(f"Added graph-level attribute 'primer_url': {primer_url}")

    output_path = os.path.join(project_root, 'SPR_Network_Graph.json')
    print(f"\n--- Writing graph to {output_path}...")
    
    graph_data = json_graph.node_link_data(spr_graph)

    # Create a final dictionary to ensure all data is preserved
    final_output = {
        "primer_url": primer_url,
        "graph_data": graph_data
    }
    
    with open(output_path, 'w') as f:
        json.dump(final_output, f, indent=4)

    print("\n--- SPR Network Graph generation complete. ---")
    print("The file 'SPR_Network_Graph.json' has been created in the project root.")

if __name__ == "__main__":
    main() 