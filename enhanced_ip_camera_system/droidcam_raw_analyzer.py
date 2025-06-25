#!/usr/bin/env python3
"""
DroidCam Raw Stream Analyzer
Built with ArchE's ResonantiA Protocol v3.1-CA

Captures and analyzes raw stream data to understand DroidCam format.
"""

import socket
import time
import threading
import cv2
import numpy as np

def capture_raw_stream(host, port, path="/video", duration=10):
    """Capture raw stream data and analyze format"""
    try:
        print(f"🔍 Capturing raw stream from {host}:{port}{path}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        
        # Send HTTP request
        request = f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUser-Agent: DroidCam-Client\r\nConnection: keep-alive\r\n\r\n"
        sock.send(request.encode())
        
        # Capture initial response
        initial_data = sock.recv(4096)
        print(f"📄 Initial response ({len(initial_data)} bytes):")
        print("=" * 50)
        
        # Try to decode as text first
        try:
            text_data = initial_data.decode('utf-8', errors='ignore')
            print("TEXT CONTENT:")
            print(text_data[:500])
            print("=" * 50)
        except:
            print("Cannot decode as text")
        
        # Show hex dump
        print("HEX DUMP (first 200 bytes):")
        hex_data = initial_data[:200].hex()
        for i in range(0, len(hex_data), 32):
            print(f"{i//2:04x}: {hex_data[i:i+32]}")
        print("=" * 50)
        
        # Look for common video format signatures
        print("🔍 ANALYZING VIDEO FORMAT SIGNATURES:")
        signatures = {
            b'\xff\xd8\xff': 'JPEG',
            b'\x00\x00\x00\x18ftypmp4': 'MP4',
            b'\x1a\x45\xdf\xa3': 'WebM/Matroska',
            b'--': 'MJPEG boundary',
            b'Content-Type: image/jpeg': 'MJPEG stream',
            b'Content-Type: video/': 'Video stream'
        }
        
        for sig, format_name in signatures.items():
            if sig in initial_data:
                print(f"  ✅ Found {format_name} signature")
        
        # Try to find MJPEG boundary
        if b'--' in initial_data:
            boundary_start = initial_data.find(b'--')
            boundary_end = initial_data.find(b'\r\n', boundary_start)
            if boundary_end > boundary_start:
                boundary = initial_data[boundary_start:boundary_end]
                print(f"  📍 MJPEG Boundary: {boundary}")
        
        # Continue capturing for analysis
        print(f"\n📡 Capturing stream for {duration} seconds...")
        total_data = len(initial_data)
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                total_data += len(chunk)
                
                # Look for JPEG markers in stream
                if b'\xff\xd8\xff' in chunk:
                    print(f"  📸 JPEG frame detected at {total_data} bytes")
                
            except socket.timeout:
                break
        
        sock.close()
        
        print(f"\n📊 Stream Analysis Complete:")
        print(f"   Total data captured: {total_data} bytes")
        print(f"   Average bitrate: {(total_data * 8) / duration / 1024:.1f} kbps")
        
        return initial_data
        
    except Exception as e:
        print(f"❌ Raw capture error: {e}")
        return None

def try_manual_mjpeg_parse(host, port, path="/video"):
    """Try to manually parse MJPEG stream"""
    try:
        print(f"\n🔧 MANUAL MJPEG PARSING ATTEMPT")
        print("=" * 40)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        # Send request with MJPEG-specific headers
        request = f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nAccept: multipart/x-mixed-replace\r\nUser-Agent: OpenCV\r\nConnection: keep-alive\r\n\r\n"
        sock.send(request.encode())
        
        # Read response
        response = b""
        while len(response) < 4096:
            chunk = sock.recv(1024)
            if not chunk:
                break
            response += chunk
            if b'\r\n\r\n' in response:
                break
        
        # Split headers and body
        if b'\r\n\r\n' in response:
            headers, body = response.split(b'\r\n\r\n', 1)
            print("📄 HTTP Headers:")
            print(headers.decode('utf-8', errors='ignore'))
            print("\n📄 Body start:")
            print(body[:100])
            
            # Try to find boundary
            headers_str = headers.decode('utf-8', errors='ignore')
            if 'boundary=' in headers_str:
                boundary = headers_str.split('boundary=')[1].split('\r\n')[0].strip()
                print(f"  📍 Found boundary: {boundary}")
                
                # Try to extract first frame
                boundary_bytes = f"--{boundary}".encode()
                if boundary_bytes in body:
                    print("  ✅ Boundary found in stream!")
                    return True
        
        sock.close()
        return False
        
    except Exception as e:
        print(f"❌ Manual MJPEG parse error: {e}")
        return False

def try_gstreamer_approach(host, port, path="/video"):
    """Try GStreamer pipeline approach"""
    try:
        print(f"\n🚀 GSTREAMER PIPELINE APPROACH")
        print("=" * 35)
        
        # Try different GStreamer pipelines
        pipelines = [
            f"souphttpsrc location=http://{host}:{port}{path} ! jpegdec ! videoconvert ! appsink",
            f"souphttpsrc location=http://{host}:{port}{path} ! multipartdemux ! jpegdec ! videoconvert ! appsink",
            f"tcpclientsrc host={host} port={port} ! jpegdec ! videoconvert ! appsink"
        ]
        
        for i, pipeline in enumerate(pipelines):
            print(f"Testing pipeline {i+1}: {pipeline[:60]}...")
            
            cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"  ✅ SUCCESS! Frame size: {frame.shape}")
                    cap.release()
                    return pipeline
                cap.release()
            print(f"  ❌ Pipeline {i+1} failed")
        
        return None
        
    except Exception as e:
        print(f"❌ GStreamer error: {e}")
        return None

