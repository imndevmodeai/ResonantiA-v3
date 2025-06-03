# --- START OF FILE 3.0ArchE/causal_inference_tool.py ---
# ResonantiA Protocol v3.0 - causal_inference_tool.py
# Implements Causal Inference capabilities with Temporal focus (Conceptual/Simulated).
# Requires integration with libraries like DoWhy, statsmodels, Tigramite, causal-learn.
# Returns results including mandatory Integrated Action Reflection (IAR).

import json
import logging
import pandas as pd
import numpy as np
import time
import networkx as nx # For graph representation if needed
from typing import Dict, Any, Optional, List, Union, Tuple # Expanded type hints
import re
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
        if df.select_dtypes(include=[object]).shape[1] > 0: # Corrected to check number of object columns
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
    libs_needed_for_operation = (needs_dowhy and not DOWHY_AVAILABLE) or (needs_statsmodels and not STATSMODELS_AVAILABLE)

    # Graph discovery is always simulated for now, or if libs are missing for it
    is_simulated_op = operation in ['discover_graph', 'discover_temporal_graph'] or libs_needed_for_operation

    if is_simulated_op:
        missing_libs_names = []
        if needs_dowhy and not DOWHY_AVAILABLE: missing_libs_names.append("DoWhy")
        if needs_statsmodels and not STATSMODELS_AVAILABLE: missing_libs_names.append("statsmodels")
        libs_str = ", ".join(missing_libs_names) if missing_libs_names else "N/A (operation simulated by design)"
        sim_reason = f"Missing libs: {libs_str}" if libs_needed_for_operation else "Operation simulated by design"
        logger.warning(f"Simulating causal inference operation '{operation}'. Reason: {sim_reason}.")
        primary_result["note"] = f"SIMULATED result ({sim_reason})"
        sim_result = _simulate_causal_inference(operation, **kwargs)
        primary_result.update(sim_result)
        primary_result["error"] = sim_result.get("error", primary_result.get("error"))
        if primary_result["error"]:
            reflection_status = "Failure"; reflection_summary = f"Simulated causal op '{operation}' failed: {primary_result['error']}"; confidence = 0.1; issues = [primary_result['error']]
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
        elif operation == 'convert_to_state': # Added for consistency with predictive tool
            op_result = _convert_to_state_vector(**kwargs)
        else:
            # This case should ideally be caught by simulation check, but as a safeguard:
            primary_result["error"] = f"Unsupported or unsimulated causal operation: {operation}"

        # --- Update primary_result and IAR from operation function --- 
        primary_result.update(op_result) # Merge results from the specific function
        # The specific operation function is responsible for setting its own IAR fields
        # So we extract them from op_result if present
        if "reflection" in op_result:
            reflection_data = op_result.pop("reflection") # Remove it from op_result to avoid nesting
            reflection_status = reflection_data.get("status", reflection_status)
            reflection_summary = reflection_data.get("summary", reflection_summary)
            confidence = reflection_data.get("confidence", confidence)
            alignment = reflection_data.get("alignment_check", alignment)
            issues = reflection_data.get("potential_issues", issues)
            preview = reflection_data.get("raw_output_preview", preview)
        else: # If no reflection provided by sub-function, create a basic one
            if primary_result.get("error"):
                reflection_status = "Failure"
                reflection_summary = f"Causal op '{operation}' failed: {primary_result['error']}"
                confidence = 0.1
                issues = [primary_result['error']]
            else:
                reflection_status = "Success"
                reflection_summary = f"Causal op '{operation}' completed."
                confidence = 0.7 # Default confidence if not specified by op_result
                alignment = "Aligned with causal analysis goal."
                preview = {k:v for k,v in primary_result.items() if k not in ['operation_performed','error','libs_available','note']}

    except Exception as e_main:
        logger.error(f"Error executing causal operation '{operation}': {e_main}", exc_info=True)
        primary_result["error"] = f"Causal operation execution error: {e_main}"
        reflection_status = "Failure"; reflection_summary = f"Causal op '{operation}' failed: {e_main}"; confidence = 0.0; alignment = "Failed due to system error."; issues = [f"System Error: {e_main}"]

    # --- Final Return --- 
    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, confidence, alignment, issues, preview)}


