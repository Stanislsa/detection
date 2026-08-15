"""
Programme pour générer des vidéos avec cadres de détection YOLO.
Utilise YOLOv11 pour détecter les objets/personnes et dessiner les bounding boxes.
"""

import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO


def generate_annotated_video(
    input_path: str, 
    output_path: str = None, 
    model_path: str = "yolo11n.pt",
    conf_threshold: float = 0.5,
    show_labels: bool = True,
    show_conf: bool = True,
    line_thickness: int = 2
):
    """
    Générer une vidéo avec cadres de détection YOLO.
    
    Args:
        input_path: Chemin de la vidéo d'entrée
        output_path: Chemin de la vidéo de sortie (optionnel)
        model_path: Chemin du modèle YOLO
        conf_threshold: Seuil de confiance pour les détections
        show_labels: Afficher les labels de classe
        show_conf: Afficher la confiance
        line_thickness: Épaisseur des lignes de bounding box
    """
    print("=" * 60)
    print("Génération de vidéo avec cadres de détection YOLO")
    print("=" * 60)
    print()
    
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"Erreur: Fichier non trouvé: {input_path}")
        return
    
    # Définir le chemin de sortie si non spécifié
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_annotated{input_path.suffix}"
    else:
        output_path = Path(output_path)
    
    print(f"Vidéo d'entrée: {input_path}")
    print(f"Vidéo de sortie: {output_path}")
    print(f"Modèle YOLO: {model_path}")
    print(f"Seuil de confiance: {conf_threshold}")
    print()
    
    # Charger le modèle YOLO
    print("Chargement du modèle YOLO...")
    try:
        model = YOLO(model_path)
        print("OK: Modèle YOLO chargé")
    except Exception as e:
        print(f"Erreur: Impossible de charger le modèle YOLO: {e}")
        return
    
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
        
        # Faire l'inférence YOLO
        results = model(frame, conf=conf_threshold, verbose=False)
        
        # Dessiner les bounding boxes sur la frame
        annotated_frame = frame.copy()
        
        if results and len(results[0].boxes) > 0:
            boxes = results[0].boxes
            
            for i in range(len(boxes)):
                # Obtenir les coordonnées de la bounding box
                box = boxes.xyxy[i].cpu().numpy()  # [x1, y1, x2, y2]
                x1, y1, x2, y2 = map(int, box)
                
                # Obtenir la confiance et la classe
                conf = float(boxes.conf[i].cpu().numpy())
                class_id = int(boxes.cls[i].cpu().numpy())
                class_name = model.names[class_id]
                
                # Définir la couleur selon la classe
                if class_id == 0:  # Person
                    color = (0, 255, 0)  # Vert
                elif class_id == 1:  # Fall
                    color = (0, 0, 255)  # Rouge
                else:
                    color = (255, 0, 0)  # Bleu
                
                # Dessiner la bounding box
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, line_thickness)
                
                # Dessiner le label et la confiance
                label = ""
                if show_labels:
                    label += class_name
                if show_conf:
                    if label:
                        label += f" {conf:.2f}"
                    else:
                        label += f"{conf:.2f}"
                
                if label:
                    # Calculer la taille du texte
                    (text_width, text_height) = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                    
                    # Dessiner le fond du label
                    cv2.rectangle(annotated_frame, (x1, y1 - text_height - 10), 
                                 (x1 + text_width, y1), color, -1)
                    
                    # Dessiner le texte
                    cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                total_detections += 1
        
        out.write(annotated_frame)
        frame_count += 1
        
        if frame_count % 30 == 0:
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


if __name__ == "__main__":
    # Vidéo spécifiée par l'utilisateur
    input_video = r"F:\Axyris\proj_indiv\detection\donne\Real-Time-Fall-Detection-using-YOLO\Result videos\annotated_coffee room fall 1.avi"
    
    # Utiliser le modèle YOLO du projet
    model_path = "yolo11n.pt"
    
    generate_annotated_video(
        input_video, 
        model_path=model_path, 
        conf_threshold=0.5,
        show_labels=True,
        show_conf=True,
        line_thickness=2
    )
