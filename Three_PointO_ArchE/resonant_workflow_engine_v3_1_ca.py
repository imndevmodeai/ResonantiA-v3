# ResonantiA Protocol v3.1-CA - Canonical Workflow Engine
# File: Three_PointO_ArchE/resonant_workflow_engine_v3_1_ca.py
# Description: The synthesized, advanced, and IAR-compliant workflow orchestration
# engine. This module represents the fusion of graph-based dependency management,
# asynchronous execution, and the core principles of the ResonantiA Protocol.

import json
import os
import logging
import copy
import time
import re
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Union, Tuple, Callable
import ast

import networkx as nx

# --- Core ArchE Component Imports ---
# Assumes a standard package structure where these modules are siblings.
try:
    from . import config
    from .action_registry import execute_action, ACTION_REGISTRY
    from .spr_manager import SPRManager
    from .action_context import ActionContext
    from .output_handler import (
        display_task_result,
        display_workflow_progress,
        display_workflow_start,
        display_workflow_complete,
        display_workflow_error,
    )
except ImportError:
    # This block provides minimal stubs for standalone parsing and understanding,
    # but the engine is intended to run within the full ArchE package.
    print("Warning: Relative imports failed. Using stubs for standalone analysis.")
    class ConfigStub:
        OUTPUT_DIR = "outputs"
        LOG_LEVEL = "INFO"
    config = ConfigStub()
    ACTION_REGISTRY = {}
    async def execute_action(**kwargs): return {"reflection": {"status": "Failed", "summary": "Action registry not loaded."}}
    class SPRManager: pass
    class ActionContext: pass

logger = logging.getLogger(__name__)


# ==============================================================================
# IAR & RESONANCE VALIDATION COMPONENTS (v3.1-CA Standard)
# ==============================================================================

class IARValidator:
    """Validates IAR structure compliance per the ResonantiA Protocol."""

    def __init__(self):
        self.required_fields = [
            'status', 'summary', 'confidence', 'alignment_check',
            'potential_issues', 'raw_output_preview'
        ]

    def validate_structure(self, iar_data: Any) -> Tuple[bool, List[str]]:
        """Validates that the provided data adheres to the mandatory IAR structure."""
        if not isinstance(iar_data, dict):
            return False, ["IAR reflection must be a dictionary."]
        issues = [f for f in self.required_fields if f not in iar_data]
        if issues:
            return False, [f"Missing required IAR field: '{issue}'" for issue in issues]
        if iar_data['status'] not in ['Success', 'Partial', 'Failed']:
            issues.append(f"Invalid IAR status: '{iar_data['status']}'.")
        confidence = iar_data['confidence']
        if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
            issues.append(f"IAR confidence must be a float between 0.0 and 1.0, got {confidence}.")
        return not issues, issues

class ResonanceTracker:
    """Tracks resonance metrics for a single workflow run."""
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []

    def record_execution(self, task_key: str, iar_data: Dict[str, Any]):
        """Records a task's IAR data."""
        self.execution_history.append({
            'task_key': task_key,
            'status': iar_data.get('status'),
            'confidence': iar_data.get('confidence', 0.0),
            'tactical_resonance': iar_data.get('tactical_resonance', 0.0),
        })

    def get_run_summary(self) -> Dict[str, Any]:
        """Generates a summary report of the run's resonance."""
        if not self.execution_history:
            return {'total_tasks': 0, 'successful_tasks': 0, 'average_confidence': 0.0}
        
        successful = [ex for ex in self.execution_history if ex['status'] == 'Success']
        avg_conf = (sum(ex['confidence'] for ex in successful) / len(successful)) if successful else 0.0
        
        return {
            'total_tasks': len(self.execution_history),
            'successful_tasks': len(successful),
            'failed_tasks': len(self.execution_history) - len(successful),
            'average_confidence': round(avg_conf, 3),
        }

