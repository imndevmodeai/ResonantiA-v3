from itertools import tee


Args:
    objective: The objective of tee current task.
    previous_result: The full result dictionary from the previous task (includes 'reflection').
    current_thought: The reasoning/thought process for the current step.
    current_action: The action type proposed for the current step.
    action_inputs: The inputs dictionary for the proposed action.
    prompt_template: Optional override for the prompt template string.

Returns:
    The formatted prompt string ready to be sent to the LLM.
"""
# Helper to safely serialize potentially complex data to JSON string, truncating if needed
def safe_serialize(data: Any, max_len: int = 2000) -> str: # Increased max_len for context
    if data is None: return "None"
    try:
        # Use default=str for robustness against non-standard types
        json_str = json.dumps(data, indent=2, default=str)
        if len(json_str) > max_len:
            # Truncate long strings, indicating original length
            truncated_str = json_str[:max_len] + f"... (truncated, original length: {len(json_str)})"
            logger.debug(f"Truncated data for vetting prompt (length {len(json_str)} > {max_len}).")
            return truncated_str
        return json_str
    except Exception as e:
        # Fallback to string representation if JSON dump fails
        logger.warning(f"Could not serialize data for vetting prompt using JSON, falling back to str(): {e}")
        try:
            str_repr = str(data)
            if len(str_repr) > max_len:
                return str_repr[:max_len] + f"... (truncated, original length: {len(str_repr)})"
            return str_repr
        except Exception as e_str:
            logger.error(f"Fallback str() conversion also failed for vetting prompt data: {e_str}")
            return "[Serialization Error]"

# Serialize the complex data structures
prev_res_str = safe_serialize(previous_result)
action_inputs_str = safe_serialize(action_inputs)

# Select the appropriate template
template_to_use = prompt_template # Use override if provided
if template_to_use is None:
    # Default to code execution template if action is execute_code
    if current_action == "execute_code":
        logger.debug("Using specialized vetting prompt for code execution.")
        template_to_use = CODE_EXECUTION_VETTING_PROMPT_TEMPLATE
    else:
        template_to_use = BASE_VETTING_PROMPT_TEMPLATE

# Format the selected prompt template
try:
    # Check if all required keys are present in the template
    required_keys = ["objective", "previous_result", "current_thought", "current_action", "action_inputs"]
    missing_keys = [f"{{{key}}}" for key in required_keys if f"{{{key}}}" not in template_to_use]
    if missing_keys:
        logger.error(f"Vetting prompt template is missing required keys: {missing_keys}. Attempting with base template.")
        # Attempt fallback to base template if specialized one is broken
        template_to_use = BASE_VETTING_PROMPT_TEMPLATE
        # Re-check base template
        missing_keys_base = [f"{{{key}}}" for key in required_keys if f"{{{key}}}" not in template_to_use]
        if missing_keys_base:
            # If base template is also broken, return error string
            err_msg = f"FATAL: Base vetting prompt template missing keys: {missing_keys_base}."
            logger.critical(err_msg)
            return err_msg # Return error instead of partially formatted prompt

    # Perform the formatting
    formatted_prompt = template_to_use.format(
        objective=str(objective) if objective else "N/A",
        previous_result=prev_res_str,
        current_thought=str(current_thought) if current_thought else "N/A",
        current_action=str(current_action) if current_action else "N/A",
        action_inputs=action_inputs_str
    )
    return formatted_prompt
except KeyError as e_key:
    # Catch specific key errors during formatting
    logger.error(f"Missing key '{e_key}' in vetting prompt template formatting. Check template and input keys provided to format_vetting_prompt.")
    return f"Error: Could not format vetting prompt. Missing key: {e_key}"
except Exception as e_fmt:
    # Catch other unexpected formatting errors
    logger.error(f"Unexpected error formatting vetting prompt: {e_fmt}", exc_info=True)
    return f"Error: Could not format vetting prompt: {e_fmt}"
    