# --- Specific Causal Operation Implementations ---

def _estimate_effect(**kwargs) -> Dict[str, Any]:
    """[IAR Enabled] Estimates causal effect using DoWhy."""
    result: Dict[str, Any] = {"error": None}
    status = "Failure"; summary = "DoWhy estimation init failed."; confidence = 0.0; alignment = "N/A"; issues = ["Initialization error."]; preview = None

    if not DOWHY_AVAILABLE:
        result["error"] = "DoWhy library not available for effect estimation."
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    # --- Input Extraction & Validation ---
    data = kwargs.get("data")
    treatment_name = kwargs.get("treatment")
    outcome_name = kwargs.get("outcome")
    graph_dot_str = kwargs.get("graph") # DOT string format
    confounder_names = kwargs.get("confounders", []) # List of confounder column names
    estimation_method = kwargs.get("method", getattr(config, 'CAUSAL_DEFAULT_ESTIMATION_METHOD', "backdoor.linear_regression"))

    df, prep_error = _prepare_causal_data(data)
    if prep_error or df is None:
        result["error"] = f"Data preparation error: {prep_error}"
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    if not treatment_name or treatment_name not in df.columns:
        result["error"] = f"Treatment '{treatment_name}' not found in data columns."
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}
    if not outcome_name or outcome_name not in df.columns:
        result["error"] = f"Outcome '{outcome_name}' not found in data columns."
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}
    missing_confounders = [c for c in confounder_names if c not in df.columns]
    if missing_confounders:
        result["error"] = f"Confounder(s) not found in data: {missing_confounders}"
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    # --- DoWhy Estimation --- 
    try:
        model_args = {"data": df, "treatment": treatment_name, "outcome": outcome_name}
        if graph_dot_str:
            model_args["graph"] = graph_dot_str
            logger.info(f"Using provided causal graph for DoWhy model.")
        elif confounder_names:
            model_args["common_causes"] = confounder_names
            logger.info(f"Using provided common_causes (confounders) for DoWhy model as no graph was given.")
        else:
            logger.warning("No causal graph or explicit confounders provided for DoWhy. Estimation might be biased if unobserved confounders exist.")
            issues.append("Warning: No graph or confounders specified; results may be biased.")

        model = CausalModel(**model_args)
        
        identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
        logger.info(f"DoWhy identified estimand object: {identified_estimand}")
        logger.info(f"DoWhy identified_estimand attributes: {dir(identified_estimand)}")

        estimate = model.estimate_effect(
            identified_estimand,
            method_name=estimation_method,
            test_significance=True,
            confidence_intervals=True
        )
        logger.debug(f"DoWhy estimate object: {estimate}")
        logger.debug(f"dir(estimate): {dir(estimate)}") # Log attributes of estimate object
        
        # Attempt to get p-value from test_stat_significance
        p_val = None
        if hasattr(estimate, "test_stat_significance"):
            sig_results = estimate.test_stat_significance
            logger.debug(f"estimate.test_stat_significance: {sig_results} (type: {type(sig_results)})")
            if isinstance(sig_results, dict) and "p_value" in sig_results:
                try:
                    p_val_raw = sig_results["p_value"]
                    # p_value might be an array/list or a scalar
                    if isinstance(p_val_raw, (list, np.ndarray)) and len(p_val_raw) > 0:
                        p_val = float(p_val_raw[0])
                    elif isinstance(p_val_raw, (float, int)):
                        p_val = float(p_val_raw)
                    logger.debug(f"P-value from test_stat_significance: {p_val}")
                except (TypeError, ValueError, IndexError) as e:
                    logger.warning(f"Could not extract/convert p-value from test_stat_significance: {e}")
        else:
            logger.debug("estimate has no attribute 'test_stat_significance'")

        # Fallback: Parse from string representation if p_val is still None
        if p_val is None:
            logger.debug("P-value not found via test_stat_significance, trying to parse from str(estimate).")
            try:
                estimate_str = str(estimate)
                match = re.search(r"p-value: \s*\[?([0-9\.eE\-]+)\s*\]?", estimate_str) # handle optional brackets
                if match:
                    p_val_str = match.group(1)
                    p_val = float(p_val_str)
                    logger.info(f"Successfully parsed p-value ({p_val}) from string representation of estimate object.")
                else:
                    logger.warning(f"Could not find p-value pattern in str(estimate): {estimate_str[:500]}") # Log part of string if pattern fails
            except Exception as e_parse:
                logger.warning(f"Failed to parse p-value from string representation: {e_parse}")

        result["p_value"] = p_val
        logger.debug(f"Final p_value set in result: {result['p_value']}")
        
        result["estimated_effect"] = estimate.value
        result["estimand_type"] = identified_estimand.estimand_type.name
        
        estimand_str = "N/A"
        if hasattr(identified_estimand, 'estimands') and 'backdoor' in identified_estimand.estimands and identified_estimand.estimands['backdoor']:
            if isinstance(identified_estimand.estimands['backdoor'], dict) and 'estimand' in identified_estimand.estimands['backdoor']:
                estimand_str = str(identified_estimand.estimands['backdoor']['estimand'])
            elif hasattr(identified_estimand.estimands['backdoor'], 'estimand_expression'):
                 estimand_str = str(identified_estimand.estimands['backdoor'].estimand_expression)
            else:
                estimand_str = str(identified_estimand.estimands['backdoor'])
        elif hasattr(identified_estimand, 'estimand_expression'):
             estimand_str = str(identified_estimand.estimand_expression)
        else:
            estimand_str = str(identified_estimand)
            if "Estimand expression:" in estimand_str:
                try:
                    estimand_str = estimand_str.split("Estimand expression:")[1].split("\\n\\n")[0].strip()
                except IndexError:
                    pass 
        result["estimand_expression"] = estimand_str

        result["method_used"] = estimation_method
        if hasattr(estimate, 'params'):
            try: result["estimator_params"] = json.loads(json.dumps(estimate.params, default=str))
            except: result["estimator_params"] = str(estimate.params)
        if hasattr(estimate, 'control_value'): result["control_value"] = estimate.control_value
        if hasattr(estimate, 'treatment_value'): result["treatment_value"] = estimate.treatment_value
        
        # Corrected confounder logic
        confounders_used_set = set()
        if hasattr(identified_estimand, 'backdoor_variables') and identified_estimand.backdoor_variables:
            bv = identified_estimand.backdoor_variables
            logger.debug(f"Raw identified_estimand.backdoor_variables: {bv} (type: {type(bv)})")
            if isinstance(bv, dict):
                for val_list in bv.values():
                    if isinstance(val_list, list):
                        for item in val_list:
                            confounders_used_set.add(str(item))
                    else:
                        confounders_used_set.add(str(val_list))
            elif isinstance(bv, list):
                for item in bv:
                    if isinstance(item, (list, tuple)):
                        confounders_used_set.update([str(i) for i in item])
                    else:
                        confounders_used_set.add(str(item))
            else:
                 confounders_used_set.add(str(bv))
        elif hasattr(identified_estimand, 'common_causes') and identified_estimand.common_causes: # Fallback
            cc_vars = identified_estimand.common_causes
            logger.debug(f"Raw identified_estimand.common_causes: {cc_vars} (type: {type(cc_vars)})")
            confounders_used_set.update([str(cc) for cc in cc_vars])
        result["confounders_identified_used"] = sorted(list(confounders_used_set))
        logger.debug(f"Processed confounders_identified_used: {result['confounders_identified_used']}")

        result["assumptions"] = str(identified_estimand.assumptions) if hasattr(identified_estimand, 'assumptions') else "N/A"
        
        result["confidence_intervals"] = estimate.confidence_interval if hasattr(estimate, "confidence_interval") else None
        
        status = "Success"
        summary = f"DoWhy causal effect estimation completed for {treatment_name} -> {outcome_name}."
        confidence = 0.75 
        if p_val is not None and p_val > 0.05: confidence = max(0.3, confidence - 0.2)
        alignment = "Aligned with causal effect estimation goal."
        preview = {"estimated_effect": result["estimated_effect"], "p_value": result.get("p_value")} 

    except Exception as e_dowhy:
        logger.error(f"DoWhy effect estimation failed: {e_dowhy}", exc_info=True)
        result["error"] = f"DoWhy estimation error: {e_dowhy}"
        status = "Failure"; summary = result["error"]; confidence = 0.1; issues.append(result["error"])

    return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}


