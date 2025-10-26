import json
import os
import logging
from typing import Dict, Any, List, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    task_dependencies: Dict[str, Set[str]]
    action_types: Set[str]

class WorkflowValidator:
    """Validates workflow structure, dependencies, and action types."""
    
    def __init__(self, action_registry: Dict[str, Any]):
        self.action_registry = action_registry
        self.required_task_fields = {
            'description', 'action_type', 'inputs', 'dependencies'
        }
        self.optional_task_fields = {
            'outputs', 'condition', 'retries', 'timeout'
        }
    
    def validate_workflow(self, workflow: Dict[str, Any]) -> ValidationResult:
        """Validate a workflow definition."""
        errors = []
        warnings = []
        task_dependencies = defaultdict(set)
        action_types = set()
        
        # Validate top-level structure
        if not isinstance(workflow, dict):
            errors.append("Workflow must be a dictionary")
            return ValidationResult(False, errors, warnings, task_dependencies, action_types)
        
        required_fields = {'name', 'description', 'version', 'tasks'}
        missing_fields = required_fields - set(workflow.keys())
        if missing_fields:
            errors.append(f"Missing required fields: {missing_fields}")
        
        # Validate tasks
        if 'tasks' not in workflow or not isinstance(workflow['tasks'], dict):
            errors.append("Workflow must contain a 'tasks' dictionary")
        else:
            for task_id, task in workflow['tasks'].items():
                # Validate task structure
                task_errors, task_warnings = self._validate_task(task_id, task)
                errors.extend(task_errors)
                warnings.extend(task_warnings)
                
                # Track dependencies and action types
                if 'dependencies' in task:
                    task_dependencies[task_id] = set(task['dependencies'])
                if 'action_type' in task:
                    action_types.add(task['action_type'])
        
        # Validate dependency cycles
        if not errors:  # Only check cycles if no other errors
            cycle = self._check_dependency_cycles(task_dependencies)
            if cycle:
                errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")
        
        # Validate action types
        invalid_actions = action_types - set(self.action_registry.keys())
        if invalid_actions:
            errors.append(f"Invalid action types: {invalid_actions}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            task_dependencies=dict(task_dependencies),
            action_types=action_types
        )
    
    def _validate_task(self, task_id: str, task: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate a single task definition."""
        errors = []
        warnings = []
        
        # Check required fields
        missing_fields = self.required_task_fields - set(task.keys())
        if missing_fields:
            errors.append(f"Task '{task_id}' missing required fields: {missing_fields}")
        
        # Validate action_type
        if 'action_type' in task:
            if task['action_type'] not in self.action_registry:
                errors.append(f"Task '{task_id}' has invalid action_type: {task['action_type']}")
        
        # Validate inputs
        if 'inputs' in task:
            if not isinstance(task['inputs'], dict):
                errors.append(f"Task '{task_id}' inputs must be a dictionary")
        
        # Validate dependencies
        if 'dependencies' in task:
            if not isinstance(task['dependencies'], list):
                errors.append(f"Task '{task_id}' dependencies must be a list")
        
        # Validate condition
        if 'condition' in task:
            if not isinstance(task['condition'], str):
                errors.append(f"Task '{task_id}' condition must be a string")
        
        # Check for unused optional fields
        unused_fields = set(task.keys()) - (self.required_task_fields | self.optional_task_fields)
        if unused_fields:
            warnings.append(f"Task '{task_id}' has unused fields: {unused_fields}")
        
        return errors, warnings
    
    def _check_dependency_cycles(self, dependencies: Dict[str, Set[str]]) -> List[str]:
        """Check for cycles in task dependencies using DFS."""
        visited = set()
        path = []
        
        def dfs(task_id: str) -> List[str]:
            if task_id in path:
                cycle_start = path.index(task_id)
                return path[cycle_start:] + [task_id]
            
            if task_id in visited:
                return []
            
            visited.add(task_id)
            path.append(task_id)
            
            for dep in dependencies.get(task_id, set()):
                cycle = dfs(dep)
                if cycle:
                    return cycle
            
            path.pop()
            return []
        
        for task_id in dependencies:
            cycle = dfs(task_id)
            if cycle:
                return cycle
        
        return []

def validate_workflow_file(filepath: str, action_registry: Dict[str, Any]) -> ValidationResult:
    """Validate a workflow file."""
    try:
        with open(filepath, 'r') as f:
            workflow = json.load(f)
        
        validator = WorkflowValidator(action_registry)
        return validator.validate_workflow(workflow)
    
    except json.JSONDecodeError as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"Invalid JSON: {str(e)}"],
            warnings=[],
            task_dependencies={},
            action_types=set()
        )
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"Error validating workflow: {str(e)}"],
            warnings=[],
            task_dependencies={},
            action_types=set()
        )

if __name__ == "__main__":
    # Example usage
    from action_registry import ACTION_REGISTRY
    
    workflow_path = "workflows/system_genesis_and_evolution_workflow.json"
    result = validate_workflow_file(workflow_path, ACTION_REGISTRY)
    
    if result.is_valid:
        print("Workflow is valid!")
        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"- {warning}")
    else:
        print("Workflow is invalid!")
        print("\nErrors:")
        for error in result.errors:
            print(f"- {error}") 