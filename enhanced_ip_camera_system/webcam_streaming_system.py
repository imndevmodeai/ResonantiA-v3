#!/usr/bin/env python3
"""
Enhanced Webcam Streaming Platform Integration with IP Camera Support
Built with ArchE's ResonantiA Protocol v3.1-CA

Integrates IP camera streams with webcam streaming platforms like Chaturbate, OnlyFans, etc.
Uses camera_config.json for IP camera configuration.

Author: ArchE (ResonantiA Protocol v3.1-CA)
"""

import cv2
import numpy as np
import json
import time
import threading
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import signal
import sys

# Optional imports with graceful fallback
try:
    import pyvirtualcam
    PYVIRTUALCAM_AVAILABLE = True
except ImportError:
    PYVIRTUALCAM_AVAILABLE = False
    print("⚠️  pyvirtualcam not available - virtual camera features disabled")

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️  MediaPipe not available - advanced AI features disabled")

@dataclass
class IPCameraConfig:
    """Configuration for IP camera source"""
    camera_id: str
    name: str
    url: str
    location: str
    protocol: str
    resolution: str
    fps: int
    enabled: bool
    ai_enabled: bool
    recording_enabled: bool
    fallback_urls: Optional[List[str]] = None
    fallback_urls: List[str] = None

@dataclass
class StreamConfig:
    """Configuration for streaming settings"""
    platform: str
    stream_key: str
    rtmp_url: str
    resolution: Tuple[int, int]
    fps: int
    bitrate: int
    enabled: bool

@dataclass
class PlatformConfig:
    """Platform-specific streaming configuration"""
    chaturbate: StreamConfig
    onlyfans: StreamConfig
    obs_studio: StreamConfig
    custom_rtmp: StreamConfig

class VideoProcessor:
    """Advanced video processing with AI effects"""
    
    def __init__(self):
        self.mp_face_detection = None
        self.mp_selfie_segmentation = None
        
        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_face_detection = mp.solutions.face_detection.FaceDetection(
                    model_selection=0, min_detection_confidence=0.5)
                self.mp_selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(
                    model_selection=1)
                logging.info("✅ MediaPipe AI processing initialized")
            except Exception as e:
                logging.warning(f"MediaPipe initialization failed: {e}")
    
    def apply_beauty_filter(self, frame: np.ndarray, intensity: float = 0.3) -> np.ndarray:
        """Apply beauty filter with skin smoothing"""
        if frame is None:
            return frame
            
        # Bilateral filter for skin smoothing
        smooth = cv2.bilateralFilter(frame, 15, 80, 80)
        
        # Blend original and smoothed
        result = cv2.addWeighted(frame, 1 - intensity, smooth, intensity, 0)
        
        # Enhance brightness slightly
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = cv2.add(hsv[:, :, 2], 10)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return result
    
    def apply_background_blur(self, frame: np.ndarray, blur_strength: int = 15) -> np.ndarray:
        """Apply background blur using MediaPipe segmentation"""
        if not MEDIAPIPE_AVAILABLE or self.mp_selfie_segmentation is None:
            return frame
            
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get segmentation mask
            results = self.mp_selfie_segmentation.process(rgb_frame)
            
            if results.segmentation_mask is not None:
                # Create blurred background
                blurred_bg = cv2.GaussianBlur(frame, (blur_strength, blur_strength), 0)
                
                # Apply mask
                mask = results.segmentation_mask
                mask_3d = np.dstack((mask, mask, mask))
                
                # Combine foreground and blurred background
                result = np.where(mask_3d > 0.5, frame, blurred_bg)
                return result.astype(np.uint8)
        except Exception as e:
            logging.warning(f"Background blur failed: {e}")
        
        return frame
    
    def enhance_lighting(self, frame: np.ndarray, gamma: float = 1.2) -> np.ndarray:
        """Enhance lighting with gamma correction"""
        if frame is None:
            return frame
            
        # Gamma correction
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(frame, table)
    
    def reduce_noise(self, frame: np.ndarray) -> np.ndarray:
        """Reduce video noise"""
        if frame is None:
            return frame
            
        return cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)

