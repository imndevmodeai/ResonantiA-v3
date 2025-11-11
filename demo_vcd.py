#!/usr/bin/env python3
"""
Demo: Visual Cognitive Debugger (VCD)
Demonstrates the VCD's real-time cognitive monitoring and visualization capabilities.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("⚠️  websockets not available. Install with: pip install websockets")
    sys.exit(1)

try:
    from Three_PointO_ArchE.visual_cognitive_debugger_ui import (
        VisualCognitiveDebugger,
        CognitiveVisualizationMode
    )
    VCD_AVAILABLE = True
except ImportError as e:
    VCD_AVAILABLE = False
    print(f"⚠️  VCD not available: {e}")
    print("   This demo requires the VisualCognitiveDebugger to be available.")
    sys.exit(1)

# ============================================================================
# Demo 1: Start VCD Server
# ============================================================================

async def demo_start_vcd_server():
    """Demonstrates starting the VCD server"""
    print("=" * 80)
    print("DEMO 1: Starting VCD Server")
    print("=" * 80)
    
    vcd = VisualCognitiveDebugger(host="localhost", port=8765)
    
    print(f"\n📡 VCD Server Configuration:")
    print(f"   Host: {vcd.host}")
    print(f"   Port: {vcd.port}")
    print(f"   WebSocket URL: ws://{vcd.host}:{vcd.port}")
    
    print(f"\n🎨 Available Visualization Modes:")
    for mode in CognitiveVisualizationMode:
        print(f"   - {mode.value}")
    
    print(f"\n⚙️  Starting VCD server...")
    print(f"   (This will run in the background. Press Ctrl+C to stop.)")
    print(f"\n   To connect, use a WebSocket client or run demo_connect_to_vcd()")
    
    # Start server in background
    try:
        await vcd.start_server()
    except KeyboardInterrupt:
        print("\n\n🛑 VCD Server stopped by user")
        vcd.stop_monitoring()

# ============================================================================
# Demo 2: Connect to VCD as Client
# ============================================================================

async def demo_connect_to_vcd():
    """Demonstrates connecting to VCD as a WebSocket client"""
    print("\n" + "=" * 80)
    print("DEMO 2: Connecting to VCD as Client")
    print("=" * 80)
    
    uri = "ws://localhost:8765"
    
    print(f"\n🔌 Connecting to VCD at {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to VCD!")
            
            # Receive welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            
            print(f"\n📨 Welcome Message:")
            print(f"   Type: {welcome_data.get('type')}")
            print(f"   Message: {welcome_data.get('message')}")
            print(f"   Available Modes: {', '.join(welcome_data.get('available_modes', []))}")
            
            monitoring_status = welcome_data.get('monitoring_status', {})
            print(f"   Monitoring Active: {monitoring_status.get('active', False)}")
            print(f"   Data Stream Size: {monitoring_status.get('data_stream_size', 0)}")
            
            # Request cognitive state
            print(f"\n📊 Requesting cognitive state...")
            request = {
                "type": "get_cognitive_state",
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(request))
            
            # Wait for response (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                print(f"   Response Type: {response_data.get('type')}")
                if 'cognitive_state' in response_data:
                    state = response_data['cognitive_state']
                    print(f"   Active SPRs: {len(state.get('active_sprs', []))}")
                    print(f"   Recent Thoughts: {len(state.get('recent_thoughts', []))}")
            except asyncio.TimeoutError:
                print("   ⏱️  No response received (server may not be running)")
            
            # Request visualization
            print(f"\n🎨 Requesting visualization data...")
            viz_request = {
                "type": "get_visualization",
                "mode": "thought_network",
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(viz_request))
            
            # Wait for response
            try:
                viz_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                viz_data = json.loads(viz_response)
                print(f"   Visualization Type: {viz_data.get('type')}")
                print(f"   Mode: {viz_data.get('mode', 'unknown')}")
            except asyncio.TimeoutError:
                print("   ⏱️  No visualization response (server may not be running)")
            
            print(f"\n✅ Demo completed. Connection will close.")
            
    except websockets.exceptions.ConnectionRefused:
        print(f"❌ Connection refused. Is the VCD server running?")
        print(f"   Start it with: python demo_vcd.py --server")
    except Exception as e:
        print(f"❌ Error connecting to VCD: {e}")

# ============================================================================
# Demo 3: Show VCD Code Structure
# ============================================================================

def demo_vcd_structure():
    """Shows the VCD code structure and integration points"""
    print("\n" + "=" * 80)
    print("DEMO 3: VCD Code Structure")
    print("=" * 80)
    
    print(f"\n📚 Main Classes:")
    print(f"   1. VisualCognitiveDebugger")
    print(f"      - Main VCD server class")
    print(f"      - Handles WebSocket connections")
    print(f"      - Manages cognitive monitoring")
    print(f"      - Location: Three_PointO_ArchE/visual_cognitive_debugger_ui.py")
    
    print(f"\n   2. AdvancedCognitiveVisualizer")
    print(f"      - Generates cognitive visualizations")
    print(f"      - Supports multiple visualization modes")
    print(f"      - Creates thought networks, SPR graphs, etc.")
    print(f"      - Location: Three_PointO_ArchE/visual_cognitive_debugger_ui.py")
    
    print(f"\n🔗 Integration Points:")
    print(f"   1. ThoughtTrail")
    print(f"      - VCD reads from ThoughtTrail for cognitive history")
    print(f"      - Provides IAR entries for visualization")
    
    print(f"\n   2. SPR Manager")
    print(f"      - VCD queries SPR Manager for active patterns")
    print(f"      - Visualizes SPR relationships")
    
    print(f"\n   3. System Health Monitor")
    print(f"      - VCD integrates with health monitoring")
    print(f"      - Displays system status and metrics")
    
    print(f"\n🎨 Visualization Modes:")
    modes = [
        ("thought_network", "Network graph of cognitive thoughts and connections"),
        ("spr_activation", "Visualization of SPR activation patterns"),
        ("temporal_flow", "Time-based flow of cognitive processes"),
        ("workflow_execution", "Real-time workflow execution visualization"),
        ("iar_reflection", "IAR reflection data visualization"),
        ("system_health", "System health and performance metrics"),
    ]
    for mode, desc in modes:
        print(f"   - {mode}: {desc}")
    
    print(f"\n📡 WebSocket Protocol:")
    print(f"   - Server listens on ws://localhost:8765 (default)")
    print(f"   - Clients connect and send JSON messages")
    print(f"   - Server responds with cognitive data and visualizations")
    print(f"   - Real-time updates pushed to connected clients")

# ============================================================================
# Main Execution
# ============================================================================

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VCD Demo Script")
    parser.add_argument("--server", action="store_true", help="Start VCD server")
    parser.add_argument("--client", action="store_true", help="Connect as client")
    parser.add_argument("--structure", action="store_true", help="Show VCD structure")
    args = parser.parse_args()
    
    if args.server:
        await demo_start_vcd_server()
    elif args.client:
        await demo_connect_to_vcd()
    elif args.structure:
        demo_vcd_structure()
    else:
        # Run all demos
        print("\n" + "=" * 80)
        print("Visual Cognitive Debugger (VCD) Demo")
        print("=" * 80)
        
        # Show structure first
        demo_vcd_structure()
        
        # Then try to connect (if server is running)
        print(f"\n" + "=" * 80)
        print("Attempting to connect to VCD server...")
        print("=" * 80)
        print(f"\n💡 Tip: Start the VCD server in another terminal with:")
        print(f"   python demo_vcd.py --server")
        print(f"\n   Then run this script again to connect as a client.")
        
        try:
            await demo_connect_to_vcd()
        except Exception as e:
            print(f"\n⚠️  Could not connect to server: {e}")
            print(f"   This is expected if the server is not running.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")

