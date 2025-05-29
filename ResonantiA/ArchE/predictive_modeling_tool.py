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
# Use relative imports for configuration
try:
    from . import config
except ImportError:
    # Fallback config if running standalone or package structure differs
    class FallbackConfig:
        PREDICTIVE_DEFAULT_TIMESERIES_MODEL = "ARIMA"
        MODEL_SAVE_DIR = 'outputs/models'
        PREDICTIVE_ARIMA_DEFAULT_ORDER = (1, 1, 1)
        PREDICTIVE_DEFAULT_EVAL_METRICS = ["mean_absolute_error"]
    config = FallbackConfig(); logging.warning("config.py not found for predictive tool, using fallback configuration.")

# --- Import Predictive Libraries (Set flag based on success) ---
PREDICTIVE_LIBS_AVAILABLE = False
STATSMODELS_AVAILABLE = False
SKLEARN_AVAILABLE = False
JOBLIB_AVAILABLE = False
try:
    import statsmodels.api as sm # For ARIMA, VAR etc.
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.base.tsa_model import TimeSeriesModelResults # For type hinting fit results
    STATSMODELS_AVAILABLE = True
    from sklearn.model_selection import train_test_split # For evaluation
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score # Example metrics
    SKLEARN_AVAILABLE = True
    import joblib # For saving/loading trained models
    JOBLIB_AVAILABLE = True

    PREDICTIVE_LIBS_AVAILABLE = True # Set flag to True if all core libs loaded
    logging.getLogger(__name__).info("Actual predictive modeling libraries (statsmodels, sklearn, joblib) loaded successfully.")

except ImportError as e_imp:
    logging.getLogger(__name__).warning(f"Predictive libraries import failed: {e_imp}. Predictive Tool will run in SIMULATION MODE.")
