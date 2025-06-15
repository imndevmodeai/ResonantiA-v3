# 4. Running Your First Workflow

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Provide a simple command example, explain its structure, and describe the expected output.
-->

This page guides you through running your first workflow with Arche.

*   **Command Structure**
    *   Example Command: `python -m Three_PointO_ArchE.main workflows/basic_analysis.json -c '{"user_query": "Explain the concept of Sparse Priming Representations."}'`
    *   **Explanation of Components:**
        *   `python -m Three_PointO_ArchE.main`: How to execute Arche as a module from the project root. This ensures all relative paths within the package work correctly.
        *   `workflows/basic_analysis.json`: Specifies the path to the workflow (`Process blueprintS`) file.
        *   `-c '{"user_query": "..."}'`: The `--context_json` or `-c` argument, used to pass initial context as a JSON string. Explain common initial context keys like `user_query`.
*   **Expected Output**
    *   **Console Output:** Describe what the user might see in the console (e.g., log messages, status updates, final summary from `display_output` tool if used).
    *   **Files in `outputs/` directory:**
        *   Mention that results are typically saved here.
        *   Example: `outputs/result_basic_analysis_run_YYYYMMDD_HHMMSS.json` (explain the naming convention).
        *   Briefly describe the structure of this main JSON result file (more detail in the next section). 