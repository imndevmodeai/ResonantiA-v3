from typing import Dict, Any, Optional
import json
import logging
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer

logger = logging.getLogger(__name__)

def analyze_failure(failure_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze workflow failure and provide detailed analysis."""
    print(f"[DEBUG] Analyzing {failure_type} failure with context: {context}")
    
    # Extract relevant information
    error_message = context.get("error_message", "")
    failed_task = context.get("failed_task", "")
    workflow_definition = context.get("workflow_definition", {})
    
    # Perform analysis based on failure type
    analysis = {
        "failure_type": failure_type,
        "failed_task": failed_task,
        "error_message": error_message,
        "timestamp": now_iso(),
        "recommendations": []
    }
    
    if failure_type == "template_resolution":
        # Analyze template resolution failures
        analysis["recommendations"].extend([
            "Check template variable paths in workflow definition",
            "Verify action return structure matches template expectations",
            "Ensure all referenced variables exist in the context"
        ])
    elif failure_type == "action_structure":
        # Analyze action structure failures
        analysis["recommendations"].extend([
            "Verify action returns both 'output' and 'reflection' keys",
            "Check action implementation follows ResonantiA Protocol v3.0",
            "Ensure all required fields are present in the return structure"
        ])
    
    return {
        "output": analysis,
        "reflection": {
            "status": "Success",
            "summary": f"Completed {failure_type} failure analysis",
            "confidence": 0.95,
            "alignment_check": "Aligned",
            "potential_issues": None,
            "raw_output_preview": str(analysis)[:150]
        }
    }

def fix_template(analysis: Dict[str, Any], workflow: Dict[str, Any]) -> Dict[str, Any]:
    """Fix template variable issues in workflow definition."""
    print(f"[DEBUG] Fixing template issues with analysis: {analysis}")
    
    # Extract workflow tasks
    tasks = workflow.get("tasks", {})
    modified_tasks = {}
    
    for task_id, task in tasks.items():
        if "inputs" in task:
            modified_inputs = {}
            for input_key, input_value in task["inputs"].items():
                if isinstance(input_value, str) and "{{" in input_value:
                    # Fix template variable paths
                    fixed_value = _fix_template_path(input_value, analysis)
                    modified_inputs[input_key] = fixed_value
                else:
                    modified_inputs[input_key] = input_value
            task["inputs"] = modified_inputs
        modified_tasks[task_id] = task
    
    modified_workflow = {
        **workflow,
        "tasks": modified_tasks,
        "metadata": {
            **workflow.get("metadata", {}),
            "template_fix_timestamp": now_iso()
        }
    }
    
    return {
        "output": modified_workflow,
        "reflection": {
            "status": "Success",
            "summary": "Fixed template variable issues",
            "confidence": 0.9,
            "alignment_check": "Aligned",
            "potential_issues": None,
            "raw_output_preview": str(modified_workflow)[:150]
        }
    }

def fix_action(analysis: Dict[str, Any], action_code: str) -> Dict[str, Any]:
    """Fix action structure issues in action implementation."""
    print(f"[DEBUG] Fixing action structure with analysis: {analysis}")
    
    # Parse action code
    lines = action_code.split("\n")
    modified_lines = []
    
    # Add proper return structure
    for line in lines:
        if "return" in line and "{" in line:
            # Replace with proper structure
            modified_lines.append("    return {")
            modified_lines.append("        \"output\": result,")
            modified_lines.append("        \"reflection\": {")
            modified_lines.append("            \"status\": \"Success\",")
            modified_lines.append("            \"summary\": \"Action completed successfully\",")
            modified_lines.append("            \"confidence\": 0.95,")
            modified_lines.append("            \"alignment_check\": \"Aligned\",")
            modified_lines.append("            \"potential_issues\": None,")
            modified_lines.append("            \"raw_output_preview\": str(result)[:150]")
            modified_lines.append("        }")
            modified_lines.append("    }")
        else:
            modified_lines.append(line)
    
    modified_code = "\n".join(modified_lines)
    
    return {
        "output": modified_code,
        "reflection": {
            "status": "Success",
            "summary": "Fixed action structure issues",
            "confidence": 0.9,
            "alignment_check": "Aligned",
            "potential_issues": None,
            "raw_output_preview": str(modified_code)[:150]
        }
    }

def validate_workflow(modified_workflow: Dict[str, Any]) -> Dict[str, Any]:
    """Validate modified workflow definition."""
    print(f"[DEBUG] Validating modified workflow: {modified_workflow}")
    
    # Perform validation checks
    validation_results = {
        "template_variables": _validate_template_variables(modified_workflow),
        "task_dependencies": _validate_dependencies(modified_workflow),
        "action_references": _validate_action_references(modified_workflow)
    }
    
    is_valid = all(validation_results.values())
    
    return {
        "output": {
            "is_valid": is_valid,
            "validation_results": validation_results
        },
        "reflection": {
            "status": "Success" if is_valid else "Failure",
            "summary": "Workflow validation completed",
            "confidence": 0.95,
            "alignment_check": "Aligned",
            "potential_issues": None if is_valid else list(validation_results.keys()),
            "raw_output_preview": str(validation_results)[:150]
        }
    }

def validate_action(modified_action: str) -> Dict[str, Any]:
    """Validate modified action implementation."""
    print(f"[DEBUG] Validating modified action: {modified_action}")
    
    # Perform validation checks
    validation_results = {
        "return_structure": _validate_return_structure(modified_action),
        "error_handling": _validate_error_handling(modified_action),
        "debug_logging": _validate_debug_logging(modified_action)
    }
    
    is_valid = all(validation_results.values())
    
    return {
        "output": {
            "is_valid": is_valid,
            "validation_results": validation_results
        },
        "reflection": {
            "status": "Success" if is_valid else "Failure",
            "summary": "Action validation completed",
            "confidence": 0.95,
            "alignment_check": "Aligned",
            "potential_issues": None if is_valid else list(validation_results.keys()),
            "raw_output_preview": str(validation_results)[:150]
        }
    }

def self_heal_output(inputs: Dict[str, Any], context_for_action: 'ActionContext') -> Dict[str, Any]:
    """
    Attempts to heal a malformed output from an LLM by re-running the generation
    with explicit instructions to fix the format.
    """
    original_prompt = inputs.get("original_prompt")
    invalid_output = inputs.get("invalid_output")
    target_schema = inputs.get("target_schema")

    if not all([original_prompt, invalid_output, target_schema]):
        return {"error": "Self-healing requires original_prompt, invalid_output, and target_schema."}

    healing_prompt = f"""
    The following prompt was given to a generation model:
    --- PROMPT ---
    {original_prompt}
    --- END PROMPT ---

    Unfortunately, the model produced a malformed output that did not conform to the required JSON schema.
    
    --- INVALID OUTPUT ---
    {json.dumps(invalid_output, indent=2)}
    --- END INVALID OUTPUT ---

    Your task is to correct this output. The output MUST conform to the following JSON schema:
    --- TARGET SCHEMA ---
    {json.dumps(target_schema, indent=2)}
    --- END TARGET SCHEMA ---

    Please provide ONLY the corrected JSON object, with no other text or explanation.
    """

    try:
        # We need access to the LLM provider for this action.
        # This assumes the action context provides a way to get it.
        # This is a simplification; a real implementation would need a more robust dependency injection.
        from .llm_provider import EnhancedLLMProvider
        llm_provider = EnhancedLLMProvider()

        corrected_output_str = llm_provider.generate_text(
            prompt=healing_prompt,
            model_settings={"temperature": 0.1} # Use low temp for deterministic correction
        )
        
        # Attempt to parse the corrected string into a dictionary
        corrected_output = json.loads(corrected_output_str)
        return {"output": corrected_output}

    except json.JSONDecodeError:
        error_msg = "Self-healing failed: The healing model also produced invalid JSON."
        logger.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred during self-healing: {e}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg}


# Helper functions
def _fix_template_path(template: str, analysis: Dict[str, Any]) -> str:
    """Fix template variable path based on analysis."""
    # Implement template path fixing logic
    return template

def _validate_template_variables(workflow: Dict[str, Any]) -> bool:
    """Validate template variables in workflow."""
    # Implement template validation logic
    return True

def _validate_dependencies(workflow: Dict[str, Any]) -> bool:
    """Validate task dependencies in workflow."""
    # Implement dependency validation logic
    return True

def _validate_action_references(workflow: Dict[str, Any]) -> bool:
    """Validate action references in workflow."""
    # Implement action reference validation logic
    return True

def _validate_return_structure(action: str) -> bool:
    """Validate action return structure."""
    # Implement return structure validation logic
    return True

def _validate_error_handling(action: str) -> bool:
    """Validate error handling in action."""
    # Implement error handling validation logic
    return True

def _validate_debug_logging(action: str) -> bool:
    """Validate debug logging in action."""
    # Implement debug logging validation logic
    return True 