#!/usr/bin/env python3
"""
Simple test script to run the ArchE Webcam Web UI
This script bypasses the virtual camera requirement for testing
"""

import os
import sys

# Add the project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import and run the web UI
from webcam_streaming_system.web_ui import main

if __name__ == "__main__":
    print("🎥 Starting ArchE Webcam Streaming System Web UI...")
    print("🌐 Web interface will be available at: http://localhost:5000")
    print("📱 Open your browser and navigate to the URL above")
    print("⏹️  Press Ctrl+C to stop the server")
    print("")
    print("Note: Virtual camera support requires /dev/video10 device")
    print("Run 'sudo modprobe v4l2loopback devices=1 video_nr=10 card_label=\"ArchE_Webcam\" exclusive_caps=0' to enable it")
    print("")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

