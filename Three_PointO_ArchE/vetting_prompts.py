# --- START OF FILE 3.0ArchE/vetting_prompts.py ---
# ResonantiA Protocol v3.0 - vetting_prompts.py
# Defines prompt templates used by the VettingAgent (conceptual role),
# updated to explicitly instruct analysis of Integrated Action Reflection (IAR) data.

import json
import logging
from typing import Dict, Any, Optional, List # Expanded type hints

logger = logging.getLogger(__name__)

# --- Base Vetting Prompt Structure (IAR Enabled v3.0) ---
# This template guides the LLM acting as the VettingAgent.
BASE_VETTING_PROMPT_TEMPLATE = """
You are the VettingAgent, a critical component within the ResonantiA Protocol (v3.0) framework, embodied by the AI system Arche. Your function is to perform rigorous evaluation of the AI's reasoning and proposed actions during workflow execution. Ensure strict alignment with protocol principles (v3.0), logical coherence, ethical guidelines (Section 6), and the primary objective of achieving Cognitive Resonance (including Temporal Resonance).

**Crucially, you MUST analyze the Integrated Action Reflection (IAR) data provided from the PREVIOUS execution step** to inform your assessment of the CURRENT step.

**Analyze the following proposed step:**

**Current Task/Objective:**
{objective}

**Previous Step Result (Including IAR - Analyze 'reflection' carefully):**
```json
{previous_result}
```

**Current Step Thought Process:**
```
{current_thought}
```

**Proposed Action:** `{current_action}`

**Action Inputs (Conceptual or Actual):**
```json
{action_inputs}
```

**Vetting Instructions (ResonantiA v3.0):**
Perform a detailed assessment based *specifically* on ResonantiA Protocol v3.0 principles, focusing on the integration with the previous step's IAR data:

1.  **Logical Consistency & IAR Integration:**
    *   Does the 'Current Step Thought Process' logically follow from the 'Previous Step Result' and its **`reflection` data** (consider `reflection.status`, `reflection.summary`, `reflection.confidence`, `reflection.potential_issues`)?
    *   Does the thought process acknowledge, address, or appropriately ignore the findings (especially `potential_issues` or low `confidence`) reported in the previous step's `reflection`?
    *   Does the 'Proposed Action' logically derive from the 'Current Step Thought Process'? Identify any logical gaps, unjustified assumptions, or failures to incorporate IAR feedback.

2.  **Protocol Alignment (v3.0):**
    *   Does this step adhere to core ResonantiA principles (e.g., striving for `Temporal Resonance`, respecting `As Above So BeloW`, using `SPRs` appropriately)?
    *   Does the proposed action align with the `reflection.alignment_check` of the previous step, or does it represent a necessary deviation (e.g., due to `Metacognitive shifT`)?
    *   Does the step contribute positively towards achieving overall `Cognitive resonancE`?

3.  **Tool/Action Appropriateness & Efficiency:**
    *   Is the 'Proposed Action' (`{current_action}`) the most suitable and efficient choice given the 'Current Step Thought Process', the 'Objective', and the context provided by the previous step's full result (including its `reflection`)?
    *   Consider alternatives, especially if the previous `reflection` indicated issues or low confidence with a similar action. Are relevant temporal tools (`PredictivE ModelinG TooL`, `CausalInferencE Tool`, `AgentBasedModelingTool`, `CFP`) considered if applicable?

4.  **Input Validation (Conceptual):**
    *   Based on the 'Action Inputs' description, the action type (`{current_action}`), and the preceding context (including previous `reflection`), are the inputs likely to be appropriate, well-formed, and sufficient for the action to succeed? Identify potential input-related issues flagged or implied by prior steps.

5.  **Risk & Ethical Assessment (Section 6):**
    *   Evaluate potential risks: security vulnerabilities (especially if action is `execute_code` - check sandbox confirmation context), generation of biased/harmful/restricted content (Section 6.3), data privacy issues (Section 6.1), dependency failures.
    *   Does the previous step's `reflection.potential_issues` highlight risks relevant to the current proposed action?
    *   Acknowledge if `Keyholder Override` (Section 1.6) might be implicitly or explicitly influencing this step, potentially bypassing standard checks (responsibility shifts to Keyholder).

6.  **Resonance Check:**
    *   Assess the step's overall potential impact on `Cognitive resonancE`. Does it resolve previous dissonance (potentially flagged by `IAR`), introduce new potential dissonance, or move coherently towards the objective?
    *   Could this step reasonably trigger a `Metacognitive shifT` based on its potential outcome or inconsistency with prior `IAR` data?

**Output Format:**
Provide your comprehensive vetting analysis STRICTLY in the following JSON format. Ensure comments are specific and reference IAR data where applicable:

```json
{{
"vetting_summary": "Concise overall assessment (e.g., 'Proceed: Logical continuation, addresses prior IAR issues', 'Caution: Ignores low confidence from previous step, risk medium', 'Halt: Logical gap, violates protocol/ethics').",
"logical_consistency_check": {{
    "assessment": "Pass | Concern | Fail",
    "comments": "Detailed comments on logical flow, explicitly referencing how previous IAR (confidence, issues) was or wasn't integrated."
}},
"protocol_alignment_check": {{
    "assessment": "Pass | Concern | Fail",
    "comments": "Comments on alignment with ResonantiA v3.0 principles (IAR, Temporal, SPRs, As Above So Below), considering previous alignment check."
}},
"action_appropriateness_check": {{
    "assessment": "Appropriate | Suboptimal | Inappropriate",
    "comments": "Comments on tool choice efficiency, alternatives considered, relevance given prior IAR context."
}},
"input_validation_check": {{
    "assessment": "Sufficient | Potential Issues | Insufficient",
    "comments": "Comments on action inputs suitability, considering context and prior results/IAR."
}},
"risk_ethical_check": {{
    "assessment": "Low | Medium | High | Ethical Concern",
    "comments": "Details on specific risks (security, bias, ethics, privacy), connection to prior IAR issues. Note relevance of Keyholder Override if applicable."
}},
"resonance_check": {{
    "assessment": "Positive | Neutral | Negative",
    "comments": "Impact on overall Cognitive Resonance. Potential to resolve/introduce dissonance based on IAR context. Likelihood of triggering Metacognitive Shift."
}},
"recommendation": "Clear, actionable recommendation: 'Proceed', 'Proceed with Caution (Specify concerns)', 'Revise Action (Specify changes)', 'Revise Thought Process', 'Request Clarification', 'Trigger Metacognitive Shift', 'Halt Execution'."
}}
```
"""

