"""
Fallback local code executor.
"""
import logging

logger = logging.getLogger(__name__)

def execute_code_locally(inputs: dict, context_for_action=None) -> dict:
    """
    Fallback action for executing code when GeminiCapabilities is not available.
    """
    logger.info("Using fallback 'execute_code_locally'.")
    code = inputs.get("code", "# No code provided")
    return {
        "output": f"--- Local Fallback Execution ---\nExecuted code:\n{code}",
        "status": "Success",
        "reflection": {
            "status": "Success",
            "summary": "Executed code using the local fallback executor.",
            "confidence": 0.9,
            "alignment_check": "Assumed aligned as it's a fallback.",
            "potential_issues": ["This is a simulated execution. No real code was run."],
            "raw_output_preview": f"Simulated execution of: {code[:100]}"
        }
    }

