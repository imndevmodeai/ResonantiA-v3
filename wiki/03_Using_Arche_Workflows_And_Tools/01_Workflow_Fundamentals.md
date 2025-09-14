# 1. Workflow Fundamentals

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Explain the anatomy of a workflow JSON file, how data flows, and conditional execution using IAR data.
-->

This page explains the fundamental concepts of Arche workflows (Process blueprintS).

*   **Anatomy of a Process blueprintS (JSON file in `workflows/`)**
    *   Overall structure: A JSON object, typically a list of task dictionaries.
    *   **Defining Tasks:**
        *   `task_id`: Unique identifier for the task.
        *   `action_type`: Specifies the tool/function to execute (e.g., `generate_text_llm`, `search_web`, `execute_code`, `run_prediction`).
        *   `inputs`: A dictionary defining the inputs for the action. How to reference outputs from previous tasks (e.g., `{{prior_task_id.results.some_key}}`).
        *   `dependencies`: A list of `task_id`s that must complete before this task can start.
        *   `condition`: (Optional) A string expression that must evaluate to true for the task to run. Explain how IAR data can be used here (e.g., `{{prior_task_id.reflection.confidence > 0.7}}`).
        *   `description`: (Optional) A human-readable description of the task.
*   **Workflow Context: How Data (including IAR) Flows Between Tasks**
    *   Explain the concept of the workflow context that the Core Workflow Engine maintains.
    *   How task results (including the full IAR dictionary under the `reflection` key) are stored under their `task_id`.
    *   Reinforce referencing task outputs and IAR data using template variables like `{{task_id.results.key}}` and `{{task_id.reflection.confidence}}` or `{{task_id.reflection.potential_issues}}`.
*   **Conditional Execution using IAR Data**
    *   Provide concrete examples of using the `condition` field with IAR data.
    *   Example: Only run a detailed analysis task if a prior data gathering task has high confidence: `"condition": "{{data_gathering_task.reflection.confidence > 0.8}}"`.
    *   Example: Trigger an error handling task if a prior task fails: `"condition": "{{critical_task.reflection.status == 'Failure'}}"`. 