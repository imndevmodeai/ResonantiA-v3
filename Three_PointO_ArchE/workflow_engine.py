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
from typing import Dict, Any, List, Optional, Set, Union, Tuple, Callable # Expanded type hints
# Use relative imports within the package
from . import config
from .action_registry import execute_action, ACTION_REGISTRY, register_action # Imports the function that calls specific tools and centralized registry
from .spr_manager import SPRManager # May be used for SPR-related context or validation
from .error_handler import handle_action_error, DEFAULT_ERROR_STRATEGY, DEFAULT_RETRY_ATTEMPTS # Imports error handling logic
from .action_context import ActionContext # Import from new file
import ast
from datetime import datetime # Added import
from .workflow_recovery import WorkflowRecoveryHandler
from .recovery_actions import (
    analyze_failure,
    fix_template,
    fix_action,
    validate_workflow,
    validate_action
)
from .tools import display_output
from .system_genesis_tool import perform_system_genesis_action

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

class IARCompliantWorkflowEngine:
    """Enhanced workflow engine with IAR compliance and recovery support."""
    
    def __init__(self, workflows_dir: str = "workflows", spr_manager = None):
        self.workflows_dir = workflows_dir
        self.spr_manager = spr_manager
        self.last_workflow_name = None
        self.action_registry = ACTION_REGISTRY.copy()  # Use centralized registry
        self.recovery_handler = None
        self.current_run_id = None
        self.current_workflow = None
        self.iar_validator = IARValidator()
        self.resonance_tracker = ResonanceTracker()
        
        # Register standard actions
        self.register_action("display_output", display_output)
        self.register_action("perform_system_genesis_action", perform_system_genesis_action)
        
        # Register recovery actions
        self.register_recovery_actions()
        logger.info("IARCompliantWorkflowEngine initialized with full vetting capabilities")

    def register_action(self, action_type: str, action_func: Callable) -> None:
        """Register an action function with the engine."""
        register_action(action_type, action_func, force=True)  # Use centralized registration
        self.action_registry = ACTION_REGISTRY.copy()  # Update local copy
        logger.debug(f"Registered action: {action_type}")

    def register_recovery_actions(self) -> None:
        """Register recovery-related actions."""
        self.register_action("analyze_failure", analyze_failure)
        self.register_action("fix_template", fix_template)
        self.register_action("fix_action", fix_action)
        self.register_action("validate_workflow", validate_workflow)
        self.register_action("validate_action", validate_action)

    def _execute_task(self, task: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task with proper action type handling."""
        action_type = task.get("action_type")
        if not action_type:
            raise ValueError("Task must specify action_type")
        
        if action_type not in self.action_registry:
            raise ValueError(f"Unknown action type: {action_type}")
        
        action_func = self.action_registry[action_type]
        inputs = self._resolve_template_variables(task.get("inputs", {}), results)
        
        try:
            result = action_func(inputs)
            if not isinstance(result, dict):
                result = {"output": result}
            return result
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            raise

    def _resolve_template_variables(self, inputs: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve template variables in task inputs."""
        resolved = {}
        for key, value in inputs.items():
            if isinstance(value, str) and "{{" in value and "}}" in value:
                # Extract task and field from template
                template = value.strip("{} ")
                parts = template.split(".", 1)
                if len(parts) == 2:
                    task_id, field_path = parts
                else:
                    task_id, field_path = parts[0], ""
                # Support nested field resolution (e.g., result.patterns)
                if task_id in results:
                    field_value = results[task_id]
                    if field_path:
                        for subfield in field_path.split('.'):
                            if isinstance(field_value, dict) and subfield in field_value:
                                field_value = field_value[subfield]
                            else:
                                field_value = None
                                break
                    resolved[key] = field_value
                else:
                    resolved[key] = value
            else:
                resolved[key] = value
        return resolved

    def get_resonance_dashboard(self) -> Dict[str, Any]:
        """Get the current resonance dashboard."""
        return {
            "run_id": self.current_run_id,
            "workflow": self.last_workflow_name,
            "resonance_report": self.resonance_tracker.get_resonance_report(),
            "iar_validation": self.iar_validator.get_validation_status() if hasattr(self.iar_validator, 'get_validation_status') else None
        }

    def load_workflow(self, workflow_path: str) -> Dict[str, Any]:
        """Load workflow definition from file."""
        try:
            logger.info(f"Attempting to load workflow definition from: {workflow_path}")
            with open(workflow_path, 'r') as f:
                workflow = json.load(f)
            
            # Validate workflow structure
            if "tasks" not in workflow:
                raise ValueError("Workflow must contain 'tasks' section")
            
            # Validate each task
            for task_id, task in workflow["tasks"].items():
                if "action_type" not in task:
                    raise ValueError(f"Task '{task_id}' is missing required 'action_type'")
                if "description" not in task:
                    raise ValueError(f"Task '{task_id}' is missing required 'description'")
                if "inputs" not in task:
                    raise ValueError(f"Task '{task_id}' is missing required 'inputs'")
                
                # Verify action is registered
                action_type = task["action_type"]
                if action_type not in self.action_registry:
                    raise ValueError(f"Action type '{action_type}' is not registered in the engine")
            
            self.last_workflow_name = workflow.get("name", "Unnamed Workflow")
            return workflow
            
        except Exception as e:
            logger.error(f"Unexpected error loading workflow file {workflow_path}: {str(e)}")
            raise

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
            action_type = task_info.get("action_type")
            
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

    def execute_workflow(self, workflow_path: str, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a workflow with recovery support."""
        try:
            logger.info("Executing workflow with recovery support...")
            
            # Load workflow
            workflow = self.load_workflow(workflow_path)
            self.current_workflow = workflow
            self.current_run_id = str(uuid.uuid4())
            
            # Initialize recovery handler
            self.recovery_handler = WorkflowRecoveryHandler(workflow, self.current_run_id)
            
            # Initialize context
            initial_context = initial_context or {}
            runtime_context = {}
            
            # Execute tasks
            results = {}
            iar_failures = []  # Track IAR insights during execution
            
            for task_id, task in workflow["tasks"].items():
                try:
                    # Execute task
                    task_result = self._execute_task(task, results)
                    
                    # Validate IAR structure
                    is_valid, issues = self.iar_validator.validate_structure(task_result.get("reflection", {}))
                    if not is_valid:
                        iar_failures.append({
                            "task_id": task_id,
                            "issues": issues
                        })
                    
                    # Record execution for resonance tracking
                    self.resonance_tracker.record_execution(task_id, task_result.get("reflection", {}), runtime_context)
                    
                    # Store result
                    results[task_id] = task_result
                    runtime_context[task_id] = task_result
                    
                except Exception as e:
                    logger.error(f"Task {task_id} failed: {str(e)}")
                    
                    # Analyze failure
                    failure_context = {
                        "failed_task": task_id,
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    }
                    failure_analysis = self.recovery_handler.analyze_failure(failure_context)
                    
                    if failure_analysis.get("output", {}).get("status") == "recoverable":
                        # Append recovery flow
                        recovery_result = self.recovery_handler.append_recovery_flow(failure_analysis)
                        if recovery_result["output"]["status"] == "success":
                            workflow = recovery_result["output"]["modified_workflow"]
                            self.current_workflow = workflow
                            
                            # Retry task with recovery
                            task_result = self._execute_task(task, results)
                            results[task_id] = task_result
                            runtime_context[task_id] = task_result
                        else:
                            raise
                    else:
                        raise
            
            # Generate final report
            final_report = {
                "workflow_name": workflow.get("name", "Unnamed Workflow"),
                "run_id": self.current_run_id,
                "status": "Success",
                "results": results,
                "iar_failures": iar_failures,
                "resonance_report": self.resonance_tracker.get_resonance_report()
            }
            
            return final_report
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            raise

# --- END OF FILE 3.0ArchE/workflow_engine.py --- 
