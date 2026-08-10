"""
Étapes du pipeline vidéo.
Chaque étape a une responsabilité unique dans le flux de traitement.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from dataclasses import dataclass
from datetime import datetime
import numpy as np

from app.core.logger import get_logger


@dataclass
class PipelineContext:
    """Contexte partagé entre les étapes du pipeline."""
    camera_id: str
    frame: Optional[np.ndarray] = None
    frame_number: int = 0
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PipelineResult:
    """Résultat d'une étape du pipeline."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PipelineStage(ABC):
    """
    Étape de base du pipeline.
    Toutes les étapes héritent de cette classe.
    """
    
    def __init__(self, name: str):
        """
        Initialise l'étape.
        
        Args:
            name: Nom de l'étape
        """
        self.name = name
        self._logger = get_logger(f"PipelineStage.{name}")
        self._next_stage: Optional[PipelineStage] = None
        self._enabled = True
        self._metrics = {
            "processed_count": 0,
            "error_count": 0,
            "avg_processing_time_ms": 0.0
        }
    
    def set_next(self, stage: 'PipelineStage'):
        """
        Définit l'étape suivante dans le pipeline.
        
        Args:
            stage: Étape suivante
        """
        self._next_stage = stage
    
    def enable(self):
        """Active l'étape."""
        self._enabled = True
        self._logger.info(f"Étape {self.name} activée")
    
    def disable(self):
        """Désactive l'étape."""
        self._enabled = False
        self._logger.info(f"Étape {self.name} désactivée")
    
    def is_enabled(self) -> bool:
        """Retourne True si l'étape est activée."""
        return self._enabled
    
    def process(self, context: PipelineContext) -> PipelineResult:
        """
        Traite le contexte et passe au résultat.
        
        Args:
            context: Contexte du pipeline
        
        Returns:
            Résultat du traitement
        """
        if not self._enabled:
            return PipelineResult(success=True, data=context)
        
        start_time = datetime.now()
        
        try:
            result = self._process(context)
            
            # Mettre à jour les métriques
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._metrics["processed_count"] += 1
            self._metrics["avg_processing_time_ms"] = (
                (self._metrics["avg_processing_time_ms"] * (self._metrics["processed_count"] - 1) + processing_time)
                / self._metrics["processed_count"]
            )
            
            # Passer à l'étape suivante si succès
            if result.success and self._next_stage:
                return self._next_stage.process(context)
            
            return result
            
        except Exception as e:
            self._metrics["error_count"] += 1
            self._logger.error(f"Erreur dans l'étape {self.name}: {e}")
            return PipelineResult(success=False, error=str(e))
    
    @abstractmethod
    def _process(self, context: PipelineContext) -> PipelineResult:
        """
        Implémentation spécifique du traitement.
        
        Args:
            context: Contexte du pipeline
        
        Returns:
            Résultat du traitement
        """
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de l'étape."""
        return self._metrics.copy()


class CaptureStage(PipelineStage):
    """
    Étape de capture vidéo.
    Récupère les frames depuis la source (RTSP, webcam, fichier).
    """
    
    def __init__(self, camera_worker):
        """
        Initialise l'étape de capture.
        
        Args:
            camera_worker: Worker de capture vidéo
        """
        super().__init__("Capture")
        self._camera_worker = camera_worker
    
    def _process(self, context: PipelineContext) -> PipelineResult:
        """Capture un frame depuis la source."""
        # Le frame est déjà capturé par le CameraWorker
        # Cette étape valide et prépare le frame
        if context.frame is None:
            return PipelineResult(success=False, error="No frame available")
        
        # Valider le frame
        if not isinstance(context.frame, np.ndarray) or context.frame.size == 0:
            return PipelineResult(success=False, error="Invalid frame")
        
        # Ajouter des métadonnées de capture
        context.metadata["captured_at"] = datetime.now()
        context.metadata["frame_shape"] = context.frame.shape
        
        return PipelineResult(success=True, data=context)


