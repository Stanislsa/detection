"""
Wrapper YOLO11 pour la détection de personnes et optimisation multi-caméra.

Intégration avec OpenVINO pour accélération CPU Intel (ThinkPad i5).
Support multi-flux RTSP avec frame skipping pour économie RAM.

Reference:
- Ultralytics YOLO11 (2024)
- OpenVINO Toolkit (Intel)
"""

import cv2
import numpy as np
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass
from pathlib import Path
import time

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

from app.config import settings


@dataclass
class YOLODetection:
    """Résultat de détection YOLO."""
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    class_id: int
    class_name: str
    timestamp: float


@dataclass
class YOLOResult:
    """Résultat complet de détection sur une frame."""
    detections: List[YOLODetection]
    frame: np.ndarray
    timestamp: float
    processing_time_ms: float


class YOLODetector:
    """
    Wrapper YOLO11 optimisé pour CPU Intel avec OpenVINO.
    
    Fonctionnalités:
    - Détection de personnes (classe 0 COCO)
    - Conversion automatique OpenVINO
    - Frame skipping pour économie RAM
    - Support multi-caméra
    """
    
    def __init__(
        self,
        model_name: str = "yolo11n.pt",
        device: str = "cpu",
        confidence_threshold: float = 0.5,
        use_openvino: bool = True,
        frame_skip: int = 1
    ):
        """
        Initialise le détecteur YOLO.
        
        Args:
            model_name: Nom du modèle (yolo11n.pt, yolo11s.pt, etc.)
            device: Device d'exécution (cpu, cuda, openvino)
            confidence_threshold: Seuil de confiance [0, 1]
            use_openvino: Utiliser OpenVINO si disponible
            frame_skip: Sauter N frames (1 = toutes, 3 = 1 sur 3)
        """
        if YOLO is None:
            raise ImportError("ultralytics non installé. pip install ultralytics")
        
        self.model_name = model_name
        self.device = device
        self.confidence_threshold = confidence_threshold
        self.use_openvino = use_openvino
        self.frame_skip = frame_skip
        self.frame_count = 0
        
        # Charger le modèle
        self.model = self._load_model()
        
        # Classe personne dans COCO (0 = person)
        self.person_class_id = 0
        
    def _load_model(self):
        """Charge le modèle YOLO avec conversion OpenVINO si demandé."""
        model_path = Path(model_name)
        
        # Si OpenVINO demandé et modèle non converti
        if self.use_openvino and not model_path.name.endswith("_openvino_model"):
            openvino_path = model_path.stem + "_openvino_model"
            if Path(openvino_path).exists():
                # Utiliser le modèle OpenVINO existant
                return YOLO(openvino_path, task="detect")
            else:
                # Convertir automatiquement
                print(f"Conversion OpenVINO de {model_name}...")
                base_model = YOLO(model_name)
                base_model.export(format="openvino", dynamic=True, half=True)
                return YOLO(openvino_path, task="detect")
        
        # Charger le modèle standard
        return YOLO(model_name, task="detect")
    
    def process_frame(self, frame: np.ndarray) -> Optional[YOLOResult]:
        """
        Traite une frame et détecte les personnes.
        
        Args:
            frame: Image OpenCV (BGR)
        
        Returns:
            YOLOResult avec détections ou None si frame skip
        """
        # Frame skipping
        self.frame_count += 1
        if self.frame_count % self.frame_skip != 0:
            return None
        
        start_time = time.time()
        
        # Inférence YOLO
        results = self.model(
            frame,
            conf=self.confidence_threshold,
            device=self.device,
            verbose=False,
            classes=[self.person_class_id]  # Uniquement personnes
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        # Extraire les détections
        detections = self._extract_detections(results[0])
        
        return YOLOResult(
            detections=detections,
            frame=frame,
            timestamp=time.time(),
            processing_time_ms=processing_time
        )
    
    def _extract_detections(self, result) -> List[YOLODetection]:
        """
        Extrait les détections depuis le résultat YOLO.
        
        Args:
            result: Résultat brut YOLO
        
        Returns:
            Liste des détections filtrées (personnes uniquement)
        """
        detections = []
        
        if result.boxes is None:
            return detections
        
        for box in result.boxes:
            # Filtrer uniquement les personnes
            if int(box.cls[0]) != self.person_class_id:
                continue
            
            # Coordonnées bounding box
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Confiance
            confidence = float(box.conf[0])
            
            # Nom de classe
            class_name = result.names[int(box.cls[0])]
            
            detections.append(YOLODetection(
                bbox=(x1, y1, x2, y2),
                confidence=confidence,
                class_id=int(box.cls[0]),
                class_name=class_name,
                timestamp=time.time()
            ))
        
        return detections
    
    def get_primary_person_roi(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Retourne la ROI (Region of Interest) de la personne principale.
        
        Utile pour restreindre MediaPipe à la zone pertinente.
        
        Args:
            frame: Image OpenCV
        
        Returns:
            Bounding box (x1, y1, x2, y2) ou None
        """
        result = self.process_frame(frame)
        if not result or not result.detections:
            return None
        
        # Prendre la détection avec la confiance la plus élevée
        primary = max(result.detections, key=lambda d: d.confidence)
        return primary.bbox
    
    def draw_detections(self, frame: np.ndarray, result: YOLOResult) -> np.ndarray:
        """
        Dessine les bounding boxes sur l'image.
        
        Args:
            frame: Image originale
            result: Résultat de détection
        
        Returns:
            Image avec bounding boxes
        """
        output = frame.copy()
        
        for detection in result.detections:
            x1, y1, x2, y2 = detection.bbox
            
            # Dessiner rectangle
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Dessiner label
            label = f"{detection.class_name}: {detection.confidence:.2f}"
            cv2.putText(
                output,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
        
        return output
    
    def convert_to_openvino(self, output_dir: str = None):
        """
        Convertit le modèle actuel au format OpenVINO.
        
        Args:
            output_dir: Répertoire de sortie (défaut: même que modèle)
        """
        print(f"Conversion de {self.model_name} vers OpenVINO...")
        
        output_path = self.model.export(
            format="openvino",
            dynamic=True,
            half=True,
            output_dir=output_dir
        )
        
        print(f"Modèle OpenVINO créé: {output_path}")
        return output_path
    
    def get_fps(self) -> float:
        """
        Estime le FPS basé sur le temps de traitement.
        
        Returns:
            FPS estimé
        """
        # À implémenter avec historique des temps
        return 30.0  # Valeur par défaut
    
    def close(self):
        """Libère les ressources."""
        if hasattr(self.model, 'predictor'):
            del self.model
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class MultiYOLODetector:
    """
    Gestionnaire multi-caméra avec YOLO.
    
    Supporte plusieurs flux RTSP simultanés avec threading.
    """
    
    def __init__(
        self,
        camera_sources: List[str],
        model_name: str = "yolo11n.pt",
        use_openvino: bool = True,
        frame_skip: int = 3
    ):
        """
        Initialise le détecteur multi-caméra.
        
        Args:
            camera_sources: Liste des sources (RTSP URLs, webcam indices)
            model_name: Nom du modèle YOLO
            use_openvino: Utiliser OpenVINO
            frame_skip: Frame skipping pour économie RAM
        """
        self.camera_sources = camera_sources
        self.detectors = []
        self.captures = []
        
        # Créer un détecteur par caméra
        for source in camera_sources:
            detector = YOLODetector(
                model_name=model_name,
                use_openvino=use_openvino,
                frame_skip=frame_skip
            )
            self.detectors.append(detector)
            
            # Ouvrir la capture
            cap = cv2.VideoCapture(source)
            if cap.isOpened():
                self.captures.append(cap)
            else:
                print(f"Erreur: Impossible d'ouvrir {source}")
    
    def process_all(self) -> Dict[str, Optional[YOLOResult]]:
        """
        Traite toutes les caméras.
        
        Returns:
            Dictionnaire {source: YOLOResult}
        """
        results = {}
        
        for i, (source, cap, detector) in enumerate(zip(
            self.camera_sources, self.captures, self.detectors
        )):
            ret, frame = cap.read()
            if ret:
                results[source] = detector.process_frame(frame)
            else:
                results[source] = None
        
        return results
    
    def close(self):
        """Ferme toutes les captures et détecteurs."""
        for cap in self.captures:
            cap.release()
        
        for detector in self.detectors:
            detector.close()
