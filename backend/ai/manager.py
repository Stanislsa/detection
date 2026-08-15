"""
AI Manager - Unified management of all AI detection and classification models.
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.core.exceptions import DetectionException
from .yolo import YOLODetector, YOLOPersonDetector
from .mediapipe import MediaPipePoseDetector, MediaPipeFallDetector
from .openvino import OpenVINODetector
from .classifier import ImageClassifier, SceneClassifier
from .scientific import ScientificEngine

logger = get_logger(__name__)


class AIManager:
    """
    Unified AI manager for all detection and classification models.
    
    Manages model lifecycle, inference orchestration, and result aggregation.
    """
    
    def __init__(self):
        """Initialize AI manager."""
        self.detectors: Dict[str, Any] = {}
        self.classifiers: Dict[str, Any] = {}
        self.scientific_engine = ScientificEngine()
        
        self._initialize_models()
        logger.info("AI manager initialized")
    
    def _initialize_models(self):
        """Initialize all configured AI models."""
        try:
            # Initialize YOLO detector
            if settings.YOLO_MODEL:
                self.detectors["yolo"] = YOLODetector(
                    model_path=settings.YOLO_MODEL,
                    device=settings.AI_DEVICE
                )
                logger.info("YOLO detector initialized")
            
            # Initialize YOLO person detector
            if settings.YOLO_MODEL:
                self.detectors["yolo_person"] = YOLOPersonDetector(
                    model_path=settings.YOLO_MODEL,
                    device=settings.AI_DEVICE
                )
                logger.info("YOLO person detector initialized")
            
            # Initialize MediaPipe pose detector
            if settings.MEDIAPIPE_MODEL_COMPLEXITY is not None:
                self.detectors["mediapipe_pose"] = MediaPipePoseDetector(
                    model_complexity=settings.MEDIAPIPE_MODEL_COMPLEXITY
                )
                logger.info("MediaPipe pose detector initialized")
            
            # Initialize MediaPipe fall detector
            if settings.MEDIAPIPE_MODEL_COMPLEXITY is not None:
                self.detectors["mediapipe_fall"] = MediaPipeFallDetector(
                    model_complexity=settings.MEDIAPIPE_MODEL_COMPLEXITY
                )
                logger.info("MediaPipe fall detector initialized")
            
            # Initialize OpenVINO detector if enabled
            if settings.OPENVINO_ENABLED:
                self.detectors["openvino"] = OpenVINODetector(
                    device=settings.OPENVINO_DEVICE,
                    precision=settings.OPENVINO_PRECISION
                )
                logger.info("OpenVINO detector initialized")
            
            # Initialize image classifier
            self.classifiers["image"] = ImageClassifier(device=settings.AI_DEVICE)
            logger.info("Image classifier initialized")
            
            # Initialize scene classifier
            self.classifiers["scene"] = SceneClassifier(device=settings.AI_DEVICE)
            logger.info("Scene classifier initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
    
    def detect_persons(self, image, method: str = "yolo_person") -> List[Dict[str, Any]]:
        """
        Detect persons in image.
        
        Args:
            image: Input image
            method: Detection method (yolo_person, mediapipe_pose)
        
        Returns:
            List of person detections
        """
        if method not in self.detectors:
            raise DetectionException(f"Detector not available: {method}")
        
        detector = self.detectors[method]
        return detector.detect(image)
    
    def detect_fall(
        self,
        image,
        person_profile: Optional[Dict] = None,
        method: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Detect fall using specified method.
        
        Args:
            image: Input image
            person_profile: Person profile for adaptive thresholds
            method: Detection method (mediapipe_fall, hybrid)
        
        Returns:
            Fall detection result
        """
        if method == "mediapipe_fall":
            if "mediapipe_fall" not in self.detectors:
                raise DetectionException("MediaPipe fall detector not available")
            
            detector = self.detectors["mediapipe_fall"]
            return detector.detect_fall(image, person_profile)
        
        elif method == "hybrid":
            return self._hybrid_fall_detection(image, person_profile)
        
        else:
            raise DetectionException(f"Unknown detection method: {method}")
    
    def _hybrid_fall_detection(
        self,
        image,
        person_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Hybrid fall detection combining multiple methods.
        
        Args:
            image: Input image
            person_profile: Person profile
        
        Returns:
            Combined fall detection result
        """
        results = {}
        
        # YOLO person detection
        if "yolo_person" in self.detectors:
            yolo_results = self.detectors["yolo_person"].detect(image)
            results["yolo"] = yolo_results
        
        # MediaPipe pose analysis
        if "mediapipe_fall" in self.detectors:
            mediapipe_results = self.detectors["mediapipe_fall"].detect_fall(image, person_profile)
            results["mediapipe"] = mediapipe_results
        
        # Scientific analysis if pose landmarks available
        if "mediapipe" in results and results["mediapipe"].get("fall_detected"):
            try:
                # Get pose landmarks
                pose_detector = self.detectors.get("mediapipe_pose")
                if pose_detector:
                    poses = pose_detector.detect(image)
                    if poses:
                        landmarks = poses[0]["landmarks"]
                        
                        # Run scientific analysis
                        scientific_results = self.scientific_engine.analyze_fall(
                            landmarks,
                            results["mediapipe"].get("vertical_velocity", 0.0),
                            person_profile
                        )
                        results["scientific"] = scientific_results
            except Exception as e:
                logger.error(f"Scientific analysis failed: {e}")
        
        # Combine results
        combined = self._combine_detection_results(results)
        
        return combined
    
    def _combine_detection_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine results from multiple detection methods.
        
        Args:
            results: Dictionary of results from different methods
        
        Returns:
            Combined result
        """
        combined = {
            "fall_detected": False,
            "confidence": 0.0,
            "methods_used": list(results.keys()),
            "method_results": results
        }
        
        # Weighted combination
        weights = {
            "mediapipe": 0.6,
            "yolo": 0.4
        }
        
        total_weight = 0.0
        weighted_confidence = 0.0
        
        for method, result in results.items():
            if method in weights:
                weight = weights[method]
                confidence = result.get("confidence", 0.0)
                
                weighted_confidence += weight * confidence
                total_weight += weight
        
        if total_weight > 0:
            combined["confidence"] = weighted_confidence / total_weight
        
        # Determine fall detection
        combined["fall_detected"] = combined["confidence"] > 0.75
        
        # Include scientific decision if available
        if "scientific" in results:
            combined["scientific_decision"] = results["scientific"].get("decision", {})
        
        return combined
    
    def classify_image(
        self,
        image,
        classifier: str = "image",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Classify image.
        
        Args:
            image: Input image
            classifier: Classifier to use (image, scene)
            top_k: Return top K predictions
        
        Returns:
            Classification results
        """
        if classifier not in self.classifiers:
            raise DetectionException(f"Classifier not available: {classifier}")
        
        classifier_instance = self.classifiers[classifier]
        return classifier_instance.classify(image, top_k)
    
    def get_model_status(self) -> Dict[str, Any]:
        """
        Get status of all loaded models.
        
        Returns:
            Model status dictionary
        """
        status = {
            "detectors": {},
            "classifiers": {},
            "scientific_engine": True
        }
        
        for name, detector in self.detectors.items():
            status["detectors"][name] = {
                "loaded": detector.is_loaded(),
                "info": detector.get_model_info()
            }
        
        for name, classifier in self.classifiers.items():
            status["classifiers"][name] = {
                "loaded": classifier.is_loaded(),
                "info": classifier.get_model_info()
            }
        
        return status
    
    def reload_model(self, model_name: str):
        """
        Reload a specific model.
        
        Args:
            model_name: Name of model to reload
        """
        # Implementation would unload and reload the model
        logger.info(f"Reloading model: {model_name}")
        # TODO: Implement proper reload logic


# Global AI manager instance
ai_manager = AIManager()
