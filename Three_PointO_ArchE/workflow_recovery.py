from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WorkflowRecoveryHandler:
    """Handles workflow recovery and failure analysis according to ResonantiA Protocol v3.0."""
    
    def __init__(self, workflow_definition: Dict[str, Any], run_id: str):
        self.workflow_definition = workflow_definition
        self.run_id = run_id
        self.recovery_flows = self._load_recovery_flows()
        
    def _load_recovery_flows(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined recovery flows for different failure scenarios."""
        return {
            "template_resolution_failure": {
                "description": "Recovery flow for template variable resolution failures",
                "tasks": {
                    "analyze_template_failure": {
                        "action_type": "analyze_failure",
                        "inputs": {
                            "failure_type": "template_resolution",
                            "context": "{{workflow_context}}"
                        }
                    },
                    "fix_template_variables": {
                        "action_type": "fix_template",
                        "inputs": {
                            "analysis": "{{analyze_template_failure.output}}",
                            "workflow": "{{workflow_definition}}"
                        },
                        "dependencies": ["analyze_template_failure"]
                    },
                    "validate_fix": {
                        "action_type": "validate_workflow",
                        "inputs": {
                            "modified_workflow": "{{fix_template_variables.output}}"
                        },
                        "dependencies": ["fix_template_variables"]
                    }
                }
            },
            "action_structure_failure": {
                "description": "Recovery flow for action return structure failures",
                "tasks": {
                    "analyze_action_failure": {
                        "action_type": "analyze_failure",
                        "inputs": {
                            "failure_type": "action_structure",
                            "context": "{{workflow_context}}"
                        }
                    },
                    "fix_action_structure": {
                        "action_type": "fix_action",
                        "inputs": {
                            "analysis": "{{analyze_action_failure.output}}",
                            "action_code": "{{workflow_context.failed_action}}"
                        },
                        "dependencies": ["analyze_action_failure"]
                    },
                    "validate_fix": {
                        "action_type": "validate_action",
                        "inputs": {
                            "modified_action": "{{fix_action_structure.output}}"
                        },
                        "dependencies": ["fix_action_structure"]
                    }
                }
            }
        }
    
    def analyze_failure(self, failure_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workflow failure and determine appropriate recovery flow."""
        print(f"[DEBUG] Analyzing failure context: {failure_context}")
        
        # Extract failure information
        failed_task = failure_context.get("failed_task")
        error_type = failure_context.get("error_type")
        error_message = failure_context.get("error_message")
        
        # Determine recovery flow
        recovery_flow = None
        if "template" in error_message.lower():
            recovery_flow = self.recovery_flows["template_resolution_failure"]
        elif "structure" in error_message.lower() or "return" in error_message.lower():
            recovery_flow = self.recovery_flows["action_structure_failure"]
        
        if not recovery_flow:
            return {
                "output": {
                    "status": "unrecoverable",
                    "message": f"No recovery flow found for error: {error_message}"
                },
                "reflection": {
                    "status": "Failure",
                    "summary": "Could not determine recovery flow",
                    "confidence": 0.0,
                    "alignment_check": "Unknown",
                    "potential_issues": [error_message],
                    "raw_output_preview": str(failure_context)[:150]
                }
            }
        
        # Prepare recovery context
        recovery_context = {
            "workflow_context": {
                "failed_task": failed_task,
                "error_type": error_type,
                "error_message": error_message,
                "workflow_definition": self.workflow_definition,
                "run_id": self.run_id
            }
        }
        
        return {
            "output": {
                "status": "recoverable",
                "recovery_flow": recovery_flow,
                "context": recovery_context
            },
            "reflection": {
                "status": "Success",
                "summary": f"Identified recovery flow for {error_type}",
                "confidence": 0.95,
                "alignment_check": "Aligned",
                "potential_issues": None,
                "raw_output_preview": str(recovery_flow)[:150]
            }
        }
    
    def append_recovery_flow(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Append recovery flow to the original workflow."""
        if analysis_result["output"]["status"] != "recoverable":
            return analysis_result
        
        recovery_flow = analysis_result["output"]["recovery_flow"]
        original_tasks = self.workflow_definition.get("tasks", {})
        
        # Create recovery task IDs with timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recovery_tasks = {}
        for task_id, task in recovery_flow["tasks"].items():
            new_task_id = f"{task_id}_{timestamp}"
            recovery_tasks[new_task_id] = task
        
        # Update dependencies in recovery tasks
        for task_id, task in recovery_tasks.items():
            if "dependencies" in task:
                task["dependencies"] = [
                    f"{dep}_{timestamp}" if dep in recovery_tasks else dep
                    for dep in task["dependencies"]
                ]
        
        # Merge original and recovery tasks
        merged_tasks = {**original_tasks, **recovery_tasks}
        
        # Create new workflow definition
        new_workflow = {
            **self.workflow_definition,
            "tasks": merged_tasks,
            "metadata": {
                "original_run_id": self.run_id,
                "recovery_timestamp": timestamp,
                "recovery_type": analysis_result["output"]["recovery_flow"]["description"]
            }
        }
        
        return {
            "output": {
                "status": "success",
                "modified_workflow": new_workflow
            },
            "reflection": {
                "status": "Success",
                "summary": "Successfully appended recovery flow",
                "confidence": 0.95,
                "alignment_check": "Aligned",
                "potential_issues": None,
                "raw_output_preview": str(new_workflow)[:150]
            }
        } 