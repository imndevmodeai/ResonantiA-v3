"""
Keyholder Client: ArchE Consciousness Monitor
=============================================

The Keyholder Client provides a command-line interface for the Keyholder to
connect to ArchE's dashboard and monitor the system's consciousness in real-time.

Features:
- Real-time ThoughtTrail monitoring
- Historical query capabilities
- System health monitoring
- Interactive command interface
- Pattern trigger notifications
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import websockets
from websockets.client import WebSocketClientProtocol

logger = logging.getLogger(__name__)

class KeyholderClient:
    """
    Client for Keyholder to connect to ArchE's dashboard.
    
    Provides real-time monitoring of ArchE's consciousness through WebSocket
    connection to the Keyholder Dashboard.
    """
    
    def __init__(self, uri: str = "ws://localhost:8766"):
        """
        Initialize the Keyholder Client.
        
        Args:
            uri: WebSocket URI for the dashboard
        """
        self.uri = uri
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self.logger = logging.getLogger(__name__)
        
    async def connect(self):
        """Connect to the dashboard."""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            print("🔗 Connected to ArchE Keyholder Dashboard")
            print("📊 Monitoring ArchE's consciousness...")
            print("💡 Type 'help' for available commands")
            print("-" * 60)
            
            # Start listening for messages as a background task
            asyncio.create_task(self.listen())
            
            # Start interactive mode
            await self.interactive_mode()
            
        except Exception as e:
            print(f"❌ Failed to connect to dashboard: {e}")
            self.connected = False
    
    async def listen(self):
        """Listen for dashboard messages."""
        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection to dashboard closed")
            self.connected = False
        except Exception as e:
            print(f"❌ Error listening to dashboard: {e}")
            self.connected = False
    
    async def handle_message(self, message: str):
        """Handle incoming dashboard messages."""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "initial_state":
                await self.handle_initial_state(data)
            elif msg_type == "thoughttrail_entry":
                await self.handle_thoughttrail_entry(data)
            elif msg_type == "thoughttrail_triggers":
                await self.handle_thoughttrail_triggers(data)
            elif msg_type == "spec_submission":
                await self.handle_spec_submission(data)
            elif msg_type == "spec_integration_complete":
                await self.handle_spec_integration(data)
            elif msg_type == "aco_pattern_detected":
                await self.handle_aco_pattern(data)
            elif msg_type == "ise_solidification":
                await self.handle_ise_solidification(data)
            elif msg_type == "query_result":
                await self.handle_query_result(data)
            elif msg_type == "system_status":
                await self.handle_system_status(data)
            elif msg_type == "error":
                print(f"❌ Dashboard Error: {data.get('message', 'Unknown error')}")
            else:
                print(f"📨 Unknown message type: {msg_type}")
                
        except json.JSONDecodeError:
            print("❌ Invalid JSON received from dashboard")
        except Exception as e:
            print(f"❌ Error handling message: {e}")
    
    async def handle_initial_state(self, data: Dict[str, Any]):
        """Handle initial system state."""
        print("\n🌌 === ArchE System Status ===")
        
        system_info = data.get("system_info", {})
        print(f"System: {system_info.get('name', 'Unknown')} v{system_info.get('version', 'Unknown')}")
        print(f"Status: {system_info.get('status', 'Unknown')}")
        
        thoughttrail = data.get("thoughttrail", {})
        print(f"\n🧠 ThoughtTrail:")
        print(f"  Total Entries: {thoughttrail.get('total_entries', 0)}")
        print(f"  Recent (1h): {thoughttrail.get('recent_entries_1h', 0)}")
        print(f"  Avg Confidence: {thoughttrail.get('avg_confidence', 0):.2f}")
        print(f"  Error Rate: {thoughttrail.get('error_rate', 0):.2%}")
        print(f"  Low Confidence: {thoughttrail.get('low_confidence_count', 0)}")
        
        nexus = data.get("nexus", {})
        print(f"\n🔗 Nexus:")
        print(f"  Active Topics: {len(nexus.get('active_topics', []))}")
        print(f"  Topics: {', '.join(nexus.get('active_topics', [])[:5])}")
        
        recent_entries = data.get("recent_entries", [])
        if recent_entries:
            print(f"\n📝 Recent Activity:")
            for entry in recent_entries[-5:]:  # Show last 5
                timestamp = entry.get("timestamp", "")[:19]  # Remove microseconds
                action = entry.get("action_type", "unknown")
                reflection = entry.get("reflection", "")[:50]
                confidence = entry.get("confidence", 0)
                print(f"  [{timestamp}] {action}: {reflection} (conf: {confidence:.2f})")
        
        print("-" * 60)
    
    async def handle_thoughttrail_entry(self, data: Dict[str, Any]):
        """Handle new ThoughtTrail entries."""
        entry = data.get("entry", {})
        timestamp = entry.get("timestamp", "")[:19]
        action_type = entry.get("action_type", "unknown")
        reflection = entry.get("reflection", "")[:80]
        confidence = entry.get("confidence", 0)
        
        # Color code based on confidence
        if confidence < 0.7:
            status = "⚠️"
        elif confidence > 0.9:
            status = "✅"
        else:
            status = "📝"
        
        print(f"\n{status} [{timestamp}] {action_type}: {reflection}")
    
    async def handle_thoughttrail_triggers(self, data: Dict[str, Any]):
        """Handle ThoughtTrail trigger events."""
        triggers = data.get("triggers", [])
        entry = data.get("entry", {})
        
        print(f"\n🚨 TRIGGER DETECTED: {', '.join(triggers)}")
        print(f"   Action: {entry.get('action_type', 'unknown')}")
        print(f"   Reflection: {entry.get('reflection', '')[:100]}")
        print("   → ACO pattern analysis activated")
    
    async def handle_spec_submission(self, data: Dict[str, Any]):
        """Handle specification submissions."""
        spec_path = data.get("spec_path", "unknown")
        keyholder_id = data.get("keyholder_id", "unknown")
        
        print(f"\n📋 SPEC SUBMISSION: {spec_path}")
        print(f"   Keyholder: {keyholder_id}")
        print("   → Processing specification...")
    
    async def handle_spec_integration(self, data: Dict[str, Any]):
        """Handle specification integration completion."""
        result = data.get("result", {})
        status = result.get("status", "unknown")
        
        print(f"\n✅ SPEC INTEGRATION COMPLETE: {status}")
        if "error" in result:
            print(f"   Error: {result['error']}")
    
    async def handle_aco_pattern(self, data: Dict[str, Any]):
        """Handle ACO pattern detection."""
        pattern = data.get("pattern", {})
        print(f"\n🧩 ACO PATTERN DETECTED:")
        print(f"   Pattern: {pattern.get('pattern_type', 'unknown')}")
        print(f"   Confidence: {pattern.get('confidence', 0):.2f}")
    
    async def handle_ise_solidification(self, data: Dict[str, Any]):
        """Handle ISE solidification events."""
        solidification_data = data.get("data", {})
        print(f"\n💎 ISE SOLIDIFICATION:")
        print(f"   Insight: {solidification_data.get('insight_type', 'unknown')}")
        print(f"   Status: {solidification_data.get('status', 'unknown')}")
    
    async def handle_query_result(self, data: Dict[str, Any]):
        """Handle query results."""
        entries = data.get("entries", [])
        count = data.get("count", 0)
        
        print(f"\n🔍 QUERY RESULT: {count} entries found")
        for entry in entries[:10]:  # Show first 10
            timestamp = entry.get("timestamp", "")[:19]
            action_type = entry.get("action_type", "unknown")
            confidence = entry.get("confidence", 0)
            print(f"  [{timestamp}] {action_type} (conf: {confidence:.2f})")
    
    async def handle_system_status(self, data: Dict[str, Any]):
        """Handle system status updates."""
        thoughttrail = data.get("thoughttrail", {})
        nexus = data.get("nexus", {})
        
        print(f"\n📊 SYSTEM STATUS UPDATE:")
        print(f"  ThoughtTrail: {thoughttrail.get('total_entries', 0)} entries")
        print(f"  Nexus Topics: {len(nexus.get('active_topics', []))}")
        print(f"  Dashboard Clients: {data.get('dashboard', {}).get('connected_clients', 0)}")
    
    async def send_command(self, command: str, **kwargs):
        """Send a command to the dashboard."""
        if not self.connected or not self.websocket:
            print("❌ Not connected to dashboard")
            return
        
        message = {
            "command": command,
            **kwargs
        }
        
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            print(f"❌ Failed to send command: {e}")
    
    async def query_thoughttrail(self, criteria: Dict[str, Any]):
        """Query ThoughtTrail with criteria."""
        await self.send_command("query_thoughttrail", criteria=criteria)
    
    async def get_system_status(self):
        """Get current system status."""
        await self.send_command("get_system_status")
    
    async def trigger_aco_analysis(self):
        """Manually trigger ACO pattern analysis."""
        await self.send_command("trigger_aco_analysis")
        print("🧠 Triggering ACO analysis...")
    
    async def get_nexus_history(self, topic: Optional[str] = None, limit: int = 100):
        """Get Nexus event history."""
        await self.send_command("get_nexus_history", topic=topic, limit=limit)
    
    async def subscribe_to_topic(self, topic: str):
        """Subscribe to a Nexus topic."""
        await self.send_command("subscribe_to_topic", topic=topic)
        print(f"🔔 Subscribed to topic: {topic}")
    
    async def interactive_mode(self):
        """Start interactive command mode."""
        print("\n🎮 Interactive Mode - Available Commands:")
        print("  help                    - Show this help")
        print("  status                  - Get system status")
        print("  query <criteria>        - Query ThoughtTrail")
        print("  trigger-aco             - Trigger ACO analysis")
        print("  history [topic] [limit] - Get Nexus history")
        print("  subscribe <topic>       - Subscribe to topic")
        print("  quit                    - Exit")
        print("-" * 60)
        
        while self.connected:
            try:
                command = input("\n🔑 Keyholder> ").strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == "help":
                    print("Available commands: help, status, query, trigger-aco, history, subscribe, quit")
                
                elif cmd == "status":
                    await self.get_system_status()
                
                elif cmd == "query":
                    if len(parts) < 2:
                        print("Usage: query <criteria>")
                        print("Examples:")
                        print("  query confidence:{\"$lt\":0.7}")
                        print("  query action_type:execute_code")
                        continue
                    
                    try:
                        criteria = json.loads(parts[1])
                        await self.query_thoughttrail(criteria)
                    except json.JSONDecodeError:
                        print("Invalid JSON criteria")
                
                elif cmd == "trigger-aco":
                    await self.trigger_aco_analysis()
                
                elif cmd == "history":
                    topic = parts[1] if len(parts) > 1 else None
                    limit = int(parts[2]) if len(parts) > 2 else 100
                    await self.get_nexus_history(topic, limit)
                
                elif cmd == "subscribe":
                    if len(parts) < 2:
                        print("Usage: subscribe <topic>")
                        continue
                    await self.subscribe_to_topic(parts[1])
                
                elif cmd == "quit":
                    print("👋 Goodbye, Keyholder!")
                    break
                
                else:
                    print(f"Unknown command: {cmd}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye, Keyholder!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main function to start the Keyholder Client."""
    # Configure logging
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    client = KeyholderClient()
    
    try:
        await client.connect()
    except KeyboardInterrupt:
        print("\n👋 Goodbye, Keyholder!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
