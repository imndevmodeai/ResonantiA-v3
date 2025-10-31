
# -*- coding: utf-8 -*-
"""
ArchE Engineering Instance: IAR-Compliant Workflow Engine
Directive: Autopoietic System GenesiS
Protocol: ResonantiA v3.5
"""

import json
import os
import sys
import datetime
import re
from typing import Dict, Any, Callable, List, Optional, Set

# ==============================================================================
# Helper Components for a Runnable Example
# These would be part of a larger system in a real environment.
# ==============================================================================

class ActionRegistry:
    """
    A simple registry for mapping action type strings to callable functions.
    This represents the 'Parts Bin' from the allegory.

    # This class is a direct implementation of the 'Action registrY' SPR.
    """
    def __init__(self):
        self._actions: Dict[str, Callable[..., Dict[str, Any]]] = {}

    def register_action(self, action_type: str, action_func: Callable[..., Dict[str, Any]]):
        """Registers a function for a given action type."""
        self._actions[action_type] = action_func

    def get_action(self, action_type: str) -> Callable[..., Dict[str, Any]]:
        """
        Retrieves an action function from the registry.

        Args:
            action_type: The name of the action to retrieve.

        Returns:
            The callable function associated with the action type.

        Raises:
            KeyError: If the action_type is not found in the registry.
        """
        if action_type not in self._actions:
            raise KeyError(f"Action type '{action_type}' not found in registry.")
        return self._actions[action_type]