except Exception as e_imp_other:
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
    issues_list = issues if issues else None
    try:
        # Attempt JSON serialization first for complex previews
        preview_str = json.dumps(preview, default=str) if isinstance(preview, (dict, list)) else str(preview)
        if preview_str and len(preview_str) > 150:
            preview_str = preview_str[:150] + "..."
    except Exception:
        try: # Fallback to simple string conversion
            preview_str = str(preview)
            if preview_str and len(preview_str) > 150: preview_str = preview_str[:150] + "..."
        except Exception:
            preview_str = "[Preview Error]"
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
                logger.warning("Time series data does not have a 'timestamp' column or DatetimeIndex. Model performance may be affected.")
            # Ensure frequency is set if possible (important for statsmodels)
            if isinstance(df.index, pd.DatetimeIndex) and df.index.freq is None:
                inferred_freq = pd.infer_freq(df.index)
                if inferred_freq:
                    df = df.asfreq(inferred_freq)
                    logger.info(f"Inferred time series frequency: {inferred_freq}")
                else:
                    logger.warning("Could not infer time series frequency. Forecasting might be unreliable.")

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
                        'forecast_future_states', 'predict', 'evaluate_model'). Required.
        **kwargs: Arguments specific to the operation:
            data (Optional[Union[Dict, pd.DataFrame]]): Input data.
            model_type (str): Type of model (e.g., 'ARIMA', 'Prophet', 'LinearRegression').
            target (str): Name of the target variable column.
            features (Optional[List[str]]): List of feature variable columns.
            model_id (Optional[str]): ID for saving/loading models.
            steps_to_forecast (Optional[int]): Number of steps for forecasting.
            evaluation_metrics (Optional[List[str]]): Metrics for evaluation.
            order (Optional[Tuple]): ARIMA order (p,d,q).
            # Add other model-specific parameters as needed

    Returns:
        Dict[str, Any]: Dictionary containing the results of the operation
                        and the mandatory IAR 'reflection' dictionary.
    """
    # --- Initialize Results & Reflection ---
    primary_result = {"operation_performed": operation, "error": None, "libs_available": PREDICTIVE_LIBS_AVAILABLE, "note": ""}
    reflection_status = "Failure"; reflection_summary = f"Prediction op '{operation}' init failed."; reflection_confidence = 0.0; reflection_alignment = "N/A"; reflection_issues = ["Initialization error."]; reflection_preview = None

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
            reflection_status = "Success"; reflection_summary = f"Simulated prediction op '{operation}' completed."; reflection_confidence = 0.6; reflection_alignment = "Aligned with prediction/analysis goal (simulated)."; reflection_issues = ["Result is simulated."]; reflection_preview = {k:v for k,v in primary_result.items() if k not in ['operation_performed','error','libs_available','note']}
        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

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
        if df is None: raise ValueError("Data preparation returned None.") # Should be caught by prep_error

        # --- Model Specific Training ---
        trained_model_object = None
        model_fit_summary = "Training not attempted."
        model_fit_results = None # Store fit results object if available

        if model_type == "ARIMA":
            if not STATSMODELS_AVAILABLE: raise ImportError("Statsmodels library required for ARIMA model is not available.")
            order = kwargs.get("order", config.PREDICTIVE_ARIMA_DEFAULT_ORDER)
            if not isinstance(order, tuple) or len(order) != 3: raise ValueError("Invalid ARIMA 'order' parameter. Expected tuple of 3 integers (p,d,q).")
            primary_result["parameters_used"] = {"order": order}
            logger.info(f"Training ARIMA{order} model for target '{target}'...")

            try:
                # Ensure data is a Series with DatetimeIndex for ARIMA
                target_series = df[target].dropna() # Drop NaNs before fitting
                if not isinstance(target_series.index, pd.DatetimeIndex):
                    raise ValueError("ARIMA requires data with a DatetimeIndex.")
                if target_series.empty:
                    raise ValueError("Target series is empty after dropping NaNs.")

                model = ARIMA(target_series, order=order)
                model_fit_results = model.fit()
                trained_model_object = model_fit_results # Store the results object which contains the fitted model
                model_fit_summary = model_fit_results.summary().as_text() # Get text summary
                # Extract AIC/BIC as potential evaluation metrics
                primary_result["evaluation_score"] = {"aic": model_fit_results.aic, "bic": model_fit_results.bic}
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

            except (ValueError, TypeError, LinAlgError) as e_arima: # Catch specific statsmodels errors
                error_msg = f"ARIMA training failed: {e_arima}"
                logger.error(error_msg, exc_info=True)
                primary_result["error"] = error_msg
                issues.append(f"ARIMA Error: {e_arima}")
            except Exception as e_arima_unexp:
                error_msg = f"Unexpected error during ARIMA training: {e_arima_unexp}"
                logger.error(error_msg, exc_info=True)
                primary_result["error"] = error_msg
                issues.append(f"System Error: {e_arima_unexp}")

        # --- Add other model types here ---
        # elif model_type == "PROPHET":
        #     if not prophet: raise ImportError("Prophet library required but not available.")
        #     # <<< INSERT Prophet training logic >>>
        #     # Requires data in specific format (ds, y columns)
        #     # model = Prophet(**kwargs.get('prophet_params', config.PREDICTIVE_PROPHET_DEFAULT_PARAMS))
        #     # model.fit(df_prophet_format)
        #     # trained_model_object = model
        #     # ... handle results, save model, set IAR ...
        #     primary_result["error"] = "Prophet model training not implemented."
        #     issues.append(primary_result["error"])

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
                    # Don't mark as failure just because saving failed, but lower confidence?
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
        data_input = kwargs.get("data")
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
            if not isinstance(model_fit_results, TimeSeriesModelResults):
                 logger.warning(f"Loaded object type ({type(model_fit_results)}) might not be ARIMA results. Forecasting may fail.")
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
                avg_forecast = np.mean(forecast_values)
                avg_ci_width = np.mean([ci[1] - ci[0] for ci in conf_intervals])
                if avg_forecast != 0 and (avg_ci_width / abs(avg_forecast)) > 0.5: # If avg CI width > 50% of avg forecast
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
        primary_result["error"] = f"Input/Validation Error: {e_val}"
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
    """[Implemented] Evaluates a trained model on test data (using sklearn metrics)."""
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
        # Assume data needs similar prep as training, but might differ (e.g., no fitting)
        df_test, prep_error = _prepare_data(data_input, target, features, is_timeseries=hasattr(model_object, 'predict')) # Guess if TS based on predict method presence
        if prep_error: raise ValueError(f"Test data preparation failed: {prep_error}")
        if df_test is None: raise ValueError("Test data preparation returned None.")

        # Separate features (if needed) and target
        y_true = df_test[target]
        X_test = df_test[features] if features else df_test # Use features if provided, else might be needed by model.predict
        if X_test.empty: raise ValueError("Test data features are empty after preparation.")
        if y_true.isnull().any(): logger.warning("Target variable in test data contains NaNs. Evaluation might be affected.")

        # --- Generate Predictions on Test Data ---
        logger.info(f"Generating predictions on test data using model {model_id}...")
        try:
            # Prediction logic depends heavily on model type (statsmodels vs sklearn etc.)
            if hasattr(model_object, 'predict'):
                # Handle statsmodels (predict needs start/end or exog) or sklearn (predict needs X)
                if isinstance(model_object, TimeSeriesModelResults): # Statsmodels Time Series
                    # Predict needs start/end indices relative to the original data
                    # Or use forecast if predicting beyond original data
                    y_pred = model_object.predict(start=X_test.index.min(), end=X_test.index.max())
                    # Align prediction index with true values for metric calculation
                    y_pred = y_pred.reindex(y_true.index)
                # elif isinstance(model_object, sklearn_model_type): # Check for sklearn type
                #     y_pred = model_object.predict(X_test)
                else: # Generic fallback attempt
                    try: y_pred = model_object.predict(X_test)
                    except TypeError: # Handle predict() not taking X_test directly
                         y_pred = model_object.predict(start=X_test.index.min(), end=X_test.index.max())
                         y_pred = y_pred.reindex(y_true.index)

            else: raise TypeError(f"Loaded model object (type: {type(model_object)}) does not have a standard 'predict' method.")

            # Ensure y_pred is pandas Series or numpy array aligned with y_true
            y_pred = pd.Series(y_pred, index=y_true.index).dropna() # Align and drop NaNs from prediction
            y_true = y_true.reindex(y_pred.index).dropna() # Align true values and drop corresponding NaNs

            if y_pred.empty or y_true.empty: raise ValueError("Predictions or true values are empty after alignment/dropping NaNs.")

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
                    scores[metric_name] = float(mean_absolute_error(y_true, y_pred))
                elif metric_name_lower == "mean_squared_error":
                    scores[metric_name] = float(mean_squared_error(y_true, y_pred))
                elif metric_name_lower == "root_mean_squared_error":
                    scores[metric_name] = float(np.sqrt(mean_squared_error(y_true, y_pred)))
                elif metric_name_lower == "r2_score":
                    scores[metric_name] = float(r2_score(y_true, y_pred))
                # Add other common metrics (e.g., MASE for time series, Accuracy/F1 for classification)
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
        reflection_summary = f"Model {model_id} evaluated using metrics: {list(scores.keys())}. "
        if metric_errors: reflection_summary += f"Errors calculating: {metric_errors}."
        # Confidence based on key metrics (e.g., R2 score if present)
        r2 = scores.get('r2_score', scores.get('R2_Score'))
        confidence = float(max(0.1, min(0.95, r2))) if r2 is not None and r2 > -1 else 0.5 # Map R2 to confidence roughly, default 0.5
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

    # Final check on status based on error
    if primary_result["error"]: reflection_status = "Failure"

    return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, confidence, alignment, issues, preview)}

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
        # Simulate some evaluation score
        sim_score = np.random.uniform(0.6, 0.95)
        result.update({"model_id": model_id, "evaluation_score": float(sim_score), "model_type": model_type, "target_variable": target})
        # Simulate saving the model (create dummy file)
        try:
            dummy_path = os.path.join(MODEL_SAVE_DIR, f"{model_id}.sim_model")
            with open(dummy_path, 'w') as f: f.write(f"Simulated model: {model_type}, Target: {target}, Score: {sim_score}")
            result["model_artifact_path"] = dummy_path
        except Exception as e_save: result["warning"] = f"Could not save simulated model file: {e_save}"

    elif operation == 'forecast_future_states':
        steps = int(kwargs.get('steps_to_forecast', 10))
        model_id = kwargs.get('model_id', 'sim_model_default')
        # Simulate forecast with some trend and noise
        last_val = np.random.rand() * 100 # Simulate a last value
        forecast_vals = last_val + np.cumsum(np.random.normal(0.1, 2.0, steps))
        ci_width = np.random.uniform(5, 15, steps)
        conf_intervals = [[float(f - w/2), float(f + w/2)] for f, w in zip(forecast_vals, ci_width)]
        result.update({"forecast": [float(f) for f in forecast_vals], "confidence_intervals": conf_intervals, "model_id_used": model_id})

    elif operation == 'predict':
        data = kwargs.get('data', [{}]) # Expect list of dicts or DataFrame dict
        model_id = kwargs.get('model_id', 'sim_model_reg')
        num_preds = len(data) if isinstance(data, list) else 5 # Guess number of predictions needed
        predictions = np.random.rand(num_preds) * 50 + np.random.normal(0, 5, num_preds)
        result.update({"predictions": [float(p) for p in predictions], "model_id_used": model_id})

    elif operation == 'evaluate_model':
        model_id = kwargs.get('model_id', 'sim_model_eval')
        metrics = kwargs.get('evaluation_metrics', config.PREDICTIVE_DEFAULT_EVAL_METRICS)
        scores = {}
        for metric in metrics:
            if "error" in metric: scores[metric] = float(np.random.uniform(1, 10))
            elif "r2" in metric: scores[metric] = float(np.random.uniform(0.5, 0.9))
            else: scores[metric] = float(np.random.uniform(0.1, 0.5)) # Simulate other scores
        result.update({"evaluation_scores": scores, "model_id_used": model_id})

    else:
        result["error"] = f"Unknown or unimplemented simulated operation: {operation}"

    return result
