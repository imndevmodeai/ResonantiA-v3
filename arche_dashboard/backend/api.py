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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

# Import terminal capturer
from .terminal_capturer import TerminalOutputCapturer, RichConsoleCapturer, stream_terminal_output

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

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.query_output_queues: Dict[str, Queue] = {}  # Maps query_id to output queue

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
    
    async def send_to_connection(self, websocket: WebSocket, message: dict):
        """Send message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending to connection: {e}")
    
    def create_output_queue(self, query_id: str) -> Queue:
        """Create an output queue for a query."""
        queue = Queue()
        self.query_output_queues[query_id] = queue
        return queue
    
    def remove_output_queue(self, query_id: str):
        """Remove an output queue for a query."""
        if query_id in self.query_output_queues:
            del self.query_output_queues[query_id]

manager = ConnectionManager()

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    provider: Optional[str] = "groq"
    model: Optional[str] = None
    max_tokens: Optional[int] = 8192
    temperature: Optional[float] = 0.7
    use_rise: Optional[bool] = True

class ThoughtTrailQuery(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: Optional[int] = 100
    query_text: Optional[str] = None
    min_confidence: Optional[float] = None

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
            timestamp,
            query,
            response_preview,
            confidence,
            processing_method,
            iar_summary,
            spr_context
        FROM thought_trail
        ORDER BY timestamp DESC
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        entries = []
        for row in rows:
            entries.append({
                "timestamp": row[0],
                "query": row[1],
                "response_preview": row[2],
                "confidence": row[3],
                "processing_method": row[4],
                "iar_summary": json.loads(row[5]) if row[5] else {},
                "spr_context": json.loads(row[6]) if row[6] else {}
            })
        
        conn.close()
        return {"entries": entries, "count": len(entries)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/thought-trail/search")
async def search_thought_trail(query: ThoughtTrailQuery):
    """Search thought trail with filters."""
    if not THOUGHT_TRAIL_DB.exists():
        raise HTTPException(status_code=404, detail="Thought trail database not found")
    
    try:
        conn = sqlite3.connect(str(THOUGHT_TRAIL_DB))
        cursor = conn.cursor()
        
        sql = "SELECT * FROM thought_trail WHERE 1=1"
        params = []
        
        if query.start_date:
            sql += " AND timestamp >= ?"
            params.append(query.start_date)
        
        if query.end_date:
            sql += " AND timestamp <= ?"
            params.append(query.end_date)
        
        if query.query_text:
            sql += " AND (query LIKE ? OR response_preview LIKE ?)"
            search_term = f"%{query.query_text}%"
            params.extend([search_term, search_term])
        
        if query.min_confidence is not None:
            sql += " AND confidence >= ?"
            params.append(query.min_confidence)
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(query.limit or 100)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        entries = []
        for row in rows:
            entry = dict(zip(columns, row))
            # Parse JSON fields
            if entry.get('iar_summary'):
                entry['iar_summary'] = json.loads(entry['iar_summary'])
            if entry.get('spr_context'):
                entry['spr_context'] = json.loads(entry['spr_context'])
            entries.append(entry)
        
        conn.close()
        return {"entries": entries, "count": len(entries), "query": query.dict()}
        
    except Exception as e:
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
        
        # Entries by provider
        cursor.execute("SELECT llm_provider, COUNT(*) FROM thought_trail GROUP BY llm_provider")
        by_provider = dict(cursor.fetchall())
        
        # Recent activity (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM thought_trail WHERE timestamp >= ?", (yesterday,))
        recent_24h = cursor.fetchone()[0]
        
        # SPR usage stats
        cursor.execute("SELECT COUNT(*) FROM thought_trail WHERE spr_context IS NOT NULL AND spr_context != '{}'")
        queries_with_sprs = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_entries": total_entries,
            "average_confidence": round(avg_confidence, 3),
            "providers_used": by_provider,
            "recent_24h": recent_24h,
            "queries_with_spr_priming": queries_with_sprs,
            "database_path": str(THOUGHT_TRAIL_DB)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

# ==================== QUERY PROCESSING ENDPOINTS ====================

@app.post("/api/query/submit")
async def submit_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """Submit a query to ArchE for processing."""
    
    try:
        # Import ask_arche functionality
        sys.path.insert(0, str(PROJECT_ROOT))
        from ask_arche_enhanced_v2 import EnhancedRealArchEProcessor, EnhancedUnifiedArchEConfig
        
        # Initialize config and processor
        config = EnhancedUnifiedArchEConfig()
        processor = EnhancedRealArchEProcessor(config)
        
        # Process query
        result = await processor.process_query(request.query)
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "query_complete",
            "timestamp": datetime.now().isoformat(),
            "query": request.query,
            "confidence": result.get("response", {}).get("reflection", {}).get("confidence", 0.0)
        })
        
        return {
            "status": "success",
            "query": request.query,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")

@app.post("/api/query/stream")
async def stream_query(request: QueryRequest):
    """Stream query responses in real-time using Server-Sent Events."""
    
    async def event_generator():
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from ask_arche_enhanced_v2 import EnhancedRealArchEProcessor, EnhancedUnifiedArchEConfig
            
            config = EnhancedUnifiedArchEConfig()
            processor = EnhancedRealArchEProcessor(config)
            
            # Send initial event
            yield f"data: {json.dumps({'type': 'start', 'query': request.query})}\n\n"
            
            # Process query
            result = await processor.process_query(request.query)
            
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
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ==================== SPR MANAGEMENT ENDPOINTS ====================

@app.get("/api/sprs/list")
async def list_sprs():
    """List all available SPRs."""
    if not SPR_DEFINITIONS.exists():
        raise HTTPException(status_code=404, detail="SPR definitions not found")
    
    try:
        with open(SPR_DEFINITIONS, 'r') as f:
            sprs = json.load(f)
        
        return {
            "sprs": sprs,
            "count": len(sprs),
            "file_path": str(SPR_DEFINITIONS)
        }
    except Exception as e:
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
                query_id = f"query_{datetime.now().timestamp()}"
                
                try:
                    sys.path.insert(0, str(PROJECT_ROOT))
                    from ask_arche_enhanced_v2 import EnhancedRealArchEProcessor, EnhancedUnifiedArchEConfig
                    
                    # Create output queue for this query
                    output_queue = manager.create_output_queue(query_id)
                    
                    # Send processing start
                    await websocket.send_json({
                        "type": "processing_start",
                        "query": query_text,
                        "query_id": query_id,
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
                    
                    # Temporarily replace console in ask_arche_enhanced_v2
                    import ask_arche_enhanced_v2
                    original_console = getattr(ask_arche_enhanced_v2, 'console', None)
                    if original_console:
                        ask_arche_enhanced_v2.console = rich_capturer.get_console()
                    
                    try:
                        # Start capturing
                        capturer.start_capture()
                        
                        # Initialize config and processor
                        config = EnhancedUnifiedArchEConfig()
                        processor = EnhancedRealArchEProcessor(config)
                        
                        # Process query
                        result = await processor.process_query(query_text)
                        
                        # Send terminal output completion
                        await websocket.send_json({
                            "type": "terminal_output",
                            "query_id": query_id,
                            "stream": "console",
                            "text": "\n[Processing Complete]\n",
                            "timestamp": datetime.now().isoformat()
                        })
                        
                    finally:
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
                        
                        # Clean up queue
                        manager.remove_output_queue(query_id)
                    
                    # Send result
                    await websocket.send_json({
                        "type": "query_response",
                        "query": query_text,
                        "query_id": query_id,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    # Cancel streaming if still running
                    if 'stream_task' in locals():
                        stream_task.cancel()
                    manager.remove_output_queue(query_id)
                    
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

# ==================== MAIN ====================

if __name__ == "__main__":
    print("\n🚀 Starting ArchE Dashboard Backend API")
    print("📍 Access at: http://localhost:8000")
    print("📚 API Docs at: http://localhost:8000/docs")
    print("🔌 WebSocket at: ws://localhost:8000/ws/live")
    print("\n" + "=" * 80 + "\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

