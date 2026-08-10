"""
Démonstration du pipeline vidéo complet.
RTSP → OpenCV Capture → FrameQueue → YOLO → Rules → Alert → DB → WS → Dashboard
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from app.desktop.camera_manager import get_camera_manager
from app.desktop.pipeline.video_pipeline import VideoPipeline, PipelineConfig
from app.desktop.pipeline.bounded_queue import FrameQueue
from app.ai.scheduler.inference_scheduler import get_inference_scheduler
from app.ai.yolo_detector import YOLODetector
from app.ai.rules.intrusion import IntrusionRuleEngine
from app.events.event_bus import get_event_bus
from app.events.event_types import EventType
from app.desktop.observability import get_observability_service
from app.desktop.health_service import get_health_service
from app.core.config_loader import get_config_loader
from app.version import get_version


class PipelineDemo:
    """
    Démonstration du pipeline vidéo complet.
    """
    
    def __init__(self):
        # Initialiser l'application
        self.app = QApplication(sys.argv)
        
        # Charger la configuration
        self.config_loader = get_config_loader()
        self.config_loader.load_all()
        
        # Initialiser les services
        self.event_bus = get_event_bus()
        self.observability = get_observability_service()
        self.health_service = get_health_service()
        self.camera_manager = get_camera_manager()
        self.inference_scheduler = get_inference_scheduler()
        
        # Afficher les informations de version
        version = get_version()
        print(f"SentinelAI {version.app_version} (Build {version.build_number})")
        print(f"Environment: {version.environment}")
        
        # Afficher les backends IA disponibles
        backends = self.inference_scheduler.get_available_backends()
        preferred = self.inference_scheduler.get_preferred_backend()
        print(f"\nBackends IA disponibles: {[b.value for b in backends]}")
        print(f"Backend préféré: {preferred.value}")
        
        # Afficher l'état de santé initial
        self._print_health_status()
        
        # Abonnements aux événements
        self._setup_event_subscriptions()
    
    def _setup_event_subscriptions(self):
        """Configure les abonnements aux événements."""
        
        def on_frame_received(event):
            print(f"[FRAME] Caméra {event.camera_id}: Frame #{event.frame_number}")
        
        def on_detection_result(event):
            print(f"[DETECTION] Caméra {event.camera_id}: {len(event.detections)} détections")
            for det in event.detections[:3]:  # Afficher les 3 premières
                print(f"  - {det.class_name}: {det.confidence:.2f} @ {det.bbox}")
        
        def on_alert_generated(event):
            print(f"[ALERT] {event.alert_type}: {event.message} (sévérité: {event.severity})")
        
        self.event_bus.subscribe(EventType.FRAME_RECEIVED, on_frame_received)
        self.event_bus.subscribe(EventType.DETECTION_RESULT, on_detection_result)
        self.event_bus.subscribe(EventType.ALERT_GENERATED, on_alert_generated)
    
    def _print_health_status(self):
        """Affiche l'état de santé des composants."""
        print("\n" + "=" * 60)
        print("ÉTAT DE SANTÉ DES COMPOSANTS")
        print("=" * 60)
        
        health_checks = self.health_service.get_all_health()
        
        for component, health in health_checks.items():
            status_symbol = "✓" if health.status.value == "healthy" else "⚠" if health.status.value == "degraded" else "✗"
            print(f"{status_symbol} {component}: {health.status.value} - {health.message}")
        
        print("=" * 60)
    
    def run_demo(self, source: str = "0", duration: int = 30):
        """
        Exécute la démonstration.
        
        Args:
            source: Source vidéo (0 = webcam, rtsp://..., file://...)
            duration: Durée de la démo en secondes
        """
        print("\n" + "=" * 60)
        print("DÉMONSTRATION PIPELINE VIDÉO")
        print("=" * 60)
        print(f"Source: {source}")
        print(f"Durée: {duration}s")
        print("=" * 60)
        
        # Créer le détecteur
        print("\n[1/5] Initialisation du détecteur...")
        try:
            detector = self.inference_scheduler.create_detector(
                backend="cpu",  # Utiliser CPU pour la démo
                model_path="yolov8n.pt"
            )
            print("✓ Détecteur créé")
        except Exception as e:
            print(f"✗ Erreur création détecteur: {e}")
            detector = None
        
        # Créer le moteur de règles
        print("\n[2/5] Initialisation du moteur de règles...")
        try:
            rule_engine = IntrusionRuleEngine(self.event_bus)
            
            # Ajouter une zone de test
            from app.ai.rules.intrusion import Zone
            zone = Zone(
                id="test_zone",
                name="Zone de test",
                polygon=[[100, 100], [300, 100], [300, 300], [100, 300]],
                max_persons=0
            )
            rule_engine.add_zone(zone)
            
            print("✓ Moteur de règles créé avec zone de test")
        except Exception as e:
            print(f"✗ Erreur création moteur de règles: {e}")
            rule_engine = None
        
        # Créer le pipeline
        print("\n[3/5] Création du pipeline...")
        try:
            config = PipelineConfig(
                buffer_size=30,
                enable_detection=detector is not None,
                enable_recording=False,
                enable_notifications=True,
                enable_event_bus=True
            )
            
            pipeline = VideoPipeline(camera_id="demo_camera", config=config)
            print("✓ Pipeline créé")
        except Exception as e:
            print(f"✗ Erreur création pipeline: {e}")
            return
        
        # Ajouter et démarrer la caméra
        print("\n[4/5] Ajout et démarrage de la caméra...")
        try:
            self.camera_manager.add_camera(
                camera_id="demo_camera",
                source=source,
                name="Demo Camera"
            )
            
            self.camera_manager.start_capture("demo_camera")
            print("✓ Caméra démarrée")
        except Exception as e:
            print(f"✗ Erreur démarrage caméra: {e}")
            return
        
        # Enregistrer la caméra pour l'observabilité
        self.observability.register_camera("demo_camera")
        
        # Démarrer la détection
        if detector:
            print("\n[5/5] Démarrage de la détection...")
            try:
                self.camera_manager.start_detection("demo_camera", detector)
                print("✓ Détection démarrée")
            except Exception as e:
                print(f"✗ Erreur démarrage détection: {e}")
        
        # Timer pour arrêter la démo
        self.stop_timer = QTimer()
        self.stop_timer.timeout.connect(self._stop_demo)
        self.stop_timer.start(duration * 1000)
        
        # Timer pour afficher les statistiques
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._print_stats)
        self.stats_timer.start(5000)  # Toutes les 5 secondes
        
        print("\n" + "=" * 60)
        print("DÉMO EN COURS...")
        print("=" * 60)
        
        # Exécuter l'application
        self.app.exec()
    
    def _print_stats(self):
        """Affiche les statistiques actuelles."""
        print("\n--- STATISTIQUES ---")
        
        # Métriques système
        system_metrics = self.observability.get_system_metrics()
        print(f"CPU: {system_metrics.cpu_percent:.1f}%")
        print(f"Mémoire: {system_metrics.memory_percent:.1f}% ({system_metrics.memory_used_gb:.2f}GB)")
        print(f"Caméras actives: {system_metrics.active_cameras}")
        print(f"FPS total: {system_metrics.total_fps:.1f}")
        
        # Métriques caméra
        camera_metrics = self.observability.get_camera_metrics("demo_camera")
        if camera_metrics:
            print(f"FPS caméra: {camera_metrics.fps:.1f}")
            print(f"Queue size: {camera_metrics.queue_size}")
            print(f"Queue dropped: {camera_metrics.queue_dropped}")
            print(f"État: {camera_metrics.state}")
    
    def _stop_demo(self):
        """Arrête la démonstration."""
        print("\n" + "=" * 60)
        print("ARRÊT DE LA DÉMO")
        print("=" * 60)
        
        # Arrêter les timers
        self.stop_timer.stop()
        self.stats_timer.stop()
        
        # Arrêter la caméra
        try:
            self.camera_manager.stop_capture("demo_camera")
            self.camera_manager.stop_detection("demo_camera")
            self.camera_manager.remove_camera("demo_camera")
            print("✓ Caméra arrêtée")
        except Exception as e:
            print(f"✗ Erreur arrêt caméra: {e}")
        
        # Afficher les statistiques finales
        self._print_final_stats()
        
        # Quitter l'application
        self.app.quit()
    
    def _print_final_stats(self):
        """Affiche les statistiques finales."""
        print("\n" + "=" * 60)
        print("STATISTIQUES FINALES")
        print("=" * 60)
        
        # Métriques système
        system_metrics = self.observability.get_system_metrics()
        print(f"\nSystème:")
        print(f"  CPU: {system_metrics.cpu_percent:.1f}%")
        print(f"  Mémoire: {system_metrics.memory_percent:.1f}% ({system_metrics.memory_used_gb:.2f}GB)")
        print(f"  Disque: {system_metrics.disk_percent:.1f}%")
        print(f"  GPU disponible: {system_metrics.gpu_available}")
        
        # Métriques caméra
        camera_metrics = self.observability.get_camera_metrics("demo_camera")
        if camera_metrics:
            print(f"\nCaméra:")
            print(f"  FPS: {camera_metrics.fps:.1f}")
            print(f"  Frames capturées: {camera_metrics.frame_count}")
            print(f"  Temps d'inférence moyen: {camera_metrics.avg_inference_time_ms:.1f}ms")
            print(f"  Queue size: {camera_metrics.queue_size}")
            print(f"  Queue dropped: {camera_metrics.queue_dropped}")
            print(f"  Drop rate: {camera_metrics.queue_drop_rate:.2%}")
            print(f"  Uptime: {camera_metrics.uptime_seconds:.1f}s")
        
        # État de santé final
        print("\n" + "=" * 60)
        self._print_health_status()
        
        print("=" * 60)


def main():
    """Fonction principale."""
    demo = PipelineDemo()
    
    # Démonstration avec webcam (source=0)
    # Pour RTSP: source="rtsp://admin:password@192.168.1.100:554/stream"
    # Pour fichier: source="file:///path/to/video.mp4"
    demo.run_demo(source="0", duration=30)


if __name__ == "__main__":
    sys.exit(main())
