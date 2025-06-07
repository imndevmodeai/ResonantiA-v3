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
from datetime import datetime # Added import

# Attempt to import numpy for numeric type checking in _compare_values, optional
try:
    import numpy as np
except ImportError:
    np = None # Set to None if numpy is not available
    logging.info("Numpy not found, some numeric type checks in _compare_values might be limited.")

logger = logging.getLogger(__name__)


# === IAR COMPLIANCE ENHANCEMENT ===
# Crystallized Artifacts Implementation - ARTIFACT 4A

class IARValidator:
    """Validates IAR structure compliance per crystallized artifacts specification"""
    
    def __init__(self):
        self.required_fields = [
            'status', 'summary', 'confidence', 
            'alignment_check', 'potential_issues',
            'raw_output_preview'
        ]
        self.enhanced_fields = [
            'tactical_resonance', 'crystallization_potential'
        ]
    
    def validate_structure(self, iar_data):
        """Validate IAR structure meets all requirements"""
        if not isinstance(iar_data, dict):
            return False, ["IAR must be a dictionary"]
        
        missing_fields = []
        for field in self.required_fields:
            if field not in iar_data:
                missing_fields.append(field)
        
        issues = []
        if missing_fields:
            issues.extend([f"Missing required field: {field}" for field in missing_fields])
        
        # Validate confidence is float between 0-1
        confidence = iar_data.get('confidence')
        if confidence is not None:
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                issues.append("Confidence must be float between 0.0 and 1.0")
        
        # Validate status is valid
        status = iar_data.get('status')
        if status not in ['Success', 'Partial', 'Failed']:
            issues.append("Status must be 'Success', 'Partial', or 'Failed'")
        
        return len(issues) == 0, issues
    
    def validate_enhanced_fields(self, iar_data):
        """Validate enhanced IAR fields for tactical resonance"""
        enhanced_issues = []
        
        for field in self.enhanced_fields:
            if field in iar_data:
                value = iar_data[field]
                if not isinstance(value, (int, float)) or not (0.0 <= value <= 1.0):
                    enhanced_issues.append(f"{field} must be float between 0.0 and 1.0")
        
        return len(enhanced_issues) == 0, enhanced_issues

