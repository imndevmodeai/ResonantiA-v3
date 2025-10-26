import logging
from typing import Dict, Any
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine as WorkflowEngine
from Three_PointO_ArchE.spr_manager import SPRManager
from Three_PointO_ArchE import config
from Three_PointO_ArchE.playbook_orchestrator import run_playbook as execute_playbook
from .config import configure_logging
import logging
import os

# Configure logging for this module
configure_logging()
logger = logging.getLogger(__name__)

def run_strategic_intelligence_workflow():
    """
    A meta-tool that executes the strategic intelligence workflow.
    """
    logger.info("Executing the Strategic Intelligence Workflow Playbook.")
    # Assuming the playbook is in the 'workflows' directory relative to the project root
    # A more robust solution would use the project root from config.
    playbook_path = os.path.join(os.path.dirname(__file__), '..', 'workflows', 'strategic_intelligence_workflow.json')
    
    if not os.path.exists(playbook_path):
        error_msg = f"Playbook not found at path: {playbook_path}"
        logger.critical(error_msg)
        return {"status": "error", "message": error_msg}
        
    return execute_playbook(playbook_path)

def run_playbook(playbook_name: str):
    """
    A generic meta-tool that executes a specified workflow playbook.

    Args:
        playbook_name (str): The filename of the playbook in the /workflows directory.
                             Example: 'asymmetric_warfare_analysis.json'
    """
    logger.info(f"Executing the '{playbook_name}' Playbook.")
    playbook_path = os.path.join(os.path.dirname(__file__), '..', 'workflows', playbook_name)

    if not os.path.exists(playbook_path):
        error_msg = f"Playbook not found at path: {playbook_path}"
        logger.critical(error_msg)
        return {"status": "error", "message": error_msg}

    return execute_playbook(playbook_path)
