#!/usr/bin/env python3
"""
WebSocket Timeout Wrapper - VCD Bridge Compatibility Fix
Provides timeout-compatible WebSocket connection handling for VCD Bridge
"""

import asyncio
import websockets
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketTimeoutWrapper:
    """
    WebSocket timeout wrapper for VCD Bridge compatibility
    Handles timeout parameter compatibility issues with different websockets library versions
    """
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.logger = logging.getLogger(f"{__name__}.WebSocketTimeoutWrapper")
    
    async def connect_with_timeout(self, uri: str, **kwargs) -> websockets.WebSocketServerProtocol:
        """
        Connect to WebSocket with timeout handling
        
        Args:
            uri: WebSocket URI
            **kwargs: Additional connection parameters
            
        Returns:
            WebSocket connection
            
        Raises:
            ConnectionRefusedError: If connection is refused
            asyncio.TimeoutError: If connection times out
            Exception: For other connection errors
        """
        try:
            # Remove timeout from kwargs if present (for compatibility)
            kwargs.pop('timeout', None)
            
            # Use asyncio.wait_for for timeout handling
            connection = await asyncio.wait_for(
                websockets.connect(uri, **kwargs),
                timeout=self.timeout
            )
            
            self.logger.info(f"Successfully connected to {uri}")
            return connection
            
        except asyncio.TimeoutError:
            self.logger.error(f"Connection to {uri} timed out after {self.timeout}s")
            raise
        except ConnectionRefusedError:
            self.logger.error(f"Connection to {uri} refused")
            raise
        except Exception as e:
            self.logger.error(f"Connection to {uri} failed: {e}")
            raise
    
    async def send_with_timeout(self, websocket: websockets.WebSocketServerProtocol, 
                              message: str, timeout: Optional[float] = None) -> None:
        """
        Send message with timeout handling
        
        Args:
            websocket: WebSocket connection
            message: Message to send
            timeout: Optional timeout override
        """
        timeout = timeout or self.timeout
        
        try:
            await asyncio.wait_for(
                websocket.send(message),
                timeout=timeout
            )
            self.logger.debug(f"Message sent successfully")
        except asyncio.TimeoutError:
            self.logger.error(f"Send operation timed out after {timeout}s")
            raise
        except Exception as e:
            self.logger.error(f"Send operation failed: {e}")
            raise
    
    async def recv_with_timeout(self, websocket: websockets.WebSocketServerProtocol,
                              timeout: Optional[float] = None) -> str:
        """
        Receive message with timeout handling
        
        Args:
            websocket: WebSocket connection
            timeout: Optional timeout override
            
        Returns:
            Received message
        """
        timeout = timeout or self.timeout
        
        try:
            message = await asyncio.wait_for(
                websocket.recv(),
                timeout=timeout
            )
            self.logger.debug(f"Message received successfully")
            return message
        except asyncio.TimeoutError:
            self.logger.error(f"Receive operation timed out after {timeout}s")
            raise
        except Exception as e:
            self.logger.error(f"Receive operation failed: {e}")
            raise

async def test_vcd_bridge_connection(uri: str = "ws://localhost:8765", 
                                   timeout: float = 5.0) -> Dict[str, Any]:
    """
    Test VCD Bridge connection with timeout wrapper
    
    Args:
        uri: WebSocket URI
        timeout: Connection timeout
        
    Returns:
        Connection test results
    """
    wrapper = WebSocketTimeoutWrapper(timeout)
    
    try:
        async with wrapper.connect_with_timeout(uri) as websocket:
            # Send test message
            test_message = {
                "type": "test_connection",
                "timestamp": datetime.now().isoformat(),
                "client": "websocket_timeout_wrapper"
            }
            
            import json
            await wrapper.send_with_timeout(websocket, json.dumps(test_message))
            
            # Wait for response
            response = await wrapper.recv_with_timeout(websocket)
            data = json.loads(response)
            
            return {
                "status": "connected",
                "response_received": True,
                "response_data": data,
                "timestamp": datetime.now().isoformat()
            }
            
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "response_received": False,
            "error": f"Connection timed out after {timeout}s",
            "timestamp": datetime.now().isoformat()
        }
    except ConnectionRefusedError:
        return {
            "status": "connection_refused",
            "response_received": False,
            "error": "Connection refused - VCD Bridge server not running",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "response_received": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Convenience function for VCD Analysis Agent
async def test_vcd_bridge_connection_simple() -> Dict[str, Any]:
    """Simple VCD Bridge connection test for VCD Analysis Agent"""
    return await test_vcd_bridge_connection()

if __name__ == "__main__":
    # Test the wrapper
    import asyncio
    
    async def main():
        print("Testing WebSocket Timeout Wrapper...")
        result = await test_vcd_bridge_connection()
        print(f"Test result: {result}")
    
    asyncio.run(main())



