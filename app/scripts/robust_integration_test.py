"""
Test d'integration robuste Python↔C++ avec gestion de reconnexion.
Utilise le backend C++ pour l'inférence YOLO et Python pour l'affichage.
"""

import socket
import struct
import numpy as np
import cv2
from typing import List, Tuple
import time


class RobustCppBackendClient:
    """Client TCP robust avec gestion de reconnexion"""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connecter au serveur C++"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)  # Timeout de 5 secondes
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"[Client] Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[Client] Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Deconnecter du serveur"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.connected = False
            print("[Client] Disconnected")
    
    def reconnect(self) -> bool:
        """Reconnecter au serveur"""
        self.disconnect()
        time.sleep(0.5)
        return self.connect()
    
    def send_frame(self, frame: np.ndarray) -> List[Tuple]:
        """
        Envoyer une frame au serveur C++ et recevoir les detections
        
        Args:
            frame: Image numpy array (BGR format from OpenCV)
            
        Returns:
            Liste de detections: [(x, y, w, h, confidence, class_id), ...]
        """
        if not self.connected or not self.socket:
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
            if len(num_detections_data) < 4:
                return []
            
            num_detections = struct.unpack('i', num_detections_data)[0]
            
            # Recevoir les detections
            detections = []
            for _ in range(num_detections):
                det_data = self.socket.recv(28)  # 7 floats * 4 bytes
                if len(det_data) < 28:
                    break
                det = struct.unpack('7f', det_data)
                detections.append(det)
            
            return detections
            
        except Exception as e:
            print(f"[Client] Error: {e}")
            self.connected = False
            return []


def run_robust_integration_test():
    """Test d'integration robuste avec gestion de reconnexion"""
    print("=" * 60)
    print("Robust Integration Test: Python ↔ C++ Backend")
    print("=" * 60)
    print()
    
    # Initialiser le client C++
    client = RobustCppBackendClient('127.0.0.1', 8888)
    
    # Ouvrir la webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open webcam")
        return
    
    print("Webcam opened successfully")
    print("Press 'q' to quit")
    print()
    
    try:
        frame_count = 0
        detection_count = 0
        connection_errors = 0
        start_time = time.time()
        last_stats_time = start_time
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame")
                break
            
            # Tenter de se connecter si necessaire
            if not client.connected:
                if client.connect():
                    connection_errors = 0
                else:
                    connection_errors += 1
                    if connection_errors % 10 == 0:
                        print(f"[Warning] Connection attempts: {connection_errors}")
            
            # Redimensionner pour l'inférence (640x640)
            frame_resized = cv2.resize(frame, (640, 640))
            
            # Envoyer la frame au backend C++ si connecte
            detections = []
            if client.connected:
                detections = client.send_frame(frame_resized)
                
                # Si erreur, tenter reconnexion
                if not client.connected:
                    client.reconnect()
            
            # Dessiner les detections sur la frame originale
            for det in detections:
                x, y, w, h, conf, class_id, _ = det
                
                # Adapter les coordonnées à la taille originale
                orig_h, orig_w = frame.shape[:2]
                scale_x = orig_w / 640
                scale_y = orig_h / 640
                
                x_scaled = int(x * scale_x)
                y_scaled = int(y * scale_y)
                w_scaled = int(w * scale_x)
                h_scaled = int(h * scale_y)
                
                # Dessiner la bounding box
                color = (0, 255, 0) if class_id == 0 else (0, 0, 255)
                cv2.rectangle(frame, (x_scaled, y_scaled), 
                           (x_scaled + w_scaled, y_scaled + h_scaled), 
                           color, 2)
                
                # Dessiner le label
                label = f"Person: {conf:.2f}" if class_id == 0 else f"Class {int(class_id)}: {conf:.2f}"
                cv2.putText(frame, label, (x_scaled, y_scaled - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            detection_count += len(detections)
            frame_count += 1
            
            # Afficher les stats toutes les 2 secondes
            elapsed = time.time() - last_stats_time
            if elapsed >= 2:
                total_elapsed = time.time() - start_time
                fps = frame_count / total_elapsed if total_elapsed > 0 else 0
                avg_detections = detection_count / frame_count if frame_count > 0 else 0
                
                status = "CONNECTED" if client.connected else "DISCONNECTED"
                print(f"[Stats] FPS: {fps:.1f} | Detections/frame: {avg_detections:.1f} | Status: {status}")
                last_stats_time = time.time()
            
            # Afficher la frame
            status_text = "C++ Backend: " + ("CONNECTED" if client.connected else "DISCONNECTED")
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                       (0, 255, 0) if client.connected else (0, 0, 255), 2)
            cv2.putText(frame, f"FPS: {frame_count/(time.time()-start_time):.1f}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Detections: {len(detections)}", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Robust Integration Test', frame)
            
            # Quitter avec 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        client.disconnect()
        
        # Afficher les statistiques finales
        total_elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print("Final Statistics")
        print("=" * 60)
        print(f"Total frames: {frame_count}")
        print(f"Total detections: {detection_count}")
        print(f"Elapsed time: {total_elapsed:.2f}s")
        print(f"Average FPS: {frame_count/total_elapsed:.2f}")
        print(f"Average detections/frame: {detection_count/frame_count:.2f}")


if __name__ == "__main__":
    run_robust_integration_test()
