"""
Base classes for AI detectors and classifiers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import numpy as np

from backend.core.logger import get_logger
from backend.core.exceptions import DetectionException

logger = get_logger(__name__)


class BaseDetector(ABC):
    """Abstract base class for detection models."""
    
    def __init__(self, model_path: Optional[str] = None, device: str = "auto"):
        """
        Initialize detector.
        
        Args:
            model_path: Path to model file
            device: Device to run inference on
        """
        self.model_path = model_path
        self.device = device
        self.model = None
        self._logger = get_logger(self.__class__.__name__)
        
        self._load_model()
    
    @abstractmethod
    def _load_model(self):
        """Load the detection model."""
        pass
    
    @abstractmethod
    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Perform detection on image.
        
        Args:
            image: Input image as numpy array
        
        Returns:
            List of detection results
        """
        pass
    
    @abstractmethod
    def preprocess(self, image: np.ndarray) -> Any:
        """
        Preprocess image for detection.
        
        Args:
            image: Input image
        
        Returns:
            Preprocessed data
        """
        pass
    
    @abstractmethod
    def postprocess(self, raw_output: Any) -> List[Dict[str, Any]]:
        """
        Postprocess raw model output.
        
        Args:
            raw_output: Raw model output
        
        Returns:
            List of detection results
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.
        
        Returns:
            Model metadata
        """
        return {
            "model_path": self.model_path,
            "device": self.device,
            "model_loaded": self.model is not None,
            "class_name": self.__class__.__name__
        }
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None


class BaseClassifier(ABC):
    """Abstract base class for classification models."""
    
    def __init__(self, model_path: Optional[str] = None, device: str = "auto"):
        """
        Initialize classifier.
        
        Args:
            model_path: Path to model file
            device: Device to run inference on
        """
        self.model_path = model_path
        self.device = device
        self.model = None
        self._logger = get_logger(self.__class__.__name__)
        
        self._load_model()
    
    @abstractmethod
    def _load_model(self):
        """Load the classification model."""
        pass
    
    @abstractmethod
    def classify(self, image: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Classify image.
        
        Args:
            image: Input image as numpy array
            top_k: Return top K predictions
        
        Returns:
            List of classification results
        """
        pass
    
    @abstractmethod
    def preprocess(self, image: np.ndarray) -> Any:
        """
        Preprocess image for classification.
        
        Args:
            image: Input image
        
        Returns:
            Preprocessed data
        """
        pass
    
    @abstractmethod
    def postprocess(self, raw_output: Any, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Postprocess raw model output.
        
        Args:
            raw_output: Raw model output
            top_k: Return top K predictions
        
        Returns:
            List of classification results
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.
        
        Returns:
            Model metadata
        """
        return {
            "model_path": self.model_path,
            "device": self.device,
            "model_loaded": self.model is not None,
            "class_name": self.__class__.__name__
        }
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None
