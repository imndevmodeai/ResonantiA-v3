#!/usr/bin/env python3
"""
Nexus Server (nexus_server.py)
A simple web server to provide a UI for interacting with ArchE.

This server provides two main functions:
1. Serves the static `index.html` page for the user interface.
2. Exposes a `/api/query` endpoint that accepts POST requests and routes
   them to the CognitiveIntegrationHub.
"""

import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# Ensure the project root is in the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from Three_PointO_ArchE.cognitive_integration_hub import CognitiveIntegrationHub
    from Three_PointO_ArchE.system_health_monitor import SystemHealthMonitor
    from Three_PointO_ArchE.thought_trail import thought_trail
    from Three_PointO_ArchE.autopoietic_learning_loop import AutopoieticLearningLoop
except ImportError as e:
    print(f"FATAL: Could not import ArchE modules. Ensure you are in the project root.")
    print(f"Error: {e}")
    sys.exit(1)

# Initialize Flask App and the Cognitive Hub
app = Flask(__name__)
print("Initializing core components for Nexus Server...")
hub = CognitiveIntegrationHub()
health_monitor = SystemHealthMonitor()
learning_loop = AutopoieticLearningLoop(guardian_review_enabled=True) # To access guardian queue
print("   ✓ All components initialized.")

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def handle_query():
    """Handles query submissions from the UI."""
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({"error": "Query cannot be empty."}), 400

    try:
        # The core of the integration: call the hub
        response = hub.route_query(query)

        # Return the response in a JSON format for the frontend
        return jsonify({
            "content": response.content,
            "source": response.source,
            "confidence": response.confidence
        })
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def get_health():
    """Returns system health metrics."""
    try:
        # In a real system, you'd call a method on the monitor.
        # Here we'll simulate fetching its dashboard data.
        dashboard_data = health_monitor.generate_dashboard()
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({"error": f"An error occurred fetching health data: {str(e)}"}), 500

@app.route('/api/thoughttrail', methods=['GET'])
def get_thoughttrail():
    """Returns the most recent ThoughtTrail entries."""
    try:
        # Access the global thought_trail instance and get recent entries
        entries = thought_trail.get_recent_entries(minutes=10) # Last 10 minutes
        # Convert dataclass objects to dicts for JSON serialization
        entries_as_dicts = [entry.__dict__ for entry in reversed(entries[-10:])] # Last 10 entries, newest first
        return jsonify(entries_as_dicts)
    except Exception as e:
        return jsonify({"error": f"An error occurred fetching ThoughtTrail data: {str(e)}"}), 500

@app.route('/api/guardian_queue', methods=['GET'])
def get_guardian_queue():
    """Returns items awaiting Guardian approval."""
    try:
        # The learning loop is already initialized
        queue_items = learning_loop.get_guardian_queue()
        return jsonify(queue_items)
    except Exception as e:
        return jsonify({"error": f"An error occurred fetching Guardian Queue data: {str(e)}"}), 500

def main():
    """Runs the Flask development server."""
    print("
    ..:: ArchE Nexus Dashboard Server ::..
    ")
    print("----------------------------------------------------")
    print("Starting the web server...")
    print("Navigate to http://127.0.0.1:5000 in your web browser.")
    print("----------------------------------------------------")
    app.run(port=5000, debug=True)

if __name__ == '__main__':
    main()
