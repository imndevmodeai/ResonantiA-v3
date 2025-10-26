#!/usr/bin/env python3
"""
Semiconductor Shortage Analysis using ArchE's Predictive Modeling and Causal Inference Tools
"""

import sys
import os
import subprocess
import json
from datetime import datetime

def run_semiconductor_analysis():
    """Run the comprehensive semiconductor shortage analysis"""
    
    print("🔬 ARCH E SEMICONDUCTOR SHORTAGE ANALYSIS")
    print("=" * 50)
    print("Using Predictive Modeling & Causal Inference Tools")
    print(f"Analysis Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Change to the correct directory
    os.chdir('/media/newbu/3626C55326C514B1/Happier')
    
    # Run the specialized workflow
    command = [
        'python3', 'execute_playbook.py', 
        'semiconductor_analysis_workflow.json',
        '--context', json.dumps({
            'goal': 'Analyze 2020-2023 semiconductor shortage using predictive modeling and causal inference',
            'constraints': {'analysis_depth': 'comprehensive', 'time_horizon': '12_months'},
            'desired_outputs': ['predictive_forecasts', 'causal_relationships', 'policy_recommendations']
        })
    ]
    
    try:
        print("🚀 Executing ArchE's Predictive Modeling & Causal Inference Analysis...")
        print("-" * 50)
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ ANALYSIS COMPLETED SUCCESSFULLY")
            print("-" * 50)
            print(result.stdout)
        else:
            print("❌ ANALYSIS ENCOUNTERED ERRORS")
            print("-" * 50)
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Analysis timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
    
    print("\n" + "=" * 50)
    print("SEMICONDUCTOR ANALYSIS COMPLETE")

if __name__ == "__main__":
    run_semiconductor_analysis()

