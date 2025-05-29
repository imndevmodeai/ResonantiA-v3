# 6. Creating Custom Workflows

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Provide best practices, common patterns, and error handling strategies for creating new workflow JSON files.
-->

This page provides guidance on creating your own custom workflows (Process blueprintS) for Arche.

*   **Best Practices for Workflow Design**
    *   **Modularity:** Break down complex processes into smaller, manageable tasks.
    *   **Clarity:** Use descriptive `task_id`s and `description` fields.
    *   **Explicit Dependencies:** Clearly define task `dependencies` to ensure correct execution order.
    *   **Robust Input Handling:** Ensure tasks correctly reference outputs from prior tasks (e.g., `{{task_id.results.key}}`). Consider potential variations in prior task outputs.
    *   **IAR-Driven Logic:** Actively use IAR data (e.g., `{{task_id.reflection.confidence}}`, `{{task_id.reflection.status}}`) in `condition` fields for adaptive workflow paths.
    *   **Configuration via Context:** Prefer passing dynamic parameters via the initial context (`-c` argument) rather than hardcoding them in the workflow JSON, where appropriate.
    *   **Iterative Development:** Start simple and add complexity incrementally. Test each part.
*   **Common Workflow Patterns**
    *   **Sequential Execution:** Tasks run one after another, defined by `dependencies`.
    *   **Parallel Execution:** Tasks with no dependencies on each other (or dependencies on the same prior set) can conceptually run in parallel (actual parallelism depends on `CoreWorkflowEngine` implementation, but the DAG allows it).
    *   **Conditional Branching:** Using the `condition` field based on data or IAR from a previous task to choose different execution paths.
        *   Example: If search confidence is low, perform an alternative search or ask for clarification.
    *   **Data Aggregation/Fan-in:** Multiple tasks complete, and their results are then used as inputs to a single subsequent task (e.g., summarizing multiple search results).
    *   **Looping (Conceptual):** While direct looping constructs aren't in the basic JSON, conceptual loops can be achieved by: 
        *   Calling a sub-workflow that performs an iteration and decides whether to call itself again (requires advanced `CoreWorkflowEngine` or manual re-triggering).
        *   Using a controlling task that conditionally re-runs a sequence of tasks if a condition isn't met (can be complex to manage state).
        *   (Note: True programmatic looping is often better handled within a Python script executed by `execute_code`).
*   **Error Handling Strategies in Workflows**
    *   **Using `condition` for Error Branches:** Create tasks that only run if a prior critical task has `{{task_id.reflection.status == 'Failure'}}` or low `confidence`.
        *   These error handling tasks could log details, notify the user, or attempt a fallback strategy.
    *   **Fallback Strategies:** If a primary approach (e.g., a specific API) fails, have a conditional path to try an alternative.
    *   **Graceful Degradation:** Design workflows to still provide some value even if parts fail (e.g., if enrichment fails, still provide the base data).
    *   **Leveraging the `Error HandleR` (Protocol Section 7.23):**
        *   Explain that the `CoreWorkflowEngine` has a conceptual `Error HandleR`.
        *   Certain error types or repeated failures can be configured (conceptually in `config.py` or engine logic) to trigger specific actions like:
            *   `trigger_metacognitive_shift`: To analyze and attempt to correct the issue.
            *   `halt_workflow`: To stop execution safely.
            *   `notify_keyholder`: (Conceptual) Send an alert.
    *   **Logging:** Rely on Arche's logging (`logs/arche_v3_log.log`) for detailed error traces. Set `LOG_LEVEL` to `DEBUG` in `config.py` for maximum detail during development.
*   **Testing Custom Workflows**
    *   Start with simple inputs and verify outputs at each step.
    *   Test edge cases and potential failure points.
    *   Examine the IAR `reflection` data for each task in the output JSON to understand its self-assessed performance. 