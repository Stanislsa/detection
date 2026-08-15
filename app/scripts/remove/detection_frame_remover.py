"""
Système complet pour détecter et supprimer les cadres de détection vidéo.
Basé sur l'analyse des projets Fall-Detection et Real-Time-Fall-Detection-using-YOLO.
"""

import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from typing import List, Tuple


class DetectionFrameRemover:
    """Système pour détecter et supprimer les cadres de détection"""
    
    def __init__(self, model_path: str = "yolo11n.pt", conf_threshold: float = 0.5):
        """
        Initialiser le système de suppression de cadres.
        
        Args:
            model_path: Chemin du modèle YOLO
            conf_threshold: Seuil de confiance pour les détections
        """
        print("Chargement du modèle YOLO...")
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        print("OK: Modèle YOLO chargé")
    
    def detect_frames(self, frame: np.ndarray) -> List[Tuple]:
        """
        Détecter les cadres de détection dans une frame.
        
        Args:
            frame: Image OpenCV
            
        Returns:
            Liste de bounding boxes: [(x1, y1, x2, y2, conf, class_id), ...]
        """
        results = self.model(frame, conf=self.conf_threshold, verbose=False)
        
        detections = []
        if results and len(results[0].boxes) > 0:
            boxes = results[0].boxes
            
            for i in range(len(boxes)):
                box = boxes.xyxy[i].cpu().numpy()  # [x1, y1, x2, y2]
                x1, y1, x2, y2 = map(int, box)
                conf = float(boxes.conf[i].cpu().numpy())
                class_id = int(boxes.cls[i].cpu().numpy())
                
                detections.append((x1, y1, x2, y2, conf, class_id))
        
        return detections
    
    def remove_detection_frames(self, frame: np.ndarray, detections: List[Tuple]) -> np.ndarray:
        """
        Supprimer les cadres de détection de la frame.
        
        Args:
            frame: Image OpenCV originale
            detections: Liste des bounding boxes
            
        Returns:
            Frame sans les cadres de détection
        """
        # Créer un masque pour les zones à supprimer
        mask = np.ones(frame.shape[:2], dtype=np.uint8) * 255
        
        for x1, y1, x2, y2, conf, class_id in detections:
            # Marquer la zone de détection comme à supprimer
            mask[y1:y2, x1:x2] = 0
        
        # Appliquer le masque pour supprimer les zones de détection
        # Option 1: Remplacer par du noir
        result = frame.copy()
        result[mask == 0] = 0
        
        return result
    
    def inpaint_detection_frames(self, frame: np.ndarray, detections: List[Tuple]) -> np.ndarray:
        """
        Supprimer les cadres de détection en utilisant l'inpainting.
        
        Args:
            frame: Image OpenCV originale
            detections: Liste des bounding boxes
            
        Returns:
            Frame avec les zones de détection inpaintées
        """
        # Créer un masque pour les zones à inpainter
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        
        for x1, y1, x2, y2, conf, class_id in detections:
            # Marquer la zone de détection comme à inpainter
            mask[y1:y2, x1:x2] = 255
        
        # Utiliser l'inpainting pour remplir les zones
        result = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
        
        return result
    
    def restructure_video(
        self, 
        input_path: str, 
        output_path: str = None,
        method: str = "black",
        show_progress: bool = True
    ):
        """
        Restructurer une vidéo en supprimant les cadres de détection.
        
        Args:
            input_path: Chemin de la vidéo d'entrée
            output_path: Chemin de la vidéo de sortie
            method: Méthode de suppression ('black' ou 'inpaint')
            show_progress: Afficher la progression
        """
        print("=" * 60)
        print("Système de Suppression de Cadres de Détection")
        print("=" * 60)
        print()
        
        input_path = Path(input_path)
        if not input_path.exists():
            print(f"Erreur: Fichier non trouvé: {input_path}")
            return
        
        # Définir le chemin de sortie si non spécifié
        if output_path is None:
            suffix = "_no_frames" if method == "black" else "_inpaint"
            output_path = input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"
        else:
            output_path = Path(output_path)
        
        print(f"Vidéo d'entrée: {input_path}")
        print(f"Vidéo de sortie: {output_path}")
        print(f"Méthode: {method}")
        print()
        
        # Ouvrir la vidéo
        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            print("Erreur: Impossible d'ouvrir la vidéo")
            return
        
        # Obtenir les propriétés de la vidéo
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Propriétés de la vidéo:")
        print(f"  - Dimensions: {width}x{height}")
        print(f"  - FPS: {fps}")
        print(f"  - Frames totales: {total_frames}")
        print()
        
        # Créer le writer vidéo
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        # Traiter toutes les frames
        frame_count = 0
        total_detections = 0
        
        print("Traitement des frames...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Détecter les cadres
            detections = self.detect_frames(frame)
            total_detections += len(detections)
            
            # Supprimer les cadres selon la méthode choisie
            if method == "black":
                processed_frame = self.remove_detection_frames(frame, detections)
            elif method == "inpaint":
                processed_frame = self.inpaint_detection_frames(frame, detections)
            else:
                processed_frame = frame.copy()
            
            out.write(processed_frame)
            frame_count += 1
            
            if show_progress and frame_count % 30 == 0:
                print(f"Progression: {frame_count}/{total_frames} frames")
        
        # Libérer les ressources
        cap.release()
        out.release()
        
        print()
        print("=" * 60)
        print("Traitement terminé")
        print("=" * 60)
        print(f"Vidéo sauvegardée: {output_path}")
        print(f"Frames traitées: {frame_count}")
        print(f"Detections totales: {total_detections}")
        print(f"Detections/frame: {total_detections/frame_count:.2f}")


def main():
    """Fonction principale pour tester le système"""
    # Vidéo spécifiée par l'utilisateur
    input_video = r"F:\Axyris\proj_indiv\detection\donne\Real-Time-Fall-Detection-using-YOLO\Result videos\annotated_coffee room fall 1.avi"
    
    # Créer le système de suppression
    remover = DetectionFrameRemover(model_path="yolo11n.pt", conf_threshold=0.5)
    
    # Méthode 1: Remplacer par du noir
    print("\n--- Méthode 1: Remplacement par noir ---")
    remover.restructure_video(
        input_video, 
        method="black",
        show_progress=True
    )
    
    # Méthode 2: Inpainting
    print("\n--- Méthode 2: Inpainting ---")
    remover.restructure_video(
        input_video, 
        method="inpaint",
        show_progress=True
    )


if __name__ == "__main__":
    main()
