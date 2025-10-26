"""
Resonant Orchestrator - ArchE's self-orchestration system for advanced tool and workflow chaining.
"""
from typing import Dict, Any, List, Set, Optional
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
import asyncio
from concurrent.futures import ThreadPoolExecutor
import networkx as nx
from rich.console import Console
from .workflow_engine import IARCompliantWorkflowEngine
from .action_registry import main_action_registry
from .output_handler import display_workflow_progress

console = Console()

class ResonantOrchestrator:
    """
    Advanced orchestration system that enables ArchE to self-organize and chain tools/workflows
    in complex patterns of execution.
    """
    
    def __init__(self):
        """Initialize the Resonant Orchestrator with its core components."""
        self.workflow_engine = IARCompliantWorkflowEngine()
        self.action_registry = main_action_registry
        self.execution_graph = nx.DiGraph()  # For tracking execution dependencies
        self.execution_history = []  # For learning from past executions
        self.tool_capabilities = {}  # For storing tool metadata and capabilities
        self.parallel_executor = ThreadPoolExecutor(max_workers=4)
        
    def analyze_capabilities(self) -> Dict[str, Any]:
        """
        Analyze and catalog all available tools and workflows.
        Returns a structured representation of system capabilities.
        """
        capabilities = {
            "tools": {},
            "workflows": {},
            "patterns": set(),
            "dependencies": {}
        }
        
        # Analyze registered actions
        for action_name, action_func in self.action_registry.actions.items():
            capabilities["tools"][action_name] = {
                "type": "action",
                "function": action_func,
                "dependencies": getattr(action_func, "dependencies", []),
                "output_type": getattr(action_func, "output_type", Any),
                "input_schema": getattr(action_func, "input_schema", {})
            }
        
        # Analyze available workflows
        # TODO: Implement workflow analysis
        
        return capabilities
    
    async def execute_resonant_chain(self, 
                                   target: str,
                                   context: Dict[str, Any],
                                   max_depth: int = 3) -> Dict[str, Any]:
        """
        Execute a resonant chain of tools and workflows to achieve a target state.
        
        Args:
            target: The target state or goal to achieve
            context: The current context and constraints
            max_depth: Maximum depth of tool/workflow chaining
            
        Returns:
            Dict containing execution results and metadata
        """
        # Analyze current capabilities
        capabilities = self.analyze_capabilities()
        
        # Build execution plan
        plan = await self._build_resonant_plan(target, context, capabilities, max_depth)
        
        # Execute plan with monitoring
        results = await self._execute_plan(plan, context)
        
        # Update execution history
        self._update_history(plan, results)
        
        return results
    
    async def _build_resonant_plan(self,
                                 target: str,
                                 context: Dict[str, Any],
                                 capabilities: Dict[str, Any],
                                 max_depth: int) -> Dict[str, Any]:
        """
        Build an execution plan using resonant patterns.
        """
        plan = {
            "target": target,
            "context": context,
            "steps": [],
            "parallel_groups": [],
            "dependencies": {}
        }
        
        # Pattern recognition and tool selection
        selected_tools = self._select_tools_for_target(target, capabilities)
        
        # Build dependency graph
        dep_graph = self._build_dependency_graph(selected_tools, context)
        
        # Identify parallel execution opportunities
        parallel_groups = self._identify_parallel_groups(dep_graph)
        
        # Build sequential steps for non-parallel operations
        sequential_steps = self._build_sequential_steps(dep_graph, parallel_groups)
        
        # Add monitoring and adaptation points
        plan["steps"] = self._add_monitoring_points(sequential_steps)
        plan["parallel_groups"] = parallel_groups
        plan["dependencies"] = self._extract_dependencies(dep_graph)
        
        return plan
    
    def _select_tools_for_target(self, target: Dict[str, Any], capabilities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Select appropriate tools based on target requirements and capabilities.
        """
        selected_tools = []
        
        # Extract target aspects
        aspects = target.get("aspects", [])
        constraints = target.get("constraints", {})
        
        # Match tools to aspects
        for aspect in aspects:
            aspect_tools = []
            for tool_name, tool_info in capabilities["tools"].items():
                if self._tool_matches_aspect(tool_name, tool_info, aspect):
                    aspect_tools.append({
                        "name": tool_name,
                        "info": tool_info,
                        "aspect": aspect
                    })
            selected_tools.extend(aspect_tools)
        
        # Apply constraints
        if constraints.get("parallel_execution", False):
            # Group tools that can run in parallel
            parallel_tools = [tool for tool in selected_tools 
                            if self._can_run_in_parallel(tool)]
            selected_tools = parallel_tools
        
        return selected_tools
    
    def _tool_matches_aspect(self, tool_name: str, tool_info: Dict[str, Any], aspect: str) -> bool:
        """
        Determine if a tool matches a target aspect.
        """
        # Check tool metadata
        if "aspects" in tool_info:
            return aspect in tool_info["aspects"]
        
        # Check tool name patterns
        aspect_patterns = {
            "code_quality": ["lint", "analyze", "check", "quality"],
            "workflow_health": ["test", "verify", "validate", "health"],
            "system_integrity": ["check", "verify", "validate", "integrity"]
        }
        
        if aspect in aspect_patterns:
            return any(pattern in tool_name.lower() 
                      for pattern in aspect_patterns[aspect])
        
        return False
    
    def _can_run_in_parallel(self, tool: Dict[str, Any]) -> bool:
        """
        Determine if a tool can run in parallel with others.
        """
        # Check tool metadata
        if "parallel_safe" in tool["info"]:
            return tool["info"]["parallel_safe"]
        
        # Check for resource conflicts
        if "resource_requirements" in tool["info"]:
            reqs = tool["info"]["resource_requirements"]
            return not any(req.get("exclusive", False) for req in reqs)
        
        return True
    
    def _build_dependency_graph(self, tools: List[Dict[str, Any]], context: Dict[str, Any]) -> nx.DiGraph:
        """
        Build a directed graph of tool dependencies.
        """
        graph = nx.DiGraph()
        
        # Add tools as nodes
        for tool in tools:
            graph.add_node(tool["name"], **tool["info"])
        
        # Add dependencies as edges
        for tool in tools:
            deps = tool["info"].get("dependencies", [])
            for dep in deps:
                if dep in graph:
                    graph.add_edge(dep, tool["name"])
        
        return graph
    
    def _identify_parallel_groups(self, dep_graph: nx.DiGraph) -> List[List[str]]:
        """
        Identify groups of tools that can run in parallel using topological layers.
        """
        parallel_groups = []
        graph = dep_graph.copy()
        while graph:
            # Find nodes with no incoming edges (ready to run)
            ready = [node for node, degree in graph.in_degree() if degree == 0]
            if not ready:
                break  # Cycle or done
            parallel_groups.append(ready)
            # Remove these nodes for the next layer
            graph.remove_nodes_from(ready)
        return parallel_groups
    
    def _build_sequential_steps(self, dep_graph: nx.DiGraph, parallel_groups: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Build sequential steps for non-parallel operations.
        """
        # Get topological sort of the graph
        try:
            topo_sort = list(nx.topological_sort(dep_graph))
        except nx.NetworkXUnfeasible:
            # Graph has cycles, use a different approach
            topo_sort = list(dep_graph.nodes())
        
        # Filter out tools that are in parallel groups
        parallel_tools = set()
        for group in parallel_groups:
            parallel_tools.update(group)
        
        sequential_tools = [tool for tool in topo_sort if tool not in parallel_tools]
        
        # Build steps
        steps = []
        for tool in sequential_tools:
            steps.append({
                "type": "action",
                "name": tool,
                "dependencies": list(dep_graph.predecessors(tool))
            })
        
        return steps
    
    def _add_monitoring_points(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add monitoring and adaptation points to the execution plan.
        """
        monitored_steps = []
        
        for step in steps:
            # Add the original step
            monitored_steps.append(step)
            
            # Add monitoring step
            monitored_steps.append({
                "type": "monitor",
                "target_step": step["name"],
                "metrics": ["execution_time", "resource_usage", "success_rate"]
            })
            
            # Add adaptation point
            monitored_steps.append({
                "type": "adapt",
                "target_step": step["name"],
                "conditions": [
                    {"metric": "execution_time", "threshold": 30},
                    {"metric": "success_rate", "threshold": 0.8}
                ]
            })
        
        return monitored_steps
    
    def _extract_dependencies(self, dep_graph: nx.DiGraph) -> Dict[str, List[str]]:
        """
        Extract dependencies from the dependency graph.
        """
        dependencies = {}
        for node in dep_graph.nodes():
            dependencies[node] = list(dep_graph.predecessors(node))
        return dependencies
    
    async def _execute_plan(self,
                          plan: Dict[str, Any],
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a resonant plan with monitoring and adaptation.
        """
        results = {
            "start_time": now_iso(),
            "steps": [],
            "parallel_results": [],
            "adaptations": []
        }
        
        # Execute parallel groups
        parallel_tasks = []
        for group in plan["parallel_groups"]:
            task = asyncio.create_task(
                self._execute_parallel_group(group, context)
            )
            parallel_tasks.append(task)
        
        # Execute sequential steps
        for step in plan["steps"]:
            step_result = await self._execute_step(step, context)
            results["steps"].append(step_result)
            
            # Check if adaptation is needed
            if self._needs_adaptation(step_result):
                adaptation = await self._adapt_execution(step_result, context)
                results["adaptations"].append(adaptation)
        
        # Wait for parallel tasks
        parallel_results = await asyncio.gather(*parallel_tasks)
        results["parallel_results"] = parallel_results
        
        results["end_time"] = now_iso()
        return results
    
    async def _execute_parallel_group(self,
                                    group: List[Dict[str, Any]],
                                    context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute a group of steps in parallel.
        """
        tasks = []
        for step in group:
            task = asyncio.create_task(
                self._execute_step(step, context)
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    async def _execute_step(self,
                          step: Dict[str, Any],
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step in the plan.
        """
        step_type = step.get("type")
        if step_type == "action":
            return await self._execute_action(step, context)
        elif step_type == "workflow":
            return await self._execute_workflow(step, context)
        else:
            raise ValueError(f"Unknown step type: {step_type}")
    
    def _needs_adaptation(self, step_result: Dict[str, Any]) -> bool:
        """
        Determine if execution needs to be adapted based on results.
        """
        # TODO: Implement adaptation logic
        return False
    
    async def _adapt_execution(self,
                             step_result: Dict[str, Any],
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt execution based on results and context.
        """
        # TODO: Implement adaptation strategies
        return {}
    
    def _update_history(self, plan: Dict[str, Any], results: Dict[str, Any]) -> None:
        """
        Update execution history with new results.
        """
        self.execution_history.append({
            "timestamp": now_iso(),
            "plan": plan,
            "results": results
        })
        
        # TODO: Implement history analysis for pattern learning 