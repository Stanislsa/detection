"""
Classificateur IA pour la classification d'images.
Peut être utilisé pour classifier des objets, des scènes, etc.
"""

from typing import Tuple, Dict, Any, Optional, List
import numpy as np

try:
    from torchvision import models, transforms
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from app.ai.base_detector import BaseClassifier
from app.core.logger import get_logger
from app.core.exceptions import DetectionException


class ImageClassifier(BaseClassifier):
    """
    Classificateur d'images utilisant PyTorch (ResNet, MobileNet, etc.).
    """
    
    def __init__(
        self,
        model_name: str = "resnet18",
        model_path: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        Initialise le classificateur.
        
        Args:
            model_name: Nom du modèle (resnet18, mobilenet_v2, etc.)
            model_path: Chemin vers un modèle entraîné (optionnel)
            device: Device d'exécution (cpu, cuda)
        """
        super().__init__(model_path)
        self.model_name = model_name
        self.device = device
        self._transform = None
        self._class_names = []
    
    def load_model(self) -> bool:
        """
        Charge le modèle de classification.
        
        Returns:
            True si succès
        """
        if not TORCH_AVAILABLE:
            self._logger.error("PyTorch non installé. pip install torch torchvision")
            raise DetectionException("PyTorch non installé")
        
        try:
            self._logger.info(f"Chargement du modèle {self.model_name}")
            
            # Charger le modèle pré-entraîné
            if self.model_name == "resnet18":
                self._model = models.resnet18(pretrained=True)
            elif self.model_name == "resnet50":
                self._model = models.resnet50(pretrained=True)
            elif self.model_name == "mobilenet_v2":
                self._model = models.mobilenet_v2(pretrained=True)
            elif self.model_name == "efficientnet_b0":
                self._model = models.efficientnet_b0(pretrained=True)
            else:
                self._logger.error(f"Modèle inconnu: {self.model_name}")
                raise DetectionException(f"Modèle inconnu: {self.model_name}")
            
            # Charger un modèle personnalisé si spécifié
            if self.model_path:
                self._model.load_state_dict(torch.load(self.model_path, map_location=self.device))
                self._logger.info(f"Modèle personnalisé chargé depuis {self.model_path}")
            
            # Configurer le device
            self._model.to(self.device)
            self._model.eval()
            
            # Configurer les transformations
            self._transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            # Charger les noms de classes ImageNet
            self._load_imagenet_classes()
            
            self._is_loaded = True
            self._logger.info(f"Modèle {self.model_name} chargé avec succès")
            return True
            
        except Exception as e:
            self._logger.error(f"Erreur chargement modèle: {e}")
            raise DetectionException(f"Erreur chargement modèle: {e}")
    
    def classify(self, frame: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Classifie un frame.
        
        Args:
            frame: Frame à classifier
            top_k: Nombre de classes top à retourner
        
        Returns:
            Liste de (class_name, confidence)
        """
        if not self._is_loaded:
            self._logger.warning("Modèle non chargé, tentative de chargement...")
            self.load_model()
        
        try:
            # Prétraitement
            input_tensor = self._transform(frame).unsqueeze(0).to(self.device)
            
            # Inférence
            with torch.no_grad():
                outputs = self._model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
            # Récupérer les top-k classes
            top_probs, top_indices = torch.topk(probabilities, top_k)
            
            results = []
            for i in range(top_k):
                class_idx = top_indices[i].item()
                confidence = top_probs[i].item()
                class_name = self._class_names[class_idx] if class_idx < len(self._class_names) else f"class_{class_idx}"
                results.append((class_name, confidence))
            
            return results
            
        except Exception as e:
            self._logger.error(f"Erreur lors de la classification: {e}")
            return [("unknown", 0.0)]
    
    def _load_imagenet_classes(self):
        """Charge les noms de classes ImageNet."""
        # Classes ImageNet (simplifié pour l'exemple)
        self._class_names = [
            "tench", "goldfish", "great_white_shark", "tiger_shark", "hammerhead",
            "electric_ray", "stingray", "cock", "hen", "ostrich",
            # ... 1000 classes au total
        ]
        
        # Pour une application complète, charger le fichier complet
        # depuis: https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le modèle.
        
        Returns:
            Dictionnaire d'informations
        """
        return {
            "type": "ImageClassifier",
            "model_name": self.model_name,
            "model_path": self.model_path,
            "device": self.device,
            "is_loaded": self._is_loaded,
            "num_classes": len(self._class_names)
        }


class SceneClassifier(ImageClassifier):
    """
    Classificateur spécialisé pour les scènes (intérieur/extérieur, etc.).
    Utilise un modèle entraîné pour la classification de scènes.
    """
    
    def __init__(self, model_path: Optional[str] = None, device: str = "cpu"):
        """
        Initialise le classificateur de scènes.
        
        Args:
            model_path: Chemin vers le modèle entraîné
            device: Device d'exécution
        """
        super().__init__("mobilenet_v2", model_path, device)
        self._scene_classes = [
            "indoor", "outdoor", "street", "room", "corridor",
            "office", "home", "warehouse", "parking", "unknown"
        ]
    
    def classify(self, frame: np.ndarray, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Classifie la scène du frame.
        
        Args:
            frame: Frame à classifier
            top_k: Nombre de classes top
        
        Returns:
            Liste de (scene_name, confidence)
        """
        # Pour l'instant, utilise le classificateur de base
        # Dans une implémentation réelle, utiliser un modèle entraîné spécifiquement
        results = super().classify(frame, top_k)
        
        # Mapper les résultats vers les classes de scènes
        scene_results = []
        for class_name, confidence in results:
            scene = self._map_to_scene(class_name)
            scene_results.append((scene, confidence))
        
        return scene_results
    
    def _map_to_scene(self, class_name: str) -> str:
        """
        Mappe une classe vers une scène.
        
        Args:
            class_name: Nom de la classe originale
        
        Returns:
            Nom de la scène
        """
        # Mapping simplifié
        indoor_keywords = ["room", "office", "home", "indoor", "corridor"]
        outdoor_keywords = ["street", "parking", "outdoor", "warehouse"]
        
        class_lower = class_name.lower()
        
        for keyword in indoor_keywords:
            if keyword in class_lower:
                return "indoor"
        
        for keyword in outdoor_keywords:
            if keyword in class_lower:
                return "outdoor"
        
        return "unknown"
