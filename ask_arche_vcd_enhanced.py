"""
Enhanced ArchE Query Interface with Visual Cognitive Debugger Integration

This is the canonical entry point for interacting with ArchE via natural language,
now enhanced with VCD (Visual Cognitive Debugger) integration for rich visualization
and debugging of the cognitive process.

It uses the CognitiveDispatch module to correctly triage and route the user's
query to the appropriate internal cognitive engine (ACO or RISE), while providing
real-time visual feedback through the VCD system.
"""

import sys
import os
import argparse
import asyncio
import json
import websockets
import time
from datetime import datetime
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.table import Table
from rich.text import Text

# --- PATH CORRECTION ---
# Ensure the project root is in the Python path to resolve module imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir)) # Project root directory
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- END PATH CORRECTION ---

try:
    from Three_PointO_ArchE.cognitive_integration_hub import CognitiveIntegrationHub
    from Three_PointO_ArchE.logging_config import setup_logging
except ImportError as e:
    print(f"Fatal Error: Could not import ArchE's core modules.")
    print(f"Please run this script from the root of the 'Happier' project directory.")
    print(f"Details: {e}")
    sys.exit(1)

# Initialize Rich Console
console = Console()

def create_query_superposition(query: str) -> Dict[str, float]:
    """
    Creates a quantum superposition of intents from a query.
    
    This is the first point of Universal Abstraction application - treating
    the query as a superposition of possible intents that will collapse
    into specific processing paths based on confidence thresholds.
    
    Args:
        query: The natural language query string
        
    Returns:
        Dictionary mapping intent types to probability amplitudes
    """
    import re
    import numpy as np
    
    # Initialize base superposition with uncertainty
    superposition = {
        "generic_inquiry": 0.3,  # Default uncertainty
        "analysis_request": 0.0,
        "content_generation": 0.0,
        "code_execution": 0.0,
        "research_task": 0.0,
        "creative_synthesis": 0.0,
        "system_analysis": 0.0,
        "strategic_planning": 0.0
    }
    
    query_lower = query.lower()
    
    # Intent detection based on keywords and patterns
    if any(word in query_lower for word in ["analyze", "analysis", "evaluate", "assess", "examine"]):
        superposition["analysis_request"] = 0.8
    if any(word in query_lower for word in ["create", "generate", "build", "develop", "design"]):
        superposition["content_generation"] = 0.7
    if any(word in query_lower for word in ["execute", "run", "implement", "code", "script"]):
        superposition["code_execution"] = 0.9
    if any(word in query_lower for word in ["research", "find", "search", "investigate", "discover"]):
        superposition["research_task"] = 0.8
    if any(word in query_lower for word in ["creative", "innovative", "novel", "fusion", "synthesis"]):
        superposition["creative_synthesis"] = 0.7
    if any(word in query_lower for word in ["system", "architecture", "health", "status", "monitor"]):
        superposition["system_analysis"] = 0.8
    if any(word in query_lower for word in ["strategy", "plan", "roadmap", "blueprint", "framework"]):
        superposition["strategic_planning"] = 0.8
    
    # Normalize probabilities to ensure they sum to 1.0 (quantum constraint)
    total_prob = sum(superposition.values())
    if total_prob > 0:
        normalized_superposition = {k: v / total_prob for k, v in superposition.items()}
    else:
        # Fallback to uniform distribution if no patterns detected
        normalized_superposition = {k: 1.0 / len(superposition) for k in superposition.keys()}
    
    # Add quantum state representation with all non-zero amplitudes
    quantum_terms = []
    for intent, prob in normalized_superposition.items():
        if intent != "quantum_state" and prob > 0.01:  # Only include significant amplitudes
            amplitude = np.sqrt(prob)
            quantum_terms.append(f"{amplitude:.3f}|{intent}⟩")
    
    if quantum_terms:
        normalized_superposition["quantum_state"] = f"|ψ⟩ = {' + '.join(quantum_terms)}"
    else:
        normalized_superposition["quantum_state"] = "|ψ⟩ = 1.000|generic_inquiry⟩"
    
    return normalized_superposition

