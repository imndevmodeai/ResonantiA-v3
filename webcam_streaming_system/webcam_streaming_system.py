import cv2
import numpy as np
import json
import time
from pathlib import Path
import pyvirtualcam
import threading
import logging

from .effects_engine import EffectsEngine
from .rtmp_streamer import RTMPStreamer
from .droidcam_manager import DroidCamManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebcamStreamingSystem:
    def __init__(self, config=None):
        logger.info("Initializing ArchE Webcam Streaming System...")
        
        # --- Load Configuration ---
        self.config = config or self.load_config()

        # --- Initialize Managers ---
        self.effects_engine = EffectsEngine()
        self.rtmp_streamer = RTMPStreamer()
        self.droidcam_manager = DroidCamManager()

        # --- System State ---
        self.cap = None
        self.vcam = None
        self.running = False
        self.main_thread = None

    def load_config(self):
        """
        Loads the streaming configuration from a JSON file.
        """
        config_file = Path('streaming_config.json')
        if not config_file.exists():
            print(f"Warning: Config file not found at streaming_config.json. Using default settings.")
            return self.get_default_config()
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Could not decode JSON from config file. Using default settings.")
            return {}

    def get_default_config(self) -> dict:
        """
        Provides a default configuration if the JSON file is missing.
        """
        return {
            "camera_device": 0,
            "resolution": {"width": 640, "height": 480},
            "fps": 30,
            "virtual_cam_device_number": 10,
            "effects": {
                "background_blur": False,
                "face_beauty": False
            },
            "platforms": {},
            "droidcam_settings": {
                "ip": "192.168.1.100",
                "port": "4747",
                "auto_connect": False
            }
        }

    def start(self):
        """
        The main loop for the streaming system.
        """
        logger.info("Starting ArchE Webcam Streaming System...")
        
        # Initialize camera
        self.cap = cv2.VideoCapture(self.config.get('camera_device', 0))
        if not self.cap.isOpened():
            logger.error(f"Failed to open camera device {self.config.get('camera_device', 0)}")
            return False
        
        # Set camera properties
        resolution = self.config.get('resolution', {'width': 640, 'height': 480})
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution['width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution['height'])
        self.cap.set(cv2.CAP_PROP_FPS, self.config.get('fps', 30))
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))

        logger.info(f"Camera initialized: {width}x{height} @ {fps}fps")

        # Start RTMP streams for enabled platforms
        for platform, settings in self.config.get('platforms', {}).items():
            if settings.get('enabled', False):
                self.rtmp_streamer.start_stream(platform, settings['rtmp_url'], settings['stream_key'])

        try:
            # --- Virtual Camera Initialization ---
            self.vcam = pyvirtualcam.Camera(width=width,
                                            height=height,
                                            fps=fps,
                                            device=f"/dev/video{self.config.get('virtual_cam_device_number', 10)}")
            logger.info(f"Virtual camera '{self.vcam.device}' started.")

            self.running = True
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to grab frame from camera")
                    continue

                # Convert to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # --- Apply effects ---
                effects = self.config.get('effects', {})
                if effects.get('background_blur', False):
                    frame_rgb = self.effects_engine.apply_background_blur(frame_rgb)
                
                if effects.get('face_beauty', False):
                    frame_rgb = self.effects_engine.apply_face_beauty(frame_rgb)

                # --- Send to virtual camera ---
                if self.vcam:
                    self.vcam.send(frame_rgb)

                # --- Send to RTMP streams ---
                self.rtmp_streamer.send_frame(frame_rgb)

        except Exception as e:
            logger.error(f"An error occurred in the main loop: {e}")
        finally:
            self.stop()
        
        logger.info("Streaming system has shut down.")
        return True

    def stop(self):
        """
        Stops the main streaming loop gracefully.
        """
        if not self.running:
            return
            
        logger.info("Stopping streaming system...")
        self.running = False
        
        # Stop streamers
        self.rtmp_streamer.stop_all_streams()

        # Release camera
        if self.cap and self.cap.isOpened():
            self.cap.release()
            logger.info("Physical camera released.")
        
        # Release virtual camera
        if self.vcam:
            self.vcam.close()
            logger.info("Virtual camera released.")
        
        logger.info("Streaming system has shut down.")

def main():
    """
    Main function to run the streaming system.
    """
    print("Initializing ArchE Webcam Streaming System...")
    system = WebcamStreamingSystem()
    system.start()

if __name__ == "__main__":
    main()
