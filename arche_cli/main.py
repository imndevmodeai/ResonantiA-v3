import click
import requests
import json
import os
import time
import random

# --- Configuration ---
PORT_FILE = "/tmp/arche_registry.port"

def get_base_url():
    """Reads the port from the temp file to construct the base URL."""
    if not os.path.exists(PORT_FILE):
        return None
    with open(PORT_FILE, 'r') as f:
        port = f.read().strip()
    return f"http://127.0.0.1:{port}"

@click.group()
def cli():
    """
    ArchE Command-Line Interface
    A tool for interacting with the ArchE distributed collective.
    """
    pass

@cli.command()
def status():
    """Check the status of the ArchE collective."""
    base_url = get_base_url()
    if not base_url:
        click.echo("Service is not running. Use 'run_service.sh start'.")
        return
        
    try:
        response = requests.get(f"{base_url}/instances")
        response.raise_for_status()
        instances = response.json()
        click.echo(f"✅ Service is running at {base_url}")
        click.echo(f"📊 Registered Instances: {len(instances)}")
        if instances:
            click.echo(json.dumps(instances, indent=2))
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Could not connect to service at {base_url}. Is it running?")
        click.echo(f"   Error: {e}")

@cli.group()
def task():
    """Manage tasks for the collective."""
    pass

@task.command(name="list")
def list_tasks():
    """List all tasks in the orchestrator's current roadmap."""
    base_url = get_base_url()
    if not base_url:
        click.echo("Service is not running.")
        return
    try:
        response = requests.get(f"{base_url}/orchestrator/roadmap")
        response.raise_for_status()
        tasks = response.json()
        click.echo(f"📋 Found {len(tasks)} tasks in the current roadmap.")
        if tasks:
            click.echo(json.dumps(tasks, indent=2))
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error listing tasks: {e}")

@task.command(name="view")
@click.argument('task_id')
def view_task(task_id):
    """View the details of a specific task."""
    base_url = get_base_url()
    if not base_url:
        click.echo("Service is not running.")
        return
    try:
        response = requests.get(f"{base_url}/orchestrator/roadmap")
        response.raise_for_status()
        tasks = response.json()
        
        task = next((t for t in tasks if t['task_id'] == task_id), None)
        
        if task:
            click.echo("🔍 Task Details:")
            click.echo(json.dumps(task, indent=2))
        else:
            click.echo(f"❌ Task with ID '{task_id}' not found.")

    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error viewing task: {e}")

@task.command(name="create")
@click.option('--desc', required=True, help="A description of the task.")
@click.option('--cap', required=True, help="The capability required for the task (e.g., 'Code executoR').")
def create_task(desc, cap):
    """Create a new task in the orchestrator's roadmap."""
    base_url = get_base_url()
    if not base_url:
        click.echo("Service is not running.")
        return

    payload = {"description": desc, "capability_needed": cap}
    try:
        response = requests.post(f"{base_url}/orchestrator/tasks", json=payload)
        response.raise_for_status()
        new_task = response.json()
        click.echo("✅ Task created successfully:")
        click.echo(json.dumps(new_task, indent=2))
        
        # Ask the user if they want to assign it now
        if click.confirm("Do you want to assign this task now?"):
            assign_response = requests.post(f"{base_url}/orchestrator/tasks/{new_task['task_id']}/assign")
            assign_response.raise_for_status()
            assigned_task = assign_response.json()
            click.echo("✅ Task assigned:")
            click.echo(json.dumps(assigned_task, indent=2))

    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error creating task: {e}")

@cli.group()
def instance():
    """Manage ArchE instances."""
    pass

@instance.command(name="register")
@click.argument('instance_id')
@click.argument('capabilities_json')
def register_instance(instance_id, capabilities_json):
    """Register a new instance with the collective."""
    base_url = get_base_url()
    if not base_url:
        click.echo("Service is not running.")
        return

    try:
        capabilities = json.loads(capabilities_json)
    except json.JSONDecodeError:
        click.echo("❌ Invalid JSON for capabilities.")
        return

    # The address is required by the API but not essential for pure CLI interaction.
    # We can provide a dummy address.
    payload = {
        "instance_id": instance_id,
        "capabilities": capabilities,
        "address": f"local:{random.randint(9000, 9999)}" # Dummy address
    }
    try:
        response = requests.post(f"{base_url}/register", json=payload)
        response.raise_for_status()
        click.echo(f"✅ Instance '{instance_id}' registered successfully.")
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error registering instance: {e}")

