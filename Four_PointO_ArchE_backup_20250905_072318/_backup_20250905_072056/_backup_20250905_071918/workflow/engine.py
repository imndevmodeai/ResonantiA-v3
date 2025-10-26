# Four_PointO_ArchE/workflow/engine.py

import json
import logging
from typing import Dict, Any, Optional, Tuple
from .action_registry import registry as action_registry
from tsp_solver.solver import TSPSolver # Example of native capability import

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """
    Orchestrates the execution of workflows defined in JSON format.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.context: Dict[str, Any] = {}
        # Initialize native capabilities
        self.tsp_solver = TSPSolver(api_key=api_key) if api_key else None

    def load_workflow(self, filepath: str) -> Dict[str, Any]:
        """
        Loads a workflow definition from a JSON file.
        """
        with open(filepath, 'r') as f:
            workflow = json.load(f)
        return workflow

    def execute_workflow(self, workflow: Dict[str, Any], context: Dict[str, Any] = None):
        """
        Executes a workflow.
        """
        logger.info(f"Starting workflow: {workflow.get('name', 'Untitled Workflow')}")
        
        self.context = context if context is not None else {}
        task_results = {}
        
        # A more advanced engine would build a dependency graph. For now, we assume tasks are ordered or have dependencies.
        tasks_to_run = list(workflow.get('tasks', {}).keys())
        executed_tasks = set()
        pruned_tasks = set()

        next_task_name = tasks_to_run[0] if tasks_to_run else None

        while next_task_name:
            if next_task_name in pruned_tasks:
                executed_tasks.add(next_task_name) # Mark as 'executed' to satisfy dependencies
                next_task_name = self._find_next_task(workflow.get('tasks', {}), executed_tasks, next_task_name)
                continue

            task = workflow['tasks'][next_task_name]
            task_name = next_task_name
            next_task_name = None # Reset for the next iteration

            # Check dependencies
            dependencies = task.get('dependencies', [])
            if not all(dep in executed_tasks for dep in dependencies):
                # Simple sequential check, find next runnable task
                next_task_name = self._find_next_task(tasks_to_run, executed_tasks)
                if task_name not in executed_tasks: # Avoid re-running the current task if deps not met
                     tasks_to_run.append(task_name)
                continue

            logger.info(f"Executing task: {task_name}")
            
            task_type = task.get('type')
            
            if task_type == 'gate':
                condition = task.get('condition')
                if self._evaluate_gate(condition):
                    next_task_name = task.get('if_true')
                    pruned_tasks.add(task.get('if_false'))
                else:
                    next_task_name = task.get('if_false')
                    pruned_tasks.add(task.get('if_true'))
                
                executed_tasks.add(task_name)
                continue

            action_name = task.get('action')
            if not action_name:
                logger.warning(f"Task {task_name} has no action defined. Skipping.")
                executed_tasks.add(task_name)
                continue

            try:
                action = self._get_action(action_name)
                
                inputs = self._prepare_inputs(task.get('inputs', {}), task_results)
                
                result, iar = action(inputs=inputs)
                
                task_results[task_name] = {'result': result, 'iar': iar}
                self.context.setdefault('tasks', {})[task_name] = task_results[task_name]
                
                logger.info(f"Task {task_name} completed with IAR confidence: {iar.get('confidence', 'N/A')}")
            
            except Exception as e:
                logger.error(f"Error executing task {task_name}: {e}", exc_info=True)
                task_results[task_name] = {'error': str(e)}
                self.context.setdefault('tasks', {})[task_name] = task_results[task_name]
                break
            
            finally:
                executed_tasks.add(task_name)
                if not next_task_name: # if not redirected by a gate
                    next_task_name = self._find_next_task(workflow.get('tasks', {}), executed_tasks, task_name)


        logger.info(f"Workflow '{workflow.get('name', 'Untitled Workflow')}' finished.")
        return {"status": "completed", "results": task_results}

    def _find_next_task(self, all_tasks, executed_tasks, last_executed=None):
        """Finds the next task to run in a simple sequential or dependency-based order."""
        if last_executed:
             # Find tasks that depend on the last executed one
            for task_name, task_data in all_tasks.items():
                if task_name not in executed_tasks and last_executed in task_data.get('dependencies', []):
                    # Check if all other dependencies are also met
                    if all(dep in executed_tasks for dep in task_data.get('dependencies', [])):
                        return task_name

        # Fallback to the first unexecuted task in the original order
        for task_name in all_tasks:
            if task_name not in executed_tasks:
                task_data = all_tasks[task_name]
                if all(dep in executed_tasks for dep in task_data.get('dependencies', [])):
                     return task_name
        return None

    def _get_action(self, action_name: str) -> Any:
        """
        Retrieves an action, handling native capabilities.
        """
        if action_name.startswith("native."):
            native_action_name = action_name.split("native.")[1]
            if hasattr(self, native_action_name):
                return getattr(self, native_action_name)
            else:
                raise ValueError(f"Native action '{native_action_name}' not found on WorkflowEngine.")

        if hasattr(self, action_name):
            return getattr(self, action_name)
        return action_registry.get_action(action_name)

    def _prepare_inputs(self, input_mapping: Dict[str, Any], task_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolves task inputs from the workflow context and previous task results.
        """
        resolved_inputs = {}
        for key, value in input_mapping.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                path = value[2:-2].strip()
                resolved_inputs[key] = self._resolve_path(path, task_results)
            else:
                resolved_inputs[key] = value
        return resolved_inputs

    def _resolve_path(self, path: str, task_results: Dict[str, Any]) -> Any:
        """Resolves a value from context or task results using a dot-notation path."""
        parts = path.split('.')
        if parts[0] == 'context':
            current_val = self.context
            parts = parts[1:]
        elif parts[0] == 'tasks':
            current_val = task_results
            parts = parts[1:]
        else:
            return None # Path must start with 'context' or 'tasks'

        for part in parts:
            if isinstance(current_val, dict):
                current_val = current_val.get(part)
            else:
                return None
        return current_val

    def _evaluate_gate(self, gate_condition: str) -> bool:
        """
        Evaluates a gate condition based on the workflow context.
        Supports simple expressions like '{{ tasks.task_name.iar.confidence > 0.8 }}'
        """
        try:
            # 1. Clean and extract the core expression
            if not (gate_condition.startswith("{{") and gate_condition.endswith("}}")):
                logger.warning(f"Invalid gate condition format: {gate_condition}. Defaulting to False.")
                return False
            
            expression = gate_condition[2:-2].strip()

            # 2. Simple parsing for "variable operator value"
            parts = expression.split()
            if len(parts) != 3:
                logger.warning(f"Invalid expression format: '{expression}'. Expected 'variable operator value'.")
                return False

            variable_path, operator, value_str = parts
            
            # 3. Resolve the variable from context
            resolved_variable = self._resolve_path(variable_path, self.context.get('tasks', {}))
            
            if resolved_variable is None:
                logger.warning(f"Resolved variable '{variable_path}' is None.")
                return False

            # 4. Coerce value to the type of the context variable
            try:
                value = type(resolved_variable)(value_str)
            except (ValueError, TypeError):
                logger.warning(f"Could not convert '{value_str}' to the type of '{resolved_variable}' ({type(resolved_variable)}).")
                return False

            # 5. Perform the comparison
            if operator == '>':
                return resolved_variable > value
            elif operator == '<':
                return resolved_variable < value
            elif operator == '==':
                return resolved_variable == value
            elif operator == '!=':
                return resolved_variable != value
            elif operator == '>=':
                return resolved_variable >= value
            elif operator == '<=':
                return resolved_variable <= value
            else:
                logger.warning(f"Unsupported operator: '{operator}'")
                return False
        
        except Exception as e:
            logger.error(f"Error evaluating gate condition '{gate_condition}': {e}", exc_info=True)
            return False

    # --- Native Capabilities ---

    def aggregate_results(self, inputs: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        A native action that aggregates results from previous steps.
        """
        aggregated = {key: value for key, value in inputs.items()}
        iar = {
            "confidence": 1.0,
            "tactical_resonance": 1.0,
            "potential_issues": [],
            "metadata": {"native_action": True}
        }
        return aggregated, iar

    # --- Example of a Native Capability exposed as an action ---
    def solve_vrp(self, addresses: list, depot_address: str, num_vehicles: int, constraints: dict):
        """
        A wrapper for the TSP Solver to be used as a workflow action.
        """
        if not self.tsp_solver:
            raise ValueError("TSP Solver not initialized. Please provide an API key.")
        return self.tsp_solver.solve_vrp_with_ortools(addresses, depot_address, num_vehicles, constraints)
