"""
Workflow Chaining Engine - Advanced workflow orchestration with IAR integration
"""
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import networkx as nx
from rich.console import Console
from .workflow_engine import IARCompliantWorkflowEngine
from .action_registry import main_action_registry
from .output_handler import display_workflow_progress

console = Console()

class WorkflowChainingEngine:
    """
    Advanced workflow engine that handles complex workflow chaining with IAR integration,
    parallel processing, and conditional execution.
    """
    
    def __init__(self):
        """Initialize the workflow chaining engine with its core components."""
        self.workflow_engine = IARCompliantWorkflowEngine()
        self.action_registry = main_action_registry
        self.execution_graph = nx.DiGraph()
        self.execution_history = []
        self.parallel_executor = ThreadPoolExecutor(max_workers=4)
        self.iar_manager = IARManager()
    
    async def execute_workflow(self, workflow: Dict[str, Any], initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a workflow with complex chaining patterns.
        
        Args:
            workflow: The workflow definition
            initial_context: Optional initial context
            
        Returns:
            Dict containing execution results and IAR data
        """
        # Initialize execution context
        context = initial_context or {}
        context['workflow_start_time'] = datetime.now().isoformat()
        
        # Build execution graph
        self._build_execution_graph(workflow)
        
        # Execute tasks in topological order
        results = {}
        completed_tasks = set()
        
        try:
            for task_name in nx.topological_sort(self.execution_graph):
                if task_name in completed_tasks:
                    continue
                
                # Check dependencies
                if not self._check_dependencies(task_name, completed_tasks):
                    continue
                
                # Execute task
                task_result = await self._execute_task(workflow['tasks'][task_name], context, results)
                
                # Process IAR
                iar_data = self.iar_manager.process_iar(task_name, task_result, context)
                
                # Store results
                results[task_name] = {
                    'result': task_result,
                    'iar': iar_data,
                    'timestamp': datetime.now().isoformat()
                }
                
                completed_tasks.add(task_name)
                
                # Check for conditional execution
                if 'condition' in workflow['tasks'][task_name]:
                    if not self._evaluate_condition(workflow['tasks'][task_name]['condition'], results):
                        continue
                
                # Handle parallel processing
                if workflow['tasks'][task_name]['action_type'] == 'perform_parallel_action':
                    await self._handle_parallel_processing(task_name, workflow['tasks'][task_name], context, results)
                
                # Handle metacognitive shift
                if workflow['tasks'][task_name]['action_type'] == 'perform_metacognitive_shift':
                    await self._handle_metacognitive_shift(task_name, workflow['tasks'][task_name], context, results)
        
        except Exception as e:
            console.print(f"[red]Error executing workflow: {str(e)}[/red]")
            raise
        
        finally:
            # Record execution history
            self.execution_history.append({
                'workflow': workflow['name'],
                'start_time': context['workflow_start_time'],
                'end_time': datetime.now().isoformat(),
                'results': results
            })
        
        return results
    
    def _build_execution_graph(self, workflow: Dict[str, Any]) -> None:
        """Build the execution graph from workflow definition."""
        self.execution_graph.clear()
        
        for task_name, task in workflow['tasks'].items():
            self.execution_graph.add_node(task_name)
            
            for dep in task.get('dependencies', []):
                self.execution_graph.add_edge(dep, task_name)
    
    def _check_dependencies(self, task_name: str, completed_tasks: Set[str]) -> bool:
        """Check if all dependencies for a task are completed."""
        return all(dep in completed_tasks for dep in self.execution_graph.predecessors(task_name))
    
    async def _execute_task(self, task: Dict[str, Any], context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task with IAR integration."""
        display_workflow_progress(task['description'], "Starting")
        
        try:
            # Resolve inputs
            resolved_inputs = self._resolve_inputs(task['inputs'], context, results)
            
            # Execute action
            action_result = await self.action_registry.execute_action(
                task['action_type'],
                resolved_inputs,
                context
            )
            
            display_workflow_progress(task['description'], "Completed")
            return action_result
        
        except Exception as e:
            display_workflow_progress(task['description'], f"Failed: {str(e)}")
            raise
    
    def _resolve_inputs(self, inputs: Dict[str, Any], context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve input values from context and previous results."""
        resolved = {}
        
        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
                # Extract reference path
                ref_path = value[2:-2].strip()
                
                # Split into components
                components = ref_path.split('.')
                
                # Resolve value
                if components[0] in results:
                    current = results[components[0]]
                    for comp in components[1:]:
                        current = current.get(comp, {})
                    resolved[key] = current
                elif components[0] in context:
                    current = context[components[0]]
                    for comp in components[1:]:
                        current = current.get(comp, {})
                    resolved[key] = current
                else:
                    resolved[key] = None
            else:
                resolved[key] = value
        
        return resolved
    
    def _evaluate_condition(self, condition: str, results: Dict[str, Any]) -> bool:
        """Evaluate a condition string against results."""
        try:
            # Replace references with actual values
            for key, value in results.items():
                if key in condition:
                    condition = condition.replace(key, str(value))
            
            # Evaluate condition
            return eval(condition)
        
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to evaluate condition: {str(e)}[/yellow]")
            return False
    
    async def _handle_parallel_processing(self, task_name: str, task: Dict[str, Any], context: Dict[str, Any], results: Dict[str, Any]) -> None:
        """Handle parallel processing tasks."""
        tasks = task['inputs']['tasks']
        
        # Create tasks for parallel execution
        async def execute_parallel_task(task_def: Dict[str, Any]) -> Dict[str, Any]:
            return await self.action_registry.execute_action(
                task_def['action'],
                task_def['data'],
                context
            )
        
        # Execute tasks in parallel
        parallel_results = await asyncio.gather(
            *[execute_parallel_task(task_def) for task_def in tasks]
        )
        
        # Store results
        results[task_name] = {
            'parallel_results': dict(zip([t['name'] for t in tasks], parallel_results)),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _handle_metacognitive_shift(self, task_name: str, task: Dict[str, Any], context: Dict[str, Any], results: Dict[str, Any]) -> None:
        """Handle metacognitive shift tasks."""
        shift_result = await self.action_registry.execute_action(
            'perform_metacognitive_shift',
            {
                'context': task['inputs']['context'],
                'threshold': task['inputs']['threshold']
            },
            context
        )
        
        # Store shift results
        results[task_name] = {
            'shift_result': shift_result,
            'timestamp': datetime.now().isoformat()
        }

class IARManager:
    """Manages IAR (Integrated Action Reflection) data for workflow execution."""
    
    def __init__(self):
        self.iar_validator = IARValidator()
        self.resonance_tracker = ResonanceTracker()
    
    def process_iar(self, task_id: str, result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process IAR data for a task execution."""
        # Validate IAR structure
        is_valid, issues = self.iar_validator.validate_structure(result)
        if not is_valid:
            raise ValueError(f"Invalid IAR structure: {issues}")
        
        # Track resonance
        self.resonance_tracker.record_execution(task_id, result, context)
        
        # Update context
        if 'iar_history' not in context:
            context['iar_history'] = []
        context['iar_history'].append(result)
        
        return result 