class ResonanceTracker:
    """Tracks tactical resonance and crystallization metrics"""
    
    def __init__(self):
        self.execution_history = []
        self.resonance_metrics = {
            'avg_tactical_resonance': 0.0,
            'avg_crystallization_potential': 0.0,
            'total_executions': 0
        }
    
    def record_execution(self, task_id, iar_data, context):
        """Record task execution for resonance tracking"""
        execution_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'task_id': task_id,
            'status': iar_data.get('status'),
            'confidence': iar_data.get('confidence', 0.0),
            'tactical_resonance': iar_data.get('tactical_resonance', 0.0),
            'crystallization_potential': iar_data.get('crystallization_potential', 0.0)
        }
        
        self.execution_history.append(execution_record)
        self._update_metrics()
        
        return execution_record
    
    def _update_metrics(self):
        """Update aggregate resonance metrics"""
        if not self.execution_history:
            return
        
        recent_executions = self.execution_history[-100:]  # Last 100 executions
        
        tactical_scores = [ex.get('tactical_resonance', 0.0) for ex in recent_executions]
        crystallization_scores = [ex.get('crystallization_potential', 0.0) for ex in recent_executions]
        
        self.resonance_metrics = {
            'avg_tactical_resonance': sum(tactical_scores) / len(tactical_scores),
            'avg_crystallization_potential': sum(crystallization_scores) / len(crystallization_scores),
            'total_executions': len(self.execution_history)
        }
    
    def get_resonance_report(self):
        """Get current resonance metrics report"""
        return {
            'current_metrics': self.resonance_metrics,
            'recent_trend': self._calculate_trend(),
            'compliance_score': self._calculate_compliance_score()
        }
    
    def _calculate_trend(self):
        """Calculate resonance trend over recent executions"""
        if len(self.execution_history) < 10:
            return "insufficient_data"
        
        recent_10 = self.execution_history[-10:]
        older_10 = self.execution_history[-20:-10]
        
        recent_avg = sum(ex.get('tactical_resonance', 0.0) for ex in recent_10) / 10
        older_avg = sum(ex.get('tactical_resonance', 0.0) for ex in older_10) / 10
        
        if recent_avg > older_avg + 0.05:
            return "improving"
        elif recent_avg < older_avg - 0.05:
            return "declining"
        else:
            return "stable"
    
    def _calculate_compliance_score(self):
        """Calculate overall IAR compliance score"""
        if not self.execution_history:
            return 0.0
        
        recent_executions = self.execution_history[-50:]
        successful_executions = [ex for ex in recent_executions if ex.get('status') == 'Success']
        
        success_rate = len(successful_executions) / len(recent_executions)
        avg_confidence = sum(ex.get('confidence', 0.0) for ex in successful_executions) / max(len(successful_executions), 1)
        avg_resonance = self.resonance_metrics['avg_tactical_resonance']
        
        # Weighted compliance score
        compliance_score = (success_rate * 0.4) + (avg_confidence * 0.3) + (avg_resonance * 0.3)
        return min(compliance_score, 1.0)
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
                logger.debug(f"_parse_filters: Filter '{filter_spec['name']}', raw_args_content: '{raw_args_content}'") # DEBUG LOG
                if raw_args_content:
                    # Regex to find comma-separated arguments, respecting quotes.
                    # Matches: a double-quoted string (allowing escaped quotes ""),
                    # OR a single-quoted string (allowing escaped quotes ''),
                    # OR any sequence of characters not containing a comma.
                    # This is applied to the content *between* the filter parentheses.
                    # arg_pattern = re.compile(r'\s*("(?:\\"|[^\\"])*"|'(?:\\'|[^\\'])*'|[^,\s][^,]*[^,\s]|[^\n,\s])\s*')
                    
                    # We want to split by comma, but not commas inside quotes.
                    # A direct split is hard. Instead, find all valid arguments.
                    # The regex above is designed to capture one valid argument at a time.
                    # However, findall with that regex will give tuples if capturing groups are used.
                    # A better approach for splitting CSV-like strings is often iterative or using a dedicated parser.

                    # Let's try a simpler split approach for now, assuming ast.literal_eval can handle the parts.
                    # This is a known tricky problem. A full robust CSV parser is complex.
                    # For now, we'll assume arguments are simple enough that splitting by comma
                    # and then stripping whitespace from each part before ast.literal_eval might work
                    # for many common cases, especially if arguments don't contain literal commas.
                    # If an argument is supposed to be a string literal containing a comma, it MUST be quoted.
                    # E.g., filter('arg1', "string, with comma", 'arg3')

                    # Attempt 1: Simplistic split by comma, then strip and eval.
                    # This will FAIL if string literals themselves contain unquoted commas meant to be part of the string.
                    potential_args_str = raw_args_content.split(',')
                    arg_matches = [s.strip() for s in potential_args_str]

                    logger.debug(f"_parse_filters: Filter '{filter_spec['name']}', (simplified split) arg_matches: {arg_matches}") # DEBUG LOG
                    
                    parsed_args = []
                    for i, arg_str in enumerate(arg_matches):
                        arg_str = arg_str.strip()
                        logger.debug(f"_parse_filters: Filter '{filter_spec['name']}', pre-eval arg {i}: '{arg_str}'") # DEBUG LOG
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
        logger.debug(f"_get_value_from_path: Attempting to get path '{path}' from context with keys: {list(context.keys()) if isinstance(context, dict) else 'Not a dict'}. Context: {str(context)[:500]}...")
        """Retrieves a value from a nested dictionary using a dot-separated path."""
        if not path: # Handle cases where path might be empty (e.g. {{ | default('foo') }})
            return None
            
        keys = path.split('.')
        value = context
        for key_idx, key in enumerate(keys):
            if path == "raw_user_query" and key == "raw_user_query":
                logger.debug(f"_get_value_from_path: SPECIAL CHECK for path='{path}', key='{key}'. Context type: {type(value)}. Key in context: {'raw_user_query' in value if isinstance(value, dict) else 'N/A'}. Value of context['{key}']: {value.get(key) if isinstance(value, dict) else 'N/A'}")
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
        filepath = os.path.join(self.workflows_dir, os.path.basename(workflow_name))

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
                if "action" not in task_data:
                    raise ValueError(f"Task '{task_id}' is missing required 'action'.")

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

    def _resolve_value(self, value: Any, runtime_context: Dict[str, Any], initial_context: Dict[str, Any], task_key: Optional[str] = None) -> Any:
        """
        Resolves a value that might be a template string, a direct value, or a nested structure.
        Handles template syntax {{ placeholder | filter1 | filter2(arg) | default(\"fallback\") }}.
        Recursively resolves values if the input value is a dictionary or a list.
        Uses initial_context for 'context.' prefixed paths, runtime_context otherwise.
        """
        original_template_for_logging = str(value)

        if isinstance(value, dict):
            resolved_dict = {}
            for k, v_item in value.items(): # Changed v to v_item to avoid conflict
                resolved_dict[k] = self._resolve_value(v_item, runtime_context, initial_context, task_key)
            return resolved_dict
        elif isinstance(value, list):
            resolved_list = []
            for item in value:
                resolved_list.append(self._resolve_value(item, runtime_context, initial_context, task_key))
            return resolved_list
        elif not isinstance(value, str) or not ("{{" in value and "}}" in value):
            return value

        logger.debug(f"Resolving template string: {original_template_for_logging} with initial_context keys: {list(initial_context.keys()) if initial_context else []}")
        
        matches = re.findall(r"(\{\{(.*?)\}\})", value, re.DOTALL)
        if not matches: # Should not happen if "{{" and "}}" are present, but as a safeguard
            return value

        # Case 1: The entire template string is a single placeholder (e.g., "{{ my_variable }}")
        if len(matches) == 1 and value.strip() == matches[0][0]:
            full_match_tag, template_content = matches[0]
            template_content = template_content.strip()
            if not template_content: return "" # Handle empty braces {{}}

            var_path_str = self._extract_var_path(template_content)
            filters = self._parse_filters(template_content)
            
            default_value_from_filter = None
            has_default_filter = False
            default_filter_spec = next((f for f in filters if f['name'] == 'default'), None)
            if default_filter_spec:
                has_default_filter = True
                default_value_from_filter = default_filter_spec['args'][0] if default_filter_spec['args'] else None
                filters.remove(default_filter_spec) # Process default first, then remove

            resolved_var_from_context = None
            if var_path_str.startswith("context."):
                actual_path = var_path_str[len("context."):]
                logger.debug(f"Attempting to get value for path: '{actual_path}' from initial_context. Keys: {list(initial_context.keys()) if isinstance(initial_context, dict) else 'Not a dict'}. Initial context itself: {initial_context}")
                retrieved_value = self._get_value_from_path(actual_path, initial_context)
                resolved_var_from_context = retrieved_value
                logger.debug(f"Resolved (single) '{var_path_str}' to: {resolved_var_from_context} (from initial_context)")
            elif task_key and var_path_str == task_key:
                logger.warning(f"Template (single) '{value}' in task '{task_key}' references itself ('{var_path_str}').")
                resolved_var_from_context = runtime_context.get(task_key)
            else:
                resolved_var_from_context = self._get_value_from_path(var_path_str, runtime_context)
                logger.debug(f"Resolved (single) '{var_path_str}' to: {resolved_var_from_context} (from runtime_context)")

            current_value_for_placeholder = None
            if resolved_var_from_context is None and has_default_filter:
                current_value_for_placeholder = default_value_from_filter
            else:
                current_value_for_placeholder = resolved_var_from_context
            
            # Apply other filters
            for f_spec in filters: # default_filter_spec already removed
                if f_spec['name'] == 'toJson':
                    current_value_for_placeholder = json.dumps(current_value_for_placeholder)
                elif f_spec['name'] == 'replace':
                    if not isinstance(current_value_for_placeholder, str):
                        current_value_for_placeholder = str(current_value_for_placeholder)
                    if len(f_spec['args']) == 2:
                        old_val, new_val = str(f_spec['args'][0]), str(f_spec['args'][1])
                        current_value_for_placeholder = current_value_for_placeholder.replace(old_val, new_val)
                    else:
                        logger.warning(f"Task '{task_key}': Filter 'replace' expects 2 arguments (old, new), got {len(f_spec['args'])}. Skipping.")
                elif f_spec['name'] == 'trim':
                    current_value_for_placeholder = str(current_value_for_placeholder).strip()
                else:
                    logger.warning(f"Task '{task_key}': Unknown filter '{f_spec['name']}' in template '{original_template_for_logging}'. Skipping filter.")
            
            logger.debug(f"Resolved single placeholder '{value}' to: {str(current_value_for_placeholder)[:200]}")
            return current_value_for_placeholder

        # Case 2: The template string has one or more embedded placeholders (e.g., "Value is {{my_var}} and {{another.path}}")
        else:
            processed_template_string = value
            for full_match_tag, template_content_inner in matches:
                template_content_inner = template_content_inner.strip()
                
                resolved_placeholder_value_after_filters = None # Initialize
                if not template_content_inner: # Handle {{}}
                    resolved_placeholder_value_after_filters = ""
                else:
                    var_path_str_inner = self._extract_var_path(template_content_inner)
                    filters_inner = self._parse_filters(template_content_inner)
                    
                    default_value_from_filter_inner = None
                    has_default_filter_inner = False
                    default_filter_spec_inner = next((f for f in filters_inner if f['name'] == 'default'), None)
                    if default_filter_spec_inner:
                        has_default_filter_inner = True
                        default_value_from_filter_inner = default_filter_spec_inner['args'][0] if default_filter_spec_inner['args'] else None
                        filters_inner.remove(default_filter_spec_inner)

                    resolved_var_from_context_inner = None
                    if var_path_str_inner.startswith("context."):
                        actual_path_inner = var_path_str_inner[len("context."):]
                        logger.debug(f"Attempting to get value for path: '{actual_path_inner}' from initial_context. Keys: {list(initial_context.keys()) if isinstance(initial_context, dict) else 'Not a dict'}. Initial context itself: {initial_context}")
                        retrieved_value = self._get_value_from_path(actual_path_inner, initial_context)
                        resolved_var_from_context_inner = retrieved_value
                        logger.debug(f"Resolved (embedded) '{var_path_str_inner}' to: {resolved_var_from_context_inner} (from initial_context)")
                    elif task_key and var_path_str_inner == task_key:
                        logger.warning(f"Template (embedded) '{value}' in task '{task_key}' references itself ('{var_path_str_inner}').")
                        resolved_var_from_context_inner = runtime_context.get(task_key)
                    else:
                        resolved_var_from_context_inner = self._get_value_from_path(var_path_str_inner, runtime_context)
                        logger.debug(f"Resolved (embedded) '{var_path_str_inner}' to: {resolved_var_from_context_inner} (from runtime_context)")
                    
                    current_value_for_placeholder_inner = None
                    if resolved_var_from_context_inner is None and has_default_filter_inner:
                        current_value_for_placeholder_inner = default_value_from_filter_inner
                    else:
                        current_value_for_placeholder_inner = resolved_var_from_context_inner

                    # Apply other filters to current_value_for_placeholder_inner
                    for f_spec_inner in filters_inner:
                        if f_spec_inner['name'] == 'toJson':
                            current_value_for_placeholder_inner = json.dumps(current_value_for_placeholder_inner)
                        elif f_spec_inner['name'] == 'replace':
                            if not isinstance(current_value_for_placeholder_inner, str):
                                current_value_for_placeholder_inner = str(current_value_for_placeholder_inner)
                            if len(f_spec_inner['args']) == 2:
                                old_val_inner, new_val_inner = str(f_spec_inner['args'][0]), str(f_spec_inner['args'][1])
                                current_value_for_placeholder_inner = current_value_for_placeholder_inner.replace(old_val_inner, new_val_inner)
                            else:
                                logger.warning(f"Task '{task_key}': Filter 'replace' expects 2 arguments (old, new), got {len(f_spec_inner['args'])}. Skipping.")
                        elif f_spec_inner['name'] == 'trim':
                            current_value_for_placeholder_inner = str(current_value_for_placeholder_inner).strip()
                        else:
                            logger.warning(f"Task '{task_key}': Unknown filter '{f_spec_inner['name']}' in template '{original_template_for_logging}'. Skipping filter.")
                    resolved_placeholder_value_after_filters = current_value_for_placeholder_inner

                # Convert the resolved placeholder value to string for embedding
                string_to_insert = ""
                if isinstance(resolved_placeholder_value_after_filters, str):
                    string_to_insert = resolved_placeholder_value_after_filters
                elif isinstance(resolved_placeholder_value_after_filters, (list, dict, tuple)):
                    string_to_insert = json.dumps(resolved_placeholder_value_after_filters)
                elif isinstance(resolved_placeholder_value_after_filters, bool):
                    string_to_insert = str(resolved_placeholder_value_after_filters).lower()
                elif resolved_placeholder_value_after_filters is None:
                    string_to_insert = "null" # Or "" or "None" depending on context, "null" seems reasonable.
                else: # numbers, etc.
                    string_to_insert = str(resolved_placeholder_value_after_filters)
                
                processed_template_string = processed_template_string.replace(full_match_tag, string_to_insert)
            
            logger.debug(f"Resolved embedded template '{original_template_for_logging}' to: {processed_template_string[:200]}")
            return processed_template_string

    def _resolve_inputs(self, inputs: Optional[Dict[str, Any]], runtime_context: Dict[str, Any], initial_context: Dict[str, Any], task_key: Optional[str] = None) -> Dict[str, Any]:
        """Resolves all template strings within a task's input dictionary."""
        if inputs is None:
            return {}
        # Pass both contexts to _resolve_value
        return self._resolve_value(inputs, runtime_context, initial_context, task_key)

    def _evaluate_condition(self, condition_str: Optional[str], runtime_context: Dict[str, Any], initial_context: Dict[str, Any]) -> bool:
        """
        Evaluates a condition string (e.g., "{{ task_output.status }} == \"Success\"").
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

            # Regex for comparison: {{ var.path OP value }} (e.g., {{ task_A.reflection.confidence > 0.7 }})
            # Handle both formats: "{{ var.path }} OP value" and "{{ var.path OP value }}"
            comp_match = re.match(r"^{{\s*([\w\.\-]+)\s*(==|!=|>|<|>=|<=)\s*(.*?)\s*}}$", condition_str)
            if not comp_match:
                # Try the old format: {{ var.path }} OP value
                comp_match = re.match(r"^{{\s*([\w\.\-]+)\s*}}\s*(==|!=|>|<|>=|<=)\s*(.*)$", condition_str)
            
            if comp_match:
                var_path, operator, value_str = comp_match.groups()
                actual_value = self._resolve_value(f"{{{{ {var_path} }}}}", runtime_context, initial_context) # Resolve the variable
                expected_value = self._parse_condition_value(value_str) # Parse the literal value
                result = self._compare_values(actual_value, operator, expected_value)
                logger.debug(f"Condition '{condition_str}' evaluated to {result} (Actual: {repr(actual_value)}, Op: {operator}, Expected: {repr(expected_value)})")
                return result

            # Regex for membership: value IN/NOT IN {{ var.path }} (e.g., "Error" in {{task_B.reflection.potential_issues}})
            in_match = re.match(r"^(.+?)\s+(in|not in)\s+{{\s*([\w\.\-]+)\s*}}$", condition_str, re.IGNORECASE)
            if in_match:
                value_str, operator, var_path = in_match.groups()
                value_to_check = self._parse_condition_value(value_str.strip()) # Parse the literal value
                container = self._resolve_value(f"{{{{{{var_path}}}}}}", runtime_context) # Resolve the container
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
                actual_value = self._resolve_value(f"{{{{{{var_path}}}}}}", runtime_context)
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

    def _sanitize_for_json(self, data: Any) -> Any:
        """Recursively sanitizes data to ensure it's JSON serializable."""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        if isinstance(data, dict):
            return {str(k): self._sanitize_for_json(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._sanitize_for_json(v) for v in data]
        if hasattr(data, 'isoformat'): # Handle datetime objects
            return data.isoformat()
        # Fallback for other types (like numpy floats, etc.)
        return str(data)

    def run_workflow(self, workflow_name: str, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point to run a workflow.
        Initializes context, manages the task queue, and returns the final results.
        Now includes detailed event logging for each action.
        """
        try:
            workflow_definition = self.load_workflow(workflow_name)
        except (FileNotFoundError, ValueError, TypeError) as e:
            logger.critical(f"Workflow execution failed during loading: {e}", exc_info=True)
            return self._summarize_run(workflow_name, "N/A", "Failed", 0, {}, {}, str(e))

        run_id = initial_context.get("workflow_run_id", f"run_{uuid.uuid4().hex}")
        initial_context["workflow_run_id"] = run_id
        
        event_log = []
        runtime_context = {
                "initial_context": initial_context,
            "workflow_run_id": run_id,
            "workflow_definition": workflow_definition,
        }
        
        tasks = workflow_definition.get('tasks', {})
        task_statuses = {key: "pending" for key in tasks}
        
        ready_tasks = {key for key, task in tasks.items() if not task.get('dependencies')}
        running_tasks = {}
        completed_tasks = set()
        
        logger.info(f"Starting workflow '{self.last_workflow_name}' (Run ID: {run_id}). Initial ready tasks: {list(ready_tasks)}")

        start_time = time.time()
        
        while ready_tasks or running_tasks:
            
            if not ready_tasks:
                if running_tasks:
                    time.sleep(0.1) 
                    continue
                else:
                    break 

            task_key = ready_tasks.pop()
            task_info = tasks[task_key]
            action_type = task_info.get("action")
            
            attempt_count = 1 
            max_attempts = task_info.get('retries', 0) + 1
            
            condition = task_info.get('condition')
            if condition and not self._evaluate_condition(condition, runtime_context, initial_context):
                logger.info(f"Skipping task '{task_key}' due to unmet condition: {condition}")
                task_statuses[task_key] = "skipped"
                completed_tasks.add(task_key) # Treat as 'completed' for dependency checking
                # Check for newly ready tasks after skipping
                for next_task_key, next_task_info in tasks.items():
                    if next_task_key not in completed_tasks and next_task_key not in ready_tasks and next_task_key not in running_tasks:
                        dependencies = next_task_info.get('dependencies', [])
                        if all(dep in completed_tasks for dep in dependencies):
                            ready_tasks.add(next_task_key)
                continue

            running_tasks[task_key] = time.time()
            
            action_context_obj = ActionContext(
                task_key=task_key, action_name=task_key, action_type=action_type,
                workflow_name=self.last_workflow_name, run_id=run_id,
                attempt_number=attempt_count, max_attempts=max_attempts,
                execution_start_time=datetime.utcnow(),
                runtime_context=runtime_context
            )

            resolved_inputs = self._resolve_inputs(task_info.get('inputs'), runtime_context, initial_context, task_key)
            
            # Resolve and merge prompt_vars if they exist for the task
            prompt_vars = task_info.get('prompt_vars')
            if prompt_vars:
                resolved_prompt_vars = self._resolve_value(prompt_vars, runtime_context, initial_context, task_key)
                if isinstance(resolved_prompt_vars, dict) and isinstance(resolved_inputs, dict):
                    resolved_inputs['initial_context'] = {**resolved_inputs.get('initial_context', {}), **resolved_prompt_vars}

            result = execute_action(
                task_key=task_key, action_name=task_key, action_type=action_type,
                inputs=resolved_inputs, context_for_action=action_context_obj,
                max_attempts=max_attempts, attempt_number=attempt_count
            )
            
            task_duration = round(time.time() - running_tasks[task_key], 4)

            event_log.append({
                "timestamp": action_context_obj.execution_start_time.isoformat() + "Z",
                "run_id": run_id, "workflow_name": self.last_workflow_name, "task_key": task_key,
                "action_type": action_type, "attempt": attempt_count, "duration_sec": task_duration,
                "inputs": self._sanitize_for_json(resolved_inputs), 
                "result": self._sanitize_for_json(result)
            })

            del running_tasks[task_key]
            completed_tasks.add(task_key)
            runtime_context[task_key] = result
            
            is_success = "error" not in result or result.get("error") is None
            task_statuses[task_key] = "completed" if is_success else "failed"
            
            if is_success:
                for next_task_key, next_task_info in tasks.items():
                    if next_task_key not in completed_tasks and next_task_key not in ready_tasks and next_task_key not in running_tasks:
                        dependencies = next_task_info.get('dependencies', [])
                        if all(dep in completed_tasks for dep in dependencies):
                             ready_tasks.add(next_task_key)

        end_time = time.time()
        run_duration = round(end_time - start_time, 2)
        
        final_status = "Completed Successfully"
        if any(status == "failed" for status in task_statuses.values()):
            final_status = "Completed with Errors"
        elif len(completed_tasks) < len(tasks):
            final_status = "Stalled"
        
        logger.info(f"Workflow '{self.last_workflow_name}' finished in {run_duration}s with status: {final_status}")

        event_log_path = os.path.join(config.OUTPUT_DIR, f"run_events_{run_id}.jsonl")
        try:
            with open(event_log_path, 'w', encoding='utf-8') as f:
                for event in event_log:
                    f.write(json.dumps(event, default=str) + '\n')
            logger.info(f"Detailed event log saved to: {event_log_path}")
        except Exception as e:
            logger.error(f"Failed to save event log to {event_log_path}: {e}")

        final_results = self._summarize_run(
            workflow_name=self.last_workflow_name, run_id=run_id, status=final_status,
            duration=run_duration, task_statuses=task_statuses, runtime_context=runtime_context
        )
        return final_results

    def _summarize_run(self, workflow_name, run_id, status, duration, task_statuses, runtime_context, error=None):
        """Helper to create the final results dictionary."""
        summary = {
            "workflow_name": workflow_name,
            "workflow_run_id": run_id,
            "workflow_status": status,
            "workflow_run_duration_sec": duration,
            "task_statuses": task_statuses,
        }
        if error:
            summary["error"] = error
        
        # Add the rest of the runtime context, which includes task outputs
        summary.update(runtime_context)
        
        return summary

# --- END OF FILE 3.0ArchE/workflow_engine.py --- 

class IARCompliantWorkflowEngine(WorkflowEngine):
    """Enhanced workflow engine with complete IAR compliance vetting"""
    
    def __init__(self, spr_manager=None):
        super().__init__(spr_manager)
        self.iar_validator = IARValidator()
        self.resonance_tracker = ResonanceTracker()
        logger.info("IARCompliantWorkflowEngine initialized with full vetting capabilities")
    
    def execute_task(self, task_definition, context):
        """Execute task with mandatory IAR compliance validation"""
        
        # Pre-execution validation
        if not self.validate_task_iar_capability(task_definition):
            raise ValueError("Task must support IAR output structure")
        
        # Execute with IAR capture
        try:
            # Use parent class execution logic
            task_key = task_definition.get('id', 'unknown_task')
            action_type = task_definition.get('action')
            
            # Create action context
            action_context_obj = ActionContext(
                task_key=task_key,
                action_name=task_key,
                action_type=action_type,
                workflow_name=getattr(self, 'last_workflow_name', 'unknown'),
                run_id=context.get('workflow_run_id', 'unknown'),
                attempt_number=1,
                max_attempts=1,
                execution_start_time=datetime.utcnow(),
                runtime_context=context
            )
            
            # Resolve inputs using parent method
            resolved_inputs = self._resolve_inputs(
                task_definition.get('inputs'), 
                context, 
                context.get('initial_context', {}), 
                task_key
            )
            
            # Execute action
            from .action_registry import execute_action
            result = execute_action(
                task_key=task_key,
                action_name=task_key,
                action_type=action_type,
                inputs=resolved_inputs,
                context_for_action=action_context_obj,
                max_attempts=1,
                attempt_number=1
            )
            
            # Validate IAR structure
            reflection = result.get('reflection', {})
            is_valid, issues = self.iar_validator.validate_structure(reflection)
            
            if not is_valid:
                raise ValueError(f"Invalid IAR structure: {issues}")
            
            # Validate enhanced fields if present
            enhanced_valid, enhanced_issues = self.iar_validator.validate_enhanced_fields(reflection)
            if not enhanced_valid:
                logger.warning(f"Enhanced IAR field issues: {enhanced_issues}")
            
            # Track resonance metrics
            execution_record = self.resonance_tracker.record_execution(
                task_id=task_key,
                iar_data=reflection,
                context=context
            )
            
            # Add execution tracking to result
            result['execution_tracking'] = execution_record
            
            return result
            
        except Exception as e:
            return self.handle_error_with_iar(e, task_definition, context)
    
    def validate_task_iar_capability(self, task_definition):
        """Ensure task can return proper IAR structure"""
        required_fields = [
            'status', 'summary', 'confidence', 
            'alignment_check', 'potential_issues',
            'raw_output_preview'
        ]
        
        # Check if task definition includes expected IAR requirements
        output_structure = task_definition.get('output_structure', {})
        reflection_structure = output_structure.get('reflection', {})
        
        if not reflection_structure:
            # If not explicitly defined, assume compliance (legacy support)
            logger.debug(f"Task {task_definition.get('id')} has no explicit IAR structure definition - assuming compliance")
            return True
        
        # Validate task definition includes IAR requirements
        return all(
            field in reflection_structure
            for field in required_fields
        )
    
    def handle_error_with_iar(self, error, task_definition, context):
        """Handle errors with proper IAR structure"""
        return {
            "error": str(error),
            "reflection": {
                "status": "Failed",
                "summary": f"Task execution failed: {error}",
                "confidence": 0.0,
                "alignment_check": "Failed due to execution error",
                "potential_issues": [f"Execution error: {error}"],
                "raw_output_preview": None,
                "tactical_resonance": 0.0,
                "crystallization_potential": 0.0
            }
        }
    
    def get_resonance_dashboard(self):
        """Get comprehensive resonance and compliance dashboard"""
        resonance_report = self.resonance_tracker.get_resonance_report()
        
        return {
            "iar_compliance_status": "FULL_COMPLIANCE_ACTIVE",
            "resonance_metrics": resonance_report['current_metrics'],
            "resonance_trend": resonance_report['recent_trend'],
            "compliance_score": resonance_report['compliance_score'],
            "validator_status": "ACTIVE",
            "total_validations": len(self.resonance_tracker.execution_history),
            "last_updated": datetime.utcnow().isoformat()
        }
