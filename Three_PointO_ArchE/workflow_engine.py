# ResonantiA Protocol v3.1-CA - IARCompliantWorkflowEngine
# File: Three_PointO_ArchE/workflow_engine.py
# Description: The canonical, IAR-compliant workflow engine. This module is the
# heart of ArchE's operational execution, responsible for parsing and running
# Process Blueprints (workflows). It manages the execution flow, task dependencies,
# conditional logic (Phasegates), and the critical processing of Integrated Action
# Reflection (IAR) data from every cognitive tool.

import json
import os
import logging
import copy
import time
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Callable, Tuple

# --- Core ArchE Component Imports ---
from . import config
from .action_registry import execute_action, ACTION_REGISTRY, register_action
from .spr_manager import SPRManager
from .error_handler import handle_action_error
from .action_context import ActionContext
from .output_handler import (
    display_task_result,
    display_workflow_progress,
    display_workflow_start,
    display_workflow_complete,
    display_workflow_error,
)

# --- Optional Imports ---
try:
    import numpy as np
except ImportError:
    np = None

logger = logging.getLogger(__name__)


# ==============================================================================
# IAR & RESONANCE VALIDATION COMPONENTS
# These classes are integral to the engine's operation and are defined here
# to ensure the module is self-contained and reflects their importance.
# Based on Crystallized Artifacts: ARTIFACT 1B & 4A
# ==============================================================================

class IARValidator:
    """Validates IAR structure compliance per the ResonantiA Protocol."""
    
    def __init__(self):
        self.required_fields = [
            'status', 'summary', 'confidence', 'alignment_check',
            'potential_issues', 'raw_output_preview'
        ]

    def validate_structure(self, iar_data: Any) -> Tuple[bool, List[str]]:
        """
        Validates that the provided data adheres to the mandatory IAR structure.

        Args:
            iar_data: The reflection dictionary to validate.

        Returns:
            A tuple containing a boolean (True if valid) and a list of issues.
        """
        if not isinstance(iar_data, dict):
            return False, ["IAR reflection must be a dictionary."]
        
        issues = []
        for field in self.required_fields:
            if field not in iar_data:
                issues.append(f"Missing required IAR field: '{field}'")

        if 'status' in iar_data and iar_data['status'] not in ['Success', 'Partial', 'Failed']:
            issues.append(f"Invalid IAR status: '{iar_data['status']}'. Must be 'Success', 'Partial', or 'Failed'.")

        if 'confidence' in iar_data:
            confidence = iar_data['confidence']
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                issues.append(f"IAR confidence must be a float between 0.0 and 1.0, but got: {confidence}")

        return not issues, issues


class ResonanceTracker:
    """Tracks tactical resonance and crystallization metrics for a workflow run."""
    
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []

    def record_execution(self, task_id: str, iar_data: Dict[str, Any]) -> None:
        """Records a task's IAR data for resonance tracking."""
        record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'task_id': task_id,
            'status': iar_data.get('status'),
            'confidence': iar_data.get('confidence', 0.0),
            'tactical_resonance': iar_data.get('tactical_resonance', 0.0),
            'crystallization_potential': iar_data.get('crystallization_potential', 0.0)
        }
        self.execution_history.append(record)

    def get_run_summary(self) -> Dict[str, Any]:
        """Generates a summary report of the entire run's resonance."""
        if not self.execution_history:
            return {
                'total_tasks': 0, 'successful_tasks': 0, 'failed_tasks': 0,
                'average_confidence': 0.0, 'average_tactical_resonance': 0.0
            }

        successful_tasks = [ex for ex in self.execution_history if ex['status'] == 'Success']
        failed_tasks = [ex for ex in self.execution_history if ex['status'] == 'Failed']

        avg_confidence = (sum(ex['confidence'] for ex in successful_tasks) / len(successful_tasks)) if successful_tasks else 0.0
        avg_resonance = (sum(ex['tactical_resonance'] for ex in successful_tasks) / len(successful_tasks)) if successful_tasks else 0.0

        return {
            'total_tasks': len(self.execution_history),
            'successful_tasks': len(successful_tasks),
            'failed_tasks': len(failed_tasks),
            'average_confidence': round(avg_confidence, 3),
            'average_tactical_resonance': round(avg_resonance, 3)
        }


# ==============================================================================
# THE CORE WORKFLOW ENGINE
# ==============================================================================

