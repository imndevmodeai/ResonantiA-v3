import logging
import json
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import asyncio
import websockets
from threading import Thread
import time
from typing import Dict, Any

# --- Flask App Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')

# --- HTML & JavaScript Template ---
# This is a self-contained single-file application for simplicity.
# In a larger system, this would be in a separate templates/ folder.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArchE Visual Cognitive Debugger</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; background-color: #121212; color: #e0e0e0; display: flex; flex-direction: column; height: 100vh; }
        header { background-color: #1e1e1e; padding: 1rem; border-bottom: 1px solid #333; text-align: center; }
        h1 { margin: 0; font-size: 1.5rem; }
        .status-bar { display: flex; justify-content: space-between; padding: 0.5rem 1rem; background-color: #1e1e1e; font-size: 0.9rem; }
        .status-indicator { display: flex; align-items: center; gap: 0.5rem; }
        .dot { height: 10px; width: 10px; background-color: #f44336; border-radius: 50%; display: inline-block; animation: blink 1.5s infinite; }
        .dot.connected { background-color: #4CAF50; animation: none; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
        .main-content { display: flex; flex: 1; overflow: hidden; }
        .log-container { flex: 1; padding: 1rem; overflow-y: auto; border-right: 1px solid #333; }
        .controls-container { width: 300px; padding: 1rem; background-color: #1e1e1e; }
        h2 { margin-top: 0; }
        .log-entry { background-color: #1e1e1e; border-left: 3px solid #4CAF50; padding: 0.8rem; margin-bottom: 0.8rem; border-radius: 4px; font-family: "SF Mono", "Fira Code", monospace; font-size: 0.85rem; white-space: pre-wrap; word-wrap: break-word; }
        .log-entry.error { border-left-color: #f44336; }
        .log-entry.warn { border-left-color: #ff9800; }
        .log-entry .timestamp { color: #888; display: block; margin-bottom: 0.3rem; font-size: 0.75rem; }
        .controls-container button { width: 100%; padding: 0.8rem; margin-bottom: 0.5rem; border: none; background-color: #007bff; color: white; border-radius: 4px; cursor: pointer; }
        .controls-container button:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <header>
        <h1>ArchE - Visual Cognitive Debugger (VCD)</h1>
    </header>
    <div class="status-bar">
        <span>The Mind's Eye of the Machine</span>
        <div class="status-indicator">
            <div id="ws-dot" class="dot"></div>
            <span id="ws-status">Connecting to ArchE Core...</span>
        </div>
    </div>
    <div class="main-content">
        <div class="log-container" id="log-container">
            <!-- Log entries will be injected here -->
        </div>
        <div class="controls-container">
            <h2>Commands</h2>
            <button onclick="sendCommand('get_status')">Get System Status</button>
            <button onclick="sendCommand('run_workflow', { name: 'SimulatedAnalytics' })">Run Analytics Workflow</button>
            <button onclick="clearLogs()">Clear Logs</button>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        const socket = io();
        const logContainer = document.getElementById('log-container');
        const wsStatus = document.getElementById('ws-status');
        const wsDot = document.getElementById('ws-dot');

        socket.on('connect', () => {
            console.log('Connected to VCD UI server.');
        });

        socket.on('bridge_status', (data) => {
            console.log('Bridge status update:', data);
            wsStatus.textContent = data.status;
            if (data.status === 'Connected') {
                wsDot.classList.add('connected');
            } else {
                wsDot.classList.remove('connected');
            }
        });
        
        socket.on('log', (log) => {
            const entry = document.createElement('div');
            entry.classList.add('log-entry');
            if(log.level) entry.classList.add(log.level);

            const timestamp = new Date().toLocaleTimeString();
            let content = `<span class="timestamp">${timestamp}</span>`;
            
            if (typeof log.data === 'object') {
                content += `<strong>${log.source || 'Event'}:</strong><br><pre>${JSON.stringify(log.data, null, 2)}</pre>`;
            } else {
                content += log.data;
            }
            
            entry.innerHTML = content;
            logContainer.appendChild(entry);
            logContainer.scrollTop = logContainer.scrollHeight;
        });

        function sendCommand(type, payload = {}) {
            const command = {
                type: type,
                request_id: 'vcd-' + Date.now(),
                payload: payload
            };
            socket.emit('send_command', command);
            logEvent('Command Sent', command);
        }

        function clearLogs() {
            logContainer.innerHTML = '';
        }

        function logEvent(source, data) {
             socket.emit('log', { source: source, data: data });
        }
    </script>
</body>
</html>
"""

# --- WebSocket Client Logic (Connects to ArchE Core) ---
class ArchEBridgeClient:
    """
    Connects to the ArchE WebSocketBridge, listens for messages,
    and forwards them to the Flask UI via SocketIO.
    """
    def __init__(self, uri="ws://localhost:8765"):
        self.uri = uri
        self.websocket = None
        self.is_running = False
        self.reconnect_delay = 5 # seconds

    async def connect(self):
        """Establish connection to the WebSocket server."""
        while self.is_running:
            try:
                logger.info(f"Attempting to connect to ArchE Bridge at {self.uri}...")
                socketio.emit('bridge_status', {'status': 'Connecting...'})
                async with websockets.connect(self.uri) as websocket:
                    self.websocket = websocket
                    logger.info("Successfully connected to ArchE WebSocket Bridge.")
                    socketio.emit('bridge_status', {'status': 'Connected'})
                    socketio.emit('log', {'source': 'VCD', 'data': 'Connection to ArchE Core established.'})
                    await self.listen()
            except (websockets.exceptions.ConnectionClosedError, OSError) as e:
                logger.warning(f"Connection to ArchE Bridge failed or was lost: {e}. Retrying in {self.reconnect_delay}s...")
                socketio.emit('bridge_status', {'status': f'Disconnected. Retrying...'})
            except Exception as e:
                logger.error(f"An unexpected error occurred in ArchEBridgeClient: {e}", exc_info=True)
            
            self.websocket = None
            await asyncio.sleep(self.reconnect_delay)

    async def listen(self):
        """Listen for incoming messages from the bridge."""
        while self.websocket and self.is_running:
            try:
                message_str = await self.websocket.recv()
                message = json.loads(message_str)
                logger.info(f"Received message from ArchE Bridge: {message}")
                # Forward the message to the browser clients
                socketio.emit('log', {'source': 'ArchE Core Response', 'data': message})
            except websockets.exceptions.ConnectionClosed:
                break # Exit listen loop to trigger reconnect

    async def send(self, message: Dict[str, Any]):
        """Send a message to the ArchE Bridge."""
        if self.websocket and self.websocket.open:
            await self.websocket.send(json.dumps(message))
            logger.info(f"Sent command to ArchE Bridge: {message}")
            return True
        else:
            logger.warning("Cannot send command: Not connected to ArchE Bridge.")
            socketio.emit('log', {'source': 'VCD', 'level': 'error', 'data': 'Cannot send command. Not connected to ArchE Core.'})
            return False

    def start(self):
        """Start the client connection loop in a background thread."""
        if not self.is_running:
            self.is_running = True
            Thread(target=self.run_async_loop, daemon=True).start()

    def run_async_loop(self):
        """Run the asyncio event loop."""
        asyncio.run(self.connect())

    def stop(self):
        """Stop the client."""
        self.is_running = False


# --- Global Instance & SocketIO Event Handlers ---
arche_client = ArchEBridgeClient()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('connect')
def handle_connect():
    logger.info('VCD UI client connected to server.')
    emit('log', {'source': 'VCD', 'data': 'UI connected to VCD server.'})
    status = 'Connected' if arche_client.websocket else 'Disconnected'
    emit('bridge_status', {'status': status})

@socketio.on('send_command')
def handle_send_command(json_data):
    logger.info(f'UI client sent command: {json_data}')
    # Need to run the async send function in the running loop
    asyncio.run(arche_client.send(json_data))

@socketio.on('log')
def handle_log(data):
    # This is for client-side logging to appear in the UI
    emit('log', data, broadcast=True)

# --- Main Entry Point ---
def main():
    """Main function to run the VCD UI."""
    logger.info("Starting Visual Cognitive Debugger (VCD)...")
    
    # Start the ArchE Bridge client in the background
    arche_client.start()
    
    # Start the Flask-SocketIO server
    logger.info("Starting Flask-SocketIO server on http://localhost:5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    print("--- Visual Cognitive Debugger (VCD) ---")
    print("This server provides a web interface to monitor and interact with the ArchE system.")
    print("1. Ensure the `websocket_bridge.py` server is running first.")
    print("2. Open your web browser and navigate to http://localhost:5001")
    main()