class VCDIntegration:
    """Visual Cognitive Debugger Integration for ArchE"""
    
    def __init__(self, vcd_host: str = "localhost", vcd_port: int = 8765):
        self.vcd_host = vcd_host
        self.vcd_port = vcd_port
        self.websocket = None
        self.connected = False
        self.session_id = None
        
    async def connect(self) -> bool:
        """Connect to the VCD Bridge"""
        try:
            uri = f"ws://{self.vcd_host}:{self.vcd_port}"
            console.print(f"[blue]Connecting to VCD Bridge at {uri}...[/blue]")
            
            self.websocket = await websockets.connect(uri)
            self.connected = True
            
            # Send initial handshake
            await self.send_message({
                "type": "handshake",
                "client": "ask_arche",
                "timestamp": datetime.now().isoformat()
            })
            
            console.print("[green]✅ Connected to VCD Bridge[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Failed to connect to VCD Bridge: {e}[/red]")
            console.print("[yellow]Continuing without VCD integration...[/yellow]")
            return False
    
    async def disconnect(self):
        """Disconnect from VCD Bridge"""
        if self.websocket and self.connected:
            await self.websocket.close()
            self.connected = False
            console.print("[blue]Disconnected from VCD Bridge[/blue]")
    
    async def send_message(self, message: Dict[str, Any]):
        """Send message to VCD Bridge"""
        if self.connected and self.websocket:
            try:
                await self.websocket.send(json.dumps(message))
            except Exception as e:
                console.print(f"[red]Failed to send VCD message: {e}[/red]")
    
    async def send_query(self, query: str) -> Optional[str]:
        """Send query to VCD Bridge and get response"""
        if not self.connected:
            return None
            
        try:
            # Send the query
            await self.send_message({
                "type": "query",
                "payload": query,
                "timestamp": datetime.now().isoformat(),
                "client": "ask_arche"
            })
            
            # Wait for response
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get("type") == "event" and data.get("event") == "final_response":
                return data.get("payload", {}).get("content", "")
            
            return None
            
        except Exception as e:
            console.print(f"[red]Error communicating with VCD: {e}[/red]")
            return None
    
    async def start_analysis(self, problem_description: str, analysis_type: str = "RISE"):
        """Start VCD analysis session"""
        if not self.connected:
            return
            
        await self.send_message({
            "type": "start_analysis",
            "problem_description": problem_description,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        })
    
    async def emit_thought_process(self, message: str, context: Dict[str, Any] = None):
        """Emit thought process to VCD"""
        if not self.connected:
            return
            
        await self.send_message({
            "type": "thought_process",
            "message": message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        })
    
    async def emit_phase_start(self, phase_name: str, description: str):
        """Emit phase start to VCD"""
        if not self.connected:
            return
            
        await self.send_message({
            "type": "phase_start",
            "phase_name": phase_name,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
    
    async def emit_phase_complete(self, phase_name: str, results: str):
        """Emit phase completion to VCD"""
        if not self.connected:
            return
            
        await self.send_message({
            "type": "phase_complete",
            "phase_name": phase_name,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })

async def main_async():
    """
    Enhanced ArchE query interface with VCD integration.
    Routes queries through both traditional ArchE processing and VCD visualization.
    """
    # --- Setup Logging ---
    setup_logging()

    console.rule("[bold yellow]ArchE Query Interface with VCD Integration[/bold yellow]")

    # --- Initialize VCD Integration ---
    vcd = VCDIntegration()
    vcd_connected = await vcd.connect()

    # --- Query Definitions ---
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        console.print(Panel(f"[bold cyan]Submitting Custom Query:[/] '{query}'", expand=False, border_style="cyan"))
    else:
        query = "Analyze the current state of artificial intelligence development, research emerging trends in autonomous systems, evaluate the potential impact on human society, and synthesize a comprehensive strategic report with recommendations for ethical AI governance."
        console.print(Panel(f"[bold cyan]Submitting Default Query:[/] '{query}'", expand=False, border_style="cyan"))

    # --- VCD Analysis Start ---
    if vcd_connected:
        await vcd.start_analysis(query, "RISE")
        await vcd.emit_thought_process("Starting ArchE cognitive processing", {"query": query})

    # --- Execution ---
    try:
        # Phase 0: Query Superposition Analysis (NEW - First Point)
        if vcd_connected:
            await vcd.emit_phase_start("Query Superposition Analysis", "Analyzing query as quantum superposition of intents")
        
        # Create quantum superposition of query intents
        query_superposition = create_query_superposition(query)
        
        # Display superposition analysis in console
        console.print("[bold blue]🔬 Query Superposition Analysis[/bold blue]")
        console.print(f"[cyan]Quantum State:[/cyan] {query_superposition.get('quantum_state', 'N/A')}")
        console.print("[cyan]Intent Probabilities:[/cyan]")
        for intent, prob in query_superposition.items():
            if intent != "quantum_state" and prob > 0:
                bar_length = int(prob * 20)  # Scale to 20 chars max
                bar = "█" * bar_length + "░" * (20 - bar_length)
                console.print(f"  {intent:<20}: {prob:.3f} {bar}")
        
        if vcd_connected:
            await vcd.emit_thought_process("Query superposition created", {
                "superposition": query_superposition,
                "quantum_state": query_superposition.get('quantum_state', 'N/A'),
                "dominant_intent": max(query_superposition.items(), key=lambda x: x[1] if x[0] != "quantum_state" else 0)
            })
        
        # Phase 1: Traditional ArchE Processing
        if vcd_connected:
            await vcd.emit_phase_start("ArchE Processing", "Executing query through CognitiveIntegrationHub")
        
        dispatcher = CognitiveIntegrationHub()
        
        # Phase 2: Query Execution with Superposition Context
        if vcd_connected:
            await vcd.emit_thought_process("Routing query through cognitive architecture", {
                "method": "CognitiveIntegrationHub",
                "superposition_context": query_superposition
            })
        
        # Pass superposition context to the dispatcher
        results = dispatcher.route_query(query, superposition_context=query_superposition)
        
        if vcd_connected:
            await vcd.emit_phase_complete("ArchE Processing", "Query execution completed successfully")
        
        console.print("[bold green]Execution Complete.[/bold green]")
        console.print("-" * 50)
        
        # Phase 3: Results Processing
        if vcd_connected:
            await vcd.emit_phase_start("Results Processing", "Formatting and presenting results")
        
        # --- Present the Final Results ---
        present_results(results)
        
        if vcd_connected:
            await vcd.emit_phase_complete("Results Processing", "Results formatted and presented")
            await vcd.emit_thought_process("ArchE query processing completed", {"status": "success"})

        console.rule("[bold yellow]Demonstration Complete[/bold yellow]")
        console.print("The script has demonstrated a full, protocol-compliant query path with VCD integration.")

    except Exception as e:
        if vcd_connected:
            await vcd.emit_thought_process(f"Error occurred: {str(e)}", {"error": True})
        
        console.print(f"\\n[bold red]An unexpected error occurred during the demonstration:[/bold red]")
        console.print_exception(show_locals=True)
    
    finally:
        # --- Cleanup ---
        if vcd_connected:
            await vcd.disconnect()

def present_results(results: Dict[str, Any]):
    """
    Formats and presents the final results of the ArchE run.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join("outputs", f"arche_report_{timestamp}.md")
    os.makedirs("outputs", exist_ok=True)

    final_answer = "No final answer synthesized."
    thought_trail = ""

    if results:
        # Look for any task that contains generated_text (RISE workflows generate synthesis tasks)
        # Find task keys (exclude metadata keys)
        metadata_keys = {'workflow_name', 'workflow_run_id', 'workflow_status', 'workflow_run_duration_sec', 'task_statuses', 'initial_context', 'workflow_definition'}
        task_keys = [key for key in results.keys() if key not in metadata_keys]
        
        # Look for synthesis task output in any task
        for task_name in task_keys:
            task_output = results[task_name]
            if "result" in task_output and isinstance(task_output["result"], dict):
                result_data = task_output["result"]
                if "generated_text" in result_data:
                    final_answer = result_data["generated_text"]
                    break  # Found the synthesis result, stop lookingcd /media/newbu/3626C55326C514B1/Happier/youscrape/backend && node server.mjs
        
        # Format the full thought trail
        try:
            # Create a clean context for the thought trail (exclude metadata)
            metadata_keys = {'workflow_name', 'workflow_run_id', 'workflow_status', 'workflow_run_duration_sec', 'task_statuses', 'initial_context', 'workflow_definition'}
            thought_trail_data = {key: value for key, value in results.items() if key not in metadata_keys}
            json_str = json.dumps(thought_trail_data, indent=4)
            thought_trail = f"```json\n{json_str}\n```"
        except Exception as e:
            thought_trail = f"Error formatting thought trail: {e}"

    # Now, write the report with the extracted answer
    with open(report_path, "w") as f:
        f.write("# ArchE Cognitive Run Report\n\n")
        f.write(f"**Timestamp:** {timestamp}\n\n")
        f.write("## Final Synthesized Result\n\n")
        f.write(f"{final_answer}\n\n")

        # --- NEW: Key Action Summaries Section ---
        f.write("## Key Action Summaries\n\n")
        if results:
            # Find task keys (exclude metadata keys)
            metadata_keys = {'workflow_name', 'workflow_run_id', 'workflow_status', 'workflow_run_duration_sec', 'task_statuses', 'initial_context', 'workflow_definition'}
            task_keys = [key for key in results.keys() if key not in metadata_keys]
            
            for task_name in task_keys:
                if task_name not in ["A1_comprehensive_knowledge_scaffolding", "J10_pre_synthesis_summary", "K11_genius_synthesis"]:
                    task_output = results[task_name]
                    result_data = task_output.get("result", {})
                    if "input_parameters" in result_data and "key_findings" in result_data:
                        f.write(f"### {task_name}\n\n")
                        f.write("**Input Parameters:**\n")
                        f.write(f"```json\n{json.dumps(result_data['input_parameters'], indent=2)}\n```\n\n")
                        f.write("**Key Findings:**\n")
                        for finding in result_data['key_findings']:
                            f.write(f"- {finding}\n")
                        f.write("\n")

        f.write("## Complete Thought Trail (IAR)\n\n")
        f.write(thought_trail)

    # Console Output
    console = Console()
    console.rule("[bold green]Final Synthesized Result[/bold green]")
    console.print(Markdown(final_answer))
    console.print(Panel(f"Full report saved to [bold cyan]{report_path}[/]", expand=False, border_style="green"))


def main():
    """
    Synchronous wrapper for the async main function.
    """
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
