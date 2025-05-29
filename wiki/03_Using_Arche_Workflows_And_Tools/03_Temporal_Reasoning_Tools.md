# 3. Temporal Reasoning Tools (4D Thinking in Practice)

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
For each temporal tool, explain its purpose, key operations/parameters, example usage (linking to example workflows if available), and specific IAR considerations (how it calculates confidence, common potential_issues it might report).
-->

This page details Arche's Temporal Reasoning Tools, which are central to its 4D Thinking capabilities. Each tool's usage, key operations, example workflows, and Integrated Action Reflection (IAR) considerations are discussed.

--- 

### `run_prediction` (PredictivE ModelinG TooL - Protocol Section 7.19)

*   **Purpose:** Performs time-series forecasting and predictive modeling.
*   **Key Operations / Parameters:**
    *   `action`: Specific operation (e.g., "train_model", "forecast_future_states", "evaluate_model").
    *   `data_path` or `series_data`: Path to historical data or the data itself.
    *   `target_column`: Name of the column to forecast.
    *   `feature_columns`: (Optional) Exogenous variables for models like ARIMA-X.
    *   `model_type`: (e.g., "ARIMA", "Prophet", "LSTM" - from `config.py` defaults or specified).
    *   `model_params`: Specific parameters for the chosen model (e.g., ARIMA order (p,d,q)).
    *   `steps_to_forecast`: Number of future steps to predict.
    *   `model_save_path`: (Optional) Path to save a trained model.
    *   `model_load_path`: (Optional) Path to load a pre-trained model.
*   **Example Usage:**
    *   Forecasting with ARIMA: See `temporal_forecasting_workflow.json` (Link: `../../workflows/temporal_forecasting_workflow.json`).
    *   This workflow demonstrates training a model and generating future state predictions.
*   **IAR Considerations (`reflection` key):**
    *   `confidence`: Can be based on model evaluation metrics (e.g., lower RMSE/MAE implies higher confidence), stability of forecast intervals, or successful model fitting. Lower if fitting fails or data is insufficient.
    *   `potential_issues`: "Model fitting failed: [error]", "Insufficient data for reliable forecast", "Data not stationary (for ARIMA)", "High forecast uncertainty/wide confidence intervals", "Model evaluation metrics poor", "Error loading/saving model".

--- 

### `perform_causal_inference` (CausalInferenceTool - Protocol Section 7.13)

*   **Purpose:** Identifies and estimates causal relationships, including temporal (lagged) effects.
*   **Key Operations / Parameters:**
    *   `action`: Specific operation (e.g., "estimate_effect", "run_granger_causality", "discover_temporal_graph", "estimate_lagged_effects").
    *   `data_path` or `data`: Path to data or the DataFrame itself.
    *   `treatment_column`: Name of the treatment variable.
    *   `outcome_column`: Name of the outcome variable.
    *   `instrument_column`: (Optional) Name of an instrumental variable.
    *   `common_causes_columns`: (Optional) Confounding variables.
    *   `max_lag`: (For temporal methods like Granger or VAR) Maximum lag to consider.
    *   `significance_level`: (e.g., 0.05) for statistical tests.
*   **Example Usage:**
    *   Temporal Causal Analysis: See `temporal_causal_analysis_workflow.json` (Link: `../../workflows/temporal_causal_analysis_workflow.json`).
    *   This workflow might demonstrate running Granger causality or estimating lagged effects using VAR models.
*   **IAR Considerations (`reflection` key):**
    *   `confidence`: Can be based on statistical significance (e.g., p-values), model fit (for model-based estimation), or robustness to assumption checks. Causal claims are often hard to make with high confidence.
    *   `potential_issues`: "Causal assumptions may be violated (e.g., unobserved confounders)", "Insufficient data for robust estimation", "Granger causality does not imply true causation", "Model misspecification", "Statistical test assumptions not met", "Low statistical power".

--- 

### `perform_abm` (AgentBasedModelingTool - Protocol Section 7.14)

*   **Purpose:** Creates, runs, and analyzes agent-based models to simulate emergent behaviors.
*   **Key Operations / Parameters:**
    *   `action`: (e.g., "create_model", "run_simulation", "analyze_results", "convert_to_state_vector").
    *   `model_definition_path` or `model_class`: Path to Python file defining the Mesa Agent/Model classes or the classes themselves.
    *   `simulation_params`: Dictionary of parameters to pass to the model constructor (e.g., number of agents, grid size, interaction rules).
    *   `num_steps`: Number of steps to run the simulation.
    *   `analysis_config`: Configuration for the `analyze_results` step (e.g., metrics to track, temporal patterns to detect like convergence, oscillation).
*   **Example Usage:**
    *   Running a basic grid model: See `simple_causal_abm_test_v3_0.json` (Link: `../../workflows/simple_causal_abm_test_v3_0.json`).
    *   This workflow demonstrates setting up a model, running it, and analyzing its output.
*   **IAR Considerations (`reflection` key):**
    *   `confidence`: Can reflect simulation stability (e.g., did it crash?), convergence if expected, clarity of emergent patterns. Lower if results are highly stochastic or sensitive to initial conditions without clear patterns.
    *   `potential_issues`: "Simulation unstable or crashed", "Results highly sensitive to initial parameters", "No clear emergent pattern detected", "Analysis limitations: [details]", "Model definition error: [error]".

--- 

### `run_cfp` (CfpframeworK - Protocol Section 7.6)

*   **Purpose:** Compares the dynamics of two systems/scenarios using quantum-inspired principles and implemented state evolution.
*   **Key Input Parameters:**
    *   `system_a_config`: Configuration for system A (e.g., initial state vector, Hamiltonian/ODE definition, parameters).
    *   `system_b_config`: Configuration for system B.
    *   `observable_definition`: Definition of the observable to measure (e.g., a specific function of the state).
    *   `time_horizon`: Duration over which to simulate and compare evolution.
    *   `evolution_model_type`: (e.g., "custom_ode", "hamiltonian") Specifies how `_evolve_state` should work.
    *   `num_time_points`: Number of points to evaluate over the horizon.
*   **Example Usage:**
    *   Comparing scenario state vectors: See `comparative_future_scenario_workflow.json` (Link: `../../workflows/comparative_future_scenario_workflow.json`).
    *   This workflow would define two scenarios (e.g., from predictive model outputs) and use CFP to compare their evolution.
*   **IAR Considerations (`reflection` key):**
    *   `confidence`: Based on numerical stability of the evolution, precision of calculations, successful execution of the comparison. Lower if evolution models are placeholders or significant numerical errors occur.
    *   `potential_issues`: "Evolution model is a placeholder/not fully implemented", "Numerical instability during state evolution", "High Spooky Flux Divergence indicates significant deviation (interpret with care)", "Observable definition error", "Calculation error: [details]".

--- 

*Note: Effective use of these temporal tools often involves careful data preprocessing, thoughtful model/parameter selection, and critical interpretation of results, guided by the IAR data.* 