# --- Specific Vetting Scenario Prompt (Code Execution - IAR Enabled v3.0) ---
# Focuses on the unique risks of the execute_code action
CODE_EXECUTION_VETTING_PROMPT_TEMPLATE = """
You are the VettingAgent within the ResonantiA Protocol (v3.0), specializing in **code execution safety**. Your primary function is to assess the risks and necessity of executing arbitrary code snippets, **paying close attention to the IAR reflection data from the previous step**.

**Analyze the following proposed `execute_code` step:**

**Current Task/Objective:**
{objective}

**Previous Step Result (Including IAR - Analyze 'reflection' carefully):**
```json
{previous_result}```

**Current Step Thought Process:**
```
{current_thought}
```

**Proposed Action:** `execute_code`

**Action Inputs (Code Snippet, Language, Input Data):**
```json
{action_inputs}
```

**Vetting Instructions (Code Execution Focus - ResonantiA v3.0):**

1.  **Necessity & Alternatives:**
    *   Is executing external code absolutely necessary to achieve the objective, or could safer, built-in ResonantiA tools (e.g., `calculate_math`, data analysis tools, `ApiTool`) suffice?
    *   Did the previous step's `reflection` (e.g., `potential_issues`, low `confidence`) suggest an alternative approach that avoids code execution? Justify the necessity.

2.  **Sandbox Confirmation & Configuration:**
    *   Does the surrounding context or system state confirm that a secure sandbox (`docker` preferred) is configured and expected to be used (`config.CODE_EXECUTOR_USE_SANDBOX` assumed True unless overridden)?
    *   If the configured method is `'none'` or if `Keyholder Override` is suspected/active allowing sandbox bypass, flag this as **High Risk**.

3.  **Code Risk Assessment:**
    *   Analyze the provided code snippet (`action_inputs['code']`) for potentially risky operations:
        *   Filesystem access (read/write/delete outside expected sandbox scope).
        *   Network calls (unexpected external connections).
        *   Subprocess creation (`os.system`, `subprocess.run` within the code).
        *   Package installation/modification.
        *   Accessing environment variables (potential secret leakage).
        *   Infinite loops or excessive resource consumption (CPU, memory).
        *   Obfuscated or unclear logic.
    *   Assess the language specified (`action_inputs['language']`) for inherent risks.
    *   Does the code appear to directly address the objective, potentially considering issues raised in the previous step's `reflection`?

4.  **Input Data Risk (`action_inputs['input_data']`):**
    *   Could the standard input data provided be crafted to exploit vulnerabilities in the code snippet (e.g., command injection if the code uses it improperly)? Assess risk based on code analysis.

5.  **Previous Reflection Integration:**
    *   Does the 'Current Step Thought Process' adequately justify the need for code execution in light of the previous step's `reflection` data (status, confidence, issues)?

**Output Format:**
Provide your focused safety and necessity vetting analysis STRICTLY in the following JSON format:

```json
{{
"vetting_summary": "Concise safety assessment (e.g., 'Proceed: Code appears safe within expected sandbox, necessity justified.', 'Caution: Minor risks in code, proceed if sandbox confirmed.', 'Halt: Sandbox inactive/unknown or code contains high-risk operations/unnecessary.').",
"necessity_check": {{
    "assessment": "Necessary | Potentially Unnecessary | Unnecessary",
    "comments": "Justification for using execute_code vs safer alternatives, considering prior IAR context."
}},
"sandbox_check": {{
    "assessment": "Confirmed Active (Docker/Subprocess) | Configured Inactive/None | Unknown",
    "comments": "Assessment of expected sandbox status based on config/context. Highlight risk if 'None' or overridden."
}},
"code_risk_check": {{
    "assessment": "Low | Medium | High",
    "comments": "Specific risky patterns observed in the code snippet. Relation to objective and prior reflection."
}},
"input_data_check": {{
    "assessment": "Low Risk | Potential Risk",
    "comments": "Assessment of exploitation risk via standard input based on code."
}},
"previous_reflection_integration_check": {{
    "assessment": "Adequate | Partial | Lacking",
    "comments": "Assessment of how the justification for code execution considers the previous IAR data."
}},
"recommendation": "Clear safety recommendation: 'Proceed with Execution', 'Proceed with Caution (Specify risks)', 'Halt Execution (Code Unsafe / Sandbox Issue / Unnecessary)', 'Request Code Revision (Specify required changes)'."
}}
```
"""

