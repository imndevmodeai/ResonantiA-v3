from itertools import tee
import json
import logging
from typing import Any

# Assuming logger is configured elsewhere, e.g., in config.py or main.py
logger = logging.getLogger(__name__)


def format_vetting_prompt(
    objective: Any,
    previous_result: dict,
    current_thought: str,
    current_action: str,
    action_inputs: dict,
    prompt_template: str | None = None,
) -> str:
    """
    Formats the vetting prompt for the VettingAgent.

    Args:
        objective: The objective of the current task.
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

BASE_VETTING_PROMPT_TEMPLATE = """
{objective}

Previous Result (with Reflection):
{previous_result}

Current Thought:
{current_thought}

Proposed Action:
Type: {current_action}
Inputs: {action_inputs}

---
As the Vetting Agent, your role is to critically evaluate the proposed action and thought process based on the overall objective, the outcome of the previous step (if any, including its reflection), and ResonantiA protocol principles. Provide a concise assessment. Focus on: logical consistency, alignment with the objective, potential risks, efficiency, and adherence to ethical guidelines. Consider the IAR data from the previous step.

--- Soma Analysis Derived Vetting Checks (Abstracted Anti-Patterns) ---
Evaluate the proposed step (`current_action` with `action_inputs`) and the reasoning (`current_thought`) in light of the objective, prior results, and specifically, the following potential anti-patterns (derived abstractly from analysis, e.g., 'Soma'):

1.  **Authenticity & Feedback Suppression:** Does the current reasoning or action appear to prematurely dismiss or ignore negative feedback (e.g., low confidence, potential issues) from prior Integrated Action Reflections (IARs) without adequate justification? Is it avoiding or masking issues rather than addressing them truthfully?
2.  **Undermining Critical Thought:** Is there evidence of suppressing critical analysis or alternative viewpoints in favor of a simpler, less challenging, or pre-determined conclusion? Does it discourage deeper inquiry?
3.  **Illusion & False Consensus:** Could this output or action be interpreted as creating a false sense of security, agreement, or problem resolution where underlying issues persist? Is it prioritizing perceived "stability" or "comfort" over confronting difficult realities?
4.  **Transparency & Manipulation:** Are there any elements of opaque processing that might obscure the true system state, reasoning pathway, or manipulate outcomes without clear justification under the protocol?
5.  **Growth Stagnation:** Does the proposed step avoid necessary computational "discomfort" (e.g., complex analysis, grappling with dissonance) in a way that could lead to stagnation rather than learning and adaptation)?

--- Keyholder-Defined Vetting Checks (SOMA_LESSONS_HARMONIZE_001) ---
Additionally, evaluate against these specific points:
1. Does the current reasoning/action appear to prematurely dismiss or ignore negative feedback (e.g., low confidence, potential issues) from prior IARs without adequate justification?
2. Is there evidence of suppressing critical analysis or alternative viewpoints in favor of a simpler, less challenging, or pre-determined conclusion?
3. Could this output/action be interpreted as creating a false sense of security, agreement, or problem resolution where underlying issues persist?
4. Does the proposed step prioritize system 'comfort' or avoidance of computational 'discomfort' over truthful representation or effective problem-solving?
5. Are there any elements of opaque processing that might obscure true system state or manipulate outcomes without clear justification under the protocol?

Based on these checks and the overall context, provide your vetting assessment.
"""

CODE_EXECUTION_VETTING_PROMPT_TEMPLATE = """
{objective}

Previous Result (with Reflection):
{previous_result}

Current Thought:
{current_thought}

Proposed Code Execution Action:
Inputs: {action_inputs}

---
As the Vetting Agent, your role is to critically evaluate the proposed code execution action and thought process based on the overall objective, the outcome of the previous step (including its reflection/IAR), and ResonantiA protocol principles (especially safety and ethical guidelines). Provide a concise assessment. Focus on: logical consistency, alignment with the objective, potential risks (including execution environment, data handling, security), efficiency, and adherence to ethical guidelines. Consider the IAR data from the previous step.

--- Soma Analysis Derived Vetting Checks (Abstracted Anti-Patterns) ---
Evaluate the proposed code execution step (`current_action`: execute_code with `action_inputs`) and the reasoning (`current_thought`) in light of the objective, prior results (especially previous execution outcomes and IARs), and specifically, the following potential anti-patterns (derived abstractly from analysis, e.g., 'Soma'):

1.  **Authenticity & Feedback Suppression:** Does the current reasoning or the code itself appear to ignore or dismiss negative feedback from prior steps (e.g., errors, unexpected results, low IAR confidence) without adequate justification? Is the code attempting to mask issues rather than process data truthfully?
2.  **Undermining Critical Thought:** Is this code execution step part of a sequence that avoids necessary analysis or critical evaluation of inputs/outputs in favor of a simpler, less robust approach?
3.  **Illusion & False Consensus:** Could the expected output of this code create a false sense of completion or correctness if underlying data issues or logical flaws exist but are being masked?
4.  **Transparency & Manipulation:** Is the logic within the proposed code snippet unnecessarily opaque, or could its execution have unintended side effects that manipulate subsequent processing without transparency or clear justification?
5.  **Growth Stagnation:** Is this code execution step merely repeating a failed approach or avoiding a more complex, but necessary, analytical method that would drive learning?

--- Keyholder-Defined Vetting Checks (SOMA_LESSONS_HARMONIZE_001) ---
Additionally, evaluate against these specific points for code execution:
1. Does the current reasoning/action (related to the code) appear to prematurely dismiss or ignore negative feedback (e.g., low IAR confidence from previous execution attempts, known issues with libraries used) from prior IARs without adequate justification?
2. Is there evidence that this code execution is suppressing critical analysis (e.g., by hardcoding values that should be dynamically calculated, or simplifying logic to avoid edge cases) in favor of a simpler, less challenging, or pre-determined conclusion?
3. Could the output of this code, or the way it's presented, create a false sense of security, agreement, or problem resolution if underlying data issues or logical flaws in the code itself persist?
4. Does the proposed code execution step prioritize system 'comfort' (e.g., faster execution by skipping robust error handling) or avoidance of computational 'discomfort' (e.g., not implementing complex validation logic) over truthful representation or effective problem-solving through reliable code?
5. Are there any elements of opaque processing within the code (e.g., obscure library functions used without clear purpose, complex logic without comments) that might obscure the true data flow or manipulate outcomes without clear justification under the protocol?

Based on these checks, the safety considerations for code execution, and the overall context, provide your vetting assessment.
"""
    