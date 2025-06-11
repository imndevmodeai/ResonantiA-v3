from flask import Flask, request, jsonify
# from .registry import ArchERegistry # Old simple registry
from .orchestrator import TaskOrchestrator
from .distributed_arche_registry import DistributedArchERegistry, REGISTRY_FILE_PATH

app = Flask(__name__)

# Create a single, persistent registry and orchestrator for the service
# Use the advanced, file-based DistributedArchERegistry with an absolute path
registry = DistributedArchERegistry(registry_file=REGISTRY_FILE_PATH)
orchestrator = TaskOrchestrator(registry) # Pass the registry instance

@app.route('/register', methods=['POST'])
def register():
    # This endpoint is now conceptually DEPRECATED in favor of the python script.
    return jsonify({
        "status": "error",
        "message": "This registration endpoint is deprecated. Please register instances using the 'distributed_arche_registry.py' script for full capability mapping."
    }), 501

@app.route('/instances', methods=['GET'])
def list_instances():
    # Return instances from the new registry, converting them to dicts
    instances = [instance.to_dict() for instance in registry.instances.values()]
    return jsonify(instances)

@app.route('/instance/<string:instance_id>', methods=['GET'])
def get_instance(instance_id):
    instance = registry.instances.get(instance_id)
    if instance:
        return jsonify(instance.to_dict())
    else:
        return jsonify({"status": "error", "message": "Instance not found"}), 404

@app.route('/unregister', methods=['POST'])
def unregister_instance():
    # This function does not exist in the new registry, returning error
    return jsonify({
        "status": "error", 
        "message": "Unregister instances using 'distributed_arche_registry.py' script."
        }), 501

@app.route('/reset', methods=['POST'])
def reset_registry():
    """
    Clears all instances from the registry AND resets the orchestrator's roadmap.
    For testing/internal use.
    """
    orchestrator.roadmap.clear() # Clear the orchestrator's state
    result = registry.clear()
    return jsonify(result)

# --- Orchestrator Endpoints ---

@app.route('/orchestrator/roadmap', methods=['GET'])
def get_roadmap():
    """
    Returns the current state of all tasks in the orchestrator's roadmap.
    """
    return jsonify(list(orchestrator.roadmap.values()))

@app.route('/orchestrator/tasks', methods=['POST'])
def create_task():
    """
    Creates a new task in the orchestrator's roadmap.
    """
    data = request.json
    if not data or 'description' not in data or 'capability_needed' not in data:
        return jsonify({"status": "error", "message": "Invalid task creation data"}), 400
    
    task = orchestrator.create_task(
        description=data['description'],
        capability_needed=data['capability_needed']
    )
    return jsonify(task)

@app.route('/orchestrator/tasks/<string:task_id>/assign', methods=['POST'])
def assign_task(task_id):
    """
    Triggers the orchestrator to assign a specific task.
    """
    success = orchestrator.assign_task(task_id)
    task_state = orchestrator.roadmap.get(task_id, {})
    if success:
        return jsonify(task_state)
    else:
        return jsonify(task_state), 404 # Not found or other assignment error

@app.route('/tasks/<string:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """
    Called by an ArchE instance to report the completion of a task.
    This is the entry point for the IAR feedback loop.
    """
    data = request.json
    if not data or 'result' not in data or 'iar' not in data:
        return jsonify({"status": "error", "message": "Invalid task completion data"}), 400

    success = orchestrator.report_task_completion(
        task_id=task_id,
        result=data['result'],
        iar=data['iar']
    )
    
    if success:
        return jsonify({"status": "success", "task_id": task_id})
    else:
        return jsonify({"status": "error", "message": "Task not found or failed to update"}), 404

def run_registry_service(host='0.0.0.0', port=5000):
    """Starts the ArchE Registry API service."""
    print(f"Starting ArchE Registry service on {host}:{port}")
    app.run(host=host, port=port)

if __name__ == '__main__':
    run_registry_service() 