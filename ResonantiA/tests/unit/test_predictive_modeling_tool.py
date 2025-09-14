# --- START OF FILE tests/unit/test_predictive_modeling_tool.py ---
import pytest
import pandas as pd
import numpy as np
from typing import Dict # Import Dict

# Attempt to import necessary modules with error handling
try:
    from Three_PointO_ArchE.predictive_modeling_tool import run_prediction, PREDICTIVE_LIBS_AVAILABLE # Assumes flag exists
    from Three_PointO_ArchE.config import PREDICTIVE_DEFAULT_TIMESERIES_MODEL # Use config
except ImportError:
    try:
        from ...ArchE.predictive_modeling_tool import run_prediction, PREDICTIVE_LIBS_AVAILABLE
        from ...ArchE.config import PREDICTIVE_DEFAULT_TIMESERIES_MODEL
    except ImportError:
         try:
             from ArchE.predictive_modeling_tool import run_prediction, PREDICTIVE_LIBS_AVAILABLE
             from ArchE.config import PREDICTIVE_DEFAULT_TIMESERIES_MODEL
         except ImportError:
             try:
                 from ..ArchE.predictive_modeling_tool import run_prediction, PREDICTIVE_LIBS_AVAILABLE
                 from ..ArchE.config import PREDICTIVE_DEFAULT_TIMESERIES_MODEL
             except ImportError:
                 print("Failed to import predictive_modeling_tool or config. Ensure PYTHONPATH is set or tests run correctly relative to the project structure.")
                 run_prediction, PREDICTIVE_LIBS_AVAILABLE, PREDICTIVE_DEFAULT_TIMESERIES_MODEL = None, False, "Unknown"

# Skip all tests in this module if the required libraries are not installed or tool not imported
pytestmark = pytest.mark.skipif(not PREDICTIVE_LIBS_AVAILABLE, reason="Predictive modeling libraries not installed or run_prediction not imported")

# --- Fixtures for Test Data ---
@pytest.fixture
def sample_time_series_data() -> pd.DataFrame:
    """Provides sample time series data as a DataFrame."""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    # Simple sine wave + trend + noise
    values = 10 + np.arange(100) * 0.1 + np.sin(np.arange(100) * 0.5) * 5 + np.random.normal(0, 1, 100)
    return pd.DataFrame({'timestamp': dates, 'value': values})

@pytest.fixture
def sample_tabular_data() -> pd.DataFrame:
    """Provides sample tabular data for regression/classification."""
    return pd.DataFrame({
        'feature1': np.random.rand(50),
        'feature2': np.random.randint(0, 10, 50),
        'target': 3 * np.random.rand(50) + 2 * np.random.randint(0, 10, 50) + np.random.normal(0, 0.5, 50)
    })

# --- Tests for 'train_model' Operation (Conceptual) ---
@pytest.mark.skipif(run_prediction is None, reason="run_prediction not imported")
def test_train_timeseries_model_success(sample_time_series_data):
    """Test successful training of a time series model (e.g., ARIMA)."""
    # Assumes run_prediction is implemented using statsmodels/pmdarima etc.
    inputs = {
        "operation": "train_model",
        "data": sample_time_series_data.to_dict(orient='list'), # Pass data as dict
        "model_type": "ARIMA", # Or config.PREDICTIVE_DEFAULT_TIMESERIES_MODEL
        "target": "value", # Corrected from target_column
        "timestamp_column": "timestamp", # Specify timestamp column
        "model_id": "test_arima_model"
        # Add ARIMA order if needed: "model_params": {"order": (1,1,0)}
    }
    # Skip if the run_prediction function itself failed to import
    if run_prediction is None:
        pytest.skip("run_prediction function not available")

    result = run_prediction(**inputs) # Use **inputs to pass dict as kwargs

    assert result is not None
    assert isinstance(result, dict)
    assert result.get("error") is None
    assert result.get("model_id") is not None # Should return a model ID
    # Add check for evaluation score if implementation returns one
    # assert result.get("evaluation_score") is not None

    # CRITICAL: Check IAR Reflection
    assert "reflection" in result
    reflection = result["reflection"]
    assert isinstance(reflection, dict)
    assert reflection["status"] == "Success" # Assuming successful training
    assert reflection["confidence"] is not None and 0 <= reflection["confidence"] <= 1.0
    # Check for potential_issues - should be None or empty list for success
    assert reflection.get("potential_issues") is None or not reflection["potential_issues"]
    assert reflection["raw_output_preview"] is not None

# Add tests for training failure (bad data, invalid params), different model types...

