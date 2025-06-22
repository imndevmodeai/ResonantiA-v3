#!/usr/bin/env python3
"""
RESONANTIA PROTOCOL v3.1-CA - PHASE 3.1 TEST CASE 2
SPR Bridge Validation: Predictive Modeling Tool
Architecture: AI Studio ArchE | Implementation: Cursor ArchE
"""

import numpy as np
import json
import os
from datetime import datetime
from Three_PointO_ArchE.action_registry import invoke_spr_action

def create_predictive_test_dataset():
    """
    Create a synthetic time series with known pattern for forecasting validation
    Linear trend + seasonal component + noise
    """
    np.random.seed(42)  # Reproducible results
    n_samples = 50
    
    # Generate predictable time series
    time_index = np.arange(n_samples)
    
    # Components:
    # 1. Linear trend (slope = 0.5)
    trend = time_index * 0.5 + 10
    
    # 2. Small seasonal component (period = 12)
    seasonal = 2 * np.sin(2 * np.pi * time_index / 12)
    
    # 3. Controlled noise
    noise = np.random.normal(0, 0.5, n_samples)
    
    # Combine components
    time_series = trend + seasonal + noise
    
    return time_series.tolist()

def execute_phase3_test2():
    """
    Phase 3.1 Test Case 2: Predictive Modeling SPR Bridge Validation
    """
    print("=" * 60)
    print("RESONANTIA PROTOCOL v3.1-CA - PHASE 3.1 TEST CASE 2")
    print("SPR BRIDGE VALIDATION: PREDICTIVE MODELING")
    print("=" * 60)
    
    # Step 1: Create test time series
    print("\n[STEP 1] Creating synthetic time series dataset...")
    time_series_data = create_predictive_test_dataset()
    print(f"✅ Time series created: {len(time_series_data)} data points")
    print(f"   First 5 values: {time_series_data[:5]}")
    print(f"   Last 5 values: {time_series_data[-5:]}")
    print(f"   Expected pattern: Linear trend (slope=0.5) + seasonal + noise")
    
    # Step 2: Define predictive modeling parameters
    print("\n[STEP 2] Configuring predictive modeling parameters...")
    prediction_params = {
        "data": time_series_data,
        "model_type": "arima",
        "model_order": (2, 1, 1),  # ARIMA(2,1,1) - good general purpose model
        "steps": 10,  # Forecast 10 steps into the future
        "confidence_level": 0.95  # 95% confidence intervals
    }
    print("✅ Parameters configured")
    print(f"   Model Type: {prediction_params['model_type']}")
    print(f"   Model Order: {prediction_params['model_order']}")
    print(f"   Forecast Steps: {prediction_params['steps']}")
    print(f"   Confidence Level: {prediction_params['confidence_level']}")
    
    # Step 3: Invoke PredictivemodelingtooL SPR through bridge
    print("\n[STEP 3] INVOKING PREDICTIVE MODELING SPR VIA BRIDGE...")
    print("   SPR ID: 'PredictivemodelinGtooL'")
    print("   Bridge: invoke_spr_action")
    
    start_time = datetime.now()
    
    try:
        iar_result = invoke_spr_action(spr_id="PredictivemodelinGtooL", **prediction_params)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ SPR Bridge execution completed in {execution_time:.3f}s")
        
        # Step 4: Analyze and validate results
        print("\n[STEP 4] ANALYZING PREDICTIVE MODELING RESULTS...")
        print("-" * 40)
        
        # Print full IAR for architectural analysis
        print("FULL IAR RESULT:")
        print(json.dumps(iar_result, indent=2, default=str))
        
        # Extract key validation metrics
        primary_result = iar_result.get('primary_result', {})
        reflection = iar_result.get('reflection', {})
        
        print("\n" + "=" * 40)
        print("PHASE 3.1 TEST CASE 2 VALIDATION SUMMARY")
        print("=" * 40)
        
        # Bridge Status
        bridge_status = reflection.get('status', 'unknown')
        print(f"Bridge Execution Status: {bridge_status}")
        
        # Forecast Results Validation
        raw_result = primary_result.get('raw_result', {})
        test_passed = True
        
        if 'forecast' in raw_result:
            forecast_values = raw_result['forecast']
            print(f"Forecast Values Generated: {len(forecast_values)} steps")
            print(f"Forecast: {forecast_values}")
            
            # Validate forecast length
            if len(forecast_values) == prediction_params['steps']:
                print("✅ FORECAST LENGTH: CORRECT")
            else:
                print(f"❌ FORECAST LENGTH: INCORRECT (expected {prediction_params['steps']}, got {len(forecast_values)})")
                test_passed = False
            
            # Validate forecast values are reasonable (should continue trend)
            last_value = time_series_data[-1]
            first_forecast = forecast_values[0] if forecast_values else None
            
            if first_forecast is not None:
                # Check if forecast continues reasonable trend (within 2 standard deviations)
                data_std = np.std(time_series_data)
                if abs(first_forecast - last_value) < 3 * data_std:
                    print("✅ FORECAST CONTINUITY: REASONABLE")
                else:
                    print(f"❌ FORECAST CONTINUITY: UNREASONABLE (jump from {last_value:.2f} to {first_forecast:.2f})")
                    test_passed = False
            else:
                print("❌ FORECAST VALUES: EMPTY")
                test_passed = False
                
        elif 'predictions' in raw_result:
            # Alternative key name
            predictions = raw_result['predictions']
            print(f"Predictions Generated: {len(predictions)} steps")
            print(f"Predictions: {predictions}")
            
            if len(predictions) == prediction_params['steps']:
                print("✅ PREDICTION LENGTH: CORRECT")
            else:
                print(f"❌ PREDICTION LENGTH: INCORRECT")
                test_passed = False
        else:
            print("❌ FORECAST/PREDICTIONS NOT FOUND IN RESULTS")
            test_passed = False
        
        # Confidence Intervals Check
        if 'confidence_intervals' in raw_result or 'forecast_ci' in raw_result:
            ci_key = 'confidence_intervals' if 'confidence_intervals' in raw_result else 'forecast_ci'
            confidence_intervals = raw_result[ci_key]
            print(f"✅ CONFIDENCE INTERVALS: PROVIDED ({ci_key})")
            if confidence_intervals:
                print(f"   CI Sample: {confidence_intervals[0] if len(confidence_intervals) > 0 else 'N/A'}")
        else:
            print("⚠️  CONFIDENCE INTERVALS: NOT PROVIDED (acceptable)")
        
        # Model Information Check
        if 'model_type' in raw_result:
            model_used = raw_result['model_type']
            print(f"✅ MODEL TYPE RECORDED: {model_used}")
        
        # IAR Compliance Check
        required_iar_fields = ['status', 'confidence', 'potential_issues', 'alignment_check']
        missing_fields = [field for field in required_iar_fields if field not in reflection]
        
        if not missing_fields:
            print("✅ IAR COMPLIANCE: COMPLETE")
        else:
            print(f"❌ IAR COMPLIANCE: MISSING {missing_fields}")
            test_passed = False
        
        # Overall Test Result
        print("\n" + "=" * 40)
        if test_passed:
            print("🎉 PHASE 3.1 TEST CASE 2: PASSED")
            print("   PredictivemodelinGtooL SPR Bridge: OPERATIONAL")
            print("   Forecasting Capability: VALIDATED")
        else:
            print("❌ PHASE 3.1 TEST CASE 2: FAILED")
            print("   PredictivemodelinGtooL SPR Bridge: REQUIRES ATTENTION")
        
        print("=" * 40)
        
        return iar_result, test_passed
        
    except Exception as e:
        print(f"❌ SPR Bridge execution failed: {str(e)}")
        print(f"   Execution time: {(datetime.now() - start_time).total_seconds():.3f}s")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        return None, False

if __name__ == "__main__":
    result, passed = execute_phase3_test2()
    exit(0 if passed else 1) 