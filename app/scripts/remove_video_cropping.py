"""
Programme pour supprimer le cadrage (bordures noires) d'une vidéo.
Détecte et supprime les bordures letterboxing/pillarboxing.
"""

import cv2
import numpy as np
from pathlib import Path


def detect_borders(frame: np.ndarray, threshold: int = 30) -> tuple:
    """
    Détecter les bordures noires dans une frame.
    
    Args:
        frame: Image OpenCV
        threshold: Seuil de luminosité pour détecter les bordures
        
    Returns:
        (top, bottom, left, right): Coordonnées des bordures
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Détecter les bordures horizontales (haut et bas)
    # Scanner de haut en bas
    top = 0
    for i in range(gray.shape[0] // 2):
        if np.mean(gray[i, :]) > threshold:
            top = i
            break
    
    # Scanner de bas en haut
    bottom = gray.shape[0]
    for i in range(gray.shape[0] - 1, gray.shape[0] // 2, -1):
        if np.mean(gray[i, :]) > threshold:
            bottom = i
            break
    
    # Détecter les bordures verticales (gauche et droite)
    # Scanner de gauche à droite
    left = 0
    for i in range(gray.shape[1] // 2):
        if np.mean(gray[:, i]) > threshold:
            left = i
            break
    
    # Scanner de droite à gauche
    right = gray.shape[1]
    for i in range(gray.shape[1] - 1, gray.shape[1] // 2, -1):
        if np.mean(gray[:, i]) > threshold:
            right = i
            break
    
    return top, bottom, left, right


def remove_cropping(input_path: str, output_path: str = None, threshold: int = 30):
    """
    Supprimer le cadrage d'une vidéo.
    
    Args:
        input_path: Chemin de la vidéo d'entrée
        output_path: Chemin de la vidéo de sortie (optionnel)
        threshold: Seuil de luminosité pour détecter les bordures
    """
    print("=" * 60)
    print("Suppression du cadrage vidéo")
    print("=" * 60)
    print()
    
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"Erreur: Fichier non trouvé: {input_path}")
        return
    
    # Définir le chemin de sortie si non spécifié
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_no_cropping{input_path.suffix}"
    else:
        output_path = Path(output_path)
    
    print(f"Vidéo d'entrée: {input_path}")
    print(f"Vidéo de sortie: {output_path}")
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
    
    print(f"Propriétés originales:")
    print(f"  - Dimensions: {width}x{height}")
    print(f"  - FPS: {fps}")
    print(f"  - Frames totales: {total_frames}")
    print()
    
    # Lire la première frame pour détecter les bordures
    ret, frame = cap.read()
    if not ret:
        print("Erreur: Impossible de lire la première frame")
        cap.release()
        return
    
    # Détecter les bordures
    top, bottom, left, right = detect_borders(frame, threshold)
    
    print(f"Bordures détectées:")
    print(f"  - Haut: {top} pixels")
    print(f"  - Bas: {height - bottom} pixels")
    print(f"  - Gauche: {left} pixels")
    print(f"  - Droite: {width - right} pixels")
    print()
    
    # Calculer les nouvelles dimensions
    new_width = right - left
    new_height = bottom - top
    
    print(f"Nouvelles dimensions: {new_width}x{new_height}")
    print()
    
    # Si pas de bordures significatives, copier simplement la vidéo
    if new_width >= width * 0.9 and new_height >= height * 0.9:
        print("Pas de bordures significatives détectées")
        print("Copie de la vidéo originale...")
        
        # Créer le writer vidéo
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        # Remettre la vidéo au début
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # Copier toutes les frames
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            out.write(frame)
            frame_count += 1
            
            if frame_count % 30 == 0:
                print(f"Progression: {frame_count}/{total_frames} frames")
        
        out.release()
        cap.release()
        
        print(f"Vidéo copiée: {output_path}")
        return
    
    # Créer le writer vidéo avec les nouvelles dimensions
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
        cropped = frame[top:bottom, left:right]
        
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
    
    remove_cropping(input_video)
