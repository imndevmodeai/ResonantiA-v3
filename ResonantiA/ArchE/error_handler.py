# Handles errors, uses IAR context
pass 

# --- START OF FILE 3.0ArchE/error_handler.py ---
# ResonantiA Protocol v3.0 - error_handler.py
# Defines strategies for handling errors during workflow action execution.
# Leverages IAR context from error details for more informed decisions.

import logging
import time
from typing import Dict, Any, Optional, Union # Callable was removed as it's not used in this version

# Try to import config, provide a fallback if not found (e.g., running standalone)
try:
    from . import config as arche_config # Use an alias to avoid conflict if this file is named config.py
except ImportError:
    # Minimal fallback config if resonanita_config.py is not found
    class FallbackConfig:
        DEFAULT_ERROR_STRATEGY = 'retry'
        DEFAULT_RETRY_ATTEMPTS = 1
        METAC_DISSONANCE_THRESHOLD_CONFIDENCE = 0.6 # Example value
        KEYHOLDER_OVERRIDE_ACTIVE = False # Example value
        # Add other essential config defaults if error_handler directly uses them.
    arche_config = FallbackConfig()
    logging.warning("arche_config.py not found for error_handler, using fallback configuration values.")


logger = logging.getLogger(__name__)

# --- Error Handling Strategy Constants (align with ResonantiA v3.0) ---
STRATEGY_RETRY = "retry" # Default, includes backoff
STRATEGY_FAIL_FAST = "fail_fast"
STRATEGY_LOG_AND_CONTINUE = "log_and_continue" # Logs error but workflow proceeds
STRATEGY_TRIGGER_METACOG = "trigger_metacognitive_shift" # For deeper analysis/replanning

# --- Default Configuration Values (from arche_config or fallback) ---
DEFAULT_ERROR_STRATEGY: str = getattr(arche_config, 'DEFAULT_ERROR_STRATEGY', STRATEGY_RETRY).lower()
DEFAULT_RETRY_ATTEMPTS: int = getattr(arche_config, 'DEFAULT_RETRY_ATTEMPTS', 1)
LOW_CONFIDENCE_THRESHOLD: float = getattr(arche_config, 'METAC_DISSONANCE_THRESHOLD_CONFIDENCE', 0.6)
# Keyholder Override (conceptual, for future advanced error handling)
KEYHOLDER_OVERRIDE_ACTIVE: bool = getattr(arche_config, 'KEYHOLDER_OVERRIDE_ACTIVE', False)


