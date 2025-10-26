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
    Executes the autopoietic genesis workflow by directly invoking the
    workflow engine, bypassing the fragile command-line JSON parsing.
    """
    setup_logging()
    logger = logging.getLogger("GenesisRunner")
    logger.info("--- Starting Autopoietic Genesis Test via Direct Invocation ---")

    # Prefer the autopoietic workflow if present; otherwise fall back to a known available one
    candidate_paths = [
        os.path.join("workflows", "autopoietic_genesis_v4.json"),
        os.path.join("workflows", "autopoietic_genesis_v3.json"),
        os.path.join("workflows", "system_genesis_and_evolution_workflow.json"),
        os.path.join("workflows", "basic_analysis.json"),
    ]
    workflow_name = None
    for p in candidate_paths:
        if os.path.exists(p):
            workflow_name = p
            break
    if workflow_name is None:
        raise FileNotFoundError("No suitable workflow file found in the 'workflows/' directory.")
    context_file = "autopoiesis_context.json"

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
        print("\n--- GENESIS WORKFLOW FINAL RESULT ---")
        print(json.dumps(final_result, indent=2, default=str))
        print("-------------------------------------\n")

        if final_result.get("workflow_status") != "Completed Successfully":
            logger.error("Genesis workflow did not complete successfully.")
            sys.exit(1)
        else:
            logger.info("Genesis workflow completed successfully.")
            # Verify file creation
            target_file = f"autopoiesis_test/{initial_context.get('target_filename')}"
            if os.path.exists(target_file):
                logger.info(f"SUCCESS: Verified that the target file '{target_file}' was created.")
            else:
                logger.error(f"FAILURE: Target file '{target_file}' was NOT created.")
                sys.exit(1)


    except FileNotFoundError as e:
        logger.critical(f"A required file was not found: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred during the genesis run: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
