# --- vcd_api/main.py ---
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from pathlib import Path
from collections import OrderedDict, deque

app = Flask(__name__)
CORS(app)

PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIRECTORY = PROJECT_ROOT / "outputs"

def parse_log_file(filepath: Path) -> OrderedDict:
    """Parses a .jsonl log file into an ordered dictionary of tasks, keyed by task_key."""
    tasks = OrderedDict()
    with open(filepath, 'r') as f:
        for line in f:
            try:
                task_data = json.loads(line)
                tasks[task_data['task_key']] = task_data
            except (json.JSONDecodeError, KeyError):
                print(f"Warning: Could not parse line in {filepath}: {line.strip()}")
    return tasks

def generate_intelligent_stage_name(tasks_in_stage: list, stage_level: int) -> str:
    """Generates a more descriptive name for a stage based on its tasks."""
    if not tasks_in_stage:
        return f"Stage {stage_level}: Empty"

    task_keys = [task['task_key'] for task in tasks_in_stage]
    
    # Heuristic 1: Common Prefixes
    common_prefix = os.path.commonprefix(task_keys).replace('_', ' ').strip()
    if len(common_prefix) > 4:
        # Capitalize and return
        return f"Phase {stage_level}: {common_prefix.title()}"

    # Heuristic 2: Action Types
    action_types = sorted(list(set([t['action_type'] for t in tasks_in_stage])))
    if len(action_types) == 1:
        name = action_types[0].replace('_', ' ').title()
    else:
        name = " & ".join([t.replace('_', ' ').title() for t in action_types])
    
    return f"Phase {stage_level}: {name}"


def synthesize_run_data_dynamically(tasks: OrderedDict) -> dict:
    """
    Transforms a flat dict of tasks into a hierarchical structure of stages by analyzing dependencies.
    This is the core of the DYNAMIC Synthesis Layer.
    """
    if not tasks:
        return {"run_id": "Unknown", "workflow_name": "Unknown", "overall_status": "Failure", "stages": []}

    graph = {key: [] for key in tasks}
    in_degree = {key: 0 for key in tasks}
    
    for task_key, task_data in tasks.items():
        deps = task_data.get('dependencies', [])
        if deps:
            for dep in deps:
                if dep in graph:
                    graph[dep].append(task_key)
                    in_degree[task_key] += 1

    queue = deque([key for key, degree in in_degree.items() if degree == 0])
    stages_list = []
    stage_level = 1
    processed_tasks_count = 0
    
    while queue:
        stage_task_keys = sorted(list(queue))
        queue.clear()
        
        current_stage_tasks = [tasks[key] for key in stage_task_keys]
        processed_tasks_count += len(current_stage_tasks)
        
        for task_key in stage_task_keys:
            for neighbor in sorted(graph[task_key]):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        stage_statuses = [task.get("result", {}).get("status", "Success") for task in current_stage_tasks]
        stage_status = "Success"
        if "Failure" in stage_statuses: stage_status = "Failure"
        elif any(s == "Skipped" for s in stage_statuses): stage_status = "Skipped"
        
        stage_name = generate_intelligent_stage_name(current_stage_tasks, stage_level)

        stages_list.append({
            "stage_name": stage_name,
            "tasks": current_stage_tasks,
            "status": stage_status
        })
        stage_level += 1

    if processed_tasks_count != len(tasks):
        unprocessed = [tasks[key] for key, val in in_degree.items() if val > 0]
        stages_list.append({
            "stage_name": "Error: Cycle Detected or Missing Dependencies",
            "tasks": unprocessed, "status": "Failure"})

    overall_status = "Success"
    if any(s['status'] == 'Failure' for s in stages_list): overall_status = "Failure"
        
    return {
        "run_id": list(tasks.values())[0].get('run_id', 'Unknown'),
        "workflow_name": list(tasks.values())[0].get('workflow_name', 'Unknown'),
        "overall_status": overall_status,
        "stages": stages_list
    }

# --- API Endpoints ---
@app.route('/api/runs', methods=['GET'])
def get_all_runs():
    runs = []
    if not LOG_DIRECTORY.exists(): return jsonify({"error": "Log directory not found"}), 404

    # First, gather all runs from the directory
    for filename in os.listdir(LOG_DIRECTORY):
        if filename.startswith('run_events_run_') and filename.endswith('.jsonl'):
            run_id = filename.replace('run_events_run_', '').replace('.jsonl', '')
            try:
                with open(LOG_DIRECTORY / filename, 'r') as f:
                    first_line = f.readline()
                    log_data = json.loads(first_line)
                    workflow_name = log_data.get('workflow_name', 'Unnamed Workflow')
                    timestamp = log_data.get('timestamp', '1970-01-01T00:00:00.000000') # Default for sorting
            except Exception:
                workflow_name, timestamp = 'Unknown Workflow', '1970-01-01T00:00:00.000000'
            runs.append({"run_id": run_id, "workflow_name": workflow_name, "timestamp": timestamp})
    
    # Second, apply sorting based on query parameters
    sort_by = request.args.get('sortBy', 'timestamp')
    order = request.args.get('order', 'desc')
    
    reverse = (order == 'desc')
    
    # Ensure the key exists to avoid errors
    valid_sort_keys = ['timestamp', 'workflow_name', 'run_id']
    if sort_by not in valid_sort_keys:
        sort_by = 'timestamp'
        
    runs.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse)

    return jsonify(runs)

@app.route('/api/run/<run_id>', methods=['GET'])
def get_run_details(run_id: str):
    log_file = LOG_DIRECTORY / f"run_events_run_{run_id}.jsonl"
    if not log_file.exists(): return jsonify({"error": "Run ID not found"}), 404

    try:
        tasks = parse_log_file(log_file)
        synthesized_data = synthesize_run_data_dynamically(tasks)
        return jsonify(synthesized_data)
    except Exception as e:
        app.logger.error(f"Failed to synthesize log file for run {run_id}: {e}", exc_info=True)
        return jsonify({"error": f"Failed to synthesize log file: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
