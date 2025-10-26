# ResonantiA Maestro - Master Orchestrator Specification (v3.5)

## 1. Overview

The `ResonantiaMaestro` is the central nervous system and master orchestrator for the Arche system operating under the ResonantiA Protocol v3.5. It serves as the primary entry point for all user intents, replacing direct calls to the `WorkflowEngine`. Its core purpose is to achieve a deep `Cognitive resonancE` with the user's request, assess its nature and complexity, and then commission the most appropriate cognitive engine or workflow to produce a robust, fully-formed, and resonant result.

This centralized orchestration ensures that the full power of Arche's diverse capabilities—from the rapid, instinctual pattern-matching of the Adaptive Cognitive Orchestrator (`ACO`) to the deep, multi-phase analysis of the Resonant Insight and Strategy Engine (`RISE`)—is brought to bear in the most effective and efficient manner possible.

## 2. Core Responsibilities

- **Unified Intent Intake:** Acts as the single entry point for all queries and workflow requests via its `orchestrate_query` method.
- **Intelligent Query Assessment:** Analyzes each request to determine the optimal processing path. This prevents the use of heavyweight analytical engines for trivial tasks and ensures complex queries receive the necessary depth of analysis.
- **Cognitive Engine Commissioning:** Dynamically routes requests to the appropriate sub-system:
  - **RISE Orchestrator:** For complex, novel, or strategic queries requiring deep analysis, synthesis, and strategy generation.
  - **Adaptive Cognitive Orchestrator (ACO):** (Conceptual) For rapid responses to known patterns and routine queries.
  - **Direct Workflow Engine:** For explicit requests to run a specific workflow blueprint.
- **Context Management:** Ensures that the `initial_context`, including the `user_query`, is correctly formatted and passed to the commissioned engine or workflow.
- **Failure Resilience:** Provides a top-level try-except block to handle critical failures during orchestration, creating a potential entry point for system-level recovery workflows or a `Metacognitive shifT`.

## 3. Architectural Flow

The operational flow of the `ResonantiaMaestro` follows a clear, logical sequence:

1.  **Initialization (`__init__`):** The `Maestro` is instantiated, and in turn, it initializes all its subordinate systems: `SPRManager`, `WorkflowEngine`, and `RISEOrchestrator`. This ensures all cognitive tools are ready upon system start.
2.  **Orchestration Request (`orchestrate_query`):** The `main.py` entry point receives a user request (either a natural language query or a direct workflow command) and passes it to the `orchestrate_query` method.
3.  **Query Assessment (`_assess_query_complexity`):** This internal method performs the critical routing decision. It uses a set of robust heuristics to classify the query:
    - **Direct Command:** If a specific `workflow_to_run` is present in the context, it immediately routes to the `WorkflowEngine`.
    - **High Complexity Keywords:** It scans the query for terms like `analyze`, `design`, `strategy`, `causal`, etc., which indicate a need for the deep analytical power of the `RISE` engine.
    - **Default Path:** By default, and for any query not meeting other criteria, it routes to `RISE` to ensure a high-quality, robust response, embodying the principle of thoroughness.
4.  **Engine Delegation:** Based on the assessment, the `Maestro` calls the appropriate method on the selected sub-system (e.g., `rise_orchestrator.execute_full_rise_cycle(...)` or `workflow_engine.run_workflow(...)`).
5.  **Result Aggregation:** The `Maestro` receives the `final_result` dictionary from the subordinate engine and passes it back to the main application for output and serialization.

## 4. Key Methods

### `__init__(self, spr_manager: Optional[SPRManager] = None)`
- Initializes the `SPRManager`.
- Initializes the `WorkflowEngine`, passing the `spr_manager`.
- Initializes the `RISEOrchestrator`, passing both the `workflow_engine` and `spr_manager`.

### `orchestrate_query(self, query: str, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
- The primary public method and entry point.
- Takes a `query` string and an optional `initial_context` dictionary.
- Calls `_assess_query_complexity` to get the execution plan.
- Executes the plan by calling the appropriate engine (`RISE` or `WorkflowEngine`).
- Wraps the execution in a `try...except` block for robust error handling.
- Returns the final results dictionary from the executed process.

### `_assess_query_complexity(self, query: str, initial_context: Dict[str, Any]) -> Dict[str, Any]`
- A private method responsible for the core routing logic.
- Returns an `assessment` dictionary containing the `engine` to use, the `workflow` to run, a `reason` for the decision, and a `confidence` score.
- Current implementation uses heuristics based on keywords and context flags. Future versions could replace this with a trained classifier model or a more sophisticated SPR-based routing mechanism for greater accuracy and adaptability.

## 5. Integration with `main.py`

The `main.py` script is refactored to be a thin client for the `ResonantiaMaestro`.
- It no longer initializes the `WorkflowEngine` or `SPRManager` directly.
- It initializes a single `ResonantiaMaestro` instance.
- It parses command-line arguments for a user query (`-q`/`--query`) and an optional workflow file.
- It passes these arguments to the `maestro.orchestrate_query()` method and handles the final result serialization.