def _run_granger_causality(**kwargs) -> Dict[str, Any]:
    """[IAR Enabled] Performs Granger causality tests between time series columns."""
    result: Dict[str, Any] = {"error": None, "granger_results": {}}
    status = "Failure"; summary = "Granger causality init failed."; confidence = 0.0; alignment = "N/A"; issues = ["Initialization error."]; preview = None

    if not STATSMODELS_AVAILABLE:
        result["error"] = "Statsmodels library not available for Granger causality."
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    # --- Input Extraction & Validation ---
    data = kwargs.get("data")
    max_lag = kwargs.get("max_lag", 5) # Default max lag
    # target_column: The variable whose causes are being investigated (Y in X -> Y)
    target_column = kwargs.get("target_column")
    # predictor_columns: List of variables to test as potential causes of target_column (X_i in X_i -> Y)
    # If None, test all other numeric columns against target_column.
    predictor_columns = kwargs.get("predictor_columns")
    significance_level = kwargs.get("significance_level", 0.05) # Default alpha
    # Test types: 'ssr_chi2test', 'ssr_ftest', 'lrtest', 'params_ftest'
    # Default to F-test which is common
    granger_test_type = kwargs.get("test_type", "ssr_ftest")

    df, prep_error = _prepare_causal_data(data)
    if prep_error or df is None:
        result["error"] = f"Data preparation error: {prep_error}"
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    try: max_lag = int(max_lag); assert max_lag > 0
    except: max_lag = 5; logger.warning(f"Invalid max_lag, defaulting to {max_lag}.")

    if not target_column or target_column not in df.columns:
        result["error"] = f"Target column '{target_column}' not found in data."
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    # Ensure target column is numeric
    if not pd.api.types.is_numeric_dtype(df[target_column]):
        result["error"] = f"Target column '{target_column}' must be numeric for Granger causality."
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    # Determine predictor columns
    if predictor_columns is None:
        # Use all other numeric columns as potential predictors
        predictor_columns = [col for col in df.columns if col != target_column and pd.api.types.is_numeric_dtype(df[col])]
        if not predictor_columns:
            result["error"] = "No suitable numeric predictor columns found in data (excluding target)."
            issues = [result["error"]]; summary = result["error"]
            return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}
    else:
        # Validate provided predictor columns
        missing_preds = [p for p in predictor_columns if p not in df.columns]
        if missing_preds: result["error"] = f"Predictor column(s) not found: {missing_preds}"; issues = [result["error"]]; summary = result["error"]
        non_numeric_preds = [p for p in predictor_columns if p in df.columns and not pd.api.types.is_numeric_dtype(df[p])]
        if non_numeric_preds: result["error"] = f"Predictor column(s) must be numeric: {non_numeric_preds}"; issues = [result["error"]]; summary = result["error"]
        if result["error"]: return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    # --- Perform Granger Causality Tests --- 
    test_results_dict: Dict[str, Any] = {}
    any_significant = False
    # Ensure the specific exception is importable or defined
    try:
        from statsmodels.tools.sm_exceptions import InfeasibleTestError
    except ImportError:
        # Define a placeholder if not importable, so `except` block doesn't fail
        class InfeasibleTestError(Exception):
            pass

    try:
        for pred_col in predictor_columns:
            if pred_col == target_column: continue # Skip testing column against itself

            logger.info(f"Running Granger causality: '{pred_col}' -> '{target_column}' (max_lag={max_lag}) Session ID: {getattr(config, 'SESSION_ID', 'N/A')[:8]}")
            pair_df = df[[target_column, pred_col]].dropna()
            if len(pair_df) < max_lag + 5: # Heuristic: Need enough data points relative to lag
                logger.warning(f"Skipping Granger test for {pred_col} -> {target_column} due to insufficient data after dropna (len={len(pair_df)}, max_lag={max_lag}).")
                test_results_dict[f"{pred_col}_to_{target_column}"] = {"skipped": True, "reason": "Insufficient data after dropna for max_lag.", "p_value": None, "is_significant": False, "error": None}
                continue

            p_value = None
            current_pair_error = None
            lag_results_dict = {} # Initialize here
            try:
                granger_test_output = grangercausalitytests(pair_df[[target_column, pred_col]], maxlag=[max_lag], verbose=False)
                if max_lag in granger_test_output and len(granger_test_output[max_lag]) > 0:
                    lag_results_dict = granger_test_output[max_lag][0]
                    if granger_test_type in lag_results_dict:
                        p_value = lag_results_dict[granger_test_type][1]
                    else:
                        logger.warning(f"Chosen Granger test_type '{granger_test_type}' not found in results for {pred_col} -> {target_column} at lag {max_lag}. Trying F-test.")
                        if "ssr_ftest" in lag_results_dict:
                            p_value = lag_results_dict["ssr_ftest"][1]
            except InfeasibleTestError as e_infeasible:
                logger.warning(f"Granger test infeasible for {pred_col} -> {target_column}: {e_infeasible}")
                current_pair_error = f"InfeasibleTestError: {e_infeasible}"
            except Exception as e_pair_test:
                logger.error(f"Error during Granger test for {pred_col} -> {target_column}: {e_pair_test}", exc_info=True)
                current_pair_error = str(e_pair_test)

            is_significant = p_value is not None and p_value < significance_level
            if is_significant: any_significant = True

            test_results_dict[f"{pred_col}_to_{target_column}"] = {
                "p_value": p_value,
                "is_significant_at_{significance_level}": is_significant,
                "max_lag_tested": max_lag,
                "test_type_used": granger_test_type if p_value is not None else ("ssr_ftest" if "ssr_ftest" in lag_results_dict and not current_pair_error else "N/A"),
                "error": current_pair_error
            }

        result["granger_results"] = test_results_dict
        status = "Success"
        summary = f"Granger causality tests completed for target '{target_column}'."
        confidence = 0.7 # Granger implies correlation, not deep causation. Requires assumptions.
        alignment = "Aligned with temporal causal influence detection goal."
        issues.append("Granger causality indicates temporal precedence, not true causal effect without strong assumptions (e.g., no unobserved confounders, correct lag). Stationarity of series is assumed.")
        if not any_significant: summary += " No significant Granger causes found at this lag/alpha."
        else: summary += " Significant Granger cause(s) identified."
        preview = test_results_dict

    except Exception as e_granger:
        logger.error(f"Granger causality test failed: {e_granger}", exc_info=True)
        result["error"] = f"Granger causality error: {e_granger}"
        status = "Failure"; summary = result["error"]; confidence = 0.1; issues.append(result["error"])

    return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}


