# --- START OF FILE 3.0ArchE/workflow_engine.py ---
# ResonantiA Protocol v3.0 - workflow_engine.py
# Orchestrates the execution of defined workflows (Process Blueprints).
# Manages context, dependencies, conditions, action execution, and error handling.
# Critically handles Integrated Action Reflection (IAR) results by storing
# the complete action output dictionary (including 'reflection') in the context.

import json
import os
import logging
import copy
import time
import re
import numpy as np # Added for condition evaluation helper
from typing import Dict, Any, List, Optional, Set, Union, Tuple # Expanded type hints
# Use relative imports within the package
from . import config
from .action_registry import execute_action # Imports the function that calls specific tools
from .spr_manager import SPRManager # May be used for SPR-related context or validation
from .error_handler import handle_action_error, DEFAULT_ERROR_STRATEGY, DEFAULT_RETRY_ATTEMPTS # Imports error handling logic
import uuid # Added import
from pathlib import Path

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """
    Executes workflows defined in JSON (Process Blueprints) according to ResonantiA v3.0.
    Serves as the execution backbone for these Process Blueprints, including those
    instantiating MetaWorkflow SPRs, by orchestrating task execution based on dependencies,
    resolving inputs using context, and evaluating conditions.

    Critically, it manages the invocation of actions (tools) via the action_registry
    and ensures adherence to the Integrated Action Reflection (IAR) protocol by
    storing the complete action result (primary output + 'reflection' dictionary)
    from each step into the workflow context. This IAR data is then available for
    subsequent tasks and conditional logic.

    The engine also integrates with error handling strategies (retry, fail_fast,
    trigger_metacog) and conceptually acknowledges Keyholder Override for potential bypasses.
    """
    def __init__(self, spr_manager: Optional[SPRManager] = None):
        # Initialize with paths and settings from config
        self.workflows_dir = getattr(config, 'WORKFLOW_DIR', 'workflows')
        self.max_recursion_depth = getattr(config, 'MAX_RECURSION_DEPTH', 10) # Safety limit
        self.spr_manager = spr_manager # Store SPR manager if provided
        self.last_workflow_name: Optional[str] = None # Store name of last loaded workflow
        logger.info(f"Workflow Engine (v3.0) initialized. Workflows expected in: '{self.workflows_dir}'")
        if not os.path.isdir(self.workflows_dir):
            # Log warning if configured workflow directory doesn't exist
            logger.warning(f"Workflows directory '{self.workflows_dir}' does not exist or is not a directory.")

    def load_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """
        Loads and validates a workflow definition from a JSON file.
        Handles relative paths based on configured workflows_dir.
        Performs basic structural validation (presence of 'tasks' dictionary).
        """
        if not isinstance(workflow_name, str):
            raise TypeError("workflow_name must be a string.")

        # Construct full path, handling relative paths and '.json' extension
        filepath = workflow_name
        if not os.path.isabs(filepath) and not filepath.startswith(self.workflows_dir):
            filepath = os.path.join(self.workflows_dir, filepath)
        # Auto-append .json if missing and file exists or likely intended
        if not filepath.lower().endswith(".json"):
            potential_json_path = filepath + ".json"
            if os.path.exists(potential_json_path):
                filepath = potential_json_path
            elif not os.path.exists(filepath): # If original path also doesn't exist, assume .json was intended
                filepath += ".json"

        logger.info(f"Attempting to load workflow definition from: {filepath}")
        if not os.path.exists(filepath):
            logger.error(f"Workflow file not found: {filepath}")
            raise FileNotFoundError(f"Workflow file not found: {filepath}")
        if not os.path.isfile(filepath):
            logger.error(f"Workflow path is not a file: {filepath}")
            raise ValueError(f"Workflow path is not a file: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                workflow = json.load(f)

            # Basic structural validation
            if not isinstance(workflow, dict):
                raise ValueError("Workflow file content must be a JSON object (dictionary).")
            if "tasks" not in workflow or not isinstance(workflow.get("tasks"), dict):
                raise ValueError("Workflow file must contain a 'tasks' dictionary.")
            # Validate individual task structure (basic)
            for task_id, task_data in workflow["tasks"].items():
                if not isinstance(task_data, dict):
                    raise ValueError(f"Task definition for '{task_id}' must be a dictionary.")
                if "action_type" not in task_data:
                    raise ValueError(f"Task '{task_id}' is missing required 'action_type'.")

            loaded_name = workflow.get('name', os.path.basename(filepath))
            self.last_workflow_name = loaded_name # Store name for logging/results
            logger.info(f"Successfully loaded and validated workflow: '{loaded_name}'")
            return workflow
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from workflow file {filepath}: {e}")
            raise ValueError(f"Invalid JSON in workflow file: {filepath}")
        except Exception as e:
            logger.error(f"Unexpected error loading workflow file {filepath}: {e}", exc_info=True)
            raise # Re-raise other unexpected errors

    def _resolve_value(self, value: Any, context: Dict[str, Any], current_key: Optional[str] = None, depth: int = 0) -> Any:
        """
        Recursively resolves a value potentially containing context references {{...}}.
        Supports dot notation for accessing nested dictionary keys and list indices
        within task results (including accessing IAR 'reflection' data).
        Handles lists and dictionaries containing references. Includes depth limit.
        """
        if depth > self.max_recursion_depth: # Prevent excessive recursion
            logger.error(f"Recursion depth limit ({self.max_recursion_depth}) exceeded resolving value for key '{current_key}'. Returning None.")
            return None

        if isinstance(value, str):
            # Regex to find all occurrences of {{ var.path }}
            # Non-greedy match for var.path to handle multiple on one line correctly
            # Needs to handle cases where the entire string is a template vs. interpolation
            
            # First, check if the entire string is a template {{...}}
            if value.startswith("{{") and value.endswith("}}"):
                var_path = value[2:-2].strip()
                if not var_path: return None # Handle empty braces {{}}
                # ... (rest of the existing full-template resolution logic, copied below)
                if var_path == 'initial_context':
                    return copy.deepcopy(context.get('initial_context', {}))
                if var_path == 'workflow_run_id':
                    return context.get('workflow_run_id', 'unknown_run')
                parts = var_path.split('.')
                current_val = context
                try:
                    for i, part in enumerate(parts):
                        if isinstance(current_val, dict):
                            if part in current_val:
                                current_val = current_val[part]
                            elif part.isdigit() and int(part) in current_val:
                                current_val = current_val[int(part)]
                            elif i == 0 and 'initial_context' in context and part in context['initial_context']:
                                current_val = context['initial_context'][part]
                            else:
                                raise KeyError(f"Key '{part}' not found in dictionary.")
                        elif isinstance(current_val, list):
                            try:
                                idx = int(part)
                                if not -len(current_val) <= idx < len(current_val):
                                    raise IndexError("List index out of range.")
                                current_val = current_val[idx]
                            except (ValueError, IndexError) as e_list:
                                raise KeyError(f"Invalid list index '{part}': {e_list}")
                        else:
                            raise TypeError(f"Cannot access part '{part}' in non-dict/non-list context: {type(current_val)}")
                    resolved_value = copy.deepcopy(current_val) if isinstance(current_val, (dict, list)) else current_val
                    logger.debug(f"Resolved full template '{var_path}' for key '{current_key}' to value: {str(resolved_value)[:80]}...")
                    return resolved_value
                except (KeyError, IndexError, TypeError) as e:
                    logger.warning(f"Could not resolve context variable '{var_path}' for key '{current_key}'. Error: {e}. Returning None.")
                    return None
                except Exception as e_resolve:
                    logger.error(f"Unexpected error resolving context variable '{var_path}' for key '{current_key}': {e_resolve}", exc_info=True)
                    return None
            else:
                # If not a full template, perform string interpolation
                # Using a simpler regex to find all {{...}} occurrences
                # This will replace each {{var.path}} with its resolved value or "None" if unresolvable
                # A more robust version might raise errors or have specific format for unresolvable vars
                def replace_match(match):
                    var_path_interpolated = match.group(1).strip()
                    # Temporarily call _resolve_value for this sub-template.
                    # This is recursive. Ensure base cases handle depth correctly.
                    # Wrap with {{}} to use the full-template logic above for resolution.
                    resolved_var = self._resolve_value(f"{{{{{var_path_interpolated}}}}}", context, f"{current_key} [interpolation of {var_path_interpolated}]", depth + 1)
                    return str(resolved_var) if resolved_var is not None else "None" # Or handle unresolved differently
                
                # Use re.sub with a function to handle replacements
                # Regex to find {{ any_chars_non_greedy }} 
                interpolated_string = re.sub(r"{{\s*(.*?)\s*}}", replace_match, value)
                if interpolated_string != value:
                     logger.debug(f"Interpolated string for key '{current_key}'. Original: '{value}', Result: '{interpolated_string}'")
                return interpolated_string

        elif isinstance(value, dict):
            # Recursively resolve values within a dictionary
            return {k: self._resolve_value(v, context, k, depth + 1) for k, v in value.items()}
        elif isinstance(value, list):
            # Recursively resolve items within a list
            return [self._resolve_value(item, context, f"{current_key}[{i}]" if current_key else f"list_item[{i}]", depth + 1) for i, item in enumerate(value)]
        else:
            # Return non-string, non-collection values directly
            return value

    def _resolve_inputs(self, inputs: Optional[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolves all input values for a task using the current context."""
        if not isinstance(inputs, dict):
            # Handle case where inputs might be missing or not a dict
            logger.debug("Task inputs missing or not a dictionary. Returning empty inputs.")
            return {}
        resolved_inputs = {}
        for key, value in inputs.items():
            resolved_inputs[key] = self._resolve_value(value, context, key)
        return resolved_inputs

    def _evaluate_condition(self, condition_str: Optional[str], context: Dict[str, Any]) -> bool:
        """
        Evaluates a condition string against the current context.
        Supports basic comparisons (==, !=, >, <, >=, <=), truthiness checks,
        and membership checks (in, not in) on resolved context variables,
        including accessing IAR reflection data (e.g., {{task_A.reflection.confidence}}).
        Returns True if condition is met or if condition_str is empty/None.
        """
        if not condition_str or not isinstance(condition_str, str):
            return True # No condition means execute
        condition_str = condition_str.strip()
        logger.debug(f"Evaluating condition: '{condition_str}'")

        try:
            # Simple true/false literals
            condition_lower = condition_str.lower()
            if condition_lower == 'true': return True
            if condition_lower == 'false': return False

            # Regex for comparison: {{ var.path }} OP value (e.g., {{task_A.reflection.confidence}} > 0.7)
            comp_match = re.match(r"^{{\s*([\w\.\-]+)\s*}}\s*(==|!=|>|<|>=|<=)\s*(.*)$", condition_str)
            if comp_match:
                var_path, operator, value_str = comp_match.groups()
                actual_value = self._resolve_value(f"{{{{{var_path}}}}}", context) # Resolve the variable
                expected_value = self._parse_condition_value(value_str) # Parse the literal value
                result = self._compare_values(actual_value, operator, expected_value)
                logger.debug(f"Condition '{condition_str}' evaluated to {result} (Actual: {repr(actual_value)}, Op: {operator}, Expected: {repr(expected_value)})")
                return result

            # Regex for membership: value IN/NOT IN {{ var.path }} (e.g., "Error" in {{task_B.reflection.potential_issues}})
            in_match = re.match(r"^(.+?)\s+(in|not in)\s+{{\s*([\w\.\-]+)\s*}}$", condition_str, re.IGNORECASE)
            if in_match:
                value_str, operator, var_path = in_match.groups()
                value_to_check = self._parse_condition_value(value_str.strip()) # Parse the literal value
                container = self._resolve_value(f"{{{{{var_path}}}}}", context) # Resolve the container
                operator_lower = operator.lower()
                if isinstance(container, (list, str, dict, set)): # Check if container type supports 'in'
                        is_in = value_to_check in container
                        result = is_in if operator_lower == 'in' else not is_in
                        logger.debug(f"Condition '{condition_str}' evaluated to {result}")
                        return result
                else:
                        logger.warning(f"Container for '{operator}' check ('{var_path}') is not a list/str/dict/set: {type(container)}. Evaluating to False.")
                        return False

            # Regex for simple truthiness/existence: {{ var.path }} or !{{ var.path }}
            truth_match = re.match(r"^(!)?\s*{{\s*([\w\.\-]+)\s*}}$", condition_str)
            if truth_match:
                negated, var_path = truth_match.groups()
                actual_value = self._resolve_value(f"{{{{{var_path}}}}}", context)
                result = bool(actual_value)
                if negated: result = not result
                logger.debug(f"Condition '{condition_str}' (truthiness/existence) evaluated to {result}")
                return result

            # If no pattern matches
            logger.error(f"Unsupported condition format: {condition_str}. Defaulting evaluation to False.")
            return False
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition_str}': {e}. Defaulting to False.", exc_info=True)
            return False

    def _parse_condition_value(self, value_str: str) -> Any:
        """Parses the literal value part of a condition string into Python types."""
        val_str_cleaned = value_str.strip()
        val_str_lower = val_str_cleaned.lower()
        # Handle boolean/None literals
        if val_str_lower == 'true': return True
        if val_str_lower == 'false': return False
        if val_str_lower == 'none' or val_str_lower == 'null': return None
        # Try parsing as number (float then int)
        try:
            if '.' in val_str_cleaned or 'e' in val_str_lower: return float(val_str_cleaned)
            else: return int(val_str_cleaned)
        except ValueError:
            # Handle quoted strings
            if len(val_str_cleaned) >= 2 and val_str_cleaned.startswith(('"', "'")) and val_str_cleaned.endswith(val_str_cleaned[0]):
                return val_str_cleaned[1:-1]
            # Otherwise, return as unquoted string
            return val_str_cleaned

    def _compare_values(self, actual: Any, operator: str, expected: Any) -> bool:
        """Performs comparison between actual and expected values based on operator."""
        logger.debug(f"Comparing: {repr(actual)} {operator} {repr(expected)}")
        try:
            if operator == '==': return actual == expected
            if operator == '!=': return actual != expected
            # Ordered comparisons require compatible types (numeric or string)
            numeric_types = (int, float, np.number) # Include numpy numbers
            if isinstance(actual, numeric_types) and isinstance(expected, numeric_types):
                # Convert numpy types to standard Python types for comparison if needed
                actual_cmp = float(actual) if isinstance(actual, np.number) else actual
                expected_cmp = float(expected) if isinstance(expected, np.number) else expected
                if operator == '>': return actual_cmp > expected_cmp
                if operator == '<': return actual_cmp < expected_cmp
                if operator == '>=': return actual_cmp >= expected_cmp
                if operator == '<=': return actual_cmp <= expected_cmp
            elif isinstance(actual, str) and isinstance(expected, str):
                # String comparison
                if operator == '>': return actual > expected
                if operator == '<': return actual < expected
                if operator == '>=': return actual >= expected
                if operator == '<=': return actual <= expected
            else:
                # Type mismatch for ordered comparison
                logger.warning(f"Type mismatch or unsupported type for ordered comparison '{operator}': actual={type(actual)}, expected={type(expected)}. Evaluating to False.")
                return False
        except TypeError as e:
            # Catch potential errors during comparison (e.g., comparing None)
            logger.warning(f"TypeError during comparison '{operator}' between {type(actual)} and {type(expected)}: {e}. Evaluating to False.")
            return False
        except Exception as e_cmp:
            logger.error(f"Unexpected error during value comparison: {e_cmp}. Evaluating condition to False.")
            return False
        # Should not be reached if operator is valid
        logger.warning(f"Operator '{operator}' invalid or comparison failed for types {type(actual)} and {type(expected)}. Evaluating to False.")
        return False

    def run_workflow(self, workflow_name: str, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a loaded workflow using a topological sort approach.
        Manages context, dependencies, conditions, action calls (via registry),
        stores the full action result (including IAR 'reflection'), and handles errors.
        """
        run_start_time = time.time()
        try:
            # Load and validate the workflow definition
            workflow = self.load_workflow(workflow_name)
            workflow_display_name = self.last_workflow_name # Use name stored during load
        except (FileNotFoundError, ValueError, TypeError) as e:
            logger.error(f"Failed to load or validate workflow '{workflow_name}': {e}")
            # Return an error structure consistent with normal results
            return {"error": f"Failed to load/validate workflow: {e}", "workflow_status": "Failed", "final_results": initial_context}
        except Exception as e_load:
            logger.critical(f"Unexpected critical error loading workflow {workflow_name}: {e_load}", exc_info=True)
            return {"error": f"Unexpected critical error loading workflow: {e_load}", "workflow_status": "Failed", "final_results": initial_context}

        tasks = workflow.get("tasks", {})
        if not tasks:
            logger.warning(f"Workflow '{workflow_display_name}' contains no tasks.")
            run_duration_empty = time.time() - run_start_time
            return {
                "workflow_name": workflow_display_name,
                "workflow_status": "Completed (No Tasks)",
                "task_statuses": {},
                "workflow_run_duration_sec": round(run_duration_empty, 2),
                "initial_context": initial_context,
                "workflow_definition": workflow
            }

        # --- Initialize Execution State ---
        # task_results stores the full output dictionary (result + reflection) for each task
        task_results: Dict[str, Any] = {"initial_context": copy.deepcopy(initial_context)}
        run_id = initial_context.get("workflow_run_id", f"run_{uuid.uuid4().hex}") # Ensure run_id is set
        task_results["workflow_run_id"] = run_id
        task_results['workflow_definition'] = workflow # Store definition for reference
        # task_status tracks the state of each task (pending, queued, running, completed, failed, skipped, incomplete)
        task_status: Dict[str, str] = {task_id: 'pending' for task_id in tasks}

        # --- Build Dependency Graph & Validate ---
        # adj: adjacency list (task -> list of tasks depending on it)
        # in_degree: count of dependencies for each task
        adj: Dict[str, List[str]] = {task_id: [] for task_id in tasks}
        in_degree: Dict[str, int] = {task_id: 0 for task_id in tasks}
        valid_workflow_structure = True
        validation_errors: List[str] = []

        for task_id, task_data in tasks.items():
            # Validate dependencies list
            deps = task_data.get("dependencies", [])
            if not isinstance(deps, list):
                validation_errors.append(f"Task '{task_id}' dependencies must be a list, got {type(deps)}.")
                valid_workflow_structure = False; continue
            if task_id in deps: # Check for self-dependency
                validation_errors.append(f"Task '{task_id}' cannot depend on itself.")
                valid_workflow_structure = False

            in_degree[task_id] = len(deps) # Set initial in-degree

            # Build adjacency list and check if dependencies exist
            for dep in deps:
                if dep not in tasks:
                    validation_errors.append(f"Task '{task_id}' has unmet dependency: '{dep}'.")
                    valid_workflow_structure = False
                elif dep in adj:
                    adj[dep].append(task_id) # Add edge from dependency to current task
                else: # Should not happen if dep exists, but safeguard
                    validation_errors.append(f"Internal error building graph for dependency '{dep}' of task '{task_id}'.")
                    valid_workflow_structure = False

        if not valid_workflow_structure:
            logger.error(f"Workflow '{workflow_display_name}' has structural errors: {'; '.join(validation_errors)}")
            return {
                "error": f"Workflow definition invalid: {'; '.join(validation_errors)}",
                "workflow_status": "Failed",
                "task_statuses": task_status,
                "final_results": task_results # Return partial context
            }

        # --- Initialize Execution Queue ---
        # Start with tasks that have no dependencies (in-degree is 0)
        task_queue: List[str] = [task_id for task_id, degree in in_degree.items() if degree == 0]
        for task_id in task_queue: task_status[task_id] = 'queued' # Mark initial tasks as ready
        logger.info(f"Starting workflow '{workflow_display_name}' (Run ID: {run_id}). Initial ready tasks: {task_queue}")

        # --- Execution Loop (Topological Sort) ---
        executed_task_ids: Set[str] = set()
        executed_step_count = 0
        # Safety break to prevent infinite loops in case of unexpected graph state
        max_steps_safety_limit = len(tasks) * 2 + 10 # Allow for retries etc.

        while task_queue: # Continue as long as there are tasks ready to run
            if executed_step_count >= max_steps_safety_limit:
                logger.error(f"Workflow execution safety limit ({max_steps_safety_limit} steps) reached. Potential infinite loop or complex retries. Halting.")
                task_results["workflow_error"] = "Execution step limit reached."; break

            # Get the next task from the queue (FIFO)
            task_id = task_queue.pop(0)
            task_data = tasks[task_id]
            task_status[task_id] = 'running'
            executed_step_count += 1
            logger.info(f"Executing task: {task_id} (Step {executed_step_count}) - Action: {task_data.get('action_type')} - Desc: {task_data.get('description', 'No description')}")

            # --- Evaluate Task Condition ---
            condition = task_data.get("condition")
            should_execute = self._evaluate_condition(condition, task_results)

            if not should_execute:
                logger.info(f"Task '{task_id}' skipped due to condition not met: '{condition}'")
                task_status[task_id] = 'skipped'
                # Store a basic result indicating skipped status and reason, including a default IAR reflection
                task_results[task_id] = {
                    "status": "skipped",
                    "reason": f"Condition not met: {condition}",
                    "reflection": { # Provide default IAR for skipped tasks
                        "status": "Skipped",
                        "summary": "Task skipped because its execution condition was not met.",
                        "confidence": None, # Confidence not applicable
                        "alignment_check": "N/A", # Alignment not applicable
                        "potential_issues": [],
                        "raw_output_preview": None
                    }
                }
                executed_task_ids.add(task_id)
                # Update downstream dependencies as if completed successfully
                for dependent_task in adj.get(task_id, []):
                    if dependent_task in in_degree:
                        in_degree[dependent_task] -= 1
                        if in_degree[dependent_task] == 0 and task_status.get(dependent_task) == 'pending':
                                task_queue.append(dependent_task)
                                task_status[dependent_task] = 'queued'
                continue # Move to the next task in the queue

            # --- Execute Task Action with Error Handling & Retries ---
            task_failed_definitively = False
            action_error_details: Dict[str, Any] = {} # Store final error if task fails
            current_attempt = 1
            # Determine max attempts for this specific task (use task override or config default)
            max_action_attempts = task_data.get("retry_attempts", DEFAULT_RETRY_ATTEMPTS) + 1

            action_result: Optional[Dict[str, Any]] = None # Initialize action_result

            while current_attempt <= max_action_attempts:
                logger.debug(f"Task '{task_id}' - Attempt {current_attempt}/{max_action_attempts}")
                try:
                    # Resolve inputs using the current context (including prior results/reflections)
                    inputs = self._resolve_inputs(task_data.get("inputs"), task_results)
                    action_type = task_data.get("action_type")
                    if not action_type: raise ValueError("Task action_type is missing.") # Should be caught earlier, but safeguard

                    # Execute the action via the registry - Expects a dict return including 'reflection'
                    # Pass task_id, task_results (as current_workflow_context), and run_id (as workflow_id)
                    action_result = execute_action(action_type, inputs)

                    # Check for explicit error key in the result first
                    if isinstance(action_result, dict) and action_result.get("error"):
                        logger.warning(f"Action '{action_type}' for task '{task_id}' returned explicit error on attempt {current_attempt}: {action_result.get('error')}")
                        action_error_details = action_result # Use the full result as error details
                        # Decide whether to retry based on error handler logic
                        error_handling_outcome = handle_action_error(task_id, action_type, action_error_details, task_results, current_attempt, max_action_attempts, task_data.get("error_strategy"))
                        if error_handling_outcome['status'] == 'retry' and current_attempt < max_action_attempts:
                                logger.info(f"Workflow engine retrying task '{task_id}' (attempt {current_attempt + 1}) after action error.")
                                current_attempt += 1; time.sleep(error_handling_outcome.get('delay_sec', 0.2 * current_attempt)) # Use delay from handler
                                continue # Retry the loop
                        else: # Fail definitively if no retry or max attempts reached
                                task_failed_definitively = True; break
                    else:
                        # Success - Store the COMPLETE result (including reflection)
                        task_results[task_id] = action_result
                        logger.info(f"Task '{task_id}' action '{action_type}' executed successfully on attempt {current_attempt}.")
                        task_failed_definitively = False; break # Exit retry loop on success

                except Exception as exec_exception:
                    # Catch critical exceptions during input resolution or action execution call
                    logger.error(f"Critical exception during task '{task_id}' action '{action_type}' \n(attempt {current_attempt}): {exec_exception}", exc_info=True)

                    # TEMPORARY BYPASS of handle_action_error due to signature mismatch
                    # Treat critical exceptions during action execution as immediate failure for now.
                    action_error_details = { # Create error details structure
                        "error": f"Critical execution exception: {str(exec_exception)}",
                        "reflection": {
                               "status": "Failure", "summary": f"Critical exception during action execution: {exec_exception}",
                               "confidence": 0.0, "alignment_check": "N/A",
                               "potential_issues": ["System Error during execution."], "raw_output_preview": None
                        }
                    }
                    task_results[task_id] = action_error_details # Store the error details as task result
                    task_status[task_id] = 'failed' # Mark the task as failed
                    task_failed_definitively = True
                    logger.error(f"Task '{task_id}' failed definitively after critical exception.")
                    break # Exit retry loop

            # --- Update Workflow State After Task Execution Attempt(s) ---
            executed_task_ids.add(task_id)
            if task_failed_definitively:
                task_status[task_id] = 'failed'
                # Store the final error details (which should include a reflection dict)
                task_results[task_id] = action_error_details
                logger.error(f"Task '{task_id}' marked as failed after {current_attempt} attempt(s). Error: {action_error_details.get('error')}")
                # Note: Failed tasks do not decrement in-degree of dependents, halting that path
            else:
                # Task completed successfully (or was skipped earlier)
                task_status[task_id] = 'completed' # Mark as completed
                # Decrement in-degree for all tasks that depend on this one
                for dependent_task in adj.get(task_id, []):
                    if dependent_task in in_degree:
                        in_degree[dependent_task] -= 1
                        # If a dependent task now has all its dependencies met and is pending, add it to the queue
                        if in_degree[dependent_task] == 0 and task_status.get(dependent_task) == 'pending':
                            task_queue.append(dependent_task)
                            task_status[dependent_task] = 'queued' # Mark as ready
                            logger.debug(f"Task '{dependent_task}' now ready and added to queue.")

            # Check if workflow stalled (no tasks ready, but some pending) - indicates cycle or logic error
            if not task_queue and len(executed_task_ids) < len(tasks):
                remaining_pending = [tid for tid, status in task_status.items() if status == 'pending']
                if remaining_pending:
                    logger.error(f"Workflow stalled: No tasks in queue, but tasks {remaining_pending} are still pending. Cycle detected or unmet dependency in logic.")
                    task_results["workflow_error"] = "Cycle detected or unmet dependency."
                    for tid in remaining_pending: task_status[tid] = 'incomplete' # Mark stalled tasks
                    break # Exit main loop

        # --- Final Workflow State Calculation ---
        run_duration = time.time() - run_start_time
        logger.info(f"Workflow '{workflow_display_name}' processing loop finished in {run_duration:.2f} seconds.")

        # Check for any remaining issues after the loop finishes
        if "workflow_error" not in task_results and len(executed_task_ids) < len(tasks):
            # If loop finished but not all tasks executed (and no prior error), mark incomplete
            incomplete_tasks = [tid for tid, status in task_status.items() if status not in ['completed', 'failed', 'skipped']]
            if incomplete_tasks:
                logger.warning(f"Workflow finished, but tasks {incomplete_tasks} did not complete (status: { {t: task_status.get(t) for t in incomplete_tasks} }).")
                task_results["workflow_error"] = "Incomplete tasks remain at workflow end."
                for task_id in incomplete_tasks:
                    if task_id not in task_results: task_results[task_id] = {"error": "Task did not complete (cycle/dependency issue?).", "reflection": {"status": "Incomplete", "summary": "Task did not run.", "confidence": None, "alignment_check": "N/A", "potential_issues": ["Workflow structure/logic issue?"], "raw_output_preview": None}}
                    if task_status.get(task_id) not in ['failed', 'skipped']: task_status[task_id] = 'incomplete'

        # Determine final overall status
        final_failed_tasks = [tid for tid, status in task_status.items() if status == 'failed']
        final_incomplete_tasks = [tid for tid, status in task_status.items() if status == 'incomplete']
        if final_failed_tasks: overall_status = "Completed with Errors"
        elif final_incomplete_tasks: overall_status = "Incomplete"
        elif "workflow_error" in task_results: overall_status = "Failed" # e.g., step limit
        else: overall_status = "Completed Successfully"

        logger.info(f"Workflow '{workflow_display_name}' finished with overall status: {overall_status}")

        # Add final status information to the results dictionary
        task_results["workflow_status"] = overall_status
        task_results["task_statuses"] = task_status # Include final status of each task
        task_results["workflow_run_duration_sec"] = round(run_duration, 2)

        # --- Generate Workflow-Level IAR ---
        num_total_tasks = len(tasks)
        num_completed = sum(1 for st in task_status.values() if st == 'completed')
        num_failed = sum(1 for st in task_status.values() if st == 'failed')
        num_skipped = sum(1 for st in task_status.values() if st == 'skipped')
        num_incomplete = sum(1 for st in task_status.values() if st == 'incomplete')

        workflow_reflection_summary = f"Workflow '{workflow_display_name}' finished with status: {overall_status}. "
        workflow_reflection_summary += f"Tasks: {num_completed} completed, {num_failed} failed, {num_skipped} skipped, {num_incomplete} incomplete out of {num_total_tasks} total."
        
        workflow_reflection_status = "Success" # Default, adjust based on overall_status
        workflow_reflection_confidence = 1.0 # Default, adjust
        workflow_reflection_issues = []

        if overall_status == "Completed Successfully":
            workflow_reflection_confidence = 0.95 # High, but acknowledge distributed nature
        elif overall_status == "Completed with Errors":
            workflow_reflection_status = "Partial Success" # Or "Failure" depending on severity interpretation
            workflow_reflection_confidence = 0.5
            workflow_reflection_issues.append(f"{num_failed} task(s) failed.")
            if task_results.get("workflow_error"): workflow_reflection_issues.append(task_results["workflow_error"])
        elif overall_status == "Incomplete":
            workflow_reflection_status = "Failure"
            workflow_reflection_confidence = 0.2
            workflow_reflection_issues.append(f"{num_incomplete} task(s) did not complete.")
            if task_results.get("workflow_error"): workflow_reflection_issues.append(task_results["workflow_error"])
        elif overall_status == "Failed": # e.g. structural errors, critical load failures
            workflow_reflection_status = "Failure"
            workflow_reflection_confidence = 0.0
            workflow_reflection_issues.append(f"Workflow failed to execute properly. Error: {task_results.get('error', 'Unknown structural/load error')}")

        task_results["reflection"] = {
            "status": workflow_reflection_status,
            "summary": workflow_reflection_summary,
            "confidence": workflow_reflection_confidence,
            "alignment_check": "Workflow-level alignment (assessed by Keyholder/Meta-Cognition)",
            "potential_issues": workflow_reflection_issues if workflow_reflection_issues else None,
            "raw_output_preview": f"Overall status: {overall_status}, Failed tasks: {num_failed}",
            "metrics": {
                 "total_tasks": num_total_tasks,
                 "completed_tasks": num_completed,
                 "failed_tasks": num_failed,
                 "skipped_tasks": num_skipped,
                 "incomplete_tasks": num_incomplete,
                 "run_duration_sec": round(run_duration, 2)
            }
        }
        # Return the complete context, including initial context, task results (with IAR), and final status info
        return task_results

# --- END OF FILE 3.0ArchE/workflow_engine.py ---