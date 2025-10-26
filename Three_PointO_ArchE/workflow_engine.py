# ResonantiA Protocol v3.0 - workflow_engine.py
# Orchestrates the execution of defined workflows (Process Blueprints).
# Manages context, dependencies, conditions, action execution, and error handling.
# Critically handles Integrated Action Reflection (IAR) results by storing
# the complete action output dictionary (including 'reflection') in the
# context.

import json
import os
import logging
import copy
import time
import re
import uuid
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Union, Tuple, Callable

# --- Standardized Imports ---
# This single block ensures robust relative imports within the package.
try:
    from . import config
    from .action_registry import execute_action, main_action_registry
    from .spr_manager import SPRManager
    from .error_handler import handle_action_error
    from .action_context import ActionContext
    from .workflow_recovery import WorkflowRecoveryHandler
    from .recovery_actions import (
        analyze_failure,
        fix_template,
        fix_action,
        validate_workflow,
        validate_action,
        self_heal_output
    )
    from .system_genesis_tool import perform_system_genesis_action
    from .qa_tools import run_code_linter, run_workflow_suite
    from .output_handler import print_tagged_execution, print_tagged_results, display_output
    from .custom_json import dumps
    from .workflow_optimizer import WorkflowOptimizer
    from .thought_trail import log_to_thought_trail
except ImportError as e:
    # This block should ideally not be hit if run as part of the package,
    # but serves as a fallback and clear error indicator.
    import logging
    logging.getLogger(__name__).critical(f"A critical relative import failed in workflow_engine: {e}", exc_info=True)
    # Define dummy fallbacks to prevent outright crashing where possible
    def execute_action(*args, **kwargs): return {"error": f"Action Registry not available due to import error: {e}"}
    # Add other necessary fallbacks here as needed...
    class SPRManager: pass

import ast
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now, now_iso, ago, from_now, format_log, format_filename


# Attempt to import numpy for numeric type checking in _compare_values,
# optional
try:
    import numpy as np
except ImportError:
    np = None  # Set to None if numpy is not available
    logging.info(
        "Numpy not found, some numeric type checks in _compare_values might be limited.")

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
            issues.extend(
                [f"Missing required field: {field}" for field in missing_fields])
        
        # Validate confidence is float between 0-1
        confidence = iar_data.get('confidence')
        if confidence is not None:
            if not isinstance(
    confidence, (int, float)) or not (
        0.0 <= confidence <= 1.0):
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
                if not isinstance(
    value, (int, float)) or not (
        0.0 <= value <= 1.0):
                    enhanced_issues.append(
    f"{field} must be float between 0.0 and 1.0")
        
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
            'timestamp': now_iso(),
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
        
        # Last 100 executions
        recent_executions = self.execution_history[-100:]

        tactical_scores = [ex.get('tactical_resonance', 0.0)
                                  for ex in recent_executions]
        crystallization_scores = [
    ex.get(
        'crystallization_potential',
         0.0) for ex in recent_executions]
        
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
        
        recent_avg = sum(ex.get('tactical_resonance', 0.0)
                         for ex in recent_10) / 10
        older_avg = sum(ex.get('tactical_resonance', 0.0)
                        for ex in older_10) / 10
        
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
        successful_executions = [
    ex for ex in recent_executions if ex.get('status') == 'Success']
        
        success_rate = len(successful_executions) / len(recent_executions)
        avg_confidence = sum(ex.get('confidence', 0.0)
                             for ex in successful_executions) / max(len(successful_executions), 1)
        avg_resonance = self.resonance_metrics['avg_tactical_resonance']
        
        # Weighted compliance score
        compliance_score = (success_rate * 0.4) + \
                            (avg_confidence * 0.3) + (avg_resonance * 0.3)
        return min(compliance_score, 1.0)

# === Session State Manager ===
try:
    from .session_state_manager import load_session_state, save_session_state, append_fact
    from .context_superposition import create_context_bundle, merge_bundles
    from .prefetch_manager import trigger_predictive_prefetch
    from .sirc_autonomy import maybe_autorun_sirc
    from .causal_digest import build_flux_annotated_digest
except Exception:
    # Fallback no-ops if module not available
    def load_session_state():
        return {"facts_ledger": [], "updated_at": now_iso()}
    def save_session_state(state):
        return None
    def append_fact(state, fact):
        state.setdefault("facts_ledger", []).append({**fact, "ts": now_iso()})
    def create_context_bundle(spr_def, runtime_context, initial_context):
        return {"spr_id": spr_def.get("spr_id"), "created_at": now_iso()}
    def merge_bundles(bundles):
        return {"spr_index": [b.get("spr_id") for b in bundles]}


def _execute_standalone_workflow(workflow_definition: Dict[str, Any], initial_context: Dict[str, Any], parent_run_id: str, action_registry: Dict[str, Callable]) -> Dict[str, Any]:
    """
    Executes a workflow definition in-memory, for use by meta-actions like for_each.
    This is a simplified version of the main run_workflow loop, moved outside the class
    to prevent circular dependencies.
    """
    run_id = f"{parent_run_id}_sub_{uuid.uuid4().hex[:8]}"
    initial_context["workflow_run_id"] = run_id
    
    runtime_context = {
        "initial_context": initial_context,
        "workflow_run_id": run_id,
        "workflow_definition": workflow_definition,
    }
    
    tasks = workflow_definition.get('tasks', {})
    task_statuses = {key: "pending" for key in tasks}
    
    sorted_tasks = list(tasks.keys()) 

    logger.info(f"Starting standalone sub-workflow (Run ID: {run_id}).")
    start_time = time.time()

    for task_key in sorted_tasks:
        task_info = tasks[task_key]
        action_type = task_info.get("action_type")
        
        # This is a critical simplification: we can't use the full resolver here
        # without re-introducing the dependency. We'll manually resolve for now.
        resolved_inputs = {}
        for k, v in task_info.get('inputs', {}).items():
            if isinstance(v, str) and v == "{{ item }}":
                resolved_inputs[k] = initial_context.get('item')
            else:
                resolved_inputs[k] = v

        action_func = action_registry.get(action_type)
        if not action_func:
            error_result = {"error": f"Sub-workflow failed: Action type '{action_type}' not found."}
            runtime_context[task_key] = self._ensure_iar_compliance(error_result, action_context_obj)
            task_statuses[task_key] = "failed"
            break

        try:
            # The arguments must be passed as keyword arguments
            # to align with the action wrappers in action_registry.py
            result = action_func(**resolved_inputs)
            if not isinstance(result, dict):
                result = {"output": result}
            runtime_context[task_key] = self._ensure_iar_compliance(result, action_context_obj)
            task_statuses[task_key] = "completed"
        except Exception as e:
            error_msg = f"Sub-workflow task '{task_key}' failed: {e}"
            logger.error(error_msg, exc_info=True)
            error_result = {"error": error_msg}
            runtime_context[task_key] = self._ensure_iar_compliance(error_result, action_context_obj)
            task_statuses[task_key] = "failed"
            break

    end_time = time.time()
    run_duration = round(end_time - start_time, 2)
    
    final_status = "Completed" if all(s == "completed" for s in task_statuses.values()) else "Failed"
    
    # Can't call _summarize_run directly, so construct a simplified summary
    return {
        "workflow_name": workflow_definition.get("name", "sub-workflow"),
        "run_id": run_id,
        "status": final_status,
        "duration": run_duration,
        "task_statuses": task_statuses,
        "results": runtime_context
    }


