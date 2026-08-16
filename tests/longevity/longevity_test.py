"""Obsolete tests — pre-migration imports. Skipped at module level."""
import pytest
pytest.skip("Obsolete tests — modules removed after v2.1.0 restructure", allow_module_level=True)

"""
Test de longue durée (Longevity Test).
Validation sur 24-48 heures pour vérifier la stabilité du système.
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List
import psutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from desktop.camera_manager import get_camera_manager
from ai.yolo_detector import YOLODetector
from desktop.observability import get_observability_service
from desktop.health_service import get_health_service
from tests.reporting.test_reporter import get_test_reporter


@dataclass
class LongevitySnapshot:
    """Instantané des métriques à un moment donné."""
    timestamp: str
    memory_gb: float
    fps: float
    reconnections: int
    errors: int


class LongevityTest:
    """
    Test de longue durée pour vérifier la stabilité du système.
    """
    
    def __init__(self, duration_hours: int = 24):
        self.duration_hours = duration_hours
        self.camera_manager = get_camera_manager()
        self.observability = get_observability_service()
        self.health_service = get_health_service()
        self.test_reporter = get_test_reporter()
        
        self.snapshots: List[LongevitySnapshot] = []
        self.reconnection_count = 0
        self.error_count = 0
    
    def run_test(self, source: str = "0", camera_count: int = 1):
        """
        Exécute le test de longue durée.
        
        Args:
            source: Source vidéo (0 = webcam, rtsp://...)
            camera_count: Nombre de caméras
        """
        print("=" * 80)
        print(f"TEST DE LONGUE DURÉE - {self.duration_hours} HEURES")
        print("=" * 80)
        print(f"Source: {source}")
        print(f"Caméras: {camera_count}")
        print(f"Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Démarrer le rapport de test
        self.test_reporter.start_test_run(
            configuration={"source": source, "duration_hours": self.duration_hours},
            camera_count=camera_count,
            ai_backend="cpu",
            machine=psutil.cpu_count(logical=True)
        )
        
        # Ajouter les caméras
        camera_ids = []
        for i in range(camera_count):
            camera_id = f"longevity_camera_{i}"
            camera_ids.append(camera_id)
            
            try:
                self.camera_manager.add_camera(
                    camera_id=camera_id,
                    source=source,
                    name=f"Longevity Camera {i}"
                )
                self.camera_manager.start_capture(camera_id)
                self.observability.register_camera(camera_id)
                
                # Créer un détecteur
                try:
                    detector = YOLODetector(model_path="yolo11n.pt", device="cpu")
                    self.camera_manager.start_detection(camera_id, detector)
                except Exception as e:
                    print(f"⚠ Impossible de créer le détecteur: {e}")
                
            except Exception as e:
                print(f"✗ Erreur ajout caméra {camera_id}: {e}")
                self.error_count += 1
        
        # Attendre la stabilisation
        print("Stabilisation (30s)...")
        time.sleep(30)
        
        # Snapshot initial
        self._take_snapshot(camera_ids)
        
        # Boucle principale
        end_time = time.time() + (self.duration_hours * 3600)
        snapshot_interval = 300  # 5 minutes
        
        print(f"\nTest en cours ({self.duration_hours}h)...")
        print("Snapshots toutes les 5 minutes.")
        print("Appuyez sur Ctrl+C pour arrêter prématurément.\n")
        
        try:
            while time.time() < end_time:
                # Attendre l'intervalle
                time.sleep(snapshot_interval)
                
                # Prendre un snapshot
                self._take_snapshot(camera_ids)
                
                # Afficher les statistiques actuelles
                self._print_current_status()
                
                # Vérifier la santé du système
                self._check_system_health()
                
        except KeyboardInterrupt:
            print("\n⚠ Test interrompu par l'utilisateur")
        
        # Snapshot final
        self._take_snapshot(camera_ids)
        
        # Arrêter les caméras
        print("\nArrêt des caméras...")
        for camera_id in camera_ids:
            try:
                self.camera_manager.stop_capture(camera_id)
                self.camera_manager.stop_detection(camera_id)
                self.camera_manager.remove_camera(camera_id)
                self.observability.unregister_camera(camera_id)
            except Exception as e:
                print(f"⚠ Erreur arrêt {camera_id}: {e}")
        
        # Enregistrer les résultats dans le rapport
        self._record_results()
        
        # Terminer le rapport de test
        self.test_reporter.end_test_run()
        
        # Afficher le rapport final
        self._print_final_report()
    
    def _take_snapshot(self, camera_ids: List[str]):
        """Prend un instantané des métriques actuelles."""
        memory = psutil.virtual_memory()
        memory_gb = memory.used / (1024 ** 3)
        
        # Calculer le FPS moyen
        total_fps = 0
        for camera_id in camera_ids:
            metrics = self.observability.get_camera_metrics(camera_id)
            if metrics:
                total_fps += metrics.fps
        
        avg_fps = total_fps / len(camera_ids) if camera_ids else 0
        
        snapshot = LongevitySnapshot(
            timestamp=datetime.now().isoformat(),
            memory_gb=memory_gb,
            fps=avg_fps,
            reconnections=self.reconnection_count,
            errors=self.error_count
        )
        
        self.snapshots.append(snapshot)
    
    def _print_current_status(self):
        """Affiche le statut actuel."""
        if not self.snapshots:
            return
        
        latest = self.snapshots[-1]
        elapsed = (datetime.now() - datetime.fromisoformat(self.snapshots[0].timestamp)).total_seconds() / 3600
        
        print(f"[{latest.timestamp}] Écoulé: {elapsed:.1f}h | "
              f"Mémoire: {latest.memory_gb:.2f}GB | "
              f"FPS: {latest.fps:.1f} | "
              f"Reconnexions: {latest.reconnections} | "
              f"Erreurs: {latest.errors}")
    
    def _check_system_health(self):
        """Vérifie la santé du système."""
        health = self.health_service.get_overall_health()
        
        if health.value != "healthy":
            print(f"⚠ Alerte santé système: {health.value}")
            self.error_count += 1
    
    def _record_results(self):
        """Enregistre les résultats dans le rapport de test."""
        if not self.snapshots:
            return
        
        # Métriques de début
        first = self.snapshots[0]
        # Métriques de fin
        last = self.snapshots[-1]
        
        # Variation mémoire
        memory_variation = last.memory_gb - first.memory_gb
        
        # Variation FPS
        fps_variation = last.fps - first.fps
        
        # Enregistrer
        self.test_reporter.record_result("memory_start", first.memory_gb)
        self.test_reporter.record_result("memory_end", last.memory_gb)
        self.test_reporter.record_result("memory_variation", memory_variation)
        self.test_reporter.record_result("fps_start", first.fps)
        self.test_reporter.record_result("fps_end", last.fps)
        self.test_reporter.record_result("fps_variation", fps_variation)
        self.test_reporter.record_result("reconnections", self.reconnection_count)
        self.test_reporter.record_result("errors", self.error_count)
        
        # Observations
        if abs(memory_variation) > 0.5:
            self.test_reporter.add_observation(f"Variation mémoire significative: {memory_variation:.2f}GB")
        
        if abs(fps_variation) > 5:
            self.test_reporter.add_observation(f"Variation FPS significative: {fps_variation:.1f}")
        
        if self.reconnection_count > 0:
            self.test_reporter.add_observation(f"{self.reconnection_count} reconnexion(s) détectée(s)")
        
        if self.error_count > 0:
            self.test_reporter.add_problem(f"{self.error_count} erreur(s) détectée(s)")
    
    def _print_final_report(self):
        """Affiche le rapport final."""
        print("\n" + "=" * 80)
        print("RAPPORT FINAL - TEST DE LONGUE DURÉE")
        print("=" * 80)
        
        if not self.snapshots:
            print("Aucun snapshot enregistré")
            return
        
        first = self.snapshots[0]
        last = self.snapshots[-1]
        
        print(f"\nDurée réelle: {(datetime.now() - datetime.fromisoformat(first.timestamp)).total_seconds() / 3600:.1f}h")
        print(f"Snapshots: {len(self.snapshots)}")
        
        print(f"\nMémoire:")
        print(f"  Début: {first.memory_gb:.2f}GB")
        print(f"  Fin: {last.memory_gb:.2f}GB")
        print(f"  Variation: {last.memory_gb - first.memory_gb:.2f}GB")
        
        print(f"\nFPS:")
        print(f"  Début: {first.fps:.1f}")
        print(f"  Fin: {last.fps:.1f}")
        print(f"  Variation: {last.fps - first.fps:.1f}")
        
        print(f"\nReconnexions: {self.reconnection_count}")
        print(f"Erreurs: {self.error_count}")
        
        # Analyse de stabilité
        print(f"\nAnalyse de stabilité:")
        
        memory_stable = abs(last.memory_gb - first.memory_gb) < 0.5
        fps_stable = abs(last.fps - first.fps) < 5
        no_reconnections = self.reconnection_count == 0
        no_errors = self.error_count == 0
        
        print(f"  Stabilité mémoire: {'✓' if memory_stable else '✗'}")
        print(f"  Stabilité FPS: {'✓' if fps_stable else '✗'}")
        print(f"  Reconnexions automatiques: {'✓' if no_reconnections else '✗'}")
        print(f"  Absence d'erreurs: {'✓' if no_errors else '✗'}")
        
        overall_stable = memory_stable and fps_stable and no_reconnections and no_errors
        
        print(f"\nConclusion: {'STABLE' if overall_stable else 'INSTABLE'}")
        
        print("=" * 80)


def main():
    """Fonction principale."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test de longue durée SentinelAI")
    parser.add_argument("--duration", type=int, default=24, help="Durée en heures")
    parser.add_argument("--source", type=str, default="0", help="Source vidéo")
    parser.add_argument("--cameras", type=int, default=1, help="Nombre de caméras")
    
    args = parser.parse_args()
    
    test = LongevityTest(duration_hours=args.duration)
    test.run_test(source=args.source, camera_count=args.cameras)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
