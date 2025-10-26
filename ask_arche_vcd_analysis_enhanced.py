#!/usr/bin/env python3
"""
Enhanced ArchE Query Interface with VCD Analysis Agent Integration
Integrates specialized VCD analysis agent with RISE engine for comprehensive analysis
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
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from Three_PointO_ArchE.cognitive_integration_hub import CognitiveIntegrationHub
    from Three_PointO_ArchE.logging_config import setup_logging
    from vcd_analysis_agent import VCDAnalysisAgent, VCDAnalysisResult
except ImportError as e:
    print(f"Fatal Error: Could not import ArchE's core modules.")
    print(f"Please run this script from the root of the 'Happier' project directory.")
    print(f"Details: {e}")
    sys.exit(1)

# Initialize Rich Console
console = Console()

class VCDAnalysisIntegration:
    """Enhanced VCD Analysis Integration for ArchE with RISE engine"""
    
    def __init__(self, vcd_host: str = "localhost", vcd_port: int = 8765):
        self.vcd_host = vcd_host
        self.vcd_port = vcd_port
        self.websocket = None
        self.connected = False
        self.session_id = None
        self.vcd_analysis_agent = VCDAnalysisAgent()
        
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
                "client": "ask_arche_vcd_analysis",
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
    
    async def perform_vcd_analysis(self, query: str) -> VCDAnalysisResult:
        """Perform comprehensive VCD analysis using specialized agent"""
        console.print("[cyan]🔍 Performing comprehensive VCD analysis...[/cyan]")
        
        # Emit analysis start to VCD
        if self.connected:
            await self.send_message({
                "type": "vcd_analysis_start",
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "client": "ask_arche_vcd_analysis"
            })
        
        # Perform comprehensive VCD analysis
        analysis_result = await self.vcd_analysis_agent.perform_comprehensive_vcd_analysis()
        
        # Emit analysis results to VCD
        if self.connected:
            await self.send_message({
                "type": "vcd_analysis_complete",
                "results": {
                    "status": analysis_result.vcd_status,
                    "components_analyzed": len(analysis_result.component_analysis),
                    "integrations_analyzed": len(analysis_result.integration_analysis),
                    "recommendations_count": len(analysis_result.recommendations)
                },
                "timestamp": datetime.now().isoformat(),
                "client": "ask_arche_vcd_analysis"
            })
        
        return analysis_result
    
    async def emit_thought_process(self, message: str, context: Dict[str, Any] = None):
        """Emit thought process to VCD"""
        if self.connected:
            await self.send_message({
                "type": "thought_process",
                "message": message,
                "context": context or {},
                "timestamp": datetime.now().isoformat(),
                "client": "ask_arche_vcd_analysis"
            })
    
    async def emit_phase_start(self, phase_name: str, description: str):
        """Emit phase start to VCD"""
        if self.connected:
            await self.send_message({
                "type": "phase_start",
                "phase_name": phase_name,
                "description": description,
                "timestamp": datetime.now().isoformat(),
                "client": "ask_arche_vcd_analysis"
            })
    
    async def emit_phase_complete(self, phase_name: str, results: str):
        """Emit phase completion to VCD"""
        if self.connected:
            await self.send_message({
                "type": "phase_complete",
                "phase_name": phase_name,
                "results": results,
                "timestamp": datetime.now().isoformat(),
                "client": "ask_arche_vcd_analysis"
            })

async def main_async():
    """
    Enhanced ArchE query interface with VCD analysis agent integration.
    Routes queries through traditional ArchE processing, VCD analysis, and RISE engine.
    """
    # --- Setup Logging ---
    setup_logging()

    console.rule("[bold yellow]ArchE Query Interface with VCD Analysis Agent[/bold yellow]")

    # --- Initialize VCD Analysis Integration ---
    vcd_analysis = VCDAnalysisIntegration()
    vcd_connected = await vcd_analysis.connect()

    # --- Query Definitions ---
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        console.print(Panel(f"[bold cyan]Submitting Custom Query:[/] '{query}'", expand=False, border_style="cyan"))
    else:
        query = "Analyze the current state of the VCD system and provide comprehensive insights."
        console.print(Panel(f"[bold cyan]Submitting Default Query:[/] '{query}'", expand=False, border_style="cyan"))

    # --- Execution ---
    try:
        # Phase 1: VCD Analysis (NEW)
        if vcd_connected:
            await vcd_analysis.emit_phase_start("VCD Analysis", "Performing comprehensive VCD system analysis")
        
        console.print("[bold blue]Phase 1: VCD Analysis[/bold blue]")
        vcd_analysis_result = await vcd_analysis.perform_vcd_analysis(query)
        
        if vcd_connected:
            await vcd_analysis.emit_phase_complete("VCD Analysis", "VCD analysis completed successfully")
        
        # Phase 2: Traditional ArchE Processing
        if vcd_connected:
            await vcd_analysis.emit_phase_start("ArchE Processing", "Executing query through CognitiveIntegrationHub")
        
        console.print("[bold blue]Phase 2: ArchE Processing[/bold blue]")
        dispatcher = CognitiveIntegrationHub()
        
        if vcd_connected:
            await vcd_analysis.emit_thought_process("Routing query through cognitive architecture", {"method": "CognitiveIntegrationHub"})
        
        results = dispatcher.route_query(query)
        
        if vcd_connected:
            await vcd_analysis.emit_phase_complete("ArchE Processing", "Query execution completed successfully")
        
        console.print("[bold green]Execution Complete.[/bold green]")
        console.print("-" * 50)
        
        # Phase 3: Results Processing and VCD Integration
        if vcd_connected:
            await vcd_analysis.emit_phase_start("Results Processing", "Formatting and presenting results with VCD insights")
        
        console.print("[bold blue]Phase 3: Results Processing[/bold blue]")
        
        # --- Present the Final Results with VCD Analysis ---
        present_enhanced_results(results, vcd_analysis_result)
        
        if vcd_connected:
            await vcd_analysis.emit_phase_complete("Results Processing", "Results formatted and presented with VCD insights")
            await vcd_analysis.emit_thought_process("ArchE query processing completed with VCD analysis", {"status": "success"})

        console.rule("[bold yellow]Demonstration Complete[/bold yellow]")
        console.print("The script has demonstrated a full, protocol-compliant query path with VCD analysis agent integration.")

    except Exception as e:
        if vcd_connected:
            await vcd_analysis.emit_thought_process(f"Error occurred: {str(e)}", {"error": True})
        
        console.print(f"\n[bold red]An unexpected error occurred during the demonstration:[/bold red]")
        console.print_exception(show_locals=True)
    
    finally:
        # --- Cleanup ---
        if vcd_connected:
            await vcd_analysis.disconnect()

def present_enhanced_results(results: Dict[str, Any], vcd_analysis: VCDAnalysisResult):
    """
    Formats and presents the final results of the ArchE run with VCD analysis insights.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join("outputs", f"arche_vcd_analysis_report_{timestamp}.md")
    os.makedirs("outputs", exist_ok=True)

    final_answer = "No final answer synthesized."
    thought_trail = ""

    if results:
        # Extract final synthesis
        if "output" in results and "K11_genius_synthesis" in results["output"]:
            synthesis_output = results["output"]["K11_genius_synthesis"]
            if "result" in synthesis_output and isinstance(synthesis_output["result"], dict):
                final_result_data = synthesis_output["result"]
                if "generated_text" in final_result_data:
                    final_answer = final_result_data["generated_text"]
        
        # Format thought trail
        try:
            if "final_context" in results:
                json_str = json.dumps(results["final_context"], indent=4)
                thought_trail = f"```json\n{json_str}\n```"
        except Exception as e:
            thought_trail = f"Error formatting thought trail: {e}"

    # Write enhanced report with VCD analysis
    with open(report_path, "w") as f:
        f.write("# ArchE Query Report with VCD Analysis\n\n")
        f.write(f"**Timestamp:** {timestamp}\n\n")
        
        # VCD Analysis Section
        f.write("## VCD Analysis Results\n\n")
        f.write(f"**Analysis Type:** {vcd_analysis.analysis_type}\n")
        f.write(f"**Overall Status:** {vcd_analysis.vcd_status['overall_status']}\n")
        f.write(f"**Analysis Session ID:** {vcd_analysis.analysis_session_id}\n\n")
        
        # Component Analysis
        f.write("### Component Analysis\n\n")
        for component, analysis in vcd_analysis.component_analysis.items():
            f.write(f"#### {component.replace('_', ' ').title()}\n")
            f.write(f"Status: {analysis.get('status', 'unknown')}\n")
            if 'error' in analysis:
                f.write(f"Error: {analysis['error']}\n")
            f.write("\n")
        
        # Integration Analysis
        f.write("### Integration Analysis\n\n")
        for integration, analysis in vcd_analysis.integration_analysis.items():
            f.write(f"#### {integration.replace('_', ' ').title()}\n")
            f.write(f"Status: {analysis.get('status', 'unknown')}\n")
            if 'error' in analysis:
                f.write(f"Error: {analysis['error']}\n")
            f.write("\n")
        
        # Performance Metrics
        f.write("### Performance Metrics\n\n")
        f.write(f"Performance Rating: {vcd_analysis.performance_metrics.get('performance_rating', 'unknown')}\n")
        f.write(f"Generation Time: {vcd_analysis.performance_metrics.get('cognitive_data_generation_time', 0):.3f}s\n\n")
        
        # Recommendations
        f.write("### Recommendations\n\n")
        for i, rec in enumerate(vcd_analysis.recommendations, 1):
            f.write(f"{i}. {rec}\n")
        f.write("\n")
        
        # RISE Insights
        f.write("### RISE Engine Insights\n\n")
        if vcd_analysis.ris_e_insights.get("status") == "completed":
            f.write("RISE Analysis: Completed successfully\n")
            f.write(f"Insights Generated: {len(vcd_analysis.ris_e_insights.get('insights', []))}\n")
            if vcd_analysis.ris_e_insights.get('strategic_recommendations'):
                f.write(f"Strategic Recommendations: {vcd_analysis.ris_e_insights['strategic_recommendations']}\n")
        else:
            f.write(f"RISE Analysis: {vcd_analysis.ris_e_insights.get('status', 'unknown')}\n")
        f.write("\n")
        
        # Traditional Results
        f.write("## Final Synthesized Result\n\n")
        f.write(f"{final_answer}\n\n")

        # Key Action Summaries
        f.write("## Key Action Summaries\n\n")
        if results and "output" in results:
            for task_name, task_output in results["output"].items():
                if task_name not in ["A1_comprehensive_knowledge_scaffolding", "J10_pre_synthesis_summary", "K11_genius_synthesis"]:
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
    console.rule("[bold green]VCD Analysis Results[/bold green]")
    
    # Display VCD Analysis Summary
    vcd_table = Table(title="VCD Analysis Summary")
    vcd_table.add_column("Component", style="cyan")
    vcd_table.add_column("Status", style="green")
    vcd_table.add_column("Details", style="yellow")
    
    for component, analysis in vcd_analysis.component_analysis.items():
        status = analysis.get('status', 'unknown')
        details = str(analysis.get('error', 'OK'))[:50] if 'error' in analysis else 'OK'
        vcd_table.add_row(component.replace('_', ' ').title(), status, details)
    
    console.print(vcd_table)
    
    # Display Recommendations
    console.print("\n[bold blue]Key Recommendations:[/bold blue]")
    for i, rec in enumerate(vcd_analysis.recommendations[:5], 1):  # Show top 5
        console.print(f"{i}. {rec}")
    
    # Display Traditional Results
    console.rule("[bold green]Final Synthesized Result[/bold green]")
    console.print(Markdown(final_answer))
    console.print(Panel(f"Enhanced report saved to [bold cyan]{report_path}[/]", expand=False, border_style="green"))

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



