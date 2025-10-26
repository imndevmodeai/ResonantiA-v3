#!/usr/bin/env python3
"""
Direct RISE Analysis Runner with VCD Integration
Runs a complete RISE analysis on the provided query with rich VCD events.
"""

import sys
import os
import asyncio
import websockets
import json
import threading
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator

class VCDEventCallback:
    """Event callback that connects to the VCD bridge via WebSocket"""
    
    def __init__(self):
        self.websocket = None
        self.connected = False
        self.event_loop = None
        
    async def connect_to_vcd_bridge(self):
        """Connect to the VCD bridge WebSocket"""
        try:
            self.websocket = await websockets.connect("ws://localhost:8765")
            self.connected = True
            print("✅ Connected to VCD Bridge")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to VCD Bridge: {e}")
            return False
    
    async def send_event(self, event_data):
        """Send event to VCD bridge"""
        if self.connected and self.websocket:
            try:
                await self.websocket.send(json.dumps(event_data))
            except Exception as e:
                print(f"❌ Failed to send event to VCD: {e}")
                self.connected = False
    
    def __call__(self, event_data):
        """Synchronous callback that queues events for async sending"""
        if self.event_loop and self.connected:
            # Schedule the async send in the event loop
            asyncio.run_coroutine_threadsafe(
                self.send_event(event_data), 
                self.event_loop
            )
    
    async def disconnect(self):
        """Disconnect from VCD bridge"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False

async def run_analysis_with_vcd(query):
    """Run RISE analysis with VCD integration"""
    # Create VCD event callback
    vcd_callback = VCDEventCallback()
    
    # Connect to VCD bridge
    await vcd_callback.connect_to_vcd_bridge()
    
    # Set up event loop for the callback
    vcd_callback.event_loop = asyncio.get_event_loop()
    
    try:
        # Initialize the RISE orchestrator with VCD callback
        orchestrator = RISE_Orchestrator(event_callback=vcd_callback)
        
        # Run the complete RISE workflow
        result = orchestrator.run_rise_workflow(
            problem_description=query,
            code_executor_timeout=900
        )
        
        return result
        
    finally:
        # Disconnect from VCD bridge
        await vcd_callback.disconnect()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_rise_analysis.py '<your analysis query>'")
        sys.exit(1)
    
    query = sys.argv[1]
    
    print(f"🚀 Starting RISE Analysis with VCD Integration...")
    print(f"📝 Query: {query[:100]}...")
    
    try:
        # Run the analysis with VCD integration
        result = asyncio.run(run_analysis_with_vcd(query))
        
        print("\n✅ RISE Analysis Complete!")
        print("=" * 80)
        
        # Display the results
        if result.get("success"):
            print("🎯 Analysis Status: SUCCESS")
            
            # Show Phase A results
            if "phase_a_result" in result:
                print("\n📚 Phase A - Knowledge Scaffolding:")
                phase_a = result["phase_a_result"]
                print(f"   Knowledge Base: {phase_a.get('session_knowledge_base', 'N/A')[:200]}...")
                print(f"   Specialized Agent: {phase_a.get('specialized_agent', 'N/A')[:200]}...")
            
            # Show Phase B results
            if "phase_b_result" in result:
                print("\n🧠 Phase B - Strategy Fusion:")
                phase_b = result["phase_b_result"]
                print(f"   Strategic Dossier: {phase_b.get('fused_strategic_dossier', 'N/A')[:200]}...")
            
            # Show Phase C results
            if "phase_c_result" in result:
                print("\n⚖️ Phase C - High Stakes Vetting:")
                phase_c = result["phase_c_result"]
                print(f"   Vetted Strategy: {phase_c.get('final_strategy', 'N/A')[:200]}...")
            
            # Show Phase D results
            if "phase_d_result" in result:
                print("\n🔬 Phase D - SPR Distillation:")
                phase_d = result["phase_d_result"]
                print(f"   SPR Definition: {phase_d.get('spr_definition', 'N/A')[:200]}...")
            
            # Show final result
            if "final_result" in result:
                print("\n🎉 Final Result:")
                print(result["final_result"])
                
        else:
            print("❌ Analysis Status: FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ RISE Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import time
    main()