def _estimate_lagged_effects(**kwargs) -> Dict[str, Any]:
    """[IAR Enabled] Estimates lagged effects using a Vector Autoregression (VAR) model."""
    result: Dict[str, Any] = {"error": None, "lagged_effects": {}, "var_model_summary": None, "optimal_lag": None}
    status = "Failure"; summary = "Lagged effects estimation init failed."; confidence = 0.0; alignment = "N/A"; issues = ["Initialization error."]; preview = None

    if not STATSMODELS_AVAILABLE:
        result["error"] = "Statsmodels library not available for VAR modeling."
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    # --- Input Extraction & Validation ---
    data = kwargs.get("data")
    # Columns to include in the VAR model. If None, use all numeric columns.
    var_columns = kwargs.get("columns")
    # Max lag for VAR model selection. If None, statsmodels might select it.
    max_lag_var = kwargs.get("max_lag") # Can be None for auto-selection
    # Information criterion for lag selection: 'aic', 'bic', 'hqic', 'fpe'
    lag_selection_criterion = kwargs.get("lag_criterion", "aic").lower()
    # Column for which to primarily report lagged effects (optional, for focus)
    focus_variable = kwargs.get("focus_variable")

    df, prep_error = _prepare_causal_data(data)
    if prep_error or df is None:
        result["error"] = f"Data preparation error: {prep_error}"
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    if var_columns is None:
        var_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        if len(var_columns) < 2:
            result["error"] = "VAR model requires at least two numeric columns. Found fewer after filtering."
            issues = [result["error"]]; summary = result["error"]
            return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}
    else:
        missing_cols = [c for c in var_columns if c not in df.columns]
        non_numeric_cols = [c for c in var_columns if c in df.columns and not pd.api.types.is_numeric_dtype(df[c])]
        if missing_cols: result["error"] = f"Column(s) for VAR not found: {missing_cols}"
        elif non_numeric_cols: result["error"] = f"Column(s) for VAR must be numeric: {non_numeric_cols}"
        if result["error"]:
            issues = [result["error"]]
            summary = result["error"] # Update summary with specific error
            # status, confidence, alignment, preview remain as initialized for failure
            return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    df_var = df[var_columns].dropna() # Use only selected columns and drop NaNs
    if len(df_var) < (max_lag_var if max_lag_var else 10) + 10: # Heuristic for sufficient data
        result["error"] = f"Insufficient data points (found {len(df_var)}) for VAR model with chosen columns and max_lag."
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    if focus_variable and focus_variable not in var_columns:
        logger.warning(f"Focus variable '{focus_variable}' not in VAR columns. Reporting for all.")
        focus_variable = None

    # --- Fit VAR Model and Extract Lagged Effects --- 
    try:
        var_model = VAR(df_var)
        # Fit the model. If max_lag_var is None, statsmodels selects based on ic.
        # Otherwise, it fits up to max_lag_var and then can select optimal.
        if max_lag_var is not None:
            var_results = var_model.fit(maxlags=max_lag_var, ic=lag_selection_criterion)
            optimal_lag_selected = var_results.k_ar # This is the lag order selected by the criterion
        else: # Let statsmodels decide the maxlags too
            var_results = var_model.fit(ic=lag_selection_criterion)
            optimal_lag_selected = var_results.k_ar

        result["var_model_summary"] = str(var_results.summary()) # Full model summary
        result["optimal_lag"] = optimal_lag_selected

        # Extract lagged coefficients (effects)
        # Coefficients are in var_results.params: DataFrame where index is lagged var, columns are equations for each var
        lagged_coefs = var_results.params
        lagged_effects_data: Dict[str, Dict[str, float]] = {}

        for lag in range(1, optimal_lag_selected + 1):
            lag_str = f"L{lag}"
            for caused_var in var_columns: # The variable being affected in the equation
                # Initialize dict for this caused_var if not present
                if caused_var not in lagged_effects_data: lagged_effects_data[caused_var] = {}

                for causing_var in var_columns: # The lagged variable acting as a predictor
                    coef_name = f"{lag_str}.{causing_var}" # e.g., L1.VarA
                    if coef_name in lagged_coefs.index: # Check if this lagged term exists in results
                        # The column in lagged_coefs is the equation for 'caused_var'
                        # The row index is the lagged term 'L<lag>.<causing_var>'
                        # So, lagged_coefs.loc[coef_name, caused_var] is coef of L<lag>.causing_var on caused_var
                        coef_value = lagged_coefs.loc[coef_name, caused_var]
                        lagged_effects_data[caused_var][f"{causing_var}_lag{lag}"] = round(coef_value, 6)

        result["lagged_effects"] = lagged_effects_data
        status = "Success"
        summary = f"VAR model fitted (optimal_lag={optimal_lag_selected}) and lagged effects extracted."
        confidence = 0.7 # VAR models make assumptions (stationarity, no omitted vars)
        alignment = "Aligned with temporal lagged effect estimation."
        issues.append("VAR model assumes stationarity of time series and no omitted variable bias. Interpret coefficients with caution.")
        # Preview focused effects if specified, else a general preview
        if focus_variable and focus_variable in lagged_effects_data:
            preview = {focus_variable: lagged_effects_data[focus_variable]}
        else:
            preview = {k: dict(list(v.items())[:2]) for k,v in list(lagged_effects_data.items())[:2]} # Preview first few

    except Exception as e_var:
        logger.error(f"VAR model fitting or effect extraction failed: {e_var}", exc_info=True)
        result["error"] = f"VAR model error: {e_var}"
        status = "Failure"; summary = result["error"]; confidence = 0.1; issues.append(result["error"])

    return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}


