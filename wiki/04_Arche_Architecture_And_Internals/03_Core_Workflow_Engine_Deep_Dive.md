# 3. Core Workflow Engine Deep Dive (`workflow_engine.py`)

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Detail the execution lifecycle, context management (especially IAR), and conditional logic evaluation.
-->

This page provides a deeper look into the `CoreWorkflowEngine` (typically implemented in `workflow_engine.py`), which is the heart of Arche's task orchestration.

*   **Execution Lifecycle (DAG Processing)**
    1.  **Initialization:** The engine is instantiated, often with an initial context (e.g., from command-line arguments).
    2.  **Workflow Parsing:** Reads the specified workflow JSON file, validating its structure and building an internal representation of tasks and their dependencies (a Directed Acyclic Graph - DAG).
    3.  **Dependency Resolution & Execution Order:** Determines the correct order of task execution. Tasks with no dependencies are run first. Subsequent tasks are run only after all their listed `dependencies` have successfully completed.
    4.  **Task Execution Loop:** Iterates through tasks in the resolved order:
        *   **Conditional Check:** If a `condition` field is present for the task, it is evaluated. If false, the task is skipped (IAR status might be "Skipped").
        *   **Input Resolution:** Resolves input values for the current task by looking up data from the `workflow_context` (e.g., `{{prior_task.results.output_key}}`, `{{another_task.reflection.confidence}}`).
        *   **Action Invocation:** Calls the `ActionRegistry` to get the appropriate Python function for the task's `action_type`.
        *   **Tool Execution:** Executes the tool function with the resolved inputs.
        *   **Output & IAR Handling (Critical):** The tool function returns a dictionary containing its `results` and the mandatory `reflection` (IAR) dictionary. The engine stores this entire dictionary in the `workflow_context` under the current `task_id`.
        *   **Error Handling (Conceptual `Error HandleR` - Protocol Section 7.23):** If a task fails or returns problematic IAR, the engine's error handling logic is invoked. This might involve logging, halting, or triggering `Metacognitive shifT` based on configuration.
    5.  **Completion:** Once all tasks are processed (completed, skipped, or failed and handled), the engine finalizes the `workflow_context` (which now contains all task results and reflections) and may return it or trigger a final display/save action.
*   **Context Management (Including IAR Propagation)**
    *   **`workflow_context`:** A central Python dictionary maintained by the engine throughout the workflow's lifecycle.
    *   **Initial Context:** Populated at the start (e.g., `user_query` from `-c` arg).
    *   **Task Outputs:** For each completed task, its `task_id` becomes a key in the `workflow_context`. The value is a dictionary: `{"results": <primary_output>, "reflection": <iar_dictionary>}`.
    *   **Data Referencing:** Tasks access data from this context using a template notation (e.g., `{{task_A.results.data_point}}`, `{{task_B.reflection.status}}`). The engine is responsible for parsing these templates and injecting the correct values.
    *   **IAR Availability:** This mechanism makes the *full IAR data* (status, confidence, issues, etc.) from any prior task readily available to all subsequent tasks for input generation or conditional logic.
*   **Conditional Logic Evaluation (`condition` field processing)**
    *   The `condition` field in a task definition is a string expression.
    *   Before executing a task, the engine resolves any template variables within this string using the current `workflow_context`.
    *   The resolved string is then evaluated as a Pythonic boolean expression (e.g., using `eval()` in a carefully controlled, safe manner, or a more restricted expression parser).
    *   **Examples using IAR data:**
        *   `"condition": "{{check_data.reflection.confidence > 0.8}}"`
        *   `"condition": "'Critical Error' not in {{step_one.reflection.potential_issues}}"`
        *   `"condition": "{{step_two.reflection.status == 'Success'}} and {{step_three.results.value_count > 10}}"`
    *   If the condition evaluates to `True`, the task proceeds. If `False`, the task is skipped.
*   **Interaction with Action Registry**
    *   The engine relies on the `ActionRegistry` (`action_registry.py`) to find the correct Python function to call for a given `action_type`.
    *   This decouples the engine from the specific tool implementations.

*The CoreWorkflowEngine's robust handling of task orchestration, context (especially IAR data), and conditional logic is fundamental to Arche's ability to execute complex, adaptive, and self-aware processes.* 