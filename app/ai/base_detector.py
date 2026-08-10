"""
Interface de base pour les détecteurs IA.
Permet de facilement remplacer ou ajouter de nouveaux modèles.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

from app.desktop.workers.detection_worker import DetectionResult
from app.core.logger import get_logger


class BaseDetector(ABC):
    """
    Classe de base pour tous les détecteurs IA.
    Définit l'interface commune que tous les détecteurs doivent implémenter.
    """
    
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        """
        Initialise le détecteur.
        
        Args:
            model_path: Chemin vers le modèle (optionnel)
            confidence_threshold: Seuil de confiance par défaut
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self._model = None
        self._is_loaded = False
        self._logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def load_model(self) -> bool:
        """
        Charge le modèle IA.
        
        Returns:
            True si succès
        """
        pass
    
    @abstractmethod
    def detect(self, frame: np.ndarray, confidence_threshold: Optional[float] = None) -> List[DetectionResult]:
        """
        Effectue la détection sur un frame.
        
        Args:
            frame: Frame à analyser
            confidence_threshold: Seuil de confiance (utilise celui par défaut si None)
        
        Returns:
            Liste des résultats de détection
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le modèle.
        
        Returns:
            Dictionnaire avec les infos du modèle
        """
        pass
    
    def is_loaded(self) -> bool:
        """Vérifie si le modèle est chargé."""
        return self._is_loaded
    
    def unload(self):
        """Décharge le modèle pour libérer la mémoire."""
        if self._model is not None:
            self._model = None
            self._is_loaded = False
            self._logger.info("Modèle déchargé")
    
    def set_confidence_threshold(self, threshold: float):
        """
        Définit le seuil de confiance.
        
        Args:
            threshold: Seuil de confiance (0.0 - 1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))
    
    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Prétraite le frame avant détection.
        Peut être surchargé par les sous-classes.
        
        Args:
            frame: Frame original
        
        Returns:
            Frame prétraité
        """
        return frame
    
    def postprocess(self, raw_results: Any, frame_shape: Tuple[int, int]) -> List[DetectionResult]:
        """
        Post-traite les résultats bruts du modèle.
        Doit être implémenté par les sous-classes.
        
        Args:
            raw_results: Résultats bruts du modèle
            frame_shape: Dimensions du frame original (height, width)
        
        Returns:
            Liste des résultats de détection
        """
        pass


class BaseClassifier(ABC):
    """
    Classe de base pour les classificateurs IA.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialise le classificateur.
        
        Args:
            model_path: Chemin vers le modèle
        """
        self.model_path = model_path
        self._model = None
        self._is_loaded = False
        self._logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def load_model(self) -> bool:
        """
        Charge le modèle IA.
        
        Returns:
            True si succès
        """
        pass
    
    @abstractmethod
    def classify(self, frame: np.ndarray) -> Tuple[str, float]:
        """
        Classifie un frame.
        
        Args:
            frame: Frame à classifier
        
        Returns:
            (class_name, confidence)
        """
        pass
    
    def is_loaded(self) -> bool:
        """Vérifie si le modèle est chargé."""
        return self._is_loaded
    
    def unload(self):
        """Décharge le modèle."""
        if self._model is not None:
            self._model = None
            self._is_loaded = False
