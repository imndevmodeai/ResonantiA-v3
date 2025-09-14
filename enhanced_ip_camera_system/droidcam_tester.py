#!/usr/bin/env python3
"""
DroidCam Connection Tester and Enhanced Webcam Streaming
Built with ArchE's ResonantiA Protocol v3.1-CA

Advanced testing and connection for DroidCam Android IP cameras.
"""

import cv2
import requests
import time
import threading
from urllib.parse import urlparse

def test_http_endpoint(url, timeout=5):
    """Test HTTP endpoint connectivity"""
    try:
        response = requests.get(url, timeout=timeout, stream=True)
        return response.status_code, response.headers.get('content-type', 'unknown')
    except Exception as e:
        return None, str(e)

def test_opencv_connection(url, timeout=10):
    """Test OpenCV connection with enhanced parameters"""
    try:
        # Try different OpenCV backends
        backends = [
            cv2.CAP_FFMPEG,
            cv2.CAP_GSTREAMER, 
            cv2.CAP_V4L2,
            cv2.CAP_ANY
        ]
        
        for backend in backends:
            print(f"  Trying backend: {backend}")
            cap = cv2.VideoCapture(url, backend)
            
            if cap.isOpened():
                # Set buffer size to reduce latency
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_FPS, 30)
                
                start_time = time.time()
                while time.time() - start_time < timeout:
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        cap.release()
                        return True, frame.shape, backend
                    time.sleep(0.1)
                
                cap.release()
        
        return False, "No frame captured", None
        
    except Exception as e:
        return False, str(e), None

def main():
    """Main DroidCam testing function"""
    print("🔍 DROIDCAM ADVANCED CONNECTION TESTER")
    print("Built with ArchE's ResonantiA Protocol v3.1-CA")
    print("=" * 50)
    print()
    
    # DroidCam test URLs
    test_urls = [
        "http://192.168.13.37:3346/video",
        "http://192.168.13.37:3346/mjpegfeed?640x480",
        "http://192.168.13.37:3346/mjpegfeed?1280x720", 
        "http://192.168.13.37:3346/mjpegfeed?320x240",
        "http://192.168.13.37:6969/video",
        "http://192.168.13.37:6969/videofeed",
        "http://192.168.13.37:6969/stream",
        "http://192.168.13.37:6969/mjpeg",
        "http://192.168.13.37:6969/cam.mjpg"
    ]
    
    working_urls = []
    
    for url in test_urls:
        print(f"Testing: {url}")
        
        # Test HTTP connectivity
        status, content_type = test_http_endpoint(url)
        if status:
            print(f"  ✅ HTTP Status: {status}, Content-Type: {content_type}")
            
            # Test OpenCV connectivity
            success, result, backend = test_opencv_connection(url)
            if success:
                print(f"  ✅ OpenCV Success: {result}, Backend: {backend}")
                working_urls.append((url, backend))
            else:
                print(f"  ❌ OpenCV Failed: {result}")
        else:
            print(f"  ❌ HTTP Failed: {content_type}")
        
        print()
    
    if working_urls:
        print("🎉 WORKING CONNECTIONS FOUND!")
        print("=" * 30)
        for url, backend in working_urls:
            print(f"✅ {url} (Backend: {backend})")
        
        # Test the first working URL with live streaming
        print(f"\n🎬 Starting live test with: {working_urls[0][0]}")
        test_live_streaming(working_urls[0][0], working_urls[0][1])
    else:
        print("❌ No working connections found.")
        print("\nTroubleshooting suggestions:")
        print("1. Ensure DroidCam app is running on your Android device")
        print("2. Check that both devices are on the same WiFi network")
        print("3. Verify the IP address is correct")
        print("4. Try different port numbers in DroidCam settings")
        print("5. Check Android firewall/security settings")

def test_live_streaming(url, backend):
    """Test live streaming from working URL"""
    try:
        cap = cv2.VideoCapture(url, backend)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            print("❌ Failed to open live stream")
            return
        
        print("✅ Live stream opened successfully!")
        print("Press 'q' to quit live test...")
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            
            # Add overlay information
            cv2.putText(frame, f"DroidCam Live Test", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Frame: {frame_count}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"URL: {url}", (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("DroidCam Live Test", frame)
            
            # Calculate FPS every 30 frames
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"📊 FPS: {fps:.1f}, Frames: {frame_count}")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time if total_time > 0 else 0
        print(f"\n📊 Live test completed:")
        print(f"   Total frames: {frame_count}")
        print(f"   Duration: {total_time:.1f}s")
        print(f"   Average FPS: {avg_fps:.1f}")
        
    except Exception as e:
        print(f"❌ Live streaming error: {e}")

if __name__ == "__main__":
    main()
