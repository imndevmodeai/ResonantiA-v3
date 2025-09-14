# 4. Action Registry and Tool Integration (`action_registry.py`)

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Explain how new tools are registered and the IAR contract for tools.
-->

This page describes the `ActionRegistry` (typically in `action_registry.py`) and the process for integrating new tools into Arche, emphasizing the critical Integrated Action Reflection (IAR) contract.

*   **Purpose of the Action Registry**
    *   Acts as a central dispatcher that maps `action_type` strings (used in workflow JSON files) to the actual Python functions that implement the tool's logic.
    *   Decouples the `CoreWorkflowEngine` from the specific implementations of individual tools. This makes the system modular and easier to extend.
*   **Registering New Tools**
    *   **Method:** Typically involves adding an entry to a dictionary within `action_registry.py`.
    *   **Example:**
        ```python
        # In action_registry.py
        from . import tools, predictive_modeling_tool # etc.

        ACTION_REGISTRY = {
            "generate_text_llm": tools.invoke_llm,
            "search_web": tools.run_search,
            "execute_code": code_executor_instance.execute, # If it's a class method
            "run_prediction": predictive_modeling_tool.run_prediction_workflow_step,
            # ... other existing tools ...
            "new_custom_tool": my_new_module.my_tool_function, # Registering a new tool
        }

        def get_action(action_type):
            return ACTION_REGISTRY.get(action_type)
        ```
    *   The `CoreWorkflowEngine` calls `get_action(task['action_type'])` to retrieve the callable function.
*   **The Integrated Action Reflection (IAR) Contract (MANDATORY FOR ALL TOOLS)**
    *   **Purpose:** To ensure every action performed by Arche is self-aware of its execution quality, limitations, and alignment. This is fundamental for meta-cognition, adaptive workflows, and reliable system operation.
    *   **Requirement:** Every Python function registered as an action *MUST* return a dictionary. This dictionary has two top-level keys:
        *   `results`: Contains the primary output(s) of the tool.
The structure of `results` is tool-specific.
        *   `reflection`: Contains a standardized dictionary with the IAR data.
    *   **Standard Fields in the `reflection` Dictionary (Protocol Section 3.14):**
        *   `status`: (String) One of "Success", "Failure", "Partial", "Skipped". Indicates the outcome of the action.
        *   `summary`: (String) A concise, human-readable summary of what the action did and its outcome.
        *   `confidence`: (Float, typically 0.0-1.0) The tool's self-assessed confidence in the validity, accuracy, and completeness of its `results`. The interpretation is tool-specific but should be documented.
        *   `alignment_check`: (String) One of "Aligned", "Potentially Misaligned", "N/A". How well the action's outcome aligned with its intended purpose within the workflow and the broader goals.
        *   `potential_issues`: (List of strings) A list of any warnings, errors, limitations, caveats, biases, or assumptions relevant to the action's execution or its results. This is CRITICAL for debugging and for the `VettingAgenT`.
        *   `raw_output_preview`: (String, optional but recommended) A truncated string representation of the primary `results` for quick inspection in logs or by other system components.
        *   `error_message`: (String, optional) If `status` is "Failure", this should contain a specific error message.
        *   `execution_time_ms`: (Float, optional) Time taken to execute the action.
        *   (Other tool-specific reflection fields can be added if necessary, but the core ones above are mandatory).
    *   **Implementation within Tools:** Each tool developer is responsible for:
        1.  Performing the core logic of the tool.
        2.  Evaluating its own performance to populate the `reflection` fields accurately and honestly.
        3.  Returning the combined `{"results": ..., "reflection": ...}` dictionary.
*   **Benefits of the IAR Contract and Registry**
    *   **Modularity & Extensibility:** Easily add new capabilities (tools) without modifying the core engine.
    *   **System Self-Awareness:** IAR data provides a continuous stream of information about the system's internal state and performance.
    *   **Adaptive Behavior:** Workflows can use IAR data in `condition` fields to dynamically change their execution paths.
    *   **Enhanced Debugging & Auditing:** `potential_issues` and other reflection fields provide rich diagnostic information.
    *   **Foundation for Meta-Cognition:** `Metacognitive shifT` and `SIRC` heavily rely on analyzing IAR data to detect dissonance and guide reasoning.

*Adherence to the IAR contract is paramount for any new tool integrated into Arche. It is the cornerstone of the system's reflective and adaptive capabilities.* 