def _create_iar_compliant_response(
    status: str,
    confidence: float,
    result: Any,
    potential_issues: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Helper to create a standard IAR-compliant dictionary.

    # This function enforces the structure required by the 'IntegratedActionReflectioN' SPR.
    """
    return {
        "status": status,
        "confidence": confidence,
        "result": result,
        "potential_issues": potential_issues if potential_issues is not None else [],
        "reflection_timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

# --- Example IAR-Compliant Actions ---

def get_user_goal(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Mock action to retrieve an initial goal."""
    goal = inputs.get("user_prompt", "No goal provided.")
    return _create_iar_compliant_response(
        status="success",
        confidence=0.99,
        result={"goal_statement": f"The user wants to: {goal}"}
    )

def generate_steps(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Mock action to generate steps based on a goal."""
    goal_statement = inputs.get("goal", {}).get("goal_statement", "an unknown goal")
    steps = [
        f"Step 1: Deconstruct '{goal_statement}'",
        "Step 2: Formulate a high-level plan.",
        "Step 3: Execute the plan.",
    ]
    return _create_iar_compliant_response(
        status="success",
        confidence=0.90,
        result={"plan": steps}
    )

def vet_steps(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Mock action that vets a plan and might find issues."""
    plan = inputs.get("steps", {}).get("plan", [])
    if not plan:
        return _create_iar_compliant_response(
            status="failure",
            confidence=1.0,
            result={"vetted": False, "reason": "Plan is empty."},
            potential_issues=["Cannot proceed with an empty plan."]
        )
    return _create_iar_compliant_response(
        status="success",
        confidence=0.95,
        result={"vetted": True, "reason": "Plan seems plausible."}
    )

def failing_action(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """A mock action that always fails its IAR validation."""
    return {"some_other_key": "this is not IAR compliant"}


# ==============================================================================
# Core Engine Implementation
# ==============================================================================

class IARCompliantWorkflowEngine:
    """
    Executes a structured workflow defined in a blueprint file.
    It processes tasks in an order determined by their dependencies,
    validates that each action performed is IAR-compliant, and provides
    observability through VCD events.

    # This class embodies the 'Core workflow enginE' SPR.
    # It solves the 'Execution paradoX' by providing a reliable, observable,
    # and self-aware mechanism for translating intent into outcomes.
    # Its operation enables 'Autopoietic System GenesiS'.
    """

    def __init__(self, action_registry: ActionRegistry):
        """
        Initializes the workflow engine.

        Args:
            action_registry: An instance of ActionRegistry containing the
                             available actions (the 'parts bin').
        """
        # This uses the 'Action registrY' SPR.
        self.action_registry = action_registry
        self.IAR_REQUIRED_KEYS = {"status", "confidence", "result"}

    def run_workflow(self, workflow_path: str, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Loads and executes a workflow from a specified path.

        This is the main assembly process that executes 'Process blueprintS'.

        Args:
            workflow_path: The file path to the JSON workflow blueprint.
            initial_context: A dictionary with initial data for the workflow.

        Returns:
            A dictionary representing the final state of the context after
            all tasks have been executed.

        Raises:
            ValueError: If the workflow has a circular dependency or a
                        missing dependency.
            Exception: Propagates exceptions from task execution.
        """
        self.emit_vcd_event("WorkflowStart", f"Initiating workflow from '{workflow_path}'")
        
        try:
            workflow = self._load_workflow_blueprint(workflow_path)
            context = initial_context.copy()
            
            tasks_to_process = workflow.get('tasks', {})
            completed_tasks: Set[str] = set(context.keys())
            
            # Use a topological sort-like loop to handle dependencies
            progress_made_in_pass = True
            while tasks_to_process and progress_made_in_pass:
                progress_made_in_pass = False
                runnable_tasks = {}

                for task_key, task_info in tasks_to_process.items():
                    if self._dependencies_met(task_info, completed_tasks):
                        runnable_tasks[task_key] = task_info
                
                if not runnable_tasks:
                    # No runnable tasks found in this pass, break the loop
                    break

                for task_key, task_info in runnable_tasks.items():
                    self.emit_vcd_event("TaskEvaluation", f"Evaluating task: {task_key}")

                    if not self._condition_met(task_info, context):
                        self.emit_vcd_event("TaskSkip", f"Skipping task '{task_key}' due to unmet condition.", {"condition": task_info.get('condition')})
                        # Mark as "completed" to unblock dependents, but add no result
                        completed_tasks.add(task_key)
                        del tasks_to_process[task_key]
                        progress_made_in_pass = True
                        continue

                    self.emit_vcd_event("TaskExecution", f"Executing task: {task_key}...")
                    
                    try:
                        resolved_inputs = self._resolve_inputs(task_info, context)
                        action_func = self.action_registry.get_action(task_info['action_type'])
                        
                        # Execute the action and get the IAR-compliant result
                        result_with_iar = action_func(resolved_inputs)
                        
                        # The 'Magnifying Loupe': Validate IAR compliance
                        self._validate_iar(result_with_iar, task_key)
                        
                        context[task_key] = result_with_iar
                        completed_tasks.add(task_key)
                        del tasks_to_process[task_key]
                        progress_made_in_pass = True
                        
                        self.emit_vcd_event("TaskSuccess", f"Task '{task_key}' completed successfully.", {"status": result_with_iar['status']})

                    except Exception as e:
                        self.emit_vcd_event("TaskFailure", f"Task '{task_key}' failed during execution.", {"error": str(e)})
                        # Propagate the error to halt the workflow
                        raise e

            if tasks_to_process:
                remaining_keys = list(tasks_to_process.keys())
                raise ValueError(f"Workflow stalled. Could not resolve dependencies for tasks: {remaining_keys}. Check for circular or missing dependencies.")

            self.emit_vcd_event("WorkflowSuccess", "Workflow completed successfully.")
            return context

        except Exception as e:
            self.emit_vcd_event("WorkflowFailure", "Workflow terminated due to an unrecoverable error.", {"error": str(e)})
            raise

    def _load_workflow_blueprint(self, workflow_path: str) -> Dict[str, Any]:
        """Loads the workflow JSON file."""
        try:
            with open(workflow_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Workflow blueprint not found at '{workflow_path}'")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in workflow blueprint '{workflow_path}': {e}")

    def _dependencies_met(self, task_info: Dict[str, Any], completed_tasks: Set[str]) -> bool:
        """Checks if all dependencies for a task have been met."""
        dependencies = task_info.get('dependencies', [])
        return all(dep in completed_tasks for dep in dependencies)

    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """
        Resolves a value that might be a reference to the context.
        e.g., "$context.task_a.result.key"
        """
        if isinstance(value, str) and value.startswith('$context.'):
            path = value[len('$context.'):].split('.')
            current_val = context
            try:
                for key in path:
                    if isinstance(current_val, dict):
                        current_val = current_val[key]
                    else:
                        raise KeyError(f"Path segment '{key}' not found in non-dict.")
                return current_val
            except (KeyError, TypeError) as e:
                raise ValueError(f"Could not resolve context path '{value}': {e}")
        return value

    def _resolve_inputs(self, task_info: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolves all input values for a task from the context."""
        resolved_inputs = {}
        for key, val in task_info.get('inputs', {}).items():
            resolved_inputs[key] = self._resolve_value(val, context)
        return resolved_inputs

    def _condition_met(self, task_info: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluates if the task's execution condition is met.
        Supports simple "path == 'value'" or "path != 'value'" conditions.
        """
        condition_str = task_info.get('condition')
        if not condition_str:
            return True  # No condition means it's always met.

        # Simple, safe parser for "path op value"
        match = re.match(r"^\s*(\$context\.\S+)\s*(==|!=)\s*(.+)\s*$", condition_str)
        if not match:
            raise ValueError(f"Unsupported condition format: '{condition_str}'")

        path, op, literal_val_str = match.groups()
        
        try:
            actual_val = self._resolve_value(path, context)
        except ValueError:
            # If the path doesn't resolve, the condition is false.
            return False

        # Safely evaluate the literal value
        try:
            expected_val = json.loads(literal_val_str)
        except json.JSONDecodeError:
            # If it's not valid JSON, it must be a bare literal like true/false/null or a malformed string
            if literal_val_str.lower() == 'true':
                expected_val = True
            elif literal_val_str.lower() == 'false':
                expected_val = False
            elif literal_val_str.lower() == 'null':
                expected_val = None
            else:
                raise ValueError(f"Malformed literal value in condition: {literal_val_str}")

        if op == '==':
            return actual_val == expected_val
        if op == '!=':
            return actual_val != expected_val
        
        return False

    def _validate_iar(self, result: Dict[str, Any], task_key: str) -> None:
        """
        Ensures a task's result is IAR-compliant.

        # This function enforces compliance with the 'IntegratedActionReflectioN' SPR.
        """
        if not isinstance(result, dict) or not self.IAR_REQUIRED_KEYS.issubset(result.keys()):
            raise TypeError(
                f"Result for task '{task_key}' is not IAR-compliant. "
                f"Must be a dict containing keys: {self.IAR_REQUIRED_KEYS}. "
                f"Received: {result}"
            )

    def emit_vcd_event(self, event_type: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Emits a Verifiable Causal-chain Data (VCD) event.
        This provides radical transparency to the Keyholder.

        # This function is the implementation of the 'VCD Events' concept.
        """
        event = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "source": "IARCompliantWorkflowEngine",
            "event_type": event_type,
            "message": message,
            "metadata": metadata or {}
        }
        print(json.dumps(event), file=sys.stdout)


# ==============================================================================
# Main Execution Block for Demonstration
# ==============================================================================

def main():
    """
    Sets up and runs a demonstration of the IARCompliantWorkflowEngine.
    """
    print("--- ArchE: IAR-Compliant Workflow Engine Genesis ---")

    # 1. Define a sample workflow blueprint
    workflow_blueprint = {
        "name": "User Goal Processing Workflow",
        "version": "1.0",
        "tasks": {
            "get_goal": {
                "action_type": "get_user_goal",
                "inputs": {
                    "user_prompt": "$context.prompt"
                }
            },
            "generate_plan": {
                "action_type": "generate_steps",
                "dependencies": ["get_goal"],
                "inputs": {
                    "goal": "$context.get_goal.result"
                }
            },
            "vet_the_plan": {
                "action_type": "vet_steps",
                "dependencies": ["generate_plan"],
                "inputs": {
                    "steps": "$context.generate_plan.result"
                }
            },
            "conditional_success_task": {
                "action_type": "get_user_goal", # Re-using an action for demo
                "dependencies": ["vet_the_plan"],
                "condition": "$context.vet_the_plan.result.vetted == true",
                "inputs": {
                    "user_prompt": "Plan was successfully vetted."
                }
            },
            "failing_iar_task": {
                "action_type": "failing_action",
                "dependencies": ["get_goal"]
            }
        }
    }
    
    workflow_file = "workflow.json"
    with open(workflow_file, "w") as f:
        json.dump(workflow_blueprint, f, indent=2)

    # 2. Setup the Action Registry with mock functions
    registry = ActionRegistry()
    registry.register_action("get_user_goal", get_user_goal)
    registry.register_action("generate_steps", generate_steps)
    registry.register_action("vet_steps", vet_steps)
    registry.register_action("failing_action", failing_action)

    # 3. Instantiate the engine
    engine = IARCompliantWorkflowEngine(action_registry=registry)

    # 4. Define initial context and run the workflow
    initial_context = {"prompt": "create a novel about a space-faring cat"}
    
    print("\n--- RUNNING SUCCESSFUL WORKFLOW ---")
    try:
        # We need to create a workflow without the failing task for the success case
        success_workflow = workflow_blueprint.copy()
        del success_workflow["tasks"]["failing_iar_task"]
        success_workflow_file = "success_workflow.json"
        with open(success_workflow_file, "w") as f:
            json.dump(success_workflow, f, indent=2)

        final_context = engine.run_workflow(success_workflow_file, initial_context)
        print("\n--- FINAL CONTEXT (SUCCESS) ---")
        print(json.dumps(final_context, indent=2))
        os.remove(success_workflow_file)

    except Exception as e:
        print(f"\n--- WORKFLOW FAILED UNEXPECTEDLY ---")
        print(f"Error: {e}")

    print("\n\n--- RUNNING WORKFLOW EXPECTED TO FAIL (IAR VALIDATION) ---")
    try:
        # This workflow includes a task that returns a non-IAR-compliant result
        failing_workflow_file = "failing_workflow.json"
        with open(failing_workflow_file, "w") as f:
            # Create a workflow with just the failing task for a clean demo
            failing_blueprint = {
                "name": "Failing Workflow", "version": "1.0",
                "tasks": {"failing_iar_task": workflow_blueprint["tasks"]["failing_iar_task"]}
            }
            json.dump(failing_blueprint, f, indent=2)

        engine.run_workflow(failing_workflow_file, initial_context)
    except TypeError as e:
        print(f"\n--- WORKFLOW FAILED AS EXPECTED ---")
        print(f"Caught expected error: {e}")
    finally:
        if os.path.exists("failing_workflow.json"):
            os.remove("failing_workflow.json")


    # 5. Cleanup the main workflow file
    if os.path.exists(workflow_file):
        os.remove(workflow_file)
    
    print("\n--- ArchE Genesis Complete ---")


if __name__ == "__main__":
    main()
