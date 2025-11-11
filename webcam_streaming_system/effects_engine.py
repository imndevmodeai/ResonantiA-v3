import cv2
import numpy as np

# Make mediapipe optional with graceful fallback
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None

class EffectsEngine:
    def __init__(self):
        """
        Initializes the AI Effects Engine.
        """
        if not MEDIAPIPE_AVAILABLE:
            self.mp_selfie_segmentation = None
            self.selfie_segmentation = None
            print("Effects Engine Initialized (mediapipe not available - background blur disabled).")
        else:
            self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
            self.selfie_segmentation = self.mp_selfie_segmentation.SelfieSegmentation(model_selection=0)
            print("Effects Engine Initialized.")

    def apply_background_blur(self, frame: np.ndarray, blur_intensity: int = 25) -> np.ndarray:
        """
        Applies a blur effect to the background of the frame.
        Falls back to simple blur if mediapipe is not available.
        """
        if not MEDIAPIPE_AVAILABLE or self.selfie_segmentation is None:
            # Fallback: apply simple blur to entire frame
            return cv2.GaussianBlur(frame, (blur_intensity, blur_intensity), 0)
        
        # Convert the BGR image to RGB.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and get the segmentation mask.
        results = self.selfie_segmentation.process(rgb_frame)
        mask = results.segmentation_mask
        
        # Create a condition where the mask is greater than a threshold.
        condition = np.stack((mask,) * 3, axis=-1) > 0.6
        
        # Create a blurred version of the background.
        blurred_background = cv2.GaussianBlur(frame, (blur_intensity, blur_intensity), 0)
        
        # Combine the foreground (person) with the blurred background.
        output_frame = np.where(condition, frame, blurred_background)
        
        return output_frame

    def apply_face_beauty(self, frame: np.ndarray, strength: float = 0.7) -> np.ndarray:
        """
        Applies a simple 'beauty' filter to the frame.
        This is a basic skin smoothing effect.
        """
        # A simple bilateral filter for skin smoothing.
        # It preserves edges while reducing noise.
        beauty_frame = cv2.bilateralFilter(frame, d=9, sigmaColor=75, sigmaSpace=75)
        
        # Blend the original frame with the smoothed frame
        output_frame = cv2.addWeighted(frame, 1 - strength, beauty_frame, strength, 0)

        return output_frame

    def close(self):
        """
        Cleans up resources used by the effects engine.
        """
        if self.selfie_segmentation is not None:
            self.selfie_segmentation.close()
        print("Effects Engine resources released.")
