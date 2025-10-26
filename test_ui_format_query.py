#!/usr/bin/env python3
"""
Test query in UI format
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ui_format_query():
    """Test query in the format that the UI sends"""
    uri = "ws://localhost:3005"
    
    try:
        logger.info(f"🔗 Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connected successfully!")
            
            # Send a query in the exact format the UI sends
            query = {
                "type": "query",
                "content": "Design a comprehensive strategy for navigating an unknown competitive landscape where information is limited, risks are high, and the stakes involve significant resource allocation. The strategy must account for multiple unknown variables, potential adversarial actions, and the need for rapid adaptation to emerging intelligence.",
                "metadata": {
                    "timestamp": int(asyncio.get_event_loop().time() * 1000),
                    "session_id": "ui_session",
                    "source": "ui"
                }
            }
            
            logger.info(f"📤 Sending UI format query: {query['content'][:50]}...")
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
    asyncio.run(test_ui_format_query()) 