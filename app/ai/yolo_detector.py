"""
Détecteur YOLO (You Only Look Once).
Implémentation pour YOLOv8/YOLOv5 avec Ultralytics.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

from app.ai.base_detector import BaseDetector
from app.desktop.workers.detection_worker import DetectionResult
from app.core.logger import get_logger
from app.core.exceptions import DetectionException


class YOLODetector(BaseDetector):
    """
    Détecteur utilisant YOLO (Ultralytics).
    Supporte YOLOv8, YOLOv5 et autres modèles Ultralytics.
    """
    
    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.5,
        device: str = "cpu"
    ):
        """
        Initialise le détecteur YOLO.
        
        Args:
            model_path: Chemin vers le modèle ou nom du modèle pré-entraîné
            confidence_threshold: Seuil de confiance
            device: Device d'exécution (cpu, cuda, mps, etc.)
        """
        super().__init__(model_path, confidence_threshold)
        self.device = device
        self._class_names = {
            0: "person",
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            4: "airplane",
            5: "bus",
            6: "train",
            7: "truck",
            8: "boat",
            # ... autres classes COCO
        }
    
    def load_model(self) -> bool:
        """
        Charge le modèle YOLO.
        
        Returns:
            True si succès
        """
        if not YOLO_AVAILABLE:
            self._logger.error("Ultralytics YOLO non installé. pip install ultralytics")
            raise DetectionException("Ultralytics YOLO non installé")
        
        try:
            self._logger.info(f"Chargement du modèle YOLO: {self.model_path}")
            self._model = YOLO(self.model_path)
            self._model.to(self.device)
            self._is_loaded = True
            
            # Mettre à jour les noms de classes si disponibles
            if hasattr(self._model, 'names'):
                self._class_names = self._model.names
            
            self._logger.info("Modèle YOLO chargé avec succès")
            return True
            
        except Exception as e:
            self._logger.error(f"Erreur chargement modèle YOLO: {e}")
            raise DetectionException(f"Erreur chargement modèle: {e}")
    
    def detect(self, frame: np.ndarray, confidence_threshold: Optional[float] = None) -> List[DetectionResult]:
        """
        Effectue la détection avec YOLO.
        
        Args:
            frame: Frame à analyser
            confidence_threshold: Seuil de confiance
        
        Returns:
            Liste des résultats de détection
        """
        if not self._is_loaded:
            self._logger.warning("Modèle non chargé, tentative de chargement...")
            self.load_model()
        
        threshold = confidence_threshold or self.confidence_threshold
        
        try:
            # Prétraitement
            processed_frame = self.preprocess(frame)
            
            # Inférence
            results = self._model(
                processed_frame,
                conf=threshold,
                verbose=False,
                device=self.device
            )
            
            # Post-traitement
            detections = []
            for result in results:
                detections.extend(self._process_result(result, frame.shape))
            
            return detections
            
        except Exception as e:
            self._logger.error(f"Erreur lors de la détection YOLO: {e}")
            return []
    
    def _process_result(self, result, frame_shape: Tuple[int, int]) -> List[DetectionResult]:
        """
        Traite les résultats bruts de YOLO.
        
        Args:
            result: Résultat brut de YOLO
            frame_shape: Dimensions du frame (height, width, channels)
        
        Returns:
            Liste des résultats de détection
        """
        detections = []
        
        if result.boxes is not None:
            for box in result.boxes:
                # Bounding box
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                bbox = (int(x1), int(y1), int(x2 - x1), int(y2 - y1))
                
                # Classe et confiance
                class_id = int(box.cls[0].cpu().numpy())
                confidence = float(box.conf[0].cpu().numpy())
                
                # Nom de classe
                class_name = self._class_names.get(class_id, f"class_{class_id}")
                
                # Données additionnelles
                additional_data = {
                    "class_id": class_id,
                    "xyxy": [int(x1), int(y1), int(x2), int(y2)]
                }
                
                detection = DetectionResult(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    bbox=bbox,
                    additional_data=additional_data
                )
                detections.append(detection)
        
        return detections
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le modèle.
        
        Returns:
            Dictionnaire d'informations
        """
        return {
            "type": "YOLO",
            "model_path": self.model_path,
            "device": self.device,
            "confidence_threshold": self.confidence_threshold,
            "is_loaded": self._is_loaded,
            "class_names": self._class_names
        }
    
    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Prétraite le frame (YOLO gère cela automatiquement).
        
        Args:
            frame: Frame original
        
        Returns:
            Frame original (YOLO gère le prétraitement)
        """
        return frame


class YOLOPersonDetector(YOLODetector):
    """
    Détecteur spécialisé pour les personnes uniquement.
    Filtre les résultats pour ne garder que les détections de personnes.
    """
    
    def detect(self, frame: np.ndarray, confidence_threshold: Optional[float] = None) -> List[DetectionResult]:
        """
        Effectue la détection et filtre pour les personnes.
        
        Args:
            frame: Frame à analyser
            confidence_threshold: Seuil de confiance
        
        Returns:
            Liste des détections de personnes uniquement
        """
        all_detections = super().detect(frame, confidence_threshold)
        
        # Filtrer pour ne garder que les personnes
        person_detections = [
            d for d in all_detections
            if d.class_name == "person"
        ]
        
        return person_detections
