"""
Mini programme de test pour le tracking de visage en temps réel.
Utilise OpenCV pour détecter et suivre les visages avec la webcam.
"""

import cv2
import numpy as np
from typing import List, Tuple
import time


class FaceTracker:
    """Tracker de visage simple avec OpenCV"""
    
    def __init__(self):
        # Charger le détecteur de visage Haar Cascade
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Initialiser le tracker KCF pour le suivi
        self.tracker = None
        self.tracking = False
        self.tracker_box = None
        
        # Statistiques
        self.frame_count = 0
        self.detection_count = 0
        self.start_time = time.time()
        
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Détecter les visages dans une frame.
        
        Args:
            frame: Image OpenCV (BGR)
            
        Returns:
            Liste de bounding boxes [(x, y, w, h), ...]
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        self.detection_count += len(faces)
        return faces
    
    def start_tracking(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]):
        """
        Commencer le tracking d'un visage.
        
        Args:
            frame: Image actuelle
            bbox: Bounding box (x, y, w, h)
        """
        self.tracker = cv2.TrackerKCF_create()
        self.tracker.init(frame, bbox)
        self.tracking = True
        self.tracker_box = bbox
        
    def update_tracking(self, frame: np.ndarray) -> Tuple[bool, Tuple[int, int, int, int]]:
        """
        Mettre à jour le tracking.
        
        Args:
            frame: Image actuelle
            
        Returns:
            (success, bbox) où bbox est (x, y, w, h)
        """
        if not self.tracking or self.tracker is None:
            return False, (0, 0, 0, 0)
        
        success, bbox = self.tracker.update(frame)
        if success:
            self.tracker_box = tuple(map(int, bbox))
        else:
            self.tracking = False
            self.tracker_box = None
            
        return success, self.tracker_box
    
    def draw_detections(self, frame: np.ndarray, faces: List[Tuple[int, int, int, int]]):
        """
        Dessiner les détections sur la frame.
        
        Args:
            frame: Image OpenCV
            faces: Liste de bounding boxes
        """
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 'Face', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    def draw_tracking(self, frame: np.ndarray):
        """
        Dessiner le tracking sur la frame.
        
        Args:
            frame: Image OpenCV
        """
        if self.tracking and self.tracker_box:
            x, y, w, h = self.tracker_box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, 'Tracking', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    def draw_stats(self, frame: np.ndarray):
        """
        Dessiner les statistiques sur la frame.
        
        Args:
            frame: Image OpenCV
        """
        elapsed = time.time() - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        stats = [
            f"FPS: {fps:.1f}",
            f"Frames: {self.frame_count}",
            f"Detections: {self.detection_count}",
            f"Tracking: {'ON' if self.tracking else 'OFF'}"
        ]
        
        for i, stat in enumerate(stats):
            cv2.putText(frame, stat, (10, 30 + i*25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    def run(self, camera_id: int = 0):
        """
        Exécuter le tracking de visage en temps réel.
        
        Args:
            camera_id: ID de la webcam (défaut: 0)
        """
        print("=== Face Tracking Test ===")
        print("Press 'q' to quit")
        print("Press 's' to start tracking first face")
        print("Press 'r' to reset tracking")
        print()
        
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print("Error: Cannot open webcam")
            return
        
        print("Webcam opened successfully")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Cannot read frame")
                    break
                
                self.frame_count += 1
                
                # Détecter les visages
                faces = self.detect_faces(frame)
                
                # Mettre à jour le tracking si actif
                if self.tracking:
                    success, bbox = self.update_tracking(frame)
                    if not success:
                        self.tracking = False
                        print("Tracking lost")
                
                # Dessiner
                self.draw_detections(frame, faces)
                self.draw_tracking(frame)
                self.draw_stats(frame)
                
                # Afficher
                cv2.imshow('Face Tracking Test', frame)
                
                # Gestion des touches
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Quitting...")
                    break
                elif key == ord('s') and len(faces) > 0 and not self.tracking:
                    # Commencer le tracking du premier visage
                    self.start_tracking(frame, tuple(faces[0]))
                    print("Tracking started")
                elif key == ord('r'):
                    self.tracking = False
                    self.tracker = None
                    self.tracker_box = None
                    print("Tracking reset")
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            
            # Afficher les statistiques finales
            elapsed = time.time() - self.start_time
            print("\n=== Statistics ===")
            print(f"Total frames: {self.frame_count}")
            print(f"Total detections: {self.detection_count}")
            print(f"Elapsed time: {elapsed:.2f}s")
            print(f"Average FPS: {self.frame_count/elapsed:.2f}")


if __name__ == "__main__":
    tracker = FaceTracker()
    tracker.run(camera_id=0)
