"""
Pose Detector

Reference: docs/scientific_engine/07_FallDetectionLogic.md
Google Research - MediaPipe Pose (2020) - DOI: 10.1145/3383090
"""

import cv2
import mediapipe as mp
from typing import Tuple, List, Optional
import numpy as np


class MediaPipePoseDetector:
    """
    Detects human pose landmarks using MediaPipe Pose.
    
    Reference: Google Research - MediaPipe Pose (2020)
    DOI: 10.1145/3383090
    """
    
    def __init__(self, model_complexity: int = 1, min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Initialize the pose detector.
        
        Args:
            model_complexity: Model complexity (0, 1, or 2)
            min_detection_confidence: Minimum confidence for detection
            min_tracking_confidence: Minimum confidence for tracking
        """
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def detect(self, frame: np.ndarray) -> Optional[dict]:
        """
        Detect pose landmarks in a frame.
        
        Args:
            frame: Input frame (BGR format)
        
        Returns:
            Dictionary containing landmarks and confidence, or None if no detection
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks is None:
            return None
        
        # Extract landmarks
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            })
        
        return {
            'landmarks': landmarks,
            'confidence': results.pose_landmarks.visibility
        }
    
    def get_landmark(self, landmarks: List[dict], landmark_id: int) -> Optional[Tuple[float, float, float]]:
        """
        Get a specific landmark by ID.
        
        Args:
            landmarks: List of landmark dictionaries
            landmark_id: MediaPipe landmark ID (0-32)
        
        Returns:
            Tuple of (x, y, z) coordinates or None if not found
        """
        if landmark_id < 0 or landmark_id >= len(landmarks):
            return None
        
        landmark = landmarks[landmark_id]
        return (landmark['x'], landmark['y'], landmark['z'])
    
    def draw_landmarks(self, frame: np.ndarray, landmarks: List[dict]) -> np.ndarray:
        """
        Draw landmarks on the frame.
        
        Args:
            frame: Input frame
            landmarks: List of landmark dictionaries
        
        Returns:
            Frame with landmarks drawn
        """
        # Convert landmarks to MediaPipe format
        mp_landmarks = self.mp_pose.PoseLandmark
        pose_landmarks = self.mp_pose.Pose()
        
        for i, landmark in enumerate(landmarks):
            pose_landmarks.landmark[i].x = landmark['x']
            pose_landmarks.landmark[i].y = landmark['y']
            pose_landmarks.landmark[i].z = landmark['z']
            pose_landmarks.landmark[i].visibility = landmark['visibility']
        
        # Draw landmarks
        self.mp_drawing.draw_landmarks(
            frame, pose_landmarks, self.mp_pose.POSE_CONNECTIONS
        )
        
        return frame
    
    def release(self):
        """Release resources."""
        self.pose.close()


def extract_33_points(frame: np.ndarray, detector: MediaPipePoseDetector) -> Optional[List[Tuple[float, float, float]]]:
    """
    Extract 33 MediaPipe pose points from a frame.
    
    Reference: Google Research - MediaPipe Pose (2020)
    DOI: 10.1145/3383090
    
    Args:
        frame: Input frame
        detector: MediaPipePoseDetector instance
    
    Returns:
        List of 33 (x, y, z) tuples or None if no detection
    """
    result = detector.detect(frame)
    
    if result is None:
        return None
    
    landmarks = result['landmarks']
    points = []
    
    for landmark in landmarks:
        points.append((landmark['x'], landmark['y'], landmark['z']))
    
    return points
