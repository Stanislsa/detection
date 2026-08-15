"""
YOLO detector implementation using Ultralytics.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.core.exceptions import DetectionException
from .base import BaseDetector

logger = get_logger(__name__)


class YOLODetector(BaseDetector):
    """YOLO detector using Ultralytics library."""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "auto",
        confidence_threshold: float = 0.5,
        nms_threshold: float = 0.45,
        frame_skip: int = 3
    ):
        """
        Initialize YOLO detector.
        
        Args:
            model_path: Path to YOLO model file
            device: Device to run inference on
            confidence_threshold: Detection confidence threshold
            nms_threshold: Non-maximum suppression threshold
            frame_skip: Skip frames for performance
        """
        if model_path is None:
            model_path = settings.YOLO_MODEL
        
        self.confidence_threshold = confidence_threshold or settings.YOLO_CONFIDENCE_THRESHOLD
        self.nms_threshold = nms_threshold or settings.YOLO_NMS_THRESHOLD
        self.frame_skip = frame_skip or settings.YOLO_FRAME_SKIP
        
        self.frame_count = 0
        
        super().__init__(model_path, device)
    
    def _load_model(self):
        """Load YOLO model."""
        try:
            from ultralytics import YOLO
            
            # Check if model path exists, otherwise download
            model_path = self.model_path
            if not Path(model_path).exists():
                logger.info(f"YOLO model not found at {model_path}, will download")
            
            self.model = YOLO(model_path)
            
            # Set device
            if self.device != "auto":
                self.model.to(self.device)
            
            logger.info(f"YOLO model loaded: {model_path}")
            
        except ImportError:
            raise DetectionException("ultralytics package not installed")
        except Exception as e:
            raise DetectionException(f"Failed to load YOLO model: {e}")
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for YOLO detection.
        
        Args:
            image: Input image
        
        Returns:
            Preprocessed image
        """
        # YOLO handles preprocessing internally
        return image
    
    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Perform YOLO detection on image.
        
        Args:
            image: Input image as numpy array
        
        Returns:
            List of detection results
        """
        if not self.is_loaded():
            raise DetectionException("Model not loaded")
        
        # Frame skipping for performance
        self.frame_count += 1
        if self.frame_count % self.frame_skip != 0:
            return []
        
        try:
            # Run inference
            results = self.model(
                image,
                conf=self.confidence_threshold,
                iou=self.nms_threshold,
                verbose=False
            )
            
            # Postprocess results
            detections = self.postprocess(results)
            
            return detections
            
        except Exception as e:
            logger.error(f"YOLO detection failed: {e}")
            return []
    
    def postprocess(self, raw_output: Any) -> List[Dict[str, Any]]:
        """
        Postprocess YOLO results.
        
        Args:
            raw_output: Raw YOLO results
        
        Returns:
            List of detection results
        """
        detections = []
        
        for result in raw_output:
            boxes = result.boxes
            
            if boxes is None:
                continue
            
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Get confidence and class
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                class_name = self.model.names.get(class_id, f"class_{class_id}")
                
                detection = {
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": confidence,
                    "class_id": class_id,
                    "class_name": class_name,
                    "detection_method": "yolo"
                }
                
                detections.append(detection)
        
        return detections


class YOLOPersonDetector(YOLODetector):
    """YOLO detector specialized for person detection only."""
    
    PERSON_CLASS_ID = 0  # COCO dataset person class ID
    
    def __init__(self, **kwargs):
        """Initialize YOLO person detector."""
        super().__init__(**kwargs)
    
    def postprocess(self, raw_output: Any) -> List[Dict[str, Any]]:
        """
        Postprocess YOLO results, filter for persons only.
        
        Args:
            raw_output: Raw YOLO results
        
        Returns:
            List of person detection results
        """
        all_detections = super().postprocess(raw_output)
        
        # Filter for person class only
        person_detections = [
            det for det in all_detections
            if det["class_id"] == self.PERSON_CLASS_ID
        ]
        
        return person_detections
