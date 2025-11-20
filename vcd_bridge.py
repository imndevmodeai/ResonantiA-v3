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
import logging
import re

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

# Optional: ask_arche_enhanced_v2 integration (flow routing support)
try:
    from ask_arche_enhanced_v2 import (  # type: ignore
        EnhancedUnifiedArchEConfig as ASKV2_Config,
        EnhancedRealArchEProcessor as ASKV2_Processor
    )
    ASK_V2_AVAILABLE = True
except Exception:
    ASK_V2_AVAILABLE = False

# Optional: CrystallizedObjectiveGenerator (COG)
try:
    from crystallized_objective_generator import (
        CrystallizedObjectiveGenerator,
        SPR
    )
    COG_AVAILABLE = True
except ImportError:
    COG_AVAILABLE = False
    CrystallizedObjectiveGenerator = None
    SPR = None

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
        # Current processing flow: 'aco' (default), 'ask_v2' (if available), 'oge' (Objective Generation Engine - server-side)
        self.current_flow = "aco"
        self.ask_v2_available = ASK_V2_AVAILABLE
        # ---- Stream terminal logs to VCD with emojis ----
        self._install_vcd_logging_handler()
        self._install_stdout_proxy()
        
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
        
        # Initialize COG (CrystallizedObjectiveGenerator) if available
        self.cog = None
        if COG_AVAILABLE and SPR is not None:
            try:
                def load_spr_bank() -> List[SPR]:
                    """Load SPRs from SPRManager for COG"""
                    spr_defs = self.spr_manager.get_all_sprs()
                    spr_list = []
                    for spr_id, spr_data in spr_defs.items():
                        if isinstance(spr_data, dict):
                            # Map SPRManager format to COG SPR dataclass
                            spr_list.append(SPR(
                                id=spr_id,
                                name=spr_data.get("name", spr_id),
                                tags=spr_data.get("tags", []) + [spr_data.get("category", "unknown")],
                                signature=spr_data.get("signature", {}),
                                pattern=spr_data.get("pattern", spr_id),
                                preconditions=spr_data.get("preconditions", {}),
                                effects=spr_data.get("effects", {}),
                                cost=spr_data.get("cost", 1.0),
                                temporal_hint=spr_data.get("temporal_hint"),
                                metadata={
                                    "definition": spr_data.get("definition", ""),
                                    "category": spr_data.get("category", "unknown"),
                                    "relationships": spr_data.get("relationships", {})
                                }
                            ))
                    return spr_list
                
                self.cog = CrystallizedObjectiveGenerator(
                    spr_bank_loader=load_spr_bank,
                    max_candidates=128
                )
                print("✅ CrystallizedObjectiveGenerator (COG) initialized successfully.")
            except Exception as e:
                print(f"⚠️  COG initialization failed: {e}")
                import traceback
                traceback.print_exc()
                self.cog = None
        
        # Instantiate the ACO as the main entry point
        self.aco = AdaptiveCognitiveOrchestrator(
            protocol_chunks=[],  # Let ACO load defaults
            llm_provider=self.llm_provider, # Pass the initialized provider
            event_callback=self.broadcast_event_to_vcd,
            loop=self.loop # Pass the asyncio event loop
        )

        # RISE is now managed by ACO, but we keep a reference for direct access if needed
        self.rise_orchestrator = self.aco.rise_orchestrator

        # Initialize guide accessor for documentation access
        try:
            from Three_PointO_ArchE.vcd_guide_accessor import VCDGuideAccessor
            self.guide_accessor = VCDGuideAccessor()
            print("✅ VCD Guide Accessor initialized.")
        except Exception as e:
            print(f"⚠️  VCD Guide Accessor not available: {e}")
            self.guide_accessor = None

        print("✅ VCD Bridge initialized with ACO and RISE Engine.")

    # ---- Logging and Stdout streaming to VCD ----
    def _install_vcd_logging_handler(self):
        """Attach a logging handler that forwards log records to VCD as rich events with emojis."""
        bridge = self

        class VCDLogHandler(logging.Handler):
            LEVEL_EMOJI = {
                logging.DEBUG: "🧪",
                logging.INFO: "ℹ️",
                logging.WARNING: "⚠️",
                logging.ERROR: "❌",
                logging.CRITICAL: "🔥",
            }
            def emit(self, record: logging.LogRecord):
                try:
                    emoji = self.LEVEL_EMOJI.get(record.levelno, "📝")
                    title = f"{emoji} {record.levelname}"
                    msg = self.format(record)
                    context = {
                        "logger": record.name,
                        "module": record.module,
                        "file": record.pathname,
                        "line": record.lineno,
                        "function": record.funcName,
                        "created": datetime.fromtimestamp(record.created).isoformat(),
                        "process": record.process,
                        "thread": record.thread,
                    }
                    fut = asyncio.run_coroutine_threadsafe(
                        bridge.emit_thought_process(f"{title}: {msg}", context),
                        bridge.loop
                    )
                    # best-effort; don't wait
                except Exception:
                    pass

        handler = VCDLogHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.addHandler(handler)

    def _install_stdout_proxy(self):
        """Mirror stdout/stderr lines to VCD as thought events with emojis and image previews."""
        bridge = self
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        image_pattern = re.compile(r"(https?://\\S+\\.(?:png|jpg|jpeg|gif|webp|svg))", re.IGNORECASE)

        class VCDStreamProxy:
            def __init__(self, wrapped, loop, bridge_ref):
                self._wrapped = wrapped
                self._buffer = []
                self._loop = loop
                self._bridge = bridge_ref
            def _emit_line(self, line: str, stream_name: str):
                # Emit the raw line
                asyncio.run_coroutine_threadsafe(
                    self._bridge.emit_thought_process(f"🖥️ {line}", {"source": stream_name}),
                    self._loop
                )
                # If line contains an image URL, emit a visualization
                m = image_pattern.search(line)
                if m:
                    url = m.group(1)
                    asyncio.run_coroutine_threadsafe(
                        self._bridge.emit_data_visualization(
                            chart_type="image",
                            data={"images": [url]},
                            title="Streamed image from logs",
                            interactive=False
                        ),
                        self._loop
                    )
            def write(self, data):
                try:
                    self._wrapped.write(data)
                    # accumulate until newline
                    for ch in data:
                        if ch == "\n":
                            line = "".join(self._buffer).strip()
                            self._buffer.clear()
                            if line:
                                self._emit_line(line, "stdout")
                        else:
                            self._buffer.append(ch)
                except Exception:
                    # ensure stdout never breaks
                    pass
            def flush(self):
                try:
                    self._wrapped.flush()
                except Exception:
                    pass

        try:
            sys.stdout = VCDStreamProxy(original_stdout, self.loop, self)
            sys.stderr = VCDStreamProxy(original_stderr, self.loop, self)
        except Exception:
            # If proxy fails, keep original stdout
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    def _oge_generate_pipeline(self, query: str) -> List[Dict[str, Any]]:
        """
        Python adaptation of oge/services/objectiveGenerator.ts (generateObjectivePipeline).
        Returns a list of stage dictionaries compatible for simple rendering.
        """
        def get_compression(input_len: int, output_len: int) -> float:
            if output_len == 0:
                return float(input_len)
            return round(input_len / output_len, 2)

        spr_keyword_map = {
            'historical': 'H', 'emergent': 'E', 'causal': 'C', 'predictive': 'F',
            'predicting': 'F', 'temporal': 'T', 'compare': 'Tr', 'matchup': 'Tr',
            'prime': 'H', 'circa': 'T', 'age': 'T'
        }
        import re

        results: List[Dict[str, Any]] = []
        current_input = query
        cumulative_compression = 1.0

        # Stage 1: Feature Extraction
        temporal_markers = ", ".join(re.findall(r"(?:circa\\s+\\d{4}-\\d{4}|age\\s+\\d+-\\d+)", query, flags=re.IGNORECASE))
        domain_keywords = ", ".join([kw for kw in ['boxing', 'match', 'prime'] if kw in query.lower()])
        complexity_indicators = [kw for kw in ['emergent', 'causal', 'predictive'] if kw in query.lower()]
        spr_keywords = [kw for kw in spr_keyword_map.keys() if kw in query.lower()]
        stage1_output = f"⦅temporal:[{temporal_markers}], domain:[{domain_keywords}], complexity:[{', '.join(complexity_indicators)}]⦆"
        stage_compression = get_compression(len(current_input), len(stage1_output))
        cumulative_compression *= stage_compression
        results.append({
            "stageNumber": 1, "title": "Feature Extraction", "symbol": "⦅ F ⦆",
            "input": f"⟦{query}⟧", "output": stage1_output,
            "stageCompression": stage_compression, "cumulativeCompression": round(cumulative_compression, 2)
        })
        current_input = stage1_output

        # Stage 2: TemporalScope Building
        stage2_output = 'Δ⦅explicit:"Historical primes", implicit:"Round-by-round", contextual:"Era differences"⦆'
        stage_compression = get_compression(len(current_input), len(stage2_output))
        cumulative_compression *= stage_compression
        results.append({
            "stageNumber": 2, "title": "TemporalScope Building", "symbol": "Δ⦅ T ⦆",
            "input": current_input, "output": stage2_output,
            "stageCompression": stage_compression, "cumulativeCompression": round(cumulative_compression, 2)
        })
        current_input = stage2_output

        # Stage 3: SPR Activation
        activated_sprs = []
        for kw in spr_keywords:
            sym = spr_keyword_map.get(kw)
            if sym and sym not in activated_sprs:
                activated_sprs.append(sym)
        stage3_output = "⊢" + "⊢".join(activated_sprs) if activated_sprs else ""
        stage_compression = get_compression(len(current_input), len(stage3_output))
        cumulative_compression *= stage_compression
        results.append({
            "stageNumber": 3, "title": "SPR Activation", "symbol": "⊢ SPR ⊢",
            "input": current_input, "output": stage3_output,
            "stageCompression": stage_compression, "cumulativeCompression": round(cumulative_compression, 2)
        })
        current_input = stage3_output

        # Stage 4: Mandate Selection
        mandates = ['⊨Ω']
        if temporal_markers:
            mandates.insert(0, '⊨M₆')
        if len(complexity_indicators) > 0:
            mandates.insert(0, '⊨M₉')
        stage4_output = "".join(mandates)
        stage_compression = get_compression(len(current_input), len(stage4_output))
        cumulative_compression *= stage_compression
        results.append({
            "stageNumber": 4, "title": "Mandate Selection", "symbol": "⊨ M ⊨",
            "input": current_input, "output": stage4_output,
            "stageCompression": stage_compression, "cumulativeCompression": round(cumulative_compression, 2)
        })
        current_input = stage4_output

        # Stage 5: Template Assembly
        stage5_output = "⊧{Apply_full_spectrum...}"
        stage_compression = get_compression(len(current_input), len(stage5_output))
        cumulative_compression *= stage_compression
        results.append({
            "stageNumber": 5, "title": "Template Assembly", "symbol": "⊧ T ⊧",
            "input": current_input, "output": stage5_output,
            "stageCompression": stage_compression, "cumulativeCompression": round(cumulative_compression, 2)
        })
        current_input = stage5_output

        # Stage 6: Domain Customization
        stage6_output = "⊨{boxing_explanations}"
        stage_compression = get_compression(len(current_input), len(stage6_output))
        cumulative_compression *= stage_compression
        results.append({
            "stageNumber": 6, "title": "Domain Customization", "symbol": "⊨ D ⊨",
            "input": current_input, "output": stage6_output,
            "stageCompression": stage_compression, "cumulativeCompression": round(cumulative_compression, 2)
        })
        current_input = stage6_output

        # Stage 7: Final Assembly
        stage7_output = "⟧{problem_description}⟧"
        stage_compression = get_compression(len(current_input), len(stage7_output))
        cumulative_compression *= stage_compression
        results.append({
            "stageNumber": 7, "title": "Final Assembly", "symbol": "⟦ PD ⟧",
            "input": current_input, "output": stage7_output,
            "stageCompression": stage_compression, "cumulativeCompression": round(cumulative_compression, 2)
        })
        current_input = stage7_output

        # Stage 8: Zepto Objective
        try:
            s1 = results[0]["output"]
            s2 = results[1]["output"]
            s3 = results[2]["output"]
            s4 = results[3]["output"]
        except Exception:
            s1 = s2 = s3 = s4 = ""
        zepto_spr = f"⟦Q⟧→{s1[:15]}...→{s2[:10]}...→{s3}→{s4}→⊧T→⊨D→⟧PD⟧"
        final_cumulative = get_compression(len(query), len(zepto_spr))
        results.append({
            "stageNumber": 8, "title": "Zepto Objective", "symbol": "◊ Z ◊",
            "input": current_input, "output": zepto_spr,
            "stageCompression": get_compression(len(current_input), len(zepto_spr)),
            "cumulativeCompression": round(final_cumulative, 2)
        })
        # Stage 9: Crystallized Zepto Objective (display)
        results.append({
            "stageNumber": 9, "title": "Crystallized Zepto Objective", "symbol": "◊",
            "input": query, "output": zepto_spr,
            "stageCompression": 0, "cumulativeCompression": round(final_cumulative, 2)
        })
        return results

    async def process_query_routed(self, prompt: str) -> str:
        """
        Route the query through the selected flow and return a final response string.
        Flows:
          - 'aco' (default): AdaptiveCognitiveOrchestrator.process_query_with_evolution (sync, run in thread)
          - 'ask_v2' (optional): EnhancedRealArchEProcessor.process_query (async)
          - 'oge' (server-side Objective Generation Engine adaptation)
        """
        flow = (self.current_flow or "aco").lower()
        if flow == "ask_v2" and self.ask_v2_available:
            try:
                # Initialize a minimal EnhancedRealArchEProcessor without VCD loopback
                cfg = ASKV2_Config()
                processor = ASKV2_Processor(vcd=None, config=cfg)
                results = await processor.process_query(prompt)
                if isinstance(results, dict) and "response" in results:
                    return str(results["response"])
                return str(results)
            except Exception as e:
                # Fallback to ACO on failure
                await self.emit_thought_process(
                    f"ask_v2 flow failed, falling back to ACO: {e}",
                    {"flow": "ask_v2", "fallback": "aco"}
                )
                return await asyncio.to_thread(self.aco.process_query_with_evolution, prompt)
        if flow == "oge":
            try:
                stages = self._oge_generate_pipeline(prompt)
                # Emit a rich event for visualization (optional)
                try:
                    await self.emit_thought_process("OGE pipeline generated", {"stage_count": len(stages)})
                except Exception:
                    pass
                # Format a readable summary
                lines = []
                for s in stages:
                    lines.append(f"[{s['stageNumber']}] {s['title']} {s['symbol']}")
                    lines.append(f"  input:  {s['input']}")
                    lines.append(f"  output: {s['output']}")
                    lines.append(f"  compression: x{s['stageCompression']}  cumulative: x{s['cumulativeCompression']}")
                return "\n".join(lines)
            except Exception as e:
                await self.emit_thought_process(f"OGE flow failed: {e}", {"flow": "oge"})
                return f"OGE processing failed: {e}"

        # Default ACO path
        return await asyncio.to_thread(self.aco.process_query_with_evolution, prompt)

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
            "flow": self.current_flow,
        })
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    # Handle guide requests
                    if msg_type == "get_guide":
                        await self.handle_guide_request(websocket, data)
                        continue
                    elif msg_type == "list_guides":
                        await self.handle_list_guides_request(websocket)
                        continue
                    elif msg_type == "search_guides":
                        await self.handle_search_guides_request(websocket, data)
                        continue
                    
                    if msg_type == "set_flow":
                        requested = (data.get("flow") or "").lower()
                        allowed = ["aco", "oge"] + (["ask_v2"] if self.ask_v2_available else [])
                        if requested in allowed:
                            self.current_flow = requested
                            await self.send_to_client(websocket, {
                                "type": "system",
                                "message_type": "flow_changed",
                                "content": f"Flow set to {self.current_flow}",
                                "flow": self.current_flow,
                                "timestamp": datetime.now().isoformat(),
                            })
                        else:
                            await self.send_to_client(websocket, {
                                "type": "system",
                                "message_type": "error",
                                "content": f"Unsupported flow '{requested}'. Allowed: {allowed}",
                                "timestamp": datetime.now().isoformat(),
                            })
                    elif msg_type == "get_cognitive_state":
                        await self.send_to_client(websocket, {
                            "type": "cognitive_state",
                            "flow": self.current_flow,
                            "session_id": self.session_id,
                            "timestamp": datetime.now().isoformat(),
                        })
                    elif msg_type == "handshake":
                        await self.send_to_client(websocket, {
                            "type": "system",
                            "message_type": "handshake_ack",
                            "content": "Handshake acknowledged by VCD Bridge",
                            "flow": self.current_flow,
                            "timestamp": datetime.now().isoformat(),
                        })
                    elif msg_type == "query" and "payload" in data:
                        prompt = data["payload"]
                        print(f"▶️ Received query. Flow={self.current_flow} Prompt: {prompt[:80]}...")
                        final_response = await self.process_query_routed(prompt)

                        # Now, broadcast the final response back to the VCD
                        print(f"✅ Processing complete. Broadcasting final response.")
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
    
    # --- Guide Access Methods ---
    
    async def handle_guide_request(self, websocket, data: dict):
        """Handle request for a specific guide."""
        if not self.guide_accessor:
            await self.send_to_client(websocket, {
                "type": "guide_response",
                "error": "Guide accessor not available",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        guide_id = data.get("guide_id") or data.get("component")
        if not guide_id:
            await self.send_to_client(websocket, {
                "type": "guide_response",
                "error": "guide_id or component required",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        guide = self.guide_accessor.get_guide(guide_id)
        if guide:
            await self.send_to_client(websocket, {
                "type": "guide_response",
                "guide": guide,
                "timestamp": datetime.now().isoformat()
            })
        else:
            await self.send_to_client(websocket, {
                "type": "guide_response",
                "error": f"Guide not found: {guide_id}",
                "available_guides": [g["component"] for g in self.guide_accessor.list_guides()],
                "timestamp": datetime.now().isoformat()
            })
    
    async def handle_list_guides_request(self, websocket):
        """Handle request to list all available guides."""
        if not self.guide_accessor:
            await self.send_to_client(websocket, {
                "type": "guides_list_response",
                "error": "Guide accessor not available",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        guides = self.guide_accessor.list_guides()
        await self.send_to_client(websocket, {
            "type": "guides_list_response",
            "guides": guides,
            "total": len(guides),
            "timestamp": datetime.now().isoformat()
        })
    
    async def handle_search_guides_request(self, websocket, data: dict):
        """Handle request to search guides."""
        if not self.guide_accessor:
            await self.send_to_client(websocket, {
                "type": "guides_search_response",
                "error": "Guide accessor not available",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        query = data.get("query", "")
        if not query:
            await self.send_to_client(websocket, {
                "type": "guides_search_response",
                "error": "query parameter required",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        results = self.guide_accessor.search_guides(query)
        await self.send_to_client(websocket, {
            "type": "guides_search_response",
            "query": query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        })

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
