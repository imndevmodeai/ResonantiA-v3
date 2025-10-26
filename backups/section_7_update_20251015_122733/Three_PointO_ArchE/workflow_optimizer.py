"""
================================
Workflow Optimizer (workflow_optimizer.py)
================================

As Above: The Principle of the Optimal Path
--------------------------------------------
Every complex endeavor is a journey with many stops. The wisdom lies not just in visiting each destination, but in the path taken between them. The Workflow Optimizer embodies this universal principle. It abstracts the classic "Traveling Salesman Problem" into a higher philosophy: finding the most efficient, least costly sequence of *any* set of operations to achieve a goal. It is the wisdom of enlightened sequencing, ensuring the system's will is executed not just effectively, but with elegance and economy.

So Below: The Operational Logic
-------------------------------
This module provides the `WorkflowOptimizer` class, a tool designed to be integrated into the `IARCompliantWorkflowEngine`. It takes a graph of workflow tasks, analyzes their dependencies and associated costs, and calculates the most efficient execution order to minimize resource consumption (e.g., time, tokens, computational cost).
"""

import networkx as nx
import itertools
from typing import Dict, Any, List, Tuple

class WorkflowOptimizer:
    """
    Applies combinatorial optimization principles to find the most efficient
    execution path for a given workflow plan.
    """

    def __init__(self, plan: Dict[str, Any]):
        """
        Initializes the optimizer with a workflow plan.

        Args:
            plan (Dict[str, Any]): The workflow plan, expected to contain 'tasks'
                                 and 'dependencies'.
        """
        self.tasks = plan.get("tasks", [])
        self.dependencies = plan.get("dependencies", {})
        self.graph = self._build_dependency_graph()

    def _build_dependency_graph(self) -> nx.DiGraph:
        """Builds a directed graph from the tasks and their dependencies."""
        G = nx.DiGraph()
        task_ids = [task['id'] for task in self.tasks]
        G.add_nodes_from(task_ids)

        for task_id, deps in self.dependencies.items():
            if task_id in task_ids:
                for dep_id in deps:
                    if dep_id in task_ids:
                        G.add_edge(dep_id, task_id)
        
        if not nx.is_directed_acyclic_graph(G):
            raise ValueError("Workflow contains circular dependencies and cannot be optimized.")
            
        return G

    def get_optimized_execution_plan(self) -> List[List[str]]:
        """
        Calculates the optimal execution plan.

        Returns:
            A list of lists, where each inner list represents a "stage" of tasks
            that can be executed in parallel.
        """
        # A topological sort gives us a valid execution order that respects dependencies.
        # This is the simplest form of optimization (ensuring validity).
        # For a true TSP-like optimization, we would need cost metrics between tasks.
        
        # For now, we will use topological generations, which groups tasks into parallelizable stages.
        generations = list(nx.topological_generations(self.graph))
        
        # Reverse the graph to trace dependencies correctly for the generations algorithm
        # nx.topological_generations expects nodes with no outgoing edges to be the start
        # but in our dependency graph, nodes with no *incoming* edges are the start.
        # Let's use the standard topological sort and then structure it.
        
        # Correct approach: a standard topological sort gives a linear valid order.
        # To find parallel stages, we can use Kahn's algorithm logic.
        
        in_degree = {node: self.graph.in_degree(node) for node in self.graph.nodes()}
        queue = [node for node, degree in in_degree.items() if degree == 0]
        
        execution_plan = []
        while queue:
            # All nodes in the current queue can be executed in parallel
            execution_plan.append(queue)
            
            next_queue = []
            for node in queue:
                for neighbor in self.graph.successors(node):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_queue.append(neighbor)
            queue = next_queue

        if sum(len(stage) for stage in execution_plan) != len(self.graph.nodes()):
             raise ValueError("Workflow contains a cycle, cannot generate a valid plan.")

        return execution_plan

    def _get_task_cost(self, task_id: str) -> float:
        """
        Retrieves the cost of a task. In a real system, this would be based on
        historical execution data (time, tokens, etc.).
        
        For now, we'll use a placeholder.
        """
        task = next((t for t in self.tasks if t['id'] == task_id), None)
        if task:
            # Mock cost based on action type
            action = task.get('action', 'unknown')
            cost_map = {'llm_query': 10, 'web_search': 5, 'file_io': 2}
            return cost_map.get(action, 1)
        return 1

    def get_tsp_optimized_plan(self) -> List[str]:
        """
        A more advanced optimization that treats independent tasks within a stage
        like a Traveling Salesman Problem to find the cheapest sequence.
        
        NOTE: This is a conceptual implementation. A true TSP optimization on workflow
        tasks is complex and depends heavily on accurate cost metrics *between* tasks
        (e.g., cost of data transformation from task A's output to task B's input).
        
        For now, we'll optimize the linear order of the entire plan based on task costs.
        """
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Cannot perform TSP optimization on a graph with cycles.")

        # Get all valid topological sorts (all possible valid linear execution paths)
        all_paths = list(nx.all_topological_sorts(self.graph))
        
        if not all_paths:
            # Handle case with no tasks or a single task
            if self.graph.nodes():
                return list(self.graph.nodes())
            return []

        best_path = None
        min_cost = float('inf')

        # Calculate the cost of each path and find the minimum
        for path in all_paths:
            # The "cost" in this context is simply the sum of individual task costs.
            # A more advanced model could include transition costs between tasks.
            current_cost = sum(self._get_task_cost(task_id) for task_id in path)
            
            if current_cost < min_cost:
                min_cost = current_cost
                best_path = path

        return best_path if best_path is not None else []


