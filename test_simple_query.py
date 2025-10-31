#!/usr/bin/env python3
"""
Test simple query to WebSocket server
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_query():
    """Test simple query to WebSocket server"""
    uri = "ws://localhost:3004"
    
    try:
        logger.info(f"🔗 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connected successfully!")
            
            # Send a simple query
            query = {
                "type": "query",
                "content": "What is 2+2?",
                "metadata": {
                    "timestamp": str(asyncio.get_event_loop().time()),
                    "session_id": "test_session",
                    "query_type": "simple"
                }
            }
            
            logger.info(f"📤 Sending query: {query['content']}")
            await websocket.send(json.dumps(query))
            
            # Wait for multiple responses
            logger.info("📥 Waiting for responses...")
            response_count = 0
            try:
                while response_count < 5:  # Expect up to 5 responses
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    response_count += 1
                    logger.info(f"📨 Response {response_count}: {response}")
                    
                    # Parse response to check if it's the final one
                    try:
                        data = json.loads(response)
                        if data.get("type") == "response" and data.get("metadata", {}).get("status") == "completed":
                            logger.info("✅ Received final response, stopping...")
                            break
                    except json.JSONDecodeError:
                        pass
                        
            except asyncio.TimeoutError:
                logger.info(f"⏰ Timeout after receiving {response_count} responses")
                
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_query()) 