#!/usr/bin/env python3
"""
Web UI for ArchE Webcam Streaming System
Flask-based web interface for cross-platform compatibility
"""

import os
import sys
import json
import logging
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
import cv2
import base64
import numpy as np

# Add the project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, script_dir)  # Also add the webcam_streaming_system directory

# Import webcam streaming components
try:
    from effects_engine import EffectsEngine
    from rtmp_streamer import RTMPStreamer
    from droidcam_manager import DroidCamManager
    from webcam_streaming_system import WebcamStreamingSystem
except ImportError as e:
    logging.error(f"Failed to import webcam streaming components: {e}")
    # Define dummy classes for development
    class EffectsEngine:
        def __init__(self): pass
        def apply_background_blur(self, frame): return frame
        def apply_face_beauty(self, frame): return frame
    
    class RTMPStreamer:
        def __init__(self): pass
        def start_stream(self, platform, url): return True
        def send_frame(self, frame): pass
        def stop_all_streams(self): pass
    
    class DroidCamManager:
        def __init__(self): pass
        def connect(self): return True
        def disconnect(self): pass
        def get_default_ip(self): return "192.168.1.100"
        def get_default_port(self): return "4747"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'arche_webcam_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for streaming
streaming_system = None
camera = None
effects_engine = None
rtmp_streamer = None
droidcam_manager = None
is_streaming = False
current_config = {}

def load_config():
    """Load configuration from JSON file"""
    config_path = os.path.join(project_root, 'webcam_streaming_system', 'streaming_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}")
        return {
            "camera_device": 0,
            "resolution": {"width": 640, "height": 480},
            "fps": 30,
            "effects": {
                "background_blur": False,
                "face_beauty": False
            },
            "rtmp_streams": {},
            "droidcam_settings": {
                "ip": "192.168.1.100",
                "port": "4747",
                "auto_connect": False
            }
        }

def save_config(config):
    """Save configuration to JSON file"""
    config_path = os.path.join(project_root, 'webcam_streaming_system', 'streaming_config.json')
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return False

def initialize_components():
    """Initialize all streaming components"""
    global camera, effects_engine, rtmp_streamer, droidcam_manager
    
    try:
        # Initialize camera
        camera = cv2.VideoCapture(current_config.get('camera_device', 0))
        if not camera.isOpened():
            logger.error("Failed to open camera")
            return False
        
        # Set camera properties
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, current_config['resolution']['width'])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, current_config['resolution']['height'])
        camera.set(cv2.CAP_PROP_FPS, current_config.get('fps', 30))
        
        # Initialize effects engine
        effects_engine = EffectsEngine()
        
        # Initialize RTMP streamer
        rtmp_streamer = RTMPStreamer()
        
        # Initialize DroidCam manager
        droidcam_manager = DroidCamManager()
        
        logger.info("All components initialized successfully")
        logger.info("Note: Virtual camera support requires /dev/video10 device")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        return False

def cleanup_components():
    """Cleanup all streaming components"""
    global camera, rtmp_streamer, is_streaming
    
    is_streaming = False
    
    if camera:
        camera.release()
    
    if rtmp_streamer:
        rtmp_streamer.stop_all_streams()
    
    logger.info("Components cleaned up")

def generate_frames():
    """Generate video frames for streaming"""
    global camera, effects_engine, is_streaming, current_config
    
    while is_streaming and camera:
        try:
            ret, frame = camera.read()
            if not ret:
                logger.warning("Failed to read frame from camera")
                continue
            
            # Apply effects based on configuration
            if current_config.get('effects', {}).get('background_blur', False):
                frame = effects_engine.apply_background_blur(frame)
            
            if current_config.get('effects', {}).get('face_beauty', False):
                frame = effects_engine.apply_face_beauty(frame)
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Control frame rate
            time.sleep(1.0 / current_config.get('fps', 30))
            
        except Exception as e:
            logger.error(f"Error generating frame: {e}")
            break

@app.route('/')
def index():
    """Main web interface"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify(current_config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    global current_config
    
    try:
        new_config = request.json
        current_config.update(new_config)
        
        if save_config(current_config):
            return jsonify({"status": "success", "message": "Configuration updated"})
        else:
            return jsonify({"status": "error", "message": "Failed to save configuration"}), 500
            
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/start_streaming', methods=['POST'])
def start_streaming():
    """Start the streaming system"""
    global is_streaming, streaming_system
    
    try:
        if not is_streaming:
            if initialize_components():
                is_streaming = True
                return jsonify({"status": "success", "message": "Streaming started"})
            else:
                return jsonify({"status": "error", "message": "Failed to initialize components"}), 500
        else:
            return jsonify({"status": "info", "message": "Streaming already active"})
            
    except Exception as e:
        logger.error(f"Error starting streaming: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stop_streaming', methods=['POST'])
def stop_streaming():
    """Stop the streaming system"""
    global is_streaming
    
    try:
        cleanup_components()
        return jsonify({"status": "success", "message": "Streaming stopped"})
        
    except Exception as e:
        logger.error(f"Error stopping streaming: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/droidcam/connect', methods=['POST'])
def connect_droidcam():
    """Connect to DroidCam"""
    global droidcam_manager
    
    try:
        if droidcam_manager and droidcam_manager.connect():
            return jsonify({"status": "success", "message": "DroidCam connected"})
        else:
            return jsonify({"status": "error", "message": "Failed to connect to DroidCam"}), 500
            
    except Exception as e:
        logger.error(f"Error connecting DroidCam: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/droidcam/disconnect', methods=['POST'])
def disconnect_droidcam():
    """Disconnect from DroidCam"""
    global droidcam_manager
    
    try:
        if droidcam_manager:
            droidcam_manager.disconnect()
            return jsonify({"status": "success", "message": "DroidCam disconnected"})
        else:
            return jsonify({"status": "error", "message": "DroidCam not initialized"}), 500
            
    except Exception as e:
        logger.error(f"Error disconnecting DroidCam: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('status', {'message': 'Connected to ArchE Webcam System'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('get_status')
def handle_get_status():
    """Handle status request"""
    emit('status_update', {
        'is_streaming': is_streaming,
        'camera_device': current_config.get('camera_device', 0),
        'resolution': current_config.get('resolution', {'width': 640, 'height': 480}),
        'effects': current_config.get('effects', {}),
        'timestamp': datetime.now().isoformat()
    })

def main():
    """Main function to run the web server"""
    global current_config
    
    # Load configuration
    current_config = load_config()
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    logger.info("Starting ArchE Webcam Web UI Server...")
    logger.info(f"Configuration loaded: {len(current_config)} settings")
    
    # Run the Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()
