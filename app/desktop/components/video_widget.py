"""
Composant VideoWidget indépendant.
Supporte Webcam, RTSP, fichier vidéo, détection IA.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont
import cv2
import numpy as np
from typing import Optional, Tuple, List


class VideoWidget(QWidget):
    """
    Widget vidéo indépendant pour affichage de flux.
    
    Supporte :
    - Webcam locale
    - Flux RTSP
    - Fichier vidéo
    - Détection IA (bounding boxes, labels)
    - Capture d'image
    """
    
    # Signaux
    frame_received = pyqtSignal(np.ndarray)  # Nouvelle frame reçue
    detection_received = pyqtSignal(list)  # Nouvelle détection IA
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.source = None  # Webcam index, RTSP URL ou chemin fichier
        self.source_type = None  # 'webcam', 'rtsp', 'file'
        self.capture = None
        self.is_playing = False
        self.show_detections = True
        self.detections = []  # Liste des détections actuelles
        
        self._init_ui()
        self._init_timer()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                border-radius: 12px;
                border: 2px solid #4A4A6A;
            }
        """)
        self.setMinimumSize(640, 480)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label pour l'affichage vidéo
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                color: #A0A0B0;
                font-size: 14pt;
            }
        """)
        self.video_label.setText("📹 Flux vidéo en attente...")
        layout.addWidget(self.video_label)
    
    def _init_timer(self):
        """Initialise le timer pour la lecture vidéo."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)
    
    def set_source(self, source: str, source_type: str = "webcam"):
        """
        Définit la source vidéo.
        
        Args:
            source: Source (index webcam, URL RTSP ou chemin fichier)
            source_type: Type de source ('webcam', 'rtsp', 'file')
        """
        self.source = source
        self.source_type = source_type
        self._open_capture()
    
    def _open_capture(self):
        """Ouvre la capture vidéo."""
        if self.capture is not None:
            self.capture.release()
        
        if self.source_type == "webcam":
            self.capture = cv2.VideoCapture(int(self.source))
        else:
            self.capture = cv2.VideoCapture(self.source)
        
        if self.capture.isOpened():
            self.video_label.setText("")
        else:
            self.video_label.setText("❌ Erreur d'ouverture du flux")
    
    def play(self):
        """Démarre la lecture vidéo."""
        if self.capture is None or not self.capture.isOpened():
            self._open_capture()
        
        if self.capture and self.capture.isOpened():
            self.is_playing = True
            self.timer.start(30)  # ~33 FPS
    
    def pause(self):
        """Met en pause la lecture vidéo."""
        self.is_playing = False
        self.timer.stop()
    
    def stop(self):
        """Arrête la lecture vidéo."""
        self.pause()
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        self.video_label.setText("📹 Flux vidéo en attente...")
    
    def _update_frame(self):
        """Met à jour l'image vidéo."""
        if not self.is_playing or self.capture is None:
            return
        
        ret, frame = self.capture.read()
        
        if ret:
            # Émettre le signal avec la frame brute
            self.frame_received.emit(frame)
            
            # Dessiner les détections si activé
            if self.show_detections and self.detections:
                frame = self._draw_detections(frame)
            
            # Convertir pour affichage PyQt
            self._display_frame(frame)
    
    def _display_frame(self, frame: np.ndarray):
        """
        Affiche une frame dans le widget.
        
        Args:
            frame: Image OpenCV (BGR)
        """
        # Convertir BGR → RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Redimensionner si nécessaire
        h, w = rgb_frame.shape[:2]
        widget_w, widget_h = self.width(), self.height()
        
        if w > widget_w or h > widget_h:
            # Conserver le ratio d'aspect
            ratio = min(widget_w / w, widget_h / h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            rgb_frame = cv2.resize(rgb_frame, (new_w, new_h))
        
        # Convertir en QImage
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Afficher
        pixmap = QPixmap.fromImage(q_image)
        self.video_label.setPixmap(pixmap)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def _draw_detections(self, frame: np.ndarray) -> np.ndarray:
        """
        Dessine les bounding boxes et labels sur la frame.
        
        Args:
            frame: Image OpenCV
        
        Returns:
            Image avec détections dessinées
        """
        for detection in self.detections:
            bbox = detection.get("bbox", None)  # (x1, y1, x2, y2)
            label = detection.get("label", "")
            confidence = detection.get("confidence", 0.0)
            color = detection.get("color", (0, 255, 0))
            
            if bbox:
                x1, y1, x2, y2 = bbox
                
                # Dessiner rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Dessiner label
                if label:
                    text = f"{label}: {confidence:.2f}"
                    cv2.putText(
                        frame, text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                    )
        
        return frame
    
    def set_detections(self, detections: List[dict]):
        """
        Définit les détections à afficher.
        
        Args:
            detections: Liste de détections
                [{'bbox': (x1, y1, x2, y2), 'label': str, 'confidence': float, 'color': tuple}]
        """
        self.detections = detections
    
    def clear_detections(self):
        """Efface toutes les détections."""
        self.detections = []
    
    def toggle_detections(self):
        """Bascule l'affichage des détections."""
        self.show_detections = not self.show_detections
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture l'image actuelle.
        
        Returns:
            Image capturée ou None
        """
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                return frame
        return None
    
    def closeEvent(self, event):
        """Gère la fermeture du widget."""
        self.stop()
        super().closeEvent(event)
