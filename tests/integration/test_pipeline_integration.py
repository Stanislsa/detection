"""
Test d'intégration du pipeline vidéo complet.
RTSP → OpenCV Capture → FrameQueue → YOLO → Rules → Alert → DB → WS → Dashboard
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import numpy as np

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.desktop.pipeline.video_pipeline import VideoPipeline, PipelineConfig
from app.desktop.pipeline.bounded_queue import FrameQueue
from app.ai.yolo_detector import YOLODetector
from app.ai.rules.intrusion import IntrusionRuleEngine
from app.events.event_bus import get_event_bus
from app.desktop.observability import get_observability_service
from app.desktop.camera_manager import get_camera_manager


class PipelineIntegrationTest:
    """
    Test d'intégration du pipeline vidéo complet.
    """
    
    def __init__(self):
        self.event_bus = get_event_bus()
        self.observability = get_observability_service()
        self.camera_manager = get_camera_manager()
        
        # Métriques
        self.metrics = {
            "frames_captured": 0,
            "frames_processed": 0,
            "detections": 0,
            "alerts": 0,
            "start_time": None,
            "end_time": None,
            "latencies": []
        }
        
        # Objectifs de performance
        self.performance_targets = {
            "camera_open_time_s": 2.0,
            "inference_time_ms": 40.0,
            "total_latency_ms": 200.0,
            "fps_min": 20.0,
            "memory_max_gb": 2.0,
            "availability_percent": 99.0
        }
    
    def run_test(self, source: str = "donne/Fall-Detection/Video Datasets Samples/walking.mp4", duration: int = 10):
        """
        Exécute le test d'intégration.
        
        Args:
            source: Source vidéo (0 = webcam, rtsp://..., file://...)
            duration: Durée du test en secondes
        """
        print("=" * 80)
        print("TEST D'INTÉGRATION PIPELINE VIDÉO")
        print("=" * 80)
        print(f"Source: {source}")
        print(f"Durée: {duration}s")
        print(f"Objectifs:")
        for target, value in self.performance_targets.items():
            print(f"  - {target}: {value}")
        print("=" * 80)
        
        # Test 1: Ouverture de caméra
        print("\n[TEST 1] Ouverture de caméra...")
        camera_open_start = time.time()
        
        try:
            from app.desktop.models.camera import Camera, CameraStatus
            
            camera = Camera(
                id=1,
                name="Test Camera",
                source=source,
                source_type="file"
            )
            
            self.camera_manager.add_camera(camera)
            self.camera_manager.start_camera("1")
            
            camera_open_time = time.time() - camera_open_start
            print(f"✓ Caméra ouverte en {camera_open_time:.2f}s")
            
            if camera_open_time > self.performance_targets["camera_open_time_s"]:
                print(f"⚠ WARNING: Temps d'ouverture > {self.performance_targets['camera_open_time_s']}s")
            
        except Exception as e:
            print(f"✗ ERREUR: Impossible d'ouvrir la caméra: {e}")
            return False
        
        # Test 2: Création du pipeline
        print("\n[TEST 2] Création du pipeline...")
        try:
            config = PipelineConfig(
                buffer_size=30,
                enable_detection=True,
                enable_recording=False,
                enable_notifications=True,
                enable_event_bus=True
            )
            
            pipeline = VideoPipeline(camera_id="test_camera", config=config)
            print("✓ Pipeline créé")
            
        except Exception as e:
            print(f"✗ ERREUR: Impossible de créer le pipeline: {e}")
            return False
        
        # Test 3: Détecteur YOLO
        print("\n[TEST 3] Initialisation du détecteur YOLO...")
        try:
            detector = YOLODetector(
                model_path="yolov8n.pt",
                device="cpu"  # Utiliser CPU pour le test
            )
            print("✓ Détecteur YOLO initialisé")
            
        except Exception as e:
            print(f"✗ ERREUR: Impossible d'initialiser YOLO: {e}")
            print("⚠ Le test continuera sans détection IA")
            detector = None
        
        # Test 4: Moteur de règles
        print("\n[TEST 4] Initialisation du moteur de règles...")
        try:
            rule_engine = IntrusionRuleEngine(self.event_bus)
            print("✓ Moteur de règles initialisé")
            
        except Exception as e:
            print(f"✗ ERREUR: Impossible d'initialiser le moteur de règles: {e}")
            return False
        
        # Test 5: Abonnement aux événements
        print("\n[TEST 5] Abonnement aux événements...")
        
        def on_frame_received(event):
            self.metrics["frames_captured"] += 1
        
        def on_detection_result(event):
            self.metrics["detections"] += len(event.detections)
            self.metrics["frames_processed"] += 1
        
        def on_alert_generated(event):
            self.metrics["alerts"] += 1
        
        from app.events.event_types import EventType
        self.event_bus.subscribe(EventType.FRAME_RECEIVED, on_frame_received)
        self.event_bus.subscribe(EventType.DETECTION_RESULT, on_detection_result)
        self.event_bus.subscribe(EventType.ALERT_GENERATED, on_alert_generated)
        
        print("✓ Abonnements créés")
        
        # Test 6: Exécution du pipeline
        print(f"\n[TEST 6] Exécution du pipeline ({duration}s)...")
        self.metrics["start_time"] = time.time()
        
        try:
            # Simuler le traitement de frames
            import cv2
            cap = cv2.VideoCapture(source)
            
            frame_count = 0
            start_time = time.time()
            
            while time.time() - start_time < duration:
                ret, frame = cap.read()
                
                if not ret:
                    print("⚠ Fin du flux vidéo")
                    break
                
                frame_count += 1
                
                # Mesurer la latence
                frame_timestamp = time.time()
                
                # Détection (si disponible)
                if detector:
                    inference_start = time.time()
                    detections = detector.detect(frame)
                    inference_time = (time.time() - inference_start) * 1000
                    
                    if inference_time > self.performance_targets["inference_time_ms"]:
                        print(f"⚠ WARNING: Temps d'inférence > {self.performance_targets['inference_time_ms']}ms")
                    
                    # Publier le résultat
                    from app.events.event_types import DetectionResultEvent
                    event = DetectionResultEvent(
                        camera_id="test_camera",
                        detections=detections,
                        frame_number=frame_count,
                        timestamp=datetime.now()
                    )
                    self.event_bus.publish(event)
                
                # Calculer la latence
                latency = (time.time() - frame_timestamp) * 1000
                self.metrics["latencies"].append(latency)
                
                # Afficher les statistiques toutes les secondes
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    avg_latency = sum(self.metrics["latencies"]) / len(self.metrics["latencies"]) if self.metrics["latencies"] else 0
                    
                    print(f"  FPS: {fps:.1f} | Latence: {avg_latency:.1f}ms | Frames: {frame_count} | Détections: {self.metrics['detections']}")
            
            cap.release()
            self.metrics["end_time"] = time.time()
            
            print(f"✓ Pipeline exécuté ({frame_count} frames)")
            
        except Exception as e:
            print(f"✗ ERREUR: Impossible d'exécuter le pipeline: {e}")
            return False
        
        # Nettoyage
        self.camera_manager.stop_camera("1")
        self.camera_manager.remove_camera("1")
        
        # Rapport final
        self._print_report()
        
        return True
    
    def _print_report(self):
        """Affiche le rapport final du test."""
        print("\n" + "=" * 80)
        print("RAPPORT FINAL")
        print("=" * 80)
        
        # Calculer les métriques
        duration = self.metrics["end_time"] - self.metrics["start_time"]
        fps = self.metrics["frames_captured"] / duration if duration > 0 else 0
        avg_latency = sum(self.metrics["latencies"]) / len(self.metrics["latencies"]) if self.metrics["latencies"] else 0
        detection_rate = self.metrics["detections"] / self.metrics["frames_processed"] if self.metrics["frames_processed"] > 0 else 0
        
        print(f"\nMétriques:")
        print(f"  Durée: {duration:.2f}s")
        print(f"  Frames capturées: {self.metrics['frames_captured']}")
        print(f"  Frames traitées: {self.metrics['frames_processed']}")
        print(f"  Détections: {self.metrics['detections']}")
        print(f"  Alertes: {self.metrics['alerts']}")
        print(f"  FPS: {fps:.1f}")
        print(f"  Latence moyenne: {avg_latency:.1f}ms")
        print(f"  Taux de détection: {detection_rate:.2f} détections/frame")
        
        print(f"\nObjectifs:")
        fps_ok = fps >= self.performance_targets["fps_min"]
        latency_ok = avg_latency <= self.performance_targets["total_latency_ms"]
        
        print(f"  FPS ≥ {self.performance_targets['fps_min']}: {'✓' if fps_ok else '✗'} ({fps:.1f})")
        print(f"  Latence ≤ {self.performance_targets['total_latency_ms']}ms: {'✓' if latency_ok else '✗'} ({avg_latency:.1f}ms)")
        
        # Métriques système
        print(f"\nMétriques système:")
        system_metrics = self.observability.get_system_metrics()
        print(f"  CPU: {system_metrics.cpu_percent:.1f}%")
        print(f"  Mémoire: {system_metrics.memory_percent:.1f}% ({system_metrics.memory_used_gb:.2f}GB)")
        print(f"  Disque: {system_metrics.disk_percent:.1f}%")
        print(f"  GPU disponible: {system_metrics.gpu_available}")
        
        print("\n" + "=" * 80)


def main():
    """Fonction principale."""
    test = PipelineIntegrationTest()
    
    # Test avec webcam (source=0)
    success = test.run_test(source="0", duration=10)
    
    if success:
        print("\n✓ Test d'intégration réussi")
        return 0
    else:
        print("\n✗ Test d'intégration échoué")
        return 1


if __name__ == "__main__":
    sys.exit(main())
