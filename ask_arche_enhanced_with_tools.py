#!/usr/bin/env python3
"""
Enhanced ArchE Query Interface with Comprehensive Tool Inventory & VCD Integration

This is the canonical entry point for interacting with ArchE via natural language,
now enhanced with:
1. Comprehensive startup process showing all registered tools
2. VCD (Visual Cognitive Debugger) integration for rich visualization
3. Real-time tool inventory display in both terminal and VCD UI
4. Complete system status and capability reporting

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
from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

# --- PATH CORRECTION ---
# Ensure the project root is in the Python path to resolve module imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir)) # Project root directory
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- END PATH CORRECTION ---

try:
    from Three_PointO_ArchE.cognitive_integration_hub import CognitiveIntegrationHub
    from Three_PointO_ArchE.action_registry import ActionRegistry
    from Three_PointO_ArchE.logging_config import setup_logging
    from Three_PointO_ArchE.spr_manager import SPRManager
    from Three_PointO_ArchE.temporal_core import now_iso
except ImportError as e:
    print(f"Fatal Error: Could not import ArchE's core modules.")
    print(f"Please run this script from the root of the 'Happier' project directory.")
    print(f"Details: {e}")
    sys.exit(1)

# Initialize Rich Console
console = Console()

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
                "client": "ask_arche_enhanced",
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
    
    async def emit_system_startup(self, tool_inventory: Dict[str, Any]):
        """Emit comprehensive system startup information to VCD"""
        if not self.connected:
            return
            
        await self.send_message({
            "type": "system_startup",
            "tool_inventory": tool_inventory,
            "timestamp": datetime.now().isoformat()
        })
    
    async def emit_tool_registration(self, tool_name: str, tool_info: Dict[str, Any]):
        """Emit individual tool registration to VCD"""
        if not self.connected:
            return
            
        await self.send_message({
            "type": "tool_registered",
            "tool_name": tool_name,
            "tool_info": tool_info,
            "timestamp": datetime.now().isoformat()
        })
    
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

def display_system_banner():
    """Display the comprehensive ArchE system banner"""
    banner_text = """