class IPCameraStreamManager:
    """Manages IP camera streams for webcam streaming platforms"""
    
    def __init__(self, config_path: str = "camera_config.json", streaming_config_path: str = "streaming_config.json"):
        self.config_path = config_path
        self.streaming_config_path = streaming_config_path
        self.cameras: List[IPCameraConfig] = []
        self.streaming_config: Optional[PlatformConfig] = None
        self.active_streams: Dict[str, cv2.VideoCapture] = {}
        self.processor = VideoProcessor()
        self.virtual_cam = None
        self.running = False
        
        # Performance metrics
        self.frame_count = 0
        self.start_time = time.time()
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Load configurations
        self.load_camera_config()
        self.load_streaming_config()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_camera_config(self):
        """Load IP camera configuration"""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                logging.error(f"Camera config file not found: {self.config_path}")
                return
                
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            self.cameras = []
            for cam_data in config_data.get('cameras', []):
                if cam_data.get('enabled', False):
                    camera_config = IPCameraConfig(**cam_data)
                    self.cameras.append(camera_config)
                    logging.info(f"✅ Loaded camera: {camera_config.name} ({camera_config.url})")
            
            logging.info(f"Loaded {len(self.cameras)} enabled IP cameras")
            
        except Exception as e:
            logging.error(f"Failed to load camera config: {e}")
    
    def load_streaming_config(self):
        """Load streaming platform configuration"""
        try:
            config_file = Path(self.streaming_config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Convert to StreamConfig objects
                platforms = {}
                for platform_name, platform_data in config_data.get('platforms', {}).items():
                    if platform_data.get('enabled', False):
                        platforms[platform_name] = StreamConfig(**platform_data)
                
                self.streaming_config = platforms
                logging.info(f"✅ Loaded streaming config for {len(platforms)} platforms")
            else:
                logging.warning(f"Streaming config not found: {self.streaming_config_path}")
                
        except Exception as e:
            logging.error(f"Failed to load streaming config: {e}")
    
    def connect_to_camera(self, camera: IPCameraConfig) -> Optional[cv2.VideoCapture]:
        """Connect to an IP camera with fallback URL support"""
        urls_to_try = [camera.url]
        
        # Add fallback URLs if available
        if hasattr(camera, 'fallback_urls') and camera.fallback_urls:
            urls_to_try.extend(camera.fallback_urls)
        
        for url in urls_to_try:
            try:
                logging.info(f"Attempting to connect to camera: {camera.name} at {url}")
                
                # Handle different URL types
                if url == "0" or url.isdigit():
                    # Local webcam
                    cap = cv2.VideoCapture(int(url))
                else:
                    # IP camera or video file
                    cap = cv2.VideoCapture(url)
                
                if not cap.isOpened():
                    logging.warning(f"Failed to open camera stream: {url}")
                    continue
                
                # Configure camera settings
                width, height = map(int, camera.resolution.split('x'))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                cap.set(cv2.CAP_PROP_FPS, camera.fps)
                
                # Set connection timeout for IP cameras
                if not url.isdigit():
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Test frame capture with timeout
                start_time = time.time()
                timeout = 10  # 10 second timeout
                
                while time.time() - start_time < timeout:
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        logging.info(f"✅ Successfully connected to camera: {camera.name} at {url}")
                        logging.info(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
                        return cap
                    time.sleep(0.1)
                
                logging.warning(f"Timeout reading from camera: {url}")
                cap.release()
                
            except Exception as e:
                logging.error(f"Error connecting to camera at {url}: {e}")
                if 'cap' in locals():
                    cap.release()
                continue
        
        logging.error(f"Failed to connect to camera: {camera.name} - all URLs exhausted")
        return None
    
    def setup_virtual_camera(self, width: int = 1280, height: int = 720, fps: int = 30):
        """Setup virtual camera for streaming"""
        if not PYVIRTUALCAM_AVAILABLE:
            logging.warning("Virtual camera not available - install pyvirtualcam")
            return False
        
        try:
            self.virtual_cam = pyvirtualcam.Camera(width=width, height=height, fps=fps)
            logging.info(f"✅ Virtual camera setup: {width}x{height}@{fps}fps")
            return True
        except Exception as e:
            logging.error(f"Failed to setup virtual camera: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray, camera: IPCameraConfig) -> np.ndarray:
        """Process frame with AI effects and enhancements"""
        if frame is None:
            return None
        
        try:
            # Apply beauty filter
            frame = self.processor.apply_beauty_filter(frame, intensity=0.3)
            
            # Apply background blur (if enabled)
            if camera.ai_enabled:
                frame = self.processor.apply_background_blur(frame, blur_strength=15)
            
            # Enhance lighting
            frame = self.processor.enhance_lighting(frame, gamma=1.1)
            
            # Add timestamp overlay
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, f"{camera.name} | {timestamp}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add streaming indicator
            cv2.putText(frame, "🔴 LIVE", 
                       (frame.shape[1] - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            return frame
            
        except Exception as e:
            logging.error(f"Frame processing error: {e}")
            return frame
    
    def calculate_fps(self):
        """Calculate and log FPS"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 5.0:  # Update every 5 seconds
            fps = self.fps_counter / (current_time - self.last_fps_time)
            logging.info(f"📊 Processing FPS: {fps:.1f}")
            self.fps_counter = 0
            self.last_fps_time = current_time
    
    def stream_camera(self, camera: IPCameraConfig):
        """Stream from a specific IP camera"""
        cap = self.connect_to_camera(camera)
        if not cap:
            return
        
        self.active_streams[camera.camera_id] = cap
        
        try:
            while self.running:
                ret, frame = cap.read()
                if not ret or frame is None:
                    logging.warning(f"No frame from camera: {camera.name}")
                    time.sleep(0.1)
                    continue
                
                # Process frame
                processed_frame = self.process_frame(frame, camera)
                if processed_frame is None:
                    continue
                
                # Send to virtual camera
                if self.virtual_cam and PYVIRTUALCAM_AVAILABLE:
                    try:
                        # Convert BGR to RGB for virtual camera
                        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                        self.virtual_cam.send(rgb_frame)
                        self.virtual_cam.sleep_until_next_frame()
                    except Exception as e:
                        logging.error(f"Virtual camera error: {e}")
                
                # Display preview window
                cv2.imshow(f"Stream: {camera.name}", processed_frame)
                
                # Calculate FPS
                self.calculate_fps()
                
                # Check for exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except Exception as e:
            logging.error(f"Streaming error for {camera.name}: {e}")
        finally:
            cap.release()
            if camera.camera_id in self.active_streams:
                del self.active_streams[camera.camera_id]
    
    def start_streaming(self):
        """Start streaming from all enabled IP cameras"""
        if not self.cameras:
            logging.error("No enabled cameras found in configuration")
            return
        
        print("🚀 ENHANCED IP CAMERA WEBCAM STREAMING PLATFORM")
        print("Built with ArchE's ResonantiA Protocol v3.1-CA")
        print("=" * 56)
        print()
        print("Features:")
        print("  ✅ IP Camera Integration")
        print("  ✅ Real-time video processing")
        print("  ✅ Beauty filters and effects")
        print("  ✅ Background blur")
        print("  ✅ Virtual camera support")
        print("  ✅ Streaming platform integration")
        print("  ✅ Performance optimized")
        print()
        
        if not PYVIRTUALCAM_AVAILABLE or not MEDIAPIPE_AVAILABLE:
            print("⚠️  Optional dependencies missing:")
            if not PYVIRTUALCAM_AVAILABLE:
                print("     pip install pyvirtualcam")
            if not MEDIAPIPE_AVAILABLE:
                print("     pip install mediapipe")
            print()
        
        logging.info("🚀 Starting Enhanced IP Camera Webcam Streaming System")
        
        # Use the first enabled camera for primary streaming
        primary_camera = self.cameras[0]
        logging.info(f"Primary camera: {primary_camera.name}")
        
        # Setup virtual camera
        width, height = map(int, primary_camera.resolution.split('x'))
        if self.setup_virtual_camera(width, height, primary_camera.fps):
            logging.info("✅ Virtual camera ready for streaming platforms")
        else:
            logging.warning("Virtual camera failed to start - continuing with preview only")
        
        self.running = True
        
        try:
            # Start streaming from primary camera
            self.stream_camera(primary_camera)
            
        except KeyboardInterrupt:
            logging.info("Streaming interrupted by user")
        except Exception as e:
            logging.error(f"Streaming error: {e}")
        finally:
            self.stop_streaming()
    
    def stop_streaming(self):
        """Stop all streaming"""
        logging.info("Stopping streaming system...")
        self.running = False
        
        # Release all camera streams
        for camera_id, cap in self.active_streams.items():
            try:
                cap.release()
                logging.info(f"Released camera: {camera_id}")
            except Exception as e:
                logging.error(f"Error releasing camera {camera_id}: {e}")
        
        self.active_streams.clear()
        
        # Close virtual camera
        if self.virtual_cam:
            try:
                self.virtual_cam.close()
                logging.info("Virtual camera closed")
            except Exception as e:
                logging.error(f"Error closing virtual camera: {e}")
        
        # Close all OpenCV windows
        cv2.destroyAllWindows()
        
        # Calculate final stats
        total_time = time.time() - self.start_time
        avg_fps = self.frame_count / total_time if total_time > 0 else 0
        logging.info(f"📊 Final stats: {self.frame_count} frames in {total_time:.1f}s (avg {avg_fps:.1f} FPS)")
        
        logging.info("Streaming system stopped")
    
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        logging.info(f"Received signal {signum}, shutting down...")
        self.stop_streaming()
        sys.exit(0)

def main():
    """Main entry point"""
    try:
        # Create and start the streaming system
        streamer = IPCameraStreamManager()
        streamer.start_streaming()
        
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
