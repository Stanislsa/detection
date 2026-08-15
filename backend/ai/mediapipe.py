"""
MediaPipe pose and fall detector implementation.
"""

import numpy as np
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.core.exceptions import DetectionException
from backend.core.constants import GRAVITY
from .base import BaseDetector

logger = get_logger(__name__)


class MediaPipePoseDetector(BaseDetector):
    """MediaPipe pose detector for human pose estimation."""
    
    def __init__(
        self,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        static_image_mode: bool = False
    ):
        """
        Initialize MediaPipe pose detector.
        
        Args:
            model_complexity: Model complexity (0, 1, 2)
            min_detection_confidence: Minimum detection confidence
            min_tracking_confidence: Minimum tracking confidence
            static_image_mode: Whether to treat input as static image
        """
        self.model_complexity = model_complexity or settings.MEDIAPIPE_MODEL_COMPLEXITY
        self.min_detection_confidence = min_detection_confidence or settings.MEDIAPIPE_MIN_DETECTION_CONFIDENCE
        self.min_tracking_confidence = min_tracking_confidence or settings.MEDIAPIPE_MIN_TRACKING_CONFIDENCE
        self.static_image_mode = static_image_mode
        
        super().__init__(None, "cpu")
    
    def _load_model(self):
        """Load MediaPipe pose model."""
        try:
            import mediapipe as mp
            
            self.mp_pose = mp.solutions.pose
            self.model = self.mp_pose.Pose(
                static_image_mode=self.static_image_mode,
                model_complexity=self.model_complexity,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
            
            logger.info("MediaPipe pose model loaded")
            
        except ImportError:
            raise DetectionException("mediapipe package not installed")
        except Exception as e:
            raise DetectionException(f"Failed to load MediaPipe model: {e}")
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for MediaPipe.
        
        Args:
            image: Input image
        
        Returns:
            Preprocessed image
        """
        # Convert BGR to RGB for MediaPipe
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    
    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Perform pose detection on image.
        
        Args:
            image: Input image as numpy array
        
        Returns:
            List of pose landmarks
        """
        if not self.is_loaded():
            raise DetectionException("Model not loaded")
        
        try:
            # Preprocess
            processed_image = self.preprocess(image)
            
            # Run pose detection
            results = self.model.process(processed_image)
            
            # Postprocess
            poses = self.postprocess(results)
            
            return poses
            
        except Exception as e:
            logger.error(f"MediaPipe detection failed: {e}")
            return []
    
    def postprocess(self, raw_output: Any) -> List[Dict[str, Any]]:
        """
        Postprocess MediaPipe results.
        
        Args:
            raw_output: Raw MediaPipe results
        
        Returns:
            List of pose landmarks
        """
        poses = []
        
        if raw_output.pose_landmarks:
            landmarks = []
            for idx, landmark in enumerate(raw_output.pose_landmarks.landmark):
                landmarks.append({
                    "id": idx,
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility
                })
            
            poses.append({
                "landmarks": landmarks,
                "detection_method": "mediapipe"
            })
        
        return poses


class MediaPipeFallDetector(MediaPipePoseDetector):
    """
    Fall detector using MediaPipe pose landmarks.
    
    Analyzes body orientation, velocity, and position to detect falls.
    """
    
    def __init__(self, **kwargs):
        """Initialize MediaPipe fall detector."""
        self.previous_landmarks = None
        self.previous_timestamp = None
        self.fall_confidence = 0.0
        
        super().__init__(**kwargs)
    
    def detect_fall(
        self,
        image: np.ndarray,
        person_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Detect fall using pose analysis.
        
        Args:
            image: Input image
            person_profile: Person profile for adaptive thresholds
        
        Returns:
            Fall detection result with confidence
        """
        # Get pose landmarks
        poses = self.detect(image)
        
        if not poses:
            return {
                "fall_detected": False,
                "confidence": 0.0,
                "method": "mediapipe"
            }
        
        landmarks = poses[0]["landmarks"]
        
        # Calculate fall indicators
        trunk_angle = self._calculate_trunk_angle(landmarks)
        is_horizontal = self._is_body_horizontal(landmarks)
        head_position = self._get_head_position(landmarks)
        
        # Calculate velocity if previous landmarks available
        vertical_velocity = 0.0
        if self.previous_landmarks and self.previous_timestamp:
            vertical_velocity = self._calculate_vertical_velocity(
                landmarks,
                self.previous_landmarks,
                datetime.utcnow() - self.previous_timestamp
            )
        
        # Update previous state
        self.previous_landmarks = landmarks
        self.previous_timestamp = datetime.utcnow()
        
        # Calculate fall confidence
        fall_confidence = self._calculate_fall_confidence(
            trunk_angle,
            is_horizontal,
            head_position,
            vertical_velocity,
            person_profile
        )
        
        # Determine if fall detected
        threshold = person_profile.get("velocity_threshold", -2.5) if person_profile else -2.5
        fall_detected = fall_confidence > 0.75 or vertical_velocity < threshold
        
        return {
            "fall_detected": fall_detected,
            "confidence": fall_confidence,
            "trunk_angle": trunk_angle,
            "is_horizontal": is_horizontal,
            "vertical_velocity": vertical_velocity,
            "method": "mediapipe"
        }
    
    def _calculate_trunk_angle(self, landmarks: List[Dict]) -> float:
        """
        Calculate trunk angle relative to vertical.
        
        Args:
            landmarks: Pose landmarks
        
        Returns:
            Trunk angle in degrees
        """
        try:
            # Get shoulder and hip landmarks
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            
            # Calculate midpoints
            shoulder_mid = {
                "x": (left_shoulder["x"] + right_shoulder["x"]) / 2,
                "y": (left_shoulder["y"] + right_shoulder["y"]) / 2
            }
            hip_mid = {
                "x": (left_hip["x"] + right_hip["x"]) / 2,
                "y": (left_hip["y"] + right_hip["y"]) / 2
            }
            
            # Calculate angle from vertical
            dx = shoulder_mid["x"] - hip_mid["x"]
            dy = shoulder_mid["y"] - hip_mid["y"]
            
            angle = math.degrees(math.atan2(abs(dx), abs(dy)))
            
            return angle
            
        except Exception as e:
            logger.error(f"Failed to calculate trunk angle: {e}")
            return 0.0
    
    def _is_body_horizontal(self, landmarks: List[Dict]) -> bool:
        """
        Check if body is in horizontal position.
        
        Args:
            landmarks: Pose landmarks
        
        Returns:
            True if body is horizontal
        """
        try:
            trunk_angle = self._calculate_trunk_angle(landmarks)
            return trunk_angle > 60.0  # Threshold for horizontal
        except:
            return False
    
    def _get_head_position(self, landmarks: List[Dict]) -> Dict[str, float]:
        """
        Get head position relative to body.
        
        Args:
            landmarks: Pose landmarks
        
        Returns:
            Head position dict
        """
        try:
            nose = landmarks[0]
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            
            shoulder_mid_y = (left_shoulder["y"] + right_shoulder["y"]) / 2
            
            return {
                "x": nose["x"],
                "y": nose["y"],
                "below_shoulders": nose["y"] > shoulder_mid_y
            }
        except:
            return {"x": 0.0, "y": 0.0, "below_shoulders": False}
    
    def _calculate_vertical_velocity(
        self,
        current_landmarks: List[Dict],
        previous_landmarks: List[Dict],
        time_delta
    ) -> float:
        """
        Calculate vertical velocity of head.
        
        Args:
            current_landmarks: Current pose landmarks
            previous_landmarks: Previous pose landmarks
            time_delta: Time between frames
        
        Returns:
            Vertical velocity in m/s
        """
        try:
            current_head = current_landmarks[0]
            previous_head = previous_landmarks[0]
            
            # Calculate vertical displacement (normalized to meters)
            dy = (current_head["y"] - previous_head["y"]) * 2.0  # Approximate scale
            
            # Calculate velocity
            dt = time_delta.total_seconds()
            if dt > 0:
                velocity = dy / dt
                return velocity
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate vertical velocity: {e}")
            return 0.0
    
    def _calculate_fall_confidence(
        self,
        trunk_angle: float,
        is_horizontal: bool,
        head_position: Dict,
        vertical_velocity: float,
        person_profile: Optional[Dict] = None
    ) -> float:
        """
        Calculate overall fall confidence.
        
        Args:
            trunk_angle: Trunk angle
            is_horizontal: Whether body is horizontal
            head_position: Head position
            vertical_velocity: Vertical velocity
            person_profile: Person profile for adaptive weights
        
        Returns:
            Fall confidence (0-1)
        """
        # Get profile-specific weights
        if person_profile:
            weights = person_profile.get("gravity_time_weights", {})
            angle_threshold = person_profile.get("angle_threshold", 60.0)
        else:
            weights = {
                "intensity": 0.30,
                "time_on_ground": 0.35,
                "injury_probability": 0.15,
                "reactivity": 0.20
            }
            angle_threshold = 60.0
        
        # Calculate individual scores
        angle_score = min(trunk_angle / angle_threshold, 1.0)
        horizontal_score = 1.0 if is_horizontal else 0.0
        velocity_score = min(abs(vertical_velocity) / 3.0, 1.0)  # Normalize to 3 m/s
        head_score = 1.0 if head_position.get("below_shoulders", False) else 0.5
        
        # Weighted combination
        confidence = (
            weights.get("intensity", 0.3) * velocity_score +
            weights.get("reactivity", 0.2) * angle_score +
            weights.get("time_on_ground", 0.35) * horizontal_score +
            weights.get("injury_probability", 0.15) * head_score
        )
        
        return min(confidence, 1.0)
