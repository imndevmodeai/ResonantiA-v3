#!/usr/bin/env python3
"""
ArchE Interface - Persistent Server Client
This script provides a command-line interface to the persistent ArchE server,
replacing the old stateless mastermind/interact.py approach.

Usage:
    python arche_interface.py "Your query here"
    python arche_interface.py --server-mode  # Read from stdin
    python arche_interface.py --status       # Get server status
"""

import sys
import json
import asyncio
import websockets
import argparse
import os
from typing import Optional

async def send_query_to_server(query: str, server_url: str = None) -> dict:
    """Send a query to the ArchE persistent server and return the response."""
    # Use environment variable for port if available, otherwise use default
    if server_url is None:
        port = os.environ.get('ARCHE_PORT', '3005')
        server_url = f"ws://localhost:{port}"
    
    try:
        async with websockets.connect(server_url) as websocket:
            print(f"🔗 Connected to ArchE persistent server at {server_url}")
            
            # Send the query
            await websocket.send(query)
            print(f"📤 Query sent: {query[:50]}...")
            
            # Wait for response
            response = await websocket.recv()
            print(f"📥 Response received")
            
            # Parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If response is not JSON, wrap it
                return {
                    "type": "response",
                    "content": response,
                    "raw_response": True
                }
                
    except (websockets.exceptions.ConnectionClosed, websockets.exceptions.InvalidURI, OSError) as e:
        error_msg = f"❌ ERROR: Cannot connect to ArchE persistent server at {server_url}"
        suggestion = f"💡 Suggestion: Make sure the server is running: python arche_persistent_server.py"
        print(error_msg)
        print(f"   Details: {str(e)}")
        print(suggestion)
        return {
            "type": "error",
            "content": error_msg,
            "suggestion": suggestion,
            "server_url": server_url
        }
    except Exception as e:
        error_msg = f"❌ ERROR: {str(e)}"
        print(error_msg)
        return {
            "type": "error",
            "content": error_msg,
            "server_url": server_url
        }

async def get_server_status(server_url: str = None) -> dict:
    """Get the status of the ArchE persistent server."""
    # Use environment variable for port if available, otherwise use default
    if server_url is None:
        port = os.environ.get('ARCHE_PORT', '3005')
        server_url = f"ws://localhost:{port}"
    
    try:
        async with websockets.connect(server_url) as websocket:
            # Send a simple status query
            await websocket.send("status")
            response = await websocket.recv()
            return json.loads(response)
    except Exception as e:
        return {
            "type": "error",
            "content": f"Failed to get server status: {str(e)}",
            "server_url": server_url
        }

def format_response(response: dict) -> str:
    """Format the server response for display."""
    if response.get("error"):
        output = f"❌ ERROR: {response['error']}\n"
        if response.get("suggestion"):
            output += f"💡 Suggestion: {response['suggestion']}\n"
        return output
    
    if response.get("query_processed"):
        output = f"✅ Query processed successfully\n"
        output += f"🔗 Processing pathway: {response.get('processing_pathway', 'Unknown')}\n"
        output += f"⏱️  Processing time: {response.get('processing_time', 0):.3f}s\n"
        
        # Show temporal continuity info
        if response.get("temporal_continuity"):
            tc = response["temporal_continuity"]
            output += f"🧠 Cognitive continuity: {'Active' if tc.get('cognitive_continuity_active') else 'Inactive'}\n"
            output += f"📊 Total queries processed: {tc.get('total_queries_processed', 0)}\n"
            output += f"💾 Session memory entries: {tc.get('session_memory_entries', 0)}\n"
        
        # Show answer
        if response.get("answer"):
            output += f"\n📝 Answer:\n{response['answer']}\n"
        elif response.get("truth_packet"):
            tp = response["truth_packet"]
            output += f"\n🔍 Truth Verification Results:\n"
            output += f"   Final Answer: {tp['final_answer']}\n"
            output += f"   Confidence: {tp['confidence_score']:.2f}\n"
            output += f"   Source Consensus: {tp['source_consensus']}\n"
        elif response.get("rise_result"):
            rr = response["rise_result"]
            output += f"\n🚀 RISE Strategic Analysis:\n"
            output += f"   Status: {rr.get('execution_status', 'Unknown')}\n"
            output += f"   Session ID: {rr.get('session_id', 'Unknown')}\n"
        
        return output
    
    if response.get("server_status"):
        output = f"🖥️  Server Status: {response['server_status']}\n"
        output += f"⏱️  Uptime: {response.get('uptime_seconds', 0):.1f}s\n"
        output += f"📊 Total queries: {response.get('total_queries_processed', 0)}\n"
        output += f"🧠 Cognitive continuity: {'Active' if response.get('cognitive_continuity_active') else 'Inactive'}\n"
        
        components = response.get("components_status", {})
        output += f"🔧 Components status:\n"
        for component, status in components.items():
            status_icon = "✅" if status else "❌"
            output += f"   {status_icon} {component}: {'Active' if status else 'Inactive'}\n"
        
        return output
    
    # Fallback: return JSON
    return json.dumps(response, indent=2, default=str)

async def main():
    """Main interface function."""
    parser = argparse.ArgumentParser(
        description="ArchE Interface - Connect to persistent ArchE server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python arche_interface.py "What is artificial intelligence?"
  python arche_interface.py --server-mode  # Read from stdin
  python arche_interface.py --status       # Get server status
  echo "Hello ArchE" | python arche_interface.py --server-mode
        """
    )
    
    parser.add_argument(
        'query', 
        nargs='?', 
        help='Query to send to ArchE (if not provided, will read from stdin in server mode)'
    )
    parser.add_argument(
        '--server-mode', 
        action='store_true',
        help='Read query from stdin (for use with WebSocket server)'
    )
    parser.add_argument(
        '--status', 
        action='store_true',
        help='Get server status instead of processing a query'
    )
    parser.add_argument(
        '--server-url', 
        default=None,
        help='WebSocket server URL (default: uses ARCHE_PORT environment variable or ws://localhost:3005)'
    )
    parser.add_argument(
        '--json', 
        action='store_true',
        help='Output raw JSON response'
    )
    
    args = parser.parse_args()
    
    # Handle status request
    if args.status:
        response = await get_server_status(args.server_url)
        if args.json:
            print(json.dumps(response, indent=2, default=str))
        else:
            print(format_response(response))
        return
    
    # Get query from argument or stdin
    query = None
    if args.query:
        query = args.query
    elif args.server_mode or not sys.stdin.isatty():
        # Read from stdin
        try:
            query = sys.stdin.read().strip()
        except KeyboardInterrupt:
            print("\n❌ Query input interrupted")
            return
        except Exception as e:
            print(f"❌ Error reading from stdin: {e}")
            return
    
    if not query:
        print("❌ No query provided")
        print("Use: python arche_interface.py \"Your query here\"")
        print("Or:  echo \"Your query\" | python arche_interface.py --server-mode")
        return
    
    # Send query to server
    print(f"🔄 Sending query to persistent ArchE server...")
    response = await send_query_to_server(query, args.server_url)
    
    # Format and display response
    if args.json:
        print(json.dumps(response, indent=2, default=str))
    else:
        print(format_response(response))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 