class IARCompliantWorkflowEngine:
    """
    Orchestrates the execution of defined workflows (Process Blueprints),
    enforcing IAR compliance and managing the flow of data and control.
    """

    def __init__(self, workflows_dir: str = "workflows", spr_manager: Optional[SPRManager] = None):
        self.workflows_dir = workflows_dir
        self.spr_manager = spr_manager or SPRManager()
        self.action_registry = ACTION_REGISTRY.copy()
        self.iar_validator = IARValidator()
        self.logger = logging.getLogger(__name__)
        logger.info("IARCompliantWorkflowEngine initialized.")

    def load_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Loads and validates a workflow definition from a JSON file."""
        # Check if workflow_name already contains the full path or starts with the workflows_dir
        if workflow_name.startswith(self.workflows_dir + os.sep) or os.path.isabs(workflow_name):
            workflow_path = workflow_name
        else:
            workflow_path = os.path.join(self.workflows_dir, workflow_name)

        if not os.path.exists(workflow_path):
            raise FileNotFoundError(f"Workflow file not found: {workflow_path}")

        logger.info(f"Loading workflow definition from: {workflow_path}")
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        if "tasks" not in workflow or not isinstance(workflow["tasks"], dict):
            raise ValueError("Workflow definition must contain a 'tasks' dictionary.")
        
        for task_id, task in workflow["tasks"].items():
            if "action_type" not in task:
                raise ValueError(f"Task '{task_id}' is missing required 'action_type'.")
            if task["action_type"] not in self.action_registry:
                raise ValueError(f"Action type '{task['action_type']}' for task '{task_id}' is not registered.")
        
        return workflow

    async def run_workflow(self, workflow_name: str, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point to run a workflow.
        Manages the task queue, context, dependencies, and IAR processing.
        """
        workflow_definition = self.load_workflow(workflow_name)
        
        run_id = str(uuid.uuid4())

        display_workflow_start(workflow_definition.get('name', workflow_name), run_id)

        start_time = time.time()
        resonance_tracker = ResonanceTracker()

        # Initialize runtime_context with initial_context
        runtime_context: Dict[str, Any] = {"initial_context": initial_context}
        
        tasks = workflow_definition.get('tasks', {})
        completed_tasks: Set[str] = set()
        
        # Initialize task queue with tasks that have no dependencies
        ready_tasks: Set[str] = {
            task_id for task_id, task in tasks.items() if not task.get('dependencies')
        }

        while ready_tasks:
            task_key = ready_tasks.pop()
            task_info = tasks[task_key]
            display_workflow_progress(task_key, "Starting")

            # --- 1. Condition Evaluation (Phasegate) ---
            if not self._evaluate_condition(task_info.get('condition'), runtime_context, initial_context):
                display_workflow_progress(task_key, "Skipped (Condition Not Met)")
                completed_tasks.add(task_key) # Mark as complete for dependency resolution
                self._update_ready_tasks(tasks, completed_tasks, ready_tasks)
                continue

            # --- 2. Input Resolution ---
            try:
                resolved_inputs = self._resolve_value(task_info.get('inputs', {}), runtime_context, initial_context)
            except Exception as e:
                display_workflow_error(f"Error resolving inputs for task '{task_key}': {e}", "N/A")
                return self._summarize_run(workflow_name, run_id, "Failed", start_time, runtime_context, resonance_tracker, str(e))

            # --- 3. Action Execution ---
            action_context = ActionContext(
                task_key=task_key,
                action_name=task_info.get('description', task_key),
                action_type=task_info['action_type'],
                workflow_name=workflow_definition.get('name', workflow_name),
                run_id=run_id,
                runtime_context=runtime_context
            )
            
            try:
                result = await execute_action(
                    action_type=task_info['action_type'],
                    inputs=resolved_inputs,
                    context=action_context
                )

                # --- 4. IAR Compliance Vetting ---
                reflection = result.get('reflection')
                is_valid, issues = self.iar_validator.validate_structure(reflection)
                if not is_valid:
                    error_msg = f"IAR Compliance Failure in task '{task_key}': {', '.join(issues)}"
                    logger.critical(error_msg)
                    raise ValueError(error_msg)

                # --- 5. Context & State Update ---
                runtime_context[task_key] = result
                resonance_tracker.record_execution(task_key, reflection)
                display_task_result(task_key, result)
            except Exception as e:
                display_workflow_error(f"Execution failed for task '{task_key}': {e}", "N/A")
                return self._summarize_run(workflow_name, run_id, "Failed", start_time, runtime_context, resonance_tracker, str(e))

            completed_tasks.add(task_key)
            display_workflow_progress(task_key, "Completed")

            # --- 6. Update Ready Tasks ---
            self._update_ready_tasks(tasks, completed_tasks, ready_tasks)

        # --- Finalization ---
        final_status = "Completed Successfully" if len(completed_tasks) == len(tasks) else "Stalled (Dependency Deadlock)"
        summary = self._summarize_run(workflow_name, run_id, final_status, start_time, runtime_context, resonance_tracker)
        output_path = self._save_workflow_result(summary)
        display_workflow_complete(summary, output_path)
        return summary

    def _update_ready_tasks(self, all_tasks: Dict, completed: Set[str], ready: Set[str]):
        """Identifies and adds new tasks to the ready queue."""
        for task_id, task in all_tasks.items():
            if task_id not in completed and task_id not in ready:
                dependencies = task.get('dependencies', [])
                if all(dep in completed for dep in dependencies):
                    ready.add(task_id)

    def _resolve_value(self, value: Any, runtime_context: Dict, initial_context: Dict) -> Any:
        """Recursively resolves template strings `{{...}}` within any data structure."""
        if isinstance(value, dict):
            return {k: self._resolve_value(v, runtime_context, initial_context) for k, v in value.items()}
        if isinstance(value, list):
            return [self._resolve_value(item, runtime_context, initial_context) for item in value]
        if not isinstance(value, str) or "{{" not in value:
            return value

        # Full string replacement, e.g., `{{ task_a.output }}`
        full_match = re.fullmatch(r"\s*\{\{\s*(.*?)\s*\}\}\s*", value)
        if full_match:
            return self._evaluate_template_expression(full_match.group(1), runtime_context, initial_context)

        # Embedded string replacement, e.g., `File path is {{ context.path }}/data.csv`
        def repl(match):
            resolved = self._evaluate_template_expression(match.group(1), runtime_context, initial_context)
            if resolved is None: return "null"
            if isinstance(resolved, (dict, list)): return json.dumps(resolved)
            return str(resolved)
        
        return re.sub(r"\{\{\s*(.*?)\s*\}\}", repl, value)

    def _evaluate_template_expression(self, expression: str, runtime_context: Dict, initial_context: Dict) -> Any:
        """Evaluates a single `{{...}}` expression, including filters."""
        parts = expression.split('|')
        var_path = parts[0].strip()
        filters = parts[1:]

        # Resolve initial value
        if var_path.startswith("context."):
            current_value = self._get_value_from_path(var_path[len("context."):], initial_context)
        else:
            current_value = self._get_value_from_path(var_path, runtime_context)

        # Apply filters
        for f in filters:
            f = f.strip()
            if f == "toJson":
                current_value = json.dumps(current_value)
            # Add other filters here as needed
            # e.g., elif f.startswith("default("): ...
        
        return current_value

    def _get_value_from_path(self, path: str, context: Dict) -> Any:
        """Gets a value from a nested dictionary using a dot-separated path."""
        try:
            for key in path.split('.'):
                context = context[key]
            return context
        except (KeyError, TypeError, IndexError):
            return None

    def _evaluate_condition(self, condition_str: Optional[str], runtime_context: Dict, initial_context: Dict) -> bool:
        """Evaluates a condition string. Returns True if condition is met or absent."""
        if not condition_str:
            return True
        
        # Simple truthiness check: `{{ task_a.result }}` or `!{{ task_a.result }}`
        truth_match = re.fullmatch(r"\s*(!)?\s*\{\{\s*(.*?)\s*\}\}\s*", condition_str)
        if truth_match:
            negated, var_path = truth_match.groups()
            value = self._resolve_value(f"{{{{ {var_path} }}}}", runtime_context, initial_context)
            result = bool(value)
            return not result if negated else result

        # Comparison check: `{{ task_a.reflection.confidence }} > 0.8`
        comp_match = re.fullmatch(r"\s*\{\{\s*(.*?)\s*\}\}\s*(==|!=|>|<|>=|<=)\s*(.*)", condition_str)
        if comp_match:
            var_path, op, literal_val_str = comp_match.groups()
            actual_val = self._resolve_value(f"{{{{ {var_path} }}}}", runtime_context, initial_context)
            expected_val = ast.literal_eval(literal_val_str.strip())
            return self._compare_values(actual_val, op, expected_val)

        logger.warning(f"Unsupported condition format: '{condition_str}'. Defaulting to False.")
        return False

    def _compare_values(self, actual: Any, op: str, expected: Any) -> bool:
        """Compares two values using the given operator."""
        try:
            if op == '==': return actual == expected
            if op == '!=': return actual != expected
            if op == '>': return actual > expected
            if op == '<': return actual < expected
            if op == '>=': return actual >= expected
            if op == '<=': return actual <= expected
        except TypeError:
            logger.warning(f"Cannot compare types {type(actual)} and {type(expected)} with operator '{op}'.")
            return False
        return False

    def _summarize_run(self, workflow_name, run_id, status, start_time, runtime_context, tracker, error=None):
        """Creates the final summary dictionary for a workflow run."""
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        summary = {
            "workflow_name": workflow_name,
            "workflow_run_id": run_id,
            "workflow_status": status,
            "workflow_run_duration_sec": duration,
            "resonance_summary": tracker.get_run_summary(),
            "final_context": self._sanitize_for_json(runtime_context)
        }
        if error:
            summary["error_summary"] = str(error)
        
        return summary

    def _save_workflow_result(self, result: Dict[str, Any]) -> str:
        """Saves the final workflow result to a JSON file."""
        run_id = result.get("workflow_run_id", "unknown_run")
        filename = f"result_{run_id}.json"
        output_path = os.path.join(config.OUTPUT_DIR, filename)
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        return output_path

    def _sanitize_for_json(self, data: Any) -> Any:
        """Recursively sanitizes data to ensure it's JSON serializable."""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        if isinstance(data, dict):
            return {str(k): self._sanitize_for_json(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._sanitize_for_json(item) for item in data]
        if hasattr(data, 'isoformat'):
            return data.isoformat()
        if np and isinstance(data, np.integer):
            return int(data)
        if np and isinstance(data, np.floating):
            return float(data)
        if np and isinstance(data, np.ndarray):
            return data.tolist()
        return str(data)