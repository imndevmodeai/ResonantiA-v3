#!/usr/bin/env python3
"""
Full ArchE Genesis Test Runner

This script tests if ArchE can create a complete, independent instance of itself
from Living Specifications using Autopoietic System Genesis.

The test generates multiple core components:
- workflow_engine.py
- llm_tool.py  
- spr_manager.py
- action_registry.py
- config.py

All generated code is isolated in the 'arche_genesis_test/' directory
and does not affect the production ArchE codebase.
"""

import json
import logging
import sys
import os
import time

# Add the current directory to Python path so we can import Three_PointO_ArchE
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.logging_config import setup_logging

def main():
    """
    Run the Full ArchE Genesis Test to demonstrate Autopoietic System Genesis.
    """
    setup_logging()
    logger = logging.getLogger("FullArchEGenesisTest")
    
    print("🧬 " + "="*70)
    print("🧬 FULL ARCHE GENESIS TEST - AUTOPOIETIC SYSTEM GENESIS")
    print("🧬 " + "="*70)
    print()
    print("🎯 OBJECTIVE: Generate a complete, independent ArchE instance")
    print("📋 COMPONENTS: workflow_engine, llm_tool, spr_manager, action_registry, config")
    print("🔒 ISOLATION: All code generated in 'arche_genesis_test/' directory")
    print("⚡ MODEL: Gemini 2.5 Pro (latest reasoning model)")
    print()
    
    workflow_name = "full_arche_genesis_test.json"
    context_file = "full_arche_genesis_context.json"

    try:
        # 1. Load the initial context from the JSON file
        logger.info(f"Loading context from: {context_file}")
        with open(context_file, 'r', encoding='utf-8') as f:
            initial_context = json.load(f)
        logger.info("✅ Context loaded successfully.")
        print(f"📄 Context loaded from: {context_file}")

        # 2. Initialize the workflow engine
        logger.info("Initializing IARCompliantWorkflowEngine...")
        engine = IARCompliantWorkflowEngine()
        logger.info("✅ Workflow engine initialized.")
        print("🔧 Workflow engine initialized")

        # 3. Run the workflow
        logger.info(f"Starting Full ArchE Genesis workflow: {workflow_name}")
        print(f"🚀 Starting workflow: {workflow_name}")
        print()
        
        start_time = time.time()
        
        result = engine.run_workflow(
            workflow_name=workflow_name,
            initial_context=initial_context
        )
        
        end_time = time.time()
        execution_time = end_time - start_time

        # 4. Report results
        logger.info("Full ArchE Genesis Test completed.")
        print()
        print("🎉 " + "="*70)
        print("🎉 FULL ARCHE GENESIS TEST COMPLETED!")
        print("🎉 " + "="*70)
        print()
        print(f"⏱️  Total Execution Time: {execution_time:.2f} seconds")
        print(f"📊 Workflow Result Status: {result.get('status', 'Unknown')}")
        print()
        
        # Check if the arche_genesis_test directory was created
        if os.path.exists("arche_genesis_test"):
            print("📁 Generated Files:")
            for root, dirs, files in os.walk("arche_genesis_test"):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    print(f"   ✅ {file_path} ({file_size:,} bytes)")
            print()
            
            print("🧪 NEXT STEPS:")
            print("   1. Inspect the generated code in 'arche_genesis_test/'")
            print("   2. Test the generated ArchE instance independently")
            print("   3. Compare with production ArchE for 'As Above, So Below' alignment")
            print()
            print("🔒 ISOLATION CONFIRMED: Production ArchE codebase unaffected")
        else:
            print("❌ ERROR: 'arche_genesis_test' directory was not created")
            print("   The workflow may have failed during execution")

        print()
        print("📋 FULL RESULT DETAILS:")
        print(json.dumps(result, indent=2))

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"❌ ERROR: File not found - {e}")
        print("   Please ensure all required files exist:")
        print(f"   - workflows/{workflow_name}")
        print(f"   - {context_file}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error during Full ArchE Genesis Test: {e}", exc_info=True)
        print(f"❌ CRITICAL ERROR: {e}")
        print("   Check the logs for detailed error information")
        sys.exit(1)

if __name__ == "__main__":
    main()