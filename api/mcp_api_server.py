from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

# --- Configuration ---
# Assuming the script is in the 'api' directory, and the project root is one level up.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REGISTRY_PATH = os.path.join(PROJECT_ROOT, 'arche_registry.json')
SPR_PATH = os.path.join(PROJECT_ROOT, 'knowledge_graph', 'spr_definitions_tv.json')

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for the Next.js app

def get_live_data():
    """
    Gathers live data from the ArchE system's source files.
    This function replaces the mock data structure.
    """
    
    # --- 1. Fetch Registered Instances ---
    instances_data = []
    try:
        with open(REGISTRY_PATH, 'r') as f:
            registry = json.load(f)
            for inst_id, inst_details in registry.get('instances', {}).items():
                # Simulate status based on last heartbeat (e.g., active in the last 5 minutes)
                last_active_dt = datetime.fromisoformat(inst_details.get('last_active'))
                is_online = (datetime.utcnow() - last_active_dt).total_seconds() < 300
                
                instances_data.append({
                    'id': inst_id,
                    'name': inst_details.get('name', 'Unnamed Worker'),
                    'status': 'online' if is_online else 'offline',
                    'capabilities': inst_details.get('capabilities', {}).get('Cognitive toolS', []),
                    'last_active': inst_details.get('last_active')
                })
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is invalid, return an empty list
        pass

    # --- 2. Fetch Orchestrator Roadmap ---
    roadmap_data = []
    try:
        with open(REGISTRY_PATH, 'r') as f:
             registry = json.load(f)
             roadmap_data = registry.get('roadmap', [])
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # --- 3. Fetch Knowledge Graph Stats ---
    kg_data = {'spr_count': 0, 'recent_additions': []}
    try:
        with open(SPR_PATH, 'r') as f:
            sprs = json.load(f)
            kg_data['spr_count'] = len(sprs.get('spr_definitions', []))
            # Get the 3 most recently created SPRs
            sorted_sprs = sorted(
                sprs.get('spr_definitions', []), 
                key=lambda x: x.get('metadata', {}).get('created_at', ''), 
                reverse=True
            )
            for spr in sorted_sprs[:3]:
                 kg_data['recent_additions'].append({
                     'id': spr.get('spr_id'),
                     'concept': spr.get('concept_name'),
                     'created_at': spr.get('metadata', {}).get('created_at')
                 })

    except (FileNotFoundError, json.JSONDecodeError):
        pass

    return {
        'instances': instances_data,
        'roadmap': roadmap_data,
        'knowledge_graph': kg_data
    }

@app.route('/api/mcp', methods=['GET'])
def get_mcp_data():
    """
    API endpoint to serve the live MCP data.
    """
    live_data = get_live_data()
    return jsonify(live_data)

if __name__ == '__main__':
    # Runs the Flask server on port 5001
    app.run(debug=True, port=5001)

