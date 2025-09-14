
#!/usr/bin/env python3
"""
Autopoietic Mandate System

This system enforces the mandatory use of the Autopoietic System Genesis workflow
for all system development and evolution. It ensures that the system builds itself
from its own specification, solving the Execution paradoX through ultimate
Implementation resonancE.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class AutopoieticMandateSystem:
    """
    Enforces the mandatory use of Autopoietic System Genesis for all system development.
    This is the ultimate solution to the Execution paradoX.
    """
    
    def __init__(self, keyholder_authority: str = "keyy=('IMnDEVmode')"):
        self.keyholder_authority = keyholder_authority
        self.mandate_file = "autopoietic_mandate_status.json"
        self.workflow_path = "workflows/autopoietic_genesis_protocol.json"
        self.protocol_file = "ResonantiA_Protocol_v3.1-CA.md"
        self.output_directory = "Three_PointO_ArchE"
        
    def validate_keyholder_authority(self) -> bool:
        """Validate that the current operation is authorized by the Keyholder."""
        return self.keyholder_authority == "keyy=('IMnDEVmode')"
    
    def check_mandate_status(self) -> Dict[str, Any]:
        """Check the current status of the Autopoietic mandate."""
        try:
            if os.path.exists(self.mandate_file):
                with open(self.mandate_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    "mandate_active": False,
                    "last_genesis": None,
                    "genesis_count": 0,
                    "mandate_enforced": False
                }
        except Exception as e:
            logger.error(f"Error checking mandate status: {e}")
            return {"mandate_active": False, "error": str(e)}
    
    def activate_mandate(self) -> Dict[str, Any]:
        """Activate the Autopoietic System Genesis mandate."""
        if not self.validate_keyholder_authority():
            return {
                "status": "error",
                "message": "Keyholder authority not recognized. Mandate activation requires Keyholder override."
            }
        
        mandate_status = {
            "mandate_active": True,
            "activated_by": self.keyholder_authority,
            "activation_date": datetime.utcnow().isoformat(),
            "last_genesis": None,
            "genesis_count": 0,
            "mandate_enforced": True,
            "workflow_path": self.workflow_path,
            "protocol_file": self.protocol_file,
            "output_directory": self.output_directory
        }
        
        try:
            with open(self.mandate_file, 'w') as f:
                json.dump(mandate_status, f, indent=2)
            
            logger.info("Autopoietic System Genesis mandate activated")
            return {
                "status": "success",
                "message": "Autopoietic System Genesis mandate activated. All system development must now use the Genesis protocol.",
                "mandate_status": mandate_status
            }
        except Exception as e:
            logger.error(f"Error activating mandate: {e}")
            return {"status": "error", "message": str(e)}
    
    def enforce_mandate(self, operation_type: str, operation_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce the Autopoietic mandate for any system development operation.
        
        Args:
            operation_type: Type of operation being attempted
            operation_details: Details of the operation
            
        Returns:
            Dict containing mandate enforcement result
        """
        mandate_status = self.check_mandate_status()
        
        if not mandate_status.get("mandate_active", False):
            return {
                "status": "warning",
                "message": "Autopoietic mandate not active. Operation allowed but not recommended.",
                "recommendation": "Activate Autopoietic System Genesis mandate for proper system evolution."
            }
        
        # Check if this operation should trigger Genesis
        genesis_triggers = [
            "code_generation",
            "system_evolution", 
            "architecture_change",
            "new_feature_development",
            "protocol_modification"
        ]
        
        if operation_type in genesis_triggers:
            return {
                "status": "mandate_enforced",
                "message": f"Operation '{operation_type}' requires Autopoietic System Genesis execution.",
                "mandate_requirement": "Execute autopoietic_genesis_protocol.json workflow",
                "workflow_path": self.workflow_path,
                "operation_blocked": True
            }
        
        return {
            "status": "allowed",
            "message": f"Operation '{operation_type}' allowed under current mandate.",
            "mandate_requirement": None
        }
    
    def execute_genesis_workflow(self) -> Dict[str, Any]:
        """
        Execute the Autopoietic System Genesis workflow.
        This is the core mechanism for system self-building.
        """
        if not self.validate_keyholder_authority():
            return {
                "status": "error",
                "message": "Keyholder authority not recognized. Genesis execution requires Keyholder override."
            }
        
        if not os.path.exists(self.workflow_path):
            return {
                "status": "error",
                "message": f"Genesis workflow not found at {self.workflow_path}"
            }
        
        try:
            # Import workflow engine
            from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
            
            # Initialize workflow engine
            workflow_engine = IARCompliantWorkflowEngine()
            
            # Prepare inputs for the Genesis workflow
            genesis_inputs = {
                "protocol_file": self.protocol_file,
                "output_directory": self.output_directory,
                "keyholder_authority": self.keyholder_authority
            }
            
            # Execute the Genesis workflow
            logger.info("Executing Autopoietic System Genesis workflow...")
            result = workflow_engine.run_workflow(
                "autopoietic_genesis_protocol.json",
                genesis_inputs
            )
            
            # Update mandate status
            self._update_genesis_status(result)
            
            return {
                "status": "success",
                "message": "Autopoietic System Genesis completed successfully",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing Genesis workflow: {e}")
            return {
                "status": "error",
                "message": f"Genesis workflow execution failed: {str(e)}"
            }
    
    def _update_genesis_status(self, genesis_result: Dict[str, Any]) -> None:
        """Update the mandate status after Genesis execution."""
        try:
            mandate_status = self.check_mandate_status()
            mandate_status.update({
                "last_genesis": datetime.utcnow().isoformat(),
                "genesis_count": mandate_status.get("genesis_count", 0) + 1,
                "last_genesis_result": genesis_result
            })
            
            with open(self.mandate_file, 'w') as f:
                json.dump(mandate_status, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating Genesis status: {e}")
    
    def get_mandate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report on the mandate status."""
        mandate_status = self.check_mandate_status()
        
        report = {
            "mandate_active": mandate_status.get("mandate_active", False),
            "genesis_count": mandate_status.get("genesis_count", 0),
            "last_genesis": mandate_status.get("last_genesis"),
            "workflow_path": self.workflow_path,
            "protocol_file": self.protocol_file,
            "keyholder_authority": self.keyholder_authority,
            "mandate_enforced": mandate_status.get("mandate_enforced", False)
        }
        
        if mandate_status.get("mandate_active"):
            report["status"] = "MANDATE ACTIVE - System must build itself from specification"
        else:
            report["status"] = "MANDATE INACTIVE - Manual development allowed"
        
        return report

def mandate_check(operation_type: str, operation_details: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Global function to check mandate enforcement for any operation.
    
    Args:
        operation_type: Type of operation being attempted
        operation_details: Details of the operation
        
    Returns:
        Dict containing mandate enforcement result
    """
    mandate_system = AutopoieticMandateSystem()
    return mandate_system.enforce_mandate(operation_type, operation_details or {})

def activate_autopoietic_mandate() -> Dict[str, Any]:
    """
    Global function to activate the Autopoietic System Genesis mandate.
    
    Returns:
        Dict containing activation result
    """
    mandate_system = AutopoieticMandateSystem()
    return mandate_system.activate_mandate()

def execute_autopoietic_genesis() -> Dict[str, Any]:
    """
    Global function to execute the Autopoietic System Genesis workflow.
    
    Returns:
        Dict containing Genesis execution result
    """
    mandate_system = AutopoieticMandateSystem()
    return mandate_system.execute_genesis_workflow()

if __name__ == "__main__":
    # Example usage
    mandate_system = AutopoieticMandateSystem()
    
    # Activate the mandate
    activation_result = mandate_system.activate_mandate()
    print("Mandate Activation:", json.dumps(activation_result, indent=2))
    
    # Check mandate status
    status = mandate_system.get_mandate_report()
    print("Mandate Status:", json.dumps(status, indent=2))
    
    # Execute Genesis workflow
    genesis_result = mandate_system.execute_genesis_workflow()
    print("Genesis Result:", json.dumps(genesis_result, indent=2)) 