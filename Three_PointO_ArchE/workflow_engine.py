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
import uuid # Added for workflow_run_id generation consistency
from typing import Dict, Any, List, Optional, Set, Union, Tuple # Expanded type hints
# Use relative imports within the package
from . import config
from .action_registry import execute_action # Imports the function that calls specific tools
from .spr_manager import SPRManager # May be used for SPR-related context or validation
from .error_handler import handle_action_error, DEFAULT_ERROR_STRATEGY, DEFAULT_RETRY_ATTEMPTS # Imports error handling logic
from .action_context import ActionContext # Import from new file
import ast

# Attempt to import numpy for numeric type checking in _compare_values, optional
try:
    import numpy as np
except ImportError:
    np = None # Set to None if numpy is not available
    logging.info("Numpy not found, some numeric type checks in _compare_values might be limited.")

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """
    Executes workflows defined in JSON (Process Blueprints) according to ResonantiA v3.0.
    Manages task execution order based on dependencies, resolves inputs using context
    (including nested access into results and IAR reflections), evaluates conditions,
    invokes actions via the action registry, stores the complete action result
    (primary output + IAR reflection dict) in the context, and integrates with
    error handling strategies (retry, fail_fast, trigger_metacog).
    Acknowledges Keyholder Override conceptually for potential bypasses.
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

    def _extract_var_path(self, template_content: str) -> str:
        """Extracts the variable path from the template content (e.g., 'var.path' from 'var.path | filter')."""
        return template_content.split('|')[0].strip()

    def _parse_filters(self, template_content: str) -> List[Dict[str, Any]]:
        """Parses filter specifications from the template content."""
        parts = template_content.split('|')[1:]
        filters = []
        if not parts:
            return filters

        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            filter_spec = {'name': '', 'args': []}
            if '(' in part and part.endswith(')'):
                name_part, args_part_str = part[:-1].split('(', 1)
                filter_spec['name'] = name_part.strip()
                raw_args_content = args_part_str.strip()
                if raw_args_content:
                    # More robust regex for splitting CSV-like args, respecting quotes and escapes within quotes
                    # Using triple quotes for the regex string itself to avoid escaping issues for single/double quotes inside it
                    arg_pattern = re.compile(r"""(?:[^,\'\"]|'(?:[^\\']|\\\\.)*'|\"(?:[^\\\"]|\\\\.)*\")+""")
                    arg_matches = arg_pattern.findall(raw_args_content)
                    parsed_args = []
                    for arg_str in arg_matches:
                        arg_str = arg_str.strip()
                        # Try ast.literal_eval for quoted strings, then specific keywords, then numbers, then fallback to string
                        if (arg_str.startswith('"') and arg_str.endswith('"')) or \
                           (arg_str.startswith("'") and arg_str.endswith("'")):
                            try:
                                parsed_args.append(ast.literal_eval(arg_str))
                            except (ValueError, SyntaxError): # Fallback if not a valid Python literal
                                parsed_args.append(arg_str[1:-1]) # Simple unquoting as last resort
                        elif arg_str.lower() == 'true':
                            parsed_args.append(True)
                        elif arg_str.lower() == 'false':
                            parsed_args.append(False)
                        elif arg_str.lower() == 'null' or arg_str.lower() == 'none':
                            parsed_args.append(None)
                        else:
                            try:
                                if '.' in arg_str or 'e' in arg_str.lower(): # Handle floats/scientific notation
                                    parsed_args.append(float(arg_str))
                                else:
                                    parsed_args.append(int(arg_str))
                            except ValueError:
                                parsed_args.append(arg_str) # Fallback to string if not number/keyword
                    filter_spec['args'] = parsed_args
            else:
                filter_spec['name'] = part
            filters.append(filter_spec)
        return filters

    def _get_value_from_path(self, path: str, context: Dict[str, Any]) -> Any:
        """Retrieves a value from a nested dictionary using a dot-separated path."""
        if not path: # Handle cases where path might be empty (e.g. {{ | default('foo') }})
            return None
            
        keys = path.split('.')
        value = context
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list):
                try:
                    idx = int(key)
                    if 0 <= idx < len(value):
                        value = value[idx]
                    else:
                        logger.debug(f"Index '{idx}' out of bounds for path '{path}' (list length {len(value)}). Returning None.")
                        return None # Index out of bounds
                except ValueError:
                    logger.debug(f"Invalid list index '{key}' in path '{path}'. Expected integer. Returning None.")
                    return None # Invalid index format
            else:
                # Path leads to a non-dict/non-list item, or key not found
                logger.debug(f"Key '{key}' not found or invalid access in path '{path}'. Current value type: {type(value)}. Returning None.")
                return None
        return value

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

    def _resolve_value(self, value: Any, context: Dict[str, Any], task_key: Optional[str] = None) -> Any:
        """
        Resolves a value that might be a template string, a direct value, or a nested structure.
        Handles template syntax {{ placeholder | filter1 | filter2(arg) | default(\"fallback\") }}.
        """
        original_template_str = value # Keep a copy for certain checks

        if not isinstance(value, str) or not ("{{" in value and "}}" in value):
            # If it's not a string, or a string without {{...}}, return it as is.
            # This handles direct values, numbers, booleans, lists/dicts defined directly in JSON.
            return value

        logger.debug(f"Resolving template string: {value}")
        
        # Regex to find all {{...}} placeholders, including their content
        # Group 1: Full content inside {{...}} (e.g., "var.path | filter")
        # Group 0: The full match including braces (e.g., "{{ var.path | filter }}")
        matches = re.findall(r"(\{\{(.*?)\}\})", value, re.DOTALL)

        if not matches: # Should not happen if "{{" and "}}" are present, but as a safeguard
            return value

        # Case 1: The entire template string is a single placeholder (e.g., "{{ my_variable }}")
        # matches[0][0] is the full placeholder tag like "{{ my_variable | filter }}"
        # matches[0][1] is the content inside, like "my_variable | filter"
        if len(matches) == 1 and value.strip() == matches[0][0]:
            full_template_content = matches[0][1].strip()
            if not full_template_content: return "" # Handle empty braces {{}}

            var_path_str = self._extract_var_path(full_template_content)
            filters = self._parse_filters(full_template_content)
            
            default_value_from_filter = None
            has_default_filter = False
            # Check for default filter first
            for f_spec in filters:
                if f_spec['name'] == 'default':
                    has_default_filter = True
                    # Default arg should already be literal or resolved correctly by _parse_filters if it was {{...}}
                    default_value_from_filter = f_spec['args'][0] if f_spec['args'] else None
                    break
            
            resolved_var_from_context = self._get_value_from_path(var_path_str, context)

            if resolved_var_from_context is None and has_default_filter:
                current_value = default_value_from_filter
            else:
                current_value = resolved_var_from_context

            # Apply other filters
            for f_spec in filters:
                if f_spec['name'] == 'default': continue # Already handled
                if f_spec['name'] == 'toJson':
                    current_value = json.dumps(current_value)
                # Add other filters here:
                # elif f_spec['name'] == 'another_filter':
                #     current_value = self._apply_another_filter(current_value, f_spec['args'])
                else:
                    logger.warning(f"Task '{task_key}': Unknown filter '{f_spec['name']}' in template '{original_template_str}'. Skipping filter.")

            logger.debug(f"Resolved single placeholder '{value}' to: {str(current_value)[:100]}")
            return current_value

        # Case 2: The template string has one or more embedded placeholders (e.g., "Value is {{my_var}} and {{another.path}}")
        else:
            processed_template_string = value
            for full_match_tag, full_template_content_inner in matches:
                full_template_content_inner = full_template_content_inner.strip()
                if not full_template_content_inner:
                    string_to_insert = "" # Replace empty {{}} with empty string
                            else:
                    var_path_str = self._extract_var_path(full_template_content_inner)
                    filters = self._parse_filters(full_template_content_inner)
                    
                    default_value_from_filter = None
                    has_default_filter = False
                    for f_spec in filters:
                        if f_spec['name'] == 'default':
                            has_default_filter = True
                            default_value_from_filter = f_spec['args'][0] if f_spec['args'] else None
                            break
                    
                    resolved_var_from_context = self._get_value_from_path(var_path_str, context)

                    if resolved_var_from_context is None and has_default_filter:
                        current_value_for_placeholder = default_value_from_filter
                    else:
                        current_value_for_placeholder = resolved_var_from_context

                    # Apply other filters
                    for f_spec in filters:
                        if f_spec['name'] == 'default': continue
                        if f_spec['name'] == 'toJson':
                            current_value_for_placeholder = json.dumps(current_value_for_placeholder)
                        # Add other filters here
        else:
                            logger.warning(f"Task '{task_key}': Unknown filter '{f_spec['name']}' in template '{original_template_str}'. Skipping filter.")

                    # Convert the resolved placeholder value to string for embedding
                    if isinstance(current_value_for_placeholder, str):
                        string_to_insert = current_value_for_placeholder
                    elif isinstance(current_value_for_placeholder, (list, dict, tuple)):
                        string_to_insert = json.dumps(current_value_for_placeholder)
                    elif isinstance(current_value_for_placeholder, bool):
                        string_to_insert = str(current_value_for_placeholder).lower()
                    elif current_value_for_placeholder is None:
                        # Represent None as "null" if embedding in a string that might be JSON-like,
                        # or "" or "None" depending on desired string context. Let's use "null" for now.
                        string_to_insert = "null" 
                    else: # numbers, etc.
                        string_to_insert = str(current_value_for_placeholder)
                
                processed_template_string = processed_template_string.replace(full_match_tag, string_to_insert)
            
            logger.debug(f"Resolved embedded template '{value}' to: {processed_template_string[:200]}")
            return processed_template_string

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
                actual_value = self._resolve_value(f"{{{{ {var_path} }}}}", context) # Resolve the variable
                expected_value = self._parse_condition_value(value_str) # Parse the literal value
                result = self._compare_values(actual_value, operator, expected_value)
                logger.debug(f"Condition '{condition_str}' evaluated to {result} (Actual: {repr(actual_value)}, Op: {operator}, Expected: {repr(expected_value)})")
                return result

            # Regex for membership: value IN/NOT IN {{ var.path }} (e.g., "Error" in {{task_B.reflection.potential_issues}})
            in_match = re.match(r"^(.+?)\s+(in|not in)\s+{{\s*([\w\.\-]+)\s*}}$", condition_str, re.IGNORECASE)
            if in_match:
                value_str, operator, var_path = in_match.groups()
                value_to_check = self._parse_condition_value(value_str.strip()) # Parse the literal value
                container = self._resolve_value(f"{{{{{{var_path}}}}}}", context) # Resolve the container
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
                actual_value = self._resolve_value(f"{{{{{{var_path}}}}}}", context)
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
            
            # Define numeric types, including numpy types if available
            numeric_types_list = [int, float]
            if np:
                numeric_types_list.append(np.number)
            numeric_types = tuple(numeric_types_list)

            if isinstance(actual, numeric_types) and isinstance(expected, numeric_types):
                # Convert numpy types to standard Python types for comparison if needed
                actual_cmp = float(actual) if np and isinstance(actual, np.number) else actual
                expected_cmp = float(expected) if np and isinstance(expected, np.number) else expected
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

                    # Construct ActionContext for this specific action call
                    current_action_context = ActionContext(
                        task_key=task_id,
                        action_name=task_data.get("action_name", task_id),
                        action_type=action_type,
                        workflow_name=workflow.get('name', self.last_workflow_name or "UnknownWorkflow"),
                        run_id=run_id,
                        attempt_number=current_attempt,
                        max_attempts=max_action_attempts
                    )
                    logger.debug(f"Constructed ActionContext: {current_action_context}")

                    # Execute action via Action Registry, passing all required arguments
                    action_result = execute_action(
                        task_key=task_id,
                        action_name=task_data.get("action_name", task_id),
                        action_type=action_type,
                        inputs=inputs,
                        context_for_action=current_action_context,
                        max_attempts=max_action_attempts,
                        attempt_number=current_attempt
                    )
                    task_execution_successful = True # If execute_action returns without raising an exception

                    # Check for explicit error key in the result first
                    if isinstance(action_result, dict) and action_result.get("error"):
                        logger.warning(f"Action '{action_type}' for task '{task_id}' returned explicit error on attempt {current_attempt}: {action_result.get('error')}")
                        action_error_details = action_result # Use the full result as error details
                        # Decide whether to retry based on error handler logic
                        error_handling_outcome = handle_action_error(task_id, action_type, action_error_details, task_results, current_attempt)
                        if error_handling_outcome['status'] == 'retry' and current_attempt < max_action_attempts:
                                logger.info(f"Workflow engine retrying task '{task_id}' (attempt {current_attempt + 1}) after action error.")
                                current_attempt += 1; time.sleep(0.2 * current_attempt) # Simple backoff
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
                    logger.error(f"Critical exception during task '{task_id}' action '{action_type}' (attempt {current_attempt}): {exec_exception}", exc_info=True)
                    # Create a standard error structure with a default reflection
                    action_error_details = {
                        "error": f"Critical execution exception: {str(exec_exception)}",
                        "reflection": {
                                "status": "Failure", "summary": f"Critical exception: {exec_exception}",
                                "confidence": 0.0, "alignment_check": "N/A",
                                "potential_issues": ["System Error during execution."], "raw_output_preview": None
                        }
                    }
                    # Decide whether to retry based on error handler logic
                    error_handling_outcome = handle_action_error(task_id, action_type, action_error_details, task_results, current_attempt)
                    if error_handling_outcome['status'] == 'retry' and current_attempt < max_action_attempts:
                        logger.info(f"Workflow engine retrying task '{task_id}' (attempt {current_attempt + 1}) after critical exception.")
                        current_attempt += 1; time.sleep(0.2 * current_attempt) # Simple backoff
                        continue # Retry the loop
                    else: # Fail definitively if no retry or max attempts reached
                        task_failed_definitively = True; break

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

        # Return the complete context, including initial context, task results (with IAR), and final status info
        return task_results

# --- END OF FILE 3.0ArchE/workflow_engine.py --- 