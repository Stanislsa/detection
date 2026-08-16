"""
Image and scene classifier implementation using PyTorch.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import torch

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.core.exceptions import DetectionException
from .base import BaseClassifier

logger = get_logger(__name__)


class ImageClassifier(BaseClassifier):
    """Image classifier using PyTorch pre-trained models."""
    
    def __init__(
        self,
        model_name: str = "resnet18",
        model_path: Optional[str] = None,
        device: str = "auto",
        num_classes: int = 1000
    ):
        """
        Initialize image classifier.
        
        Args:
            model_name: Model architecture (resnet18, resnet50, mobilenet_v2, etc.)
            model_path: Path to custom model weights
            device: Device to run inference on
            num_classes: Number of output classes
        """
        self.model_name = model_name
        self.num_classes = num_classes
        
        super().__init__(model_path, device)
    
    def _load_model(self):
        """Load PyTorch model."""
        try:
            import torchvision.models as models
            import torchvision.transforms as transforms
            
            # Load model architecture
            if self.model_name == "resnet18":
                self.model = models.resnet18(pretrained=True)
            elif self.model_name == "resnet50":
                self.model = models.resnet50(pretrained=True)
            elif self.model_name == "mobilenet_v2":
                self.model = models.mobilenet_v2(pretrained=True)
            else:
                raise DetectionException(f"Unknown model: {self.model_name}")
            
            # Load custom weights if provided
            if self.model_path and Path(self.model_path).exists():
                state_dict = torch.load(self.model_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                logger.info(f"Custom weights loaded from {self.model_path}")
            
            # Set device
            if self.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # Define preprocessing transforms
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            # Load ImageNet labels
            self._load_imagenet_labels()
            
            logger.info(f"{self.model_name} classifier loaded on {self.device}")
            
        except ImportError:
            raise DetectionException("torch or torchvision not installed")
        except Exception as e:
            raise DetectionException(f"Failed to load classifier: {e}")
    
    def _load_imagenet_labels(self):
        """Load ImageNet class labels."""
        try:
            import urllib.request
            
            labels_url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
            with urllib.request.urlopen(labels_url) as response:
                import json
                self.labels = json.loads(response.read())
        except Exception:
            self.labels = [f"class_{i}" for i in range(1000)]
    
    def preprocess(self, image: np.ndarray) -> torch.Tensor:
        """
        Preprocess image for classification.
        
        Args:
            image: Input image as numpy array
        
        Returns:
            Preprocessed tensor
        """
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = image[:, :, ::-1]
        
        # Apply transforms
        tensor = self.transform(image)
        
        # Add batch dimension
        tensor = tensor.unsqueeze(0).to(self.device)
        
        return tensor
    
    def classify(self, image: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Classify image.
        
        Args:
            image: Input image as numpy array
            top_k: Return top K predictions
        
        Returns:
            List of classification results
        """
        if not self.is_loaded():
            raise DetectionException("Model not loaded")
        
        try:
            # Preprocess
            input_tensor = self.preprocess(image)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
            # Postprocess
            results = self.postprocess(probabilities, top_k)
            
            return results
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return []
    
    def postprocess(self, raw_output: torch.Tensor, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Postprocess classification results.
        
        Args:
            raw_output: Model output probabilities
            top_k: Return top K predictions
        
        Returns:
            List of classification results
        """
        # Get top K predictions
        top_k_prob, top_k_indices = torch.topk(raw_output, top_k)
        
        results = []
        for i in range(top_k):
            class_id = top_k_indices[i].item()
            probability = top_k_prob[i].item()
            class_name = self.labels[class_id] if class_id < len(self.labels) else f"class_{class_id}"
            
            results.append({
                "class_id": class_id,
                "class_name": class_name,
                "confidence": probability,
                "method": "pytorch_classifier"
            })
        
        return results


class SceneClassifier(ImageClassifier):
    """Scene classifier specialized for indoor/outdoor scene recognition."""
    
    def __init__(self, **kwargs):
        """Initialize scene classifier."""
        super().__init__(model_name="resnet50", **kwargs)
    
    def classify_scene(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Classify scene type.
        
        Args:
            image: Input image
        
        Returns:
            Scene classification result
        """
        results = self.classify(image, top_k=1)
        
        if results:
            return {
                "scene_type": results[0]["class_name"],
                "confidence": results[0]["confidence"],
                "method": "scene_classifier"
            }
        
        return {
            "scene_type": "unknown",
            "confidence": 0.0,
            "method": "scene_classifier"
        }
