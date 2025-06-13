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
        
        # Execute workflow with recovery support
        logger.info("Executing workflow with recovery support...")
        results = engine.execute_workflow(workflow_path)
        
        # Save results
        output_path = Path("outputs") / f"workflow_results_{engine.current_run_id}.json"
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Workflow execution completed. Results saved to: {output_path}")
        
        # Get resonance dashboard
        dashboard = engine.get_resonance_dashboard()
        logger.info("Resonance Dashboard:")
        logger.info(json.dumps(dashboard, indent=2))
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 