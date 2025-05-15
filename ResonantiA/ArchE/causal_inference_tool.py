# --- START OF FILE 3.0ArchE/causal_inference_tool.py ---
# ResonantiA Protocol v3.0 - causal_inference_tool.py
# Implements Causal Inference capabilities with Temporal focus.
# Includes functional DoWhy estimation and statsmodels Granger causality/VAR.
# Graph discovery remains conceptual/simulated.
# Returns results including mandatory Integrated Action Reflection (IAR).

import json
import logging
import pandas as pd
import numpy as np
import time
import networkx as nx # For graph representation if needed
from typing import Dict, Any, Optional, List, Union, Tuple # Expanded type hints
# Use relative imports for configuration
try:
    from . import config
except ImportError:
    # Fallback config if running standalone or package structure differs
    class FallbackConfig: CAUSAL_DEFAULT_DISCOVERY_METHOD="PC"; CAUSAL_DEFAULT_ESTIMATION_METHOD="backdoor.linear_regression"; CAUSAL_DEFAULT_TEMPORAL_METHOD="Granger"
    config = FallbackConfig(); logging.warning("config.py not found for causal tool, using fallback configuration.")

# --- Import Causal Libraries (Set flag based on success) ---
CAUSAL_LIBS_AVAILABLE = False
DOWHY_AVAILABLE = False
STATSMODELS_AVAILABLE = False
# Add flags for causal-learn, tigramite if implementing those discovery methods
try:
    import dowhy
    from dowhy import CausalModel
    DOWHY_AVAILABLE = True
    import statsmodels.api as sm # For Granger, VAR models
    from statsmodels.tsa.stattools import grangercausalitytests
    from statsmodels.tsa.api import VAR # For lagged effects estimation
    STATSMODELS_AVAILABLE = True

    CAUSAL_LIBS_AVAILABLE = DOWHY_AVAILABLE and STATSMODELS_AVAILABLE # Set based on core libs needed for implemented features
    log_msg = "Actual causal inference libraries loaded: "
    if DOWHY_AVAILABLE: log_msg += "DoWhy, "
    if STATSMODELS_AVAILABLE: log_msg += "statsmodels"
    logging.getLogger(__name__).info(log_msg.strip(', '))

except ImportError as e_imp:
    logging.getLogger(__name__).warning(f"Causal libraries import failed: {e_imp}. Causal Inference Tool functionality will be limited or simulated.")
except Exception as e_imp_other:
    logging.getLogger(__name__).error(f"Unexpected error importing causal libraries: {e_imp_other}. Tool simulating.")

logger = logging.getLogger(__name__)

# --- IAR Helper Function ---
# (Reused for consistency)
def _create_reflection(status: str, summary: str, confidence: Optional[float], alignment: Optional[str], issues: Optional[List[str]], preview: Any) -> Dict[str, Any]:
    """Helper function to create the standardized IAR reflection dictionary."""
    if confidence is not None: confidence = max(0.0, min(1.0, confidence))
    issues_list = issues if issues else None
    try:
        preview_str = json.dumps(preview, default=str) if isinstance(preview, (dict, list)) else str(preview)
        if preview_str and len(preview_str) > 150: preview_str = preview_str[:150] + "..."
    except Exception:
        try: preview_str = str(preview); preview_str = preview_str[:150] + "..." if len(preview_str) > 150 else preview_str
        except Exception: preview_str = "[Preview Error]"
    return {"status": status, "summary": summary, "confidence": confidence, "alignment_check": alignment if alignment else "N/A", "potential_issues": issues_list, "raw_output_preview": preview_str}