if __name__ == '__main__':
    # Example usage for demonstration
    console = __import__('rich.console').console.Console()

    # --- Example 1: Simple linear workflow ---
    plan1 = {
        "tasks": [
            {"id": "A", "action": "web_search"},
            {"id": "B", "action": "llm_query"},
            {"id": "C", "action": "file_io"}
        ],
        "dependencies": {
            "B": ["A"],
            "C": ["B"]
        }
    }
    optimizer1 = WorkflowOptimizer(plan1)
    parallel_plan1 = optimizer1.get_optimized_execution_plan()
    
    console.print("[bold green]-- Example 1: Linear Workflow --[/bold green]")
    console.print("Parallel Execution Plan (Stages):", parallel_plan1)
    
    # --- Example 2: Workflow with parallel opportunities ---
    plan2 = {
        "tasks": [
            {"id": "A_fetch_data", "action": "web_search"},
            {"id": "B_process_data", "action": "llm_query"},
            {"id": "C_fetch_user_prefs", "action": "file_io"},
            {"id": "D_generate_report", "action": "llm_query"}
        ],
        "dependencies": {
            "B_process_data": ["A_fetch_data"],
            "D_generate_report": ["B_process_data", "C_fetch_user_prefs"]
        }
    }
    optimizer2 = WorkflowOptimizer(plan2)
    parallel_plan2 = optimizer2.get_optimized_execution_plan()
    tsp_plan2 = optimizer2.get_tsp_optimized_plan()

    console.print("\n[bold green]-- Example 2: Parallel Workflow --[/bold green]")
    console.print("Parallel Execution Plan (Stages):", parallel_plan2)
    console.print("TSP-like Optimized Linear Path:", tsp_plan2)

    # --- Example 3: Invalid workflow with a cycle ---
    plan3 = {
        "tasks": [{"id": "A"}, {"id": "B"}],
        "dependencies": {"A": ["B"], "B": ["A"]}
    }
    try:
        console.print("\n[bold red]-- Example 3: Workflow with Cycle (Error Expected) --[/bold red]")
        optimizer3 = WorkflowOptimizer(plan3)
    except ValueError as e:
        console.print(f"Successfully caught expected error: {e}")
