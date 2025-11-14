#!/usr/bin/env python3
"""
Simple WebSocket Client for Visual Cognitive Debugger (VCD)
Connects to VCD Bridge and displays real-time cognitive data
"""

import asyncio
import json
import websockets
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich import box

console = Console()

class VCDWebSocketClient:
    """Simple WebSocket client for VCD visualization"""
    
    def __init__(self, uri: str = "ws://localhost:8765"):
        self.uri = uri
        self.connected = False
        self.messages_received = []
        self.cognitive_state = {}
        self.thoughts = []
        
    async def connect(self):
        """Connect to VCD Bridge"""
        try:
            console.print(f"[blue]🔌 Connecting to VCD Bridge at {self.uri}...[/blue]")
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            console.print("[green]✅ Connected to VCD Bridge![/green]")
            return True
        except websockets.exceptions.ConnectionRefused:
            console.print("[red]❌ Connection refused. Is the VCD Bridge running?[/red]")
            console.print("[yellow]   Start it with: python3 vcd_bridge.py[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]❌ Connection error: {e}[/red]")
            return False
    
    async def send_handshake(self):
        """Send handshake message"""
        handshake = {
            "type": "handshake",
            "client": "vcd_websocket_client",
            "timestamp": datetime.now().isoformat(),
            "features": ["real_time_monitoring", "cognitive_state", "visualizations"]
        }
        await self.websocket.send(json.dumps(handshake))
        console.print("[cyan]📤 Sent handshake[/cyan]")
    
    async def request_cognitive_state(self):
        """Request current cognitive state"""
        request = {
            "type": "get_cognitive_state",
            "timestamp": datetime.now().timestamp()
        }
        await self.websocket.send(json.dumps(request))
        console.print("[cyan]📤 Requested cognitive state[/cyan]")
    
    async def listen(self, duration: int = 30):
        """Listen for messages for specified duration"""
        console.print(f"[blue]👂 Listening for {duration} seconds...[/blue]")
        console.print("[yellow]   (Press Ctrl+C to stop early)[/yellow]\n")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            while True:
                # Check timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= duration:
                    console.print(f"\n[blue]⏱️  {duration} seconds elapsed. Stopping...[/blue]")
                    break
                
                # Wait for message with timeout
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=1.0
                    )
                    await self.handle_message(message)
                except asyncio.TimeoutError:
                    # No message received, continue listening
                    continue
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]⏹️  Stopped by user[/yellow]")
        except Exception as e:
            console.print(f"\n[red]❌ Error: {e}[/red]")
    
    async def handle_message(self, message: str):
        """Handle incoming message"""
        try:
            data = json.loads(message)
            msg_type = data.get("type", "unknown")
            
            # Store message
            self.messages_received.append({
                "type": msg_type,
                "timestamp": datetime.now().isoformat(),
                "data": data
            })
            
            # Display based on type
            if msg_type == "welcome":
                self.display_welcome(data)
            elif msg_type == "cognitive_state":
                self.cognitive_state = data.get("cognitive_state", {})
                self.display_cognitive_state(data)
            elif msg_type == "thought_process":
                self.thoughts.append(data)
                self.display_thought(data)
            elif msg_type == "event":
                self.display_event(data)
            elif msg_type == "visualization":
                self.display_visualization(data)
            else:
                self.display_generic(data)
                
        except json.JSONDecodeError:
            console.print(f"[yellow]⚠️  Received non-JSON message: {message[:100]}...[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Error handling message: {e}[/red]")
    
    def display_welcome(self, data: dict):
        """Display welcome message"""
        message = data.get("message", "Welcome!")
        console.print(Panel(
            f"[green]{message}[/green]\n"
            f"Server: {data.get('server', 'VCD Bridge')}\n"
            f"Session: {data.get('session_id', 'N/A')}",
            title="🎉 VCD Welcome",
            border_style="green"
        ))
    
    def display_cognitive_state(self, data: dict):
        """Display cognitive state"""
        state = data.get("cognitive_state", {})
        
        table = Table(title="🧠 Cognitive State", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        if "active_sprs" in state:
            table.add_row("Active SPRs", str(len(state["active_sprs"])))
        if "recent_thoughts" in state:
            table.add_row("Recent Thoughts", str(len(state["recent_thoughts"])))
        if "cognitive_resonance" in state:
            table.add_row("Cognitive Resonance", f"{state['cognitive_resonance']:.2f}")
        if "temporal_resonance" in state:
            tr = state["temporal_resonance"]
            if isinstance(tr, dict):
                table.add_row("Temporal Coherence", f"{tr.get('temporal_coherence', 0):.2f}")
        
        console.print(table)
    
    def display_thought(self, data: dict):
        """Display thought process"""
        message = data.get("message", "")
        context = data.get("context", {})
        
        thought_text = f"[cyan]{message}[/cyan]"
        if context:
            thought_text += f"\n[dim]Context: {json.dumps(context, indent=2)[:200]}...[/dim]"
        
        console.print(Panel(
            thought_text,
            title="💭 Thought Process",
            border_style="cyan"
        ))
    
    def display_event(self, data: dict):
        """Display event"""
        event = data.get("event", {})
        event_type = event.get("type", "unknown")
        title = event.get("title", event_type)
        description = event.get("description", "")
        
        console.print(Panel(
            f"[yellow]{title}[/yellow]\n{description}",
            title=f"📡 Event: {event_type}",
            border_style="yellow"
        ))
    
    def display_visualization(self, data: dict):
        """Display visualization data"""
        mode = data.get("mode", "unknown")
        viz_data = data.get("visualization_data", {})
        
        console.print(Panel(
            f"[magenta]Mode: {mode}[/magenta]\n"
            f"Nodes: {viz_data.get('nodes', {}).get('count', 0)}\n"
            f"Edges: {viz_data.get('edges', {}).get('count', 0)}",
            title="🎨 Visualization",
            border_style="magenta"
        ))
    
    def display_generic(self, data: dict):
        """Display generic message"""
        msg_type = data.get("type", "unknown")
        console.print(f"[dim]📨 {msg_type}: {json.dumps(data, indent=2)[:200]}...[/dim]")
    
    def display_summary(self):
        """Display summary of received messages"""
        console.print("\n" + "=" * 80)
        console.print("[bold]📊 Summary[/bold]")
        console.print("=" * 80)
        
        # Count message types
        type_counts = {}
        for msg in self.messages_received:
            msg_type = msg["type"]
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
        
        table = Table(title="Message Statistics", box=box.ROUNDED)
        table.add_column("Message Type", style="cyan")
        table.add_column("Count", style="green")
        
        for msg_type, count in sorted(type_counts.items()):
            table.add_row(msg_type, str(count))
        
        console.print(table)
        console.print(f"\n[green]✅ Total messages received: {len(self.messages_received)}[/green]")
    
    async def disconnect(self):
        """Disconnect from VCD Bridge"""
        if self.connected:
            await self.websocket.close()
            self.connected = False
            console.print("[blue]🔌 Disconnected from VCD Bridge[/blue]")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VCD WebSocket Client")
    parser.add_argument("--uri", default="ws://localhost:8765", help="VCD Bridge WebSocket URI")
    parser.add_argument("--duration", type=int, default=30, help="Listen duration in seconds")
    args = parser.parse_args()
    
    client = VCDWebSocketClient(uri=args.uri)
    
    # Connect
    if not await client.connect():
        sys.exit(1)
    
    try:
        # Send handshake
        await client.send_handshake()
        await asyncio.sleep(0.5)
        
        # Request cognitive state
        await client.request_cognitive_state()
        await asyncio.sleep(0.5)
        
        # Listen for messages
        await client.listen(duration=args.duration)
        
        # Display summary
        client.display_summary()
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]💥 Fatal error: {e}[/red]")
        sys.exit(1)

