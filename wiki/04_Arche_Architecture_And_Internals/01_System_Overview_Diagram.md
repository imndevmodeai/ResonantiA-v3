# 1. System Overview Diagram

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
This page should ideally embed or link to a diagram. For now, a textual description of the components and their interactions will suffice.
-->

This page provides a conceptual overview of Arche's system architecture.

**(Conceptual Diagram Description)**

*   **Keyholder:** Interacts with the system, provides input, and can exercise `Keyholder Override`.
*   **Core Workflow Engine (`workflow_engine.py`):**
    *   Orchestrates task execution based on `Process blueprintS` (workflow JSON files).
    *   Manages workflow context (data flow).
    *   Handles `Integrated Action Reflection (IAR)` data from tools.
    *   Interacts with the `Action Registry`.
*   **Action Registry (`action_registry.py`):**
    *   Maps `action_type` from workflows to specific Python functions (tools).
    *   Ensures tools adhere to the IAR contract.
*   **Cognitive Tools (various files in `3.0ArchE/` e.g., `tools.py`, `predictive_modeling_tool.py`, `code_executor.py`, `cfp_framework.py`):**
    *   Perform discrete actions (e.g., LLM calls, search, code execution, prediction, CFP analysis, causal inference, ABM).
    *   **Crucially, all tools generate IAR data (a `reflection` dictionary) alongside their results.** This IAR data feeds back into the `Core Workflow Engine` and is available for vetting and meta-cognition.
*   **Knowledge Network Oneness (KnO) / SPRManager (`spr_manager.py`, `knowledge_graph/spr_definitions_tv.json`):**
    *   `SPRManager`: Manages SPR definitions in the `Knowledge tapestrY` (`spr_definitions_tv.json`).
    *   `SPR Decompressor` (Conceptual): Facilitates internal cognitive activation based on recognized SPRs.
    *   `InsightSolidificatioN` workflow interacts with `SPRManager` to update the `Knowledge tapestrY`.
*   **VettingAgenT (Conceptual, often `LLMTool` + `vetting_prompts.py`):**
    *   Analyzes proposed actions, reasoning, and outputs, **critically using IAR data from previous steps** for context.
    *   Can trigger `Metacognitive shifT`.
*   **Meta-Cognition Loops:**
    *   **`Metacognitive shifT`:** Reactive correction mechanism triggered by dissonance (often identified via IAR or `VettingAgenT`). Involves CRC (Cognitive Reflection Cycle using IAR-rich ThoughtTraiL).
    *   **`Synergistic Intent Resonance Cycle (SIRC)`:** Proactive mechanism for deep intent alignment and complex planning, leveraging conceptual IAR for feasibility.
*   **Configuration (`config.py`):** Provides system-wide settings, API keys, tool parameters.
*   **Logging (`logs/arche_v3_log.log`):** Records system activity.
*   **Outputs (`outputs/`):** Stores results, models, visualizations.

**(Flow Description)**

1.  Keyholder initiates a workflow via `main.py`, providing initial context.
2.  `Core Workflow Engine` parses the workflow and starts executing tasks.
3.  For each task, it resolves inputs (potentially from prior task results/IAR) and calls the `Action Registry`.
4.  `Action Registry` invokes the appropriate tool function.
5.  The tool performs its action and **returns results including an IAR `reflection` dictionary.**
6.  `Core Workflow Engine` stores this in the context.
7.  `VettingAgenT` may analyze the step (using prior IAR).
8.  `Metacognitive shifT` or `SIRC` may be triggered based on IAR, vetting, or specific workflow steps.
9.  SPRs encountered are processed by the `SPR Decompressor` activating knowledge in `KnO`.
10. `InsightSolidificatioN` can update `KnO` via `SPRManager`.
11. The process continues until the workflow completes, with results and logs generated.

*This high-level diagram illustrates the dynamic interplay between components, emphasizing the central role of the Core Workflow Engine and the crucial feedback loop provided by Integrated Action Reflection (IAR).* 