#!/usr/bin/env python3
import json
import logging
import sys
from pathlib import Path
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Mock Action Definitions (Copied from run_workflow.py) ---
def mock_action_a(inputs):
    """Mock action A implementation"""
    return {
        "out_a": f"Processed: {inputs.get('in_a', 'No input')}",
        "reflection": {
            "status": "Success",
            "confidence": 0.9,
            "summary": "Action A completed successfully",
            "alignment_check": True,
            "potential_issues": [],
            "raw_output_preview": "Sample output from action A"
        }
    }

def mock_action_b(inputs):
    """Mock action B implementation"""
    return {
        "out_b": f"Processed B: {inputs.get('in_b', 'No input')}",
        "reflection": {
            "status": "Success",
            "confidence": 0.85,
            "summary": "Action B completed successfully",
            "alignment_check": True,
            "potential_issues": [],
            "raw_output_preview": "Sample output from action B"
        }
    }

def mock_action_c(inputs):
    """Mock action C implementation"""
    return {
        "out_c": "Conditional task C executed",
        "reflection": {
            "status": "Success",
            "confidence": 0.95,
            "summary": "Action C completed successfully",
            "alignment_check": True,
            "potential_issues": [],
            "raw_output_preview": "Sample output from action C"
        }
    }
# --- End Mock Action Definitions ---

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_workflow_with_recovery.py <workflow_path>")
        sys.exit(1)
    
    workflow_path = sys.argv[1]
    if not Path(workflow_path).exists():
        logger.error(f"Workflow file not found: {workflow_path}")
        sys.exit(1)
    
    try:
        # Initialize workflow engine
        engine = IARCompliantWorkflowEngine()
        
        # Register mock actions with the engine
        engine.register_action("mock_action_a", mock_action_a)
        engine.register_action("mock_action_b", mock_action_b)
        engine.register_action("mock_action_c", mock_action_c)

        # Load the workflow definition from the file
        logger.info(f"Loading workflow definition from: {workflow_path}")
        workflow_definition = engine.load_workflow(workflow_path)
        
        # Execute workflow with recovery support
        logger.info("Executing workflow with recovery support...")
        results = engine.execute_workflow(workflow_definition)
        
        # Save results
        output_path = Path("outputs") / f"workflow_results_{results.get('run_id', 'unknown_run')}.json"
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Workflow execution completed. Results saved to: {output_path}")
        
        # Get resonance dashboard
        dashboard = engine.get_resonance_dashboard()
        logger.info("Resonance Dashboard:")
        logger.info(json.dumps(dashboard, indent=2))
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 