#!/usr/bin/env python3
"""
DroidCam HTTP-Only Connection Tester
Built with ArchE's ResonantiA Protocol v3.1-CA

Forces HTTP-only connections to avoid TLS read packet errors.
"""

import cv2
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Disable SSL warnings and force HTTP
urllib3.disable_warnings(InsecureRequestWarning)

def test_raw_http_connection(host, port, path="/"):
    """Test raw HTTP connection without SSL"""
    import socket
    import time
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        
        # Send raw HTTP request
        request = f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nConnection: close\r\n\r\n"
        sock.send(request.encode())
        
        # Read response
        response = sock.recv(1024).decode('utf-8', errors='ignore')
        sock.close()
        
        return True, response[:200] + "..." if len(response) > 200 else response
        
    except Exception as e:
        return False, str(e)

def test_opencv_with_params(url):
    """Test OpenCV with specific parameters to avoid SSL"""
    try:
        # Force HTTP backend parameters
        cap = cv2.VideoCapture()
        
        # Set properties before opening
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Open with explicit HTTP
        success = cap.open(url)
        
        if success:
            print(f"  ✅ OpenCV opened: {url}")
            
            # Try to read frame
            for attempt in range(50):  # Try 50 times over 5 seconds
                ret, frame = cap.read()
                if ret and frame is not None:
                    cap.release()
                    return True, frame.shape
                time.sleep(0.1)
            
            cap.release()
            return False, "Opened but no frame received"
        else:
            return False, "Failed to open"
            
    except Exception as e:
        return False, str(e)

def main():
    """Main HTTP-only testing function"""
    print("🔧 DROIDCAM HTTP-ONLY CONNECTION TESTER")
    print("Built with ArchE's ResonantiA Protocol v3.1-CA")
    print("=" * 50)
    print()
    
    host = "192.168.13.37"
    ports_and_paths = [
        (3346, "/video"),
        (3346, "/mjpegfeed?640x480"),
        (3346, "/mjpegfeed?320x240"),
        (3346, "/"),
        (6969, "/video"),
        (6969, "/videofeed"),
        (6969, "/stream"),
        (6969, "/")
    ]
    
    working_connections = []
    
    for port, path in ports_and_paths:
        url = f"http://{host}:{port}{path}"
        print(f"Testing: {url}")
        
        # Test raw HTTP socket connection
        success, response = test_raw_http_connection(host, port, path)
        if success:
            print(f"  ✅ Raw HTTP Success")
            print(f"  📄 Response preview: {response[:100]}...")
            
            # Test OpenCV connection
            cv_success, cv_result = test_opencv_with_params(url)
            if cv_success:
                print(f"  ✅ OpenCV Success: {cv_result}")
                working_connections.append(url)
            else:
                print(f"  ⚠️  OpenCV Issue: {cv_result}")
        else:
            print(f"  ❌ Raw HTTP Failed: {response}")
        
        print()
    
    if working_connections:
        print("🎉 WORKING HTTP CONNECTIONS FOUND!")
        print("=" * 35)
        for url in working_connections:
            print(f"✅ {url}")
        
        # Test live streaming with first working connection
        print(f"\n🎬 Testing live streaming with: {working_connections[0]}")
        test_live_stream(working_connections[0])
    else:
        print("❌ No working HTTP connections found.")
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("1. Check DroidCam app is running and streaming")
        print("2. Verify 'Start Server' is pressed in DroidCam")
        print("3. Try different quality settings in DroidCam")
        print("4. Restart DroidCam app")
        print("5. Check WiFi connection on both devices")

def test_live_stream(url):
    """Test live streaming with HTTP-only connection"""
    try:
        print("🎬 Starting live stream test...")
        
        cap = cv2.VideoCapture()
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        if not cap.open(url):
            print("❌ Failed to open live stream")
            return
        
        print("✅ Live stream opened! Press 'q' to quit...")
        
        frame_count = 0
        start_time = time.time()
        last_fps_time = time.time()
        fps_counter = 0
        
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("⚠️  No frame received, continuing...")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            fps_counter += 1
            
            # Add overlay
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, f"DroidCam HTTP Stream", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"{current_time}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Frame: {frame_count}", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, url, (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            cv2.imshow("DroidCam HTTP Live Stream", frame)
            
            # Calculate FPS every 3 seconds
            current_time = time.time()
            if current_time - last_fps_time >= 3.0:
                fps = fps_counter / (current_time - last_fps_time)
                print(f"📊 Live FPS: {fps:.1f}, Total Frames: {frame_count}")
                fps_counter = 0
                last_fps_time = current_time
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time if total_time > 0 else 0
        print(f"\n📊 Live stream test completed:")
        print(f"   Total frames: {frame_count}")
        print(f"   Duration: {total_time:.1f}s")
        print(f"   Average FPS: {avg_fps:.1f}")
        
    except Exception as e:
        print(f"❌ Live stream error: {e}")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
