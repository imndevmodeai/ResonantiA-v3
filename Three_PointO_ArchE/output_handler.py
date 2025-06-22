"""
Output handler for workflow engine with rich terminal formatting.
"""
import json
from datetime import datetime
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def display_task_result(task_name: str, result: Dict[str, Any]) -> None:
    """Display task execution result with rich formatting."""
    reflection = result.get("reflection", {})
    status = reflection.get("status", "Unknown")
    confidence = reflection.get("confidence", "N/A")
    summary = reflection.get("summary", "No summary provided.")
    
    status_icon = "✅" if status == "Success" else "⚠️" if status == "Partial" else "❌" if status == "Failed" else "⚪️"
    
    # Explicitly format confidence as a string to avoid rendering issues
    formatted_confidence = f"{confidence:.2f}" if isinstance(confidence, (int, float)) else str(confidence)
    
    # Create a table for the task result
    table = Table(title=f"Task: {task_name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Status", status_icon)
    table.add_row("Confidence", formatted_confidence)
    
    # Add summary if available
    if summary != "No summary provided.":
        table.add_row("Summary", summary)
    
    # Display the table
    console.print(table)
    
    # Display raw output preview if available
    if "raw_output_preview" in result:
        console.print("\nOutput Preview:")
        console.print(Panel(result["raw_output_preview"], title="Raw Output"))

def display_workflow_progress(task_name: str, status: str) -> None:
    """Display workflow execution progress with timestamp."""
    print(f"⏳ [{datetime.now().strftime('%H:%M:%S')}] Task '{task_name}': {status}")

def display_workflow_start(workflow_name: str, run_id: str) -> None:
    """Display workflow start message."""
    print("\n" + "="*80)
    print(f"🚀 STARTING WORKFLOW: {workflow_name} (Run ID: {run_id})")
    print("="*80)

def display_workflow_complete(summary: dict, output_path: str) -> None:
    """Display workflow completion message with results summary."""
    print("\n" + "="*80)
    print(f"🏁 WORKFLOW COMPLETE: {summary['workflow_name']}")
    print(f"   Status: {summary['workflow_status']}")
    print(f"   Duration: {summary['workflow_run_duration_sec']} seconds")
    print(f"   Resonance Report: {summary.get('resonance_summary')}")
    print(f"   Full results saved to: {output_path}")
    print("="*80 + "\n")

def display_workflow_error(error_msg: str, output_path: str) -> None:
    """Display workflow error message."""
    print("\n" + "!"*80)
    print(f"🔥 WORKFLOW FAILED: {error_msg}")
    if output_path != "N/A":
        print(f"   Partial results saved to: {output_path}")
    print("!"*80 + "\n") 