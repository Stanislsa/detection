"""
Service d'entraînement YOLO.
Gère l'entraînement, le suivi et l'export des modèles.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import threading
import json

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

from app.core.logger import get_logger


@dataclass
class TrainingConfig:
    """Configuration d'entraînement."""
    dataset_path: str
    data_yaml: str
    model_name: str = "yolo11n.pt"
    epochs: int = 100
    imgsz: int = 640
    batch: int = 16
    optimizer: str = "Adam"
    lr0: float = 0.001
    patience: int = 10
    device: str = "cpu"
    project: str = "models"
    name: str = "trained_model"
    save: bool = True
    verbose: bool = True


@dataclass
class TrainingMetrics:
    """Métriques d'entraînement."""
    epoch: int
    loss: float
    mAP50: float
    mAP50_95: float
    precision: float
    recall: float
    learning_rate: float


class TrainingService:
    """
    Service d'entraînement YOLO.
    """
    
    def __init__(self):
        self._logger = get_logger(__name__)
        self._model: Optional[YOLO] = None
        self._is_training = False
        self._training_thread: Optional[threading.Thread] = None
        self._progress_callback: Optional[Callable[[int, int], None]] = None
        self._metrics_callback: Optional[Callable[TrainingMetrics, None]] = None
        self._log_callback: Optional[Callable[str, None]] = None
    
    def set_callbacks(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        metrics_callback: Optional[Callable[TrainingMetrics, None]] = None,
        log_callback: Optional[Callable[str, None]] = None
    ):
        """
        Définit les callbacks pour le suivi de l'entraînement.
        
        Args:
            progress_callback: Callback progression (current, total)
            metrics_callback: Callback métriques (TrainingMetrics)
            log_callback: Callback logs (message)
        """
        self._progress_callback = progress_callback
        self._metrics_callback = metrics_callback
        self._log_callback = log_callback
    
    def start_training(self, config: TrainingConfig) -> bool:
        """
        Démarre l'entraînement.
        
        Args:
            config: Configuration d'entraînement
        
        Returns:
            True si démarré avec succès
        """
        if not YOLO_AVAILABLE:
            self._logger.error("Ultralytics YOLO non installé")
            if self._log_callback:
                self._log_callback("Erreur: Ultralytics YOLO non installé")
            return False
        
        if self._is_training:
            self._logger.warning("Un entraînement est déjà en cours")
            if self._log_callback:
                self._log_callback("Erreur: Un entraînement est déjà en cours")
            return False
        
        # Vérifier le dataset
        dataset_path = Path(config.dataset_path)
        if not dataset_path.exists():
            self._logger.error(f"Dataset introuvable: {config.dataset_path}")
            if self._log_callback:
                self._log_callback(f"Erreur: Dataset introuvable: {config.dataset_path}")
            return False
        
        # Lancer l'entraînement dans un thread séparé
        self._training_thread = threading.Thread(
            target=self._train_thread,
            args=(config,),
            daemon=True
        )
        self._training_thread.start()
        
        return True
    
    def _train_thread(self, config: TrainingConfig):
        """Thread d'entraînement."""
        try:
            self._is_training = True
            
            if self._log_callback:
                self._log_callback(f"Chargement du modèle: {config.model_name}")
            
            # Charger le modèle
            self._model = YOLO(config.model_name)
            
            if self._log_callback:
                self._log_callback("Modèle chargé avec succès")
                self._log_callback(f"Début de l'entraînement: {config.epochs} epochs")
            
            # Enregistrer le callback d'epoch
            self._model.add_callback("on_train_epoch_end", self._on_epoch_end)
            
            # Entraîner
            results = self._model.train(
                data=config.data_yaml,
                epochs=config.epochs,
                imgsz=config.imgsz,
                batch=config.batch,
                optimizer=config.optimizer,
                lr0=config.lr0,
                patience=config.patience,
                device=config.device,
                project=config.project,
                name=config.name,
                save=config.save,
                verbose=config.verbose
            )
            
            if self._log_callback:
                self._log_callback("Entraînement terminé avec succès")
                self._log_callback(f"Modèle sauvegardé dans: {results.save_dir}")
            
        except Exception as e:
            self._logger.error(f"Erreur lors de l'entraînement: {e}")
            if self._log_callback:
                self._log_callback(f"Erreur: {e}")
        
        finally:
            self._is_training = False
    
    def _on_epoch_end(self, trainer):
        """Callback à la fin de chaque epoch."""
        try:
            # Récupérer les métriques
            metrics = trainer.metrics
            
            # Créer l'objet de métriques
            training_metrics = TrainingMetrics(
                epoch=trainer.epoch,
                loss=metrics.get("loss", 0.0),
                mAP50=metrics.get("metrics/mAP50(B)", 0.0),
                mAP50_95=metrics.get("metrics/mAP50-95(B)", 0.0),
                precision=metrics.get("metrics/precision(B)", 0.0),
                recall=metrics.get("metrics/recall(B)", 0.0),
                learning_rate=trainer.optimizer.param_groups[0]['lr']
            )
            
            # Appeler le callback de progression
            if self._progress_callback:
                self._progress_callback(trainer.epoch, trainer.epochs)
            
            # Appeler le callback de métriques
            if self._metrics_callback:
                self._metrics_callback(training_metrics)
            
            # Log
            if self._log_callback:
                self._log_callback(
                    f"Epoch {trainer.epoch}/{trainer.epochs} - "
                    f"Loss: {training_metrics.loss:.4f} - "
                    f"mAP50: {training_metrics.mAP50:.4f} - "
                    f"mAP50-95: {training_metrics.mAP50_95:.4f}"
                )
            
        except Exception as e:
            self._logger.error(f"Erreur callback epoch: {e}")
    
    def stop_training(self):
        """Arrête l'entraînement en cours."""
        if self._is_training and self._model:
            self._logger.info("Arrêt de l'entraînement demandé")
            if self._log_callback:
                self._log_callback("Arrêt de l'entraînement...")
            
            # YOLO ne supporte pas l'arrêt propre, on marque simplement comme arrêté
            self._is_training = False
    
    def is_training(self) -> bool:
        """
        Retourne si un entraînement est en cours.
        
        Returns:
            True si entraînement en cours
        """
        return self._is_training
    
    def export_model(
        self,
        model_path: str,
        format: str = "onnx",
        output_path: Optional[str] = None
    ) -> bool:
        """
        Exporte le modèle entraîné.
        
        Args:
            model_path: Chemin vers le modèle entraîné
            format: Format d'export (onnx, openvino, torchscript)
            output_path: Chemin de sortie (optionnel)
        
        Returns:
            True si export réussi
        """
        try:
            if not YOLO_AVAILABLE:
                self._logger.error("Ultralytics YOLO non installé")
                return False
            
            # Charger le modèle
            model = YOLO(model_path)
            
            if self._log_callback:
                self._log_callback(f"Export du modèle vers {format}...")
            
            # Exporter
            model.export(format=format)
            
            if self._log_callback:
                self._log_callback(f"Export {format} réussi")
            
            return True
            
        except Exception as e:
            self._logger.error(f"Erreur export modèle: {e}")
            if self._log_callback:
                self._log_callback(f"Erreur export: {e}")
            return False
    
    def get_available_models(self) -> list:
        """
        Retourne la liste des modèles pré-entraînés disponibles.
        
        Returns:
            Liste des noms de modèles
        """
        return [
            "yolo11n.pt",  # Nano
            "yolo11s.pt",  # Small
            "yolo11m.pt",  # Medium
            "yolo11l.pt",  # Large
            "yolo11x.pt",  # Extra Large
            "yolov8n.pt",
            "yolov8s.pt",
            "yolov8m.pt",
            "yolov8l.pt",
            "yolov8x.pt"
        ]
    
    def validate_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """
        Valide la structure du dataset.
        
        Args:
            dataset_path: Chemin vers le dataset
        
        Returns:
            Dictionnaire avec les résultats de validation
        """
        path = Path(dataset_path)
        
        result = {
            "valid": False,
            "errors": [],
            "warnings": []
        }
        
        # Vérifier l'existence
        if not path.exists():
            result["errors"].append(f"Dataset introuvable: {dataset_path}")
            return result
        
        # Vérifier data.yaml
        data_yaml = path / "data.yaml"
        if not data_yaml.exists():
            result["errors"].append("data.yaml introuvable")
        else:
            result["data_yaml"] = str(data_yaml)
        
        # Vérifier les dossiers
        required_dirs = ["train", "valid"]
        for dir_name in required_dirs:
            dir_path = path / dir_name
            if not dir_path.exists():
                result["errors"].append(f"Dossier {dir_name} introuvable")
            else:
                images_dir = dir_path / "images"
                if not images_dir.exists():
                    result["errors"].append(f"Dossier {dir_name}/images introuvable")
                else:
                    image_count = len(list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")))
                    result[f"{dir_name}_images"] = image_count
                    
                    if image_count == 0:
                        result["warnings"].append(f"Aucune image dans {dir_name}/images")
        
        # Vérifier test (optionnel)
        test_dir = path / "test"
        if test_dir.exists():
            test_images = test_dir / "images"
            if test_images.exists():
                image_count = len(list(test_images.glob("*.jpg")) + list(test_images.glob("*.png")))
                result["test_images"] = image_count
        
        result["valid"] = len(result["errors"]) == 0
        
        return result


def get_training_service() -> TrainingService:
    """
    Fonction utilitaire pour récupérer le TrainingService.
    
    Returns:
        Instance singleton du TrainingService
    """
    if not hasattr(get_training_service, "_instance"):
        get_training_service._instance = TrainingService()
    return get_training_service._instance
