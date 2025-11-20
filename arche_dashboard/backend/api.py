#!/usr/bin/env python3
"""
ArchE Dashboard Backend API
============================

FastAPI-based backend providing:
- Thought trail access and visualization
- Real-time query processing
- WebSocket communication
- Cursor ArchE conversation interface
- IAR-compliant endpoints

ResonantiA Protocol v3.5-GP
"""

import os
import sys
import json
import sqlite3
import asyncio
import io
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from queue import Queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

# Import terminal capturer
try:
    from .terminal_capturer import TerminalOutputCapturer, RichConsoleCapturer, stream_terminal_output
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    from terminal_capturer import TerminalOutputCapturer, RichConsoleCapturer, stream_terminal_output

# Import ArchE components
try:
    from Three_PointO_ArchE.thought_trail import ThoughtTrail
    from Three_PointO_ArchE.llm_providers import get_llm_provider
    from Three_PointO_ArchE.spr_manager import SPRManager
    ARCHE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ArchE components not fully available: {e}")
    ARCHE_AVAILABLE = False

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
THOUGHT_TRAIL_DB = PROJECT_ROOT / "Three_PointO_ArchE" / "ledgers" / "thought_trail.db"
SPR_DEFINITIONS = PROJECT_ROOT / "knowledge_graph" / "spr_definitions_tv.json"
SESSION_DIR = PROJECT_ROOT / "Three_PointO_ArchE" / "ledgers" / "sessions"

