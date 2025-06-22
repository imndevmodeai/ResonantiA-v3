import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
from correction_handler import CorrectionHandler
from knowledge_crystallization_system import KnowledgeCrystallizationSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Task:
    task_id: str
    description: str
    required_capability: str
    status: str
    assigned_to: Optional[str]
    created_at: float
    completed_at: Optional[float]
    result: Optional[str]
    iar: Optional[Dict[str, str]]  # Insight, Action, Reflection
    parameters: Dict[str, Any]
    dependencies: List[str]
    retry_count: int = 0
    max_retries: int = 3

class WorkflowManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.capabilities: Dict[str, Any] = {}
        self.correction_handler = CorrectionHandler()
        self.knowledge_system = KnowledgeCrystallizationSystem()
        
    def register_capability(self, name: str, handler: Any):
        """Register a capability handler for task execution"""
        self.capabilities[name] = handler
        logger.info(f"Registered capability: {name}")
        
    def create_task(self, description: str, required_capability: str, 
                   parameters: Dict[str, Any], dependencies: List[str] = None) -> Task:
        """Create a new task with unique ID and timestamp"""
        task_id = f"task_{int(time.time() * 1000)}_{uuid.uuid4().hex[:4]}"
        task = Task(
            task_id=task_id,
            description=description,
            required_capability=required_capability,
            status="pending",
            assigned_to=None,
            created_at=time.time(),
            completed_at=None,
            result=None,
            iar=None,
            parameters=parameters,
            dependencies=dependencies or []
        )
        self.tasks[task_id] = task
        logger.info(f"Created task: {task_id}")
        return task
    
    def execute_task(self, task_id: str) -> bool:
        """Execute a task using its registered capability handler"""
        task = self.tasks.get(task_id)
        if not task:
            logger.error(f"Task not found: {task_id}")
            return False
            
        if task.required_capability not in self.capabilities:
            logger.error(f"Capability not found: {task.required_capability}")
            return False
            
        try:
            # --- Knowledge System Integration ---
            # Find applicable patterns before execution
            problem_description = f"{task.description} which requires {task.required_capability}"
            applicable_patterns = self.knowledge_system.find_applicable_patterns(problem_description)
            if applicable_patterns:
                top_pattern = applicable_patterns[0]
                logger.info(f"Found applicable knowledge pattern: '{top_pattern.name}' (Success Rate: {top_pattern.success_rate:.2%})")
                # In a full implementation, these patterns would modify the execution strategy or parameters.
                # For now, we will just log the finding.

            # Check dependencies
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != "completed":
                    logger.error(f"Dependency not met: {dep_id}")
                    return False
            
            # Execute task
            handler = self.capabilities[task.required_capability]
            result = handler(**task.parameters)
            
            # Update task status
            task.status = "completed"
            task.completed_at = time.time()
            task.result = str(result)
            
            # Generate IAR (Insight, Action, Reflection)
            task.iar = {
                "insight": "Task completed successfully",
                "action": "No immediate action required",
                "reflection": "Task execution met expectations"
            }
            
            # --- Knowledge System Integration ---
            # Upon success, this could potentially be captured as an insight.
            # For now, we will just log the successful application of any found patterns.
            if applicable_patterns:
                self.knowledge_system.apply_pattern(applicable_patterns[0].pattern_id, "workflow_manager_instance", success=True)
                logger.info(f"Successfully applied pattern '{applicable_patterns[0].name}' to task {task.task_id}")

            logger.info(f"Task completed: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Task failed: {task_id}, Error: {str(e)}")
            task.status = "failed"
            # --- Knowledge System Integration ---
            # Log pattern application failure
            if applicable_patterns:
                self.knowledge_system.apply_pattern(applicable_patterns[0].pattern_id, "workflow_manager_instance", success=False)
                logger.info(f"Failed application of pattern '{applicable_patterns[0].name}' to task {task.task_id}")
            self._handle_task_failure(task, str(e))
            return False
    
    def _handle_task_failure(self, task: Task, error_message: str):
        """Handle task failure and initiate correction process"""
        if task.retry_count >= task.max_retries:
            logger.error(f"Task {task.task_id} exceeded max retries")
            return
        # Prepare failure context for correction
        failure_context = {
            "failure_context": {
                "task_id": task.task_id,
                "description": task.description,
                "required_capability": task.required_capability,
                "status": "failed",
                "error_type": "execution_error",
                "error_message": error_message,
                "context": {
                    "parameters": task.parameters,
                    "retry_count": task.retry_count,
                    "dependencies": task.dependencies
                }
            }
        }
        # Generate correction plan
        correction_plan = self.correction_handler.generate_correction_plan(
            failure_context,
            f"Task was initiated to {task.description}"
        )
        if correction_plan:
            # Apply correction to parameters
            original_parameters = task.parameters.copy()
            updated_parameters = self.correction_handler.apply_correction(
                task.parameters,
                correction_plan
            )
            # Update task with correction
            task.retry_count += 1
            task.parameters = updated_parameters
            task.status = "pending"
            logger.info(f"Applied correction to task: {task.task_id}")
            logger.info(f"Updated parameters: {json.dumps(updated_parameters, indent=2)}")
            # Automatically re-execute the task if retries remain
            if task.retry_count < task.max_retries:
                logger.info(f"Automatically retrying task: {task.task_id} (retry {task.retry_count})")
                
                # We need to capture the result of the retry attempt
                retry_successful = self.execute_task(task.task_id)

                # --- Knowledge System Integration: Capture Learning ---
                if retry_successful:
                    problem_desc = f"Task '{task.description}' failed with error: {error_message}"
                    solution_desc = f"Applied correction plan. Original params: {original_parameters}. Corrected params: {updated_parameters}."
                    
                    self.knowledge_system.capture_insight(
                        title=f"Correction for: {task.description}",
                        category="DEBUGGING_PATTERNS",
                        problem_pattern=problem_desc,
                        solution_pattern=solution_desc,
                        validation_evidence=[f"Correction successful on retry for task {task.task_id}"],
                        applicability=[task.required_capability],
                        source_instance="workflow_manager_instance"
                    )
                    logger.info(f"Captured new knowledge insight from successful correction of task {task.task_id}.")

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get detailed status of a task"""
        task = self.tasks.get(task_id)
        if task:
            return asdict(task)
        return None
    
    def get_workflow_status(self) -> Dict:
        """Get overall workflow status"""
        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == "completed"]),
            "failed_tasks": len([t for t in self.tasks.values() if t.status == "failed"]),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == "pending"]),
            "corrections_applied": len(self.correction_handler.get_correction_history())
        }

    def execute_json_workflow(self, workflow_path: str, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Loads and executes a declarative JSON workflow file.
        This method adapts the declarative, step-based workflow into the manager's dynamic, task-based system.
        """
        logger.info(f"Executing JSON workflow from: {workflow_path}")
        try:
            with open(workflow_path, 'r') as f:
                workflow_def = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load or parse JSON workflow: {e}")
            return {"status": "FAILED", "error": f"Failed to load or parse JSON workflow: {e}"}

        workflow_tasks = workflow_def.get("tasks", {})
        if not workflow_tasks:
            logger.error("No 'tasks' found in the JSON workflow definition.")
            return {"status": "FAILED", "error": "No 'tasks' found in JSON definition."}

        # Create all tasks first
        task_map = {} # Maps step_id from JSON to our internal task_id
        for step_id, task_def in workflow_tasks.items():
            dependencies = task_def.get("dependencies", [])
            # We will map these step_id dependencies to internal task_ids later
            
            task = self.create_task(
                description=task_def.get("description", "No description"),
                required_capability=task_def.get("action_type", "default_action"),
                parameters=task_def.get("inputs", {}),
                dependencies=dependencies # Keep original dependency names for now
            )
            task_map[step_id] = task.task_id

        # Now update dependencies to use internal task_ids
        for step_id, internal_task_id in task_map.items():
            task = self.tasks[internal_task_id]
            task.dependencies = [task_map[dep_id] for dep_id in task.dependencies]

        # Execute tasks in an order that respects dependencies
        executed_tasks = set()
        while len(executed_tasks) < len(workflow_tasks):
            tasks_to_run = [
                task for task in self.tasks.values() 
                if task.task_id in task_map.values() and 
                   task.task_id not in executed_tasks and
                   all(dep_id in executed_tasks for dep_id in task.dependencies)
            ]
            
            if not tasks_to_run:
                logger.error("Could not determine next task to run. Check for circular dependencies.")
                return {"status": "FAILED", "error": "Circular dependency or unresolved dependency in workflow."}

            for task in tasks_to_run:
                self.execute_task(task.task_id)
                executed_tasks.add(task.task_id)
        
        logger.info(f"JSON workflow '{workflow_def.get('name', 'Untitled')}' completed.")
        return self.get_workflow_status()

