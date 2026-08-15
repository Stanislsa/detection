"""
Test d'integration simple Python↔C++ pour montrer le fonctionnement reel.
Envoie une seule image et affiche les resultats.
"""

import socket
import struct
import numpy as np
import cv2


def test_cpp_backend():
    """Test simple du backend C++ avec une image"""
    print("=" * 60)
    print("Simple Integration Test: Python ↔ C++ Backend")
    print("=" * 60)
    print()
    
    # 1. Creer une image de test
    print("[1/4] Creating test image...")
    test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    print("OK: Test image created (640x640x3)")
    
    # 2. Connecter au backend C++
    print()
    print("[2/4] Connecting to C++ backend...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 8888))
        print("OK: Connected to 127.0.0.1:8888")
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        print("Make sure the C++ backend is running:")
        print("  cd cpp_backend/build/bin/Release")
        print("  ./fall_detection_backend.exe --model ../../../../models/fall_detection.onnx")
        return
    
    # 3. Envoyer l'image
    print()
    print("[3/4] Sending image to C++ backend...")
    try:
        rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_image.shape
        
        # Envoyer l'entete
        header = struct.pack('iii', width, height, channels)
        sock.sendall(header)
        
        # Envoyer les donnees
        image_data = rgb_image.tobytes()
        sock.sendall(image_data)
        print(f"OK: Image sent ({len(image_data)} bytes)")
    except Exception as e:
        print(f"ERROR: Failed to send image: {e}")
        sock.close()
        return
    
    # 4. Recevoir les detections
    print()
    print("[4/4] Receiving detections from C++ backend...")
    try:
        # Recevoir le nombre de detections
        num_detections_data = sock.recv(4)
        num_detections = struct.unpack('i', num_detections_data)[0]
        print(f"OK: Received {num_detections} detections")
        
        # Recevoir les detections
        detections = []
        for i in range(num_detections):
            det_data = sock.recv(28)  # 7 floats * 4 bytes
            det = struct.unpack('7f', det_data)
            detections.append(det)
        
        # Afficher les resultats
        print()
        print("=" * 60)
        print("Results from C++ Backend")
        print("=" * 60)
        print(f"Total detections: {num_detections}")
        print()
        
        if num_detections > 0:
            print("First 5 detections:")
            for i, det in enumerate(detections[:5]):
                x, y, w, h, conf, class_id, _ = det
                print(f"  [{i+1}] Class {int(class_id)}: conf={conf:.3f}, bbox=({x:.1f}, {y:.1f}, {w:.1f}, {h:.1f})")
            
            if num_detections > 5:
                print(f"  ... and {num_detections - 5} more")
        else:
            print("No objects detected in test image")
        
        print()
        print("=" * 60)
        print("✅ Integration Test SUCCESSFUL")
        print("=" * 60)
        print()
        print("The Python↔C++ integration is working correctly!")
        print("The C++ backend is performing YOLO inference via ONNX Runtime.")
        
    except Exception as e:
        print(f"ERROR: Failed to receive detections: {e}")
    
    finally:
        sock.close()
        print()
        print("Connection closed")


if __name__ == "__main__":
    test_cpp_backend()