# Create FastAPI app
app = FastAPI(
    title="ArchE Dashboard API",
    description="Backend API for ArchE Cognitive Dashboard",
    version="3.5-GP"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager with proper isolation
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.query_output_queues: Dict[str, Queue] = {}  # Maps query_id to output queue
        self.connection_queries: Dict[WebSocket, List[str]] = {}  # Track queries per connection
        self.active_processors: Dict[str, Any] = {}  # Track active processors by query_id
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
            self.connection_queries[websocket] = []
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        async def _disconnect():
            async with self._lock:
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)
                
                # Clean up queries for this connection
                if websocket in self.connection_queries:
                    query_ids = self.connection_queries[websocket].copy()
                    for query_id in query_ids:
                        self.cleanup_query(query_id)
                    del self.connection_queries[websocket]
                
                logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")
        
        # Run cleanup in background
        asyncio.create_task(_disconnect())

    async def broadcast(self, message: dict):
        """Broadcast message to all active connections."""
        disconnected = []
        async with self._lock:
            for connection in self.active_connections.copy():
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Error broadcasting to connection: {e}")
                    disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_to_connection(self, websocket: WebSocket, message: dict):
        """Send message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Error sending to connection: {e}")
            self.disconnect(websocket)
    
    def create_output_queue(self, query_id: str) -> Queue:
        """Create an output queue for a query."""
        queue = Queue()
        self.query_output_queues[query_id] = queue
        return queue
    
    def remove_output_queue(self, query_id: str):
        """Remove an output queue for a query."""
        if query_id in self.query_output_queues:
            del self.query_output_queues[query_id]
    
    def register_query(self, websocket: WebSocket, query_id: str):
        """Register a query for a connection."""
        if websocket not in self.connection_queries:
            self.connection_queries[websocket] = []
        self.connection_queries[websocket].append(query_id)
    
    def register_processor(self, query_id: str, processor: Any):
        """Register an active processor for cleanup tracking."""
        self.active_processors[query_id] = processor
    
    def cleanup_query(self, query_id: str):
        """Clean up all resources for a query."""
        # Remove output queue
        self.remove_output_queue(query_id)
        
        # Clean up processor if exists
        if query_id in self.active_processors:
            processor = self.active_processors.pop(query_id)
            # Schedule async cleanup
            async def cleanup_processor():
                try:
                    if hasattr(processor, 'shutdown'):
                        await processor.shutdown()
                except Exception as e:
                    logger.warning(f"Error cleaning up processor for {query_id}: {e}")
            
            asyncio.create_task(cleanup_processor())
    
    def get_active_queries_count(self) -> int:
        """Get count of active queries."""
        return len(self.query_output_queues)
    
    def get_connection_count(self) -> int:
        """Get count of active connections."""
        return len(self.active_connections)

manager = ConnectionManager()

# Helper function to clean result for JSON serialization
def clean_result_for_json(result: Any) -> Any:
    """Recursively clean result dictionary to remove non-serializable objects."""
    if isinstance(result, dict):
        cleaned = {}
        for key, value in result.items():
            # Skip config objects and other non-serializable objects
            if key == 'config' or 'EnhancedUnifiedArchEConfig' in str(type(value)):
                continue
            # Skip other complex objects that can't be serialized
            if hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool, type(None))):
                # Try to extract serializable attributes if it's a simple object
                try:
                    cleaned[key] = {k: v for k, v in value.__dict__.items() 
                                   if isinstance(v, (str, int, float, bool, type(None), dict, list))}
                except:
                    continue
            else:
                cleaned[key] = clean_result_for_json(value)
        return cleaned
    elif isinstance(result, list):
        return [clean_result_for_json(item) for item in result]
    else:
        # For primitive types, return as-is
        if isinstance(result, (str, int, float, bool, type(None))):
            return result
        # For other types, try to convert to string or skip
        try:
            return str(result)
        except:
            return None

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    provider: Optional[str] = "groq"
    model: Optional[str] = None
    max_tokens: Optional[int] = 8192
    temperature: Optional[float] = 0.7
    use_rise: Optional[bool] = True
    enhanced_query: Optional[str] = None  # Use enhanced query if provided
    detected_sprs: Optional[List[str]] = None  # Pre-identified SPRs from enhanced query
    required_capabilities: Optional[List[str]] = None  # Pre-identified capabilities from enhanced query

class ThoughtTrailQuery(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: Optional[int] = 100
    query_text: Optional[str] = None
    min_confidence: Optional[float] = None

class QueryEnhancementRequest(BaseModel):
    query: str
    enhancement_level: Optional[str] = "auto"  # 'minimal', 'moderate', 'comprehensive', 'auto'

# ==================== THOUGHT TRAIL ENDPOINTS ====================

@app.get("/api/thought-trail/recent")
async def get_recent_thought_trail(limit: int = 50):
    """Get recent thought trail entries from the database."""
    if not THOUGHT_TRAIL_DB.exists():
        raise HTTPException(status_code=404, detail="Thought trail database not found")
    
    try:
        conn = sqlite3.connect(str(THOUGHT_TRAIL_DB))
        cursor = conn.cursor()
        
        query = """
        SELECT 
            event_id,
            entry_id,
            timestamp_utc,
            source_manifestation,
            action_type,
            iar_intention,
            iar_action_details,
            iar_reflection,
            confidence,
            metadata
        FROM thought_trail
        ORDER BY event_id DESC
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        entries = []
        for row in rows:
            # Parse JSON fields
            try:
                iar_action_details = json.loads(row[6]) if row[6] else {}
                iar_reflection = json.loads(row[7]) if row[7] else {}
                metadata = json.loads(row[9]) if row[9] else {}
            except:
                iar_action_details = {}
                iar_reflection = {}
                metadata = {}
            
            # Extract query from iar_action_details or iar_intention
            query_text = ""
            if isinstance(iar_action_details, dict):
                query_text = iar_action_details.get("query") or iar_action_details.get("input") or ""
            if not query_text:
                query_text = row[5]  # iar_intention as fallback
            
            # Extract response from iar_reflection
            response_preview = ""
            if isinstance(iar_reflection, dict):
                response_preview = iar_reflection.get("response") or iar_reflection.get("output") or iar_reflection.get("text") or ""
            
            entries.append({
                "event_id": row[0],
                "entry_id": row[1],
                "timestamp": row[2],
                "source_manifestation": row[3],
                "action_type": row[4],
                "query": query_text[:200] if query_text else "",  # Truncate for preview
                "response_preview": str(response_preview)[:200] if response_preview else "",
                "confidence": row[8] if row[8] is not None else 0.0,
                "processing_method": row[4],  # Use action_type
                "iar_summary": {
                    "intention": row[5],
                    "action": iar_action_details,
                    "reflection": iar_reflection
                },
                "spr_context": metadata.get("spr_context", {}) if isinstance(metadata, dict) else {}
            })
        
        conn.close()
        return {"entries": entries, "count": len(entries)}
        
    except Exception as e:
        logger.error(f"Thought trail query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/thought-trail/search")
