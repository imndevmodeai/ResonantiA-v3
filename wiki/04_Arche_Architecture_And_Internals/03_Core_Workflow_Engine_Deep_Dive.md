# 3. Core Workflow Engine Deep Dive (`workflow_engine.py`)

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Detail the execution lifecycle, context management (especially IAR), and conditional logic evaluation.
-->

This page provides a deeper look into the `IARCompliantWorkflowEngine` (from `workflow_engine.py`), which is the heart of Arche's task orchestration. It is designed to execute a single, complete workflow from start to finish, managing all IAR processing and context propagation.

*   **Execution Lifecycle**
    1.  **Initialization:** The `IARCompliantWorkflowEngine` is instantiated. It can be initialized with an `SPRManager` instance to provide SPR context to workflows.
    2.  **Workflow Execution (`run_workflow`):** This is the main method. It takes the workflow file path and an initial context dictionary.
        *   It generates a unique `workflow_run_id`.
        *   It loads the workflow JSON file.
        *   It prepares a `workflow_context` dictionary, populating it with initial context and metadata.
    3.  **Task Execution Loop:** The engine iterates through the tasks defined in the workflow's `steps`:
        *   **Dependency & Condition Checks:** It first checks if the task has dependencies that have not been met or if a `condition` string evaluates to false. If so, the task is skipped and its status is marked as `Skipped`.
        *   **Input Resolution:** It resolves input values for the current task by looking up data from the `workflow_context` using template notation (e.g., `{{prior_task.results.output_key}}`).
        *   **Action Invocation:** Calls the `ActionRegistry` to get the appropriate Python function for the task's `action_type`.
        *   **Tool Execution:** Executes the tool function with the resolved inputs.
        *   **Output & IAR Handling (Critical):** The tool function returns its `results` and `reflection` (IAR) dictionary. The engine stores this entire output dictionary in the `workflow_context`, keyed by the `task_id`.
        *   **Error Handling:** If a task fails (raises an exception), the engine catches it, logs the error, updates the task's status to `Failed`, and stores the error message in the context. By default, it continues to the next task unless dependencies fail.
    4.  **Completion:** After iterating through all tasks, the engine calculates the total run duration, sets a final `workflow_status`, and returns the complete `workflow_context` dictionary, which now contains all task results and reflections.
*   **Context Management (The `workflow_context` Dictionary)**
    *   **Single Source of Truth:** The `workflow_context` is a large, single Python dictionary that is built up over the course of the workflow execution.
    *   **Initial Context:** Populated at the start (e.g., `user_query` from the `-c` command-line argument).
    *   **Task Outputs:** For each completed task, its `task_id` becomes a key in the `workflow_context`. The value is the complete dictionary returned by the tool: `{"results": <primary_output>, "reflection": <iar_dictionary>}`.
    *   **Data Referencing:** Tasks access data from this context using a template notation (e.g., `{{task_A.results.data_point}}`, `{{task_B.reflection.status}}`). The engine is responsible for parsing these templates and injecting the correct values.
*   **A Note on `workflow_chaining_engine.py`**
    *   The repository also contains a `WorkflowChainingEngine`. As its name implies, this is likely a more specialized engine designed to run multiple, separate workflow files in a sequence or a complex graph.
    *   It is **not** the default engine used for single workflow execution. It uses the `networkx` library to manage a graph of dependencies, which suggests a more powerful, but different, orchestration pattern than the primary `IARCompliantWorkflowEngine`.

*The `IARCompliantWorkflowEngine` provides a robust, linear execution of a workflow's tasks, with its primary strength being the meticulous management of a unified context and the propagation of IAR data between steps.* 