@instance.command(name="unregister")
@click.argument('instance_id')
def unregister_instance(instance_id):
    """Unregister an instance from the collective."""
    base_url = get_base_url()
    if not base_url:
        click.echo("Service is not running.")
        return

    payload = {"instance_id": instance_id}
    try:
        response = requests.post(f"{base_url}/unregister", json=payload)
        response.raise_for_status()
        click.echo(f"✅ Instance '{instance_id}' unregistered successfully.")
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error unregistering instance: {e}")

@task.command(name="complete")
@click.argument('instance_id')
@click.argument('task_id')
@click.argument('iar_json')
def complete_task(instance_id, task_id, iar_json):
    """Mark a task as complete and provide IAR feedback."""
    base_url = get_base_url()
    if not base_url:
        click.echo("Service is not running.")
        return

    try:
        iar_data = json.loads(iar_json)
    except json.JSONDecodeError:
        click.echo("❌ Invalid JSON for IAR data.")
        return

    payload = {
        "instance_id": instance_id,
        "result": "Completed via CLI",
        "iar": iar_data
    }
    try:
        response = requests.post(f"{base_url}/tasks/{task_id}/complete", json=payload)
        response.raise_for_status()
        click.echo(f"✅ Task '{task_id}' marked as complete by instance '{instance_id}'.")
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Error completing task: {e}")

@cli.group()
def system():
    """Commands for system-level operations like stress testing."""
    pass

@system.command(name="stress-test")
@click.option('--workers', default=5, help="Number of temporary worker instances to register.")
@click.option('--tasks', default=10, help="Number of tasks to create and assign.")
def stress_test(workers, tasks):
    """
    Performs a stress test on the collective.
    This will register temporary workers, create and assign tasks,
    simulate their completion, and then unregister the workers.
    """
    base_url = get_base_url()
    if not base_url:
        click.echo("Service is not running.")
        return

    click.echo(f"🚀 Starting Stress Test: {workers} workers, {tasks} tasks.")
    
    # --- Register Workers ---
    click.echo("\n--- Phase 1: Registering Workers ---")
    worker_clients = []
    capabilities = ["Code executoR", "Causal inference tooL", "Predictive modeling tooL", "Search tooL"]
    for i in range(workers):
        instance_id = f"stress-worker-{i+1}"
        client = ArchEClient(base_url, instance_id, f"local:{9000+i}")
        worker_clients.append(client)
        caps = {"Cognitive toolS": random.sample(capabilities, k=random.randint(1, 4))}
        client.register(caps)
    click.echo(f"{workers} workers registered.")

    # --- Create and Assign Tasks ---
    click.echo("\n--- Phase 2: Creating and Assigning Tasks ---")
    created_tasks = []
    for i in range(tasks):
        desc = f"Stress test task #{i+1}"
        cap = random.choice(capabilities)
        payload = {"description": desc, "capability_needed": cap}
        try:
            res = requests.post(f"{base_url}/orchestrator/tasks", json=payload)
            res.raise_for_status()
            new_task = res.json()
            created_tasks.append(new_task)
            
            # Immediately try to assign
            assign_res = requests.post(f"{base_url}/orchestrator/tasks/{new_task['task_id']}/assign")
            if assign_res.status_code != 200:
                click.echo(f"⚠️ Could not assign task {new_task['task_id']} for capability {cap}")

        except requests.exceptions.RequestException as e:
            click.echo(f"❌ Error during task creation/assignment: {e}")
    click.echo(f"{len(created_tasks)} tasks created and assignment attempted.")

    # --- Simulate Completion ---
    click.echo("\n--- Phase 3: Simulating Task Completion ---")
    all_tasks_res = requests.get(f"{base_url}/orchestrator/roadmap")
    all_tasks = all_tasks_res.json()
    
    assigned_tasks = [t for t in all_tasks if t['status'] == 'assigned']
    for task_to_complete in assigned_tasks:
        completion_payload = {
            "result": f"Completed result for {task_to_complete['task_id']}",
            "iar": {"confidence": round(random.uniform(0.7, 0.99), 2), "crystallization_potential": "high"}
        }
        requests.post(f"{base_url}/tasks/{task_to_complete['task_id']}/complete", json=completion_payload)
    click.echo(f"Simulated completion for {len(assigned_tasks)} assigned tasks.")
    
    # --- Cleanup ---
    click.echo("\n--- Phase 4: Cleaning Up Workers ---")
    for client in worker_clients:
        client.unregister()
    click.echo("Workers unregistered.")

    click.echo("\n✅ Stress Test Complete.")
    click.echo(f"Inspect the results with 'arche-cli task list' and 'arche-cli task view <id>'.")
    click.echo(f"Inspect the collective's growth by viewing 'knowledge_tapestry.json'.")

if __name__ == '__main__':
    cli() 