🧠 **ArchE Enhanced Query Interface with VCD Integration**
═══════════════════════════════════════════════════════════════════════════════
🎯 **Comprehensive Cognitive Architecture**
🔬 **Real-time Visual Cognitive Debugging**
🛠️ **Complete Tool Inventory & Capability Reporting**
🌐 **Multi-modal Analysis & Synthesis**
═══════════════════════════════════════════════════════════════════════════════
"""
    console.print(Panel(banner_text, border_style="bold cyan", expand=False))

def get_tool_categories() -> Dict[str, List[str]]:
    """Get comprehensive tool categories and their tools"""
    return {
        "🧠 Cognitive Engines": [
            "rise_orchestrator", "adaptive_cognitive_orchestrator", 
            "cognitive_integration_hub", "metacognitive_shift_processor"
        ],
        "🔍 Analysis Tools": [
            "causal_inference_tool", "agent_based_modeling_tool", 
            "predictive_modeling_tool", "temporal_reasoning_engine"
        ],
        "📚 Knowledge Management": [
            "spr_manager", "knowledge_graph_manager", 
            "insight_solidification_engine", "autopoietic_self_analysis"
        ],
        "🌐 External Tools": [
            "web_search_tool", "enhanced_web_search_tool", 
            "code_executor", "puppeteer_tool"
        ],
        "🎥 Media Processing": [
            "webcam_streaming_system", "effects_engine", 
            "rtmp_streamer", "droidcam_manager"
        ],
        "🔧 System Tools": [
            "action_registry", "workflow_engine", 
            "error_handler", "session_manager"
        ]
    }

def display_tool_inventory(action_registry: ActionRegistry, vcd: VCDIntegration = None):
    """Display comprehensive tool inventory"""
    
    # Get registered actions - handle the case where list_actions might not be available
    try:
        registered_actions = action_registry.list_actions()
        print(f"DEBUG: Found {len(registered_actions)} actions via list_actions()")
    except AttributeError:
        # Fallback: get actions from the internal registry
        registered_actions = list(action_registry.actions.keys()) if hasattr(action_registry, 'actions') else []
        print(f"DEBUG: Found {len(registered_actions)} actions via actions.keys()")
    
    # If still empty, try to get from the global registry
    if not registered_actions:
        try:
            from Three_PointO_ArchE.action_registry import main_action_registry
            registered_actions = main_action_registry.list_actions()
            print(f"DEBUG: Found {len(registered_actions)} actions via main_action_registry")
        except:
            pass
    
    try:
        action_signatures = action_registry.get_action_signatures()
    except AttributeError:
        # Fallback: create basic signatures
        action_signatures = {action: {"description": "No description available"} for action in registered_actions}
    
    # Create tool inventory data
    tool_inventory = {
        "total_tools": len(registered_actions),
        "registered_actions": registered_actions,
        "action_signatures": action_signatures,
        "tool_categories": get_tool_categories(),
        "system_status": {
            "action_registry": "active",
            "cognitive_hub": "active", 
            "vcd_integration": "connected" if vcd and vcd.connected else "disconnected",
            "timestamp": now_iso()
        }
    }
    
    # Display in terminal
    console.print("\n" + "="*80)
    console.print("[bold green]🛠️  COMPREHENSIVE TOOL INVENTORY[/bold green]")
    console.print("="*80)
    
    # Tool count summary
    console.print(f"[bold cyan]Total Registered Tools: {len(registered_actions)}[/bold cyan]")
    
    # Display by categories
    categories = get_tool_categories()
    for category, tools in categories.items():
        console.print(f"\n[bold yellow]{category}[/bold yellow]")
        console.print("-" * len(category))
        
        # Find tools that match this category
        matching_tools = [tool for tool in registered_actions if any(cat_tool in tool.lower() for cat_tool in tools)]
        
        if matching_tools:
            for tool in matching_tools:
                console.print(f"  ✅ {tool}")
                # Get tool signature if available
                if tool in action_signatures:
                    sig = action_signatures[tool]
                    console.print(f"     📝 {sig.get('description', 'No description available')}")
        else:
            console.print("  ⚠️  No tools found in this category")
    
    # Display all registered actions
    console.print(f"\n[bold magenta]📋 ALL REGISTERED ACTIONS ({len(registered_actions)}):[/bold magenta]")
    console.print("-" * 50)
    
    for i, action in enumerate(registered_actions, 1):
        console.print(f"{i:3d}. {action}")
        if action in action_signatures:
            sig = action_signatures[action]
            if 'description' in sig:
                console.print(f"     📄 {sig['description']}")
    
    # System status
    console.print(f"\n[bold green]🟢 SYSTEM STATUS:[/bold green]")
    console.print(f"  • Action Registry: Active ({len(registered_actions)} tools)")
    console.print(f"  • Cognitive Hub: Active")
    console.print(f"  • VCD Integration: {'Connected' if vcd and vcd.connected else 'Disconnected'}")
    console.print(f"  • Timestamp: {now_iso()}")
    
    console.print("="*80)
    
    # Emit to VCD if connected
    if vcd and vcd.connected:
        asyncio.create_task(vcd.emit_system_startup(tool_inventory))
    
    return tool_inventory

def display_system_capabilities():
    """Display ArchE system capabilities"""
    capabilities_text = """
🚀 **ArchE System Capabilities**

🧠 **Cognitive Processing:**
  • RISE Enhanced Synergistic Inquiry
  • Adaptive Cognitive Orchestration (ACO)
  • Metacognitive Self-Correction
  • Quantum-Inspired Perception

🔬 **Analysis & Modeling:**
  • Temporal Causal Inference (PCMCI+)
  • Agent-Based Modeling (Mesa Framework)
  • Predictive Time Series Analysis
  • Comparative Fluxual Processing

📚 **Knowledge Management:**
  • Sparse Priming Representations (SPRs)
  • Knowledge Graph Operations
  • Autopoietic Self-Analysis
  • Insight Solidification & Learning

🌐 **External Integration:**
  • Enhanced Web Search & Analysis
  • Safe Code Execution Sandbox
  • Web Automation & Scraping
  • Real-time Data Processing

🎥 **Media Processing:**
  • AI-Driven Video Effects
  • Multi-platform RTMP Streaming
  • DroidCam Integration
  • Virtual Camera Support

🔧 **System Features:**
  • IAR-Compliant Workflow Execution
  • Real-time Error Handling
  • Session Management & Persistence
  • Visual Cognitive Debugging (VCD)