async def search_thought_trail(query: ThoughtTrailQuery):
    """Search thought trail with filters."""
    if not THOUGHT_TRAIL_DB.exists():
        raise HTTPException(status_code=404, detail="Thought trail database not found")
    
    try:
        conn = sqlite3.connect(str(THOUGHT_TRAIL_DB))
        cursor = conn.cursor()
        
        sql = """
        SELECT 
            event_id,
            entry_id,
            timestamp_utc,
            source_manifestation,
            action_type,
            iar_intention,
            iar_action_details,
            iar_reflection,
            confidence,
            metadata
        FROM thought_trail WHERE 1=1
        """
        params = []
        
        if query.start_date:
            sql += " AND timestamp_utc >= ?"
            params.append(query.start_date)
        
        if query.end_date:
            sql += " AND timestamp_utc <= ?"
            params.append(query.end_date)
        
        if query.query_text:
            sql += " AND (iar_intention LIKE ? OR iar_action_details LIKE ? OR iar_reflection LIKE ?)"
            search_term = f"%{query.query_text}%"
            params.extend([search_term, search_term, search_term])
        
        if query.min_confidence is not None:
            sql += " AND confidence >= ?"
            params.append(query.min_confidence)
        
        sql += " ORDER BY event_id DESC LIMIT ?"
        params.append(query.limit or 100)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        entries = []
        for row in rows:
            # Parse JSON fields
            try:
                iar_action_details = json.loads(row[6]) if row[6] else {}
                iar_reflection = json.loads(row[7]) if row[7] else {}
                metadata = json.loads(row[9]) if row[9] else {}
            except:
                iar_action_details = {}
                iar_reflection = {}
                metadata = {}
            
            # Extract query from iar_action_details or iar_intention
            query_text = ""
            if isinstance(iar_action_details, dict):
                query_text = iar_action_details.get("query") or iar_action_details.get("input") or ""
            if not query_text:
                query_text = row[5]  # iar_intention as fallback
            
            # Extract response from iar_reflection
            response_preview = ""
            if isinstance(iar_reflection, dict):
                response_preview = iar_reflection.get("response") or iar_reflection.get("output") or iar_reflection.get("text") or ""
            
            entries.append({
                "event_id": row[0],
                "entry_id": row[1],
                "timestamp": row[2],
                "source_manifestation": row[3],
                "action_type": row[4],
                "query": query_text[:200] if query_text else "",
                "response_preview": str(response_preview)[:200] if response_preview else "",
                "confidence": row[8] if row[8] is not None else 0.0,
                "processing_method": row[4],
                "iar_summary": {
                    "intention": row[5],
                    "action": iar_action_details,
                    "reflection": iar_reflection
                },
                "spr_context": metadata.get("spr_context", {}) if isinstance(metadata, dict) else {}
            })
        
        conn.close()
        return {"entries": entries, "count": len(entries), "query": query.dict()}
        
    except Exception as e:
        logger.error(f"Thought trail search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/api/thought-trail/stats")
