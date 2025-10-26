#!/usr/bin/env python3
"""
Synthetic IP Camera Demo for Enhanced Webcam Streaming
Built with ArchE's ResonantiA Protocol v3.1-CA

Demonstrates the webcam streaming system with synthetic video when IP camera is unavailable.
"""

import cv2
import numpy as np
import time
from datetime import datetime
import threading

def create_synthetic_frame(width=1280, height=720, frame_count=0):
    """Create a synthetic video frame with animations"""
    # Create base frame
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add gradient background
    for y in range(height):
        intensity = int(255 * (y / height))
        frame[y, :] = [intensity // 3, intensity // 2, intensity]
    
    # Add moving circle
    center_x = int(width // 2 + 200 * np.sin(frame_count * 0.05))
    center_y = int(height // 2 + 100 * np.cos(frame_count * 0.03))
    cv2.circle(frame, (center_x, center_y), 50, (0, 255, 255), -1)
    
    # Add text overlay
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, f"IP Camera Demo | {timestamp}", 
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.putText(frame, "🔴 LIVE STREAMING", 
               (width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    cv2.putText(frame, f"Frame: {frame_count}", 
               (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Add connection status
    cv2.putText(frame, "IP: 192.168.13.37:6969 (DEMO MODE)", 
               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return frame

def main():
    """Run synthetic IP camera demo"""
    print("🚀 SYNTHETIC IP CAMERA STREAMING DEMO")
    print("Built with ArchE's ResonantiA Protocol v3.1-CA")
    print("=" * 50)
    print()
    print("Simulating IP camera at: 192.168.13.37:6969")
    print("Features demonstrated:")
    print("  ✅ Video processing pipeline")
    print("  ✅ Real-time frame generation")
    print("  ✅ Timestamp overlays")
    print("  ✅ Live streaming indicators")
    print("  ✅ Performance metrics")
    print()
    print("Press 'q' to quit")
    print()
    
    frame_count = 0
    fps_counter = 0
    start_time = time.time()
    last_fps_time = time.time()
    
    try:
        while True:
            # Generate synthetic frame
            frame = create_synthetic_frame(frame_count=frame_count)
            
            # Display frame
            cv2.imshow("Enhanced IP Camera Streaming Demo", frame)
            
            # Calculate FPS
            fps_counter += 1
            current_time = time.time()
            
            if current_time - last_fps_time >= 3.0:  # Update every 3 seconds
                fps = fps_counter / (current_time - last_fps_time)
                print(f"📊 Demo FPS: {fps:.1f} | Frames: {frame_count} | Runtime: {current_time - start_time:.1f}s")
                fps_counter = 0
                last_fps_time = current_time
            
            frame_count += 1
            
            # Control frame rate (30 FPS)
            time.sleep(1/30)
            
            # Check for exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo error: {e}")
    finally:
        cv2.destroyAllWindows()
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time if total_time > 0 else 0
        print(f"\n📊 Final Stats:")
        print(f"   Total Frames: {frame_count}")
        print(f"   Runtime: {total_time:.1f}s")
        print(f"   Average FPS: {avg_fps:.1f}")
        print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()