class IARManager:
    """Centralizes IAR validation and resonance tracking for the engine."""
    def __init__(self):
        self.validator = IARValidator()
        self.tracker = ResonanceTracker()

    def process_and_validate(self, task_key: str, action_type: str, tool_output: Dict[str, Any]) -> Dict[str, Any]:
        """Performs the mandatory IAR Compliance Vetting."""
        if "reflection" not in tool_output or not isinstance(tool_output["reflection"], dict):
            error_msg = f"IAR Compliance Failure in '{task_key}': 'reflection' key missing or invalid."
            logger.critical(error_msg)
            failure_iar = {
                "status": "Failed", "summary": error_msg, "confidence": 0.0,
                "alignment_check": "Misaligned", "potential_issues": [error_msg],
                "raw_output_preview": str(tool_output)[:200]
            }
            tool_output["reflection"] = failure_iar
        
        iar_data = tool_output["reflection"]
        is_valid, issues = self.validator.validate_structure(iar_data)
        if not is_valid:
            error_msg = f"IAR Structure Invalid in '{task_key}': {', '.join(issues)}"
            logger.error(error_msg)
            iar_data["status"] = "Failed"
            iar_data.setdefault("potential_issues", []).append(error_msg)
            iar_data["confidence"] = 0.0

        self.tracker.record_execution(task_key, iar_data)
        return tool_output


# ==============================================================================
# ResonantWorkflowEngine_v3_1_CA
# ==============================================================================

