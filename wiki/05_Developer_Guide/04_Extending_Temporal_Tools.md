# 4. Extending Temporal Tools

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Focus on the specific considerations for temporal tools: data handling, model integration, parameterization, and IAR for uncertainty.
-->

This page provides guidance for developers on extending Arche's Temporal Reasoning Tools (e.g., `PredictiveModelingTool`, `CausalInferenceTool`, `AgentBasedModelingTool`, `CfpFramework`). These tools often involve more complex state management, data handling, and IAR considerations related to uncertainty and model validity.

*   **General Considerations for Temporal Tools**
    *   **Time-Series Data Handling:**
        *   Ensure robust handling of time-series data formats (e.g., Pandas DataFrames with DatetimeIndex).
        *   Implement clear data validation for timestamps, frequency, and missing values.
        *   Consider how the tool will handle different time granularities.
    *   **Model Integration:**
        *   If integrating new forecasting models, causal inference algorithms, or ABM frameworks, ensure they can be parameterized and invoked cleanly.
        *   Abstract away library-specific complexities where possible.
    *   **State Management (for multi-step operations):**
        *   Temporal analyses can be multi-step (e.g., train model, then predict; define ABM, then run, then analyze).
        *   The `action` parameter within the tool's input is often used to control these steps.
        *   Consider how intermediate state (e.g., a trained model object, simulation state) is passed between these steps. It might be stored in memory (if small and for short sequences) or written to/read from disk (`outputs/models/` or a temporary location), with paths passed in the workflow context.
    *   **Parameterization:**
        *   Expose key model and analysis parameters through the tool's input arguments (defined in the workflow).
        *   Provide sensible defaults in `config.py` where appropriate.
*   **Specific IAR Considerations for Temporal Tools**
    *   **`confidence`:** This is particularly nuanced for temporal tools.
        *   **Predictive Models:** Confidence can be derived from model evaluation metrics (e.g., 1 - MAPE, or scaled RMSE), width of prediction intervals, or stability of model parameters.
        *   **Causal Inference:** Confidence might relate to p-values of causal links, robustness to sensitivity analyses, or model fit statistics. Often, causal claims have inherently lower confidence than associative claims.
        *   **ABM:** Confidence might reflect simulation stability, convergence to a steady state (if expected), or the clarity/robustness of emergent patterns.
        *   **CFP:** Confidence can relate to numerical stability of simulations, precision of calculations.
    *   **`potential_issues` (Crucial for Temporal Tools):** This list should be comprehensive.
        *   **Data Issues:** "Insufficient historical data", "Data not stationary (for ARIMA)", "High percentage of missing values", "Inconsistent time frequency detected".
        *   **Model/Algorithm Issues:** "Model fitting failed: [error]", "Algorithm did not converge", "Assumptions of the model may be violated (e.g., linearity, exogeneity)", "High forecast uncertainty / wide prediction intervals", "Poor model evaluation metrics: [metric_name]=[value]", "Granger causality does not imply true causation".
        *   **Simulation Issues (ABM/CFP):** "Simulation unstable", "Results highly sensitive to initial parameters/stochasticity", "Observable definition error in CFP".
        *   **Interpretation Caveats:** "Correlation does not imply causation", "Forecast accuracy degrades over longer horizons".
    *   **`summary`:** Should clearly state the action performed (e.g., "ARIMA model trained", "Forecast generated for 12 steps", "Granger causality test completed") and key quantitative outcomes (e.g., "RMSE: 5.2", "Identified causal link from X to Y with p-value 0.03").
*   **Extending `PredictiveModelingTool` (Example)**
    *   **Adding a New Model Type (e.g., "ExponentialSmoothing"):**
        1.  Implement the fitting and prediction logic for Exponential Smoothing in `predictive_modeling_tool.py` or a helper module.
        2.  Add "ExponentialSmoothing" as a recognized `model_type`.
        3.  Define relevant parameters (e.g., `trend`, `seasonal`, `seasonal_periods`) and handle them in your new logic.
        4.  Implement IAR: How will confidence be assessed? What are specific potential issues for this model?
        5.  Add default parameters to `config.py` if desired.
        6.  Update documentation and tests.
*   **Extending `CausalInferenceTool` (Example)**
    *   **Adding a New Causal Discovery Algorithm:**
        1.  Integrate the new algorithm into `causal_inference_tool.py`.
        2.  Add a new `action` (e.g., "discover_causal_graph_pcalg") or a new `method` parameter.
        3.  Handle its specific input requirements and output formats.
        4.  Implement IAR: Confidence might be based on edge reliability scores if the algorithm provides them. `potential_issues` should highlight algorithm assumptions and limitations.
*   **Testing Temporal Tool Extensions**
    *   Use well-understood datasets where temporal patterns or causal links are known or expected.
    *   Test sensitivity to different data characteristics (e.g., seasonality, trends, noise levels).
    *   Verify that IAR outputs (especially `confidence` and `potential_issues`) change appropriately with varying input data and model performance.
    *   Ensure that saving/loading of models or intermediate states works correctly.

*Extending temporal tools requires a good understanding of the underlying algorithms and a diligent approach to implementing the IAR contract to reflect the inherent uncertainties and assumptions in time-dependent analyses.* 