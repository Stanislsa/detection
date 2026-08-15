"""
Programme pour supprimer le cadre de tracking en utilisant YOLO.
Détecte les objets/personnes avec YOLO et recadre la vidéo autour de la zone d'intérêt.
"""

import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO


def detect_tracking_region(frame: np.ndarray, model: YOLO, conf_threshold: float = 0.5) -> tuple:
    """
    Détecter la région de tracking en utilisant YOLO.
    
    Args:
        frame: Image OpenCV
        model: Modèle YOLO
        conf_threshold: Seuil de confiance
        
    Returns:
        (x_min, y_min, x_max, y_max): Coordonnées de la bounding box englobante
    """
    # Faire l'inférence YOLO
    results = model(frame, conf=conf_threshold, verbose=False)
    
    if not results or len(results[0].boxes) == 0:
        # Pas de détection, retourner la frame complète
        height, width = frame.shape[:2]
        return 0, 0, width, height
    
    # Extraire les bounding boxes
    boxes = results[0].boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
    
    # Trouver la bounding box englobante
    x_min = int(np.min(boxes[:, 0]))
    y_min = int(np.min(boxes[:, 1]))
    x_max = int(np.max(boxes[:, 2]))
    y_max = int(np.max(boxes[:, 3]))
    
    # Ajouter une marge (10%)
    height, width = frame.shape[:2]
    margin_x = int((x_max - x_min) * 0.1)
    margin_y = int((y_max - y_min) * 0.1)
    
    x_min = max(0, x_min - margin_x)
    y_min = max(0, y_min - margin_y)
    x_max = min(width, x_max + margin_x)
    y_max = min(height, y_max + margin_y)
    
    return x_min, y_min, x_max, y_max


def yolo_crop_video(input_path: str, output_path: str = None, model_path: str = "yolo11n.pt", conf_threshold: float = 0.5):
    """
    Supprimer le cadre de tracking en utilisant YOLO.
    
    Args:
        input_path: Chemin de la vidéo d'entrée
        output_path: Chemin de la vidéo de sortie (optionnel)
        model_path: Chemin du modèle YOLO
        conf_threshold: Seuil de confiance pour les détections
    """
    print("=" * 60)
    print("Suppression du cadre de tracking avec YOLO")
    print("=" * 60)
    print()
    
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"Erreur: Fichier non trouvé: {input_path}")
        return
    
    # Définir le chemin de sortie si non spécifié
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_yolo_cropped{input_path.suffix}"
    else:
        output_path = Path(output_path)
    
    print(f"Vidéo d'entrée: {input_path}")
    print(f"Vidéo de sortie: {output_path}")
    print(f"Modèle YOLO: {model_path}")
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
    
    print(f"Propriétés originales:")
    print(f"  - Dimensions: {width}x{height}")
    print(f"  - FPS: {fps}")
    print(f"  - Frames totales: {total_frames}")
    print()
    
    # Analyser quelques frames pour déterminer la région de tracking optimale
    print("Analyse des frames pour déterminer la région de tracking...")
    num_analysis_frames = min(30, total_frames)
    all_x_min = []
    all_y_min = []
    all_x_max = []
    all_y_max = []
    
    for i in range(num_analysis_frames):
        ret, frame = cap.read()
        if not ret:
            break
        
        x_min, y_min, x_max, y_max = detect_tracking_region(frame, model, conf_threshold)
        all_x_min.append(x_min)
        all_y_min.append(y_min)
        all_x_max.append(x_max)
        all_y_max.append(y_max)
    
    # Déterminer la région de tracking moyenne
    avg_x_min = int(np.mean(all_x_min))
    avg_y_min = int(np.mean(all_y_min))
    avg_x_max = int(np.mean(all_x_max))
    avg_y_max = int(np.mean(all_y_max))
    
    print(f"Région de tracking détectée:")
    print(f"  - X min: {avg_x_min}")
    print(f"  - Y min: {avg_y_min}")
    print(f"  - X max: {avg_x_max}")
    print(f"  - Y max: {avg_y_max}")
    print()
    
    # Calculer les nouvelles dimensions
    new_width = avg_x_max - avg_x_min
    new_height = avg_y_max - avg_y_min
    
    print(f"Nouvelles dimensions: {new_width}x{new_height}")
    print()
    
    # Si la région est trop petite ou trop grande, utiliser la frame complète
    if new_width < width * 0.3 or new_height < height * 0.3:
        print("Région de tracking trop petite, utilisation de la frame complète")
        avg_x_min, avg_y_min, avg_x_max, avg_y_max = 0, 0, width, height
        new_width, new_height = width, height
    elif new_width > width * 0.95 or new_height > height * 0.95:
        print("Région de tracking trop grande, utilisation de la frame complète")
        avg_x_min, avg_y_min, avg_x_max, avg_y_max = 0, 0, width, height
        new_width, new_height = width, height
    
    # Créer le writer vidéo
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (new_width, new_height))
    
    # Remettre la vidéo au début
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # Traiter toutes les frames
    frame_count = 0
    print("Traitement des frames...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Recadrer la frame
        cropped = frame[avg_y_min:avg_y_max, avg_x_min:avg_x_max]
        
        out.write(cropped)
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
    print(f"Dimensions finales: {new_width}x{new_height}")


if __name__ == "__main__":
    # Vidéo spécifiée par l'utilisateur
    input_video = r"F:\Axyris\proj_indiv\detection\donne\Real-Time-Fall-Detection-using-YOLO\Result videos\annotated_coffee room fall 1.avi"
    
    # Utiliser le modèle YOLO du projet
    model_path = "yolo11n.pt"
    
    yolo_crop_video(input_video, model_path=model_path, conf_threshold=0.5)
