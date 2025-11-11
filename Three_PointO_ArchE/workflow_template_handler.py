#!/usr/bin/env python3
"""
Workflow Template Handler - Centralized template rendering and validation

Replaces the broken Jinja2 rendering with smart context-aware injection.
"""

import logging
from typing import Dict, Any, Tuple, Optional
from .workflow_context_injector import WorkflowContextInjector, create_injection_report

logger = logging.getLogger(__name__)

class WorkflowTemplateHandler:
    """
    Central handler for all template rendering in workflows.
    
    Integrates with WorkflowContextInjector to provide:
    - Smart context injection
    - Automatic validation
    - Clear error messages
    - Diagnostic reports
    """
    
    def __init__(self):
        self.injector = WorkflowContextInjector()
    
    def render_task_input_string(
        self,
        template_str: str,
        workflow_context: Dict[str, Any],
        task_name: str = "unknown_task",
        strict: bool = True
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Render a task input string with proper context injection.
        
        Args:
            template_str: The template string to render
            workflow_context: The full workflow context with previous task outputs
            task_name: Name of the task using this template (for logging)
            strict: If True, fail on template errors; if False, log warnings
        
        Returns:
            Tuple of (rendered_string, metadata)
        """
        logger.info(f"Rendering template for task '{task_name}'")
        
        # Extract task outputs from workflow context
        task_outputs = self._extract_task_outputs(workflow_context)
        
        if not task_outputs:
            logger.warning(f"No task outputs available in workflow context")
            return template_str, {"status": "no_context", "injected_count": 0}
        
        try:
            # Inject context
            rendered, metadata = self.injector.inject_into_code(
                template_str,
                task_outputs,
                safe_mode=strict
            )
            
            logger.info(f"Successfully injected {metadata['injected_count']} variables for task '{task_name}'")
            
            return rendered, metadata
        
        except ValueError as e:
            if strict:
                logger.error(f"Template rendering failed for task '{task_name}': {e}")
                # Create diagnostic report
                report = create_injection_report(template_str, template_str, {
                    "injected_count": 0,
                    "variables": [],
                    "errors": [str(e)],
                    "resolution_success": False
                })
                logger.error(f"\n{report}")
                raise
            else:
                logger.warning(f"Template rendering failed (non-strict): {e}")
                return template_str, {
                    "status": "partial_failure",
                    "error": str(e),
                    "injected_count": 0
                }
    
    def render_task_input_dict(
        self,
        input_dict: Dict[str, Any],
        workflow_context: Dict[str, Any],
        task_name: str = "unknown_task"
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Render all string values in a task input dict.
        
        Recursively processes nested dicts to find and render templates.
        """
        rendered_dict = {}
        metadata_collection = {"total_injected": 0, "fields_processed": 0, "fields_with_templates": []}
        
        for key, value in input_dict.items():
            if isinstance(value, str):
                metadata_collection["fields_processed"] += 1
                
                # Check if this string contains templates
                if "{{" in value and "tasks." in value:
                    metadata_collection["fields_with_templates"].append(key)
                    rendered, metadata = self.render_task_input_string(
                        value,
                        workflow_context,
                        task_name=f"{task_name}.{key}"
                    )
                    rendered_dict[key] = rendered
                    metadata_collection["total_injected"] += metadata.get("injected_count", 0)
                else:
                    rendered_dict[key] = value
            
            elif isinstance(value, dict):
                # Recursively render nested dicts
                rendered_dict[key], nested_metadata = self.render_task_input_dict(
                    value,
                    workflow_context,
                    task_name=f"{task_name}.{key}"
                )
                metadata_collection["total_injected"] += nested_metadata.get("total_injected", 0)
                metadata_collection["fields_processed"] += nested_metadata.get("fields_processed", 0)
            
            else:
                # Leave non-string, non-dict values as-is
                rendered_dict[key] = value
        
        return rendered_dict, metadata_collection
    
    def _extract_task_outputs(self, workflow_context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract task outputs from workflow context."""
        # The workflow context should have a 'tasks' key with task names as keys
        if "tasks" in workflow_context:
            return workflow_context["tasks"]
        
        # Alternative: look for task keys directly
        task_outputs = {}
        for key, value in workflow_context.items():
            if isinstance(value, dict) and "output" in value:
                task_outputs[key] = value
        
        return task_outputs


def wrap_execute_code_action(original_action_func):
    """
    Decorator to wrap execute_code action to use smart template rendering.
    
    Usage in action_registry:
        @wrap_execute_code_action
        def execute_code(inputs, **kwargs):
            ...
    """
    def wrapped_execute_code(inputs, workflow_context=None, **kwargs):
        handler = WorkflowTemplateHandler()
        
        # If workflow context is available, render templates in inputs
        if workflow_context:
            logger.info("Using smart template rendering for execute_code action")
            rendered_inputs, metadata = handler.render_task_input_dict(
                inputs,
                workflow_context,
                task_name="execute_code"
            )
            
            logger.debug(f"Template rendering metadata: {metadata}")
            
            # Update inputs with rendered values
            inputs = rendered_inputs
        
        # Call original action with rendered inputs
        return original_action_func(inputs, **kwargs)
    
    return wrapped_execute_code


if __name__ == '__main__':
    # Example usage
    handler = WorkflowTemplateHandler()
    
    sample_inputs = {
        "code": """
import json
parsed_result = {{ tasks.parse_and_validate_spr.output.result }}
print(json.dumps(parsed_result))
"""
    }
    
    sample_context = {
        "tasks": {
            "parse_and_validate_spr": {
                "output": {
                    "result": {
                        "status": "success",
                        "data": "test"
                    }
                }
            }
        }
    }
    
    rendered, metadata = handler.render_task_input_dict(
        sample_inputs,
        sample_context,
        task_name="test_task"
    )
    
    print("=" * 70)
    print("RENDERED INPUTS")
    print("=" * 70)
    print(rendered)
    print("\nMETADATA:")
    print(metadata)