def main():
    """Main raw stream analysis"""
    print("🔬 DROIDCAM RAW STREAM ANALYZER")
    print("Built with ArchE's ResonantiA Protocol v3.1-CA")
    print("=" * 50)
    print()
    
    host = "192.168.13.37"
    test_configs = [
        (3346, "/video"),
        (3346, "/mjpegfeed?640x480"),
        (6969, "/video"),
        (6969, "/videofeed")
    ]
    
    for port, path in test_configs:
        print(f"\n🔍 ANALYZING: {host}:{port}{path}")
        print("=" * 60)
        
        # Capture and analyze raw stream
        raw_data = capture_raw_stream(host, port, path, duration=5)
        
        if raw_data:
            # Try manual MJPEG parsing
            mjpeg_success = try_manual_mjpeg_parse(host, port, path)
            
            # Try GStreamer approach
            if mjpeg_success:
                gst_pipeline = try_gstreamer_approach(host, port, path)
                if gst_pipeline:
                    print(f"\n🎉 WORKING GSTREAMER PIPELINE FOUND!")
                    print(f"Pipeline: {gst_pipeline}")
                    
                    # Test live streaming
                    print("\n🎬 Testing live stream (press 'q' to quit)...")
                    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
                    if cap.isOpened():
                        frame_count = 0
                        while frame_count < 100:  # Test 100 frames
                            ret, frame = cap.read()
                            if ret and frame is not None:
                                cv2.imshow("DroidCam Live", frame)
                                frame_count += 1
                                if cv2.waitKey(1) & 0xFF == ord('q'):
                                    break
                            else:
                                break
                        cap.release()
                        cv2.destroyAllWindows()
                        print(f"✅ Successfully streamed {frame_count} frames!")
                        return
        
        print(f"❌ Analysis failed for {host}:{port}{path}")
    
    print("\n🔧 FINAL TROUBLESHOOTING RECOMMENDATIONS:")
    print("1. Ensure DroidCam app is actively streaming (green indicator)")
    print("2. Try different video quality settings in DroidCam")
    print("3. Restart DroidCam app and try again")
    print("4. Check if DroidCam requires authentication")
    print("5. Try connecting with VLC player first: vlc http://192.168.13.37:3346/video")

if __name__ == "__main__":
    main()
