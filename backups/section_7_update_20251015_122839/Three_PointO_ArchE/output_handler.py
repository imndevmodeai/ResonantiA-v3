"""
Output handler for workflow engine with rich terminal formatting.
"""
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def _compact(obj: Any, max_chars: int = 600) -> str:
    """Return a compact JSON-ish preview of obj, trimmed for terminal visibility."""
    try:
        from json import dumps as _jdumps
        text = _jdumps(obj, ensure_ascii=False, default=str)
    except Exception:
        text = str(obj)
    if len(text) > max_chars:
        return text[:max_chars] + "..."
    return text

def print_tagged_execution(task_name: str, action_type: str, inputs: Dict[str, Any]) -> None:
    """Emit execution tag block to the terminal for traceable runs."""
    try:
        print("->|execution|<-")
        print(f"TASK: {task_name} | ACTION: {action_type}")
        print(_compact({"inputs": inputs}))
    except Exception:
        # Keep terminal resilient; do not crash on logging issues
        pass

def print_tagged_results(task_name: str, action_type: str, result: Dict[str, Any]) -> None:
    """Emit results tag block to the terminal with a concise preview."""
    try:
        print("->|Results|<-")
        # Hardened status check: default to Failed if result is empty or status is missing
        status = "Failed"
        if result and result.get("status"):
            status = result.get("status")
        elif result and "error" not in result:
            status = "Success"

        print(f"TASK: {task_name} | ACTION: {action_type} | STATUS: {status}")
        
        # Always print the full result for complete transparency
        print(_compact(result))
    except Exception:
        pass

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
    timestamp = format_log()
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

def display_workflow_error(error_message: str):
    """Displays a formatted error message for a workflow failure."""
    print(f"\\n--- WORKFLOW ERROR ---\\n{error_message}\\n----------------------")

def display_output(content: str):
    """A generic function to display content to the console."""
    print(content)
    return {
        "status": "Success",
        "message": "Content displayed.",
        "reflection": {
            "tool_name": "display_output",
            "status": "Success",
            "confidence": 1.0,
            "message": "Successfully displayed content to the console."
        }
    } 