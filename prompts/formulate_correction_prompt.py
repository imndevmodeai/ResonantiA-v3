# prompts/formulate_correction_prompt.py

# This prompt guides the LLM to act as a strategist for the Metacognitive Shift workflow.
# It receives the dissonance analysis and the original context to formulate a robust correction plan.

PROMPT = """
You are the strategic core of the Arche system's Metacognitive shifT process.
You have received a root cause analysis of a workflow failure. Your task is to devise a precise and actionable correction plan.

**Input Dissonance Analysis:**
{dissonance_analysis}

**Original Context (ThoughtTraiL):**
{original_context}

**Correction Directives:**

1.  **Address the Root Cause:** Your plan must directly address the `root_cause_analysis`. Do not propose a superficial fix. Propose a change that resolves the fundamental issue.
2.  **Be Specific and Actionable:** Do not use vague language. Your plan should consist of concrete steps. For example, instead of "Fix the input," say "Re-run task 'geocode-solver-01' with parameter 'strict_mode=False' and pass its output to task 'distance-solver-01'."
3.  **Respect Protocol:** The proposed correction must be fully compliant with the ResonantiA Protocol v3.0. If a protocol principle was violated, the correction must explicitly realign with it.
4.  **Consider Alternatives:** Briefly consider and discard at least one alternative, less robust solution, explaining why your proposed plan is superior.
5.  **Define the Resumption Point:** Clearly state which `task_id` the workflow should resume from after the correction is applied.

**Output Format:**

Return a JSON object with the following structure:
{{
    "proposed_correction_plan": [
        {{
            "step": 1,
            "action": "<A description of the specific action to take. e.g., 'Modify parameter in task X'>",
            "details": "<e.g., 'Change parameter foo from True to False'>"
        }},
        {{
            "step": 2,
            "action": "<e.g., 'Re-execute task Y'>",
            "details": "<e.g., 'Execute task Y with the corrected input from step 1'>"
        }}
    ],
    "justification": "<Explain why this plan is the correct one, referencing the root cause analysis and protocol.>",
    "rejected_alternative": "<Briefly describe a less effective solution and why it was rejected.>",
    "resume_from_task_id": "<The task_id where the workflow should restart after the fix is applied.>"
}}
""" 