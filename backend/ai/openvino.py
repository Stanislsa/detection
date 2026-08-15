"""
OpenVINO detector implementation for Intel hardware optimization.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.core.exceptions import DetectionException
from .base import BaseDetector

logger = get_logger(__name__)


class OpenVINODetector(BaseDetector):
    """OpenVINO detector for Intel CPU/GPU/NPU optimization."""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "AUTO",
        precision: str = "FP16",
        confidence_threshold: float = 0.5
    ):
        """
        Initialize OpenVINO detector.
        
        Args:
            model_path: Path to OpenVINO model directory
            device: Device (AUTO, CPU, GPU, NPU)
            precision: Model precision (FP32, FP16, INT8)
            confidence_threshold: Detection confidence threshold
        """
        self.precision = precision or settings.OPENVINO_PRECISION
        self.device = device or settings.OPENVINO_DEVICE
        self.confidence_threshold = confidence_threshold or settings.YOLO_CONFIDENCE_THRESHOLD
        
        if model_path is None:
            model_path = settings.MODELS_DIR / "openvino"
        
        super().__init__(str(model_path), self.device)
    
    def _load_model(self):
        """Load OpenVINO model."""
        try:
            from openvino.runtime import Core
            
            self.core = Core()
            
            # Find model files
            model_dir = Path(self.model_path)
            xml_path = model_dir / "model.xml"
            bin_path = model_dir / "model.bin"
            
            if not xml_path.exists():
                logger.warning(f"OpenVINO model not found at {xml_path}")
                self.model = None
                return
            
            # Read model
            self.model = self.core.read_model(model=xml_path, weights=bin_path)
            
            # Compile model
            self.compiled_model = self.core.compile_model(
                model=self.model,
                device_name=self.device
            )
            
            # Get input/output
            self.input_layer = self.compiled_model.input(0)
            self.output_layer = self.compiled_model.output(0)
            
            logger.info(f"OpenVINO model loaded on {self.device}")
            
        except ImportError:
            raise DetectionException("openvino package not installed")
        except Exception as e:
            raise DetectionException(f"Failed to load OpenVINO model: {e}")
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for OpenVINO.
        
        Args:
            image: Input image
        
        Returns:
            Preprocessed image
        """
        if not self.is_loaded():
            return image
        
        # Resize to model input size
        input_shape = self.input_layer.shape
        target_height, target_width = input_shape[2], input_shape[3]
        
        import cv2
        resized = cv2.resize(image, (target_width, target_height))
        
        # Normalize and transpose
        if len(resized.shape) == 3:
            resized = resized.transpose(2, 0, 1)
        
        # Add batch dimension
        resized = np.expand_dims(resized, axis=0)
        
        return resized.astype(np.float32)
    
    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Perform OpenVINO detection on image.
        
        Args:
            image: Input image as numpy array
        
        Returns:
            List of detection results
        """
        if not self.is_loaded():
            raise DetectionException("Model not loaded")
        
        try:
            # Preprocess
            processed = self.preprocess(image)
            
            # Run inference
            result = self.compiled_model([processed])[self.output_layer]
            
            # Postprocess
            detections = self.postprocess(result)
            
            return detections
            
        except Exception as e:
            logger.error(f"OpenVINO detection failed: {e}")
            return []
    
    def postprocess(self, raw_output: Any) -> List[Dict[str, Any]]:
        """
        Postprocess OpenVINO results.
        
        Args:
            raw_output: Raw model output
        
        Returns:
            List of detection results
        """
        detections = []
        
        # OpenVINO output format varies by model
        # This is a generic implementation for YOLO-like models
        try:
            output = raw_output[0]
            
            # Filter by confidence
            if len(output.shape) == 3:
                # Format: [batch, detections, 6] (x1, y1, x2, y2, confidence, class)
                for detection in output[0]:
                    if detection[4] > self.confidence_threshold:
                        detections.append({
                            "bbox": detection[:4].tolist(),
                            "confidence": float(detection[4]),
                            "class_id": int(detection[5]),
                            "class_name": f"class_{int(detection[5])}",
                            "detection_method": "openvino"
                        })
            
        except Exception as e:
            logger.error(f"OpenVINO postprocessing failed: {e}")
        
        return detections
