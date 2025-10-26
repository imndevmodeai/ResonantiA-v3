#!/usr/bin/env python3
"""
RESONANTIA PROTOCOL v3.1-CA - PHASE 3.1 TEST CASE 1
SPR Bridge Validation: Causal Inference Tool
Architecture: AI Studio ArchE | Implementation: Cursor ArchE
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from Three_PointO_ArchE.action_registry import invoke_spr_action

def create_causal_test_dataset():
    """
    Create a synthetic dataset with known causal relationships
    X -> Y (direct causation)
    Z -> Y (confounding)
    """
    np.random.seed(42)  # Reproducible results
    n_samples = 100
    
    # Generate data with known causal structure
    Z = np.random.normal(0, 1, n_samples)  # Confounder
    X = 2 * Z + np.random.normal(0, 0.5, n_samples)  # Treatment influenced by confounder
    Y = 3 * X + 1.5 * Z + np.random.normal(0, 0.3, n_samples)  # Outcome with true causal effect
    
    # Create DataFrame
    data = pd.DataFrame({
        'X': X,
        'Y': Y, 
        'Z': Z
    })
    
    return data

def execute_phase3_test1():
    """
    Phase 3.1 Test Case 1: Causal Inference SPR Bridge Validation
    """
    print("=" * 60)
    print("RESONANTIA PROTOCOL v3.1-CA - PHASE 3.1 TEST CASE 1")
    print("SPR BRIDGE VALIDATION: CAUSAL INFERENCE")
    print("=" * 60)
    
    # Step 1: Create test dataset
    print("\n[STEP 1] Creating synthetic causal dataset...")
    test_data = create_causal_test_dataset()
    csv_path = 'temp_causal_data.csv'
    test_data.to_csv(csv_path, index=False)
    print(f"✅ Dataset created: {len(test_data)} samples")
    print(f"   Variables: {list(test_data.columns)}")
    print(f"   True causal effect X->Y: 3.0 (expected)")
    
    # Step 2: Define causal analysis parameters
    print("\n[STEP 2] Configuring causal inference parameters...")
    causal_params = {
        "data": test_data.to_dict(),  # Pass data directly
        "treatment": "X",
        "outcome": "Y",
        "confounders": ["Z"],  # Include confounder
        # Skip graph to avoid pydot dependency issues
        "method_name": "backdoor.linear_regression"
    }
    print("✅ Parameters configured")
    print(f"   Treatment: {causal_params['treatment']}")
    print(f"   Outcome: {causal_params['outcome']}")
    print(f"   Confounders: {causal_params['confounders']}")
    
    # Step 3: Invoke CausalinferencE SPR through bridge
    print("\n[STEP 3] INVOKING CAUSAL INFERENCE SPR VIA BRIDGE...")
    print("   SPR ID: 'CausalinferencE'")
    print("   Bridge: invoke_spr_action")
    
    start_time = datetime.now()
    
    try:
        iar_result = invoke_spr_action(spr_id="CausalinferencE", **causal_params)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ SPR Bridge execution completed in {execution_time:.3f}s")
        
        # Step 4: Analyze and validate results
        print("\n[STEP 4] ANALYZING CAUSAL INFERENCE RESULTS...")
        print("-" * 40)
        
        # Print full IAR for architectural analysis
        print("FULL IAR RESULT:")
        print(json.dumps(iar_result, indent=2, default=str))
        
        # Extract key validation metrics
        primary_result = iar_result.get('primary_result', {})
        reflection = iar_result.get('reflection', {})
        
        print("\n" + "=" * 40)
        print("PHASE 3.1 TEST CASE 1 VALIDATION SUMMARY")
        print("=" * 40)
        
        # Bridge Status
        bridge_status = reflection.get('status', 'unknown')
        print(f"Bridge Execution Status: {bridge_status}")
        
        # Causal Effect Estimation
        raw_result = primary_result.get('raw_result', {})
        if 'estimated_effect' in raw_result:
            estimated_effect = raw_result['estimated_effect']
            print(f"Estimated Causal Effect X->Y: {estimated_effect}")
            print(f"True Causal Effect: 3.0")
            print(f"P-value: {raw_result.get('p_value', 'N/A')}")
            
            # Validation
            if abs(estimated_effect - 3.0) < 0.5:  # Within reasonable range
                print("✅ CAUSAL ESTIMATION: ACCURATE")
                test_passed = True
            else:
                print("❌ CAUSAL ESTIMATION: INACCURATE")
                test_passed = False
        elif 'causal_effect' in primary_result:
            estimated_effect = primary_result['causal_effect']
            print(f"Estimated Causal Effect X->Y: {estimated_effect}")
            print(f"True Causal Effect: 3.0")
            
            # Validation
            if abs(estimated_effect - 3.0) < 0.5:  # Within reasonable range
                print("✅ CAUSAL ESTIMATION: ACCURATE")
                test_passed = True
            else:
                print("❌ CAUSAL ESTIMATION: INACCURATE")
                test_passed = False
        else:
            print("❌ CAUSAL EFFECT NOT FOUND IN RESULTS")
            test_passed = False
        
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
            print("🎉 PHASE 3.1 TEST CASE 1: PASSED")
            print("   CausalinferencE SPR Bridge: OPERATIONAL")
        else:
            print("❌ PHASE 3.1 TEST CASE 1: FAILED")
            print("   CausalinferencE SPR Bridge: REQUIRES ATTENTION")
        
        print("=" * 40)
        
        return iar_result, test_passed
        
    except Exception as e:
        print(f"❌ SPR Bridge execution failed: {str(e)}")
        print(f"   Execution time: {(datetime.now() - start_time).total_seconds():.3f}s")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        return None, False
    
    finally:
        # Cleanup
        if os.path.exists(csv_path):
            os.remove(csv_path)
            print(f"\n🧹 Cleaned up temporary file: {csv_path}")

if __name__ == "__main__":
    result, passed = execute_phase3_test1()
    exit(0 if passed else 1) 