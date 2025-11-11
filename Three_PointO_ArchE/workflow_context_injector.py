#!/usr/bin/env python3
"""
Workflow Context Injector - Smart Template Resolution for Inter-Task Communication

This module solves the pattern of tasks needing to reference outputs from previous tasks.
Instead of raw Jinja2 templates, this provides intelligent context injection with:
- Automatic variable extraction and injection
- Pre-execution validation
- Clear error diagnostics
- Fallback mechanisms
"""

import re
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class TemplateVariable:
    """Represents a single template variable reference."""
    full_ref: str  # e.g., "tasks.parse_and_validate_spr.output.result"
    path_parts: List[str]  # e.g., ["parse_and_validate_spr", "output", "result"]
    line_number: int
    is_valid: bool = False
    resolved_value: Any = None
    error_message: str = ""

class WorkflowContextInjector:
    """
    Intelligently injects workflow task outputs into code snippets.
    
    Replaces naive Jinja2 rendering with a smart system that:
    1. Extracts task references from code
    2. Validates they exist in workflow context
    3. Injects values directly into code
    4. Provides clear diagnostics on failures
    """
    
    def __init__(self):
        self.template_pattern = re.compile(r'\{\{\s*tasks\.(\w+(?:\.\w+)*)\s*\}\}')
        self.task_ref_cache: Dict[str, Any] = {}
    
    def extract_template_variables(self, code: str) -> List[TemplateVariable]:
        """Extract all template variable references from code."""
        variables = []
        for line_num, line in enumerate(code.split('\n'), 1):
            for match in self.template_pattern.finditer(line):
                full_ref = match.group(0)
                path = match.group(1).split('.')
                
                variables.append(TemplateVariable(
                    full_ref=full_ref,
                    path_parts=path,
                    line_number=line_num
                ))
        
        return variables
    
    def validate_and_resolve(
        self,
        variables: List[TemplateVariable],
        task_outputs: Dict[str, Dict[str, Any]]
    ) -> Tuple[List[TemplateVariable], List[str]]:
        """
        Validate that all template variables can be resolved from task outputs.
        
        Returns:
            Tuple of (validated_variables, error_messages)
        """
        errors = []
        
        for var in variables:
            # First part is task name
            task_name = var.path_parts[0]
            
            if task_name not in task_outputs:
                errors.append(f"Line {var.line_number}: Task '{task_name}' not found in workflow outputs")
                var.error_message = f"Task '{task_name}' not in outputs"
                continue
            
            # Navigate the path
            current = task_outputs[task_name]
            for i, part in enumerate(var.path_parts[1:], 1):
                if not isinstance(current, dict):
                    errors.append(
                        f"Line {var.line_number}: Cannot access '{part}' - "
                        f"'{'.'.join(var.path_parts[:i])}' is not a dict (is {type(current).__name__})"
                    )
                    var.error_message = f"Path resolution failed at '{'.'.join(var.path_parts[:i])}'"
                    break
                
                if part not in current:
                    available = list(current.keys())[:5]
                    errors.append(
                        f"Line {var.line_number}: Key '{part}' not found in "
                        f"'{'.'.join(var.path_parts[:i])}'. Available: {available}"
                    )
                    var.error_message = f"Key '{part}' not found"
                    break
                
                current = current[part]
            else:
                # Successfully resolved
                var.is_valid = True
                var.resolved_value = current
        
        return variables, errors
    
    def inject_into_code(
        self,
        code: str,
        task_outputs: Dict[str, Dict[str, Any]],
        safe_mode: bool = True
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Intelligently inject task outputs into code.
        
        Args:
            code: Python code with Jinja2-style task references
            task_outputs: Dict of task_name -> task result
            safe_mode: If True, fail on any unresolvable variable
        
        Returns:
            Tuple of (injected_code, injection_metadata)
        
        Raises:
            ValueError: If safe_mode=True and variables cannot be resolved
        """
        # Extract variables
        variables = self.extract_template_variables(code)
        
        if not variables:
            # No template variables, return as-is
            return code, {"injected_count": 0, "variables": []}
        
        # Validate and resolve
        variables, errors = self.validate_and_resolve(variables, task_outputs)
        
        # Handle errors
        if errors:
            if safe_mode:
                error_msg = "Template variable resolution failed:\n" + "\n".join(errors)
                logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                logger.warning(f"Some template variables couldn't be resolved: {errors}")
        
        # Inject valid variables directly into code
        injected_code = code
        injected_variables = []
        
        for var in variables:
            if not var.is_valid:
                if safe_mode:
                    continue  # Skip invalid variables in safe mode
                else:
                    # In non-safe mode, comment out the reference
                    logger.warning(f"Skipping invalid variable at line {var.line_number}: {var.error_message}")
                    continue
            
            # Convert the value to a safe Python literal
            try:
                # For simple types, use repr(); for complex types, use json
                if isinstance(var.resolved_value, (str, int, float, bool, type(None))):
                    value_repr = repr(var.resolved_value)
                else:
                    value_repr = json.dumps(var.resolved_value)
                
                # Replace the template with the injected value
                injected_code = injected_code.replace(var.full_ref, value_repr)
                injected_variables.append({
                    "variable": var.full_ref,
                    "line": var.line_number,
                    "type": type(var.resolved_value).__name__,
                    "preview": str(var.resolved_value)[:100]
                })
                
                logger.debug(f"Injected {var.full_ref} at line {var.line_number}")
            
            except Exception as e:
                logger.error(f"Failed to inject {var.full_ref}: {e}")
                if safe_mode:
                    raise ValueError(f"Cannot inject {var.full_ref}: {e}")
        
        metadata = {
            "injected_count": len(injected_variables),
            "variables": injected_variables,
            "errors": errors,
            "resolution_success": len(errors) == 0
        }
        
        return injected_code, metadata
    
    def create_task_context_dict(
        self,
        task_outputs: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Generate Python code that recreates the task context as a dict.
        
        This can be prepended to user code to provide `tasks` as a variable.
        """
        # Create a safe serialization of task outputs
        try:
            tasks_dict_code = f"tasks = {json.dumps(task_outputs)}"
        except (TypeError, ValueError):
            # If not JSON serializable, use repr with comments
            logger.warning("Task outputs not JSON serializable, using repr()")
            tasks_dict_code = f"tasks = {repr(task_outputs)}"
        
        return tasks_dict_code


def create_injection_report(
    original_code: str,
    injected_code: str,
    metadata: Dict[str, Any]
) -> str:
    """Create a diagnostic report of the injection process."""
    report = []
    report.append("=" * 70)
    report.append("WORKFLOW CONTEXT INJECTION REPORT")
    report.append("=" * 70)
    
    report.append(f"\n✓ Variables Injected: {metadata['injected_count']}")
    report.append(f"✓ Resolution Success: {metadata['resolution_success']}")
    
    if metadata['variables']:
        report.append("\nInjected Variables:")
        for var in metadata['variables']:
            report.append(f"  • {var['variable']} ({var['type']})")
            report.append(f"    Line: {var['line']}, Value: {var['preview']}")
    
    if metadata['errors']:
        report.append(f"\n⚠ Errors ({len(metadata['errors'])}):")
        for error in metadata['errors']:
            report.append(f"  • {error}")
    
    report.append("\nOriginal Code:")
    report.append("-" * 70)
    report.append(original_code)
    
    report.append("\nInjected Code:")
    report.append("-" * 70)
    report.append(injected_code)
    
    report.append("\n" + "=" * 70)
    
    return "\n".join(report)


if __name__ == '__main__':
    # Example usage
    injector = WorkflowContextInjector()
    
    sample_code = """
import json
from difflib import SequenceMatcher

parsed_result = {{ tasks.parse_and_validate_spr.output.result }}
if parsed_result.get('status') != 'success':
    print(json.dumps(parsed_result))
else:
    new_spr = parsed_result['spr_definition']
    print(json.dumps(new_spr))
"""
    
    sample_task_outputs = {
        "parse_and_validate_spr": {
            "output": {
                "result": {
                    "status": "success",
                    "spr_definition": {
                        "spr_id": "test_spr",
                        "term": "Test",
                        "description": "A test SPR"
                    }
                }
            }
        }
    }
    
    try:
        injected, metadata = injector.inject_into_code(sample_code, sample_task_outputs)
        print(create_injection_report(sample_code, injected, metadata))
    except Exception as e:
        print(f"Error: {e}")