class IARCompliantWorkflowEngine:
    """Enhanced workflow engine with IAR compliance and recovery support."""

    def __init__(self, workflows_dir: str = "workflows", spr_manager=None, event_callback: Optional[Callable] = None):
        self.workflows_dir = workflows_dir
        self.spr_manager = spr_manager
        self.event_callback = event_callback  # <-- ADDED
        self.last_workflow_name = None
        self.action_registry = main_action_registry.actions.copy()  # Use centralized registry
        self.recovery_handler = None
        self.current_run_id = None
        self.current_workflow = None
        self.iar_validator = IARValidator()
        self.resonance_tracker = ResonanceTracker()

        # Register standard actions
        self.register_action("display_output", display_output)
        self.register_action("perform_system_genesis_action",
     perform_system_genesis_action)
        self.register_action("run_code_linter", run_code_linter)
        self.register_action("run_workflow_suite", run_workflow_suite)

        # Register recovery actions
        self.register_recovery_actions()
        logger.info(
            "IARCompliantWorkflowEngine initialized with full vetting capabilities")

    @log_to_thought_trail
    def register_action(self, action_type: str, action_func: Callable) -> None:
        """Register an action function with the engine."""
        main_action_registry.register_action(
            action_type,
            action_func,
        )
        self.action_registry = main_action_registry.actions.copy()  # Update local copy
        logger.debug(f"Registered action: {action_type}")

    def register_recovery_actions(self) -> None:
        """Register recovery-related actions."""
        self.register_action("analyze_failure", analyze_failure)
        self.register_action("fix_template", fix_template)
        self.register_action("fix_action", fix_action)
        self.register_action("validate_workflow", validate_workflow)
        self.register_action("validate_action", validate_action)
        self.register_action("self_heal_output", self_heal_output)
        # Register the new for_each meta-action
        self.register_action("for_each", self._execute_for_each_task_wrapper)

    def _execute_for_each_task_wrapper(self, inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Wrapper for for_each action that can be called from action registry.
        Creates a minimal ActionContext for the actual implementation.
        """
        # Create a minimal ActionContext for the for_each implementation
        context_for_action = ActionContext(
            workflow_name="for_each_wrapper",
            task_name="for_each",
            runtime_context=kwargs.get('runtime_context', {}),
            initial_context=kwargs.get('initial_context', {})
        )
        return self._execute_for_each_task(inputs, context_for_action)

    def _execute_for_each_task(self, inputs: Dict[str, Any], context_for_action: ActionContext) -> Dict[str, Any]:
        """
        Executes a sub-workflow for each item in a list.
        This is a meta-action handled directly by the engine.
        """
        logger.info(f"Executing for_each task in workflow '{context_for_action.workflow_name}'")
        
        items_list = inputs.get('items')
        sub_workflow_def = inputs.get('workflow')

        if not isinstance(items_list, list):
            return {"error": f"Input 'items' for for_each must be a list, but got {type(items_list)}."}
        if not isinstance(sub_workflow_def, dict) or 'tasks' not in sub_workflow_def:
            return {"error": "Input 'workflow' for for_each must be a valid workflow definition with a 'tasks' section."}

        all_results = []
        
        for index, item in enumerate(items_list):
            logger.info(f"Executing for_each iteration {index + 1}/{len(items_list)}.")
            
            # The initial context for the sub-workflow includes the main context
            # plus the current item.
            sub_initial_context = copy.deepcopy(context_for_action.runtime_context.get('initial_context', {}))
            sub_initial_context['item'] = item
            sub_initial_context['loop_index'] = index
            
            # Run the sub-workflow directly without creating a new engine instance
            sub_workflow_result = _execute_standalone_workflow(
                workflow_definition=sub_workflow_def,
                initial_context=sub_initial_context,
                parent_run_id=context_for_action.run_id,
                action_registry=self.action_registry
            )
            all_results.append(sub_workflow_result)
        
        logger.info("Completed all for_each iterations.")
        return {"results": all_results}
    
    @log_to_thought_trail
    def _execute_task(self, task: Dict[str, Any],
                      results: Dict[str, Any], initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a single task with proper action type handling."""
        action_type = task.get("action_type")
        if not action_type:
            raise ValueError("Task must specify action_type")

        if action_type not in self.action_registry:
            raise ValueError(f"Unknown action type: {action_type}")

        action_func = self.action_registry[action_type]
        # Use the robust resolver that supports embedded placeholders and context paths
        resolved_inputs = self._resolve_inputs(
            task.get('inputs'),
            results,  # runtime_context
            initial_context,
            task_key
        )

        try:
            result = action_func(**resolved_inputs)
            if not isinstance(result, dict):
                result = {"output": result}
            return result
        except Exception as e:
            error_msg = f"Task '{task.get('description', 'Unknown')}' failed: {str(e)}"
            logger.error(error_msg)
            
            # Enhanced error reporting with input validation
            if "Missing required input" in str(e):
                logger.error(f"Input validation failed for task. Provided inputs: {list(inputs.keys())}")
            elif "NoneType" in str(e):
                logger.error(f"Null value error - check if previous task outputs are properly formatted")
            
            raise ValueError(error_msg)

    def _resolve_template_variables(self, inputs: Dict[str, Any], results: Dict[str, Any], initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Resolve template variables in task inputs."""
        resolved = {}
        initial_context = initial_context or {}
        for key, value in inputs.items():
            if isinstance(value, str) and "{{" in value and "}}" in value:
                # Extract task and field from template
                template = value.strip("{} ")
                
                # NEW: Add support for a default filter
                default_value = None
                if "|" in template:
                    parts = template.split("|", 1)
                    template = parts[0].strip()
                    filter_part = parts[1].strip()
                    if filter_part.startswith("default("):
                        default_value = filter_part[len("default("):-1].strip()
                        # Basic handling for quotes
                        if default_value.startswith(("'", '"')) and default_value.endswith(("'", '"')):
                            default_value = default_value[1:-1]

                parts = template.split(".", 1)
                
                # NEW: Add support for initial_context via `context.` prefix
                if parts[0] == 'context':
                    context_key = parts[1] if len(parts) > 1 else None
                    if context_key and context_key in initial_context:
                        resolved[key] = initial_context[context_key]
                    else:
                        resolved[key] = default_value if default_value is not None else value
                    continue

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
                    if field_value is not None:
                        resolved[key] = field_value
                    else:
                        resolved[key] = default_value if default_value is not None else value
                else:
                    resolved[key] = default_value if default_value is not None else value
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

    @log_to_thought_trail
    def load_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Load workflow definition from file."""
        # Ensure the workflow path is absolute by joining with the engine's workflows_dir
        if not os.path.isabs(workflow_name):
            # Dynamic path resolution - check multiple possible locations
            engine_dir = os.path.dirname(os.path.abspath(__file__))
            possible_paths = [
                workflow_name,  # Direct path
                os.path.join(self.workflows_dir, os.path.basename(workflow_name)),  # In workflows dir
                os.path.join(engine_dir, "workflows", os.path.basename(workflow_name)), # Relative to the engine
                os.path.join(os.path.dirname(engine_dir), os.path.basename(workflow_name)),  # Project root
                os.path.join(os.getcwd(), os.path.basename(workflow_name))  # Current working directory
            ]
            
            workflow_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    workflow_path = path
                    break
            
            if workflow_path is None:
                raise FileNotFoundError(f"Workflow file not found. Searched: {possible_paths}")
        else:
            workflow_path = workflow_name

        try:
            logger.info(f"Attempting to load workflow definition from: {workflow_path}")
            with open(workflow_path, 'r') as f:
                workflow = json.load(f)

            # Validate workflow structure
            if "tasks" not in workflow:
                raise ValueError("Workflow must contain 'tasks' section")
            
            # Ensure workflow has a proper name
            if "name" not in workflow and "workflow_name" not in workflow:
                workflow["name"] = f"Unnamed Workflow ({os.path.basename(workflow_path)})"
            elif "name" not in workflow and "workflow_name" in workflow:
                workflow["name"] = workflow["workflow_name"]

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

        except FileNotFoundError:
            logger.error(f"Workflow file not found at the specified path: {workflow_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from workflow file {workflow_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading workflow file {workflow_path}: {str(e)}")
            raise

    def _extract_var_path(self, template_content: str) -> str:
        """Extracts the core variable path from a template string, ignoring filters."""
        # The variable path is the part before the first pipe '|'
        return template_content.split('|', 1)[0].strip()

    def _parse_filters(self, template_content: str) -> list:
        """Parses filter syntax (e.g., | filter(arg1, 'arg2')) from a template string."""
        parts = template_content.split('|')[1:] # Get all parts after the variable path
        filters = []
        filter_regex = re.compile(r"^\s*(\w+)\s*(?:\((.*?)\))?\s*$") # Matches 'filter(args)' or 'filter'

        for part in parts:
            match = filter_regex.match(part)
            if match:
                name, args_str = match.groups()
                args = []
                if args_str:
                    # This is a simplified arg parser; it splits by comma and handles basic quotes
                    # A more robust solution might use shlex or a dedicated parsing library
                    try:
                        # Attempt to parse as a JSON list to handle quotes and types
                        args = json.loads(f'[{args_str}]')
                    except json.JSONDecodeError:
                        # Fallback for non-standard JSON arguments
                        args = [a.strip() for a in args_str.split(',')]
                filters.append({"name": name, "args": args})
        return filters

    def _get_value_from_path(self, path: str, context: Dict[str, Any]) -> Any:
        """Gets a value from a nested dictionary using a dot-separated path."""
        keys = path.split('.')
        value = context
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None # Path does not exist
        return value

    def _resolve_value(self,
    value: Any,
    runtime_context: Dict[str,
    Any],
    initial_context: Dict[str,
    Any],
     task_key: Optional[str] = None) -> Any:
        """
        Resolves a value that might be a template string, a direct value, or a nested structure.
        Handles template syntax {{ placeholder | filter1 | filter2(arg) | default(\"fallback\") }}.
        Recursively resolves values if the input value is a dictionary or a list.
        Uses initial_context for 'context.' prefixed paths, runtime_context otherwise.
        """
        original_template_for_logging = str(value)

        if isinstance(value, dict):
            resolved_dict = {}
            for k, v_item in value.items(
            ):  # Changed v to v_item to avoid conflict
                resolved_dict[k] = self._resolve_value(
    v_item, runtime_context, initial_context, task_key)
            return resolved_dict
        elif isinstance(value, list):
            resolved_list = []
            for item in value:
                resolved_list.append(
    self._resolve_value(
        item,
        runtime_context,
        initial_context,
         task_key))
            return resolved_list
        elif not isinstance(value, str) or not ("{{" in value and "}}" in value):
            return value

        logger.debug(
    f"Resolving template string: {original_template_for_logging} with initial_context keys: {
        list(
            initial_context.keys()) if initial_context else []}")
        
        matches = re.findall(r"(\{\{(.*?)\}\})", value, re.DOTALL)
        # Should not happen if "{{" and "}}" are present, but as a safeguard
        if not matches:
            return value

        # Case 1: The entire template string is a single placeholder (e.g., "{{
        # my_variable }}")
        if len(matches) == 1 and value.strip() == matches[0][0]:
            full_match_tag, template_content = matches[0]
            template_content = template_content.strip()
            if not template_content: return ""  # Handle empty braces {{}}

            var_path_str = self._extract_var_path(template_content)
            filters = self._parse_filters(template_content)
            
            default_value_from_filter = None
            has_default_filter = False
            default_filter_spec = next(
    (f for f in filters if f['name'] == 'default'), None)
            if default_filter_spec:
                has_default_filter = True
                default_value_from_filter = default_filter_spec[
                    'args'][0] if default_filter_spec['args'] else None
                # Process default first, then remove
                filters.remove(default_filter_spec)

            resolved_var_from_context = None
            if var_path_str.startswith("context."):
                actual_path = var_path_str[len("context."):]
                logger.debug(
    f"Attempting to get value for path: '{actual_path}' from initial_context. Keys: {
        list(
            initial_context.keys()) if isinstance(
                initial_context,
                 dict) else 'Not a dict'}. Initial context itself: {initial_context}")
                retrieved_value = self._get_value_from_path(
                    actual_path, initial_context)
                resolved_var_from_context = retrieved_value
                logger.debug(
    f"Resolved (single) '{var_path_str}' to: {resolved_var_from_context} (from initial_context)")
            elif task_key and var_path_str == task_key:
                logger.warning(
    f"Template (single) '{value}' in task '{task_key}' references itself ('{var_path_str}').")
                resolved_var_from_context = runtime_context.get(task_key)
            else:
                # Try runtime_context first
                resolved_var_from_context = self._get_value_from_path(
                    var_path_str, runtime_context)
                if resolved_var_from_context is None:
                    # Fallback: try initial_context using the same path
                    resolved_var_from_context = self._get_value_from_path(
                        var_path_str, initial_context)
                logger.debug(
    f"Resolved (single) '{var_path_str}' to: {resolved_var_from_context} (from runtime_context/initial_context)")

            current_value_for_placeholder = None
            if resolved_var_from_context is None and has_default_filter:
                current_value_for_placeholder = default_value_from_filter
            else:
                current_value_for_placeholder = resolved_var_from_context
            
            # Apply other filters
            for f_spec in filters:  # default_filter_spec already removed
                if f_spec['name'] == 'from_json':
                    try:
                        current_value_for_placeholder = json.loads(current_value_for_placeholder)
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"Task '{task_key}': Value for filter 'from_json' could not be parsed. Value: {current_value_for_placeholder}")
                        # Keep the value as is or set to a default error indicator? Let's keep it for now.
                elif f_spec['name'] == 'toJson':
                    current_value_for_placeholder = json.dumps(
                        current_value_for_placeholder)
                elif f_spec['name'] == 'replace':
                    if not isinstance(current_value_for_placeholder, str):
                        current_value_for_placeholder = str(
                            current_value_for_placeholder)
                    if len(f_spec['args']) == 2:
                        old_val, new_val = str(
    f_spec['args'][0]), str(
        f_spec['args'][1])
                        current_value_for_placeholder = current_value_for_placeholder.replace(
                            old_val, new_val)
                    else:
                        logger.warning(
    f"Task '{task_key}': Filter 'replace' expects 2 arguments (old, new), got {
        len(
            f_spec['args'])}. Skipping.")
                elif f_spec['name'] == 'trim':
                    current_value_for_placeholder = str(
                        current_value_for_placeholder).strip()
                else:
                    logger.warning(
    f"Task '{task_key}': Unknown filter '{
        f_spec['name']}' in template '{original_template_for_logging}'. Skipping filter.")
            
            logger.debug(
    f"Resolved single placeholder '{value}' to: {
        str(current_value_for_placeholder)[
            :200]}")
            return current_value_for_placeholder

        # Case 2: The template string has one or more embedded placeholders
        # (e.g., "Value is {{my_var}} and {{another.path}}")
        else:
            processed_template_string = value
            for full_match_tag, template_content_inner in matches:
                template_content_inner = template_content_inner.strip()
                
                resolved_placeholder_value_after_filters = None  # Initialize
                if not template_content_inner:  # Handle {{}}
                    resolved_placeholder_value_after_filters = ""
                else:
                    var_path_str_inner = self._extract_var_path(
                        template_content_inner)
                    filters_inner = self._parse_filters(template_content_inner)
                    
                    default_value_from_filter_inner = None
                    has_default_filter_inner = False
                    default_filter_spec_inner = next(
    (f for f in filters_inner if f['name'] == 'default'), None)
                    if default_filter_spec_inner:
                        has_default_filter_inner = True
                        default_value_from_filter_inner = default_filter_spec_inner[
                            'args'][0] if default_filter_spec_inner['args'] else None
                        filters_inner.remove(default_filter_spec_inner)

                    resolved_var_from_context_inner = None
                    if var_path_str_inner.startswith("context."):
                        actual_path_inner = var_path_str_inner[len(
                            "context."):]
                        logger.debug(
    f"Attempting to get value for path: '{actual_path_inner}' from initial_context. Keys: {
        list(
            initial_context.keys()) if isinstance(
                initial_context,
                 dict) else 'Not a dict'}. Initial context itself: {initial_context}")
                        retrieved_value = self._get_value_from_path(
                            actual_path_inner, initial_context)
                        resolved_var_from_context_inner = retrieved_value
                        logger.debug(
    f"Resolved (embedded) '{var_path_str_inner}' to: {resolved_var_from_context_inner} (from initial_context)")
                    elif task_key and var_path_str_inner == task_key:
                        logger.warning(
    f"Template (embedded) '{value}' in task '{task_key}' references itself ('{var_path_str_inner}').")
                        resolved_var_from_context_inner = runtime_context.get(
                            task_key)
                    else:
                        # Try runtime_context first
                        resolved_var_from_context_inner = self._get_value_from_path(
                            var_path_str_inner, runtime_context)
                        if resolved_var_from_context_inner is None:
                            # Fallback to initial_context if not found
                            resolved_var_from_context_inner = self._get_value_from_path(
                                var_path_str_inner, initial_context)
                        logger.debug(
    f"Resolved (embedded) '{var_path_str_inner}' to: {resolved_var_from_context_inner} (from runtime_context/initial_context)")
                    
                    current_value_for_placeholder_inner = None
                    if resolved_var_from_context_inner is None and has_default_filter_inner:
                        current_value_for_placeholder_inner = default_value_from_filter_inner
                    else:
                        current_value_for_placeholder_inner = resolved_var_from_context_inner

                    # Apply other filters to
                    # current_value_for_placeholder_inner
                    for f_spec_inner in filters_inner:
                        if f_spec_inner['name'] == 'from_json':
                            try:
                                current_value_for_placeholder_inner = json.loads(current_value_for_placeholder_inner)
                            except (json.JSONDecodeError, TypeError):
                                logger.warning(f"Task '{task_key}': Value for filter 'from_json' could not be parsed. Value: {current_value_for_placeholder_inner}")
                        elif f_spec_inner['name'] == 'toJson':
                            current_value_for_placeholder_inner = json.dumps(
                                current_value_for_placeholder_inner)
                        elif f_spec_inner['name'] == 'replace':
                            if not isinstance(
    current_value_for_placeholder_inner, str):
                                current_value_for_placeholder_inner = str(
                                    current_value_for_placeholder_inner)
                            if len(f_spec_inner['args']) == 2:
                                old_val_inner, new_val_inner = str(
    f_spec_inner['args'][0]), str(
        f_spec_inner['args'][1])
                                current_value_for_placeholder_inner = current_value_for_placeholder_inner.replace(
                                    old_val_inner, new_val_inner)
                            else:
                                logger.warning(
    f"Task '{task_key}': Filter 'replace' expects 2 arguments (old, new), got {
        len(
            f_spec_inner['args'])}. Skipping.")
                        elif f_spec_inner['name'] == 'trim':
                            current_value_for_placeholder_inner = str(
                                current_value_for_placeholder_inner).strip()
                        else:
                            logger.warning(
    f"Task '{task_key}': Unknown filter '{
        f_spec_inner['name']}' in template '{original_template_for_logging}'. Skipping filter.")
                    resolved_placeholder_value_after_filters = current_value_for_placeholder_inner

                # Convert the resolved placeholder value to string for
                # embedding
                string_to_insert = ""
                if isinstance(resolved_placeholder_value_after_filters, str):
                    string_to_insert = resolved_placeholder_value_after_filters
                elif isinstance(resolved_placeholder_value_after_filters, (list, dict, tuple)):
                    string_to_insert = json.dumps(
                        resolved_placeholder_value_after_filters)
                elif isinstance(resolved_placeholder_value_after_filters, bool):
                    string_to_insert = str(
                        resolved_placeholder_value_after_filters).lower()
                elif resolved_placeholder_value_after_filters is None:
                    # Or "" or "None" depending on context, "null" seems
                    # reasonable.
                    string_to_insert = "null"
                else:  # numbers, etc.
                    string_to_insert = str(
                        resolved_placeholder_value_after_filters)

                processed_template_string = processed_template_string.replace(
                    full_match_tag, string_to_insert)

            logger.debug(
                f"Resolved embedded template '{original_template_for_logging}' to: {processed_template_string[:200]}")
            return processed_template_string

    def _resolve_inputs(self,
    inputs: Optional[Dict[str,
    Any]],
    runtime_context: Dict[str,
    Any],
    initial_context: Dict[str,
    Any],
    task_key: Optional[str] = None) -> Dict[str,
     Any]:
        """Resolves all template strings within a task's input dictionary."""
        if inputs is None:
            return {}
        # Pass both contexts to _resolve_value
        return self._resolve_value(
    inputs,
    runtime_context,
    initial_context,
     task_key)

    def _evaluate_condition(self,
    condition_str: Optional[str],
    runtime_context: Dict[str,
    Any],
    initial_context: Dict[str,
     Any]) -> bool:
        """
        Evaluates a condition string (e.g., "{{ task_output.status }} == \"Success\"").
        Supports basic comparisons (==, !=, >, <, >=, <=), truthiness checks,
        and membership checks (in, not in) on resolved context variables,
        including accessing IAR reflection data (e.g., {{task_A.reflection.confidence}}).
        Returns True if condition is met or if condition_str is empty/None.
        """
        if not condition_str or not isinstance(condition_str, str):
            return True  # No condition means execute
        condition_str = condition_str.strip()
        logger.debug(f"Evaluating condition: '{condition_str}'")

        try:
            # Simple true/false literals
            condition_lower = condition_str.lower()
            if condition_lower == 'true': return True
            if condition_lower == 'false': return False

            # Regex for comparison: {{ var.path OP value }} (e.g., {{ task_A.reflection.confidence > 0.7 }})
            # Handle both formats: "{{ var.path }} OP value" and "{{ var.path
            # OP value }}"
            comp_match = re.match(
    r"^{{\s*([\w\.\-]+)\s*(==|!=|>|<|>=|<=)\s*(.*?)\s*}}$",
     condition_str)
            if not comp_match:
                # Try the old format: {{ var.path }} OP value
                comp_match = re.match(
    r"^{{\s*([\w\.\-]+)\s*}}\s*(==|!=|>|<|>=|<=)\s*(.*)$",
     condition_str)
            
            if comp_match:
                var_path, operator, value_str = comp_match.groups()
                actual_value = self._resolve_value(
                    # Resolve the variable
                    f"{{{{ {var_path} }}}}", runtime_context, initial_context)
                expected_value = self._parse_condition_value(
                    value_str)  # Parse the literal value
                result = self._compare_values(
    actual_value, operator, expected_value)
                logger.debug(
    f"Condition '{condition_str}' evaluated to {result} (Actual: {
        repr(actual_value)}, Op: {operator}, Expected: {
            repr(expected_value)})")
                return result

            # Regex for membership: value IN/NOT IN {{ var.path }} (e.g.,
            # "Error" in {{task_B.reflection.potential_issues}})
            in_match = re.match(
    r"^(.+?)\s+(in|not in)\s+{{\s*([\w\.\-]+)\s*}}$",
    condition_str,
     re.IGNORECASE)
            if in_match:
                value_str, operator, var_path = in_match.groups()
                value_to_check = self._parse_condition_value(
                    value_str.strip())  # Parse the literal value
                container = self._resolve_value(
                    # Resolve the container
                    f"{{{{ {var_path} }}}}", runtime_context, initial_context)
                operator_lower = operator.lower()
                if isinstance(container, (list, str, dict, set)
                              ):  # Check if container type supports 'in'
                        is_in = value_to_check in container
                        result = is_in if operator_lower == 'in' else not is_in
                        logger.debug(
    f"Condition '{condition_str}' evaluated to {result}")
                        return result
                else:
                        logger.warning(
    f"Container for '{operator}' check ('{var_path}') is not a list/str/dict/set: {
        type(container)}. Evaluating to False.")
                        return False

            # Regex for simple truthiness/existence: {{ var.path }} or !{{
            # var.path }}
            truth_match = re.match(
    r"^(!)?\s*{{\s*([\w\.\-]+)\s*}}$",
     condition_str)
            if truth_match:
                negated, var_path = truth_match.groups()
                actual_value = self._resolve_value(
                    f"{{{{ {var_path} }}}}", runtime_context, initial_context)
                result = bool(actual_value)
                if negated: result = not result
                logger.debug(
    f"Condition '{condition_str}' (truthiness/existence) evaluated to {result}")
                return result

            # If no pattern matches
            logger.error(
    f"Unsupported condition format: {condition_str}. Defaulting evaluation to False.")
            return False
        except Exception as e:
            logger.error(
    f"Error evaluating condition '{condition_str}': {e}. Defaulting to False.",
     exc_info=True)
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
            if len(val_str_cleaned) >= 2 and val_str_cleaned.startswith(
                ('"', "'")) and val_str_cleaned.endswith(val_str_cleaned[0]):
                return val_str_cleaned[1:-1]
            # Otherwise, return as unquoted string
            return val_str_cleaned

    def _compare_values(
    self,
    actual: Any,
    operator: str,
     expected: Any) -> bool:
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

            if isinstance(
    actual,
    numeric_types) and isinstance(
        expected,
         numeric_types):
                # Convert numpy types to standard Python types for comparison
                # if needed
                actual_cmp = float(actual) if np and isinstance(
                    actual, np.number) else actual
                expected_cmp = float(expected) if np and isinstance(
                    expected, np.number) else expected
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
                logger.warning(
    f"Type mismatch or unsupported type for ordered comparison '{operator}': actual={
        type(actual)}, expected={
            type(expected)}. Evaluating to False.")
                return False
        except TypeError as e:
            # Catch potential errors during comparison (e.g., comparing None)
            logger.warning(
    f"TypeError during comparison '{operator}' between {
        type(actual)} and {
            type(expected)}: {e}. Evaluating to False.")
            return False
        except Exception as e_cmp:
            logger.error(
    f"Unexpected error during value comparison: {e_cmp}. Evaluating condition to False.")
            return False
        # Should not be reached if operator is valid
        logger.warning(
    f"Operator '{operator}' invalid or comparison failed for types {
        type(actual)} and {
            type(expected)}. Evaluating to False.")
        return False

    def _sanitize_for_json(self, data: Any) -> Any:
        """Recursively sanitizes data to ensure it's JSON serializable."""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        if isinstance(data, dict):
            return {str(k): self._sanitize_for_json(v)
                        for k, v in data.items()}
        if isinstance(data, list):
            return [self._sanitize_for_json(v) for v in data]
        if hasattr(data, 'isoformat'):  # Handle datetime objects
            return data.isoformat()
        # Fallback for other types (like numpy floats, etc.)
        return str(data)

    def _emit_event(self, event_type: str, payload: Dict[str, Any]):
        """Helper to safely call the event_callback if it exists."""
        if self.event_callback:
            try:
                # Package the event data correctly for the VCD callback
                event_data = {
                    "type": "thought_process_step",
                    "event": event_type,
                    "timestamp": now_iso(),
                    "payload": payload
                }
                self.event_callback(event_data)
            except Exception as e:
                logger.warning(f"Failed to emit VCD event: {e}")
    
    def _emit_rich_vcd_event(self, event_type: str, title: str, description: str, 
                           metadata: Dict[str, Any] = None, links: List[Dict[str, Any]] = None,
                           code_blocks: List[Dict[str, Any]] = None, simulations: List[Dict[str, Any]] = None,
                           visualizations: List[Dict[str, Any]] = None):
        """Emit rich VCD events with enhanced metadata and interactive elements."""
        if self.event_callback:
            try:
                # Create rich event data structure
                rich_event_data = {
                    "type": "rich_event",
                    "event": event_type,
                    "timestamp": now_iso(),
                    "payload": {
                        "event_id": f"{event_type}_{uuid.uuid4().hex[:8]}",
                        "event_type": event_type,
                        "title": title,
                        "description": description,
                        "phase": getattr(self, 'current_phase', 'Unknown'),
                        "links": links or [],
                        "code_blocks": code_blocks or [],
                        "simulations": simulations or [],
                        "visualizations": visualizations or [],
                        "expandable": True,
                        "drill_down_enabled": True,
                        "interactive": True,
                        "metadata": metadata or {},
                        "tags": [event_type.lower(), "workflow", "analysis"]
                    }
                }
                self.event_callback(rich_event_data)
            except Exception as e:
                logger.warning(f"Failed to emit rich VCD event: {e}")

    @log_to_thought_trail
    def run_workflow(self, workflow_name: str,
                     initial_context: Dict[str, Any],
                     timeout: int = 900,
                     model: str = None) -> Dict[str, Any]:
        """
        Main entry point to run a workflow.
        Initializes context, manages the task queue, and returns the final results.
        Now includes detailed event logging for each action.
        """
        try:
            workflow_definition = self.load_workflow(workflow_name)
        except (FileNotFoundError, ValueError, TypeError) as e:
            logger.critical(
    f"Workflow execution failed during loading: {e}",
     exc_info=True)
            return self._summarize_run(
    workflow_name, "N/A", "Failed", 0, {}, {}, str(e))

        run_id = initial_context.get(
    "workflow_run_id", f"run_{
        uuid.uuid4().hex}")
        initial_context["workflow_run_id"] = run_id
        
        # Inject the model into the initial context so all tasks can access it
        if model:
            initial_context["model"] = model

        event_log = []
        # Load externalized session state (non-negotiable) and inject into initial_context
        try:
            session_state = load_session_state()
        except Exception:
            session_state = {"facts_ledger": [], "updated_at": now_iso()}
        initial_context = {**initial_context, "session_state": session_state}
        # Prime SPR bundles if text context exists
        try:
            if self.spr_manager and hasattr(self.spr_manager, "scan_and_prime"):
                prime_text = initial_context.get("prime_text") or initial_context.get("user_query") or ""
                spr_defs = self.spr_manager.scan_and_prime(prime_text) or []
                bundles = [create_context_bundle(sd, {}, initial_context) for sd in spr_defs]
                if bundles:
                    initial_context["context_bundles"] = merge_bundles(bundles)
                    # Feed pinned policy headers to retrieval layer for modulation
                    pinned_terms = [sd.get("term") for sd in spr_defs if sd.get("term")]
                    if pinned_terms:
                        initial_context.setdefault("retrieval_modulation", {})
                        initial_context["retrieval_modulation"]["pinned_policy_terms"] = pinned_terms
                        initial_context["retrieval_modulation"]["pinned_policy_weight"] = 2.0
        except Exception:
            pass
        runtime_context = {
                "initial_context": initial_context,
            "workflow_run_id": run_id,
            "workflow_definition": workflow_definition,
        }

        # Autonomous SIRC: refine complex intent into executable objective
        try:
            initial_context = maybe_autorun_sirc(initial_context, getattr(self, 'spr_manager', None))
        except Exception:
            pass
        
        tasks = workflow_definition.get('tasks', {})
        dependencies = workflow_definition.get('dependencies', {})
        task_statuses = {key: "pending" for key in tasks}

        # --- OPTIMIZATION INJECTION ---
        try:
            optimizer = WorkflowOptimizer({"tasks": [{"id": tid} for tid in tasks.keys()], "dependencies": dependencies})
            execution_plan = optimizer.get_optimized_execution_plan()
            logger.info(f"Workflow plan optimized. Executing in {len(execution_plan)} parallel stage(s).")
            self._emit_event("ThoughtTrail", {"message": f"Optimal execution path calculated: {len(execution_plan)} stages."})
        except ValueError as e:
            logger.error(f"Could not optimize workflow: {e}. Falling back to naive execution order.")
            # Fallback to a simple, potentially incorrect order if optimization fails
            execution_plan = [[key for key in tasks.keys() if not dependencies.get(key)]]
        
        running_tasks = {}
        completed_tasks = set()
        
        logger.info(
    f"Starting workflow '{
        self.last_workflow_name}' (Run ID: {run_id}).")

        start_time = time.time()
        
        # --- REFACTORED EXECUTION LOOP ---
        for stage_index, stage_tasks in enumerate(execution_plan):
            logger.info(f"Executing stage {stage_index + 1}/{len(execution_plan)} with tasks: {stage_tasks}")
            self._emit_event("ThoughtTrail", {"message": f"Beginning execution of stage {stage_index + 1}."})

            # In a true parallel implementation, these tasks would be submitted to a thread/process pool.
            # For this simulation, we'll execute them sequentially within the stage.
            for task_key in stage_tasks:
                if task_key in completed_tasks:
                    continue # Should not happen with a correct plan, but a safeguard.

                task_info = tasks[task_key]
                action_type = task_info.get("action_type")
            
                attempt_count = 1 
                max_attempts = task_info.get('retries', 0) + 1
                
                condition = task_info.get('condition')

                self._emit_event("ThoughtTrail", {"message": f"Evaluating condition for task: {task_key}..."})

                if condition and not self._evaluate_condition(
                    condition, runtime_context, initial_context):
                    logger.info(
        f"Skipping task '{task_key}' due to unmet condition: {condition}")
                    task_statuses[task_key] = "skipped"
                    
                    self._emit_event("ThoughtTrail", {"message": f"Task '{task_key}' skipped. Condition not met."})

                    completed_tasks.add(task_key)
                    self._execute_resonant_corrective_loop(
                        trigger_task=task_key, 
                        reason="condition_unmet",
                        runtime_context=runtime_context
                    )
                    continue

                running_tasks[task_key] = time.time()
                
                self._emit_event("ThoughtTrail", {"message": f"Executing task: {task_key} (Action: {action_type})"})
                
                action_context_obj = ActionContext(
                    task_key=task_key, action_name=task_key, action_type=action_type,
                    workflow_name=self.last_workflow_name, run_id=run_id,
                    attempt_number=attempt_count, max_attempts=max_attempts,
                    execution_start_time=now(),
                    runtime_context=runtime_context
                )

                resolved_inputs = self._resolve_inputs(
                    task_info.get('inputs'), runtime_context, initial_context, task_key
                )
                
                prompt_vars = task_info.get('prompt_vars')
                if prompt_vars:
                    resolved_prompt_vars = self._resolve_value(
                        prompt_vars, runtime_context, initial_context, task_key)
                    if isinstance(resolved_prompt_vars, dict) and isinstance(resolved_inputs, dict):
                        resolved_inputs['initial_context'] = {
                            **resolved_inputs.get('initial_context', {}), **resolved_prompt_vars}

                try:
                    print_tagged_execution(task_key, action_type, resolved_inputs)
                except Exception:
                    pass

                try:
                    result = execute_action(
                        action_type=action_type,
                        inputs=resolved_inputs,
                        context_for_action=action_context_obj
                    )
                    # Defensive: Ensure result is always a dict
                    if not isinstance(result, dict):
                        logger.error(f"execute_action returned non-dict type: {type(result)}. Converting to error dict.")
                        result = {
                            "error": f"execute_action returned invalid type: {type(result)}",
                            "reflection": {
                                "status": "Failed",
                                "summary": f"Action execution returned invalid type: {type(result)}",
                                "confidence": 0.0,
                                "alignment_check": {"objective_alignment": 0.0, "protocol_alignment": 0.0},
                                "potential_issues": ["execute_action did not return a dictionary"],
                                "raw_output_preview": str(result)
                            }
                        }
                except Exception as e:
                    # Ultimate failsafe: If execute_action itself raises an exception (which it shouldn't)
                    logger.error(f"CRITICAL: execute_action raised an exception (this should never happen): {e}", exc_info=True)
                    result = {
                        "error": f"CRITICAL: execute_action raised exception: {str(e)}",
                        "reflection": {
                            "status": "Failed",
                            "summary": f"Action execution raised an unhandled exception: {str(e)}",
                            "confidence": 0.0,
                            "alignment_check": {"objective_alignment": 0.0, "protocol_alignment": 0.0},
                            "potential_issues": [f"execute_action raised: {type(e).__name__}: {str(e)}"],
                            "raw_output_preview": str(e)
                        }
                    }
                
                try:
                    print_tagged_results(task_key, action_type, result)
                except Exception:
                    pass
                
                if isinstance(result, dict) and 'output' in result and isinstance(result['output'], str):
                    try:
                        json_string = result['output'].strip()
                        if json_string.startswith('{') and json_string.endswith('}'):
                            parsed_output = json.loads(json_string)
                            result.update(parsed_output)
                            logger.debug(f"Parsed and merged JSON output from execute_code task '{task_key}'.")
                    except json.JSONDecodeError:
                        logger.debug(f"Output of task '{task_key}' looked like JSON but failed to parse. Proceeding with raw string output.")

                result = self._ensure_iar_compliance(result, action_context_obj)
                result = self._validate_and_heal_output(result, task_info, action_context_obj)

                if result.get("reflection", {}).get("confidence", 1.0) < 0.7:
                    self._execute_resonant_corrective_loop(
                        trigger_task=task_key, reason="low_confidence",
                        runtime_context=runtime_context, task_result=result
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
                
                status_msg = "succeeded" if is_success else "failed"
                self._emit_event("ThoughtTrail", {"message": f"Task '{task_key}' {status_msg}. Duration: {task_duration}s"})

                # IAR contract validation (bedrock of trust)
                reflection = result.get("reflection") or result.get("iar") or {}
                if isinstance(reflection, dict) and reflection:
                    ok, issues = self.iar_validator.validate_structure(reflection)
                    if not ok:
                        # Mark as failure on contract violation
                        result.setdefault("error", "IAR contract violation")
                        result["iar_issues"] = issues
                        task_statuses[task_key] = "failed"
                        is_success = False
                    else:
                        # Record resonance metrics when available
                        try:
                            self.resonance_tracker.record_execution(task_key, reflection, runtime_context)
                        except Exception:
                            pass

                # Append atomic fact to facts_ledger for successful tasks
                if is_success:
                    try:
                        append_fact(session_state, {
                            "task": task_key,
                            "status": "success",
                            "confidence": (reflection or {}).get("confidence"),
                            "summary": (reflection or {}).get("summary") or result.get("summary"),
                        })
                    except Exception:
                        pass

                    # Causal-preserving progressive summarization (flux-annotated digest)
                    try:
                        # Use recent successful results as raw events window
                        trail_window = []
                        for k in list(runtime_context.keys())[-60:]:
                            if isinstance(runtime_context.get(k), dict):
                                entry = runtime_context.get(k)
                                if isinstance(entry, dict) and ("reflection" in entry or "iar" in entry):
                                    trail_window.append({
                                        'task_id': k,
                                        'outputs': entry,
                                        'iar_reflection': entry.get('reflection') or entry.get('iar') or {}
                                    })
                        if trail_window:
                            digest = build_flux_annotated_digest(trail_window)
                            if isinstance(digest, dict):
                                session_state.setdefault("digests", []).append(digest)
                                save_session_state(session_state)
                    except Exception:
                        pass

                    # Build superpositioned context bundles on SPR activations (from outputs)
                    try:
                        if self.spr_manager and isinstance(result.get("output_text"), str):
                            spr_defs = self.spr_manager.scan_and_prime(result["output_text"]) or []
                            if spr_defs:
                                bundles = [create_context_bundle(sd, runtime_context, initial_context) for sd in spr_defs]
                                existing = initial_context.get("context_bundles")
                                merged = merge_bundles(bundles if not existing else bundles + [existing])
                                initial_context["context_bundles"] = merged
                                # Predictive prefetch when bundles change
                                try:
                                    trigger_predictive_prefetch(session_state, initial_context)
                                except Exception:
                                    pass
                    except Exception:
                        pass

        end_time = time.time()
        run_duration = round(end_time - start_time, 2)
        
        final_status = "Completed Successfully"
        if any(status == "failed" for status in task_statuses.values()):
            final_status = "Completed with Errors"
        elif len(completed_tasks) < len(tasks):
            final_status = "Stalled"
        
        logger.info(
    f"Workflow '{
        self.last_workflow_name}' finished in {run_duration}s with status: {final_status}")

        # --- Event Log Persistence ---
        # Save the detailed event log for this run to a file for deeper analysis.
        try:
            # Use the project outputs directory for the event log
            from .config import PathConfig
            config = PathConfig()
            outputs_dir = config.outputs
            outputs_dir.mkdir(exist_ok=True)
            event_log_path = outputs_dir / f"run_events_{run_id}.jsonl"
            with open(event_log_path, 'w', encoding='utf-8') as f:
                for event in event_log:
                    f.write(json.dumps(event, default=str) + '\n')
            logger.info(f"Event log for run {run_id} saved to {event_log_path}")
        except Exception as e:
            logger.error(f"Failed to save event log to {event_log_path}: {e}")

        # Persist session state at the end of run
        try:
            save_session_state(session_state)
        except Exception:
            pass

        # Compute declared workflow outputs (if any) using template resolution
        try:
            outputs_def = workflow_definition.get('output', {})
            if isinstance(outputs_def, dict) and outputs_def:
                for out_key, out_spec in outputs_def.items():
                    if isinstance(out_spec, dict) and 'value' in out_spec:
                        try:
                            resolved_out = self._resolve_value(
                                out_spec.get('value'),
                                runtime_context,
                                initial_context
                            )
                            runtime_context[out_key] = resolved_out
                        except Exception as e_out:
                            logger.warning(f"Failed to resolve workflow output '{out_key}': {e_out}")
        except Exception as e_outputs:
            logger.warning(f"Error while computing workflow outputs: {e_outputs}")

        final_results = self._summarize_run(
            workflow_name=self.last_workflow_name, run_id=run_id, status=final_status,
            duration=run_duration, task_statuses=task_statuses, runtime_context=runtime_context
        )
        return final_results

    def _summarize_run(
    self,
    workflow_name,
    run_id,
    status,
    duration,
    task_statuses,
    runtime_context,
     error=None):
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

    def _display_task_result(self, task_name: str, result: Dict[str, Any]) -> None:
        """Display task execution result in a formatted way."""
        print("\n" + "="*80)
        print(f"Task: {task_name}")
        print("-"*80)
        
        # Display status
        status = result.get("status", "Unknown")
        print(f"Status: {status}")
        
        # Display summary if available
        if "summary" in result:
            print(f"\nSummary:\n{result['summary']}")
        
        # Display confidence if available
        if "confidence" in result:
            print(f"\nConfidence: {result['confidence']:.2f}")
        
        # Display raw output preview if available
        if "raw_output_preview" in result:
            print("\nOutput Preview:")
            print("-"*40)
            print(result["raw_output_preview"])
            print("-"*40)
        
        print("="*80 + "\n")

    def _display_workflow_progress(self, task_name: str, status: str) -> None:
        """Display workflow execution progress."""
        print(f"\n[{format_log()}] {task_name}: {status}")

    def execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with enhanced terminal output."""
        display_workflow_start(workflow.get('name', 'Unnamed Workflow'))
        
        start_time = now()
        run_id = str(uuid.uuid4())
        
        try:
            # Validate workflow
            if not self._validate_workflow(workflow):
                raise ValueError("Workflow validation failed")
            
            # Initialize results
            results = {
                "workflow_name": workflow.get("name", "unknown"),
                "run_id": run_id,
                "start_time": start_time.isoformat(),
                "tasks": {}
            }
            
            # Execute tasks
            for task_name, task in workflow.get("tasks", {}).items():
                display_workflow_progress(task_name, "Starting")
                
                # Check dependencies
                dependencies = task.get("dependencies", [])
                for dep in dependencies:
                    if dep not in results["tasks"]:
                        raise ValueError(f"Missing dependency: {dep}")
                
                # Execute task
                try:
                    task_result = self._execute_task(task, results, initial_context)
                    results["tasks"][task_name] = task_result
                    display_task_result(task_name, task_result)
                    display_workflow_progress(task_name, "Completed")
                except Exception as e:
                    error_msg = f"Task {task_name} failed: {str(e)}"
                    display_workflow_progress(task_name, f"Failed: {error_msg}")
                    results["tasks"][task_name] = {
                        "status": "Failed",
                        "error": error_msg
                    }
                    raise
            
            # Workflow completed successfully
            end_time = now()
            results["end_time"] = end_time.isoformat()
            results["workflow_status"] = "Completed Successfully"
            results["execution_time_seconds"] = (end_time - start_time).total_seconds()
            
            # Save and display final result
            output_path = self._save_workflow_result(results)
            display_workflow_complete(results, output_path)
            
            return results
            
        except Exception as e:
            # Workflow failed
            end_time = now()
            results["end_time"] = end_time.isoformat()
            results["workflow_status"] = "Failed"
            results["error"] = str(e)
            results["execution_time_seconds"] = (end_time - start_time).total_seconds()
            
            # Save and display error
            output_path = self._save_workflow_result(results)
            display_workflow_error(str(e), output_path)
            
            return results

    def _save_workflow_result(self, result: Dict[str, Any]) -> str:
        """Save workflow result to a file with timestamp."""
        timestamp = format_filename()
        workflow_name = result.get("workflow_name", "unknown_workflow")
        run_id = result.get("run_id", str(uuid.uuid4()))
        filename = f"result_{workflow_name}_run_{run_id}_{timestamp}.json"
        
        # Add timestamp to the result data
        result["timestamp"] = timestamp
        
        output_path = os.path.join("outputs", filename)
        os.makedirs("outputs", exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        return output_path
    
    def _auto_organize_log(self, log_file_path: str):
        """Auto-organize a single log file using the log organizer."""
        try:
            # Check if auto-organization is enabled
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log_organization_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                if not config.get("auto_organization", {}).get("enabled", True):
                    logger.info("Auto-log organization is disabled")
                    return
            
            # Import log organizer
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from log_organizer import LogOrganizer
            
            # Create organizer instance
            organizer = LogOrganizer()
            
            # Extract metadata from the log file
            metadata = organizer._extract_log_metadata(log_file_path)
            
            # Generate organized filename
            organized_filename = organizer._generate_organized_filename(metadata)
            
            # Determine destination directory
            workflow_clean = re.sub(r'[^\w\-_]', '_', metadata["workflow_name"])
            workflow_clean = workflow_clean.replace('__', '_').strip('_')
            
            phase = metadata["phase"]
            if metadata["error_count"] > 0:
                dest_dir = organizer.organized_dir / "errors"
            elif phase != "unknown":
                dest_dir = organizer.organized_dir / "phases" / f"phase_{phase}"
                dest_dir.mkdir(parents=True, exist_ok=True)
            else:
                dest_dir = organizer.organized_dir / "workflows" / workflow_clean
                dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy file to organized location
            dest_path = dest_dir / organized_filename
            import shutil
            shutil.copy2(log_file_path, dest_path)
            
            # Create metadata file
            metadata_file = dest_path.with_suffix('.metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Update catalog
            workflow_name = metadata["workflow_name"]
            if workflow_name not in organizer.catalog["workflows"]:
                organizer.catalog["workflows"][workflow_name] = {
                    "count": 0,
                    "phases": set(),
                    "sessions": set(),
                    "total_errors": 0,
                    "total_tasks": 0
                }
            
            organizer.catalog["workflows"][workflow_name]["count"] += 1
            organizer.catalog["workflows"][workflow_name]["phases"].add(phase)
            organizer.catalog["workflows"][workflow_name]["sessions"].add(metadata["session_id"])
            organizer.catalog["workflows"][workflow_name]["total_errors"] += metadata["error_count"]
            organizer.catalog["workflows"][workflow_name]["total_tasks"] += metadata["task_count"]
            
            # Convert sets to lists for JSON serialization
            for workflow_data in organizer.catalog["workflows"].values():
                workflow_data["phases"] = list(workflow_data["phases"])
                workflow_data["sessions"] = list(workflow_data["sessions"])
            
            organizer.catalog["metadata"]["total_logs"] += 1
            organizer.catalog["metadata"]["last_organized"] = now_iso()
            
            # Save updated catalog
            organizer._save_catalog()
            
            logger.info(f"Auto-organized log: {log_file_path} -> {dest_path}")
            
        except Exception as e:
            logger.warning(f"Auto-organization failed for {log_file_path}: {e}")

    def _ensure_iar_compliance(self, result: Dict[str, Any], context: 'ActionContext') -> Dict[str, Any]:
        """
        Acts as middleware to guarantee every action result has a compliant IAR.
        If the reflection is missing or invalid, it generates a default one.
        """
        reflection = result.get("reflection") or result.get("iar") or {}
        is_compliant, issues = self.iar_validator.validate_structure(reflection)

        if is_compliant:
            return result

        logger.warning(
            f"Task '{context.task_key}' produced a non-compliant IAR. Issues: {issues}. Generating fallback IAR.")

        # If we are here, the IAR is non-compliant, so we build one.
        is_error = "error" in result and result["error"] is not None

        generated_reflection = {
            "status": "Failed" if is_error else "Success",
            "summary": reflection.get("summary") or f"Task '{context.task_key}' completed.",
            "confidence": reflection.get("confidence") or (0.5 if is_error else 0.9),
            "alignment_check": reflection.get("alignment_check") or "Unknown",
            "potential_issues": reflection.get("potential_issues") or (
                [result["error"]] if is_error else []),
            "raw_output_preview": reflection.get("raw_output_preview") or str(
                result.get("output") or result)[:200]
        }
        
        # Add the generated (or original if it existed) reflection back to the result
        result["reflection"] = generated_reflection
        
        # If the original failure was an IAR contract violation, remove the error
        # now that we have fixed it.
        if result.get("error") == "IAR contract violation":
            del result["error"]
            if "iar_issues" in result:
                del result["iar_issues"]

        return result

    def _validate_and_heal_output(self, result: Dict[str, Any], task_info: Dict[str, Any], context: 'ActionContext') -> Dict[str, Any]:
        """
        Validates the task result against its defined output_schema.
        If validation fails, triggers a self-healing action to correct the format.
        """
        schema = task_info.get("output_schema")
        if not schema:
            return result # No schema to validate against

        # Simple validation for now. A more robust solution would use jsonschema.
        is_valid = True
        if schema.get("type") == "object" and isinstance(result, dict):
            for prop in schema.get("required", []):
                if prop not in result:
                    is_valid = False
                    break
        elif schema.get("type") == "string" and not isinstance(result, str):
            is_valid = False
        
        if is_valid:
            return result

        logger.warning(f"Task '{context.task_key}' output failed schema validation. Attempting self-healing.")
        
        try:
            heal_action = self.action_registry.get("self_heal_output")
            if not heal_action:
                logger.error("Self-healing failed: 'self_heal_output' action not registered.")
                result["error"] = "Output schema validation failed and self-healing is unavailable."
                return result
            
            healing_result = heal_action(
                inputs={
                    "original_prompt": context.runtime_context.get("initial_context", {}).get("prompt"), # A bit simplified
                    "invalid_output": result.get("output") or result,
                    "target_schema": schema
                },
                context_for_action=context
            )
            
            if "error" in healing_result:
                logger.error(f"Self-healing failed for task '{context.task_key}': {healing_result['error']}")
                result["error"] = "Output schema validation and subsequent self-healing failed."
                return result
            
            logger.info(f"Task '{context.task_key}' output successfully self-healed.")
            # Return the corrected output
            return healing_result

        except Exception as e:
            logger.error(f"Exception during self-healing for task '{context.task_key}': {e}")
            result["error"] = "An exception occurred during output self-healing."
            return result

    def _execute_resonant_corrective_loop(self, trigger_task: str, reason: str, runtime_context: Dict[str, Any], task_result: Optional[Dict[str, Any]] = None):
        """
        Executes a corrective workflow in response to a trigger like a skipped task or low-confidence result.
        RCL web search disabled - requires explicit LLM prompting for web searches.
        """
        logger.info(f"RCL triggered for task '{trigger_task}' due to '{reason}'. RCL web search disabled - requires explicit LLM prompting.")
        
        # RCL web search disabled to prevent automatic web searches without LLM prompting
        # Log the issue for manual review instead of automatically searching
        logger.warning(f"Task '{trigger_task}' failed with reason '{reason}'. Manual intervention may be required.")
        
        # Store the failure information for potential manual review
        failure_info = {
            "trigger_task": trigger_task,
            "trigger_reason": reason,
            "original_workflow_run_id": runtime_context.get("workflow_run_id"),
            "task_result": task_result or runtime_context.get(trigger_task),
            "timestamp": time.time(),
            "rcl_action": "logged_for_review"
        }
        
        # Could save to a log file for manual review if needed
        # For now, just log the information
        logger.info(f"RCL failure logged: {failure_info}")


    def _validate_and_heal_output(self, result: Dict[str, Any], task_info: Dict[str, Any], context: 'ActionContext') -> Dict[str, Any]:
        """
        Validates the task result against its defined output_schema.
        If validation fails, triggers a self-healing action to correct the format.
        """
        schema = task_info.get("output_schema")
        if not schema:
            return result # No schema to validate against

        # Simple validation for now. A more robust solution would use jsonschema.
        is_valid = True
        if schema.get("type") == "object" and isinstance(result, dict):
            for prop in schema.get("required", []):
                if prop not in result:
                    is_valid = False
                    break
        elif schema.get("type") == "string" and not isinstance(result, str):
            is_valid = False
        
        if is_valid:
            return result

        logger.warning(f"Task '{context.task_key}' output failed schema validation. Attempting self-healing.")
        
        try:
            heal_action = self.action_registry.get("self_heal_output")
            if not heal_action:
                logger.error("Self-healing failed: 'self_heal_output' action not registered.")
                result["error"] = "Output schema validation failed and self-healing is unavailable."
                return result
            
            healing_result = heal_action(
                inputs={
                    "original_prompt": context.runtime_context.get("initial_context", {}).get("prompt"), # A bit simplified
                    "invalid_output": result.get("output") or result,
                    "target_schema": schema
                },
                context_for_action=context
            )
            
            if "error" in healing_result:
                logger.error(f"Self-healing failed for task '{context.task_key}': {healing_result['error']}")
                result["error"] = "Output schema validation and subsequent self-healing failed."
                return result
            
            logger.info(f"Task '{context.task_key}' output successfully self-healed.")
            # Return the corrected output
            return healing_result

        except Exception as e:
            logger.error(f"Exception during self-healing for task '{context.task_key}': {e}")
            result["error"] = "An exception occurred during output self-healing."
            return result

# --- END OF FILE 3.0ArchE/workflow_engine.py ---