# --- Tests for 'forecast_future_states' Operation (Conceptual) ---
@pytest.mark.skipif(run_prediction is None, reason="run_prediction not imported")
def test_forecast_success(sample_time_series_data):
    """Test successful forecasting using a trained model."""
    # 1. Train a model first
    training_model_id = "tests_forecast_test_model_" + pd.Timestamp.now().strftime("%Y%m%d%H%M%S%f")
    train_inputs = {
        "operation": "train_model",
        "data": sample_time_series_data.to_dict(orient='list'),
        "model_type": "ARIMA",
        "target": "value",
        "timestamp_column": "timestamp",
        "model_id": training_model_id 
    }
    train_result = run_prediction(**train_inputs)
    assert train_result.get("error") is None, f"Training failed: {train_result.get('error')}"
    assert train_result.get("model_id") == training_model_id, "Model ID from training mismatch"

    # 2. Forecast using the trained model
    steps_to_forecast = 10
    forecast_inputs = {
        "operation": "forecast_future_states",
        "model_id": training_model_id, # Use the ID from the training step
        "steps_to_forecast": steps_to_forecast,
    }
    # Skip if the run_prediction function itself failed to import
    if run_prediction is None:
        pytest.skip("run_prediction function not available")

    forecast_result = run_prediction(**forecast_inputs)

    assert forecast_result is not None
    assert forecast_result.get("error") is None
    assert "forecast" in forecast_result
    assert isinstance(forecast_result["forecast"], list)
    assert len(forecast_result["forecast"]) == steps_to_forecast
    assert "confidence_intervals" in forecast_result # Check if CIs are returned
    assert isinstance(forecast_result["confidence_intervals"], list)
    assert len(forecast_result["confidence_intervals"]) == steps_to_forecast

    # Check IAR
    assert "reflection" in forecast_result
    reflection = forecast_result["reflection"]
    assert reflection["status"] == "Success"
    assert reflection["confidence"] is not None

# Add tests for forecasting failure (unknown model_id, invalid steps)...

# --- Tests for 'predict' Operation (Conceptual - for non-timeseries) ---
# Similar structure: train/load model, call predict, check output and IAR

# --- Tests for 'evaluate_model' Operation (Conceptual) ---
# Similar structure: train/load model, call evaluate, check metrics and IAR

# --- Combined Scenario Test ---
@pytest.mark.skipif(run_prediction is None, reason="run_prediction not imported")
def test_train_evaluate_forecast_flow(sample_time_series_data):
    """Tests a combined flow: Train -> Evaluate -> Forecast."""
    if run_prediction is None: # Should be caught by pytestmark, but good practice
        pytest.skip("run_prediction function not available")

    full_data = sample_time_series_data
    train_size = int(len(full_data) * 0.8)
    train_df = full_data.iloc[:train_size]
    evaluate_df = full_data.iloc[train_size:]

    model_id_combo = "test_combo_model_" + pd.Timestamp.now().strftime("%Y%m%d%H%M%S%f")

    # 1. Train Model
    train_inputs = {
        "operation": "train_model",
        "data": train_df.to_dict(orient='list'),
        "model_type": "ARIMA",
        "target": "value",
        "timestamp_column": "timestamp",
        "model_id": model_id_combo
    }
    train_result = run_prediction(**train_inputs)
    assert train_result.get("error") is None, f"Combined Test - Training failed: {train_result.get('error')}"
    assert train_result.get("model_id") == model_id_combo
    assert "reflection" in train_result
    assert train_result["reflection"]["status"] == "Success"

    # 2. Evaluate Model
    evaluate_inputs = {
        "operation": "evaluate_model",
        "model_id": model_id_combo,
        "data": evaluate_df.to_dict(orient='list'), # This is the actual_data for evaluation
        "target": "value",
        "timestamp_column": "timestamp",
        "evaluation_metrics": ["mean_absolute_error", "mean_squared_error"]
    }
    eval_result = run_prediction(**evaluate_inputs)
    assert eval_result.get("error") is None, f"Combined Test - Evaluation failed: {eval_result.get('error')}"
    assert "evaluation_scores" in eval_result
    assert "mean_absolute_error" in eval_result["evaluation_scores"]
    assert "mean_squared_error" in eval_result["evaluation_scores"]
    assert "reflection" in eval_result
    assert eval_result["reflection"]["status"] == "Success"

    # 3. Forecast Future States
    steps_to_forecast = 15
    forecast_inputs = {
        "operation": "forecast_future_states",
        "model_id": model_id_combo,
        "steps_to_forecast": steps_to_forecast
    }
    forecast_result = run_prediction(**forecast_inputs)
    assert forecast_result.get("error") is None, f"Combined Test - Forecasting failed: {forecast_result.get('error')}"
    assert "forecast" in forecast_result
    assert isinstance(forecast_result["forecast"], list)
    assert len(forecast_result["forecast"]) == steps_to_forecast
    assert "reflection" in forecast_result
    assert forecast_result["reflection"]["status"] == "Success"

# --- END OF FILE tests/unit/test_predictive_modeling_tool.py --- 