def handle_action_error(
    task_id: str,
    action_type: str,
    error_details: Dict[str, Any], # Expected to contain 'error' and potentially 'reflection'
    context: Dict[str, Any],
    current_attempt: int,
    max_attempts: Optional[int] = None, # Max attempts for this specific task
    task_error_strategy: Optional[str] = None # Override strategy for this task
) -> Dict[str, Any]:
    """
    Determines the course of action when a workflow task action fails.
    Leverages IAR reflection data within error_details if available.

    Args:
        task_id (str): The ID of the task that failed.
        action_type (str): The type of action that failed.
        error_details (Dict): Dictionary containing error information. Crucially,
                              may contain the 'reflection' dict from the failed action.
        context (Dict): The current workflow context.
        current_attempt (int): The current attempt number for this action.
        max_attempts (Optional[int]): Max retry attempts allowed for this task.
                                      Defaults to arche_config.DEFAULT_RETRY_ATTEMPTS + 1.
        task_error_strategy (Optional[str]): Specific strategy override for this task.
                                             Defaults to arche_config.DEFAULT_ERROR_STRATEGY.

    Returns:
        Dict[str, Any]: A dictionary indicating the outcome:
            {'status': 'retry' | 'fail' | 'continue' | 'trigger_metacog'}
            Optionally includes 'reason' or 'delay_sec' for retries.
    """
    # Determine strategy and max attempts
    strategy = (task_error_strategy or DEFAULT_ERROR_STRATEGY).lower()
    # max_retries is the total number of times an action can run (1 initial + N retries)
    max_total_attempts = (max_attempts if max_attempts is not None else (DEFAULT_RETRY_ATTEMPTS + 1))


    # Extract error message and IAR reflection from details
    error_message = error_details.get('error', 'Unknown error')
    failed_action_reflection = error_details.get('reflection')

    logger.warning(f"Handling error for Task '{task_id}' (Action: {action_type}, Attempt: {current_attempt}/{max_total_attempts}, Strategy: {strategy})")
    logger.debug(f"Error Details: {error_message}")

    if failed_action_reflection and isinstance(failed_action_reflection, dict):
        logger.debug(f"Failed Action IAR: Status='{failed_action_reflection.get('status')}', Confidence={failed_action_reflection.get('confidence')}, Issues={failed_action_reflection.get('potential_issues')}")
    else:
        logger.debug("No valid IAR reflection data available in error details.")

    # --- Keyholder Override Check (Conceptual) ---
    if KEYHOLDER_OVERRIDE_ACTIVE:
        # Placeholder for Keyholder logic - e.g., force fail, force continue, or specific retry.
        # This would involve checking an external signal or pre-set override condition.
        logger.info(f"Keyholder Override is active. [Placeholder for override logic affecting task '{task_id}']")
        # Example: return {'status': 'fail', 'reason': "Keyholder override: Forced failure."}

    # --- Strategy Implementation ---

    # 1. Fail Fast Strategy
    if strategy == STRATEGY_FAIL_FAST:
        logger.error(f"Strategy '{STRATEGY_FAIL_FAST}': Task '{task_id}' failed definitively.")
        return {'status': 'fail', 'reason': f"Fail fast strategy invoked on attempt {current_attempt}."}

    # 2. Log and Continue Strategy
    elif strategy == STRATEGY_LOG_AND_CONTINUE:
        logger.warning(f"Strategy '{STRATEGY_LOG_AND_CONTINUE}': Logging error for task '{task_id}' and continuing workflow.")
        # The task is still marked as 'failed' in the workflow, but the workflow proceeds.
        # The 'error_details' will be stored as the task's result.
        return {'status': 'fail', 'reason': f"Logged error and continued past task '{task_id}' as per strategy."} # 'fail' here means task fails, workflow continues

    # 3. Retry Strategy (Default, with exponential backoff)
    elif strategy == STRATEGY_RETRY:
        if current_attempt < max_total_attempts:
            delay_seconds = min(1.0 * (2 ** (current_attempt -1)), 30) # Exponential backoff, cap at 30s
            logger.info(f"Strategy '{STRATEGY_RETRY}': Task '{task_id}' will be retried. Attempt {current_attempt + 1} of {max_total_attempts}. Delaying for {delay_seconds:.2f}s.")
            return {'status': 'retry', 'delay_sec': delay_seconds, 'reason': f"Retrying attempt {current_attempt + 1}."}
        else:
            logger.error(f"Strategy '{STRATEGY_RETRY}': Task '{task_id}' failed after exhausting all {max_total_attempts} attempts.")
            return {'status': 'fail', 'reason': f"Exhausted all {max_total_attempts} retry attempts."}

    # 4. Trigger Metacognitive Shift Strategy
    elif strategy == STRATEGY_TRIGGER_METACOG:
        # Check if conditions warrant triggering meta-shift (e.g., low confidence failure)
        confidence = failed_action_reflection.get('confidence') if isinstance(failed_action_reflection, dict) else None
        if confidence is not None and confidence < LOW_CONFIDENCE_THRESHOLD:
             logger.info(f"Strategy '{STRATEGY_TRIGGER_METACOG}': Triggering due to low confidence ({confidence:.2f}) failure in task '{task_id}'.")
             # Pass relevant context, including the error and IAR data
             trigger_context = {
                 "dissonance_source": f"Action '{action_type}' failed in task '{task_id}' with low confidence ({confidence:.2f}). Error: {error_message}",
                 "triggering_task_id": task_id,
                 "failed_action_details": error_details # Includes error and reflection
             }
             # This status signals the WorkflowEngine to potentially invoke a meta-workflow.
             # For now, it will likely behave like 'fail' unless engine has specific meta-workflow logic.
             return {'status': 'trigger_metacog', 'reason': "Low confidence failure detected, metacognitive shift indicated.", 'trigger_context': trigger_context}
        else:
             # If confidence is not low, or reflection unavailable, default to fail for this strategy.
             logger.error(f"Strategy '{STRATEGY_TRIGGER_METACOG}': Conditions not met (Confidence: {confidence}). Failing task '{task_id}'.")
             return {'status': 'fail', 'reason': f"Metacognitive shift conditions not met on attempt {current_attempt}. Defaulting to fail for task."}

    # Default Fallback (Should not be reached if strategy is valid and handled above)
    else:
        logger.error(f"Unknown or unhandled error handling strategy '{strategy}' for task '{task_id}'. Defaulting to 'fail'.")
        return {'status': 'fail', 'reason': f"Unknown error strategy '{strategy}'. Failing task."}

# Note: The simpler handle_action_error that wraps a single action_fn call has been removed
# as the WorkflowEngine now calls the more detailed version above directly.
# If a simple wrapper is needed elsewhere, it can be added separately.

# --- END OF FILE 3.0ArchE/error_handler.py --- 