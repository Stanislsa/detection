"""
Test de montée en charge (Load Test).
Mesure les performances avec 1, 2, 4, 8 caméras simultanées.
"""

import sys
import time
import threading
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict
import psutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.desktop.camera_manager import get_camera_manager
from app.ai.yolo_detector import YOLODetector
from app.desktop.observability import get_observability_service


@dataclass
class LoadTestResult:
    """Résultats d'un test de charge."""
    camera_count: int
    duration: int
    fps_total: float
    fps_per_camera: float
    avg_inference_time_ms: float
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    gpu_percent: float
    gpu_available: bool
    total_queue_dropped: int
    drop_rate: float
    avg_latency_ms: float


class LoadTest:
    """
    Test de montée en charge multi-caméras.
    """
    
    def __init__(self):
        self.camera_manager = get_camera_manager()
        self.observability = get_observability_service()
        self.results: List[LoadTestResult] = []
        
        # Sources de test (webcams ou fichiers)
        self.sources = ["0"]  # Utiliser la webcam par défaut
    
    def run_load_test(self, camera_counts: List[int] = [1, 2, 4, 8], duration: int = 30):
        """
        Exécute les tests de charge.
        
        Args:
            camera_counts: Liste des nombres de caméras à tester
            duration: Durée de chaque test en secondes
        """
        print("=" * 80)
        print("TEST DE MONTÉE EN CHARGE")
        print("=" * 80)
        print(f"Durée par test: {duration}s")
        print(f"Configurations: {camera_counts} caméras")
        print("=" * 80)
        
        for camera_count in camera_counts:
            print(f"\n{'=' * 80}")
            print(f"TEST AVEC {camera_count} CAMÉRA(S)")
            print(f"{'=' * 80}")
            
            result = self._run_single_test(camera_count, duration)
            self.results.append(result)
            
            self._print_result(result)
            
            # Nettoyage
            self._cleanup()
            
            # Pause entre les tests
            if camera_count != camera_counts[-1]:
                print(f"\nPause de 10s avant le test suivant...")
                time.sleep(10)
        
        # Résumé final
        self._print_summary()
    
    def _run_single_test(self, camera_count: int, duration: int) -> LoadTestResult:
        """
        Exécute un test avec un nombre spécifique de caméras.
        
        Args:
            camera_count: Nombre de caméras
            duration: Durée du test en secondes
        
        Returns:
            Résultats du test
        """
        # Créer les caméras
        camera_ids = []
        for i in range(camera_count):
            camera_id = f"load_test_camera_{i}"
            camera_ids.append(camera_id)
            
            # Utiliser différentes sources si disponibles
            source = self.sources[i % len(self.sources)]
            
            self.camera_manager.add_camera(
                camera_id=camera_id,
                source=source,
                name=f"Load Test Camera {i}"
            )
            
            # Enregistrer pour l'observabilité
            self.observability.register_camera(camera_id)
        
        # Créer un détecteur partagé
        try:
            detector = YOLODetector(
                model_path="yolo11n.pt",
                device="cpu"
            )
        except Exception as e:
            print(f"⚠ Impossible de créer le détecteur: {e}")
            detector = None
        
        # Démarrer toutes les caméras
        print(f"Démarrage de {camera_count} caméras...")
        for camera_id in camera_ids:
            try:
                self.camera_manager.start_capture(camera_id)
                if detector:
                    self.camera_manager.start_detection(camera_id, detector)
            except Exception as e:
                print(f"⚠ Erreur démarrage {camera_id}: {e}")
        
        # Attendre la stabilisation
        print("Stabilisation (5s)...")
        time.sleep(5)
        
        # Mesurer les métriques
        print(f"Mesure des métriques ({duration}s)...")
        start_time = time.time()
        
        # Collecter les métriques périodiquement
        cpu_samples = []
        memory_samples = []
        
        while time.time() - start_time < duration:
            # Métriques système
            cpu_samples.append(psutil.cpu_percent(interval=0.1))
            memory = psutil.virtual_memory()
            memory_samples.append(memory.percent)
            
            time.sleep(1)
        
        # Arrêter toutes les caméras
        print("Arrêt des caméras...")
        for camera_id in camera_ids:
            try:
                self.camera_manager.stop_capture(camera_id)
                self.camera_manager.stop_detection(camera_id)
            except Exception as e:
                print(f"⚠ Erreur arrêt {camera_id}: {e}")
        
        # Collecter les métriques finales
        system_metrics = self.observability.get_system_metrics()
        
        # Calculer les métriques par caméra
        total_fps = 0
        total_inference_time = 0
        total_queue_dropped = 0
        total_frames = 0
        total_dropped = 0
        
        for camera_id in camera_ids:
            camera_metrics = self.observability.get_camera_metrics(camera_id)
            if camera_metrics:
                total_fps += camera_metrics.fps
                total_inference_time += camera_metrics.avg_inference_time_ms
                total_queue_dropped += camera_metrics.queue_dropped
                total_frames += camera_metrics.frame_count
                total_dropped += camera_metrics.queue_dropped
        
        # Calculer les moyennes
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        avg_memory = sum(memory_samples) / len(memory_samples) if memory_samples else 0
        avg_inference_time = total_inference_time / camera_count if camera_count > 0 else 0
        fps_per_camera = total_fps / camera_count if camera_count > 0 else 0
        drop_rate = total_dropped / (total_frames + total_dropped) if (total_frames + total_dropped) > 0 else 0
        
        # Créer le résultat
        result = LoadTestResult(
            camera_count=camera_count,
            duration=duration,
            fps_total=total_fps,
            fps_per_camera=fps_per_camera,
            avg_inference_time_ms=avg_inference_time,
            cpu_percent=avg_cpu,
            memory_percent=avg_memory,
            memory_used_gb=system_metrics.memory_used_gb,
            gpu_percent=system_metrics.gpu_percent,
            gpu_available=system_metrics.gpu_available,
            total_queue_dropped=total_queue_dropped,
            drop_rate=drop_rate,
            avg_latency_ms=avg_inference_time  # Approximation
        )
        
        return result
    
    def _cleanup(self):
        """Nettoie les caméras après un test."""
        camera_ids = [f"load_test_camera_{i}" for i in range(10)]  # Max 10
        
        for camera_id in camera_ids:
            try:
                self.camera_manager.remove_camera(camera_id)
                self.observability.unregister_camera(camera_id)
            except:
                pass
    
    def _print_result(self, result: LoadTestResult):
        """Affiche les résultats d'un test."""
        print(f"\nRésultats pour {result.camera_count} caméra(s):")
        print(f"  FPS total: {result.fps_total:.1f}")
        print(f"  FPS par caméra: {result.fps_per_camera:.1f}")
        print(f"  Temps d'inférence moyen: {result.avg_inference_time_ms:.1f}ms")
        print(f"  CPU: {result.cpu_percent:.1f}%")
        print(f"  Mémoire: {result.memory_percent:.1f}% ({result.memory_used_gb:.2f}GB)")
        print(f"  GPU: {result.gpu_percent:.1f}% (disponible: {result.gpu_available})")
        print(f"  Frames supprimées: {result.total_queue_dropped}")
        print(f"  Taux de suppression: {result.drop_rate:.2%}")
        print(f"  Latence moyenne: {result.avg_latency_ms:.1f}ms")
    
    def _print_summary(self):
        """Affiche le résumé de tous les tests."""
        print("\n" + "=" * 80)
        print("RÉSUMÉ DES TESTS DE CHARGE")
        print("=" * 80)
        
        print(f"\n{'Caméras':<10} {'FPS Total':<12} {'FPS/Cam':<10} {'Inférence(ms)':<15} {'CPU(%)':<10} {'Mémoire(GB)':<12} {'Drop(%)':<10}")
        print("-" * 80)
        
        for result in self.results:
            print(f"{result.camera_count:<10} {result.fps_total:<12.1f} {result.fps_per_camera:<10.1f} "
                  f"{result.avg_inference_time_ms:<15.1f} {result.cpu_percent:<10.1f} "
                  f"{result.memory_used_gb:<12.2f} {result.drop_rate:<10.2%}")
        
        print("=" * 80)
        
        # Analyse de la scalabilité
        if len(self.results) >= 2:
            print("\nAnalyse de la scalabilité:")
            
            # Comparaison 1 vs 8 caméras
            result_1 = next((r for r in self.results if r.camera_count == 1), None)
            result_8 = next((r for r in self.results if r.camera_count == 8), None)
            
            if result_1 and result_8:
                fps_ratio = result_8.fps_total / result_1.fps_total if result_1.fps_total > 0 else 0
                cpu_ratio = result_8.cpu_percent / result_1.cpu_percent if result_1.cpu_percent > 0 else 0
                memory_ratio = result_8.memory_used_gb / result_1.memory_used_gb if result_1.memory_used_gb > 0 else 0
                
                print(f"  FPS (1→8 caméras): {fps_ratio:.2f}x (idéal: 8x)")
                print(f"  CPU (1→8 caméras): {cpu_ratio:.2f}x")
                print(f"  Mémoire (1→8 caméras): {memory_ratio:.2f}x")
                
                if fps_ratio >= 6:
                    print("  ✓ Scalabilité FPS: Excellente")
                elif fps_ratio >= 4:
                    print("  ⚠ Scalabilité FPS: Bonne")
                else:
                    print("  ✗ Scalabilité FPS: Insuffisante")
        
        print("=" * 80)


def main():
    """Fonction principale."""
    test = LoadTest()
    
    # Tests avec 1, 2, 4, 8 caméras
    # Note: Pour 8 caméras, il faut 8 sources différentes (webcams ou fichiers RTSP)
    test.run_load_test(camera_counts=[1, 2, 4], duration=30)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
