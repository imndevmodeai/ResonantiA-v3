"""
Cognitive Visualizer for ArchE

This module provides functions to generate various visualizations of ArchE's
cognitive processes, particularly the query superposition and workflow execution.
"""

from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
import json

console = Console()

def generate_superposition_visualization(superposition: Dict[str, float]) -> None:
    """
    Generates and prints a detailed visualization of the query superposition state.
    """
    if not superposition:
        console.print("[yellow]No superposition data to visualize.[/yellow]")
        return

    table = Table(title="🔬 Query Superposition Analysis", style="bold blue", show_header=True, header_style="bold magenta")
    table.add_column("Intent", style="cyan", no_wrap=True)
    table.add_column("Probability", justify="right", style="green")
    table.add_column("Visualization", style="yellow")

    quantum_state = superposition.get("quantum_state", "N/A")

    # Filter out quantum_state and ensure all values are numeric
    numeric_items = [(intent, prob) for intent, prob in superposition.items() 
                     if isinstance(prob, (int, float)) and intent != "quantum_state" and prob > 0.01]
    
    for intent, prob in sorted(numeric_items, key=lambda item: item[1], reverse=True):
            bar_length = int(prob * 30)
            bar = "█" * bar_length
            table.add_row(intent, f"{prob:.3f}", bar)

    console.print(table)
    console.print(Panel(f"[bold]Quantum State:[/bold] {quantum_state}", border_style="blue"))


def generate_cognitive_flow_visualization(results: Dict[str, Any]) -> None:
    """
    Generates and prints a tree-based visualization of the cognitive workflow execution.
    """
    if not results or 'workflow_name' not in results:
        console.print("[yellow]No workflow data to visualize.[/yellow]")
        return

    workflow_name = results.get('workflow_name', 'Unknown Workflow')
    run_id = results.get('workflow_run_id', 'N/A')
    status = results.get('workflow_status', 'N/A')
    duration = results.get('workflow_run_duration_sec', 'N/A')

    tree = Tree(f"🧠 [bold magenta]Cognitive Flow: {workflow_name}[/bold magenta]\nRun ID: {run_id} | Status: {status} | Duration: {duration}s", guide_style="bold bright_blue")

    metadata_keys = {
        'workflow_name', 'workflow_run_id', 'workflow_status',
        'workflow_run_duration_sec', 'task_statuses', 'initial_context',
        'workflow_definition'
    }
    task_keys = [key for key in results.keys() if key not in metadata_keys]

    for task_name in task_keys:
        task_data = results.get(task_name, {})
        task_status = task_data.get('status', 'unknown')
        action_type = task_data.get('action_type', 'N/A')
        
        color = "green" if task_status == 'Success' else "red"
        branch = tree.add(f"[{color}]▶️ {task_name} ({action_type}) - {task_status}[/{color}]")

        inputs = task_data.get('inputs', {})
        if inputs:
            inputs_str = json.dumps(inputs, indent=2)
            branch.add(f"[cyan]Inputs:[/cyan]\n[dim]{inputs_str}[/dim]")

        result = task_data.get('result', {})
        if result:
            # Preview of result, truncated if too long
            result_str = json.dumps(result, indent=2)
            if len(result_str) > 500:
                result_str = result_str[:500] + "..."
            branch.add(f"[green]Result:[/green]\n[dim]{result_str}[/dim]")

    console.print(tree)

def create_visualization_report(query: str, superposition: Dict[str, float], results: Dict[str, Any], output_path: str) -> None:
    """
    Creates a comprehensive HTML report with all visualizations.
    (Placeholder for future implementation)
    """
    console.print(f"[bold yellow]Placeholder:[/bold yellow] An interactive HTML report would be generated at '{output_path}'.")
    console.print("This would include interactive charts, workflow graphs, and detailed data exploration.")
    # In a real implementation, you would use a library like Plotly, D3.js, or just generate HTML/CSS/JS
    # to create an interactive dashboard file.
    
    # For now, we'll just print the text-based visualizations
    generate_superposition_visualization(superposition)
    generate_cognitive_flow_visualization(results)
