import json
import logging
import sys
import os

# Add the current directory to Python path so we can import Three_PointO_ArchE
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.logging_config import setup_logging

def main():
    """
    Simple test to isolate the JSON parsing issue.
    """
    setup_logging()
    logger = logging.getLogger("SimpleTest")
    logger.info("--- Starting Simple Genesis Test ---")

    workflow_name = "simple_genesis_test.json"
    context_file = "simple_test_context.json"

    try:
        # 1. Load the initial context from the JSON file
        logger.info(f"Loading context from: {context_file}")
        with open(context_file, 'r', encoding='utf-8') as f:
            initial_context = json.load(f)
        logger.info("Context loaded successfully.")

        # 2. Instantiate the Workflow Engine
        logger.info("Instantiating IARCompliantWorkflowEngine...")
        engine = IARCompliantWorkflowEngine()
        logger.info("Engine instantiated successfully.")

        # 3. Run the workflow
        logger.info(f"Executing workflow: {workflow_name}")
        final_result = engine.run_workflow(workflow_name, initial_context)
        logger.info("Workflow execution finished.")

        # 4. Print the final summary
        print("\n--- SIMPLE TEST FINAL RESULT ---")
        print(json.dumps(final_result, indent=2, default=str))
        print("-----------------------------------\n")

        if final_result.get("workflow_status") != "Completed Successfully":
            logger.error("Simple test workflow did not complete successfully.")
            sys.exit(1)
        else:
            logger.info("Simple test workflow completed successfully.")

    except Exception as e:
        logger.critical(f"An unexpected error occurred during the simple test: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()