async def get_thought_trail_stats():
    """Get overall statistics from thought trail."""
    if not THOUGHT_TRAIL_DB.exists():
        raise HTTPException(status_code=404, detail="Thought trail database not found")
    
    try:
        conn = sqlite3.connect(str(THOUGHT_TRAIL_DB))
        cursor = conn.cursor()
        
        # Total entries
        cursor.execute("SELECT COUNT(*) FROM thought_trail")
        total_entries = cursor.fetchone()[0]
        
        # Average confidence
        cursor.execute("SELECT AVG(confidence) FROM thought_trail WHERE confidence IS NOT NULL")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        # Entries by action type (instead of provider)
        cursor.execute("SELECT action_type, COUNT(*) FROM thought_trail GROUP BY action_type")
        by_action_type = dict(cursor.fetchall())
        
        # Recent activity (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM thought_trail WHERE timestamp_utc >= ?", (yesterday,))
        recent_24h = cursor.fetchone()[0]
        
        # SPR usage stats - check metadata for spr_context
        cursor.execute("SELECT COUNT(*) FROM thought_trail WHERE metadata IS NOT NULL AND metadata != ''")
        entries_with_metadata = cursor.fetchone()[0]
        
        # Count entries with SPR context in metadata
        queries_with_sprs = 0
        if entries_with_metadata > 0:
            cursor.execute("SELECT metadata FROM thought_trail WHERE metadata IS NOT NULL AND metadata != ''")
            for row in cursor.fetchall():
                try:
                    metadata = json.loads(row[0]) if row[0] else {}
                    if isinstance(metadata, dict) and metadata.get("spr_context"):
                        queries_with_sprs += 1
                except:
                    pass
        
        conn.close()
        
        return {
            "total_entries": total_entries,
            "average_confidence": round(avg_confidence, 3),
            "providers_used": by_action_type,  # Using action_type as proxy
            "recent_24h": recent_24h,
            "queries_with_spr_priming": queries_with_sprs,
            "database_path": str(THOUGHT_TRAIL_DB)
        }
        
    except Exception as e:
        logger.error(f"Thought trail stats error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

# ==================== QUERY PROCESSING ENDPOINTS ====================

@app.post("/api/query/submit")
async def submit_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """Submit a query to ArchE for processing."""
    
    processor = None
    try:
        # Import ask_arche functionality
        sys.path.insert(0, str(PROJECT_ROOT))
        from ask_arche_enhanced_v2 import EnhancedRealArchEProcessor, EnhancedUnifiedArchEConfig, EnhancedVCDIntegration
        
        # Use enhanced query if provided, otherwise use original query
        actual_query = request.enhanced_query if request.enhanced_query else request.query
        
        # Initialize config with dynamic parameters from dashboard selections
        # Disable Cursor auto-detection if user explicitly selected a provider
        enable_auto_detect = request.provider is None or request.provider == "cursor"
        config = EnhancedUnifiedArchEConfig(
            provider=request.provider,
            model=request.model,
            use_rise=request.use_rise,
            enable_cursor_auto_detect=enable_auto_detect
        )
        
        logger.info(f"Config initialized: provider={config.llm_provider}, model={config.llm_config.get('model')}, use_rise={config.use_rise}, enhanced_query={'yes' if request.enhanced_query else 'no'}")
        
        logger.info(f"🔧 Creating EnhancedVCDIntegration and EnhancedRealArchEProcessor...")
        vcd = EnhancedVCDIntegration(config)
        processor = EnhancedRealArchEProcessor(vcd, config)
        logger.info(f"✅ Processor created successfully")
        
        # Process query with pre-identified SPRs and capabilities from enhanced query
        logger.info(f"🚀 CALLING processor.process_query() with query length: {len(actual_query)}, SPRs: {len(request.detected_sprs) if request.detected_sprs else 0}, Capabilities: {len(request.required_capabilities) if request.required_capabilities else 0}")
        result = await processor.process_query(
            actual_query,
            pre_identified_sprs=request.detected_sprs,
            pre_identified_capabilities=request.required_capabilities
        )
        logger.info(f"✅ processor.process_query() RETURNED. Result type: {type(result)}, Is dict: {isinstance(result, dict)}")
        
        # Ensure result is a dictionary (process_query might return string or dict)
        if isinstance(result, str):
            # If result is a string, wrap it in a proper structure
            result = {
                "response": {
                    "text": result,
                    "reflection": {
                        "confidence": 0.5,  # Default confidence for string responses
                        "status": "completed"
                    }
                },
                "llm_provider": "unknown",
                "processing_method": "direct"
            }
        elif not isinstance(result, dict):
            # If result is neither string nor dict, convert to dict
            result = {
                "response": {
                    "text": str(result),
                    "reflection": {
                        "confidence": 0.5,
                        "status": "completed"
                    }
                },
                "llm_provider": "unknown",
                "processing_method": "direct"
            }
        
        # Broadcast to WebSocket clients
        confidence = 0.0
        try:
            if isinstance(result, dict):
                confidence = result.get("response", {}).get("reflection", {}).get("confidence", 0.0)
        except (AttributeError, TypeError):
            confidence = 0.0
        
        await manager.broadcast({
            "type": "query_complete",
            "timestamp": datetime.now().isoformat(),
            "query": request.query,
            "confidence": confidence
        })
        
        # Clean result to remove non-serializable objects
        clean_result = clean_result_for_json(result)
        
        return {
            "status": "success",
            "query": request.query,
            "result": clean_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")
    finally:
        # CRITICAL: Always shutdown processor to close browser instances
        if processor:
            try:
                await processor.shutdown()
            except Exception as e:
                logger.error(f"Error during processor shutdown: {e}")
        
        # Additional safety: Force cleanup of any orphaned browser processes
        try:
            sys.path.insert(0, os.path.join(str(PROJECT_ROOT), "Three_PointO_ArchE"))
            from browser_cleanup import cleanup_browser_processes
            cleanup_browser_processes()
        except Exception as e:
            logger.debug(f"Browser cleanup utility not available or failed: {e}")

@app.post("/api/query/stream")
async def stream_query(request: QueryRequest):
    """Stream query responses in real-time using Server-Sent Events."""
    
    async def event_generator():
        processor = None
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from ask_arche_enhanced_v2 import EnhancedRealArchEProcessor, EnhancedUnifiedArchEConfig, EnhancedVCDIntegration
            
            config = EnhancedUnifiedArchEConfig()
            vcd = EnhancedVCDIntegration(config)
            processor = EnhancedRealArchEProcessor(vcd, config)
            
            # Send initial event
            yield f"data: {json.dumps({'type': 'start', 'query': request.query})}\n\n"
            
            # Process query with pre-identified SPRs and capabilities
            result = await processor.process_query(
                request.query,
                pre_identified_sprs=request.detected_sprs,
                pre_identified_capabilities=request.required_capabilities
            )
            
            # Stream response chunks
            response_text = result.get("response", {}).get("text", "")
            chunk_size = 50
            
            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i:i+chunk_size]
                yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"
                await asyncio.sleep(0.01)  # Small delay for streaming effect
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'complete', 'result': result})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            # CRITICAL: Always shutdown processor to close browser instances
            if processor:
                try:
                    await processor.shutdown()
                except Exception as e:
                    logger.error(f"Error during processor shutdown: {e}")
            
            # Additional safety: Force cleanup of any orphaned browser processes
            try:
                sys.path.insert(0, os.path.join(str(PROJECT_ROOT), "Three_PointO_ArchE"))
                from browser_cleanup import cleanup_browser_processes
                cleanup_browser_processes()
            except Exception as e:
                logger.debug(f"Browser cleanup utility not available or failed: {e}")
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ==================== SPR MANAGEMENT ENDPOINTS ====================

