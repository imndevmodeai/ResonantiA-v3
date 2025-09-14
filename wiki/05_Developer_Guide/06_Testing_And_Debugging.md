# 6. Testing & Debugging

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Discuss unit tests, integration tests (workflow tests), interpreting IAR for debugging, and using logs.
-->

This page provides guidance on testing new or modified code within Arche and strategies for debugging issues.

*   **Types of Tests**
    *   **Unit Tests:**
        *   **Purpose:** Test individual functions or methods in isolation, especially for core logic within tools or utility functions.
        *   **Framework:** Use a standard Python testing framework like `unittest` or `pytest`.
        *   **Location:** Tests should ideally be placed in a separate `tests/` directory, mirroring the package structure (e.g., `tests/unit/test_tools.py`).
        *   **Focus:** Verify correct outputs for given inputs, proper handling of edge cases, and that IAR `reflection` dictionaries are formed correctly by tool functions (even if with mocked external calls).
    *   **Integration Tests (Workflow Tests):**
        *   **Purpose:** Test the interaction of multiple components by running complete or partial workflows.
        *   **Method:** Create dedicated test workflow JSON files in a `tests/workflows/` directory.
        *   **Focus:**
            *   Verify that data flows correctly between tasks (including IAR data).
            *   Test conditional logic based on IAR outputs.
            *   Ensure tools integrate correctly with the `CoreWorkflowEngine` and `ActionRegistry`.
            *   Check that the final output in the `outputs/` directory is as expected.
        *   These tests can use mocked versions of external services (e.g., LLMs, APIs) to ensure reproducibility and avoid costs, or run against real services in a controlled manner for end-to-end validation.
*   **Debugging Strategies**
    *   **1. Interpreting Integrated Action Reflection (IAR) Data:**
        *   **This is your primary debugging tool for workflow issues.**
        *   After running a workflow, examine the main JSON output file in the `outputs/` directory.
        *   For each task, look at its `reflection` dictionary:
            *   `status`: Was it "Success", "Failure", or "Partial"?
            *   `confidence`: Is it unexpectedly low? Why?
            *   `potential_issues`: This list is GOLD for debugging. It contains warnings, errors, and caveats reported *by the tool itself*.
            *   `summary`: What did the tool think it did?
            *   `error_message`: If status is "Failure", this should provide details.
        *   Trace back through the workflow using IAR data. If a task failed or produced poor results, examine the IAR of its `dependencies` to see if the issue originated upstream.
    *   **2. Using Arche's Logs:**
        *   **Location:** `logs/arche_v3_log.log` (or as configured in `config.py`).
        *   **Log Level:** For debugging, set `LOG_LEVEL = "DEBUG"` in `config.py` to get the most detailed output.
        *   Logs will contain information about:
            *   Workflow engine activity (task starting, finishing, conditional evaluations).
            *   Tool execution details (often more verbose than the IAR summary).
            *   Full stack traces for unhandled exceptions.
            *   `SPRManager` activity, `CodeExecutor` sandbox interactions, etc.
    *   **3. Python Debugger (`pdb` or IDE Debugger):**
        *   For complex issues within a specific Python function (e.g., a tool's internal logic), use a standard Python debugger.
        *   You can set breakpoints and step through the code.
        *   To debug a workflow run, you might need to invoke the `CoreWorkflowEngine` programmatically from a test script where you can control debugger attachment, rather than just via `main.py`.
    *   **4. Incremental Testing:**
        *   When developing a new tool or complex workflow, test incrementally.
        *   Start with a very simple workflow that only runs your new tool with known inputs.
        *   Gradually add complexity and dependencies.
    *   **5. Mocking External Services:**
        *   When unit testing tools that call external APIs (LLMs, web search, etc.), use Python's `unittest.mock` library to mock these external calls.
        *   This makes your tests faster, more reliable (not dependent on network or API keys), and free.
        *   You can assert that the external services were called with the correct parameters.
*   **Common Issues & Pitfalls**
    *   **Incorrect IAR Implementation:** Tools not returning a complete or accurate `reflection` dictionary. This undermines the entire system's self-awareness.
    *   **Workflow Input/Output Mismatches:** A task expecting an input (e.g., `{{task_A.results.data}}`) where `task_A` produces results in a different structure or key name.
    *   **Faulty Conditional Logic:** `condition` strings in workflows not evaluating as expected, often due to incorrect context variable paths or typos.
    *   **Configuration Errors:** Incorrect API keys, file paths, or tool parameters in `config.py`.
    *   **Sandbox Issues (`CodeExecutor`):** Docker not running, incorrect Docker image, or permission problems if using subprocess mode incautiously.

*Effective testing and diligent use of IAR data and logs are essential for developing robust and reliable additions to the Arche system.* 