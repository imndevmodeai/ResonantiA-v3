#!/usr/bin/env python3
"""
VCD Bridge - Visual Cognitive Debugger Backend (LIVE INTEGRATION)
Connects the actual ArchE cognitive core to the VCD frontend via WebSocket.
Enhanced with rich interactive capabilities for research-grade analysis.
"""
import asyncio
import json
import websockets
import sys
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Ensure the ArchE modules can be imported by adding the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
    from Three_PointO_ArchE.sirc_intake_handler import SIRCIntakeHandler, SircIntentPacket
    from Three_PointO_ArchE.spr_manager import SPRManager
    from Three_PointO_ArchE.adaptive_cognitive_orchestrator import AdaptiveCognitiveOrchestrator
    from Three_PointO_ArchE.llm_providers import get_llm_provider, LLMProviderError
    print("✅ Successfully imported ArchE core components.")
except ImportError as e:
    print(f"❌ Failed to import ArchE core components: {e}")
    print("Ensure you have run `export PYTHONPATH=$PYTHONPATH:./Three_PointO_ArchE:./Four_PointO_ArchE`")
    sys.exit(1)

# For running non-async methods in the event loop
import asyncio
from concurrent.futures import ThreadPoolExecutor

WS_PORT = 8765
WS_HOST = "0.0.0.0"

class VCDEventType(Enum):
    """Enhanced VCD event types with rich media support"""
    ANALYSIS_START = "analysis_start"
    PHASE_START = "phase_start"
    WEB_SEARCH = "web_search"
    WEB_BROWSE = "web_browse"
    CODE_EXECUTION = "code_execution"
    SIMULATION_RUN = "simulation_run"
    DATA_VISUALIZATION = "data_visualization"
    STRATEGY_SYNTHESIS = "strategy_synthesis"
    THOUGHT_PROCESS = "thought_process"
    PHASE_COMPLETE = "phase_complete"
    ANALYSIS_COMPLETE = "analysis_complete"

@dataclass
class VCDRichEvent:
    """Enhanced VCD event with rich media support"""
    event_id: str
    event_type: VCDEventType
    timestamp: str
    phase: str
    title: str
    description: str
    
    # Rich media components
    links: List[Dict[str, Any]] = None
    code_blocks: List[Dict[str, Any]] = None
    simulations: List[Dict[str, Any]] = None
    visualizations: List[Dict[str, Any]] = None
    
    # Interactive elements
    expandable: bool = True
    drill_down_enabled: bool = False
    interactive: bool = False
    
    # Metadata
    metadata: Dict[str, Any] = None
    tags: List[str] = None

