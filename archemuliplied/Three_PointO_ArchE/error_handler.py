# --- START OF FILE 3.0ArchE/error_handler.py ---
# ResonantiA Protocol v3.0 - error_handler.py
# Defines strategies for handling errors during workflow action execution.
# Leverages IAR context from error details for more informed decisions.

import logging
import time
from typing import Dict, Any, Optional
# Use relative imports for configuration
try:
    from . import config
except ImportError:
    # Fallback config if running standalone or package structure differs
    class FallbackConfig: DEFAULT_ERROR_STRATEGY='retry'; DEFAULT_RETRY_ATTEMPTS=1; METAC_DISSONANCE_THRESHOLD_CONFIDENCE=0.6
    config = FallbackConfig(); logging.warning("config.py not found for error_handler, using fallback configuration.")

logger = logging.getLogger(__name__)

# --- Default Error Handling Settings ---
DEFAULT_ERROR_STRATEGY = getattr(config, 'DEFAULT_ERROR_STRATEGY', 'retry').lower()
DEFAULT_RETRY_ATTEMPTS = getattr(config, 'DEFAULT_RETRY_ATTEMPTS', 1)
# Threshold from config used to potentially trigger meta-shift on low confidence failure
LOW_CONFIDENCE_THRESHOLD = getattr(config, 'METAC_DISSONANCE_THRESHOLD_CONFIDENCE', 0.6)

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
                                      Defaults to config.DEFAULT_RETRY_ATTEMPTS + 1.
        task_error_strategy (Optional[str]): Specific strategy override for this task.
                                             Defaults to config.DEFAULT_ERROR_STRATEGY.

    Returns:
        Dict[str, Any]: A dictionary indicating the outcome:
            {'status': 'retry' | 'fail' | 'continue' | 'trigger_metacog'}
            Optionally includes 'reason' or 'delay_sec' for retries.
    """
    # Determine strategy and max attempts
    strategy = (task_error_strategy or DEFAULT_ERROR_STRATEGY).lower()
    max_retries = max_attempts if max_attempts is not None else (DEFAULT_RETRY_ATTEMPTS + 1)

    # Extract error message and IAR reflection from details
    error_message = error_details.get('error', 'Unknown error')
    failed_action_reflection = error_details.get('reflection') # This is the IAR dict if available

    logger.warning(f"Handling error for Task '{task_id}' (Action: {action_type}, Attempt: {current_attempt}/{max_retries}, Strategy: {strategy})")
    logger.debug(f"Error Details: {error_message}")
    if failed_action_reflection and isinstance(failed_action_reflection, dict):
        logger.debug(f"Failed Action IAR: Status='{failed_action_reflection.get('status')}', Confidence={failed_action_reflection.get('confidence')}, Issues={failed_action_reflection.get('potential_issues')}")
    else:
        logger.debug("No valid IAR reflection data available in error details.")

    # --- Strategy Implementation ---

    # 1. Fail Fast Strategy
    if strategy == 'fail_fast':
        logger.error(f"Strategy 'fail_fast': Task '{task_id}' failed definitively.")
        return {'status': 'fail', 'reason': f"Fail fast strategy invoked on attempt {current_attempt}."}

    # 2. Retry Strategy (Default)
    elif strategy == 'retry':
        if current_attempt < max_retries:
            # Check for specific error types that might warrant *not* retrying
            # (e.g., authentication errors, invalid input errors that won't change)
            if "Authentication Error" in str(error_message) or "Invalid Argument" in str(error_message) or "Permission Denied" in str(error_message):
                 logger.error(f"Strategy 'retry': Non-recoverable error detected ('{error_message}'). Failing task '{task_id}' despite retry strategy.")
                 return {'status': 'fail', 'reason': f"Non-recoverable error on attempt {current_attempt}."}

            # Implement exponential backoff or fixed delay for retry
            delay = min(30, (2 ** (current_attempt - 1)) * 0.5) # Exponential backoff up to 30s
            logger.info(f"Strategy 'retry': Retrying task '{task_id}' in {delay:.1f} seconds (Attempt {current_attempt + 1}/{max_retries}).")
            time.sleep(delay) # Pause before returning retry status
            return {'status': 'retry', 'delay_sec': delay}
        else:
            logger.error(f"Strategy 'retry': Task '{task_id}' failed after reaching max attempts ({max_retries}).")
            return {'status': 'fail', 'reason': f"Maximum retry attempts ({max_retries}) reached."}

    # 3. Log and Continue Strategy
    elif strategy == 'log_and_continue':
        logger.warning(f"Strategy 'log_and_continue': Task '{task_id}' failed but workflow will continue. Error logged.")
        # The workflow engine will store the error details in the context for this task_id.
        return {'status': 'continue', 'reason': f"Log and continue strategy invoked on attempt {current_attempt}."}

    # 4. Trigger Metacognitive Shift Strategy
    elif strategy == 'trigger_metacognitive_shift':
        # Check if conditions warrant triggering meta-shift (e.g., low confidence failure)
        confidence = failed_action_reflection.get('confidence') if isinstance(failed_action_reflection, dict) else None
        if confidence is not None and confidence < LOW_CONFIDENCE_THRESHOLD:
             logger.info(f"Strategy 'trigger_metacognitive_shift': Triggering due to low confidence ({confidence:.2f}) failure in task '{task_id}'.")
             # Pass relevant context, including the error and IAR data
             trigger_context = {
                 "dissonance_source": f"Action '{action_type}' failed in task '{task_id}' with low confidence ({confidence:.2f}). Error: {error_message}",
                 "triggering_task_id": task_id,
                 "failed_action_details": error_details # Includes error and reflection
             }
             return {'status': 'trigger_metacog', 'reason': "Low confidence failure detected.", 'trigger_context': trigger_context}
        else:
             # If confidence is not low, or reflection unavailable, maybe just fail instead of meta-shift? Or retry once?
             # For now, let's fail if confidence isn't the trigger.
             logger.error(f"Strategy 'trigger_metacognitive_shift': Conditions not met (Confidence: {confidence}). Failing task '{task_id}'.")
             return {'status': 'fail', 'reason': f"Metacognitive shift conditions not met on attempt {current_attempt}."}

    # Default Fallback (Should not be reached if strategy is valid)
    else:
        logger.error(f"Unknown error handling strategy '{strategy}' for task '{task_id}'. Failing task.")
        return {'status': 'fail', 'reason': f"Unknown error strategy '{strategy}'."}

# --- END OF FILE 3.0ArchE/error_handler.py ---