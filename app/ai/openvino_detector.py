"""
Détecteur OpenVINO (Intel Neural Compute Stick / CPU Optimized).

Implémente `BaseDetector` pour les modèles YOLO convertis en IR OpenVINO
(`.xml` + `.bin`). Ce module est chargé en lazy-import depuis
`app.ai.scheduler.inference_scheduler` lorsque le backend sélectionné
est `OPENVINO` ; il n'est donc pas requis pour les installations qui
n'utilisent pas OpenVINO.
"""

from typing import List, Dict, Any, Optional
import numpy as np

try:
    from openvino.runtime import Core as OVCore
    OPENVINO_AVAILABLE = True
except ImportError:  # pragma: no cover - import optionnel
    OPENVINO_AVAILABLE = False

from app.ai.base_detector import BaseDetector
from app.desktop.workers.detection_worker import DetectionResult
from app.core.logger import get_logger
from app.core.exceptions import DetectionException


class OpenVINODetector(BaseDetector):
    """
    Détecteur utilisant OpenVINO IR.

    Args:
        model_path: Chemin vers le fichier `.xml` du modèle IR (le `.bin`
            adjacent doit se trouver dans le même répertoire).
        confidence_threshold: Seuil de confiance par défaut.
        device: Périphérique OpenVINO cible (`CPU`, `GPU`, `AUTO`, `NPU`, ...).
        input_shape: Forme d'entrée `(N, C, H, W)`. Si `None`, OpenVINO
            lit la forme depuis le modèle.
    """

    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.5,
        device: str = "CPU",
        input_shape: Optional[tuple] = None,
    ):
        super().__init__(model_path=model_path, confidence_threshold=confidence_threshold)
        self.device = device
        self.input_shape = input_shape
        self._core: Optional[OVCore] = None
        self._compiled_model = None
        self._input_tensor_name: Optional[str] = None
        self._output_tensor_name: Optional[str] = None

    # ------------------------------------------------------------------ utils
    def _ensure_path(self) -> str:
        """Vérifie que `model_path` pointe vers un `.xml` existant."""
        if not self.model_path:
            raise DetectionException("OpenVINODetector: model_path (XML) requis")
        if not self.model_path.lower().endswith(".xml"):
            raise DetectionException(
                f"OpenVINODetector: model_path doit finir par .xml, reçu: {self.model_path}"
            )
        return self.model_path

    # ----------------------------------------------------------- BaseDetector
    def load_model(self) -> bool:
        """Charge le modèle IR et compile pour le device cible."""
        if not OPENVINO_AVAILABLE:
            raise DetectionException(
                "OpenVINO n'est pas installé. `pip install openvino`."
            )

        xml_path = self._ensure_path()

        try:
            self._logger.info(f"Chargement OpenVINO IR: {xml_path} (device={self.device})")
            self._core = OVCore()
            model = self._core.read_model(model=xml_path)
            self._compiled_model = self._core.compile_model(model=model, device_name=self.device)

            # Récupère noms d'entrée/sortie du premier port
            input_port = self._compiled_model.input(0)
            output_port = self._compiled_model.output(0)
            self._input_tensor_name = input_port.any_name
            self._output_tensor_name = output_port.any_name

            self._model = self._compiled_model
            self._is_loaded = True
            self._logger.info("Modèle OpenVINO chargé et compilé OK")
            return True
        except Exception as e:
            self._logger.error(f"Erreur chargement OpenVINO: {e}")
            raise DetectionException(f"Erreur chargement OpenVINO: {e}")

    def detect(
        self,
        frame: np.ndarray,
        confidence_threshold: Optional[float] = None,
    ) -> List[DetectionResult]:
        """Exécute l'inférence sur `frame` et retourne les `DetectionResult`."""
        if not self._is_loaded:
            self._logger.warning("Modèle non chargé, chargement...")
            self.load_model()

        threshold = confidence_threshold if confidence_threshold is not None else self.confidence_threshold
        if self._compiled_model is None or self._input_tensor_name is None:
            raise DetectionException("OpenVINODetector: modèle non initialisé")

        try:
            input_tensor = self.preprocess(frame)
            result = self._compiled_model(
                {self._input_tensor_name: input_tensor}
            )[self._output_tensor_name]
            return self.postprocess(result, frame_shape=frame.shape[:2])
        except Exception as e:
            self._logger.error(f"Erreur inférence OpenVINO: {e}")
            raise DetectionException(f"Erreur inférence OpenVINO: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """Retourne des informations sur le modèle chargé."""
        info: Dict[str, Any] = {
            "backend": "openvino",
            "model_path": self.model_path,
            "device": self.device,
            "is_loaded": self._is_loaded,
            "input_tensor": self._input_tensor_name,
            "output_tensor": self._output_tensor_name,
        }
        if self._compiled_model is not None and self.input_shape is None:
            try:
                shape = self._compiled_model.input(0).partial_shape
                info["input_shape"] = [dim if dim.is_static else -1 for dim in shape]
            except Exception:  # pragma: no cover
                pass
        return info

    # ---------------------------------------------------- preprocess / postproc
    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Prépare un tenseur NCHW normalisé [0,1] pour OpenVINO.

        Le modèle fine-tuné `yolo11n` exporté en OpenVINO attend
        classiquement `1x3xHxW` en FP32. Cette implémentation:
          - redimensionne à 640x640 (taille d'entraînement)
          - convertit BGR→RGB
          - normalise [0, 255] → [0.0, 1.0]
          - transpose HWC → CHW
        """
        if frame is None or frame.size == 0:
            raise DetectionException("OpenVINODetector.preprocess: frame vide")

        # Import cv2 ici pour éviter d'imposer opencv-python aux environnements
        # n'utilisant pas OpenVINO (cohérent avec l'import lazy plus haut).
        import cv2  # local import

        resized = cv2.resize(frame, (640, 640))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB) if resized.shape[2] == 3 else resized
        normalized = rgb.astype(np.float32) / 255.0
        chw = np.transpose(normalized, (2, 0, 1))
        return np.expand_dims(chw, axis=0)

    def postprocess(self, raw_results: Any, frame_shape: tuple) -> List[DetectionResult]:
        """
        Convertit la sortie OpenVINO YOLO en `DetectionResult`.

        Format attendu : `(1, 84, 8400)` pour YOLOv8/v11 (4 box + 80 classes).
        Pour un modèle fine-tuné à 2 classes, la sortie est
        `(1, 6, 8400)` (4 box + 2 classes).
        """
        if raw_results is None:
            return []

        arr = np.asarray(raw_results)
        # Ultralytics exporte souvent en (1, N, dets) ; on transpose si besoin.
        if arr.ndim == 3 and arr.shape[0] == 1:
            arr = arr[0]
        if arr.ndim == 2 and arr.shape[0] < arr.shape[1]:
            arr = arr.T  # (detections, features)

        results: List[DetectionResult] = []
        h, w = frame_shape[:2]
        for det in arr:
            if det.size < 6:
                continue
            cx, cy, bw, bh = float(det[0]), float(det[1]), float(det[2]), float(det[3])
            class_scores = det[4:]
            class_id = int(np.argmax(class_scores))
            confidence = float(class_scores[class_id])
            if confidence < self.confidence_threshold:
                continue

            # Reconvertit centre/largeur en coin supérieur gauche
            x1 = int(max(0, (cx - bw / 2.0) * w / 640))
            y1 = int(max(0, (cy - bh / 2.0) * h / 640))
            ww = int(min(w - x1, bw * w / 640))
            hh = int(min(h - y1, bh * h / 640))

            results.append(
                DetectionResult(
                    class_id=class_id,
                    class_name=str(class_id),
                    confidence=confidence,
                    bbox=(x1, y1, ww, hh),
                )
            )
        return results