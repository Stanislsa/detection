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
        Pipeline CDC / cœur métier :
          1) YOLO → détection personne(s) (précision localisation)
          2) Crop ROI personne principale
          3) MediaPipe Pose → squelette 3D / landmarks
          4) Critères formels (angle, vitesse, impact, temps au sol)
          5) Score de gravité

        YOLO ne remplace pas MediaPipe pour la chute (contrainte CDC) :
        il cadre la personne pour améliorer la pose.
        """
        import numpy as np

        results: Dict[str, Any] = {}
        yolo_results: List[Dict[str, Any]] = []
        roi_image = image
        crop_box = None

        # 1) YOLO personnes
        if "yolo_person" in self.detectors:
            try:
                yolo_results = self.detectors["yolo_person"].detect(image) or []
                results["yolo"] = yolo_results
            except Exception as e:
                logger.warning(f"YOLO person failed: {e}")
                results["yolo"] = []
                yolo_results = []

        # 2) ROI sur la personne la plus confiante / plus grande
        if yolo_results:
            try:
                best = max(
                    yolo_results,
                    key=lambda d: float(d.get("confidence") or 0) * max(
                        1.0,
                        float((d.get("bbox") or d.get("box") or [0, 0, 1, 1])[2])
                        * float((d.get("bbox") or d.get("box") or [0, 0, 1, 1])[3]),
                    ),
                )
                box = best.get("bbox") or best.get("box") or best.get("xyxy")
                if box is not None and len(box) >= 4:
                    # Support xyxy or xywh
                    x1, y1, a, b = [float(v) for v in box[:4]]
                    if a > x1 and b > y1:  # likely xyxy
                        x2, y2 = a, b
                    else:  # xywh
                        x2, y2 = x1 + a, y1 + b
                    h, w = image.shape[:2]
                    # padding 15%
                    bw, bh = x2 - x1, y2 - y1
                    x1 = max(0, int(x1 - 0.15 * bw))
                    y1 = max(0, int(y1 - 0.15 * bh))
                    x2 = min(w, int(x2 + 0.15 * bw))
                    y2 = min(h, int(y2 + 0.15 * bh))
                    if x2 > x1 + 10 and y2 > y1 + 10:
                        roi_image = image[y1:y2, x1:x2]
                        crop_box = [x1, y1, x2, y2]
            except Exception as e:
                logger.debug(f"ROI crop skip: {e}")

        # 3) MediaPipe fall sur ROI (fallback full frame)
        mp_results: Dict[str, Any] = {}
        if "mediapipe_fall" in self.detectors:
            try:
                mp_results = self.detectors["mediapipe_fall"].detect_fall(
                    roi_image, person_profile
                )
                # Si pose échoue sur ROI, réessayer frame entière
                if not mp_results.get("landmarks_count") and roi_image is not image:
                    mp_results = self.detectors["mediapipe_fall"].detect_fall(
                        image, person_profile
                    )
                    crop_box = None
                results["mediapipe"] = mp_results
            except Exception as e:
                logger.warning(f"MediaPipe fall failed: {e}")
                results["mediapipe"] = {"fall_detected": False, "confidence": 0.0, "error": str(e)}
        else:
            results["mediapipe"] = {"fall_detected": False, "confidence": 0.0, "error": "mediapipe_unavailable"}

        # 4) Analyse scientifique optionnelle
        try:
            if hasattr(self, "scientific_engine") and self.scientific_engine:
                sci = getattr(self.scientific_engine, "analyze_fall", None)
                if callable(sci):
                    results["scientific"] = sci(image, person_profile) or {}
        except Exception as e:
            logger.debug(f"scientific analysis failed: {e}")

        combined = self._combine_detection_results(results)
        combined["yolo_person_count"] = len(yolo_results) if isinstance(yolo_results, list) else 0
        combined["roi_crop"] = crop_box
        combined["pipeline"] = "yolo_person → mediapipe_pose → fall_criteria → severity"
        return combined

    def _combine_detection_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine results — CDC : MediaPipe Pose prioritaire (pas YOLO-Pose).
        YOLO sert uniquement de confirmation « personne présente ».
        """
        mp = results.get("mediapipe") or {}
        yolo = results.get("yolo")
        person_present = True
        if isinstance(yolo, list):
            person_present = len(yolo) > 0
        elif isinstance(yolo, dict):
            person_present = bool(yolo.get("detections") or yolo.get("persons") or yolo)

        fall = bool(mp.get("fall_detected"))
        conf = float(mp.get("confidence") or 0.0)
        # Si aucune personne YOLO et confiance faible → prudence
        if not person_present and conf < 0.85:
            fall = False
            conf = conf * 0.5

        sci = results.get("scientific") or {}
        if sci.get("fall_detected") and conf < 0.9:
            conf = max(conf, float(sci.get("confidence") or conf))

        combined = {
            "fall_detected": fall,
            "confidence": round(conf, 4),
            "methods_used": list(results.keys()),
            "method_results": results,
            "person_present": person_present,
            "method": "hybrid_yolo_mediapipe",
            "trunk_angle": mp.get("trunk_angle") or mp.get("trunk_angle_deg"),
            "vertical_velocity": mp.get("vertical_velocity"),
            "vertical_velocity_ms": mp.get("vertical_velocity_ms"),
            "is_horizontal": mp.get("is_horizontal"),
            "impact_accel_ms2": mp.get("impact_accel_ms2"),
            "stillness_ratio": mp.get("stillness_ratio"),
            "criteria_version": mp.get("criteria_version"),
            "decision": mp.get("decision"),
            "severity": mp.get("severity") or sci.get("severity"),
            "time_on_ground_s": mp.get("time_on_ground_s"),
            "landmarks_count": mp.get("landmarks_count"),
            "signals": (mp.get("decision") or {}).get("signals") or {
                "trunk_angle_deg": mp.get("trunk_angle_deg") or mp.get("trunk_angle"),
                "vertical_velocity_ms": mp.get("vertical_velocity_ms"),
                "is_horizontal": 1.0 if mp.get("is_horizontal") else 0.0,
                "time_on_ground_s": mp.get("time_on_ground_s"),
            },
        }
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
