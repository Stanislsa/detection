"""
Ordonnanceur d'inférence IA.
Sélectionne automatiquement le backend optimal (CPU/OpenVINO/CUDA/DirectML).
"""

from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
import platform
import subprocess

from app.core.logger import get_logger


class InferenceBackend(Enum):
    """Backends d'inférence disponibles."""
    CPU = "cpu"
    OPENVINO = "openvino"
    CUDA = "cuda"
    DIRECTML = "directml"
    AUTO = "auto"


@dataclass
class BackendCapabilities:
    """Capacités d'un backend."""
    backend: InferenceBackend
    available: bool = False
    device_name: str = ""
    memory_gb: float = 0.0
    compute_capability: str = ""
    priority: int = 0  # Plus élevé = priorité plus haute


class InferenceScheduler:
    """
    Ordonnanceur d'inférence avec sélection automatique du backend.
    Détecte les backends disponibles et sélectionne le meilleur.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._logger = get_logger(__name__)
            self._backends: Dict[InferenceBackend, BackendCapabilities] = {}
            self._preferred_backend: Optional[InferenceBackend] = None
            self._initialized = True
            self._detect_backends()
    
    def _detect_backends(self):
        """Détecte les backends disponibles."""
        self._logger.info("Détection des backends d'inférence...")
        
        # CPU (toujours disponible)
        self._backends[InferenceBackend.CPU] = BackendCapabilities(
            backend=InferenceBackend.CPU,
            available=True,
            device_name=platform.processor() or "CPU",
            priority=1
        )
        
        # OpenVINO
        self._detect_openvino()
        
        # CUDA (NVIDIA)
        self._detect_cuda()
        
        # DirectML (Windows)
        self._detect_directml()
        
        # Sélectionner le backend préféré
        self._select_preferred_backend()
        
        self._logger.info(f"Backends détectés: {[b for b, cap in self._backends.items() if cap.available]}")
        self._logger.info(f"Backend préféré: {self._preferred_backend.value if self._preferred_backend else 'None'}")
    
    def _detect_openvino(self):
        """Détecte si OpenVINO est disponible."""
        try:
            import openvino as ov
            
            # Lister les appareils disponibles
            core = ov.Core()
            devices = core.available_devices
            
            if devices:
                # Trouver le meilleur appareil (GPU > NPU > CPU)
                device_name = "CPU"
                for device in devices:
                    if "GPU" in device.upper():
                        device_name = device
                        break
                    elif "NPU" in device.upper():
                        device_name = device
                        break
                
                self._backends[InferenceBackend.OPENVINO] = BackendCapabilities(
                    backend=InferenceBackend.OPENVINO,
                    available=True,
                    device_name=device_name,
                    priority=3  # Priorité élevée
                )
                self._logger.info(f"OpenVINO détecté: {device_name}")
            else:
                self._backends[InferenceBackend.OPENVINO] = BackendCapabilities(
                    backend=InferenceBackend.OPENVINO,
                    available=False,
                    priority=3
                )
                
        except ImportError:
            self._backends[InferenceBackend.OPENVINO] = BackendCapabilities(
                backend=InferenceBackend.OPENVINO,
                available=False,
                priority=3
            )
            self._logger.debug("OpenVINO non disponible")
    
    def _detect_cuda(self):
        """Détecte si CUDA (NVIDIA) est disponible."""
        try:
            import torch
            
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0) if device_count > 0 else "CUDA"
                memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
                
                self._backends[InferenceBackend.CUDA] = BackendCapabilities(
                    backend=InferenceBackend.CUDA,
                    available=True,
                    device_name=device_name,
                    memory_gb=memory_gb,
                    compute_capability=str(torch.cuda.get_device_capability(0)),
                    priority=5  # Priorité la plus élevée
                )
                self._logger.info(f"CUDA détecté: {device_name} ({memory_gb:.2f}GB)")
            else:
                self._backends[InferenceBackend.CUDA] = BackendCapabilities(
                    backend=InferenceBackend.CUDA,
                    available=False,
                    priority=5
                )
                
        except ImportError:
            self._backends[InferenceBackend.CUDA] = BackendCapabilities(
                backend=InferenceBackend.CUDA,
                available=False,
                priority=5
            )
            self._logger.debug("CUDA non disponible")
    
    def _detect_directml(self):
        """Détecte si DirectML est disponible (Windows)."""
        if platform.system() != "Windows":
            self._backends[InferenceBackend.DIRECTML] = BackendCapabilities(
                backend=InferenceBackend.DIRECTML,
                available=False,
                priority=4
            )
            return
        
        try:
            import torch
            
            # Vérifier si DirectML est disponible via torch-directml
            try:
                import torch_directml
                device = torch_directml.device()
                
                self._backends[InferenceBackend.DIRECTML] = BackendCapabilities(
                    backend=InferenceBackend.DIRECTML,
                    available=True,
                    device_name="DirectML",
                    priority=4
                )
                self._logger.info("DirectML détecté")
                
            except ImportError:
                self._backends[InferenceBackend.DIRECTML] = BackendCapabilities(
                    backend=InferenceBackend.DIRECTML,
                    available=False,
                    priority=4
                )
                self._logger.debug("DirectML non disponible")
                
        except ImportError:
            self._backends[InferenceBackend.DIRECTML] = BackendCapabilities(
                backend=InferenceBackend.DIRECTML,
                available=False,
                priority=4
            )
    
    def _select_preferred_backend(self):
        """Sélectionne le backend préféré basé sur la priorité."""
        available_backends = [
            (backend, cap)
            for backend, cap in self._backends.items()
            if cap.available
        ]
        
        if not available_backends:
            self._preferred_backend = InferenceBackend.CPU
            self._logger.warning("Aucun backend détecté, utilisation du CPU")
            return
        
        # Trier par priorité
        available_backends.sort(key=lambda x: x[1].priority, reverse=True)
        self._preferred_backend = available_backends[0][0]
    
    def get_preferred_backend(self) -> InferenceBackend:
        """
        Retourne le backend préféré.
        
        Returns:
            Backend préféré
        """
        return self._preferred_backend or InferenceBackend.CPU
    
    def get_backend(self, backend: InferenceBackend) -> Optional[BackendCapabilities]:
        """
        Retourne les capacités d'un backend.
        
        Args:
            backend: Backend à interroger
        
        Returns:
            Capacités ou None
        """
        return self._backends.get(backend)
    
    def get_available_backends(self) -> List[InferenceBackend]:
        """
        Retourne la liste des backends disponibles.
        
        Returns:
            Liste des backends disponibles
        """
        return [
            backend
            for backend, cap in self._backends.items()
            if cap.available
        ]
    
    def set_preferred_backend(self, backend: InferenceBackend) -> bool:
        """
        Force le backend préféré.
        
        Args:
            backend: Backend à utiliser
        
        Returns:
            True si succès
        """
        if backend not in self._backends:
            self._logger.error(f"Backend inconnu: {backend}")
            return False
        
        if not self._backends[backend].available:
            self._logger.warning(f"Backend {backend} non disponible")
            return False
        
        self._preferred_backend = backend
        self._logger.info(f"Backend préféré changé: {backend.value}")
        return True
    
    def create_detector(self, backend: Optional[InferenceBackend] = None, model_path: str = ""):
        """
        Crée un détecteur avec le backend spécifié.
        
        Args:
            backend: Backend à utiliser (AUTO si None)
            model_path: Chemin du modèle
        
        Returns:
            Instance du détecteur
        """
        if backend is None or backend == InferenceBackend.AUTO:
            backend = self.get_preferred_backend()
        
        # Importer le détecteur approprié
        if backend == InferenceBackend.OPENVINO:
            from app.ai.openvino_detector import OpenVINODetector
            return OpenVINODetector(model_path=model_path, device="GPU" if "GPU" in self._backends[backend].device_name else "CPU")
        
        elif backend == InferenceBackend.CUDA:
            from app.ai.yolo_detector import YOLODetector
            return YOLODetector(model_path=model_path, device="cuda")
        
        elif backend == InferenceBackend.DIRECTML:
            from app.ai.yolo_detector import YOLODetector
            return YOLODetector(model_path=model_path, device="directml")
        
        else:  # CPU
            from app.ai.yolo_detector import YOLODetector
            return YOLODetector(model_path=model_path, device="cpu")
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Retourne les informations système sur les backends.
        
        Returns:
            Dictionnaire d'informations
        """
        return {
            "preferred_backend": self._preferred_backend.value if self._preferred_backend else "none",
            "available_backends": [b.value for b in self.get_available_backends()],
            "backends": {
                backend.value: {
                    "available": cap.available,
                    "device_name": cap.device_name,
                    "memory_gb": cap.memory_gb,
                    "priority": cap.priority
                }
                for backend, cap in self._backends.items()
            }
        }


def get_inference_scheduler() -> InferenceScheduler:
    """
    Fonction utilitaire pour récupérer l'InferenceScheduler.
    
    Returns:
        Instance singleton du InferenceScheduler
    """
    return InferenceScheduler()
