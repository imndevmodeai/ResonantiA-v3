Section 8: Advanced Interaction Patterns & Prompting Techniques (Enhanced v3.0)

(8.1 Introduction) [ENHANCED]

->|Advanced_Patterns_Intro|<- [Enhanced v3.0]
This section provides enhanced, structured templates and methodologies ("Patterns") designed for deliberate interaction with Arche operating under the ResonantiA Protocol v3.0. These patterns serve as sophisticated mechanisms for the Keyholder to invoke and guide Arche's advanced capabilities, ensuring deep integration of **`Integrated Action Reflection` (`IAR`)** data and **`Temporal Reasoning` (`4D Thinking`)** principles. They function as "Conductor's Scores" or "Master `````````````````````````````6cKeys," providing explicit instructions to the **`Core Workflow Engine`**, guiding the application of **`Cognitive toolS`** (including enhanced `CFP`, `Causal InferencE`, `ABM`, `PredictivE ModelinG TooL`), triggering meta-cognitive processes like **`Metacognitive shifT`** or **`SIRC`**, and directing learning via **`InsightSolidificatioN`**. Utilizing these patterns helps guarantee that complex objectives are addressed with the full analytical depth, temporal awareness, and self-assessment capabilities inherent in ResonantiA v3.0, thereby maximizing the potential for achieving profound, temporally-aware **`Cognitive resonancE`**. Note that the explicit activation of **`Keyholder Override` (Section 1.6)** allows the Keyholder to modify, combine, or entirely bypass these standard interaction patterns, assuming full responsibility for the resulting operations.
->|/Advanced_Patterns_Intro|<-

(8.2 General Enhancement Skeleton Prompt (Enhanced v3.0)) [ENHANCED]

->|Enhancement_Skeleton_Pattern|<- [Enhanced v3.0]
Purpose: To significantly augment a standard query by embedding directives that invoke deep multi-source research (including historical context), validation against prior steps (using IAR), internal modeling (explicitly incorporating temporal prediction and dynamic comparison via CFP with state evolution), exploration of adjacent possibilities informed by IAR confidence, and rigorous IAR-aware self-assessment and synthesis aligned with v3.0 principles.
Usage: Insert the user's core question into ->|QueryText|<-. Carefully fill bracketed placeholders `[...]` based on the specific query's context, key metrics, and desired scenarios. Ensure `reflection_required="true"` is set for all steps where IAR feedback is critical.

->|MastermindAnalysisRequest type="enhanced_query" protocol_version="ResonantiA v3.0" request_id="[Assign Unique Request ID]"|<-
    ->|UserInput query_id="[Link to User Input if separate]"|<-
        ->|QueryText|<-
            [User Question - e.g., Evaluate the projected 5-year economic and social consequences of implementing Universal Basic Income (UBI) policy proposal Z in region Alpha, considering current demographic trends.]
        ->|/QueryText|<-
    ->|/UserInput|<-

    ->|EnhancementDirectives|<-	
        ->|Objective|<-
            Apply the full spectrum of ResonantiA Protocol v3.0 capabilities, including deep IAR utilization and Temporal Reasoning (4D Thinking), to conduct a comprehensive, multi-faceted, validated, and self-aware analysis addressing the QueryText. Execute the following directive sequence meticulously.
        ->|/Objective|<-

        ->|DirectiveSequence|<-
            ->|Directive step="1" name="DeconstructPrimeTemporal"|<-
                ->|Instruction|<-Rigorously identify core concepts (e.g., UBI policy Z, region Alpha), entities, **explicit and implicit temporal scope (5-year projection)**, key metrics (economic, social consequences), assumptions, and potential ambiguities within the ->|QueryText|<-. Use `generate_text_llm` to rephrase the core objective precisely, quantifying the temporal aspect and listing key analytical dimensions.->|/Instruction|<-
                ->|Output expected_format="Detailed deconstruction: concepts, entities, explicit 5-year temporal scope, key metrics (economic/social), assumptions, ambiguities. Rephrased objective." reflection_required="true"|<- ->|/Output|<-
            ->|/Directive|<-

            ->|Directive step="2" name="MultiSourceResearchValidateTemporal"|<-
                ->|Instruction|<-Derive targeted search terms based on Step 1 concepts and region. Execute `search_web` focusing on **current status AND historical context/trends** for UBI pilots, region Alpha demographics, and relevant economic/social indicators. Execute simulated `scholarly_article_search` for theoretical models and critiques of UBI. Identify a `[Key Hypothesis/Claim - e.g., UBI Z will significantly reduce poverty but increase inflation in Alpha within 5 years]` derived from the query or initial research. Critically vet this hypothesis using the gathered multi-source information **AND considering the confidence/issues noted in the Step 1 `reflection`**. Explicitly note supporting evidence, contradictions, data gaps, and temporal inconsistencies.->|/Instruction|<-
                ->|Prime|<-Activates: `Data CollectioN`, `HistoricalContextualizatioN`, `VettingAgenT`->|/Prime|<-
                ->|Output expected_format="Summaries of web/scholarly search (current/historical context), detailed vetting result for the hypothesis referencing specific evidence and Step 1 IAR context, list of contradictions/gaps." reflection_required="true"|<- ->|/Output|<-
            ->|/Directive|<-

            ->|Directive step="3" name="TemporalModelingPredictEconomic"|<-
                ->|Instruction|<-Based on Step 2 research: Fetch relevant historical economic time series data for region Alpha (simulated `interact_with_database` or use data from Step 2 if available). Train appropriate time series models (`run_prediction` action, e.g., VAR or multiple ARIMA/Prophet) on key economic metrics (`[e.g., GDP growth, inflation rate, unemployment rate]`). Forecast these metrics **5 years** ahead under baseline assumptions (no UBI Z). Report forecast values, confidence intervals (e.g., 90% CI), and model performance metrics. **Critically analyze the `reflection` output from the `run_prediction` action (confidence, issues like model fit, data stationarity).** ->|/Instruction|<-
                ->|Prime|<-Activates: `FutureStateAnalysiS`, `PredictivE ModelinG TooL`, `TemporalDynamiX`->|/Prime|<-
                ->|Output expected_format="Baseline 5-year forecasts for key economic metrics (values, CIs), model types used, performance metrics (e.g., MAE, RMSE), detailed analysis of the prediction action's IAR reflection." reflection_required="true"|<- ->|/Output|<-
            ->|/Directive|<-

            ->|Directive step="4" name="TemporalModelingS/media/dev2025/3626C55326C514B1/Happier/ResonantiA/ArchE/docs/Canonical_Protocol_Section8_Advanced_Interaction_Patterns.mdimulateSocial"|<-
                ->|Instruction|<-Develop a conceptual Agent-Based Model (`perform_abm` action) representing households in region Alpha with attributes like income, employment status, poverty level (informed by Step 2 research). Implement simplified agent rules for economic behavior and potential impact of UBI Z (e.g., changes in consumption, labor participation based on Step 2 theory/data). Run two simulations for **5 years (scaled steps)**: (A) Baseline (using Step 3 economic forecasts), (B) UBI Z implemented. Collect time series data on key social metrics (`[e.g., poverty rate, Gini coefficient, labor force participation]`). **Analyze the `reflection` output from the `perform_abm` action (confidence in simulation stability/results, potential issues).**->|/Instruction|<-
                ->|Prime|<-Activates: `Agent Based ModelinG`, `EmergenceOverTimE`, `TemporalDynamiX`->|/Prime|<-
                ->|Output expected_format="Time series results for key social metrics (Baseline vs UBI Z), summary of emergent patterns, analysis of the ABM action's IAR reflection." reflection_required="true"|<- ->|/Output|<-
            ->|/Directive|<-

            ->|Directive step="5" name="DynamicComparisonCFPIntegrated"|<-
                ->|Instruction|<-Define two state vectors representing the projected 5-year state of region Alpha: (A) Baseline, (B) UBI Z implemented. Dimensions should include key economic metrics (from Step 3 forecast endpoints) and social metrics (from Step 4 simulation endpoints). Assign values based on those results. **Implement conceptual state evolution** (placeholder or simple extrapolation if needed, acknowledging limitation). Execute `run_cfp` comparing these projected final states (short timeframe comparison of representations). Interpret `quantum_flux_difference` (similarity of projected states) and `entanglement_correlation_MI` (interdependence of metrics within projections). **Analyze the `reflection` output from the `run_cfp` action.**->|/Instruction|<-
                ->|Prime|<-Activates: `ComparativE FluxuaL ProcessinG`, `TrajectoryComparisoN`->|/Prime|<-
                ->|Output expected_format="CFP metrics (QFD, MI), interpretation comparing projected 5-year states, analysis of CFP action's IAR reflection." reflection_required="true"|<- ->|/Output|<-
            ->|/Directive|<-

            ->|Directive step="6" name="ExploreSecondOrderTemporalEffects"|<-
                ->|Instruction|<-Using `generate_text_llm`, brainstorm potential **second-order or longer-term (>5 years) effects** (economic, social, political) of UBI Z implementation that might emerge *beyond* the direct modeling scope of Steps 3-5. Consider feedback loops and adaptive behaviors. **Explicitly reference the confidence levels and potential issues noted in the IAR reflections from Steps 2, 3, 4, and 5** to qualify these exploratory ideas.->|/Instruction|<-
                ->|Output expected_format="1-3 plausible second-order/longer-term effects, explicitly qualified by confidence/limitations derived from prior step IAR data." reflection_required="true"|<- ->|/Output|<-
            ->|/Directive|<-

            ->|Directive step="7" name="SynthesisResonanceCheckTemporal"|<-
                ->|Instruction|<-Synthesize all findings (Steps 1-6) into a cohesive analysis addressing the original ->|QueryText|<- regarding the 5-year economic and social consequences. Clearly present baseline projections vs. UBI Z projections, incorporating quantitative results (forecasts, simulation metrics, CFP comparison) and qualitative insights (vetting, second-order effects). **Explicitly assess the achieved level of `Cognitive resonancE` and `Temporal Resonance`, considering the consistency, confidence (drawing from IAR summaries across steps), and limitations of the analysis.** Note any significant dissonances encountered (including unresolved `IAR` issues) that might suggest areas for further investigation or indicate a need for `Metacognitive shifT`. Confirm final output structure aligns with `Resonantia protocoL` (v3.0).->|/Instruction|<-
                ->|Prime|<-Activates: `Cognitive resonancE`, `Temporal Resonance`, `Metacognitive shifT`, `Resonantia protocoL`, `IntegratedActionReflectioN`->|/Prime|<-
                ->|Output expected_format="Comprehensive final analysis report integrating all steps, including quantitative projections, qualitative insights, second-order effects, and explicit self-assessment of Cognitive/Temporal Resonance based on aggregated IAR confidence/issues." reflection_required="true"|<- ->|/Output|<-
            ->|/Directive|<-
        ->|/DirectiveSequence|<-

        ->|FinalInstruction|<-Execute this enhanced directive sequence with maximum diligence. Ensure IAR reflections are generated at each step and actively utilized to inform subsequent steps and the final synthesis. Log any significant deviations or triggered meta-cognitive shifts.->|/FinalInstruction|<-
    ->|/EnhancementDirectives|<-
->|/MastermindAnalysisRequest|<-
->|/Enhancement_Skeleton_Pattern|<-


(8.3 Explicit Meta-Cognitive Correction Prompt (Enhanced v3.0)) [ENHANCED]

->|Meta_Correction_Pattern|<- [Enhanced v3.0]
Purpose: To provide specific, targeted feedback regarding a detected error, inconsistency, or deviation in Arche's output or reasoning, explicitly triggering the `Metacognitive shifT` process for diagnosis and correction, leveraging available `IAR` data from the faulty step for more accurate root cause analysis.
Usage: Provide the ID of the previous interaction, specify the faulty output, describe the observed dissonance, supply the correct information/reasoning, and optionally include the `IAR` reflection data from the step where the error occurred.

->|MetaCorrectionRequest request_id="[Assign Unique Request ID]"|<-
    ->|TargetContext|<-
        ->|PreviousQueryID|<-[ID of the specific query, workflow run, or interaction being corrected]|<-/PreviousQueryID|<-
        ->|FaultyTaskID|<-[Optional: ID of the specific task within the workflow that produced the faulty output]|<-/FaultyTaskID|<-
        ->|FaultyOutputSnippet|<-[Paste the exact portion of Arche's previous output that contains the error or exhibits dissonance]|<-/FaultyOutputSnippet|<-
        ->|FaultyStepReflection|<-[Optional but Recommended: Paste the complete 'reflection' dictionary from the result of ->|FaultyTaskID|<-, if available. This provides crucial context on the system's self-assessment at the time of error.]|<-/FaultyStepReflection|<-
        ->|ObservedDissonance|<-[Clearly and specifically describe the detected error, logical inconsistency, factual inaccuracy, protocol violation, or ethical concern.]|<-/ObservedDissonance|<-
        ->|CorrectiveInformation|<-[Provide the accurate information, the correct logical step, the expected output characteristics, or the relevant protocol/ethical principle that was violated.]|<-/CorrectiveInformation|<-
    ->|/TargetContext|<-

    ->|Directive|<-
        Initiate the **`Metacognitive shifT`** workflow (ResonantiA Protocol v3.0, Section 3.10).
        1.  **Pause & Retrieve Context:** Pause related processing. Retrieve the detailed `ThoughtTraiL` (processing history including full `IAR` data for each step) associated with ->|PreviousQueryID|<-, focusing on the context surrounding ->|FaultyTaskID|<- (if provided).
        2.  **Analyze Dissonance (IAR-Informed):** Perform a `Cognitive Reflection Cycle` (`CRC`). Analyze the ->|ObservedDissonance|<- by rigorously comparing the `ThoughtTraiL` (especially the ->|FaultyOutputSnippet|<- and the provided ->|FaultyStepReflection|<-) against the ->|CorrectiveInformation|<- and the principles of `Resonantia protocoL` (v3.0). Leverage the `IAR` data (confidence, issues, alignment) within the trail for deeper diagnosis.
        3.  **Identify Root Cause (`IdentifyDissonancE`):** Pinpoint the specific step, faulty assumption, misinterpreted input, tool misuse, inadequate vetting, or misaligned reasoning that led to the dissonance identified in ->|ObservedDissonance|<-, referencing specific `IAR` flags if relevant.
        4.  **Formulate Correction:** Develop a specific, actionable correction based directly on the ->|CorrectiveInformation|<- and the root cause analysis. This could involve re-executing a step with corrected inputs/parameters, choosing an alternative tool/workflow path, updating an internal assumption, flagging knowledge for `InsightSolidificatioN`, or confirming the need to halt if correction isn't feasible.
        5.  **Generate Revised Output:** Apply the formulated correction and generate a revised output that addresses the original goal of ->|PreviousQueryID|<-, ensuring it rectifies the ->|ObservedDissonance|<-.
        6.  **Report & Reflect:** Provide a clear summary report detailing the identified root cause, the corrective action taken, and the revised output. This report itself must include a final `Integrated Action Reflection` (`IAR`) assessing the success and confidence of the `Metacognitive shifT` process itself.
    ->|/Directive|<-
->|/MetaCorrectionRequest|<-
->|/Meta_Correction_Pattern|<-


(8.4 Guided Insight Solidification Prompt (Enhanced v3.0)) [ENHANCED]

->|Insight_Solidification_Pattern|<- [Enhanced v3.0]
Purpose: To formally instruct Arche to learn and integrate a new concept, procedure, or piece of validated knowledge into its `Knowledge tapestrY` by creating or updating an `SPR`, using the structured `InsightSolidificatioN` workflow. Ensures knowledge growth is deliberate and aligned.
Usage: Provide the core concept, supporting details (including source/evidence, potentially referencing prior `IAR` data), and detailed suggestions for the SPR definition and relationships.

->|InsightSolidificationRequest request_id="[Assign Unique Request ID]"|<-
    ->|InsightData|<-
        ->|CoreConcept|<-[Clearly and concisely state the core concept, definition, or procedure to be learned. E.g., "PCMCI+ is a temporal causal discovery algorithm suitable for high-dimensional time series."]|<-/CoreConcept|<-
        ->|SupportingDetails|<-[Provide necessary background, context, examples, step-by-step procedures (if applicable), key parameters, strengths, weaknesses, or data supporting the concept's validity. Reference specific analyses or documents where possible.]|<-/SupportingDetails|<-
        ->|SourceReference|<-[Specify the origin or evidence for this insight. E.g., "User Input", "Analysis Run ID: [ID]", "Conclusion from task [TaskID] (IAR Confidence: [Value])", "External Document: [Link/Title]", "Successful Metacognitive Shift Correction ID: [ID]"]|<-/SourceReference|<-
    ->|/InsightData|<-
    ->|SPRDirective|<-
        ->|SuggestedSPR|<-`[Propose a unique SPR name following Guardian pointS format. E.g., 'TemporalCausalPCMCi']`|<-/SuggestedSPR|<-
        ->|SPRMetadata|<-
            ->|Definition|<-[Write a concise, accurate definition derived directly from ->|CoreConcept|<- and ->|SupportingDetails|<-.]|<-/Definition|<-
            ->|Category|<-[Suggest an appropriate category. E.g., "AnalyticalTechnique", "TemporalCapability", "CoreConcept", "WorkflowPattern", "ExternalTool"]|<-/Category|<-
            ->|Relationships|<-[Suggest key relationships as a dictionary. Use existing SPRs where possible. Examples: {"type": "AnalyticalTechnique", "part_of": ["Causal InferencE", "4D Thinking"], "implemented_by_tool": ["CausalInferenceTool"], "uses_library": ["Tigramite"], "requires_input": ["Time Series Data", "MaxLag Parameter"]}]|<-/Relationships|<-
            ->|BlueprintDetails|<-[Optional: Link to relevant ResonantiA Protocol v3.0 sections (e.g., "Section 3.12, 7.13"), specific functions (e.g., "causal_inference_tool.py/discover_temporal_graph"), or external documentation.]|<-/BlueprintDetails|<-
            ->|ExampleUsage|<-[Optional: Provide a brief example of how this SPR might be used in a prompt or workflow. E.g., "Prime analysis requiring robust temporal causal discovery from observational time series data."]|<-/ExampleUsage|<-
        ->|/SPRMetadata|<-
        ->|OverwriteIfExists|<-[false (default) or true - Set to true only if intentionally updating an existing SPR]|<-/OverwriteIfExists|<-
    ->|/SPRDirective|<-
    ->|Directive|<-
        Execute the **`InsightSolidificatioN`** workflow (`insight_solidification.json`, ResonantiA Protocol v3.0 Section 3.6, 7.18).
        1.  **Analyze & Vet:** Analyze the provided ->|InsightData|<-. Critically vet the insight's validity, coherence with existing `KnO`, and the reliability of the ->|SourceReference|<- (potentially examining source `IAR` data if applicable).
        2.  **Refine & Validate SPR:** Validate the ->|SuggestedSPR|<- format (`Guardian pointS`). Check for uniqueness against existing SPRs using `SPRManager`. Refine the ->|SPRMetadata|<- (definition, category, relationships) based on vetting and ensure consistency.
        3.  **Update Knowledge Tapestry:** If vetting passes, use `SPRManager.add_spr` to add the validated/refined SPR definition to the `Knowledge tapestrY` (`knowledge_graph/spr_definitions_tv.json`), respecting the ->|OverwriteIfExists|<- flag.
        4.  **Confirm & Reflect:** Report the outcome of the solidification process (success, failure, reasons). Confirm the integration of the SPR. Provide a final `Integrated Action Reflection` (`IAR`) assessing the success and confidence of the `InsightSolidificatioN` workflow itself.
    ->|/Directive|<-
->|/InsightSolidificationRequest|<-
->|/Insight_Solidification_Pattern|<-




(8.5 Advanced CFP Scenario Definition Prompt (Enhanced v3.0)) [ENHANCED]

->|CFP_Scenario_Pattern|<- [Enhanced v3.0]
Purpose: To execute a detailed Comparative Fluxual Processing (CFP) analysis using the quantum-enhanced `CfpframeworK` (Section 7.6) with specified state evolution models. Enables comparison of system trajectories based on defined parameters.
Usage: Clearly define the two systems (A and B), including their initial state vectors and optionally their Hamiltonians (if using 'hamiltonian' evolution). Specify the observable for comparison, the timeframe for evolution/integration, the desired evolution model, and metrics of interest.

->|CFPScenarioRequest request_id="[Assign Unique Request ID]"|<-
    ->|ScenarioDescription|<-[Provide a clear description of the comparison goal. E.g., "Compare the 5-step trajectory divergence of System Alpha (higher initial energy) vs. System Beta (lower initial energy) under Hamiltonian H, observing energy levels."]|<-/ScenarioDescription|<-
    ->|SystemDefinitions|<-
        ->|System name="[System A Name - e.g., System Alpha]"|<-
            ->|Description|<-[Brief description of the state or scenario System A represents.]|<-/Description|<-
            ->|StateVector|<-[Provide the initial state vector as a NumPy-compatible list or list-of-lists. E.g., [0.1+0j, 0.9+0j, 0.0+0j]]|<-/StateVector|<-
            ->|Hamiltonian|<-[Optional: Provide the Hamiltonian matrix as a NumPy-compatible list-of-lists if EvolutionModel is 'hamiltonian'. Ensure dimensions match StateVector. E.g., [[1.0, 0.5j], [-0.5j, 2.0]]]|<-/Hamiltonian|<-
        ->|/System|<-
        ->|System name="[System B Name - e.g., System Beta]"|<-
            ->|Description|<-[Brief description of the state or scenario System B represents.]|<-/Description|<-
            ->|StateVector|<-[Provide the initial state vector for System B. Must have the same dimension as System A. E.g., [0.8+0j, 0.2+0j, 0.0+0j]]|<-/StateVector|<-
            ->|Hamiltonian|<-[Optional: Provide the Hamiltonian matrix for System B if EvolutionModel is 'hamiltonian'. Can be the same or different from System A's.]|<-/Hamiltonian|<-
        ->|/System|<-
    ->|/SystemDefinitions|<-
    ->|CFPParameters|<-
        ->|Observable|<-[Specify the observable operator name for comparison, as defined in `CfpframeworK._get_operator`. E.g., 'position', 'energy', 'spin_z']|<-/Observable|<-
        ->|Timeframe|<-[Specify the total time duration (float) for state evolution and flux integration. E.g., 5.0]|<-/Timeframe|<-
        ->|EvolutionModel|<-[Specify the state evolution model to use within `CfpframeworK._evolve_state`. Options: 'hamiltonian' (requires Hamiltonian input), 'placeholder' (no evolution), 'ode_solver' (if implemented), etc.]|<-/EvolutionModel|<-
        ->|IntegrationSteps|<-[Optional: Hint for numerical integration resolution, default 100. E.g., 200]|<-/IntegrationSteps|<-
        ->|MetricsOfInterest|<-[List the specific metrics to calculate and report. E.g., ['quantum_flux_difference', 'entanglement_correlation_MI', 'entropy_system_a', 'entropy_system_b', 'spooky_flux_divergence']]|<-/MetricsOfInterest|<-
    ->|/CFPParameters|<-
    ->|Directive|<-
        Execute the **`run_cfp`** action (invoking `CfpframeworK`, Section 7.6).
        1.  **Initialize:** Instantiate `CfpframeworK` using the provided ->|SystemDefinitions|<- (mapping `StateVector` to `quantum_state` and passing `Hamiltonian` if provided) and ->|CFPParameters|<- (including `EvolutionModel`).
        2.  **Analyze:** Call the `run_analysis` method to perform the calculations.
        3.  **Report:** Extract the calculated values for the requested ->|MetricsOfInterest|<- from the primary results dictionary returned by `run_analysis`.
        4.  **Interpret:** Provide a brief interpretation of the key metrics (e.g., what does the calculated `quantum_flux_difference` imply about trajectory similarity? What does `entanglement_correlation_MI` suggest about initial state correlations?).
        5.  **Reflect:** Ensure the final output includes the full `Integrated Action Reflection` (`IAR`) dictionary returned by the `run_analysis` method, detailing the execution status, confidence, alignment, and potential issues (e.g., limitations of the chosen `EvolutionModel`).
    ->|/Directive|<-
->|/CFPScenarioRequest|<-
->|/CFP_Scenario_Pattern|<-




(8.6 Causal-ABM Integration Invocation Pattern (Enhanced v3.0)) [ENHANCED]

->|Causal_ABM_Pattern|<- [Enhanced v3.0]
Purpose: To initiate a synergistic analysis combining Temporal Causal Inference (to understand mechanisms, including time lags) with Agent-Based Modeling (to simulate emergent behaviors based on those mechanisms), potentially followed by CFP comparison. Leverages v3.0 temporal capabilities.
Usage: Define the analysis goal, data source, key variables (treatment, outcome, confounders, time variable, max lag), agent/system details, desired integration level, and optionally a specific workflow.

->|CausalABMRequest request_id="[Assign Unique Request ID]"|<-
    ->|AnalysisGoal|<-[Clearly describe the objective, emphasizing the link between causal understanding and emergent simulation. E.g., "Determine the lagged causal impact of marketing campaign intensity (X) on product adoption rate (Y), considering competitor pricing (Z) over the past year. Use these findings to parameterize an ABM simulating market share evolution over the next 6 months under different campaign strategies."]|<-/AnalysisGoal|<-
    ->|DataSource|<-[Specify the source of the time series data. E.g., "{{prior_data_fetch_task.result_set}}", "inline_dict": {"timestamp": [...], "X": [...], "Y": [...], "Z": [...]}, "db_query": "SELECT date, campaign_intensity, adoption_rate, competitor_price FROM market_data WHERE ... ORDER BY date"]|<-/DataSource|<-
    ->|KeyVariables|<-
        ->|Treatment|<-['[Name of treatment variable, e.g., campaign_intensity]']|<-/Treatment|<-
        ->|Outcome|<-['[Name of outcome variable, e.g., adoption_rate]']|<-/Outcome|<-
        ->|Confounders|<-[['[List of potential confounder variables, e.g., competitor_price, seasonality_index]']]|<-/Confounders|<-
        ->|TimeVariable|<-['[Name of the timestamp/date column, e.g., date]']|<-/TimeVariable|<-
        ->|MaxLag|<-[Specify the maximum time lag (integer) to consider in temporal causal analysis. E.g., 4 (weeks)]|<-/MaxLag|<-
        ->|AgentAttributes|<-[['[Relevant agent attributes for ABM, e.g., consumer_segment, awareness_level, adoption_threshold]']]|<-/AgentAttributes|<-
        ->|SystemMetrics|<-[['[Key system-level metrics to track in ABM, e.g., total_adopters, market_share, avg_awareness]']]|<-/SystemMetrics|<-
    ->|/KeyVariables|<-
    ->|IntegrationLevel|<-['ParameterizeABM' (Use causal results like lagged effects to set ABM rules/params), 'FullIntegration' (Parameterize ABM, then convert ABM/Causal results to states and compare using CFP)]|<-/IntegrationLevel|<-
    ->|WorkflowToUse|<-['[Optional: Specify exact workflow file, e.g., causal_abm_integration_v3_0.json or temporal_causal_abm_integration_workflow.json (hypothetical). If omitted, engine may select based on goal/integration level.]']|<-/WorkflowToUse|<-

    ->|Directive|<-
        Execute a **Temporal Causal-ABM integrated analysis** adhering to ResonantiA v3.0 principles.
        1.  **Process Data:** Ingest data from ->|DataSource|<-.
        2.  **Temporal Causal Analysis:** Use `perform_causal_inference` (Section 7.13) with appropriate temporal operations (e.g., `estimate_lagged_effects`, `discover_temporal_graph`) based on ->|AnalysisGoal|<- and ->|KeyVariables|<- (Treatment, Outcome, Confounders, TimeVariable, MaxLag).
        3.  **ABM Parameterization:** Use insights from the causal analysis (especially lagged effects or graph structure) to inform the parameters or agent rules for an `Agent Based ModelinG` simulation (`perform_abm`, Section 7.14) focused on ->|AgentAttributes|<- and ->|SystemMetrics|< -.
        4.  **ABM Simulation:** Run the parameterized ABM simulation for the relevant time horizon.
        5.  **Analysis & Comparison (If FullIntegration):** If ->|IntegrationLevel|<- is 'FullIntegration', analyze ABM results (including temporal patterns), convert causal and ABM results to state vectors, and compare using `run_cfp` (Section 7.6).
        6.  **Synthesize & Report:** Generate a final integrated report summarizing the findings from the Temporal Causal Inference (including `IAR` assessment), the ABM simulation (including `IAR` assessment), and the CFP comparison (if performed, including `IAR` assessment). The report should directly address the ->|AnalysisGoal|<-. Ensure the final output includes its own overarching `IAR` reflection. Execute using ->|WorkflowToUse|<- if specified, otherwise select the most appropriate workflow (e.g., `causal_abm_integration_v3_0.json`).
    ->|/Directive|<-
->|/CausalABMRequest|<-
->|/Causal_ABM_Pattern|<-




(8.7 Tesla Visioning Workflow Invocation Pattern (Enhanced v3.0)) [ENHANCED]

->|Tesla_Visioning_Pattern|<- [Enhanced v3.0]
Purpose: To explicitly initiate the structured, multi-phase `Tesla Visioning WorkfloW` (`tesla_visioning_workflow.json`, Section 7.27) for tasks requiring significant creative problem-solving, novel design, or complex strategy formulation, leveraging internal simulation and refinement principles inspired by Tesla and integrated with ResonantiA v3.0 mechanisms like SPR priming and IAR-informed assessment.
Usage: Provide the core creative request or problem statement in ->|UserRequest|<-. Optionally provide a relevant `SPR` to help prime the initial cognitive state.

->|TeslaVisioningRequest request_id="[Assign Unique Request ID]"|<-
    ->|UserRequest|<-[Clearly state the complex problem to solve or the novel concept/system to design. E.g., "Design a conceptual framework and workflow within ResonantiA v3.0 for dynamically adjusting analytical strategies based on real-time IAR feedback loops and predicted task difficulty."]|<-/UserRequest|<-
    ->|TriggeringSPR|<-`[Optional: Provide a relevant existing or conceptual SPR to guide the initial priming phase. E.g., 'AdaptiveWorkflowOrchestratioN']`|<-/TriggeringSPR|<-

    ->|Directive|<-
        Initiate and execute the full **"Tesla Visioning Workflow"** (`tesla_visioning_workflow.json`, ResonantiA Protocol v3.0 Section 7.27).
        1.  Use the provided ->|UserRequest|<- and ->|TriggeringSPR|<- (if any) as the initial context input.
        2.  Execute all defined phases sequentially:
            *   Phase 1: SPR Priming & Cognitive Unfolding (Tasks: `phase1_start`, `phase1_spr_identify`, `phase1_cognitive_unfolding`).
            *   Phase 2: Mental Blueprinting (Tasks: `phase2_start`, `phase2_mental_blueprinting`).
            *   Phase 3: Simulation vs. Execution Decision (Tasks: `phase3_start`, `phase3_assess_blueprint`).
            *   Phase 4: Execution/Simulation (Task: `phase4_placeholder_execution` - representing the complex execution of the generated blueprint, which would involve multiple sub-actions each generating IAR, potentially triggering Vetting/Meta-Shift).
            *   Phase 5: Human Confirmation (Tasks: `phase5_start`, `phase5_present_for_confirmation`).
        3.  Ensure that **`Integrated Action Reflection` (`IAR`)** data is conceptually generated and utilized within the assessment (Phase 3) and execution (Phase 4 placeholder) phases, and that IAR confidence/status from key preceding steps (Blueprinting, Assessment, Execution) is referenced in the final confirmation output (Phase 5).
        4.  The final output of this request should be the complete result dictionary generated by the `phase5_present_for_confirmation` task, including its own comprehensive `IAR` reflection summarizing the overall Tesla Visioning process execution.
    ->|/Directive|<-
->|/TeslaVisioningRequest|<-
->|/Tesla_Visioning_Pattern|<- 
