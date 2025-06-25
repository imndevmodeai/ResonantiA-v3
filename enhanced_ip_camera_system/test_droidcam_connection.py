#!/usr/bin/env python3
"""
DroidCam Connection Tester
Built with ArchE's ResonantiA Protocol v3.1-CA

Simple script to test when DroidCam is properly configured.
"""

import cv2
import requests
import time

def test_droidcam_urls():
    """Test common DroidCam URLs"""
    urls = [
        "http://192.168.13.37:4747/video",      # Default DroidCam port
        "http://192.168.13.37:3346/video",      # Your custom port  
        "http://192.168.13.37:6969/video",      # Alternative port
        "http://192.168.13.37:4747/mjpegfeed?640x480",
        "http://192.168.13.37:3346/mjpegfeed?640x480"
    ]
    
    print("🔍 TESTING DROIDCAM URLS")
    print("=" * 30)
    
    working_urls = []
    
    for url in urls:
        print(f"\nTesting: {url}")
        
        # First test with requests
        try:
            response = requests.get(url, timeout=5, stream=True, 
                                  headers={'User-Agent': 'DroidCam-Client'})
            print(f"  HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"  Content-Type: {content_type}")
                
                # Try to get first chunk
                try:
                    chunk = next(response.iter_content(chunk_size=1024), None)
                    if chunk and len(chunk) > 0:
                        print(f"  ✅ Got data: {len(chunk)} bytes")
                        if chunk.startswith(b'\xff\xd8\xff'):
                            print("  🎬 JPEG detected!")
                        working_urls.append(url)
                    else:
                        print("  ❌ No data received")
                except Exception as e:
                    print(f"  ❌ Data error: {e}")
            else:
                print(f"  ❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Connection error: {e}")
    
    return working_urls

def test_opencv_capture(working_urls):
    """Test OpenCV capture with working URLs"""
    if not working_urls:
        print("\n❌ No working URLs found - check DroidCam app configuration")
        return False
    
    print(f"\n🎥 TESTING OPENCV CAPTURE")
    print("=" * 30)
    
    for url in working_urls:
        print(f"\nTesting OpenCV with: {url}")
        
        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            print("  ✅ OpenCV opened successfully")
            
            # Try to read a frame
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"  🎬 Frame captured: {frame.shape}")
                print(f"  ✅ SUCCESS! DroidCam is working!")
                
                # Show live preview for 5 seconds
                print("  📺 Showing 5-second preview...")
                start_time = time.time()
                frame_count = 0
                
                while time.time() - start_time < 5:
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        cv2.imshow('DroidCam Test', frame)
                        frame_count += 1
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    else:
                        break
                
                cv2.destroyAllWindows()
                cap.release()
                
                print(f"  📊 Captured {frame_count} frames in 5 seconds")
                print(f"  🎯 FPS: {frame_count/5:.1f}")
                
                return url
            else:
                print("  ❌ Could not read frame")
        else:
            print("  ❌ OpenCV could not open")
        
        cap.release()
    
    return False

def main():
    """Main test function"""
    print("🔬 DROIDCAM CONNECTION TESTER")
    print("Built with ArchE's ResonantiA Protocol v3.1-CA")
    print("=" * 40)
    
    # Test URLs
    working_urls = test_droidcam_urls()
    
    if working_urls:
        print(f"\n✅ Found {len(working_urls)} working URL(s):")
        for url in working_urls:
            print(f"  - {url}")
        
        # Test OpenCV
        success_url = test_opencv_capture(working_urls)
        
        if success_url:
            print(f"\n🎉 DROIDCAM IS WORKING!")
            print(f"Use this URL: {success_url}")
            print(f"\nYou can now run the enhanced IP camera system!")
        else:
            print(f"\n⚠️ URLs respond but OpenCV cannot capture")
            print(f"Check video format compatibility")
    else:
        print(f"\n❌ NO WORKING URLS FOUND")
        print(f"\nTroubleshooting steps:")
        print(f"1. Check DroidCam app shows green 'Ready' status")
        print(f"2. Verify camera preview is visible in app") 
        print(f"3. Try restarting DroidCam app completely")
        print(f"4. Check IP address in DroidCam matches 192.168.13.37")
        print(f"5. Test in browser: http://192.168.13.37:4747/video")

if __name__ == "__main__":
    main()
