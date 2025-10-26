#!/usr/bin/env python3
# Simple test to isolate VCD issues

import sys
import os

print("Starting VCD test...")

try:
    print("1. Testing basic imports...")
    import json
    import time
    import threading
    from datetime import datetime
    from typing import Dict, Any, List, Optional
    print("✅ Basic imports successful")
    
    print("2. Testing Flask import...")
    from flask import Flask, render_template_string, jsonify, request, Response
    print("✅ Flask import successful")
    
    print("3. Testing queue import...")
    import queue
    print("✅ Queue import successful")
    
    print("4. Testing socket import...")
    import socket
    print("✅ Socket import successful")
    
    print("5. Testing port binding...")
    def find_free_port_in_range(start_port=5000, end_port=5010):
        for port in range(start_port, end_port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        return None
    
    port = find_free_port_in_range()
    if port:
        print(f"✅ Found free port: {port}")
    else:
        print("❌ No free ports found")
        sys.exit(1)
    
    print("6. Testing Flask app creation...")
    app = Flask(__name__)
    print("✅ Flask app created")
    
    print("7. Testing route creation...")
    @app.route('/')
    def test_route():
        return "VCD Test Route Working"
    print("✅ Route created")
    
    print("8. Testing Flask run...")
    print(f"Starting Flask on port {port}...")
    app.run(host='127.0.0.1', port=port, debug=False)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
