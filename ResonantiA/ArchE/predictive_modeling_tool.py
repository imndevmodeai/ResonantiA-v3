# --- START OF FILE 3.0ArchE/predictive_modeling_tool.py ---
# ResonantiA Protocol v3.0 - predictive_modeling_tool.py
# Implements Predictive Modeling capabilities, focusing on Time Series Forecasting.
# Includes functional ARIMA implementation using statsmodels and joblib.
# Returns results including mandatory Integrated Action Reflection (IAR).

import json
import logging
import pandas as pd
import numpy as np
import time
import os
import uuid # For model IDs
from typing import Dict, Any, Optional, List, Union, Tuple # Expanded type hints
import io # For DataFrame info
# Use relative imports for configuration
try:
    from . import config
except ImportError:
    # Fallback config if running standalone or package structure differs
    class FallbackConfig: PREDICTIVE_DEFAULT_TIMESERIES_MODEL="ARIMA"; MODEL_SAVE_DIR='outputs/models'; PREDICTIVE_ARIMA_DEFAULT_ORDER=(1,1,1); PREDICTIVE_DEFAULT_EVAL_METRICS=["mean_absolute_error"]
    config = FallbackConfig(); logging.warning("config.py not found for predictive tool, using fallback configuration.")

# --- Import Predictive Libraries (Set flag based on success) ---
PREDICTIVE_LIBS_AVAILABLE = False
STATSMODELS_AVAILABLE = False
SKLEARN_AVAILABLE = False
JOBLIB_AVAILABLE = False
try:
    import statsmodels.api as sm # For ARIMA, VAR etc.
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.arima.model import ARIMAResultsWrapper
    from statsmodels.tsa.base.tsa_model import TimeSeriesModelResults # For type hinting fit results
    from statsmodels.tools.sm_exceptions import ConvergenceWarning, ValueWarning as StatsmodelsValueWarning # Specific warnings
    STATSMODELS_AVAILABLE = True
    from sklearn.model_selection import train_test_split # For evaluation
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score # Example metrics
    SKLEARN_AVAILABLE = True
    import joblib # For saving/loading trained models
    JOBLIB_AVAILABLE = True

    PREDICTIVE_LIBS_AVAILABLE = True # Set flag to True if all core libs loaded
    logging.getLogger(__name__).info("Actual predictive modeling libraries (statsmodels, sklearn, joblib) loaded successfully.")

except ImportError as e_imp:
    # Define dummy classes/exceptions if libraries are not available
    TimeSeriesModelResults = object # Dummy for type hinting
    ConvergenceWarning = Warning # Dummy
    StatsmodelsValueWarning = Warning # Dummy
    logging.getLogger(__name__).warning(f"Predictive libraries import failed: {e_imp}. Predictive Tool will run in SIMULATION MODE.")
except Exception as e_imp_other:
    TimeSeriesModelResults = object
    ConvergenceWarning = Warning
    StatsmodelsValueWarning = Warning
    logging.getLogger(__name__).error(f"Unexpected error importing predictive libraries: {e_imp_other}. Tool simulating.")

logger = logging.getLogger(__name__) # Logger for this module

# --- Model Persistence Setup ---
MODEL_SAVE_DIR = getattr(config, 'MODEL_SAVE_DIR', 'outputs/models')
os.makedirs(MODEL_SAVE_DIR, exist_ok=True) # Ensure directory exists

# --- IAR Helper Function ---
# (Reused for consistency)
def _create_reflection(status: str, summary: str, confidence: Optional[float], alignment: Optional[str], issues: Optional[List[str]], preview: Any) -> Dict[str, Any]:
    """Helper function to create the standardized IAR reflection dictionary."""
    if confidence is not None: confidence = max(0.0, min(1.0, confidence))
    issues_list = issues if issues and any(issues) else None # Ensure issues list is None if empty or contains only None/empty strings
    try:
        preview_str = json.dumps(preview, default=str) if isinstance(preview, (dict, list)) else str(preview)
        if preview_str and len(preview_str) > 150: preview_str = preview_str[:150] + "..."
    except Exception:
        try: preview_str = str(preview); preview_str = preview_str[:150] + "..." if len(preview_str) > 150 else preview_str
        except Exception: preview_str = "[Preview Error]"
    return {"status": status, "summary": summary, "confidence": confidence, "alignment_check": alignment if alignment else "N/A", "potential_issues": issues_list, "raw_output_preview": preview_str}