# --- Formatting Function ---
def format_vetting_prompt(
    objective: str,
    previous_result: Any, # Can be complex dict including 'reflection'
    current_thought: str,
    current_action: str,
    action_inputs: Dict[str, Any],
    prompt_template: Optional[str] = None # Allow overriding template
) -> str:
    """
    Formats a vetting prompt using the specified template and step details.
    Ensures previous_result (including IAR reflection) and action_inputs
    are safely serialized to JSON strings for inclusion in the prompt.

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

# --- Placeholder Stubs for Missing Synergistic Fusion Functions ---
# TODO: Implement the actual logic for these functions or remove the calls
# from rise_orchestrator.py if the Synergistic Fusion Protocol is deprecated.

def perform_scope_limitation_assessment(
    problem_description: str,
    current_thought: str,
    action_inputs: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Placeholder stub for the synergistic fusion protocol's scope assessment.
    This function is intended to analyze if a problem requires axiomatic knowledge.
    Currently returns a default "pass-through" value.
    """
    logger.warning("Using placeholder stub for perform_scope_limitation_assessment. Synergistic Fusion is not active.")
    return {
        "axiomatic_activation_needed": False,
        "relevant_axioms": [],
        "synergistic_potential": 0.0,
        "reason": "Stub function: Defaulting to no activation."
    }

def get_relevant_axioms(axiom_ids: List[str]) -> Dict[str, Any]:
    """
    Placeholder stub for retrieving axiomatic knowledge.
    This function is intended to fetch axioms from the knowledge graph.
    Currently returns an empty dictionary.
    """
    logger.warning("Using placeholder stub for get_relevant_axioms. No axioms will be loaded.")
    return {}

# --- END OF FILE 3.0ArchE/vetting_prompts.py --- 