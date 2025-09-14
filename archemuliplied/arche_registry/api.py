from flask import Flask, request, jsonify
# from .registry import ArchERegistry # Old simple registry
from arche_registry.orchestrator import TaskOrchestrator
# Import the distributed registry from the top-level module present in this repo
# The original relative import expected a sibling module that is not present.
from distributed_arche_registry import DistributedArchERegistry, InstanceType

app = Flask(__name__)

# Create a single, persistent registry and orchestrator for the service
# Use the advanced, file-based DistributedArchERegistry. Default file path is internal.
registry = DistributedArchERegistry()
orchestrator = TaskOrchestrator(registry)  # Pass the registry instance

@app.route('/register', methods=['POST'])
def register():
    """Register an instance with the distributed registry (CLI-compatible).

    Accepts payloads from arche_cli like:
    {
      "instance_id": "worker-1",
      "capabilities": {"Cognitive toolS": ["Code executoR"]},
      "address": "local:9001"
    }
    """
    data = request.json or {}
    input_instance_id = data.get('instance_id') or 'Unnamed-Instance'
    caps = data.get('capabilities') or {}
    # Normalize capability names from CLI payload
    cap_names = []
    if isinstance(caps, dict):
        # Look for common key used in this codebase
        for key, val in caps.items():
            if isinstance(val, list):
                cap_names.extend([str(x) for x in val])
    elif isinstance(caps, list):
        cap_names.extend([str(x) for x in caps])
    # Build capability objects for the distributed registry
    cap_objs = [{
        "name": name,
        "level": "basic",
        "specializations": [],
        "last_validated": None,
        "success_rate": 1.0
    } for name in cap_names]

    # Register with generated internal id; map input id into metadata
    internal_id = registry.register_instance(
        instance_type=InstanceType.SPECIALIZED,
        name=input_instance_id,
        description=data.get('address', 'registered via API'),
        capabilities=cap_objs,
        max_concurrent_tasks=3,
        metadata={"external_instance_id": input_instance_id}
    )
    return jsonify({"status": "success", "instance_id": internal_id})

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

@app.route('/unregister', methods=['DELETE'])
def unregister_instance():
    data = request.json or {}
    # Accept either internal id or external name
    instance_id = data.get('instance_id') or data.get('internal_id')
    if not instance_id:
        return jsonify({"status": "error", "message": "Missing instance_id"}), 400
    if instance_id in registry.instances:
        del registry.instances[instance_id]
        registry.save_registry()
        return jsonify({"status": "success", "instance_id": instance_id})
    # Try match by name
    for iid, inst in list(registry.instances.items()):
        if getattr(inst, 'name', None) == instance_id:
            del registry.instances[iid]
            registry.save_registry()
            return jsonify({"status": "success", "instance_id": iid})
    return jsonify({"status": "error", "message": "Instance not found"}), 404

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