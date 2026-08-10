"""
Pipeline vidéo complet.
Orchestre les étapes du pipeline dans l'ordre : Capture → Buffer → Detection → Rules → Alerts → EventBus.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from app.desktop.pipeline.stages import (
    PipelineStage, PipelineContext, PipelineResult,
    CaptureStage, BufferStage, DetectionStage, RuleEngineStage,
    AlertStage, EventBusStage, RecordingStage, NotificationStage
)
from app.core.logger import get_logger


@dataclass
class PipelineConfig:
    """Configuration du pipeline vidéo."""
    buffer_size: int = 30
    enable_detection: bool = True
    enable_recording: bool = False
    enable_notifications: bool = True
    enable_event_bus: bool = True


class VideoPipeline:
    """
    Pipeline vidéo complet.
    Enchaîne les étapes de traitement dans l'ordre défini.
    """
    
    def __init__(self, camera_id: str, config: PipelineConfig = None):
        """
        Initialise le pipeline vidéo.
        
        Args:
            camera_id: ID de la caméra
            config: Configuration du pipeline
        """
        self.camera_id = camera_id
        self.config = config or PipelineConfig()
        self._logger = get_logger(f"VideoPipeline.{camera_id}")
        
        # Étapes du pipeline
        self._capture_stage: Optional[CaptureStage] = None
        self._buffer_stage: Optional[BufferStage] = None
        self._detection_stage: Optional[DetectionStage] = None
        self._rule_engine_stage: Optional[RuleEngineStage] = None
        self._alert_stage: Optional[AlertStage] = None
        self._event_bus_stage: Optional[EventBusStage] = None
        self._recording_stage: Optional[RecordingStage] = None
        self._notification_stage: Optional[NotificationStage] = None
        
        # Métriques
        self._frame_count = 0
        self._error_count = 0
        self._last_frame_time = None
        
        self._build_pipeline()
    
    def _build_pipeline(self):
        """Construit le pipeline en enchaînant les étapes."""
        # Créer les étapes
        self._buffer_stage = BufferStage(buffer_size=self.config.buffer_size)
        
        # Enchaîner les étapes
        # Capture → Buffer → Detection → Rules → Alerts → EventBus → Recording → Notification
        # Note: CaptureStage est géré par CameraWorker, on commence par Buffer
        
        if self.config.enable_detection:
            # DetectionStage sera ajouté dynamiquement avec le détecteur
            pass
        
        if self.config.enable_event_bus:
            # EventBusStage sera ajouté dynamiquement avec le EventBus
            pass
        
        if self.config.enable_recording:
            # RecordingStage sera ajouté dynamiquement avec le RecordingManager
            pass
        
        if self.config.enable_notifications:
            # NotificationStage sera ajouté dynamiquement avec le NotificationService
            pass
        
        self._logger.info(f"Pipeline construit pour caméra {self.camera_id}")
    
    def set_capture_stage(self, camera_worker):
        """
        Définit l'étape de capture.
        
        Args:
            camera_worker: Worker de capture vidéo
        """
        self._capture_stage = CaptureStage(camera_worker)
        self._capture_stage.set_next(self._buffer_stage)
    
    def set_detection_stage(self, detector):
        """
        Définit l'étape de détection.
        
        Args:
            detector: Détecteur IA
        """
        self._detection_stage = DetectionStage(detector)
        
        # Insérer après Buffer
        self._buffer_stage.set_next(self._detection_stage)
        
        # Connecter aux étapes suivantes
        if self._rule_engine_stage:
            self._detection_stage.set_next(self._rule_engine_stage)
        elif self._event_bus_stage:
            self._detection_stage.set_next(self._event_bus_stage)
    
    def set_rule_engine_stage(self, rule_engine):
        """
        Définit l'étape du moteur de règles.
        
        Args:
            rule_engine: Moteur de règles
        """
        self._rule_engine_stage = RuleEngineStage(rule_engine)
        
        # Insérer après Detection
        if self._detection_stage:
            self._detection_stage.set_next(self._rule_engine_stage)
        else:
            self._buffer_stage.set_next(self._rule_engine_stage)
        
        # Connecter à AlertStage
        if self._alert_stage:
            self._rule_engine_stage.set_next(self._alert_stage)
        elif self._event_bus_stage:
            self._rule_engine_stage.set_next(self._event_bus_stage)
    
    def set_alert_stage(self, alert_service):
        """
        Définit l'étape d'alertes.
        
        Args:
            alert_service: Service de gestion des alertes
        """
        self._alert_stage = AlertStage(alert_service)
        
        # Insérer après RuleEngine
        if self._rule_engine_stage:
            self._rule_engine_stage.set_next(self._alert_stage)
        elif self._detection_stage:
            self._detection_stage.set_next(self._alert_stage)
        else:
            self._buffer_stage.set_next(self._alert_stage)
        
        # Connecter à EventBusStage
        if self._event_bus_stage:
            self._alert_stage.set_next(self._event_bus_stage)
    
    def set_event_bus_stage(self, event_bus):
        """
        Définit l'étape du bus d'événements.
        
        Args:
            event_bus: Bus d'événements
        """
        self._event_bus_stage = EventBusStage(event_bus)
        
        # Connecter à la dernière étape
        if self._alert_stage:
            self._alert_stage.set_next(self._event_bus_stage)
        elif self._rule_engine_stage:
            self._rule_engine_stage.set_next(self._event_bus_stage)
        elif self._detection_stage:
            self._detection_stage.set_next(self._event_bus_stage)
        else:
            self._buffer_stage.set_next(self._event_bus_stage)
        
        # Connecter à RecordingStage
        if self.config.enable_recording:
            self._event_bus_stage.set_next(self._recording_stage)
    
    def set_recording_stage(self, recording_manager):
        """
        Définit l'étape d'enregistrement.
        
        Args:
            recording_manager: Gestionnaire d'enregistrement
        """
        self._recording_stage = RecordingStage(recording_manager)
        
        # Insérer après EventBus
        if self._event_bus_stage:
            self._event_bus_stage.set_next(self._recording_stage)
        
        # Connecter à NotificationStage
        if self._notification_stage:
            self._recording_stage.set_next(self._notification_stage)
    
    def set_notification_stage(self, notification_service):
        """
        Définit l'étape de notification.
        
        Args:
            notification_service: Service de notifications
        """
        self._notification_stage = NotificationStage(notification_service)
        
        # Insérer après Recording
        if self._recording_stage:
            self._recording_stage.set_next(self._notification_stage)
        elif self._event_bus_stage:
            self._event_bus_stage.set_next(self._notification_stage)
    
    def process_frame(self, frame, frame_number: int = 0) -> PipelineResult:
        """
        Traite un frame à travers le pipeline.
        
        Args:
            frame: Frame à traiter
            frame_number: Numéro du frame
        
        Returns:
            Résultat du pipeline
        """
        # Créer le contexte
        context = PipelineContext(
            camera_id=self.camera_id,
            frame=frame,
            frame_number=frame_number
        )
        
        # Traiter à travers le pipeline
        result = self._buffer_stage.process(context)
        
        # Mettre à jour les métriques
        self._frame_count += 1
        if not result.success:
            self._error_count += 1
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques du pipeline."""
        metrics = {
            "camera_id": self.camera_id,
            "frame_count": self._frame_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / self._frame_count if self._frame_count > 0 else 0.0,
            "stages": {}
        }
        
        # Ajouter les métriques de chaque étape
        stages = [
            self._buffer_stage,
            self._detection_stage,
            self._rule_engine_stage,
            self._alert_stage,
            self._event_bus_stage,
            self._recording_stage,
            self._notification_stage
        ]
        
        for stage in stages:
            if stage:
                metrics["stages"][stage.name] = stage.get_metrics()
        
        return metrics
    
    def enable_stage(self, stage_name: str):
        """
        Active une étape du pipeline.
        
        Args:
            stage_name: Nom de l'étape
        """
        stage_map = {
            "Buffer": self._buffer_stage,
            "Detection": self._detection_stage,
            "RuleEngine": self._rule_engine_stage,
            "Alert": self._alert_stage,
            "EventBus": self._event_bus_stage,
            "Recording": self._recording_stage,
            "Notification": self._notification_stage
        }
        
        stage = stage_map.get(stage_name)
        if stage:
            stage.enable()
    
    def disable_stage(self, stage_name: str):
        """
        Désactive une étape du pipeline.
        
        Args:
            stage_name: Nom de l'étape
        """
        stage_map = {
            "Buffer": self._buffer_stage,
            "Detection": self._detection_stage,
            "RuleEngine": self._rule_engine_stage,
            "Alert": self._alert_stage,
            "EventBus": self._event_bus_stage,
            "Recording": self._recording_stage,
            "Notification": self._notification_stage
        }
        
        stage = stage_map.get(stage_name)
        if stage:
            stage.disable()