class BufferStage(PipelineStage):
    """
    Étape de buffer de frames.
    Gère un buffer circulaire pour les frames récents.
    """
    
    def __init__(self, buffer_size: int = 30):
        """
        Initialise l'étape de buffer.
        
        Args:
            buffer_size: Taille du buffer (nombre de frames)
        """
        super().__init__("Buffer")
        self._buffer_size = buffer_size
        self._buffer: list = []
    
    def _process(self, context: PipelineContext) -> PipelineResult:
        """Ajoute le frame au buffer."""
        # Ajouter au buffer
        self._buffer.append(context)
        
        # Garder seulement les N derniers frames
        if len(self._buffer) > self._buffer_size:
            self._buffer.pop(0)
        
        # Ajouter les frames du buffer au contexte
        context.metadata["buffer_size"] = len(self._buffer)
        context.metadata["buffer_frames"] = len(self._buffer)
        
        return PipelineResult(success=True, data=context)
    
    def get_buffer(self) -> list:
        """Retourne le buffer actuel."""
        return self._buffer.copy()
    
    def clear_buffer(self):
        """Efface le buffer."""
        self._buffer.clear()


class DetectionStage(PipelineStage):
    """
    Étape de détection IA.
    Exécute l'inférence sur le frame.
    """
    
    def __init__(self, detector):
        """
        Initialise l'étape de détection.
        
        Args:
            detector: Détecteur IA
        """
        super().__init__("Detection")
        self._detector = detector
    
    def _process(self, context: PipelineContext) -> PipelineResult:
        """Exécute la détection IA sur le frame."""
        if context.frame is None:
            return PipelineResult(success=False, error="No frame for detection")
        
        try:
            # Exécuter la détection
            detections = self._detector.detect(context.frame)
            
            # Ajouter les résultats au contexte
            context.metadata["detections"] = detections
            context.metadata["detection_count"] = len(detections)
            context.metadata["detector_name"] = self._detector.__class__.__name__
            
            return PipelineResult(success=True, data=context, metadata={"detections": detections})
            
        except Exception as e:
            return PipelineResult(success=False, error=f"Detection failed: {e}")


class RuleEngineStage(PipelineStage):
    """
    Étape du moteur de règles.
    Évalue les règles sur les détections.
    """
    
    def __init__(self, rule_engine):
        """
        Initialise l'étape du moteur de règles.
        
        Args:
            rule_engine: Moteur de règles
        """
        super().__init__("RuleEngine")
        self._rule_engine = rule_engine
    
    def _process(self, context: PipelineContext) -> PipelineResult:
        """Évalue les règles sur les détections."""
        detections = context.metadata.get("detections", [])
        
        if not detections:
            return PipelineResult(success=True, data=context)
        
        try:
            # Créer le contexte pour le moteur de règles
            rule_context = {
                "camera_id": context.camera_id,
                "timestamp": context.timestamp,
                "detections": detections,
                "frame": context.frame
            }
            
            # Évaluer les règles
            triggered_rules = self._rule_engine.process_detections(detections, rule_context)
            
            # Ajouter les résultats au contexte
            context.metadata["triggered_rules"] = triggered_rules
            context.metadata["triggered_rule_count"] = len(triggered_rules)
            
            return PipelineResult(success=True, data=context, metadata={"triggered_rules": triggered_rules})
            
        except Exception as e:
            return PipelineResult(success=False, error=f"Rule evaluation failed: {e}")


