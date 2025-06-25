#!/usr/bin/env python3
"""
DroidCam Diagnostic Suite
Built with ArchE's ResonantiA Protocol v3.1-CA

Comprehensive diagnostic tool for DroidCam connection issues.
"""

import socket
import requests
import subprocess
import time
import threading
import json
from urllib.parse import urlparse

class DroidCamDiagnostic:
    def __init__(self, host="192.168.13.37"):
        self.host = host
        self.common_ports = [3346, 6969, 4747, 8080]
        self.common_paths = [
            "/video", "/mjpegfeed", "/videofeed", "/cam", "/stream",
            "/mjpeg", "/video.mjpg", "/video.cgi", "/axis-cgi/mjpg/video.cgi"
        ]
        
    def test_basic_connectivity(self):
        """Test basic network connectivity"""
        print("🌐 BASIC CONNECTIVITY TEST")
        print("=" * 30)
        
        # Ping test
        try:
            result = subprocess.run(['ping', '-c', '3', self.host], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Ping successful to {self.host}")
            else:
                print(f"❌ Ping failed to {self.host}")
                return False
        except Exception as e:
            print(f"❌ Ping error: {e}")
            return False
        
        return True
    
    def scan_ports(self):
        """Scan for open ports"""
        print(f"\n🔍 PORT SCANNING: {self.host}")
        print("=" * 30)
        
        open_ports = []
        for port in self.common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.host, port))
                if result == 0:
                    print(f"✅ Port {port} is open")
                    open_ports.append(port)
                else:
                    print(f"❌ Port {port} is closed")
                sock.close()
            except Exception as e:
                print(f"❌ Port {port} error: {e}")
        
        return open_ports
    
    def test_http_endpoints(self, ports):
        """Test HTTP endpoints on open ports"""
        print(f"\n🌍 HTTP ENDPOINT TESTING")
        print("=" * 30)
        
        working_endpoints = []
        
        for port in ports:
            for path in self.common_paths:
                url = f"http://{self.host}:{port}{path}"
                try:
                    print(f"Testing: {url}")
                    
                    # Test with different user agents
                    headers_list = [
                        {'User-Agent': 'DroidCam-Client'},
                        {'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'},
                        {'User-Agent': 'OpenCV'},
                        {'User-Agent': 'VLC media player'},
                        {}  # No user agent
                    ]
                    
                    for headers in headers_list:
                        try:
                            response = requests.get(url, headers=headers, timeout=5, stream=True)
                            print(f"  Status: {response.status_code}")
                            print(f"  Headers: {dict(response.headers)}")
                            
                            if response.status_code == 200:
                                content_type = response.headers.get('content-type', '')
                                if 'image' in content_type or 'video' in content_type or 'multipart' in content_type:
                                    print(f"  ✅ Found video stream: {content_type}")
                                    working_endpoints.append((url, headers, content_type))
                                    
                                    # Try to get first chunk
                                    chunk = next(response.iter_content(chunk_size=1024), None)
                                    if chunk:
                                        print(f"  📊 First chunk: {len(chunk)} bytes")
                                        print(f"  🔍 Hex: {chunk[:20].hex()}")
                                        break
                            
                        except requests.exceptions.RequestException as e:
                            continue
                    
                except Exception as e:
                    print(f"  ❌ Error: {e}")
        
        return working_endpoints
    
    def test_raw_socket_connection(self, port):
        """Test raw socket connection with different protocols"""
        print(f"\n🔌 RAW SOCKET TEST: Port {port}")
        print("=" * 30)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.host, port))
            
            # Try different HTTP requests
            requests_to_try = [
                f"GET /video HTTP/1.1\r\nHost: {self.host}:{port}\r\nUser-Agent: DroidCam-Client\r\n\r\n",
                f"GET /mjpegfeed HTTP/1.1\r\nHost: {self.host}:{port}\r\nAccept: multipart/x-mixed-replace\r\n\r\n",
                f"GET / HTTP/1.1\r\nHost: {self.host}:{port}\r\n\r\n",
                f"GET /video HTTP/1.0\r\n\r\n"
            ]
            
            for i, request in enumerate(requests_to_try):
                try:
                    print(f"Trying request {i+1}...")
                    sock.send(request.encode())
                    
                    # Read response
                    response = sock.recv(4096)
                    if response:
                        print(f"  ✅ Got response: {len(response)} bytes")
                        print(f"  📄 Headers: {response[:200]}")
                        
                        # Check for video data
                        if b'\xff\xd8\xff' in response:
                            print("  🎬 JPEG data detected!")
                        if b'Content-Type: image' in response:
                            print("  ��️ Image content type found!")
                        if b'Content-Type: multipart' in response:
                            print("  📹 Multipart stream found!")
                        
                        return True
                    else:
                        print(f"  ❌ No response to request {i+1}")
                        
                except Exception as e:
                    print(f"  ❌ Request {i+1} error: {e}")
            
            sock.close()
            
        except Exception as e:
            print(f"❌ Socket connection error: {e}")
        
        return False
    
    def test_droidcam_specific_endpoints(self):
        """Test DroidCam-specific endpoints and protocols"""
        print(f"\n📱 DROIDCAM SPECIFIC TESTS")
        print("=" * 30)
        
        # DroidCam usually uses these specific endpoints
        droidcam_endpoints = [
            "http://192.168.13.37:3346/video",
            "http://192.168.13.37:3346/mjpegfeed?640x480",
            "http://192.168.13.37:3346/mjpegfeed?320x240",
            "http://192.168.13.37:6969/video",
            "http://192.168.13.37:6969/mjpegfeed",
            "http://192.168.13.37:4747/video",  # Default DroidCam port
            "http://192.168.13.37:4747/mjpegfeed"
        ]
        
        working_urls = []
        
        for url in droidcam_endpoints:
            try:
                print(f"Testing DroidCam URL: {url}")
                
                # Try with DroidCam client headers
                headers = {
                    'User-Agent': 'DroidCam-Client',
                    'Accept': 'multipart/x-mixed-replace,image/jpeg',
                    'Connection': 'keep-alive'
                }
                
                response = requests.get(url, headers=headers, timeout=10, stream=True)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    print(f"  Content-Type: {content_type}")
                    
                    # Get first chunk
                    try:
                        chunk = next(response.iter_content(chunk_size=2048), None)
                        if chunk:
                            print(f"  ✅ Got data: {len(chunk)} bytes")
                            print(f"  🔍 First 50 bytes: {chunk[:50]}")
                            
                            # Check for JPEG signature
                            if chunk.startswith(b'\xff\xd8\xff'):
                                print("  🎬 JPEG image detected!")
                                working_urls.append(url)
                            elif b'--' in chunk and b'Content-Type: image/jpeg' in chunk:
                                print("  📹 MJPEG stream detected!")
                                working_urls.append(url)
                            else:
                                print("  ⚠️ Unknown format")
                        else:
                            print("  ❌ No data received")
                    except Exception as e:
                        print(f"  ❌ Data read error: {e}")
                else:
                    print(f"  ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Connection error: {e}")
        
        return working_urls
    
    def test_opencv_compatibility(self, working_urls):
        """Test OpenCV compatibility with working URLs"""
        print(f"\n🎥 OPENCV COMPATIBILITY TEST")
        print("=" * 30)
        
        if not working_urls:
            print("❌ No working URLs to test")
            return False
        
        import cv2
        
        for url in working_urls:
            print(f"Testing OpenCV with: {url}")
            
            try:
                cap = cv2.VideoCapture(url)
                if cap.isOpened():
                    print("  ✅ OpenCV opened successfully")
                    
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"  🎬 Frame captured: {frame.shape}")
                        print("  ✅ SUCCESS! This URL works with OpenCV")
                        cap.release()
                        return url
                    else:
                        print("  ❌ Could not read frame")
                else:
                    print("  ❌ OpenCV could not open stream")
                
                cap.release()
                
            except Exception as e:
                print(f"  ❌ OpenCV error: {e}")
        
        return False
    
    def run_full_diagnostic(self):
        """Run complete diagnostic suite"""
        print("🔬 DROIDCAM DIAGNOSTIC SUITE")
        print("Built with ArchE's ResonantiA Protocol v3.1-CA")
        print("=" * 50)
        
        # Step 1: Basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Check network connection.")
            return
        
        # Step 2: Port scanning
        open_ports = self.scan_ports()
        if not open_ports:
            print("❌ No open ports found. Check DroidCam app is running.")
            return
        
        # Step 3: HTTP endpoint testing
        working_endpoints = self.test_http_endpoints(open_ports)
        
        # Step 4: Raw socket testing
        for port in open_ports:
            self.test_raw_socket_connection(port)
        
        # Step 5: DroidCam specific testing
        working_urls = self.test_droidcam_specific_endpoints()
        
        # Step 6: OpenCV compatibility
        if working_urls:
            opencv_url = self.test_opencv_compatibility(working_urls)
            if opencv_url:
                print(f"\n🎉 SUCCESS! Working OpenCV URL: {opencv_url}")
                return opencv_url
        
        print(f"\n🔧 TROUBLESHOOTING RECOMMENDATIONS:")
        print("1. Ensure DroidCam app is running and showing camera preview")
        print("2. Check DroidCam settings - try different video quality")
        print("3. Restart DroidCam app completely")
        print("4. Try different IP address (check 'adb shell ip addr')")
        print("5. Check firewall settings on Android device")
        print("6. Try connecting from another device/app first")
        
        return None

def main():
    diagnostic = DroidCamDiagnostic()
    working_url = diagnostic.run_full_diagnostic()
    
    if working_url:
        print(f"\n✅ Use this URL in your applications: {working_url}")
    else:
        print(f"\n❌ No working video stream found")

if __name__ == "__main__":
    main()
