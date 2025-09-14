# 2. `Three_PointO_ArchE` Python Package Structure

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Overview of key modules and their responsibilities. Link to detailed API docs if generated separately, or summarize here.
-->

This page provides an overview of the Python package structure for Arche, located within the `Three_PointO_ArchE/` directory. This structure is designed for modularity and clear separation of concerns, enabling robust and extensible development.

*   **`__init__.py`**
    *   Purpose: Makes the `Three_PointO_ArchE` directory a Python package.
*   **`main.py`**
    *   Purpose: Main entry point for running Arche workflows from the command line.
    *   Responsibilities: Parses command-line arguments, initializes and runs the `IARCompliantWorkflowEngine` from `workflow_engine.py`.
*   **`config.py`**
    *   Purpose: Centralized configuration for the system.
    *   Responsibilities: Stores API keys (ideally via environment variables), LLM provider settings, tool parameters, file paths, logging settings, meta-cognition thresholds.
*   **`workflow_engine.py`**
    *   Purpose: Contains the `IARCompliantWorkflowEngine`, the primary engine for executing a single workflow from start to finish.
    *   Responsibilities: Parses workflow JSON, manages a unified `workflow_context`, handles data and IAR propagation between tasks, evaluates conditional logic, and invokes actions via the `ActionRegistry`.
*   **`workflow_chaining_engine.py`**
    *   Purpose: A secondary, more specialized engine for orchestrating multiple, separate workflow files.
    *   Responsibilities: Uses `networkx` to build a dependency graph of workflows, enabling complex, multi-workflow processes. Not used for standard, single-workflow execution.
*   **`action_registry.py`**
    *   Purpose: Maps `action_type` strings from workflows to their corresponding Python tool functions.
    *   Responsibilities: Holds a dictionary of action mappings, allowing for a decoupled architecture where the engine does not need to know about specific tool implementations.
*   **Tool Modules (e.g., `tools.py`, `enhanced_tools.py`, `predictive_modeling_tool.py`, etc.)**
    *   Purpose: These modules contain the concrete implementations of the various cognitive and functional capabilities of Arche.
    *   Examples: `llm_tool.py`, `web_search_tool.py`, `code_executor.py`, `causal_inference_tool.py`, `agent_based_modeling_tool.py`, `cfp_framework.py`.
    *   **IAR Mandate:** All tool functions within these modules MUST generate and return the IAR `reflection` dictionary alongside their primary results. This is a non-negotiable contract for ensuring system self-awareness.
*   **`spr_manager.py` & `knowledge_graph/` directory**
    *   Purpose: The `SPRManager` class handles all CRUD (Create, Read, Update, Delete) operations for Sparse Priming Representations (SPRs).
    *   The `knowledge_graph/` subdirectory contains the persistent `Knowledge tapestrY` (`spr_definitions_tv.json`), which is the structured knowledge base of the system.
*   **`communication_manager.py`**
    *   Purpose: Manages asynchronous, two-way communication between different ArchE instances, forming the backbone for a distributed ArchE Collective. It is designed to use Redis Pub/Sub.
*   **`registry_manager.py`**
    *   Purpose: Provides a queryable registry of all distributed ArchE instances, their capabilities, and their current status. Works in conjunction with the `CommunicationManager`.
*   **`llm_providers.py`**
    *   Purpose: Contains functions or classes for interacting with specific LLM provider APIs (e.g., OpenAI, Google Gemini), abstracting the details of the API calls.
*   **`vetting_prompts.py`**
    *   Purpose: Stores standardized prompts used by the `VettingAgenT` (which is conceptually a specialized use of the `llm_tool.py`) to perform ethical reviews, logical consistency checks, and IAR analysis.

*This structure aims for modularity, with clear responsibilities for each component, facilitating maintenance and extension of the Arche system. The consistent implementation of IAR across all tool modules is critical for the system's self-awareness and meta-cognitive capabilities.* 