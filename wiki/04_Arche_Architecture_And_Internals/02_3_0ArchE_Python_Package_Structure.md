# 2. `3.0ArchE` Python Package Structure

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Overview of key modules and their responsibilities. Link to detailed API docs if generated separately, or summarize here.
-->

This page provides an overview of the Python package structure for Arche, located within the `3.0ArchE/` directory. (Detailed API documentation might be generated separately using tools like Sphinx).

*   **`__init__.py`**
    *   Purpose: Makes the `3.0ArchE` directory a Python package.
*   **`main.py` (Protocol Section 7.2)**
    *   Purpose: Main entry point for running Arche workflows from the command line.
    *   Responsibilities: Parses command-line arguments (workflow file, initial context), initializes and runs the `CoreWorkflowEngine`.
*   **`config.py` (Protocol Section 7.1)**
    *   Purpose: Centralized configuration for the system.
    *   Responsibilities: Stores API keys (ideally via environment variables), LLM provider settings, tool parameters, file paths, logging settings, meta-cognition thresholds.
*   **`workflow_engine.py` (Protocol Section 7.3)**
    *   Purpose: The `CoreWorkflowEngine` class orchestrates workflow execution.
    *   Responsibilities: Parses workflow JSON, manages task dependencies (DAG), handles context propagation (including IAR data), evaluates conditional logic, invokes actions via `ActionRegistry`, and manages error handling (conceptual `Error HandleR`).
*   **`action_registry.py` (Protocol Section 7.4)**
    *   Purpose: Maps `action_type` strings from workflows to their corresponding Python tool functions.
    *   Responsibilities: Holds a dictionary of action mappings, ensures tools are called correctly, conceptually validates IAR contract adherence.
*   **`tools.py` (Protocol Section 7.12)**
    *   Purpose: Contains implementations for many of the core cognitive tools.
    *   Examples: `invoke_llm` (for `generate_text_llm`), `run_search` (for `search_web`), `display_data` (for `display_output`), `calculate_expression` (for `calculate_math`).
    *   **IAR Mandate:** All tool functions herein MUST generate and return the IAR `reflection` dictionary.
*   **`enhanced_tools.py` (Protocol Section 7.9 - and others implied)**
    *   Purpose: Intended for more complex or specialized tools, potentially including `ApiTool` (`call_api`).
    *   (This could also house or be the pattern for tools like `DatabaseTool`, etc.)
    *   **IAR Mandate:** All tool functions herein MUST generate and return the IAR `reflection` dictionary.
*   **`spr_manager.py` (Protocol Section 7.5)**
    *   Purpose: The `SPRManager` class handles CRUD (Create, Read, Update, Delete) operations for SPRs in the `Knowledge tapestrY` (`knowledge_graph/spr_definitions_tv.json`).
    *   Responsibilities: Loading SPRs, saving SPRs, adding new SPRs, retrieving SPR definitions.
*   **`code_executor.py` (Protocol Section 7.10)**
    *   Purpose: The `CodeExecutor` class handles the execution of code snippets, focusing on sandboxing.
    *   Responsibilities: Manages Docker or subprocess execution, captures stdout/stderr, enforces resource limits (conceptual).
    *   **IAR Mandate:** Must return IAR reflecting execution success/failure and sandbox status.
*   **`llm_providers.py` (Protocol Section 7.8)**
    *   Purpose: Contains functions or classes for interacting with specific LLM provider APIs (e.g., OpenAI, Google Gemini).
    *   Responsibilities: Abstracts API call details, handles authentication (via keys from `config.py`), formats requests, parses responses.
*   **`vetting_prompts.py` (Protocol Section 7.11)**
    *   Purpose: Stores standardized prompts used by the `VettingAgenT` (when implemented with `LLMTool`).
    *   Responsibilities: Provides structured prompts for ethical review, logical consistency checks, IAR analysis, etc.
*   **`predictive_modeling_tool.py` (Protocol Section 7.19)**
    *   Purpose: Implements the `PredictiveModelingTool` for time-series forecasting.
    *   Responsibilities: Training models (ARIMA, etc.), making forecasts, evaluating models. Must return IAR.
*   **`causal_inference_tool.py` (Protocol Section 7.13)**
    *   Purpose: Implements the `CausalInferenceTool` for causal discovery and estimation, including temporal aspects.
    *   Responsibilities: Running causal analyses (Granger, DoWhy methods, etc.). Must return IAR.
*   **`agent_based_modeling_tool.py` (Protocol Section 7.14)**
    *   Purpose: Implements the `AgentBasedModelingTool` using frameworks like Mesa.
    *   Responsibilities: Creating, running, and analyzing ABM simulations. Must return IAR.
*   **`cfp_framework.py` (Protocol Section 7.6)**
    *   Purpose: Implements the `CfpFramework` for Comparative Fluxual Processing.
    *   Responsibilities: Simulating state evolution, calculating comparative metrics. Must return IAR.
*   **`quantum_utils.py` (Protocol Section 7.7)**
    *   Purpose: Provides utility functions supporting quantum-inspired calculations within `CfpFramework` (e.g., state vector operations, entanglement measures).

*This structure aims for modularity, with clear responsibilities for each component, facilitating maintenance and extension of the Arche system. The consistent implementation of IAR across all tool modules is critical for the system's self-awareness and meta-cognitive capabilities.* 