# --- Data Preparation Helper ---
def _prepare_data(data: Union[Dict, pd.DataFrame], target: str, features: Optional[List[str]] = None, is_timeseries: bool = True) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Converts input data to DataFrame and validates columns. Handles basic time series indexing."""
    df: Optional[pd.DataFrame] = None
    error_msg: Optional[str] = None
    try:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data.copy() # Avoid modifying original DataFrame
        else:
            error_msg = f"Invalid 'data' type: {type(data)}. Expected dict or DataFrame."
            return None, error_msg

        if df.empty:
            error_msg = "Input data is empty."
            return None, error_msg

        # Check for target column
        if target not in df.columns:
            error_msg = f"Target column '{target}' not found in data columns: {df.columns.tolist()}"
            return None, error_msg

        # Check for feature columns if provided
        if features:
            missing_features = [f for f in features if f not in df.columns]
            if missing_features:
                error_msg = f"Missing feature columns: {missing_features}"
                return None, error_msg

        # Handle time series indexing (basic example assuming 'timestamp' column or index)
        if is_timeseries:
            if 'timestamp' in df.columns:
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.set_index('timestamp')
                    logger.debug("Converted 'timestamp' column to DatetimeIndex.")
                except Exception as e_ts:
                    logger.warning(f"Could not convert 'timestamp' column to DatetimeIndex: {e_ts}. Proceeding without time index.")
            elif isinstance(df.index, pd.DatetimeIndex):
                logger.debug("Data already has a DatetimeIndex.")
            else:
                # If not DatetimeIndex and no 'timestamp' column, try to convert index if it looks date-like
                try:
                    df.index = pd.to_datetime(df.index)
                    logger.debug("Converted existing index to DatetimeIndex.")
                except Exception:
                    logger.warning("Time series data does not have a 'timestamp' column or DatetimeIndex, and index could not be converted. Model performance may be affected.")

            # Ensure frequency is set if possible (important for statsmodels)
            if isinstance(df.index, pd.DatetimeIndex) and df.index.freq is None:
                inferred_freq = pd.infer_freq(df.index)
                if inferred_freq:
                    df = df.asfreq(inferred_freq)
                    logger.info(f"Inferred time series frequency: {inferred_freq}")
                else:
                    logger.warning("Could not infer time series frequency. Forecasting might be unreliable. Ensure data has regular intervals or set frequency manually.")
            # Sort index for time series data
            df = df.sort_index()

        return df, None # Return DataFrame and no error
    except Exception as e_prep:
        error_msg = f"Data preparation failed: {e_prep}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg

# --- Main Tool Function ---
def run_prediction(operation: str, **kwargs) -> Dict[str, Any]:
    """
    [IAR Enabled] Main wrapper for predictive modeling operations.
    Dispatches to specific implementation or simulation based on 'operation'.
    Requires full implementation of specific methods using chosen libraries.

    Args:
        operation (str): The operation to perform (e.g., 'train_model',
                        'forecast_future_states', 'predict', 'evaluate_model', 'convert_to_state'). Required.
        **kwargs: Arguments specific to the operation:
            data (Optional[Union[Dict, pd.DataFrame]]): Input data.
            model_type (str): Type of model (e.g., 'ARIMA', 'Prophet', 'LinearRegression').
            target (str): Name of the target variable column.
            features (Optional[List[str]]): List of feature variable columns.
            model_id (Optional[str]): ID for saving/loading models.
            steps_to_forecast (Optional[int]): Number of steps for forecasting.
            evaluation_metrics (Optional[List[str]]): Metrics for evaluation.
            order (Optional[Tuple]): ARIMA order (p,d,q).
            prediction_result (Optional[Dict]): Result from a previous prediction step for 'convert_to_state'.
            representation_type (Optional[str]): For 'convert_to_state'.

    Returns:
        Dict[str, Any]: Dictionary containing the results of the operation
                        and the mandatory IAR 'reflection' dictionary.
    """
    # --- Initialize Results & Reflection ---
    primary_result = {"operation_performed": operation, "error": None, "libs_available": PREDICTIVE_LIBS_AVAILABLE, "note": ""}
    reflection_status = "Failure"; reflection_summary = f"Prediction op '{operation}' init failed."; confidence = 0.0; alignment = "N/A"; issues = ["Initialization error."]; reflection_preview = None

    logger.info(f"Performing prediction operation: '{operation}'")

    # --- Simulation Mode Check ---
    if not PREDICTIVE_LIBS_AVAILABLE:
        logger.warning(f"Simulating prediction operation '{operation}' due to missing libraries.")
        primary_result["note"] = "SIMULATED result (Predictive libraries not available)"
        sim_result = _simulate_prediction(operation, **kwargs)
        primary_result.update(sim_result)
        primary_result["error"] = sim_result.get("error", primary_result.get("error"))
        if primary_result["error"]:
            reflection_status = "Failure"; reflection_summary = f"Simulated prediction op '{operation}' failed: {primary_result['error']}"; reflection_confidence = 0.1; reflection_issues = [primary_result["error"]]
        else:
            reflection_status = "Success"; reflection_summary = f"Simulated prediction op '{operation}' completed."; reflection_confidence = 0.6; alignment = "Aligned with prediction/analysis goal (simulated)."; issues = ["Result is simulated."]; reflection_preview = {k:v for k,v in primary_result.items() if k not in ['operation_performed','error','libs_available','note']}
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, alignment, reflection_issues, reflection_preview)}

    # --- Actual Implementation Dispatch ---
    try:
        op_result: Dict[str, Any] = {} # Store result from the specific operation function

        # --- Operation Specific Logic ---
        if operation == 'train_model':
            op_result = _train_model(**kwargs)
        elif operation == 'forecast_future_states':
            op_result = _forecast_future_states(**kwargs)
        elif operation == 'predict': # For non-time series models
            op_result = _predict(**kwargs)
        elif operation == 'evaluate_model':
            op_result = _evaluate_model(**kwargs)
        elif operation == 'convert_to_state':
            op_result = _convert_prediction_to_state(**kwargs)
        else:
            op_result = {"error": f"Unknown prediction operation specified: {operation}"}
            # Generate default failure reflection for unknown operation
            op_result["reflection"] = _create_reflection("Failure", op_result["error"], 0.0, "N/A", ["Unknown operation"], None)

        # --- Process Result and Extract Reflection ---
        primary_result.update(op_result)
        internal_reflection = primary_result.pop("reflection", None) if isinstance(primary_result, dict) else None

        if internal_reflection is None:
            logger.error(f"Internal reflection missing from prediction operation '{operation}' result! Protocol violation.")
            internal_reflection = _create_reflection("Failure", "Internal reflection missing from tool.", 0.0, "N/A", ["Tool implementation error: Missing IAR."], op_result)
            primary_result["error"] = primary_result.get("error", "Internal reflection missing.")

        # --- Final Return ---
        primary_result["reflection"] = internal_reflection
        return primary_result

    except Exception as e_outer:
        # Catch unexpected errors in the main dispatch logic
        logger.error(f"Critical error during prediction operation '{operation}': {e_outer}", exc_info=True)
        primary_result["error"] = f"Critical failure in prediction tool orchestration: {e_outer}"
        reflection_issues = [f"Critical failure: {e_outer}"]
        reflection_summary = f"Critical failure during operation '{operation}': {e_outer}"
        return {**primary_result, "reflection": _create_reflection("Failure", reflection_summary, 0.0, "N/A", reflection_issues, None)}

# --- Internal Helper Functions for Operations ---

def _train_model(**kwargs) -> Dict[str, Any]:
    """[Implemented] Trains a predictive model (ARIMA example)."""
    # --- Initialize ---
    primary_result = {"model_id": None, "model_type": None, "parameters_used": {}, "evaluation_score": None, "error": None}
    reflection_status = "Failure"; reflection_summary = "Model training init failed."; confidence = 0.0; alignment = "N/A"; issues = []; preview = None

    try:
        # --- Extract & Validate Parameters ---
        data_input = kwargs.get("data")
        model_type = kwargs.get("model_type", config.PREDICTIVE_DEFAULT_TIMESERIES_MODEL).upper()
        target = kwargs.get("target")
        features = kwargs.get("features") # Used for multivariate models
        model_id = kwargs.get("model_id", f"{model_type.lower()}_model_{uuid.uuid4().hex[:6]}")
        primary_result["model_type"] = model_type
        primary_result["model_id"] = model_id

        if data_input is None: raise ValueError("Missing 'data' input for training.")
        if not target: raise ValueError("Missing 'target' variable name.")

        # Prepare data
        df, prep_error = _prepare_data(data_input, target, features, is_timeseries=(model_type in ["ARIMA", "PROPHET", "VAR"])) # Add other TS models
        if prep_error: raise ValueError(f"Data preparation failed: {prep_error}")
        if df is None: raise ValueError("Data preparation returned None.")

        # --- Model Specific Training ---
        trained_model_object = None
        model_fit_summary = "Training not attempted."
        model_fit_results = None # Store fit results object if available

        if model_type == "ARIMA":
            if not STATSMODELS_AVAILABLE: raise ImportError("Statsmodels library required for ARIMA model is not available.")
            order = kwargs.get("order", config.PREDICTIVE_ARIMA_DEFAULT_ORDER)
            if not isinstance(order, tuple) or len(order) != 3 or not all(isinstance(i, int) for i in order):
                raise ValueError("Invalid ARIMA 'order' parameter. Expected tuple of 3 integers (p,d,q).")
            primary_result["parameters_used"] = {"order": order}
            logger.info(f"Training ARIMA{order} model for target '{target}'...")

            try:
                # Ensure data is a Series with DatetimeIndex for ARIMA
                target_series = df[target].dropna() # Drop NaNs before fitting
                if not isinstance(target_series.index, pd.DatetimeIndex):
                    raise ValueError("ARIMA requires data with a DatetimeIndex. Ensure 'timestamp' column is present and correctly formatted or index is DatetimeIndex.")
                if target_series.index.freq is None:
                    logger.warning("ARIMA training data index has no frequency. Model fitting may fail or be unreliable. Ensure regular time intervals.")
                if target_series.empty:
                    raise ValueError("Target series is empty after dropping NaNs.")

                model = ARIMA(target_series, order=order)
                model_fit_results = model.fit()
                trained_model_object = model_fit_results # Store the results object which contains the fitted model
                model_fit_summary = model_fit_results.summary().as_text() # Get text summary
                # Extract AIC/BIC as potential evaluation metrics
                primary_result["evaluation_score"] = {"aic": float(model_fit_results.aic), "bic": float(model_fit_results.bic)}
                logger.info(f"ARIMA model trained successfully. AIC: {model_fit_results.aic:.2f}, BIC: {model_fit_results.bic:.2f}")
                # Check for convergence issues
                if hasattr(model_fit_results, 'mle_retvals') and model_fit_results.mle_retvals.get('converged') is False:
                    issues.append("ARIMA model fitting did not converge.")
                    confidence = 0.5 # Lower confidence if not converged
                else:
                    confidence = 0.85 # Higher confidence on successful fit
                reflection_status = "Success"
                reflection_summary = f"ARIMA{order} model trained successfully for target '{target}'."
                alignment = "Aligned with time series model training goal."
                preview = primary_result["evaluation_score"]

            except (ValueError, TypeError, np.linalg.LinAlgError, ConvergenceWarning, StatsmodelsValueWarning) as e_arima: # Catch specific statsmodels errors/warnings
                error_msg = f"ARIMA training failed: {type(e_arima).__name__} - {e_arima}"
                logger.error(error_msg, exc_info=True)
                primary_result["error"] = error_msg
                issues.append(f"ARIMA Error: {e_arima}")
                if isinstance(e_arima, ConvergenceWarning): issues.append("Convergence issues noted during ARIMA fit.")
            except Exception as e_arima_unexp:
                error_msg = f"Unexpected error during ARIMA training: {e_arima_unexp}"
                logger.error(error_msg, exc_info=True)
                primary_result["error"] = error_msg
                issues.append(f"System Error: {e_arima_unexp}")

        # --- Add other model types here ---
        # elif model_type == "PROPHET": ...
        else:
            primary_result["error"] = f"Unsupported model_type for training: {model_type}"
            issues.append(primary_result["error"])

        # --- Save Model Artifact ---
        if trained_model_object and not primary_result["error"]:
            if not JOBLIB_AVAILABLE:
                logger.warning("Joblib library not available. Cannot save trained model artifact.")
                issues.append("Model artifact not saved (joblib unavailable).")
            else:
                try:
                    model_filename = f"{model_id}.joblib"
                    model_filepath = os.path.join(MODEL_SAVE_DIR, model_filename)
                    joblib.dump(trained_model_object, model_filepath)
                    primary_result["model_artifact_path"] = model_filepath
                    logger.info(f"Trained model artifact saved to: {model_filepath}")
                except Exception as e_save:
                    logger.error(f"Failed to save model artifact {model_id}: {e_save}", exc_info=True)
                    issues.append(f"Model saving failed: {e_save}")
                    if confidence > 0.3: confidence = 0.7 # Lower confidence slightly

    except (ValueError, TypeError, ImportError) as e_val:
        primary_result["error"] = f"Input/Validation Error: {e_val}"
        issues = [str(e_val)]
        reflection_summary = f"Training failed due to input/validation: {e_val}"
        confidence = 0.0
    except Exception as e_train:
        primary_result["error"] = f"Unexpected training error: {e_train}"
        logger.error(f"Unexpected error during model training: {e_train}", exc_info=True)
        issues = [f"Unexpected Error: {e_train}"]
        reflection_summary = f"Training failed unexpectedly: {e_train}"
        confidence = 0.0

    # Final check on status based on error
    if primary_result["error"]: reflection_status = "Failure"

    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, confidence, alignment, issues, preview)}

def _forecast_future_states(**kwargs) -> Dict[str, Any]:
    """[Implemented] Generates forecasts using a trained time series model (ARIMA example)."""
    # --- Initialize ---
    primary_result = {"forecast": None, "confidence_intervals": None, "model_id_used": None, "error": None}
    reflection_status = "Failure"; reflection_summary = "Forecasting init failed."; confidence = 0.0; alignment = "N/A"; issues = []; preview = None

    try:
        # --- Extract & Validate Parameters ---
        model_id = kwargs.get("model_id")
        steps = int(kwargs.get("steps_to_forecast", 10))
        # Optional: Pass historical data if needed by forecast method (e.g., for dynamic prediction)
        # data_input = kwargs.get("data") # Not typically needed for simple get_forecast
        alpha = float(kwargs.get("confidence_level", 0.05)) # Alpha for confidence intervals (e.g., 0.05 for 95% CI)

        if not model_id: raise ValueError("Missing 'model_id' input for forecasting.")
        if steps <= 0: raise ValueError("'steps_to_forecast' must be positive.")
        primary_result["model_id_used"] = model_id

        # --- Load Model ---
        if not JOBLIB_AVAILABLE: raise ImportError("Joblib library required to load model artifact is not available.")
        model_filename = f"{model_id}.joblib"
        model_filepath = os.path.join(MODEL_SAVE_DIR, model_filename)
        if not os.path.exists(model_filepath): raise FileNotFoundError(f"Model artifact not found at {model_filepath}")

        try:
            # Load the saved model results object (contains fitted model)
            model_fit_results = joblib.load(model_filepath)
            logger.info(f"Loaded model artifact: {model_filepath}")
            # Basic check if loaded object seems like statsmodels results
            if not isinstance(model_fit_results, ARIMAResultsWrapper):
                logger.warning(f"Loaded object type ({type(model_fit_results)}) is not ARIMAResultsWrapper. Forecasting may fail if it's not a compatible time series model.")
        except Exception as e_load:
            raise ValueError(f"Failed to load model artifact {model_id}: {e_load}")

        # --- Generate Forecast ---
        logger.info(f"Generating forecast for {steps} steps using model {model_id}...")
        try:
            # Use get_forecast for statsmodels ARIMA results
            forecast_obj = model_fit_results.get_forecast(steps=steps)
            # Extract predicted mean values
            forecast_values = forecast_obj.predicted_mean.tolist()
            # Extract confidence intervals
            conf_int_df = forecast_obj.conf_int(alpha=alpha) # Returns DataFrame
            conf_intervals = conf_int_df.values.tolist() # Convert to list of [lower, upper]

            primary_result["forecast"] = forecast_values
            primary_result["confidence_intervals"] = conf_intervals
            reflection_status = "Success"
            reflection_summary = f"Generated forecast for {steps} steps using model {model_id}."
            # Confidence might relate to width of CIs or model properties
            confidence = 0.8 # Base confidence for successful forecast
            # Example: Reduce confidence if CIs are very wide (relative to forecast values)
            if forecast_values and conf_intervals:
                avg_forecast = np.mean(forecast_values) if forecast_values else 0
                avg_ci_width = np.mean([ci[1] - ci[0] for ci in conf_intervals if len(ci)==2]) if conf_intervals else 0
                if avg_forecast != 0 and abs(avg_ci_width / avg_forecast) > 0.5: # If avg CI width > 50% of avg forecast magnitude
                    confidence = max(0.3, confidence * 0.7) # Reduce confidence
                    issues.append("Forecast confidence intervals are wide relative to predicted values.")
            alignment = "Aligned with forecasting goal."
            preview = {"forecast_start": forecast_values[0] if forecast_values else None, "steps": steps}

        except Exception as e_forecast:
            error_msg = f"Forecasting failed using model {model_id}: {e_forecast}"
            logger.error(error_msg, exc_info=True)
            primary_result["error"] = error_msg
            issues.append(f"Forecast Error: {e_forecast}")

    except (ValueError, TypeError, ImportError, FileNotFoundError) as e_val:
        primary_result["error"] = f"Input/Validation/Load Error: {e_val}"
        issues = [str(e_val)]
        reflection_summary = f"Forecasting failed due to input/validation: {e_val}"
        confidence = 0.0
    except Exception as e_fcst_outer:
        primary_result["error"] = f"Unexpected forecasting error: {e_fcst_outer}"
        logger.error(f"Unexpected error during forecasting: {e_fcst_outer}", exc_info=True)
        issues = [f"Unexpected Error: {e_fcst_outer}"]
        reflection_summary = f"Forecasting failed unexpectedly: {e_fcst_outer}"
        confidence = 0.0

    # Final check on status based on error
    if primary_result["error"]: reflection_status = "Failure"

    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, confidence, alignment, issues, preview)}

def _predict(**kwargs) -> Dict[str, Any]:
    """[Requires Implementation] Generates predictions using a trained non-time series model."""
    # Placeholder - Requires implementation for models like LinearRegression, RandomForest etc. using sklearn/joblib
    error_msg = "Actual prediction ('predict' for non-timeseries) not implemented."
    logger.error(error_msg)
    return {"error": error_msg, "reflection": _create_reflection("Failure", error_msg, 0.0, "N/A", ["Not Implemented"], None)}

def _evaluate_model(**kwargs) -> Dict[str, Any]:
    """[Implemented with Refinements] Evaluates a trained model on test data (using sklearn metrics)."""
    # --- Initialize ---
    primary_result = {"evaluation_scores": None, "model_id_used": None, "error": None}
    reflection_status = "Failure"; reflection_summary = "Model evaluation init failed."; confidence = 0.0; alignment = "N/A"; issues = []; preview = None

    try:
        # --- Extract & Validate Parameters ---
        model_id = kwargs.get("model_id")
        data_input = kwargs.get("data") # Test data
        target = kwargs.get("target")
        features = kwargs.get("features") # Optional, depends on model type
        metrics_to_calc = kwargs.get("evaluation_metrics", config.PREDICTIVE_DEFAULT_EVAL_METRICS)

        if not model_id: raise ValueError("Missing 'model_id' input for evaluation.")
        if data_input is None: raise ValueError("Missing 'data' (test data) input for evaluation.")
        if not target: raise ValueError("Missing 'target' variable name for evaluation.")
        if not isinstance(metrics_to_calc, list) or not metrics_to_calc: raise ValueError("Invalid 'evaluation_metrics' list.")
        primary_result["model_id_used"] = model_id

        # --- Load Model ---
        if not JOBLIB_AVAILABLE: raise ImportError("Joblib library required to load model artifact is not available.")
        model_filename = f"{model_id}.joblib"
        model_filepath = os.path.join(MODEL_SAVE_DIR, model_filename)
        if not os.path.exists(model_filepath): raise FileNotFoundError(f"Model artifact not found at {model_filepath}")
        try:
            model_object = joblib.load(model_filepath) # Load the fitted model/results object
            logger.info(f"Loaded model artifact for evaluation: {model_filepath}")
        except Exception as e_load:
            raise ValueError(f"Failed to load model artifact {model_id}: {e_load}")

        # --- Prepare Data ---
        df_test, prep_error = _prepare_data(data_input, target, features, is_timeseries=isinstance(model_object, TimeSeriesModelResults))
        if prep_error: raise ValueError(f"Test data preparation failed: {prep_error}")
        if df_test is None: raise ValueError("Test data preparation returned None.")

        y_true = df_test[target]
        X_test = df_test[features] if features else df_test.drop(columns=[target], errors='ignore') # Use features or all other cols
        if X_test.empty and features: raise ValueError("Test data features are empty after preparation with specified features.")
        if X_test.empty and not features and len(df_test.columns) > 1 : logger.warning("X_test is empty after dropping target; model might require exogenous features not provided or data is univariate.")
        if y_true.isnull().any(): logger.warning("Target variable in test data contains NaNs. Evaluation might be affected.")

        # --- Generate Predictions on Test Data ---
        logger.info(f"Generating predictions on test data using model {model_id}...")
        y_pred: Optional[pd.Series] = None
        try:
            # Explicitly handle TimeSeriesModelResults (includes ARIMAResultsWrapper)
            if isinstance(model_object, ARIMAResultsWrapper):
                logger.debug("Branch: isinstance(model_object, ARIMAResultsWrapper) == True")
                if not df_test.empty:
                    y_pred_values_raw = None # Initialize
                    prediction_method_used = "None"
                    try:
                        logger.debug(f"Attempting model_object.predict(start={df_test.index.min()}, end={df_test.index.max()})")
                        y_pred_values_raw = model_object.predict(start=df_test.index.min(), end=df_test.index.max())
                        prediction_method_used = "predict(start,end)"
                        logger.debug(f"Raw y_pred_values from predict(start,end): {y_pred_values_raw[:5]}... (len: {len(y_pred_values_raw) if y_pred_values_raw is not None else 'None'})")
                        if isinstance(y_pred_values_raw, pd.Series): y_pred_values_raw = y_pred_values_raw.values # Ensure numpy array for isnan
                        if y_pred_values_raw is not None and np.isnan(y_pred_values_raw).all():
                            logger.warning("predict(start,end) resulted in all NaNs. Will try get_forecast.")
                            raise ValueError("predict(start,end) resulted in all NaNs") # Force fallback

                        y_pred = pd.Series(y_pred_values_raw, name=target)
                        y_pred = y_pred.reindex(df_test.index)
                    except Exception as e_ts_predict:
                        logger.warning(f"TimeSeries predict(start,end) failed or produced all NaNs: {e_ts_predict}. Trying get_forecast.")
                        try:
                            if not isinstance(df_test.index, pd.DatetimeIndex):
                                raise ValueError("df_test.index must be a DatetimeIndex for get_forecast.")
                            steps_to_forecast = len(df_test.index)
                            logger.debug(f"Attempting model_object.get_forecast(steps={steps_to_forecast})")
                            forecast_obj = model_object.get_forecast(steps=steps_to_forecast)
                            y_pred_values_raw = forecast_obj.predicted_mean
                            prediction_method_used = "get_forecast(steps)"
                            logger.debug(f"Raw y_pred_values from get_forecast: {y_pred_values_raw[:5]}... (len: {len(y_pred_values_raw) if y_pred_values_raw is not None else 'None'})")
                            if isinstance(y_pred_values_raw, pd.Series): y_pred_values_raw = y_pred_values_raw.values
                            if y_pred_values_raw is not None and np.isnan(y_pred_values_raw).all():
                                logger.error("get_forecast(steps) also resulted in all NaNs.")
                                # Let it proceed, will likely fail at alignment

                            if len(y_pred_values_raw) == len(df_test.index):
                                y_pred = pd.Series(y_pred_values_raw, index=df_test.index, name=target)
                            else:
                                raise ValueError(f"Length of get_forecast values ({len(y_pred_values_raw)}) does not match df_test index ({len(df_test.index)}).")
                        except Exception as e_ts_forecast:
                            raise ValueError(f"Both predict and get_forecast failed for TimeSeriesModel: Predict err: {e_ts_predict}, Forecast err: {e_ts_forecast}")
                else: # df_test is empty
                    y_pred = pd.Series(dtype=float, name=target, index=df_test.index)
                    prediction_method_used = "empty_df_test"
                logger.info(f"Prediction method used in _evaluate_model: {prediction_method_used}")
            elif hasattr(model_object, 'predict'):
                if X_test.empty and features:
                    raise ValueError("X_test is empty but features were specified for a non-time series model.")
                pred_values = model_object.predict(X_test) # Assumes X_test is appropriate for these models
                y_pred = pd.Series(pred_values, index=X_test.index if not X_test.empty else y_true.index, name=target)
            
            else:
                raise TypeError(f"Loaded model object (type: {type(model_object)}) does not have a recognized 'predict' or 'get_forecast' method.")

            if y_pred is None:
                raise ValueError("Prediction (y_pred) is None after attempting generation.")

            # Align y_pred with y_true's index. This is crucial.
            y_pred = y_pred.reindex(y_true.index)

            logger.debug(f"y_true before dropna: len={len(y_true)}, NaNs={y_true.isnull().sum()}\n{y_true.head().to_string()}")
            logger.debug(f"y_pred before dropna: len={len(y_pred)}, NaNs={y_pred.isnull().sum()}\n{y_pred.head().to_string()}")

            # Drop NaNs that might have resulted from reindexing or were in original y_true/y_pred
            # Symmetrical drop: only keep indices where BOTH y_true and y_pred are non-NaN
            common_valid_index = y_true.dropna().index.intersection(y_pred.dropna().index)
            y_true_aligned = y_true.loc[common_valid_index]
            y_pred_aligned = y_pred.loc[common_valid_index]

            if y_pred_aligned.empty or y_true_aligned.empty:
                logger.error(f"y_pred_aligned (len {len(y_pred_aligned)}) or y_true_aligned (len {len(y_true_aligned)}) is empty. Original y_true len: {len(y_true)}, original y_pred len: {len(y_pred) if y_pred is not None else 'None'}")
                logger.debug(f"y_true index: {y_true.index if y_true is not None else 'N/A'}")
                logger.debug(f"y_pred index before final alignment: {y_pred.index if y_pred is not None and hasattr(y_pred, 'index') else 'N/A'}")
                logger.debug(f"Common valid index: {common_valid_index}")
                raise ValueError("Predictions or true values are empty after alignment/dropping NaNs.")

            y_pred_final = y_pred_aligned
            y_true_final = y_true_aligned

        except Exception as e_pred:
            error_msg = f"Prediction generation failed during evaluation: {e_pred}"
            logger.error(error_msg, exc_info=True)
            primary_result["error"] = error_msg
            issues.append(f"Prediction Error: {e_pred}")
            raise ValueError(error_msg) # Raise to stop evaluation

        # --- Calculate Metrics ---
        if not SKLEARN_AVAILABLE: raise ImportError("Scikit-learn library required for evaluation metrics is not available.")
        logger.info(f"Calculating evaluation metrics: {metrics_to_calc}")
        scores = {}
        metric_errors = []
        for metric_name in metrics_to_calc:
            metric_name_lower = metric_name.lower()
            try:
                if metric_name_lower == "mean_absolute_error":
                    scores[metric_name] = float(mean_absolute_error(y_true_final, y_pred_final))
                elif metric_name_lower == "mean_squared_error":
                    scores[metric_name] = float(mean_squared_error(y_true_final, y_pred_final))
                elif metric_name_lower == "root_mean_squared_error":
                    scores[metric_name] = float(np.sqrt(mean_squared_error(y_true_final, y_pred_final)))
                elif metric_name_lower == "r2_score":
                    scores[metric_name] = float(r2_score(y_true_final, y_pred_final))
                else:
                    logger.warning(f"Unsupported evaluation metric '{metric_name}'. Skipping.")
                    metric_errors.append(f"Unsupported metric: {metric_name}")
            except Exception as e_metric:
                logger.error(f"Failed to calculate metric '{metric_name}': {e_metric}")
                metric_errors.append(f"Error calculating {metric_name}: {e_metric}")

        primary_result["evaluation_scores"] = scores
        if metric_errors: issues.extend(metric_errors)

        # --- Generate IAR Reflection ---
        reflection_status = "Success" if scores and not primary_result.get("error") else "Partial" if scores else "Failure"
        reflection_summary = f"Model {model_id} evaluated using metrics: {list(scores.keys())}."
        if metric_errors: reflection_summary += f" Errors calculating: {metric_errors}."
        r2 = scores.get('r2_score', scores.get('R2_Score'))
        confidence = float(max(0.1, min(0.95, r2))) if r2 is not None and r2 > -1 else 0.5
        alignment = "Aligned with model evaluation goal."
        preview = scores

    except (ValueError, TypeError, ImportError, FileNotFoundError) as e_val:
        primary_result["error"] = f"Input/Validation/Load Error: {e_val}"
        issues = [str(e_val)]
        reflection_summary = f"Evaluation failed due to input/validation: {e_val}"
        confidence = 0.0
    except Exception as e_eval:
        primary_result["error"] = f"Unexpected evaluation error: {e_eval}"
        logger.error(f"Unexpected error during model evaluation: {e_eval}", exc_info=True)
        issues = [f"Unexpected Error: {e_eval}"]
        reflection_summary = f"Evaluation failed unexpectedly: {e_eval}"
        confidence = 0.0

    # Final status check
    if primary_result["error"]: reflection_status = "Failure"

    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, confidence, alignment, issues, preview)}

def _convert_prediction_to_state(**kwargs) -> Dict[str, Any]:
    """[Implemented] Converts prediction results into a state vector for CFP."""
    # --- Initialize ---
    primary_result = {"state_vector": None, "representation_type": None, "dimensions": 0, "error": None}
    reflection_status = "Failure"; summary = "Prediction state conversion init failed."; confidence = 0.0; alignment = "N/A"; issues = []; preview = None

    try:
        # --- Extract & Validate Parameters ---
        prediction_result = kwargs.get('prediction_result') # Expects the full dict from a forecast/predict step
        representation_type = kwargs.get('representation_type', 'forecast_values') # Default type
        primary_result["representation_type"] = representation_type

        if not prediction_result or not isinstance(prediction_result, dict):
            raise ValueError("Missing or invalid 'prediction_result' dictionary input.")
        # Check if the input result itself indicates an error
        input_error = prediction_result.get("error")
        if input_error: raise ValueError(f"Input prediction result contains error: {input_error}")

        logger.info(f"Converting prediction result to state vector (type: {representation_type})")
        state_vector_list: List[float] = []
        error_msg: Optional[str] = None

        # --- Conversion Logic ---
        if representation_type == 'forecast_values':
            forecast_vals = prediction_result.get('forecast')
            if forecast_vals is None or not isinstance(forecast_vals, list):
                error_msg = "Missing 'forecast' list in prediction_result for 'forecast_values' conversion."
            else:
                try: state_vector_list = [float(v) for v in forecast_vals]
                except (ValueError, TypeError) as e_conv: error_msg = f"Could not convert forecast values to float: {e_conv}"
        elif representation_type == 'forecast_with_ci_width':
            forecast_vals = prediction_result.get('forecast')
            ci_vals = prediction_result.get('confidence_intervals')
            if forecast_vals is None or not isinstance(forecast_vals, list) or \
                ci_vals is None or not isinstance(ci_vals, list) or \
                len(forecast_vals) != len(ci_vals):
                error_msg = "Missing/mismatched 'forecast' or 'confidence_intervals' in prediction_result for 'forecast_with_ci_width'."
            else:
                try:
                    state_vector_list = []
                    for f_val, ci_pair in zip(forecast_vals, ci_vals):
                        if isinstance(ci_pair, list) and len(ci_pair) == 2:
                            state_vector_list.append(float(f_val))
                            state_vector_list.append(float(ci_pair[1] - ci_pair[0])) # CI Width
                        else: raise ValueError("Invalid CI pair format.")
                except (ValueError, TypeError) as e_conv: error_msg = f"Could not process forecast/CI values: {e_conv}"
        elif representation_type == 'evaluation_metrics':
            eval_scores = prediction_result.get('evaluation_scores')
            if eval_scores is None or not isinstance(eval_scores, dict):
                error_msg = "Missing 'evaluation_scores' dict in prediction_result for 'evaluation_metrics' conversion."
            else:
                # Convert metrics to a consistent order (e.g., sorted by key)
                try: state_vector_list = [float(eval_scores[k]) for k in sorted(eval_scores.keys()) if isinstance(eval_scores[k], (int, float))]
                except (ValueError, TypeError) as e_conv: error_msg = f"Could not convert evaluation scores to float: {e_conv}"
        else:
            error_msg = f"Unsupported representation_type for prediction state conversion: {representation_type}"

        # --- Final Processing & Normalization ---
        if error_msg:
            primary_result["error"] = error_msg
            state_vector_final = np.array([0.0, 0.0]) # Default error state vector
        elif not state_vector_list: # If list is empty after processing
            logger.warning(f"Resulting state vector for type '{representation_type}' is empty. Using default error state.")
            state_vector_final = np.array([0.0, 0.0])
        else:
            state_vector_final = np.array(state_vector_list, dtype=float)

        # Normalize the final state vector (L2 norm) - optional, depends on CFP use case
        norm = np.linalg.norm(state_vector_final)
        if norm > 1e-15: state_vector_normalized = state_vector_final / norm
        else: logger.warning(f"State vector for type '{representation_type}' has zero norm. Not normalizing."); state_vector_normalized = state_vector_final

        final_list = state_vector_normalized.tolist()
        dimensions = len(final_list)
        primary_result.update({"state_vector": final_list, "dimensions": dimensions})

        # --- Generate IAR Reflection ---
        if primary_result["error"]:
            reflection_status = "Failure"; summary = f"State conversion failed: {primary_result['error']}"; confidence = 0.1; issues = [primary_result["error"]]; alignment = "Failed to convert state."
        else:
            reflection_status = "Success"; summary = f"Prediction results successfully converted to state vector (type: {representation_type}, dim: {dimensions})."; confidence = 0.9; alignment = "Aligned with preparing data for comparison/CFP."; issues = None; preview = final_list

    except (ValueError, TypeError, ImportError) as e_val:
        primary_result["error"] = f"Input/Validation/Import Error: {e_val}"
        issues = [str(e_val)]; summary = f"State conversion failed: {e_val}"; confidence = 0.0
    except Exception as e_conv_outer:
        primary_result["error"] = f"Unexpected state conversion error: {e_conv_outer}"
        logger.error(f"Unexpected error converting prediction results to state vector: {e_conv_outer}", exc_info=True)
        issues = [f"Unexpected Error: {e_conv_outer}"]; summary = f"State conversion failed unexpectedly: {e_conv_outer}"; confidence = 0.0
        if primary_result.get("state_vector") is None: primary_result["state_vector"] = [0.0, 0.0]; primary_result["dimensions"] = 2

    # Final status check
    if primary_result["error"]: reflection_status = "Failure"

    return {**primary_result, "reflection": _create_reflection(reflection_status, summary, confidence, alignment, issues, preview)}

# --- Internal Simulation Function ---
def _simulate_prediction(operation: str, **kwargs) -> Dict[str, Any]:
    """Simulates prediction results when libraries are unavailable."""
    logger.debug(f"Simulating prediction operation '{operation}' with kwargs: {kwargs}")
    result = {"error": None}
    np.random.seed(int(time.time()) % 1000 + 4) # Seed

    if operation == 'train_model':
        model_id = kwargs.get('model_id', f"sim_model_{uuid.uuid4().hex[:6]}")
        model_type = kwargs.get('model_type', config.PREDICTIVE_DEFAULT_TIMESERIES_MODEL)
        target = kwargs.get('target', 'value')
        sim_score = np.random.uniform(0.6, 0.95)
        result.update({"model_id": model_id, "evaluation_score": float(sim_score), "model_type": model_type, "target_variable": target})
        try:
            dummy_path = os.path.join(MODEL_SAVE_DIR, f"{model_id}.sim_model")
            with open(dummy_path, 'w') as f: f.write(f"Simulated model: {model_type}, Target: {target}, Score: {sim_score}")
            result["model_artifact_path"] = dummy_path
        except Exception as e_save: result["warning"] = f"Could not save simulated model file: {e_save}"

    elif operation == 'forecast_future_states':
        steps = int(kwargs.get('steps_to_forecast', 10))
        model_id = kwargs.get('model_id', 'sim_model_default')
        last_val = np.random.rand() * 100
        forecast_vals = last_val + np.cumsum(np.random.normal(0.1, 2.0, steps))
        ci_width = np.random.uniform(5, 15, steps)
        conf_intervals = [[float(f - w/2), float(f + w/2)] for f, w in zip(forecast_vals, ci_width)]
        result.update({"forecast": [float(f) for f in forecast_vals], "confidence_intervals": conf_intervals, "model_id_used": model_id})

    elif operation == 'predict':
        data = kwargs.get('data', [{}])
        model_id = kwargs.get('model_id', 'sim_model_reg')
        num_preds = len(data) if isinstance(data, list) else 5
        predictions = np.random.rand(num_preds) * 50 + np.random.normal(0, 5, num_preds)
        result.update({"predictions": [float(p) for p in predictions], "model_id_used": model_id})

    elif operation == 'evaluate_model':
        model_id = kwargs.get('model_id', 'sim_model_eval')
        metrics = kwargs.get('evaluation_metrics', config.PREDICTIVE_DEFAULT_EVAL_METRICS)
        scores = {}
        for metric in metrics:
            if "error" in metric.lower(): scores[metric] = float(np.random.uniform(1, 10))
            elif "r2" in metric.lower(): scores[metric] = float(np.random.uniform(0.5, 0.9))
            else: scores[metric] = float(np.random.uniform(0.1, 0.5))
        result.update({"evaluation_scores": scores, "model_id_used": model_id})

    elif operation == 'convert_to_state':
        pred_result = kwargs.get('prediction_result', {})
        rep_type = kwargs.get('representation_type', 'forecast_values')
        state_vector = [np.random.rand() for _ in range(5)] # Default 5D state
        if rep_type == 'forecast_values' and 'forecast' in pred_result:
            state_vector = [float(x) for x in pred_result['forecast'][:5]] if isinstance(pred_result['forecast'], list) else state_vector
        elif rep_type == 'evaluation_metrics' and 'evaluation_scores' in pred_result:
            state_vector = [float(x) for x in pred_result['evaluation_scores'].values()][:5] if isinstance(pred_result['evaluation_scores'], dict) else state_vector
        norm = np.linalg.norm(state_vector)
        state_vector_list = (np.array(state_vector) / norm).tolist() if norm > 1e-9 and state_vector else [0.0]*len(state_vector)
        result.update({"state_vector": state_vector_list, "dimensions": len(state_vector_list), "representation_type": rep_type})

    else:
        result["error"] = f"Unknown or unimplemented simulated operation: {operation}"

    return result

# --- END OF FILE 3.0ArchE/predictive_modeling_tool.py ---