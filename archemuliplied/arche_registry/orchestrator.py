import time
from typing import Dict, Any, List, Optional
from .client import ArchEClient
import json
import os

KNOWLEDGE_TAPESTRY_PATH = "knowledge_tapestry.json"

class TaskOrchestrator:
    """
    Creates, assigns, and tracks tasks for a collective of ArchE instances.
    This is the core of the Distributed Coordination Framework's execution logic.
    """

    def __init__(self, registry):
        """
        Initializes the TaskOrchestrator with a direct reference to the registry.
        """
        self.registry = registry
        self.roadmap: Dict[str, Dict[str, Any]] = {}  # Tracks all tasks for a given plan.
        self.load_knowledge_tapestry()
        print("Task Orchestrator initialized with direct registry access.")

    def load_knowledge_tapestry(self):
        """Loads the knowledge tapestry from disk if it exists."""
        if os.path.exists(KNOWLEDGE_TAPESTRY_PATH):
            with open(KNOWLEDGE_TAPESTRY_PATH, 'r') as f:
                self.knowledge_tapestry = json.load(f)
            print(f"Loaded {len(self.knowledge_tapestry)} items from Knowledge Tapestry.")
        else:
            self.knowledge_tapestry = []
            print("No existing Knowledge Tapestry found. Starting fresh.")

    def persist_knowledge(self, completed_task: Dict[str, Any]):
        """
        Persists a completed task to the knowledge tapestry.
        This is a simulation of the Insight Solidification protocol.
        """
        self.knowledge_tapestry.append(completed_task)
        with open(KNOWLEDGE_TAPESTRY_PATH, 'w') as f:
            json.dump(self.knowledge_tapestry, f, indent=2)
        print(f"Insight from task '{completed_task['task_id']}' solidified into Knowledge Tapestry.")

    def find_capable_instance(self, required_capability: str) -> Optional[Dict[str, Any]]:
        """
        Finds the first available instance that has the required capability.

        Args:
            required_capability: The specific capability needed for a task 
                                 (e.g., 'Code executoR', 'Causal inference tooL').

        Returns:
            The instance dictionary if a suitable one is found, otherwise None.
        """
        instances = self.registry.find_capable_instances([required_capability])
        print(f"Orchestrator using advanced search, found {len(instances)} instances.") # DEBUG LOG
        
        if instances:
            # The new method already returns a sorted list of suitable instances
            best_instance = instances[0] # The first one is the best match
            print(f"Found capable instance '{best_instance.name}' for capability '{required_capability}'.")
            # Convert dataclass to a minimal dict view expected downstream
            return {
                "instance_id": best_instance.instance_id,
                "name": best_instance.name,
                "capabilities": [c.name for c in best_instance.capabilities],
                "status": best_instance.status.value,
            }
        
        print(f"No instance found with capability: {required_capability}")
        return None

    def create_task(self, description: str, capability_needed: str) -> Dict[str, Any]:
        """
        Creates a structured task dictionary and adds it to the orchestrator's roadmap.
        """
        # Create a more unique task ID to avoid collisions
        task_id = f"task_{int(time.time() * 1000)}_{len(self.roadmap)}"
        task = {
            "task_id": task_id,
            "description": description,
            "required_capability": capability_needed,
            "status": "pending",
            "assigned_to": None,
            "created_at": time.time(),
            "completed_at": None,
            "result": None,
            "iar": None  # Placeholder for Integrated Action Reflection
        }
        self.roadmap[task_id] = task
        print(f"Task '{task_id}' created and added to roadmap.")
        return task

    def assign_task(self, task_id: str) -> bool:
        """
        Finds a capable instance and assigns the specified task.

        Args:
            task_id: The ID of the task to be assigned from the roadmap.

        Returns:
            True if the task was assigned successfully, False otherwise.
        """
        task = self.roadmap.get(task_id)
        if not task:
            print(f"Error: Task '{task_id}' not found in roadmap for assignment.")
            return False

        print(f"\nAttempting to assign task: '{task['description']}'")
        capable_instance = self.find_capable_instance(task['required_capability'])

        if capable_instance:
            task['assigned_to'] = capable_instance['instance_id']
            task['status'] = 'assigned'
            self.roadmap[task_id] = task  # Update the state in the roadmap
            print(f"Task '{task_id}' assigned to instance '{capable_instance['instance_id']}'.")
            # In a real system, this would involve sending the task to the instance's address.
            return True
        else:
            task['status'] = 'unassigned'
            self.roadmap[task_id] = task  # Update the state in the roadmap
            print(f"Failed to assign task '{task_id}'. No suitable instance found.")
            return False

    def report_task_completion(self, task_id: str, result: Any, iar: Dict[str, Any]) -> bool:
        """
        Receives the result and IAR for a completed task and updates the roadmap.
        This is the entry point for the meta-cognitive feedback loop.

        Args:
            task_id: The ID of the completed task.
            result: The output or product of the task.
            iar: The Integrated Action Reflection data from the executing instance.

        Returns:
            True if the task was updated, False otherwise.
        """
        if task_id in self.roadmap:
            task = self.roadmap[task_id]
            task['status'] = 'completed'
            task['completed_at'] = time.time()
            task['result'] = result
            task['iar'] = iar
            self.roadmap[task_id] = task  # Update the state
            print(f"Task '{task_id}' marked as completed by instance '{task['assigned_to']}'.")
            # This is where logic for the Knowledge Crystallization Protocol would be triggered.
            self.persist_knowledge(task)
            return True
        else:
            print(f"Error: Completed task '{task_id}' not found in roadmap.")
            return False


if __name__ == '__main__':
    # This example demonstrates the orchestrator's logic.
    # It requires the registry service to be running.
    # This section is for conceptual understanding and will not be executed directly.
    pass
    
    # --- Create a conceptual roadmap (a list of tasks) ---
    roadmap = [
        orchestrator.create_task("Analyze system implementation for bugs", "direct_file_accessX"),
        orchestrator.create_task("Model the potential impact of the bug", "Causal inference tooL"),
        orchestrator.create_task("Generate a patch for the identified bug", "Code executoR"),
        orchestrator.create_task("Predict the performance impact of the patch", "Predictive modeling tooL"),
        orchestrator.create_task("This task will fail to be assigned", "NonExistentCapability")
    ]

    print(f"\nCreated roadmap with {len(roadmap)} tasks.")

    # In a real run, we would register instances first.
    # Here, we assume the registry is populated by another process.
    # For a real test, see the test suite. 