class AlertStage(PipelineStage):
    """
    Étape de génération d'alertes.
    Génère les alertes basées sur les règles déclenchées.
    """
    
    def __init__(self, alert_service):
        """
        Initialise l'étape d'alertes.
        
        Args:
            alert_service: Service de gestion des alertes
        """
        super().__init__("Alert")
        self._alert_service = alert_service
    
    def _process(self, context: PipelineContext) -> PipelineResult:
        """Génère les alertes basées sur les règles déclenchées."""
        triggered_rules = context.metadata.get("triggered_rules", [])
        
        if not triggered_rules:
            return PipelineResult(success=True, data=context)
        
        try:
            # Les alertes sont déjà générées par le moteur de règles
            # Cette étape peut ajouter une logique supplémentaire
            # (agrégation, déduplication, etc.)
            
            context.metadata["alerts_generated"] = len(triggered_rules)
            
            return PipelineResult(success=True, data=context)
            
        except Exception as e:
            return PipelineResult(success=False, error=f"Alert generation failed: {e}")


class EventBusStage(PipelineStage):
    """
    Étape de publication sur le bus d'événements.
    Publie les résultats sur le bus d'événements.
    """
    
    def __init__(self, event_bus):
        """
        Initialise l'étape du bus d'événements.
        
        Args:
            event_bus: Bus d'événements
        """
        super().__init__("EventBus")
        self._event_bus = event_bus
    
    def _process(self, context: PipelineContext) -> PipelineResult:
        """Publie les événements sur le bus."""
        try:
            # Publier les événements appropriés
            from app.events.event_types import FrameReceivedEvent, DetectionResultEvent
            
            # Frame reçu
            frame_event = FrameReceivedEvent(
                camera_id=context.camera_id,
                frame=context.frame,
                frame_number=context.frame_number
            )
            self._event_bus.publish(frame_event)
            
            # Détections
            detections = context.metadata.get("detections", [])
            if detections:
                detection_event = DetectionResultEvent(
                    camera_id=context.camera_id,
                    detections=[{
                        "class_id": d.class_id,
                        "class_name": d.class_name,
                        "confidence": d.confidence,
                        "bbox": d.bbox
                    } for d in detections],
                    model_name=context.metadata.get("detector_name", "unknown")
                )
                self._event_bus.publish(detection_event)
            
            return PipelineResult(success=True, data=context)
            
        except Exception as e:
            return PipelineResult(success=False, error=f"Event publishing failed: {e}")


class RecordingStage(PipelineStage):
    """
    Étape d'enregistrement.
    Enregistre les frames si nécessaire.
    """
    
    def __init__(self, recording_manager):
        """
        Initialise l'étape d'enregistrement.
        
        Args:
            recording_manager: Gestionnaire d'enregistrement
        """
        super().__init__("Recording")
        self._recording_manager = recording_manager
    
    def _process(self, context: PipelineContext) -> PipelineResult:
        """Enregistre le frame si nécessaire."""
        try:
            # Vérifier si l'enregistrement est actif pour cette caméra
            if self._recording_manager.is_recording(context.camera_id):
                self._recording_manager.add_frame(context.camera_id, context.frame)
                context.metadata["recorded"] = True
            else:
                context.metadata["recorded"] = False
            
            return PipelineResult(success=True, data=context)
            
        except Exception as e:
            return PipelineResult(success=False, error=f"Recording failed: {e}")


class NotificationStage(PipelineStage):
    """
    Étape de notification.
    Envoie les notifications aux opérateurs.
    """
    
    def __init__(self, notification_service):
        """
        Initialise l'étape de notification.
        
        Args:
            notification_service: Service de notifications
        """
        super().__init__("Notification")
        self._notification_service = notification_service
    
    def _process(self, context: PipelineContext) -> PipelineResult:
        """Envoie les notifications si nécessaire."""
        triggered_rules = context.metadata.get("triggered_rules", [])
        
        if not triggered_rules:
            return PipelineResult(success=True, data=context)
        
        try:
            # Les notifications sont déjà envoyées par les handlers
            # Cette étape peut ajouter une logique supplémentaire
            # (priorisation, agrégation, etc.)
            
            return PipelineResult(success=True, data=context)
            
        except Exception as e:
            return PipelineResult(success=False, error=f"Notification failed: {e}")