def _convert_to_state_vector(**kwargs) -> Dict[str, Any]:
    """[IAR Enabled] Converts causal inference results (e.g., graph, effects) into a structured state vector."""
    # This is a conceptual placeholder, similar to the predictive modeling tool's version.
    # Actual implementation would depend on the specific format of causal_result and desired state representation.
    result: Dict[str, Any] = {"error": None, "state_vector": None, "note": "Conceptual state conversion"}
    status = "Failure"; summary = "Causal state conversion init failed."; confidence = 0.0; alignment = "N/A"; issues = ["Initialization error."]; preview = None

    causal_result_input = kwargs.get("causal_result") # The output from a previous causal op
    if not causal_result_input or not isinstance(causal_result_input, dict):
        result["error"] = "Missing or invalid 'causal_result' (dict) input for state conversion."
        issues = [result["error"]]; summary = result["error"]
        return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

    try:
        # Example: Extract key features from a simulated discovery or estimation
        state_components = {}
        if "discovered_graph_dot" in causal_result_input:
            state_components["graph_complexity"] = len(causal_result_input["discovered_graph_dot"])
            state_components["has_graph"] = True
        if "estimated_effect" in causal_result_input:
            state_components["effect_magnitude"] = abs(causal_result_input["estimated_effect"])
            state_components["has_effect_estimate"] = True
        if "granger_results" in causal_result_input:
            sig_granger = sum(1 for v in causal_result_input["granger_results"].values() if isinstance(v, dict) and v.get("is_significant_at_0.05"))
            state_components["num_significant_granger"] = sig_granger
            state_components["has_granger"] = True
        if "lagged_effects" in causal_result_input and causal_result_input["lagged_effects"]:
            state_components["num_lagged_effect_sets"] = len(causal_result_input["lagged_effects"])
            state_components["has_lagged_effects"] = True

        if not state_components: # If no recognizable causal features found
            result["error"] = "No standard causal features found in input for state vector conversion."
            issues = [result["error"]]; summary = result["error"]
            return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}

        # Convert to a simple list/vector for this example
        # A more sophisticated approach might involve fixed-size embeddings or normalized feature vectors.
        # Order of keys matters for a consistent vector if just using values.
        ordered_keys = sorted(state_components.keys())
        vector = [float(state_components[k]) if isinstance(state_components[k], (int, float, bool)) else 0.0 for k in ordered_keys]
        result["state_vector"] = vector
        result["state_vector_keys"] = ordered_keys # For interpretability

        status = "Success"
        summary = "Causal results conceptually converted to state vector components."
        confidence = 0.6 # Confidence depends heavily on richness of input and conversion method
        alignment = "Aligned with state representation goal (conceptual)."
        issues = ["State vector conversion is conceptual; actual utility depends on downstream use."]
        preview = {"vector_preview": vector[:5], "num_components": len(vector)}

    except Exception as e_conv:
        logger.error(f"Causal state vector conversion failed: {e_conv}", exc_info=True)
        result["error"] = f"State conversion error: {e_conv}"
        status = "Failure"; summary = result["error"]; confidence = 0.1; issues.append(result["error"])

    return {**result, "reflection": _create_reflection(status, summary, confidence, alignment, issues, preview)}