class VCDBridge:
    def __init__(self):
        self.connected_clients = set()
        self.loop = asyncio.get_event_loop()
        self.session_id = f"vcd_session_{uuid.uuid4().hex[:8]}"
        self.current_phase = None
        self.analysis_start_time = None
        
        # --- LLM Provider Initialization ---
        try:
            # The get_llm_provider factory will handle API keys from env vars
            self.llm_provider = get_llm_provider("google") 
            print("✅ LLM Provider initialized successfully.")
        except (LLMProviderError, ValueError) as e:
            print(f"❌ CRITICAL: LLM Provider initialization failed: {e}")
            print("   Ensure GEMINI_API_KEY or OPENAI_API_KEY is set in your environment.")
            self.llm_provider = None


        # Correct Initialization:
        # Provide the correct, existing path to the SPRManager.
        spr_file_path = "knowledge_graph/spr_definitions_tv.json"
        self.spr_manager = SPRManager(spr_filepath=spr_file_path)
        
        # Pass the created spr_manager to the SIRC handler.
        self.sirc_handler = SIRCIntakeHandler(spr_manager=self.spr_manager)
        
        # Instantiate the ACO as the main entry point
        self.aco = AdaptiveCognitiveOrchestrator(
            protocol_chunks=[],  # Let ACO load defaults
            llm_provider=self.llm_provider, # Pass the initialized provider
            event_callback=self.broadcast_event_to_vcd,
            loop=self.loop # Pass the asyncio event loop
        )

        # RISE is now managed by ACO, but we keep a reference for direct access if needed
        self.rise_orchestrator = self.aco.rise_orchestrator

        print("✅ VCD Bridge initialized with ACO and RISE Engine.")

    async def broadcast_event_to_vcd(self, event_data: dict):
        """Callback for ACO/RISE to send events to the VCD."""
        # Check if this is a rich event
        if event_data.get("type") == "rich_event":
            # This is already a rich event, broadcast as-is
            await self.broadcast_to_all(event_data)
        else:
            # This is a basic event, broadcast as-is for backward compatibility
            await self.broadcast_to_all(event_data)

        
        
        

    async def handle_client(self, websocket, path=None):
        """Register client and handle incoming messages."""
        self.connected_clients.add(websocket)
        print(f"VCD client connected from {websocket.remote_address}. Total clients: {len(self.connected_clients)}")
        
        await self.send_to_client(websocket, {
            "type": "system",
            "message_type": "system",
            "content": "VCD Bridge connected to LIVE ArchE Core. Ready for directives.",
            "timestamp": datetime.now().isoformat(),
        })
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get("type") == "query" and "payload" in data:
                        prompt = data["payload"]
                        print(f"▶️ Received query. Passing to ACO: {prompt[:80]}...")
                        
                        # The ACO is the new entry point.
                        # Since process_query_with_evolution is synchronous, run it in an executor
                        # to avoid blocking the WebSocket's async event loop.
                        with ThreadPoolExecutor() as executor:
                            future = self.loop.run_in_executor(
                                executor, 
                                self.aco.process_query_with_evolution, 
                                prompt
                            )
                            # Await the result from the synchronous function.
                            final_response = await future

                            # Now, broadcast the final response back to the VCD
                            print(f"✅ ACO processing complete. Broadcasting final response.")
                            await self.broadcast_to_all({
                                "type": "event",
                                "event": "final_response",
                                "timestamp": datetime.now().isoformat(),
                                "payload": {
                                    "content": final_response,
                                    "content_type": "text"
                                }
                            })
                        
                except json.JSONDecodeError:
                    print(f"Received non-JSON message: {message}")

        finally:
            self.connected_clients.discard(websocket)
            print(f"VCD client disconnected. Total clients: {len(self.connected_clients)}")

    # --- Rich Event Emission Methods ---
    
    async def emit_rich_event(self, event: VCDRichEvent):
        """Emit a rich VCD event to all connected clients."""
        event_dict = asdict(event)
        event_dict['event_type'] = event.event_type.value
        
        await self.broadcast_to_all({
            "type": "rich_event",
            "event": event.event_type.value,
            "timestamp": event.timestamp,
            "payload": event_dict
        })
    
    async def emit_web_search(self, query: str, results: List[Dict[str, Any]], search_engine: str = "google"):
        """Emit interactive web search results"""
        links = []
        for result in results:
            links.append({
                'url': result.get('url', ''),
                'title': result.get('title', ''),
                'description': result.get('snippet', ''),
                'domain': result.get('domain', ''),
                'clickable': True
            })
        
        event = VCDRichEvent(
            event_id=f"web_search_{uuid.uuid4().hex[:8]}",
            event_type=VCDEventType.WEB_SEARCH,
            timestamp=datetime.utcnow().isoformat() + "Z",
            phase=self.current_phase or "Unknown",
            title=f"Web Search: {query}",
            description=f"Found {len(results)} results for '{query}'",
            links=links,
            expandable=True,
            drill_down_enabled=True,
            interactive=True,
            metadata={
                "query": query,
                "search_engine": search_engine,
                "result_count": len(results)
            },
            tags=["web_search", "research", "data_collection"]
        )
        
        await self.emit_rich_event(event)
    
    async def emit_code_execution(self, code: str, language: str, result: str = None,
                                execution_time: float = None, parameters: Dict[str, Any] = None,
                                interactive: bool = False):
        """Emit expandable code execution block"""
        code_block = {
            'code': code,
            'language': language,
            'execution_result': result,
            'execution_time': execution_time,
            'parameters': parameters,
            'interactive': interactive,
            'expandable': True
        }
        
        event = VCDRichEvent(
            event_id=f"code_exec_{uuid.uuid4().hex[:8]}",
            event_type=VCDEventType.CODE_EXECUTION,
            timestamp=datetime.utcnow().isoformat() + "Z",
            phase=self.current_phase or "Unknown",
            title=f"Code Execution ({language})",
            description=f"Executed {language} code with {len(code)} characters",
            code_blocks=[code_block],
            expandable=True,
            drill_down_enabled=True,
            interactive=interactive,
            metadata={
                "language": language,
                "code_length": len(code),
                "execution_time": execution_time,
                "has_result": result is not None
            },
            tags=["code_execution", "programming", language.lower()]
        )
        
        await self.emit_rich_event(event)
    
    async def emit_thought_process(self, message: str, context: Dict[str, Any] = None):
        """Emit thought process step"""
        event = VCDRichEvent(
            event_id=f"thought_{uuid.uuid4().hex[:8]}",
            event_type=VCDEventType.THOUGHT_PROCESS,
            timestamp=datetime.utcnow().isoformat() + "Z",
            phase=self.current_phase or "Unknown",
            title="Thought Process",
            description=message,
            expandable=True,
            interactive=False,
            metadata=context or {},
            tags=["thought", "process", "reasoning"]
        )
        
        await self.emit_rich_event(event)
    
    async def emit_data_visualization(self, chart_type: str, data: Dict[str, Any], title: str, interactive: bool = True):
        """Emit rich data visualization"""
        visualization = {
            'chart_type': chart_type,
            'data': data,
            'title': title,
            'interactive': interactive,
            'drill_down_enabled': True
        }
        
        event = VCDRichEvent(
            event_id=f"viz_{uuid.uuid4().hex[:8]}",
            event_type=VCDEventType.DATA_VISUALIZATION,
            timestamp=datetime.utcnow().isoformat() + "Z",
            phase=self.current_phase or "Unknown",
            title=f"Visualization: {title}",
            description=f"{chart_type.title()} chart with {len(data)} data points",
            visualizations=[visualization],
            expandable=True,
            drill_down_enabled=True,
            interactive=interactive,
            metadata={
                "chart_type": chart_type,
                "data_points": len(data),
                "title": title
            },
            tags=["visualization", "data", "chart", chart_type.lower()]
        )
        
        await self.emit_rich_event(event)
    
    async def emit_simulation(self, simulation_id: str, name: str, parameters: Dict[str, Any],
                            results: Dict[str, Any], execution_time: float = None, run_count: int = 1):
        """Emit interactive simulation results with real-time parameter adjustment"""
        simulation = {
            'simulation_id': simulation_id,
            'name': name,
            'parameters': parameters,
            'results': results,
            'interactive': True,
            'run_count': run_count,
            'execution_time': execution_time,
            'parameter_adjustment_enabled': True
        }
        
        event = VCDRichEvent(
            event_id=f"simulation_{uuid.uuid4().hex[:8]}",
            event_type=VCDEventType.SIMULATION_RUN,
            timestamp=datetime.utcnow().isoformat() + "Z",
            phase=self.current_phase or "Unknown",
            title=f"Simulation: {name}",
            description=f"Ran {run_count} simulation(s) with {len(parameters)} parameters",
            simulations=[simulation],
            expandable=True,
            drill_down_enabled=True,
            interactive=True,
            metadata={
                "simulation_id": simulation_id,
                "name": name,
                "parameter_count": len(parameters),
                "run_count": run_count,
                "execution_time": execution_time
            },
            tags=["simulation", "modeling", "analysis"]
        )
        
        await self.emit_rich_event(event)
    
    async def emit_strategy_synthesis(self, strategy_name: str, components: List[str], analysis_depth: str = "comprehensive"):
        """Emit strategy synthesis results with drill-down exploration"""
        event = VCDRichEvent(
            event_id=f"strategy_{uuid.uuid4().hex[:8]}",
            event_type=VCDEventType.STRATEGY_SYNTHESIS,
            timestamp=datetime.utcnow().isoformat() + "Z",
            phase=self.current_phase or "Unknown",
            title=f"Strategy Synthesis: {strategy_name}",
            description=f"Synthesized {len(components)} strategic components",
            expandable=True,
            drill_down_enabled=True,
            interactive=True,
            metadata={
                "strategy_name": strategy_name,
                "component_count": len(components),
                "analysis_depth": analysis_depth,
                "components": components
            },
            tags=["strategy", "synthesis", "analysis"]
        )
        
        await self.emit_rich_event(event)
    
    async def emit_phase_start(self, phase_name: str, phase_description: str):
        """Start a new analysis phase"""
        self.current_phase = phase_name
        
        event = VCDRichEvent(
            event_id=f"phase_start_{uuid.uuid4().hex[:8]}",
            event_type=VCDEventType.PHASE_START,
            timestamp=datetime.utcnow().isoformat() + "Z",
            phase=phase_name,
            title=f"Phase {phase_name} Started",
            description=phase_description,
            expandable=True,
            interactive=True,
            metadata={
                "phase_name": phase_name,
                "phase_description": phase_description
            },
            tags=["phase", "start", phase_name.lower()]
        )
        
        await self.emit_rich_event(event)
    
    async def emit_phase_complete(self, phase_name: str, results_summary: str):
        """Complete a phase with summary"""
        event = VCDRichEvent(
            event_id=f"phase_complete_{uuid.uuid4().hex[:8]}",
            event_type=VCDEventType.PHASE_COMPLETE,
            timestamp=datetime.utcnow().isoformat() + "Z",
            phase=phase_name,
            title=f"Phase {phase_name} Complete",
            description=results_summary,
            expandable=True,
            interactive=True,
            metadata={
                "phase_name": phase_name,
                "completion_time": datetime.utcnow().isoformat() + "Z"
            },
            tags=["phase", "complete", phase_name.lower()]
        )
        
        await self.emit_rich_event(event)
    
    async def emit_web_browse(self, url: str, title: str, content: str, images: List[str] = None):
        """Emit web page browsing results with rich media"""
        links = [{
            'url': url, 
            'title': title, 
            'description': content[:200] + "...",
            'clickable': True,
            'preview_available': True
        }]
        
        event = VCDRichEvent(
            event_id=f"web_browse_{uuid.uuid4().hex[:8]}",
            event_type=VCDEventType.WEB_BROWSE,
            timestamp=datetime.utcnow().isoformat() + "Z",
            phase=self.current_phase or "Unknown",
            title=f"Browsed: {title}",
            description=f"Analyzed content from {url}",
            links=links,
            expandable=True,
            drill_down_enabled=True,
            interactive=True,
            metadata={
                "url": url,
                "title": title,
                "content_length": len(content),
                "image_count": len(images) if images else 0,
                "images": images or []
            },
            tags=["web_browse", "content_analysis"]
        )
        
        await self.emit_rich_event(event)
    
    async def start_analysis(self, problem_description: str, analysis_type: str = "RISE"):
        """Start a new analysis session"""
        self.analysis_start_time = datetime.utcnow()
        self.current_phase = "Initialization"
        
        event = VCDRichEvent(
            event_id=f"analysis_start_{uuid.uuid4().hex[:8]}",
            event_type=VCDEventType.ANALYSIS_START,
            timestamp=self.analysis_start_time.isoformat() + "Z",
            phase="Initialization",
            title=f"{analysis_type} Analysis Started",
            description=f"Beginning comprehensive analysis: {problem_description[:200]}...",
            expandable=True,
            interactive=True,
            metadata={
                "problem_description": problem_description,
                "analysis_type": analysis_type,
                "session_id": self.session_id
            },
            tags=["analysis", "start", analysis_type.lower()]
        )
        
        await self.emit_rich_event(event)
        return self.session_id

    async def send_to_client(self, websocket, message):
        """Send message to a specific client."""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            self.connected_clients.discard(websocket)
    
    async def broadcast_to_all(self, message):
        """Broadcast message to all connected clients."""
        if self.connected_clients:
            await asyncio.gather(
                *[self.send_to_client(client, message) for client in self.connected_clients],
                return_exceptions=True
            )

async def main():
    bridge = VCDBridge()
    
    if not bridge.rise_orchestrator:
        print("❌ Halting server start due to RISE initialization failure.", file=sys.stderr)
        return
        
    print(f"🚀 Starting LIVE VCD Bridge on {WS_HOST}:{WS_PORT}")
    print("Waiting for VCD frontend to connect...")
    
    async with websockets.serve(bridge.handle_client, WS_HOST, WS_PORT):
        await asyncio.Future()

if __name__ == "__main__":
    # Note: For this to work, you may need to run this from the root of the Happier project
    # and ensure the PYTHONPATH is set correctly.
    # export PYTHONPATH=$PYTHONPATH:./Three_PointO_ArchE:./Four_PointO_ArchE
    asyncio.run(main())