@app.get("/api/sprs/list")
async def list_sprs(limit: Optional[int] = None, offset: int = 0):
    """List all available SPRs with optional pagination."""
    if not SPR_DEFINITIONS.exists():
        raise HTTPException(status_code=404, detail="SPR definitions not found")
    
    try:
        with open(SPR_DEFINITIONS, 'r') as f:
            all_sprs = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(all_sprs, dict):
            # Convert dict to list
            sprs_list = list(all_sprs.values()) if all_sprs else []
        elif isinstance(all_sprs, list):
            sprs_list = all_sprs
        else:
            sprs_list = []
        
        total_count = len(sprs_list)
        
        # Apply pagination if requested
        if limit is not None and limit > 0:
            start = offset
            end = start + limit
            sprs_list = sprs_list[start:end]
        elif limit is None:
            # No limit specified, return all (but still track total)
            pass
        
        return {
            "sprs": sprs_list,
            "count": len(sprs_list),
            "total_count": total_count,
            "offset": offset,
            "limit": limit if limit is not None else total_count,
            "file_path": str(SPR_DEFINITIONS)
        }
    except Exception as e:
        logger.error(f"SPR load error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"SPR load error: {str(e)}")

@app.get("/api/sprs/search/{term}")
async def search_sprs(term: str):
    """Search for SPRs by term."""
    if not SPR_DEFINITIONS.exists():
        raise HTTPException(status_code=404, detail="SPR definitions not found")
    
    try:
        with open(SPR_DEFINITIONS, 'r') as f:
            all_sprs = json.load(f)
        
        # Search in spr_id, term, and definition
        matches = []
        term_lower = term.lower()
        
        for spr in all_sprs:
            if (term_lower in spr.get("spr_id", "").lower() or
                term_lower in spr.get("term", "").lower() or
                term_lower in spr.get("definition", "").lower()):
                matches.append(spr)
        
        return {
            "matches": matches,
            "count": len(matches),
            "search_term": term
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# ==================== QUERY ENHANCEMENT ENDPOINT ====================

@app.post("/api/query/enhance")
async def enhance_query(request: QueryEnhancementRequest):
    """Enhance a query to maximize effectiveness using dynamic capability discovery."""
    try:
        # Import query enhancement engine
        sys.path.insert(0, str(PROJECT_ROOT))
        from Three_PointO_ArchE.query_enhancement_engine import create_enhancement_engine
        
        # Create enhancement engine
        engine = create_enhancement_engine(PROJECT_ROOT)
        
        # Enhance the query
        result = engine.enhance_query(
            request.query,
            enhancement_level=request.enhancement_level
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Query enhancement error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query enhancement error: {str(e)}")

# ==================== WEBSOCKET ENDPOINT ====================

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates and conversation."""
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to ArchE Dashboard",
            "timestamp": datetime.now().isoformat(),
            "arche_available": ARCHE_AVAILABLE
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "query":
                # Process query and stream response with terminal output
                query_text = data.get("query", "")
                enhanced_query = data.get("enhanced_query")  # Get enhanced query if provided
                provider = data.get("provider", "groq")
                model = data.get("model")
                use_rise = data.get("use_rise", True)
                
                # Use enhanced query if available, otherwise use original
                actual_query = enhanced_query if enhanced_query else query_text
                query_id = f"query_{datetime.now().timestamp()}"
                
                try:
                    sys.path.insert(0, str(PROJECT_ROOT))
                    from ask_arche_enhanced_v2 import EnhancedRealArchEProcessor, EnhancedUnifiedArchEConfig, EnhancedVCDIntegration
                    
                    # Create output queue for this query
                    output_queue = manager.create_output_queue(query_id)
                    
                    # Send processing start
                    await websocket.send_json({
                        "type": "processing_start",
                        "query": actual_query,
                        "query_id": query_id,
                        "using_enhanced": enhanced_query is not None,
                        "provider": provider,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Start terminal output streaming task
                    async def send_terminal_output(output_chunk: dict):
                        """Send terminal output chunk to WebSocket."""
                        await manager.send_to_connection(websocket, {
                            "type": "terminal_output",
                            "query_id": query_id,
                            **output_chunk
                        })
                    
                    # Start streaming terminal output
                    stream_task = asyncio.create_task(
                        stream_terminal_output(output_queue, send_terminal_output, interval=0.05)
                    )
                    
                    # Setup terminal capture
                    capturer = TerminalOutputCapturer(output_queue)
                    rich_capturer = RichConsoleCapturer(output_queue)
                    
                    # Temporarily replace console in ask_arche_enhanced_v2 and related modules
                    import ask_arche_enhanced_v2
                    original_console = getattr(ask_arche_enhanced_v2, 'console', None)
                    rich_console = rich_capturer.get_console()
                    
                    # Replace console in ask_arche_enhanced_v2
                    if original_console:
                        ask_arche_enhanced_v2.console = rich_console
                    
                    # Also replace console in Three_PointO_ArchE modules if they use it
                    try:
                        from Three_PointO_ArchE import config as arche_config
                        if hasattr(arche_config, 'console'):
                            arche_config.console = rich_console
                    except:
                        pass
                    
                    # Send initial terminal output message
                    await websocket.send_json({
                        "type": "terminal_output",
                        "query_id": query_id,
                        "stream": "console",
                        "text": f"[ArchE] Processing query with provider: {provider}, model: {model or 'default'}\n",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    processor = None
                    try:
                        # Register query with connection manager
                        manager.register_query(websocket, query_id)
                        
                        # Initialize config with dynamic parameters from WebSocket message
                        # Disable Cursor auto-detection if user explicitly selected a provider
                        enable_auto_detect = provider is None or provider == "cursor"
                        config = EnhancedUnifiedArchEConfig(
                            provider=provider,
                            model=model,
                            use_rise=use_rise,
                            enable_cursor_auto_detect=enable_auto_detect
                        )
                        
                        logger.info(f"WebSocket Config initialized: provider={config.llm_provider}, model={config.llm_config.get('model')}, use_rise={config.use_rise}")
                        
                        # Start capturing
                        capturer.start_capture()
                        
                        # Initialize processor with config (already set up with provider override above)
                        vcd = EnhancedVCDIntegration(config)
                        processor = EnhancedRealArchEProcessor(vcd, config)
                        
                        # Register processor for cleanup tracking
                        manager.register_processor(query_id, processor)
                        
                        # Extract SPRs and capabilities from enhanced query metadata if available
                        detected_sprs = data.get("detected_sprs")
                        required_capabilities = data.get("required_capabilities")
                        
                        logger.info(f"🔧 [WebSocket] Creating EnhancedVCDIntegration and EnhancedRealArchEProcessor...")
                        logger.info(f"✅ [WebSocket] Processor created successfully")
                        logger.info(f"🚀 [WebSocket] CALLING processor.process_query() with query length: {len(actual_query)}, SPRs: {len(detected_sprs) if detected_sprs else 0}, Capabilities: {len(required_capabilities) if required_capabilities else 0}")
                        
                        # Process query with pre-identified SPRs and capabilities
                        result = await processor.process_query(
                            actual_query,
                            pre_identified_sprs=detected_sprs,
                            pre_identified_capabilities=required_capabilities
                        )
                        logger.info(f"✅ [WebSocket] processor.process_query() RETURNED. Result type: {type(result)}, Is dict: {isinstance(result, dict)}")
                        
                        # Send terminal output completion
                        await websocket.send_json({
                            "type": "terminal_output",
                            "query_id": query_id,
                            "stream": "console",
                            "text": "\n[Processing Complete]\n",
                            "timestamp": datetime.now().isoformat()
                        })
                        
                    finally:
                        # CRITICAL: Always shutdown processor to close browser instances
                        if processor:
                            try:
                                await processor.shutdown()
                            except Exception as e:
                                logger.error(f"Error during processor shutdown: {e}")
                        
                        # Additional safety: Force cleanup of any orphaned browser processes
                        try:
                            sys.path.insert(0, os.path.join(str(PROJECT_ROOT), "Three_PointO_ArchE"))
                            from browser_cleanup import cleanup_browser_processes
                            cleanup_browser_processes()
                        except Exception as e:
                            logger.debug(f"Browser cleanup utility not available or failed: {e}")
                        
                        # Stop capturing and restore console
                        capturer.stop_capture()
                        if original_console:
                            ask_arche_enhanced_v2.console = original_console
                        
                        # Cancel streaming task
                        stream_task.cancel()
                        try:
                            await stream_task
                        except asyncio.CancelledError:
                            pass
                        
                        # Clean up all query resources
                        manager.cleanup_query(query_id)
                    
                    # Clean result - remove non-serializable objects
                    clean_result = clean_result_for_json(result)
                    
                    # Send result
                    await websocket.send_json({
                        "type": "query_response",
                        "query": query_text,
                        "query_id": query_id,
                        "result": clean_result,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    # Cancel streaming if still running
                    if 'stream_task' in locals():
                        stream_task.cancel()
                    
                    # Clean up all query resources
                    manager.cleanup_query(query_id)
                    
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                        "query_id": query_id,
                        "timestamp": datetime.now().isoformat()
                    })
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "get_status":
                # Send current system status
                await websocket.send_json({
                    "type": "status",
                    "arche_available": ARCHE_AVAILABLE,
                    "thought_trail_available": THOUGHT_TRAIL_DB.exists(),
                    "sprs_available": SPR_DEFINITIONS.exists(),
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# ==================== SYSTEM STATUS ENDPOINTS ====================

@app.get("/api/status")
async def get_system_status():
    """Get overall system status."""
    return {
        "status": "operational",
        "arche_available": ARCHE_AVAILABLE,
        "thought_trail_db": str(THOUGHT_TRAIL_DB),
        "thought_trail_exists": THOUGHT_TRAIL_DB.exists(),
        "spr_definitions": str(SPR_DEFINITIONS),
        "sprs_exists": SPR_DEFINITIONS.exists(),
        "version": "3.5-GP",
        "connections": manager.get_connection_count(),
        "active_queries": manager.get_active_queries_count(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/providers")
async def get_available_providers():
    """Get list of available LLM providers and their models."""
    try:
        providers_info = {
            "groq": {
                "name": "Groq",
                "status": "available",
                "default_model": "llama-3.3-70b-versatile",
                "models": [
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant",
                    "meta-llama/llama-4-maverick-17b-128e-instruct",
                    "meta-llama/llama-4-scout-17b-16e-instruct",
                    "groq/compound",
                    "groq/compound-mini",
                    "qwen/qwen3-32b",
                    "moonshotai/kimi-k2-instruct",
                    "openai/gpt-oss-120b",
                    "openai/gpt-oss-20b",
                    "allam-2-7b"
                ],
                "speed": "ultra_fast",
                "cost": "free_tier_available"
            },
            "google": {
                "name": "Google Gemini",
                "status": "available",
                "default_model": "gemini-2.0-flash-exp",
                "models": ["gemini-2.0-flash-exp", "gemini-1.5-pro"],
                "speed": "fast",
                "cost": "free_tier_available"
            },
            "cursor": {
                "name": "Cursor ArchE (Me)",
                "status": "available",
                "default_model": "cursor-arche-v1",
                "models": ["cursor-arche-v1"],
                "speed": "variable",
                "cost": "included"
            }
        }
        
        return {
            "providers": providers_info,
            "default_provider": "groq",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ArchE Dashboard API",
        "version": "3.5-GP",
        "timestamp": datetime.now().isoformat()
    }

# ==================== STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("=" * 80)
    print("ArchE Dashboard Backend API Starting...")
    print("=" * 80)
    print(f"Thought Trail DB: {THOUGHT_TRAIL_DB}")
    print(f"  Exists: {THOUGHT_TRAIL_DB.exists()}")
    print(f"SPR Definitions: {SPR_DEFINITIONS}")
    print(f"  Exists: {SPR_DEFINITIONS.exists()}")
    print(f"ArchE Components: {'✅ Available' if ARCHE_AVAILABLE else '❌ Not Available'}")
    print("=" * 80)

# ==================== PORT MANAGEMENT ====================

def get_dashboard_port() -> int:
    """Get available port for dashboard, handling conflicts automatically."""
    try:
        from .port_manager import get_port_manager
        port_manager = get_port_manager()
        
        # Check environment variable first
        env_port = os.environ.get("DASHBOARD_PORT")
        if env_port:
            try:
                port = int(env_port)
                if port_manager.is_port_available(port):
                    port_manager.used_ports.add(port)
                    port_manager._save_config()
                    return port
                else:
                    logger.warning(f"Port {port} from DASHBOARD_PORT is not available, finding alternative...")
            except ValueError:
                logger.warning(f"Invalid DASHBOARD_PORT value: {env_port}")
        
        # Find available port
        return port_manager.find_available_port()
    except Exception as e:
        logger.warning(f"Port manager not available, using default port 8000: {e}")
        return 8000

# ==================== MAIN ====================

if __name__ == "__main__":
    import atexit
    import signal
    
    # Get available port
    port = get_dashboard_port()
    
    # Register cleanup on exit
    def cleanup_on_exit():
        try:
            from .port_manager import get_port_manager
            port_manager = get_port_manager()
            port_manager.release_port(port)
            logger.info(f"Released port {port} on exit")
        except Exception as e:
            logger.debug(f"Error releasing port: {e}")
    
    atexit.register(cleanup_on_exit)
    
    # Handle signals
    def signal_handler(signum, frame):
        cleanup_on_exit()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("\n🚀 Starting ArchE Dashboard Backend API")
    print("📍 Access at: http://localhost:{}".format(port))
    print("📚 API Docs at: http://localhost:{}/docs".format(port))
    print("🔌 WebSocket at: ws://localhost:{}/ws/live".format(port))
    print("\n💡 Port automatically selected to avoid conflicts")
    print("   Set DASHBOARD_PORT environment variable to use a specific port")
    print("\n" + "=" * 80 + "\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload to prevent port conflicts
        log_level="info"
    )