"""
    console.print(Panel(capabilities_text, title="System Capabilities", border_style="green"))

async def main_async():
    """
    Enhanced ArchE query interface with comprehensive tool inventory and VCD integration.
    """
    # --- Setup Logging ---
    setup_logging()
    
    # Display system banner
    display_system_banner()
    
    # --- Initialize VCD Integration ---
    vcd = VCDIntegration()
    vcd_connected = await vcd.connect()
    
    # --- Initialize ArchE Core Components ---
    console.print("\n[bold blue]🔧 Initializing ArchE Core Components...[/bold blue]")
    
    # Get the global action registry (where actions are actually registered)
    try:
        from Three_PointO_ArchE.action_registry import main_action_registry
        action_registry = main_action_registry
        console.print("[green]✅ Using global action registry[/green]")
    except ImportError:
        # Fallback: create new instance
        action_registry = ActionRegistry()
        console.print("[yellow]⚠️  Using new action registry instance[/yellow]")
    
    # Initialize cognitive integration hub
    cognitive_hub = CognitiveIntegrationHub()
    
    # Initialize SPR manager with proper filepath
    spr_filepath = os.path.join(project_root, "knowledge_tapestry.json")
    if not os.path.exists(spr_filepath):
        # Create a basic knowledge tapestry file if it doesn't exist
        basic_tapestry = {
            "spr_definitions": [],
            "total_sprs": 0,
            "creation_date": now_iso(),
            "version": "1.0"
        }
        with open(spr_filepath, 'w') as f:
            json.dump(basic_tapestry, f, indent=2)
    
    spr_manager = SPRManager(spr_filepath=spr_filepath)
    
    console.print("[green]✅ Core components initialized successfully[/green]")
    
    # --- Display Comprehensive Tool Inventory ---
    tool_inventory = display_tool_inventory(action_registry, vcd)
    
    # --- Display System Capabilities ---
    display_system_capabilities()
    
    # --- Query Processing ---
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        console.print(Panel(f"[bold cyan]Submitting Custom Query:[/] '{query}'", expand=False, border_style="cyan"))
    else:
        query = "Please perform a comprehensive system analysis and show me all available capabilities."
        console.print(Panel(f"[bold cyan]Submitting Default Query:[/] '{query}'", expand=False, border_style="cyan"))
    
    # --- VCD Analysis Start ---
    if vcd_connected:
        await vcd.start_analysis(query, "RISE")
        await vcd.emit_thought_process("Starting ArchE cognitive processing with full tool inventory", {
            "query": query,
            "total_tools": tool_inventory["total_tools"],
            "registered_actions": tool_inventory["registered_actions"]
        })
    
    # --- Execution ---
    try:
        # Phase 1: Traditional ArchE Processing
        if vcd_connected:
            await vcd.emit_phase_start("ArchE Processing", "Executing query through CognitiveIntegrationHub with full tool access")
        
        console.print(f"\n[bold blue]🚀 Executing query with {tool_inventory['total_tools']} available tools...[/bold blue]")
        
        # Phase 2: Query Execution
        if vcd_connected:
            await vcd.emit_thought_process("Routing query through cognitive architecture with comprehensive tool access", {
                "method": "CognitiveIntegrationHub",
                "available_tools": tool_inventory["total_tools"]
            })
        
        results = cognitive_hub.route_query(query)
        
        if vcd_connected:
            await vcd.emit_phase_complete("ArchE Processing", "Query execution completed successfully with full tool inventory")
        
        console.print("[bold green]✅ Execution Complete.[/bold green]")
        console.print("-" * 50)
        
        # Phase 3: Results Processing
        if vcd_connected:
            await vcd.emit_phase_start("Results Processing", "Formatting and presenting results")
        
        # --- Present the Final Results ---
        present_results(results)
        
        if vcd_connected:
            await vcd.emit_phase_complete("Results Processing", "Results formatted and presented")
            await vcd.emit_thought_process("ArchE query processing completed with comprehensive tool inventory", {
                "status": "success",
                "tools_used": tool_inventory["total_tools"]
            })
        
        console.rule("[bold yellow]Demonstration Complete[/bold yellow]")
        console.print("The script has demonstrated a full, protocol-compliant query path with comprehensive tool inventory and VCD integration.")
        
    except Exception as e:
        if vcd_connected:
            await vcd.emit_thought_process(f"Error occurred: {str(e)}", {"error": True})
        
        console.print(f"\n[bold red]An unexpected error occurred during the demonstration:[/bold red]")
        console.print_exception(show_locals=True)
    
    finally:
        # --- Cleanup ---
        if vcd_connected:
            await vcd.disconnect()

def present_results(results):
    """Present the results in a formatted way"""
    if isinstance(results, dict):
        if "status" in results:
            if results["status"] == "success":
                console.print("[green]✅ Query executed successfully![/green]")
                if "output" in results:
                    output = results["output"]
                    if isinstance(output, dict):
                        for key, value in output.items():
                            console.print(f"[cyan]{key}:[/cyan] {value}")
                    else:
                        console.print(f"[cyan]Output:[/cyan] {output}")
            else:
                console.print(f"[red]❌ Query failed: {results.get('message', 'Unknown error')}[/red]")
        else:
            console.print(f"[yellow]Results:[/yellow] {results}")
    else:
        console.print(f"[yellow]Results:[/yellow] {results}")

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
