# 3. Adding New Cognitive Tools

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Step-by-step guide: define function, implement IAR, register in action_registry.py, add to workflow, test.
-->

This page provides a step-by-step guide for developers on how to add a new cognitive tool to the Arche system. Cognitive tools are the building blocks of Arche's workflows.

*   **Step 1: Define the Tool's Purpose and Scope**
    *   Clearly define what the new tool will do.
    *   Identify its inputs and expected primary outputs.
    *   Consider how it will contribute to the overall capabilities of Arche.
*   **Step 2: Create the Tool's Python Function**
    *   Create a new Python function for your tool. This can be in an existing module (e.g., `tools.py`, `enhanced_tools.py`) or a new module within the `3.0ArchE` package.
    *   **Adhere to [Coding Standards & Style](./02_Coding_Standards_And_Style.md):**
        *   Use type hints for all arguments and the return value.
        *   Write a comprehensive docstring (Google Style).
    *   **Function Signature:**
        *   The function should accept its parameters as arguments.
        *   It MUST return a dictionary containing two keys: `"results"` and `"reflection"`.
*   **Step 3: Implement the Tool's Core Logic**
    *   Write the code that performs the main action of your tool.
    *   This logic will populate the `results` part of the return dictionary.
*   **Step 4: Implement the Integrated Action Reflection (IAR) Contract (CRITICAL)**
    *   This is the most crucial part of adding a new tool.
    *   Your tool function MUST construct and return a `reflection` dictionary with the standard IAR fields. Refer to the [IAR Contract details](../04_Arche_Architecture_And_Internals/04_Action_Registry_and_Tool_Integration.md#the-integrated-action-reflection-iar-contract-mandatory-for-all-tools).
    *   **Inside your tool function, you need to:**
        1.  Determine the `status` ("Success", "Failure", "Partial").
        2.  Write a concise `summary` of the action and outcome.
        3.  Calculate a `confidence` score (0.0-1.0) based on the tool's performance, input quality, and result certainty.
        4.  Assess the `alignment_check` ("Aligned", "Potentially Misaligned", "N/A").
        5.  Compile a list of `potential_issues` (warnings, errors, caveats, limitations, biases).
        6.  Optionally include `raw_output_preview`, `error_message`, `execution_time_ms`, etc.
    *   **Include the IAR Comment Block** in your function's docstring or as a leading comment, as described in [Coding Standards & Style](./02_Coding_Standards_And_Style.md#integrated-action-reflection-iar-comment-block).
*   **Step 5: Register the Tool in `action_registry.py`**
    *   Open `3.0ArchE/action_registry.py`.
    *   Import your new tool function if it's in a new module.
    *   Add a new entry to the `ACTION_REGISTRY` dictionary:
        ```python
        # In action_registry.py
        from . import my_new_tool_module # If your tool is in a new file

        ACTION_REGISTRY = {
            # ... existing tools ...
            "your_new_tool_action_type": my_new_tool_module.your_tool_function_name,
            # or if in an existing module like tools.py:
            # "your_new_tool_action_type": tools.your_tool_function_name,
        }
        ```
    *   The `"your_new_tool_action_type"` is the string you will use in workflow JSON files to call your tool.
*   **Step 6: Add the Tool to a Workflow for Testing**
    *   Create or modify a workflow JSON file in the `workflows/` directory.
    *   Add a new task that uses your tool's `action_type`:
        ```json
        {
            "task_id": "test_my_new_tool",
            "action_type": "your_new_tool_action_type",
            "inputs": {
                "param1_name": "some_value",
                "param2_name": "{{another_task.results.output_key}}"
            },
            "dependencies": ["another_task"] // If applicable
        }
        ```
*   **Step 7: Test Thoroughly**
    *   Run the workflow. See [Running Your First Workflow](../02_Getting_Started_with_Arche/04_Running_Your_First_Workflow.md).
    *   Examine the output JSON file in the `outputs/` directory.
    *   **Verify both `results` and `reflection`:**
        *   Are the primary `results` correct?
        *   Is the `reflection` dictionary accurate? Does `confidence` make sense? Are `potential_issues` correctly reported? Is the `status` appropriate?
    *   Test with various inputs, including edge cases and potential error conditions, to ensure your IAR reporting is robust.
    *   See [Testing & Debugging](./06_Testing_And_Debugging.md) for more general guidance.
*   **Step 8: Document Your Tool**
    *   Add a new entry or update the relevant page in the Wiki (e.g., [Core Cognitive Tools](../03_Using_Arche_Workflows_And_Tools/02_Core_Cognitive_Tools.md) or create a new page if it's a major new category).
    *   Document its purpose, input parameters, output structure, and critically, its IAR behavior (this can often be adapted from your IAR comment block).
*   **Step 9: Submit a Pull Request**
    *   Follow the [Contribution Guidelines](./01_Contribution_Guidelines.md).

**Example (Conceptual):**

```python
# In 3.0ArchE/my_custom_tools.py
from typing import Dict, Any, List

def analyze_sentiment(text_input: str, language: str = "en") -> Dict[str, Any]:
    """Analyzes the sentiment of a given text.

    IAR Contract Fulfillment:
      - confidence: Based on the sentiment model's internal confidence score for the prediction.
      - potential_issues:
          - "Language not supported by sentiment model: [language]"
          - "Sentiment analysis failed: [error_detail]"
          - "Text too short for meaningful analysis"
      - status: "Success" if analysis completes, "Failure" otherwise.
      - alignment_check: "Aligned" if analysis successful, "N/A" otherwise.
    Args:
        text_input: The text to analyze.
        language: The language of the text (default: "en").

    Returns:
        A dictionary with keys "results" and "reflection".
        "results" contains: {"sentiment": "positive"|"negative"|"neutral", "score": float}.
    """
    results_data = {}
    reflection_data = {
        "status": "Failure", # Default to failure
        "summary": "Sentiment analysis attempted.",
        "confidence": 0.0,
        "alignment_check": "N/A",
        "potential_issues": [],
        "raw_output_preview": text_input[:50] + "..."
    }

    try:
        # --- Dummy sentiment analysis logic --- 
        if language != "en":
            reflection_data["potential_issues"].append(f"Language not supported by sentiment model: {language}")
            # Status remains "Failure" or could be "Partial" depending on design
            return {"results": results_data, "reflection": reflection_data}
        
        if len(text_input) < 10:
            reflection_data["potential_issues"].append("Text too short for meaningful analysis")
            reflection_data["status"] = "Partial" # Example of partial success
            reflection_data["confidence"] = 0.3
            results_data = {"sentiment": "neutral", "score": 0.5} # Default/fallback result
        elif "great" in text_input.lower():
            results_data = {"sentiment": "positive", "score": 0.9}
            reflection_data["confidence"] = 0.9
            reflection_data["status"] = "Success"
        elif "bad" in text_input.lower():
            results_data = {"sentiment": "negative", "score": 0.85}
            reflection_data["confidence"] = 0.85
            reflection_data["status"] = "Success"
        else:
            results_data = {"sentiment": "neutral", "score": 0.6}
            reflection_data["confidence"] = 0.6
            reflection_data["status"] = "Success"
        # --- End dummy logic ---

        if reflection_data["status"] == "Success":
            reflection_data["summary"] = f"Sentiment analyzed as {results_data['sentiment']} with score {results_data['score']}."
            reflection_data["alignment_check"] = "Aligned"
        elif reflection_data["status"] == "Partial":
             reflection_data["summary"] = f"Sentiment analysis partially completed due to: {reflection_data['potential_issues']}."

    except Exception as e:
        reflection_data["potential_issues"].append(f"Sentiment analysis failed: {str(e)}")
        reflection_data["summary"] = f"Sentiment analysis failed with error: {str(e)}"
        # Confidence remains 0.0, status remains "Failure"

    return {"results": results_data, "reflection": reflection_data}

```

*By meticulously following these steps, especially the IAR contract, new tools will integrate seamlessly into Arche's reflective and adaptive ecosystem.* 