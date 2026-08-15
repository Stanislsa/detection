"""
Client Python pour communiquer avec le backend C++
Envoie des images via TCP et recoit les detections
"""

import socket
import struct
import numpy as np
import cv2
from typing import List, Tuple, Optional
import time


class CppBackendClient:
    """Client TCP pour le backend C++"""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 8888):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self) -> bool:
        """Connecter au serveur C++"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"[Client] Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[Client] Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Deconnecter du serveur"""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("[Client] Disconnected")
    
    def send_frame(self, frame: np.ndarray) -> List[Tuple]:
        """
        Envoyer une frame au serveur C++ et recevoir les detections
        
        Args:
            frame: Image numpy array (BGR format from OpenCV)
            
        Returns:
            Liste de detections: [(x, y, w, h, confidence, class_id), ...]
        """
        if not self.socket:
            print("[Client] Not connected")
            return []
        
        try:
            # Convertir BGR en RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channels = rgb_frame.shape
            
            # Envoyer l'entete (width, height, channels)
            header = struct.pack('iii', width, height, channels)
            self.socket.sendall(header)
            
            # Envoyer les donnees de l'image
            image_data = rgb_frame.tobytes()
            self.socket.sendall(image_data)
            
            # Recevoir le nombre de detections
            num_detections_data = self.socket.recv(4)
            num_detections = struct.unpack('i', num_detections_data)[0]
            
            # Recevoir les detections
            detections = []
            for _ in range(num_detections):
                det_data = self.socket.recv(28)  # 7 floats * 4 bytes
                det = struct.unpack('7f', det_data)
                detections.append(det)
            
            return detections
            
        except Exception as e:
            print(f"[Client] Error sending frame: {e}")
            return []
    
    def close(self):
        """Fermer la connexion"""
        self.disconnect()


def test_client():
    """Test du client avec une webcam"""
    print("=== C++ Backend Client Test ===")
    
    # Initialiser le client
    client = CppBackendClient('127.0.0.1', 8888)
    
    if not client.connect():
        print("Failed to connect to C++ backend")
        print("Make sure the C++ backend is running:")
        print("  cd cpp_backend/build/bin")
        print("  ./fall_detection_backend")
        return
    
    # Ouvrir la webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open webcam")
        client.close()
        return
    
    print("Press 'q' to quit")
    
    try:
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame")
                break
            
            # Envoyer la frame au backend C++
            detections = client.send_frame(frame)
            
            # Dessiner les detections
            for det in detections:
                x, y, w, h, conf, class_id, _ = det
                
                # Dessiner la bounding box
                cv2.rectangle(frame, (int(x), int(y)), (int(x+w), int(y+h)), (0, 255, 0), 2)
                
                # Dessiner le label
                label = f"Class {int(class_id)}: {conf:.2f}"
                cv2.putText(frame, label, (int(x), int(y-10)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Afficher les stats
            frame_count += 1
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            cv2.putText(frame, f"FPS: {fps:.1f} | Detections: {len(detections)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Afficher la frame
            cv2.imshow('C++ Backend Client', frame)
            
            # Quitter avec 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        client.close()
        
        elapsed = time.time() - start_time
        print(f"\n=== Statistics ===")
        print(f"Total frames: {frame_count}")
        print(f"Elapsed time: {elapsed:.2f}s")
        print(f"Average FPS: {frame_count/elapsed:.2f}")


if __name__ == "__main__":
    test_client()
