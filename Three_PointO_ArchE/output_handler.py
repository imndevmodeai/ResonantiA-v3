"""
Output handler for workflow engine with rich terminal formatting.
"""
from datetime import datetime
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def display_task_result(task_name: str, result: Dict[str, Any]) -> None:
    """Display task execution result with rich formatting."""
    # Create a table for the task result
    table = Table(title=f"Task: {task_name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    # Add status
    status = result.get("status", "Unknown")
    table.add_row("Status", status)
    
    # Add summary if available
    if "summary" in result:
        table.add_row("Summary", result["summary"])
    
    # Add confidence if available
    if "confidence" in result:
        table.add_row("Confidence", f"{result['confidence']:.2f}")
    
    # Display the table
    console.print(table)
    
    # Display raw output preview if available
    if "raw_output_preview" in result:
        console.print("\nOutput Preview:")
        console.print(Panel(result["raw_output_preview"], title="Raw Output"))

def display_workflow_progress(task_name: str, status: str) -> None:
    """Display workflow execution progress with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    console.print(f"[{timestamp}] {task_name}: {status}")

def display_workflow_start(workflow_name: str) -> None:
    """Display workflow start message."""
    console.print(Panel(f"Starting Workflow: {workflow_name}", 
                       title="Workflow Execution",
                       border_style="green"))

def display_workflow_complete(results: Dict[str, Any], output_path: str) -> None:
    """Display workflow completion message with results summary."""
    # Create a table for the workflow summary
    table = Table(title="Workflow Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Status", results.get("workflow_status", "Unknown"))
    table.add_row("Execution Time", f"{results.get('execution_time_seconds', 0):.2f} seconds")
    table.add_row("Output File", output_path)
    
    console.print("\n")
    console.print(Panel(table, title="Workflow Complete", border_style="green"))

def display_workflow_error(error: str, output_path: str) -> None:
    """Display workflow error message."""
    console.print("\n")
    console.print(Panel(f"Workflow Failed: {error}\nError details saved to: {output_path}",
                       title="Workflow Error",
                       border_style="red")) 