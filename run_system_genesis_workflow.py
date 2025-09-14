import json
import logging
from Three_PointO_ArchE.workflow_manager import WorkflowManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # The WorkflowManager now handles validation and capability registration internally.
        # For this to work, we need to register the capabilities the genesis workflow uses.
        
        # In a real scenario, these handlers would be more sophisticated.
        def perform_system_genesis_action(**kwargs):
            logger.info(f"Performing system genesis action with params: {kwargs}")
            return {"status": "success", "details": f"Executed operation {kwargs.get('operation')}"}

        def display_output(**kwargs):
            logger.info("--- DISPLAY OUTPUT ---")
            logger.info(kwargs.get('content', 'No content to display.'))
            logger.info("----------------------")
            return {"status": "success"}

        # Initialize workflow manager and register capabilities
        manager = WorkflowManager()
        manager.register_capability("perform_system_genesis_action", perform_system_genesis_action)
        manager.register_capability("display_output", display_output)
        
        # Load context if needed (though the new engine doesn't use it in the same way)
        # with open('knowledge_crystallization_context.json', 'r') as f:
        #     context = json.load(f)
        
        # Execute workflow
        logger.info("Starting system genesis workflow execution with the unified WorkflowManager...")
        results = manager.execute_json_workflow('workflows/system_genesis_and_evolution_workflow.json')
        
        # Save results
        with open('workflow_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("Workflow execution completed. Results saved to workflow_results.json")
        
    except Exception as e:
        logger.error(f"Error running workflow: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 