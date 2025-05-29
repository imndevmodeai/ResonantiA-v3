# 2. Example Workflows Showcase

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
List key example workflows, briefly describe their purpose, and link to the JSON file in `workflows/` and any relevant Wiki page explaining them.
-->

This page showcases a selection of example workflows (Process blueprintS) available in the `workflows/` directory. These examples demonstrate Arche's capabilities and provide templates for creating custom workflows.

*   **`basic_analysis_workflow.json`**
    *   **Purpose:** Demonstrates a fundamental sequence: take a user query, perform a web search, and generate a textual analysis using an LLM.
    *   **Key Tools Used:** `search_web`, `generate_text_llm`.
    *   **Link to Workflow:** `../../workflows/basic_analysis_workflow.json`
    *   **Relevant Wiki Page:** [Running Your First Workflow](../02_Getting_Started_with_Arche/04_Running_Your_First_Workflow.md) (uses this as an example).
*   **`code_execution_workflow.json`**
    *   **Purpose:** Shows how to use the `execute_code` tool to run a Python script and analyze its output.
    *   **Key Tools Used:** `execute_code`, `generate_text_llm`.
    *   **Link to Workflow:** `../../workflows/code_execution_workflow.json`
*   **`insight_solidification.json`**
    *   **Purpose:** Implements Arche's formal process for vetting and integrating new knowledge into the `Knowledge tapestrY` as an SPR.
    *   **Key Tools/Concepts Used:** `VettingAgenT` (via `generate_text_llm` and vetting prompts), `SPRManager` (via a custom tool or `execute_code` to call its methods).
    *   **Link to Workflow:** `../../workflows/insight_solidification.json`
    *   **Relevant Wiki Page:** [Working with SPRs & Knowledge](../03_Using_Arche_Workflows_And_Tools/04_Working_with_SPRs_And_Knowledge.md#the-insightsolidification-workflow-insight_solidificationjson)
*   **`temporal_forecasting_workflow.json`**
    *   **Purpose:** Demonstrates time-series forecasting using the `PredictiveModelingTool`.
    *   **Key Tools Used:** `run_prediction` (with actions like "train_model", "forecast_future_states").
    *   **Link to Workflow:** `../../workflows/temporal_forecasting_workflow.json`
    *   **Relevant Wiki Page:** [Temporal Reasoning Tools](../03_Using_Arche_Workflows_And_Tools/03_Temporal_Reasoning_Tools.md#run_prediction-predictive-modeling-tool---protocol-section-719)
*   **`temporal_causal_analysis_workflow.json`**
    *   **Purpose:** Showcases temporal causal inference using the `CausalInferenceTool`, for example, to run Granger causality or estimate lagged effects.
    *   **Key Tools Used:** `perform_causal_inference`.
    *   **Link to Workflow:** `../../workflows/temporal_causal_analysis_workflow.json`
    *   **Relevant Wiki Page:** [Temporal Reasoning Tools](../03_Using_Arche_Workflows_And_Tools/03_Temporal_Reasoning_Tools.md#perform_causal_inference-causalinferencetool---protocol-section-713)
*   **`simple_causal_abm_test_v3_0.json`**
    *   **Purpose:** An example of setting up, running, and analyzing a basic Agent-Based Model using the `AgentBasedModelingTool`.
    *   **Key Tools Used:** `perform_abm`.
    *   **Link to Workflow:** `../../workflows/simple_causal_abm_test_v3_0.json`
    *   **Relevant Wiki Page:** [Temporal Reasoning Tools](../03_Using_Arche_Workflows_And_Tools/03_Temporal_Reasoning_Tools.md#perform_abm-agentbasedmodelingtool---protocol-section-714)
*   **`comparative_future_scenario_workflow.json`**
    *   **Purpose:** Illustrates the use of the `CfpFramework` to compare the evolution of two defined scenarios or system states.
    *   **Key Tools Used:** `run_cfp`.
    *   **Link to Workflow:** `../../workflows/comparative_future_scenario_workflow.json`
    *   **Relevant Wiki Page:** [Temporal Reasoning Tools](../03_Using_Arche_Workflows_And_Tools/03_Temporal_Reasoning_Tools.md#run_cfp-cfpframeworok---protocol-section-76)
*   **`causal_abm_integration_v3_0.json`**
    *   **Purpose:** A more advanced workflow demonstrating the synergistic use of `CausalInferenceTool` and `AgentBasedModelingTool` for deeper systemic understanding (Pattern 8.6).
    *   **Key Tools Used:** `perform_causal_inference`, `perform_abm`.
    *   **Link to Workflow:** `../../workflows/causal_abm_integration_v3_0.json`
    *   **Relevant Wiki Page:** [Advanced Interaction Patterns](../03_Using_Arche_Workflows_And_Tools/05_Advanced_Interaction_Patterns.md#causal-abm-integration-invocation-pattern-86)
*   **`tesla_visioning_workflow.json`**
    *   **Purpose:** An advanced workflow for complex problem-solving, simulation, and refinement cycles, guided by the Tesla Visioning pattern (Pattern 8.7).
    *   **Key Tools/Concepts Used:** Multiple tools, potentially including iterative loops, `VettingAgenT`, `Metacognitive shifT` triggers.
    *   **Link to Workflow:** `../../workflows/tesla_visioning_workflow.json`
    *   **Relevant Wiki Page:** [Advanced Interaction Patterns](../03_Using_Arche_Workflows_And_Tools/05_Advanced_Interaction_Patterns.md#tesla-visioning-workflow-invocation-pattern-87)

*These examples provide a starting point. Developers are encouraged to explore, modify, and create new workflows to leverage Arche's full potential.* 