# --- Data Preparation Helper ---
# (Similar to predictive tool, but might need different handling)
def _prepare_causal_data(data: Union[Dict, pd.DataFrame]) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Converts input data to DataFrame and performs basic validation."""
    df: Optional[pd.DataFrame] = None
    error_msg: Optional[str] = None
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            error_msg = f"Invalid 'data' type: {type(data)}. Expected dict or DataFrame."
            return None, error_msg

        if df.empty:
            error_msg = "Input data is empty."
            return None, error_msg

        # Basic check for non-numeric types that might cause issues
        if df.select_dtypes(include=[object]).shape[1] > 0:
            logger.warning("Input data contains object columns. Ensure categorical variables are properly encoded for the chosen causal method.")

        return df, None # Return DataFrame and no error
    except Exception as e_prep:
        error_msg = f"Causal data preparation failed: {e_prep}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg

# --- Main Tool Function ---
def perform_causal_inference(operation: str, **kwargs) -> Dict[str, Any]:
    """
    [IAR Enabled] Main wrapper for causal inference operations (Static & Temporal).
    Dispatches to specific implementation or simulation based on 'operation'.
    Implements DoWhy estimation and Granger causality.

    Args:
        operation (str): The causal operation to perform (e.g., 'discover_graph',
                        'estimate_effect', 'run_granger_causality',
                        'discover_temporal_graph', 'estimate_lagged_effects',
                        'convert_to_state'). Required.
        **kwargs: Arguments specific to the operation (e.g., data, treatment, outcome,
                  confounders, target_column, max_lag, method, causal_result).

    Returns:
        Dict[str, Any]: Dictionary containing results and IAR reflection.
    """
    # --- Initialize Results & Reflection ---
    primary_result = {"operation_performed": operation, "error": None, "libs_available": CAUSAL_LIBS_AVAILABLE, "note": ""}
    reflection_status = "Failure"; reflection_summary = f"Causal op '{operation}' init failed."; confidence = 0.0; alignment = "N/A"; issues = ["Initialization error."]; preview = None

    logger.info(f"Performing causal inference operation: '{operation}'")

    # --- Simulation Mode Check (If core libs needed for operation are missing) ---
    needs_dowhy = operation in ['estimate_effect']
    needs_statsmodels = operation in ['run_granger_causality', 'estimate_lagged_effects']
    libs_needed = (needs_dowhy and not DOWHY_AVAILABLE) or (needs_statsmodels and not STATSMODELS_AVAILABLE)

    # Graph discovery is always simulated for now
    is_simulated_op = operation in ['discover_graph', 'discover_temporal_graph'] or libs_needed

    if is_simulated_op:
        missing_libs = []
        if needs_dowhy and not DOWHY_AVAILABLE: missing_libs.append("DoWhy")
        if needs_statsmodels and not STATSMODELS_AVAILABLE: missing_libs.append("statsmodels")
        libs_str = ", ".join(missing_libs) if missing_libs else "N/A"
        sim_reason = f"Missing libs: {libs_str}" if libs_needed else "Operation simulated by design"
        logger.warning(f"Simulating causal inference operation '{operation}'. Reason: {sim_reason}.")
        primary_result["note"] = f"SIMULATED result ({sim_reason})"
        sim_result = _simulate_causal_inference(operation, **kwargs)
        primary_result.update(sim_result)
        primary_result["error"] = sim_result.get("error", primary_result.get("error"))
        if primary_result["error"]:
            reflection_status = "Failure"; reflection_summary = f"Simulated causal op '{operation}' failed: {primary_result['error']}"; confidence = 0.1; issues = [primary_result["error"]]
        else:
            reflection_status = "Success"; reflection_summary = f"Simulated causal op '{operation}' completed."; confidence = 0.6; alignment = "Aligned with causal analysis goal (simulated)."; issues = ["Result is simulated."]; preview = {k:v for k,v in primary_result.items() if k not in ['operation_performed','error','libs_available','note']}
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, confidence, alignment, issues, preview)}

    # --- Actual Implementation Dispatch ---
    try:
        op_result: Dict[str, Any] = {} # Store result from the specific operation function

        # --- Operation Specific Logic ---
        # Note: discover_graph and discover_temporal_graph fall through to simulation above
        if operation == 'estimate_effect':
            op_result = _estimate_effect(**kwargs)
        elif operation == 'run_granger_causality':
            op_result = _run_granger_causality(**kwargs)
        elif operation == 'estimate_lagged_effects':
            op_result = _estimate_lagged_effects(**kwargs)
        elif operation == 'convert_to_state':
            op_result = _convert_causal_to_state(**kwargs)
        else:
            op_result = {"error": f"Unknown causal inference operation specified: {operation}"}
            op_result["reflection"] = _create_reflection("Failure", op_result["error"], 0.0, "N/A", ["Unknown operation"], None)

        # --- Process Result and Extract Reflection ---
        primary_result.update(op_result)
        internal_reflection = primary_result.pop("reflection", None) if isinstance(primary_result, dict) else None

        if internal_reflection is None:
            logger.error(f"Internal reflection missing from causal operation '{operation}' result! Protocol violation.")
            internal_reflection = _create_reflection("Failure", "Internal reflection missing from tool.", 0.0, "N/A", ["Tool implementation error: Missing IAR."], op_result)
            primary_result["error"] = primary_result.get("error", "Internal reflection missing.")

        # --- Final Return ---
        primary_result["reflection"] = internal_reflection
        return primary_result

    except Exception as e_outer:
        # Catch unexpected errors in the main dispatch logic
        logger.error(f"Critical error during causal inference operation '{operation}': {e_outer}", exc_info=True)
        primary_result["error"] = f"Critical failure in causal tool orchestration: {e_outer}"
        reflection_issues = [f"Critical failure: {e_outer}"]
        reflection_summary = f"Critical failure during operation '{operation}': {e_outer}"
        return {**primary_result, "reflection": _create_reflection("Failure", reflection_summary, 0.0, "N/A", reflection_issues, None)}

# --- Internal Helper Functions for Operations ---

def _discover_graph(**kwargs) -> Dict[str, Any]:
    """[Conceptual/Simulated] Discovers causal graph structure."""
    # Requires implementation using libraries like causal-learn, pcalg, tetrad, etc.
    # Simulation logic remains from previous version for now.
    data = kwargs.get("data")
    method = kwargs.get('method', config.CAUSAL_DEFAULT_DISCOVERY_METHOD)
    alpha = float(kwargs.get('alpha', 0.05))
    logger.warning(f"Actual graph discovery ('discover_graph' using {method}) not implemented. Returning simulated graph.")
    sim_result = _simulate_causal_inference('discover_graph', data=data, method=method, alpha=alpha)
    issues = ["Graph discovery is simulated.", "Actual implementation required using appropriate libraries (e.g., causal-learn)."]
    confidence = 0.2 # Low confidence for simulation
    summary = f"Simulated graph discovery using method '{method}'."
    status = "Success" if sim_result.get("error") is None else "Failure"
    if sim_result.get("error"): issues.append(sim_result["error"])
    return {**sim_result, "reflection": _create_reflection(status, summary, confidence, "Aligned (Simulated)", issues, sim_result.get('graph'))}

def _estimate_effect(**kwargs) -> Dict[str, Any]:
    """[Implemented] Estimates causal effect using DoWhy."""
    # --- Initialize ---
    primary_result = {"causal_effect": None, "estimand": None, "confidence_intervals": None, "refutation_results": None, "error": None}
    reflection_status = "Failure"; summary = "Effect estimation init failed."; confidence = 0.0; alignment = "N/A"; issues = []; preview = None

    if not DOWHY_AVAILABLE:
        primary_result["error"] = "DoWhy library not available for effect estimation."
        return {**primary_result, "reflection": _create_reflection(reflection_status, summary, confidence, alignment, [primary_result["error"]], None)}

    try:
        # --- Extract & Validate Parameters ---
        data_input = kwargs.get("data")
        treatment = kwargs.get("treatment")
        outcome = kwargs.get("outcome")
        graph_dot_string = kwargs.get("graph_dot_string") # DOT format string for graph
        common_causes = kwargs.get("common_causes") # List of confounder names
        method_name = kwargs.get("method", config.CAUSAL_DEFAULT_ESTIMATION_METHOD) # e.g., "backdoor.linear_regression"
        proceed_unidentifiable = kwargs.get("proceed_when_unidentifiable", True)

        if data_input is None: raise ValueError("Missing 'data' input.")
        if not treatment: raise ValueError("Missing 'treatment' variable name.")
        if not outcome: raise ValueError("Missing 'outcome' variable name.")
        if not graph_dot_string and not common_causes: logger.warning("Neither 'graph_dot_string' nor 'common_causes' provided. DoWhy will attempt discovery if possible, but results may be biased.")
        if graph_dot_string and common_causes: logger.warning("Both 'graph_dot_string' and 'common_causes' provided. Using 'graph_dot_string'.")

        # Prepare data
        df, prep_error = _prepare_causal_data(data_input)
        if prep_error: raise ValueError(f"Data preparation failed: {prep_error}")
        if df is None: raise ValueError("Data preparation returned None.")

        # --- Perform Causal Estimation with DoWhy ---
        logger.info(f"Estimating effect of '{treatment}' on '{outcome}' using DoWhy (Method: {method_name})...")
        # 1. Create Causal Model
        # Use graph string if provided, otherwise common_causes (DoWhy might infer graph if neither given)
        model = CausalModel(data=df, treatment=treatment, outcome=outcome,
                            graph=graph_dot_string if graph_dot_string else None,
                            common_causes=common_causes if not graph_dot_string else None)
        logger.debug("DoWhy CausalModel created.")

        # 2. Identify Estimand
        identified_estimand = model.identify_effect(proceed_when_unidentifiable=proceed_unidentifiable)
        primary_result["estimand"] = identified_estimand.text_estimand # Store identified formula
        logger.info(f"Identified Estimand: {primary_result['estimand']}")
        if "Unobserved Confounders" in primary_result["estimand"] and not proceed_unidentifiable:
             raise ValueError("Causal effect is unidentifiable due to potential unobserved confounders. Set proceed_when_unidentifiable=True to attempt estimation anyway.")

        # 3. Estimate Effect
        causal_estimate = model.estimate_effect(identified_estimand, method_name=method_name)
        primary_result["causal_effect"] = float(causal_estimate.value) # Store estimated effect
        logger.info(f"Estimated Causal Effect ({method_name}): {primary_result['causal_effect']:.4f}")

        # Extract Confidence Intervals if available (depends on estimator)
        if hasattr(causal_estimate, 'get_confidence_intervals'):
            try:
                ci_result = causal_estimate.get_confidence_intervals()
                primary_result["confidence_intervals"] = [float(ci_result[0]), float(ci_result[1])]
                logger.info(f"Confidence Intervals: {primary_result['confidence_intervals']}")
            except Exception as e_ci: logger.warning(f"Could not retrieve confidence intervals: {e_ci}")

        # 4. Refute Estimate (Optional but Recommended)
        # Example: Placebo treatment refuter
        try:
            refute_placebo = model.refute_estimate(identified_estimand, causal_estimate, method_name="placebo_treatment_refuter")
            primary_result["refutation_results"] = primary_result.get("refutation_results", {})
            # Store p-value, interpret 'passed' based on significance level (e.g., > 0.05)
            p_val = float(refute_placebo.refutation_result['p_value']) if refute_placebo.refutation_result else 1.0
            passed = bool(p_val > 0.05)
            primary_result["refutation_results"]["placebo_treatment"] = {"p_value": p_val, "passed": passed}
            logger.info(f"Placebo Treatment Refutation p-value: {p_val:.4f} (Passed: {passed})")
        except Exception as e_refute: logger.warning(f"Placebo refutation failed: {e_refute}")
        # Add other refuters (e.g., random_common_cause, data_subset_refuter) if desired

        # --- Generate IAR ---
        reflection_status = "Success"
        summary = f"Causal effect of '{treatment}' on '{outcome}' estimated using {method_name}."
        # Confidence is inherently lower for causal claims
        confidence = 0.65
        alignment = "Aligned with causal effect estimation goal."
        issues = ["Causal effect estimates depend heavily on model assumptions (e.g., graph structure, no unobserved confounders)."]
        if "Unobserved Confounders" in primary_result["estimand"]: issues.append("Potential bias due to unobserved confounders (unidentifiable estimand).")
        if primary_result.get("refutation_results"):
            placebo_passed = primary_result["refutation_results"].get("placebo_treatment", {}).get("passed")
            if placebo_passed is False:
                issues.append("Refutation failed (Placebo Treatment): Estimate may be unreliable.")
                confidence = max(0.1, confidence - 0.3) # Reduce confidence if refutation fails
            elif placebo_passed is True:
                confidence = min(0.9, confidence + 0.1) # Increase confidence slightly if passed
        preview = {"effect": primary_result["causal_effect"], "ci": primary_result["confidence_intervals"]}

    except (ValueError, TypeError, ImportError) as e_val:
        primary_result["error"] = f"Input/Validation/Import Error: {e_val}"
        issues = [str(e_val)]; summary = f"Estimation failed: {e_val}"; confidence = 0.0
    except Exception as e_est: # Catch DoWhy specific or other errors
        primary_result["error"] = f"DoWhy estimation failed: {e_est}"
        logger.error(f"Error during DoWhy effect estimation: {e_est}", exc_info=True)
        issues = [f"DoWhy Error: {e_est}"]; summary = f"Estimation failed: {e_est}"; confidence = 0.1

    # Final status check
    if primary_result["error"]: reflection_status = "Failure"

    return {**primary_result, "reflection": _create_reflection(reflection_status, summary, confidence, alignment, issues, preview)}

def _run_granger_causality(**kwargs) -> Dict[str, Any]:
    """[Implemented] Runs Granger causality tests using statsmodels."""
    # --- Initialize ---
    primary_result = {"granger_results": None, "error": None}
    reflection_status = "Failure"; summary = "Granger causality init failed."; confidence = 0.0; alignment = "N/A"; issues = []; preview = None

    if not STATSMODELS_AVAILABLE:
        primary_result["error"] = "Statsmodels library not available for Granger causality."
        return {**primary_result, "reflection": _create_reflection(reflection_status, summary, confidence, alignment, [primary_result["error"]], None)}

    try:
        # --- Extract & Validate Parameters ---
        data_input = kwargs.get("data")
        target_column = kwargs.get("target_column")
        regressor_columns = kwargs.get("regressor_columns")
        max_lag = int(kwargs.get("max_lag", 5))
        test_to_run = kwargs.get("test", 'ssr_chi2test') # Default test

        if data_input is None: raise ValueError("Missing 'data' input.")
        if not target_column: raise ValueError("Missing 'target_column' name.")
        if not regressor_columns or not isinstance(regressor_columns, list): raise ValueError("Missing or invalid 'regressor_columns' list.")
        if max_lag <= 0: raise ValueError("'max_lag' must be a positive integer.")

        # Prepare data
        df, prep_error = _prepare_causal_data(data_input)
        if prep_error: raise ValueError(f"Data preparation failed: {prep_error}")
        if df is None: raise ValueError("Data preparation returned None.")

        columns_to_use = [target_column] + regressor_columns
        missing_cols = [c for c in columns_to_use if c not in df.columns]
        if missing_cols: raise ValueError(f"Missing columns in data: {missing_cols}")

        # Select and prepare data subset for the test
        data_subset = df[columns_to_use].dropna() # Drop rows with NaNs in relevant columns
        if len(data_subset) < max_lag + 3: # Check if enough data points remain
            raise ValueError(f"Insufficient non-NaN data points ({len(data_subset)}) for Granger causality test with max_lag={max_lag}.")

        # --- Run Granger Causality Test ---
        logger.info(f"Running Granger Causality for target '{target_column}', regressors {regressor_columns}, max_lag={max_lag}, test='{test_to_run}'...")
        # grangercausalitytests expects columns in order [endog, exog]
        # We test if regressors Granger-cause the target
        test_result_dict = grangercausalitytests(data_subset[[target_column] + regressor_columns], [max_lag], verbose=False)

        # Process results into a more serializable format
        processed_results = {}
        if test_result_dict and max_lag in test_result_dict:
            lag_results = test_result_dict[max_lag][0] # Get dict for the specified lag
            processed_results[f"lag_{max_lag}"] = {}
            for test_name, values in lag_results.items():
                # Store test statistic, p-value, degrees of freedom
                processed_results[f"lag_{max_lag}"][test_name] = {
                    "statistic": float(values[0]) if values[0] is not None else None,
                    "p_value": float(values[1]) if values[1] is not None else None,
                    "df_num": int(values[2]) if values[2] is not None else None,
                    "df_denom": int(values[3]) if values[3] is not None else None
                }
            primary_result["granger_results"] = processed_results
            reflection_status = "Success"
            summary = f"Granger causality tests completed up to lag {max_lag}."
            # Confidence depends on p-values, but base it on successful execution
            confidence = 0.8
            alignment = "Aligned with testing predictive causality."
            issues = ["Granger causality only indicates predictive power, not true causation.", "Assumes stationarity."]
            preview = processed_results # Preview the results dict
        else:
            raise ValueError("Granger causality test did not return expected results structure.")

    except (ValueError, TypeError, ImportError) as e_val:
        primary_result["error"] = f"Input/Validation/Import Error: {e_val}"
        issues = [str(e_val)]; summary = f"Granger test failed: {e_val}"; confidence = 0.0
    except Exception as e_granger: # Catch statsmodels or other errors
        primary_result["error"] = f"Granger causality test failed: {e_granger}"
        logger.error(f"Error during Granger causality test: {e_granger}", exc_info=True)
        issues = [f"Statsmodels Error: {e_granger}"]; summary = f"Granger test failed: {e_granger}"; confidence = 0.1

    # Final status check
    if primary_result["error"]: reflection_status = "Failure"

    return {**primary_result, "reflection": _create_reflection(reflection_status, summary, confidence, alignment, issues, preview)}

def _estimate_lagged_effects(**kwargs) -> Dict[str, Any]:
    """[Implemented] Estimates lagged effects using statsmodels VAR."""
    # --- Initialize ---
    primary_result = {"lagged_effects": None, "error": None}
    reflection_status = "Failure"; summary = "Lagged effects estimation init failed."; confidence = 0.0; alignment = "N/A"; issues = []; preview = None

    if not STATSMODELS_AVAILABLE:
        primary_result["error"] = "Statsmodels library not available for VAR model."
        return {**primary_result, "reflection": _create_reflection(reflection_status, summary, confidence, alignment, [primary_result["error"]], None)}

    try:
        # --- Extract & Validate Parameters ---
        data_input = kwargs.get("data")
        target_column = kwargs.get("target_column") # Can be None if analyzing all variables
        regressor_columns = kwargs.get("regressor_columns") # Can be None
        max_lag = int(kwargs.get("max_lag", 5))

        if data_input is None: raise ValueError("Missing 'data' input.")
        if max_lag <= 0: raise ValueError("'max_lag' must be a positive integer.")

        # Prepare data
        df, prep_error = _prepare_causal_data(data_input)
        if prep_error: raise ValueError(f"Data preparation failed: {prep_error}")
        if df is None: raise ValueError("Data preparation returned None.")

        # Select columns for VAR model
        if target_column and regressor_columns:
            columns_for_var = [target_column] + regressor_columns
        elif target_column:
            columns_for_var = [target_column] + [c for c in df.columns if c != target_column] # Use all others as regressors
        elif regressor_columns:
            columns_for_var = regressor_columns + [c for c in df.columns if c not in regressor_columns] # Use all others as targets
        else: # Use all columns if none specified
            columns_for_var = df.columns.tolist()

        missing_cols = [c for c in columns_for_var if c not in df.columns]
        if missing_cols: raise ValueError(f"Missing columns in data for VAR: {missing_cols}")

        data_subset = df[columns_for_var].dropna() # Drop rows with NaNs
        if len(data_subset) < max_lag + 5: # Check if enough data points remain
            raise ValueError(f"Insufficient non-NaN data points ({len(data_subset)}) for VAR model with max_lag={max_lag}.")

        # --- Fit VAR Model ---
        logger.info(f"Fitting VAR model with max_lag={max_lag} for columns: {columns_for_var}...")
        model = VAR(data_subset)
        var_results = model.fit(maxlags=max_lag)

        # --- Process Results ---
        effects_summary = {}
        # Convert coefficient matrices (numpy arrays) to nested dicts for JSON
        coeffs_dict = {}
        if var_results.params is not None:
            coeffs_df = var_results.params # DataFrame of coefficients
            # Iterate through equations (target variables)
            for target_var in coeffs_df.index:
                 coeffs_dict[target_var] = coeffs_df.loc[target_var].to_dict()
        effects_summary['coefficients'] = coeffs_dict
        effects_summary['summary_text'] = var_results.summary().as_text() # Get text summary
        # Optionally extract impulse response functions (IRFs), forecast error variance decomposition (FEVD)
        # irf = var_results.irf(periods=10) # Example IRF
        # fevd = var_results.fevd(periods=10) # Example FEVD
        # effects_summary['irf'] = ... # Process IRF output
        # effects_summary['fevd'] = ... # Process FEVD output

        primary_result["lagged_effects"] = effects_summary
        reflection_status = "Success"
        summary = f"VAR model (max_lag={max_lag}) fitted successfully."
        confidence = 0.75 # Confidence based on successful fit, but VAR has assumptions
        alignment = "Aligned with estimating lagged interdependencies."
        issues = ["VAR model assumes linearity and stationarity.", "Interpretation requires care."]
        preview = effects_summary.get('coefficients', {}).get(columns_for_var[0], {}) # Preview coefficients for first variable

    except (ValueError, TypeError, ImportError) as e_val:
        primary_result["error"] = f"Input/Validation/Import Error: {e_val}"
        issues = [str(e_val)]; summary = f"VAR estimation failed: {e_val}"; confidence = 0.0
    except Exception as e_var: # Catch statsmodels or other errors
        primary_result["error"] = f"VAR model estimation failed: {e_var}"
        logger.error(f"Error during VAR estimation: {e_var}", exc_info=True)
        issues = [f"Statsmodels Error: {e_var}"]; summary = f"VAR estimation failed: {e_var}"; confidence = 0.1

    # Final status check
    if primary_result["error"]: reflection_status = "Failure"

    return {**primary_result, "reflection": _create_reflection(reflection_status, summary, confidence, alignment, issues, preview)}

def _discover_temporal_graph(**kwargs) -> Dict[str, Any]:
    """[Conceptual/Simulated] Discovers temporal causal graph structure."""
    # Requires implementation using libraries like Tigramite, causal-learn (temporal variants)
    data = kwargs.get("data")
    max_lag = int(kwargs.get("max_lag", 5))
    method = kwargs.get('method', config.CAUSAL_DEFAULT_TEMPORAL_METHOD)
    alpha = float(kwargs.get('alpha', 0.05))
    logger.warning(f"Actual temporal graph discovery ('discover_temporal_graph' using {method}) not implemented. Returning simulated graph.")
    sim_result = _simulate_causal_inference('discover_temporal_graph', data=data, max_lag=max_lag, method=method, alpha=alpha)
    issues = ["Temporal graph discovery is simulated.", "Actual implementation required using appropriate libraries (e.g., Tigramite)."]
    confidence = 0.2 # Low confidence for simulation
    summary = f"Simulated temporal graph discovery using method '{method}'."
    status = "Success" if sim_result.get("error") is None else "Failure"
    if sim_result.get("error"): issues.append(sim_result["error"])
    return {**sim_result, "reflection": _create_reflection(status, summary, confidence, "Aligned (Simulated)", issues, sim_result.get('temporal_graph'))}

def _convert_causal_to_state(**kwargs) -> Dict[str, Any]:
    """[Implemented] Converts causal analysis results into a state vector."""
    # --- Initialize ---
    primary_result = {"state_vector": None, "representation_type": None, "dimensions": 0, "error": None}
    reflection_status = "Failure"; summary = "Causal state conversion init failed."; confidence = 0.0; alignment = "N/A"; issues = []; preview = None

    try:
        # --- Extract & Validate Parameters ---
        causal_result = kwargs.get('causal_result') # Expects the full dict from a previous step
        representation_type = kwargs.get('representation_type', 'effect_ci')
        primary_result["representation_type"] = representation_type

        if not causal_result or not isinstance(causal_result, dict):
            raise ValueError("Missing or invalid 'causal_result' dictionary input.")
        # Check if the input result itself indicates an error
        input_error = causal_result.get("error")
        if input_error: raise ValueError(f"Input causal result contains error: {input_error}")

        logger.info(f"Converting causal result to state vector (type: {representation_type})")
        state_vector = []; error_msg = None

        # --- Conversion Logic ---
        if representation_type == 'effect_ci':
            effect = causal_result.get('causal_effect')
            ci = causal_result.get('confidence_intervals')
            if effect is None or ci is None or not isinstance(ci, list) or len(ci) != 2:
                error_msg = "Missing 'causal_effect' or valid 'confidence_intervals' in causal_result for 'effect_ci' conversion."
            else: state_vector = [float(effect), float(ci[0]), float(ci[1])]
        elif representation_type == 'granger_p_values':
            gc_results_dict = causal_result.get('granger_results', {})
            # Extract p-values, handling potential nested structure
            p_values = []
            if gc_results_dict:
                # Assume structure like { 'lag_5': { 'ssr_chi2test': {'p_value': 0.01, ...}, ... } }
                for lag_key, lag_data in gc_results_dict.items():
                    if isinstance(lag_data, dict):
                        for test_key, test_data in lag_data.items():
                            if isinstance(test_data, dict) and 'p_value' in test_data:
                                p_values.append(float(test_data['p_value']) if test_data['p_value'] is not None else 1.0) # Use 1.0 for None p-value
            if not p_values: error_msg = "Could not extract Granger p-values from causal_result structure."
            else: state_vector = p_values
        elif representation_type == 'lagged_coefficients':
            lagged_effects = causal_result.get('lagged_effects', {}).get('coefficients', {})
            if not lagged_effects or not isinstance(lagged_effects, dict):
                 error_msg = "Missing or invalid 'lagged_effects.coefficients' in causal_result."
            else:
                # Flatten the coefficients into a single vector (order might matter)
                coeffs = []
                # Sort by target variable then lag variable for consistency
                for target_var in sorted(lagged_effects.keys()):
                    if isinstance(lagged_effects[target_var], dict):
                        for lag_var in sorted(lagged_effects[target_var].keys()):
                            coeffs.append(float(lagged_effects[target_var][lag_var]))
                if not coeffs: error_msg = "No coefficients found in lagged_effects structure."
                else: state_vector = coeffs
        # Add other representation types as needed
        else: error_msg = f"Unsupported representation_type for causal state conversion: {representation_type}"

        # --- Final Processing & Normalization ---
        if error_msg:
            primary_result["error"] = error_msg
            state_vector_final = np.array([0.0, 0.0]) # Default error state vector
        else:
            state_vector_final = np.array(state_vector, dtype=float)
            if state_vector_final.size == 0:
                logger.warning(f"Resulting state vector for type '{representation_type}' is empty. Using default error state.")
                state_vector_final = np.array([0.0, 0.0]) # Handle empty vector case

        # Normalize the final state vector (L2 norm) - optional, depends on CFP use case
        norm = np.linalg.norm(state_vector_final)
        if norm > 1e-15: state_vector_normalized = state_vector_final / norm
        else: logger.warning(f"State vector for type '{representation_type}' has zero norm. Not normalizing."); state_vector_normalized = state_vector_final

        state_vector_list = state_vector_normalized.tolist()
        dimensions = len(state_vector_list)
        primary_result.update({"state_vector": state_vector_list, "dimensions": dimensions})

        # --- Generate IAR ---
        if primary_result["error"]:
            reflection_status = "Failure"; summary = f"State conversion failed: {primary_result['error']}"; confidence = 0.1; issues = [primary_result["error"]]; alignment = "Failed to convert state."
        else:
            reflection_status = "Success"; summary = f"Causal results successfully converted to state vector (type: {representation_type}, dim: {dimensions})."; confidence = 0.9; alignment = "Aligned with preparing data for comparison/CFP."; issues = None; preview = state_vector_list

    except (ValueError, TypeError, ImportError) as e_val:
        primary_result["error"] = f"Input/Validation/Import Error: {e_val}"
        issues = [str(e_val)]; summary = f"State conversion failed: {e_val}"; confidence = 0.0
    except Exception as e_conv:
        primary_result["error"] = f"Unexpected state conversion error: {e_conv}"
        logger.error(f"Unexpected error converting causal results to state vector: {e_conv}", exc_info=True)
        issues = [f"Unexpected Error: {e_conv}"]; summary = f"State conversion failed unexpectedly: {e_conv}"; confidence = 0.0
        # Ensure default state vector is set on critical error
        if primary_result.get("state_vector") is None: primary_result["state_vector"] = [0.0, 0.0]; primary_result["dimensions"] = 2

    # Final status check
    if primary_result["error"]: reflection_status = "Failure"

    return {**primary_result, "reflection": _create_reflection(reflection_status, summary, confidence, alignment, issues, preview)}

# --- Internal Simulation Function ---
def _simulate_causal_inference(operation: str, **kwargs) -> Dict[str, Any]:
    """Simulates causal inference results when libraries are unavailable."""
    # (Code identical to v2.9.5, potentially add simulation for temporal ops)
    logger.debug(f"Simulating causal operation '{operation}' with kwargs: {kwargs}")
    result = {"error": None}
    np.random.seed(int(time.time()) % 1000 + 1) # Seed for reproducibility within a short time
    data = kwargs.get("data")

    if operation == 'discover_graph':
        nodes = ['x', 'y', 'z', 'w'] # Default nodes
        if isinstance(data, dict): nodes = [str(k) for k in data.keys()]
        elif isinstance(data, pd.DataFrame): nodes = data.columns.tolist()
        sim_edges = []
        if len(nodes) > 1: sim_edges = [[nodes[i], nodes[i+1]] for i in range(len(nodes)-1)] # Simple chain
        if len(nodes) > 2: sim_edges.append([nodes[0], nodes[-1]]) # Add cycle for complexity
        result['graph'] = {'nodes': nodes, 'directed_edges': sim_edges, 'method': kwargs.get('method','simulated')}

    elif operation == 'estimate_effect':
        treatment = kwargs.get('treatment', 'x'); outcome = kwargs.get('outcome', 'y'); confounders = kwargs.get('confounders', ['z'])
        sim_effect = np.random.normal(0.5, 0.2); sim_ci = sorted([sim_effect + np.random.normal(0, 0.1), sim_effect + np.random.normal(0, 0.1)])
        result.update({
            'causal_effect': float(sim_effect),
            'confidence_intervals': [float(sim_ci[0]), float(sim_ci[1])],
            'estimand': f"Simulated E[{outcome}|do({treatment})] controlling for {confounders}",
            'refutations': [{'type': 'sim_random_common_cause', 'result': 'passed (simulated)'}, {'type':'sim_placebo_treatment','result':'passed (simulated)'}],
            'p_value': float(np.random.uniform(0.0001, 0.04)) # Simulate significance
        })

    elif operation == 'run_granger_causality':
        target = kwargs.get('target_column', 'y'); regressors = kwargs.get('regressor_columns', ['x','z']); max_lag = int(kwargs.get('max_lag', 5))
        test = kwargs.get('test', 'ssr_chi2test')
        sim_granger = {
            r: { test: (np.random.uniform(1, 10), np.random.uniform(0.001, 0.15), max_lag, 100 - max_lag) } # (F-stat/Chi2, p-value, df_num, df_denom)
            for r in regressors
        }
        result['granger_results'] = {max_lag: (sim_granger,)} # Match statsmodels structure loosely

    elif operation == 'estimate_lagged_effects':
        target = kwargs.get('target_column', 'y'); regressors = kwargs.get('regressor_columns', ['x','z']); max_lag = int(kwargs.get('max_lag', 5))
        effects = {}
        for r in regressors:
            effects[r] = {f'L{i}.{target}': np.random.normal(0, 0.2) for i in range(1, max_lag + 1)}
        result['lagged_effects'] = {'coefficients': effects, 'summary': f'Simulated lagged effects up to {max_lag}'}

    elif operation == 'discover_temporal_graph':
        nodes = ['x', 'y', 'z']; max_lag = int(kwargs.get('max_lag', 5))
        if isinstance(data, dict): nodes = [str(k) for k in data.keys() if k != 'timestamp']
        elif isinstance(data, pd.DataFrame): nodes = [c for c in data.columns if c != 'timestamp']
        links = []
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i == j: continue # No self-loops usually
                for lag in range(1, max_lag + 1):
                        if np.random.rand() < 0.15: # Sparsity
                            links.append(f"{nodes[i]}(t-{lag}) -> {nodes[j]}(t)")
        result['temporal_graph'] = {'nodes': nodes, 'links': links, 'max_lag': max_lag, 'method': kwargs.get('method','simulated')}

    elif operation == 'convert_to_state':
        causal_result = kwargs.get('causal_result', {}); representation_type = kwargs.get('representation_type', 'effect_ci')
        state_vector = [0.0, 0.0]; dimensions = 2 # Default error state
        if representation_type == 'effect_ci':
            effect = causal_result.get('causal_effect', 0.5)
            ci = causal_result.get('confidence_intervals', [effect - 0.1, effect + 0.1])
            if isinstance(ci, list) and len(ci) == 2: state_vector = [effect, ci[0], ci[1]]
        elif representation_type == 'granger_p_values':
            gc_results = causal_result.get('granger_results', {}).get(kwargs.get('max_lag',5),(None,))[0] # Example access
            if gc_results: state_vector = [details[kwargs.get('test', 'ssr_chi2test')][1] for details in gc_results.values()] # Get p-values
            if not state_vector: state_vector = [1.0, 1.0] # Default if extraction fails
        elif representation_type == 'lagged_coefficients':
             lagged_effects = causal_result.get('lagged_effects', {}).get('coefficients', {})
             coeffs = []
             if lagged_effects:
                 for target_var in sorted(lagged_effects.keys()):
                     if isinstance(lagged_effects[target_var], dict):
                         for lag_var in sorted(lagged_effects[target_var].keys()):
                             coeffs.append(float(lagged_effects[target_var][lag_var]))
             if not coeffs: state_vector = [0.0, 0.0]
             else: state_vector = coeffs
        # Normalize
        state_array = np.array(state_vector, dtype=float); norm = np.linalg.norm(state_array)
        state_vector_list = (state_array / norm).tolist() if norm > 1e-15 else state_array.tolist()
        dimensions = len(state_vector_list)
        result.update({"state_vector": state_vector_list, "dimensions": dimensions, "representation_type": representation_type})

    else:
        result["error"] = f"Unknown or unimplemented simulated operation: {operation}"

    return result

# --- END OF FILE 3.0ArchE/causal_inference_tool.py ---