# Example usage
if __name__ == "__main__":
    # Create workflow manager
    wf = WorkflowManager()
    
    # Register a sample capability with more sophisticated failure handling
    def data_analysis(**kwargs):
        data_points = kwargs.get("data_points", 0)
        minimum_required = kwargs.get("minimum_required", 100)
        timeframe = kwargs.get("timeframe", "last_24_hours")
        
        # Simulate different failure scenarios based on parameters
        if data_points < minimum_required:
            raise ValueError(f"Insufficient data points: {data_points} < {minimum_required}")
        if timeframe == "last_24_hours" and data_points < 50:
            raise ValueError("24-hour window requires at least 50 data points")
        if timeframe == "last_7_days" and data_points < 200:
            raise ValueError("7-day window requires at least 200 data points")
            
        return f"Analysis completed successfully with {data_points} points over {timeframe}"
    
    wf.register_capability("data_analysis", data_analysis)
    
    print("\n=== Starting Workflow Demo ===")
    print("Creating task with initial parameters that will trigger multiple corrections...")
    
    # Create and execute a task with parameters that will need multiple corrections
    task = wf.create_task(
        description="Analyze user sentiment from logs",
        required_capability="data_analysis",
        parameters={
            "data_points": 12,
            "minimum_required": 100,
            "timeframe": "last_24_hours"
        }
    )
    
    print(f"\nInitial task created with ID: {task.task_id}")
    print("Initial parameters:", json.dumps(task.parameters, indent=2))
    
    # Execute task (this will fail and trigger multiple corrections)
    print("\nExecuting task...")
    wf.execute_task(task.task_id)
    
    # Print final workflow status
    print("\n=== Final Workflow Status ===")
    print(json.dumps(wf.get_workflow_status(), indent=2))
    
    # Print final task status
    print("\n=== Final Task Status ===")
    print(json.dumps(wf.get_task_status(task.task_id), indent=2))
    
    # Print correction history
    print("\n=== Correction History ===")
    print(json.dumps(wf.correction_handler.get_correction_history(), indent=2)) 