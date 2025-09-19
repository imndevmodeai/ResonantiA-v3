import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import copy
from datetime import datetime

# Assuming action_registry.py is in the same directory and provides this global instance
from .action_registry import main_action_registry

logger = logging.getLogger(__name__)

class IARValidator:
    """Validates the structure and content of an Integrated Action Reflection (IAR) object."""
    def validate(self, iar_data: Dict[str, Any]) -> bool:
        if not isinstance(iar_data, dict):
            raise TypeError("IAR data must be a dictionary.")
        if "confidence" not in iar_data:
            raise ValueError("IAR data must contain a 'confidence' key.")
        if not (0 <= iar_data["confidence"] <= 1):
            raise ValueError("IAR confidence must be between 0 and 1.")
        return True

class ResonanceTracker:
    """Tracks tactical resonance and crystallization metrics from IARs."""
    def __init__(self):
        self.log = []
    
    def track(self, task_id: str, iar_data: Dict[str, Any]):
        self.log.append({"task_id": task_id, "iar": iar_data})

class IARCompliantWorkflowEngine:
    """
    The master watchmaker's machine. It takes blueprints (workflows)
    and assembles reality, one IAR-compliant action at a time.
    """
    def __init__(self, workflows_dir: str, spr_manager: Optional[Any] = None):
        self.workflows_path = Path(workflows_dir)
        self.action_registry = main_action_registry
        self.iar_validator = IARValidator()
        self.resonance_tracker = ResonanceTracker()

    def emit_vcd_event(self, event_type: str, message: str, metadata: Dict[str, Any] = None):
        """Emits a structured event for the Visual Cognitive Debugger."""
        event = {
            "event_type": event_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        print(json.dumps(event))

    def run_workflow(self, workflow_name: str, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """The main assembly process for executing a workflow."""
        workflow_file = self.workflows_path / f"{workflow_name}.json"
        if not workflow_file.exists():
            raise FileNotFoundError(f"Workflow '{workflow_name}' not found at {workflow_file}")

        with open(workflow_file, 'r') as f:
            workflow = json.load(f)

        context = {"workflow_inputs": initial_context, **initial_context}
        completed_tasks = set()
        task_outputs = {}

        tasks = workflow.get("tasks", {})
        task_ids = list(tasks.keys())

        while len(completed_tasks) < len(task_ids):
            ready_tasks = [
                tid for tid in task_ids if tid not in completed_tasks and
                all(dep in completed_tasks for dep in tasks[tid].get("dependencies", []))
            ]

            if not ready_tasks:
                raise RuntimeError("Workflow stuck: cyclic dependency or missing inputs.")

            for task_id in ready_tasks:
                task_def = tasks[task_id]
                self.emit_vcd_event("task_start", f"Starting task: {task_id}", {"task": task_def})
                
                action_name = task_def["action_type"]
                action_func = self.action_registry.get_action(action_name)
                
                if not action_func:
                    raise ValueError(f"Action '{action_name}' not found in registry.")

                # Input resolution would be more complex in a real scenario
                inputs = self._resolve_inputs(task_def.get("inputs", {}), task_outputs)

                result = action_func(inputs)
                
                # IAR validation is mandatory
                iar = result.get("reflection", {})
                self.iar_validator.validate(iar)
                self.resonance_tracker.track(task_id, iar)
                
                task_outputs[task_id] = result
                completed_tasks.add(task_id)
                self.emit_vcd_event("task_complete", f"Completed task: {task_id}", {"output": result})
        
        return task_outputs

    def _resolve_inputs(self, input_spec: Dict, task_outputs: Dict) -> Dict:
        """Resolves task inputs from context and previous outputs."""
        resolved_inputs = {}
        for key, value in input_spec.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Simple substitution from previous task outputs
                path = value[2:-2].strip().split('.')
                resolved_value = task_outputs
                for p in path:
                    resolved_value = resolved_value.get(p, {})
                resolved_inputs[key] = resolved_value
            else:
                resolved_inputs[key] = value
        return resolved_inputs
