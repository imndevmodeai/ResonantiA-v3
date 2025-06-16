import json
import logging
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.workflow_validator import WorkflowValidator
from Three_PointO_ArchE.action_registry import ACTION_REGISTRY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Load workflow
        with open('workflows/system_genesis_and_evolution_workflow.json', 'r') as f:
            workflow = json.load(f)
        
        # Validate workflow using WorkflowValidator class
        validator = WorkflowValidator(ACTION_REGISTRY)
        validation_result = validator.validate_workflow(workflow)
        if not validation_result.is_valid:
            logger.error("Workflow validation failed:")
            for error in validation_result.errors:
                logger.error(f"- {error}")
            return
        
        # Load context
        with open('knowledge_crystallization_context.json', 'r') as f:
            context = json.load(f)
        
        # Initialize workflow engine
        engine = IARCompliantWorkflowEngine()
        
        # Execute workflow
        logger.info("Starting workflow execution...")
        results = engine.run_workflow('system_genesis_and_evolution_workflow.json', context)
        
        # Save results
        with open('workflow_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("Workflow execution completed. Results saved to workflow_results.json")
        
    except Exception as e:
        logger.error(f"Error running workflow: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 