class ResonantWorkflowEngine_v3_1_CA:
    """
    Synthesized Advanced Workflow Orchestration Engine for ResonantiA Protocol v3.1-CA.
    """
    def __init__(self, spr_manager: Optional[SPRManager] = None):
        self.action_registry = ACTION_REGISTRY
        self.spr_manager = spr_manager or SPRManager()
        self.current_run_id: Optional[str] = None
        self.current_workflow_def: Optional[Dict[str, Any]] = None
        self.execution_graph = nx.DiGraph()
        logger.info("ResonantWorkflowEngine_v3_1_CA initialized.")

    def _load_and_build_graph(self, workflow_def: Dict[str, Any]):
        """Validates workflow and builds the execution graph."""
        if "tasks" not in workflow_def or not isinstance(workflow_def["tasks"], dict):
            raise ValueError("Workflow definition must have a 'tasks' dictionary.")
        
        self.current_workflow_def = workflow_def
        self.execution_graph.clear()
        self.execution_graph.add_nodes_from(workflow_def["tasks"].keys())

        for task_key, task_info in workflow_def["tasks"].items():
            for dep_key in task_info.get("dependencies", []):
                if dep_key not in self.execution_graph:
                    raise ValueError(f"Task '{task_key}' has an undefined dependency: '{dep_key}'.")
                self.execution_graph.add_edge(dep_key, task_key)
        
        if not nx.is_directed_acyclic_graph(self.execution_graph):
            cycles = list(nx.simple_cycles(self.execution_graph))
            raise ValueError(f"Workflow contains circular dependencies: {cycles}")

    # --- Core Resolution and Evaluation Logic (Synthesized from best versions) ---

    def _get_value_from_path(self, data: Dict, path_parts: List[str]) -> Any:
        """Helper to get a value from a nested dictionary using a dot-separated path."""
        current = data
        for part in path_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None  # Path not found
        return current

    def _resolve_value(self, value: Any, runtime_results: Dict, initial_context: Dict) -> Any:
        """
        Resolves template expressions within strings, lists, or dictionaries.
        Supports initial_context and runtime_results paths, and basic filters like 'default', 'toJson', 'replace'.
        Returns Python native types (str, int, float, bool, dict, list, None).
        """
        if isinstance(value, dict):
            return {k: self._resolve_value(v, runtime_results, initial_context) for k, v in value.items()}
        if isinstance(value, list):
            return [self._resolve_value(item, runtime_results, initial_context) for item in value]
        
        # If not a string, or if it's an empty string, return as is
        if not isinstance(value, str) or not value:
            return value

        # Iteratively resolve templates until no more templates are found or max iterations reached.
        max_iterations = 5 # Prevent infinite loops for complex or circular templates
        current_iteration = 0
        
        # This string will be iteratively updated by the regex substitution
        current_template_string = value

        while "{{" in current_template_string and "}}" in current_template_string and current_iteration < max_iterations:
            prev_template_string = current_template_string

            # Helper function to apply a single pass of template substitution
            def apply_single_pass_substitution(match):
                expression = match.group(1).strip()
                parts = [p.strip() for p in expression.split('|')]
                var_path_str = parts[0]
                filters = parts[1:]

                resolved_val_for_expression = None
                path_parts = var_path_str.split('.')

                # Data source prioritization
                if path_parts[0] == 'initial_context' and len(path_parts) > 1:
                    resolved_val_for_expression = self._get_value_from_path(initial_context, path_parts[1:])
                elif path_parts[0] in runtime_results:
                    resolved_val_for_expression = self._get_value_from_path(runtime_results, path_parts)
                elif var_path_str in initial_context:
                    resolved_val_for_expression = initial_context.get(var_path_str)
                elif var_path_str in runtime_results:
                    resolved_val_for_expression = runtime_results.get(var_path_str)
                
                # Apply filters
                for f_filter in filters:
                    if f_filter.startswith("default("):
                        if resolved_val_for_expression is None or (isinstance(resolved_val_for_expression, str) and resolved_val_for_expression.lower() == "null"):
                            default_value_match = re.match(r"default\\(([\\'\"])(.*?)\\1\\)", f_filter)
                            if default_value_match:
                                resolved_val_for_expression = default_value_match.group(2)
                            else:
                                logger.warning(f"Malformed default filter: {f_filter}. Skipping.")
                    elif f_filter == "toJson":
                        if resolved_val_for_expression is not None:
                            try:
                                # json.dumps produces a string. This is correct for toJson filter.
                                resolved_val_for_expression = json.dumps(resolved_val_for_expression, indent=2)
                            except TypeError as e:
                                logger.warning(f"Cannot apply toJson filter to non-JSON-serializable object: {resolved_val_for_expression}. Error: {e}")
                                resolved_val_for_expression = str(resolved_val_for_expression) # Fallback to string representation
                    elif f_filter.startswith("replace("):
                        replace_args_match = re.match(r"replace\\(([\\'\"])(.*?)\\1,\\s*([\\'\"])(.*?)\\3\\)", f_filter)
                        if replace_args_match:
                            old_str_quoted = replace_args_match.group(1) + replace_args_match.group(2) + replace_args_match.group(1)
                            new_str_quoted = replace_args_match.group(3) + replace_args_match.group(4) + replace_args_match.group(3)
                            
                            try:
                                old_str_unescaped = ast.literal_eval(old_str_quoted)
                                new_str_unescaped = ast.literal_eval(new_str_quoted)
                            except (ValueError, SyntaxError) as se:
                                logger.warning(f"Malformed replace filter arguments in '{f_filter}': {se}. Skipping this filter.")
                                continue

                            if isinstance(resolved_val_for_expression, str):
                                resolved_val_for_expression = resolved_val_for_expression.replace(old_str_unescaped, new_str_unescaped)
                        else:
                            logger.warning(f"Malformed replace filter: {f_filter}. Skipping.")
                
                # After filters, convert to appropriate Python type if possible, otherwise return string
                if resolved_val_for_expression is None:
                    return "null" # Represent Python None as "null" string within the template processing
                elif isinstance(resolved_val_for_expression, (dict, list, bool, int, float)):
                    # These are already native Python types, but for embedding in a string template,
                    # we need their string representation. For JSON, they'd be handled by json.dumps.
                    return str(resolved_val_for_expression)
                elif isinstance(resolved_val_for_expression, str):
                    # Try to convert to Python literal (True, False, 123, [1,2], etc.)
                    try:
                        return ast.literal_eval(resolved_val_for_expression)
                    except (ValueError, SyntaxError):
                        return resolved_val_for_expression # Not a literal string, return as is
                else:
                    return str(resolved_val_for_expression) # Fallback for other types

            # Apply the regex substitution for one pass
            current_template_string = re.sub(r"\\{\\{\\s*(.*?)\\s*\\}\\}", apply_single_pass_substitution, current_template_string)
            
            # If no change was made in this pass, break to prevent infinite loops
            if current_template_string == prev_template_string:
                break
            current_iteration += 1

        if current_iteration >= max_iterations and "{{" in current_template_string and "}}" in current_template_string:
            logger.warning(f"Template resolution reached max iterations ({max_iterations}) with unresolved templates: {current_template_string}")

        # Final conversion from string to Python literal if applicable for the whole resolved string
        if isinstance(current_template_string, str):
            # Special handling for "null" string to Python None
            if current_template_string.lower() == "null":
                # Only return None if it was originally "{{...}}" and resolved to "null",
                # not if "null" was a literal string from the start.
                # This is a bit heuristic, but helps with common cases.
                if value == current_template_string: # If original value was just "null" string
                    return current_template_string # Keep as string
                else:
                    return None # Assume template resolved to None
            
            # Try to convert the final string to a Python literal (True, False, numbers, lists, dicts)
            try:
                return ast.literal_eval(current_template_string)
            except (ValueError, SyntaxError):
                pass # Not a literal, return as string

        return current_template_string # Return the final resolved value

    def _evaluate_condition(self, condition_str: Optional[str], runtime_results: Dict, initial_context: Dict) -> bool:
        """
        Evaluates a condition string safely, supporting templating and basic comparisons.
        Ensures full resolution of template expressions before evaluation.
        """
        if not condition_str:
            return True

        resolved_condition_expr = self._resolve_value(condition_str, runtime_results, initial_context) # Initial resolution
        logger.debug(f"Condition string: '{condition_str}', Resolved condition expr: '{resolved_condition_expr}'")

        try:
            # If the resolved expression is still a string and contains templates, try resolving again fully.
            # This handles cases where _resolve_value might need multiple passes for deeply nested or complex templates.
            if isinstance(resolved_condition_expr, str) and "{{" in resolved_condition_expr and "}}" in resolved_condition_expr:
                 resolved_condition_expr = self._resolve_value(resolved_condition_expr, runtime_results, initial_context)

            # Handle direct boolean literals or 'null' string after resolution
            if isinstance(resolved_condition_expr, str):
                lower_expr = resolved_condition_expr.strip().lower()
                if lower_expr == 'true':
                    return True
                if lower_expr == 'false':
                    return False
                if lower_expr == 'null':
                    return False # Treat 'null' as false for condition evaluation

            # Try to parse simple comparison patterns: "operand1 operator operand2"
            # Regex captures operands and operator. Operands might still be template strings.
            match = re.match(r"^\s*(.+?)\s*(==|!=|<=|>=|<|>)\s*(.+?)\s*$", str(resolved_condition_expr))
            if match:
                left_raw, operator, right_raw = match.groups()

                # Recursively resolve both sides of the comparison
                left_operand = self._resolve_value(left_raw, runtime_results, initial_context)
                right_operand = self._resolve_value(right_raw, runtime_results, initial_context)

                # Helper to safely convert operand to a comparable Python literal
                def _safe_compare_val(val):
                    if isinstance(val, str):
                        val_str = val.strip().lower()
                        if val_str == 'true': return True
                        if val_str == 'false': return False
                        if val_str == 'null': return None
                        try:
                            # Attempt literal evaluation for numbers, lists, dicts, etc.
                            return ast.literal_eval(val)
                        except (ValueError, SyntaxError):
                            return val # Treat as raw string if not a literal
                    return val # If already not a string, return as is

                left_final = _safe_compare_val(left_operand)
                right_final = _safe_compare_val(right_operand)

                logger.debug(f"Condition operands (final): left='{left_final}', op='{operator}', right='{right_final}'")

                if operator == "==":
                    return left_final == right_final
                elif operator == "!=":
                    return left_final != right_final
                elif operator == "<=":
                    return left_final <= right_final
                elif operator == ">=":
                    return left_final >= right_final
                elif operator == "<":
                    return left_final < right_final
                elif operator == ">":
                    return left_final > right_final
            
            # If no comparison pattern matched, and it's not a direct boolean/null string, 
            # try to evaluate the whole expression as a boolean literal.
            if not isinstance(resolved_condition_expr, str):
                return bool(resolved_condition_expr)
            else:
                # Final attempt to evaluate as a literal boolean (e.g., if it was originally '{{var_that_is_true}}')
                try:
                    return bool(ast.literal_eval(resolved_condition_expr))
                except (ValueError, SyntaxError):
                    # If it's a non-literal string, treat it as true if not empty, false otherwise
                    # This aligns with Python's truthiness for non-empty strings.
                    return bool(resolved_condition_expr)

        except (ValueError, SyntaxError, TypeError) as e:
            logger.error(f"Could not evaluate condition expression '{condition_str}' (resolved to '{resolved_condition_expr}'): {e}. Defaulting to False.")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during condition evaluation for '{condition_str}' (resolved to '{resolved_condition_expr}'): {e}. Defaulting to False.", exc_info=True)
            return False

    # --- Asynchronous Task Execution ---

    async def _execute_task_wrapper(self, task_key: str, runtime_results: Dict, initial_context: Dict, iar_manager: IARManager) -> Dict:
        """A wrapper to execute a single task and handle its lifecycle."""
        task_info = self.current_workflow_def['tasks'][task_key]
        display_workflow_progress(task_key, "Starting")
        
        # 1. Condition Check (Phasegate)
        if not self._evaluate_condition(task_info.get('condition'), runtime_results, initial_context):
            display_workflow_progress(task_key, "Skipped (Condition Not Met)")
            skipped_iar = {"status": "Skipped", "summary": "Condition not met", "confidence": 1.0}
            return {"output": None, "reflection": skipped_iar}

        # 2. Input Resolution
        resolved_inputs = self._resolve_value(task_info.get('inputs', {}), runtime_results, initial_context)
        
        # 3. Action Execution
        action_context = ActionContext(
            task_key=task_key, action_name=task_info.get('description', task_key),
            action_type=task_info['action_type'], workflow_name=self.current_workflow_def['workflow_name'],
            run_id=self.current_run_id, runtime_context=runtime_results
        )
        
        try:
            tool_output = await execute_action(
                action_type=task_info['action_type'],
                inputs=resolved_inputs,
                context=action_context
            )
        except Exception as e:
            logger.error(f"Task '{task_key}' crashed during execution: {e}", exc_info=True)
            tool_output = {"reflection": {"status": "Failed", "summary": f"Unhandled exception: {e}", "confidence": 0.0}}

        # 4. IAR Vetting and Resonance Tracking
        final_output = iar_manager.process_and_validate(task_key, task_info['action_type'], tool_output)
        display_task_result(task_key, final_output)
        
        return final_output

    # --- Main Workflow Execution Method ---

    async def run_workflow(self, workflow_path_or_dict: Union[str, Dict], initial_context: Optional[Dict] = None) -> Dict:
        """Main entry point to run a workflow asynchronously using a dependency graph."""
        self.current_run_id = f"run_{uuid.uuid4().hex[:12]}"
        initial_context = initial_context or {}
        initial_context.setdefault("workflow_run_id", self.current_run_id)

        try:
            self._load_and_build_graph(workflow_path_or_dict)
        except Exception as e:
            display_workflow_error(str(e), "N/A")
            return {"workflow_status": "Failed", "error": str(e)}

        display_workflow_start(self.current_workflow_def['workflow_name'], self.current_run_id)
        start_time = time.monotonic()
        
        runtime_results = {}
        iar_manager = IARManager()
        
        # Execute tasks in topological order to respect dependencies
        for task_key in nx.topological_sort(self.execution_graph):
            # Check if all dependencies for the current task have completed successfully
            dependencies = list(self.execution_graph.predecessors(task_key))
            if any(runtime_results.get(dep, {}).get("reflection", {}).get("status") == "Failed" for dep in dependencies):
                display_workflow_progress(task_key, "Skipped (Upstream Failure)")
                runtime_results[task_key] = {"reflection": {"status": "Skipped", "summary": "Upstream dependency failed."}}
                continue

            try:
                task_result = await self._execute_task_wrapper(task_key, runtime_results, initial_context, iar_manager)
                runtime_results[task_key] = task_result
            except Exception as e:
                # This catches errors in the wrapper itself, though the wrapper should handle most things.
                display_workflow_error(f"Critical error in engine for task '{task_key}': {e}", "N/A")
                runtime_results[task_key] = {"reflection": {"status": "Failed", "summary": f"Engine critical error: {e}"}}
        
        # Final Summary
        duration = time.monotonic() - start_time
        final_status = "Completed Successfully"
        if any(res.get("reflection", {}).get("status") == "Failed" for res in runtime_results.values()):
            final_status = "Completed with Errors"

        summary = {
            "workflow_name": self.current_workflow_def["workflow_name"],
            "workflow_run_id": self.current_run_id,
            "workflow_status": final_status,
            "workflow_run_duration_sec": round(duration, 2),
            "resonance_summary": iar_manager.tracker.get_run_summary(),
            "final_outputs": {k: v.get("reflection") for k, v in runtime_results.items()}
        }
        
        output_path = self._save_workflow_result(summary)
        display_workflow_complete(summary, output_path)
        return summary

    def _save_workflow_result(self, result: Dict[str, Any]) -> str:
        """Saves the final workflow result to a JSON file."""
        log_dir = getattr(config, "OUTPUT_DIR", "outputs")
        os.makedirs(log_dir, exist_ok=True)
        filename = f"result_{result['workflow_run_id']}.json"
        output_path = os.path.join(log_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        return output_path