# --- Simulation Function (for operations not fully implemented or when libs are missing) ---
def _simulate_causal_inference(operation: str, **kwargs) -> Dict[str, Any]:
    """Simulates causal inference operations, returning placeholder results."""
    logger.info(f"Simulating causal operation: '{operation}' with inputs: {list(kwargs.keys())}")
    result: Dict[str, Any] = {"error": None, "note": f"Simulated result for {operation}"}
    time.sleep(0.1) # Simulate computation time

    # Example: Simulate graph discovery (returns a placeholder DOT string)
    if operation == 'discover_graph':
        data = kwargs.get("data")
        df, _ = _prepare_causal_data(data) # Basic prep to get column names
        cols = list(df.columns) if df is not None else ['A', 'B', 'C']
        if len(cols) < 2: cols.extend(['X','Y'])
        # Simple chain graph for simulation
        result["discovered_graph_dot"] = f"digraph G {{ {cols[0]} -> {cols[1]}; {cols[1]} -> {cols[0] if len(cols) < 3 else cols[2]}; }}"
        result["method_used"] = getattr(config, 'CAUSAL_DEFAULT_DISCOVERY_METHOD', "SimulatedPC")
    elif operation == 'discover_temporal_graph':
        data = kwargs.get("data")
        df, _ = _prepare_causal_data(data) # Basic prep to get column names
        cols = list(df.columns) if df is not None else ['TVarA', 'TVarB', 'TVarC']
        if len(cols) < 2: cols.extend(['TVarX','TVarY'])
        result["discovered_temporal_graph_dot"] = f"digraph G {{ node [shape=box]; {cols[0]}(t-1) -> {cols[1]}(t); {cols[1]}(t-1) -> {cols[0] if len(cols) < 3 else cols[2]}(t); }}"
        result["method_used"] = "SimulatedTemporalDiscovery"
    # Simulate effect estimation if DoWhy is missing
    elif operation == 'estimate_effect' and not DOWHY_AVAILABLE:
        treatment = kwargs.get("treatment", "X")
        outcome = kwargs.get("outcome", "Y")
        result["estimated_effect"] = np.random.rand() * 2 - 1 # Random effect [-1, 1]
        result["estimand_type"] = "Nonparametric-ATE (Simulated)"
        result["p_value"] = np.random.rand() * 0.1 # Simulate a typically low p-value
        result["note"] += "; DoWhy library was unavailable."
    # Simulate Granger if statsmodels is missing
    elif operation == 'run_granger_causality' and not STATSMODELS_AVAILABLE:
        target = kwargs.get("target_column", "Y")
        preds = kwargs.get("predictor_columns", ["X1", "X2"])
        granger_sim_res = {}
        for p in preds:
            granger_sim_res[f"{p}_to_{target}"] = {"p_value": np.random.rand(), "is_significant_at_0.05": np.random.choice([True, False])}
        result["granger_results"] = granger_sim_res
        result["note"] += "; Statsmodels library was unavailable."
    # Simulate lagged effects if statsmodels is missing
    elif operation == 'estimate_lagged_effects' and not STATSMODELS_AVAILABLE:
        cols = kwargs.get("columns", ["VarA", "VarB"])
        lag_effects_sim = {}
        for c_caused in cols:
            lag_effects_sim[c_caused] = {}
            for c_causing in cols:
                lag_effects_sim[c_caused][f"{c_causing}_lag1"] = round(np.random.randn(), 4)
                lag_effects_sim[c_caused][f"{c_causing}_lag2"] = round(np.random.randn(), 4)
        result["lagged_effects"] = lag_effects_sim
        result["optimal_lag"] = 2
        result["note"] += "; Statsmodels library was unavailable."
    else:
        # Default simulation for unhandled or truly unimplemented ops (should be rare if dispatch is correct)
        result["output"] = f"Simulated output for {operation}"
        result["parameters_received"] = list(kwargs.keys())

    return result

# --- END OF FILE 3.0ArchE/causal_inference_tool.py --- 