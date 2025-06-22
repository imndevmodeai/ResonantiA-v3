import json
import logging
from workflow_manager import WorkflowManager
from Three_PointO_ArchE.tools.code_executor import execute_code
from Three_PointO_ArchE.tools.llm_tool import generate_text_llm
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Runs the agentic search workflow using the WorkflowManager.
    """
    if len(sys.argv) < 2:
        print("Usage: python run_agentic_workflow.py <initial_context_json_string>")
        sys.exit(1)

    initial_context_str = sys.argv[1]

    try:
        initial_context = json.loads(initial_context_str)
    except json.JSONDecodeError:
        logger.error("Invalid JSON provided for initial context.")
        sys.exit(1)

    # Instantiate the manager and register the capabilities our workflow needs
    manager = WorkflowManager()
    manager.register_capability("execute_code", execute_code)
    manager.register_capability("generate_text_llm", generate_text_llm)

    # Execute the workflow
    logger.info("Starting the Direct Agentic Search Workflow...")
    results = manager.execute_json_workflow('workflows/direct_agentic_search.json', initial_context)
    
    # Save results
    with open('workflow_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("Workflow execution completed. Results saved to workflow_results.json")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main() 