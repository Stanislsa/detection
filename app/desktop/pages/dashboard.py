"""
Page Tableau de bord avec flux vidéo en direct et informations temps réel.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional

from app.desktop.components.video_widget import VideoWidget
from app.desktop.components.card import StatCard




class DashboardPage(QWidget):
    """
    Page Tableau de bord principale.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.is_running = False
        self.current_camera_source = 0  # Webcam par défaut
        self._init_ui()
        self._init_timer()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Titre de la page
        title_label = QLabel("Tableau de bord")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 20pt;
                font-weight: 700;
            }
        """)
        layout.addWidget(title_label)
        
        # Contenu principal
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Zone vidéo (gauche)
        video_container = QFrame()
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        # Utiliser le VideoWidget component
        self.video_widget = VideoWidget()
        video_layout.addWidget(self.video_widget)
        
        # Connecter le signal frame_received pour afficher les détections
        self.video_widget.frame_received.connect(self._on_frame_received)
        
        # Boutons de contrôle
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        
        self.start_btn = QPushButton("▶ Démarrer")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.start_btn.clicked.connect(self._start_detection)
        controls_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Arrêter")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        self.stop_btn.clicked.connect(self._stop_detection)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)
        
        self.capture_btn = QPushButton("📷 Capturer")
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #3D3D5C;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4A4A6A;
            }
        """)
        self.capture_btn.clicked.connect(self._capture_frame)
        controls_layout.addWidget(self.capture_btn)
        
        self.record_btn = QPushButton("⏺ Enregistrer")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #3D3D5C;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4A4A6A;
            }
        """)
        self.record_btn.clicked.connect(self._toggle_recording)
        controls_layout.addWidget(self.record_btn)
        
        controls_layout.addStretch()
        
        self.settings_btn = QPushButton("⚙ Paramètres")
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        controls_layout.addWidget(self.settings_btn)
        
        video_layout.addLayout(controls_layout)
        
        content_layout.addWidget(video_container, stretch=2)
        
        # Informations temps réel (droite)
        info_container = QFrame()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(16)
        
        # Cartes d'information avec StatCard component
        self.persons_card = StatCard("Personnes détectées", "0", "#2563EB")
        info_layout.addWidget(self.persons_card)
        
        self.activity_card = StatCard("Activité", "Normale", "#10B981")
        info_layout.addWidget(self.activity_card)
        
        self.risk_card = StatCard("Niveau de risque", "Faible", "#F59E0B")
        info_layout.addWidget(self.risk_card)
        
        self.fps_card = StatCard("FPS", "0", "#3B82F6")
        info_layout.addWidget(self.fps_card)
        
        self.model_card = StatCard("Modèle IA", "YOLO11n", "#8B5CF6")
        info_layout.addWidget(self.model_card)
        
        self.camera_card = StatCard("État caméra", "En ligne", "#10B981")
        info_layout.addWidget(self.camera_card)
        
        info_layout.addStretch()
        
        content_layout.addWidget(info_container, stretch=1)
        
        layout.addLayout(content_layout)
    
    def _init_timer(self):
        """Initialise le timer pour les mises à jour temps réel."""
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_info)
        self.update_timer.start(1000)  # Mise à jour chaque seconde
    
    def _start_detection(self):
        """Démarre la détection."""
        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Configurer et démarrer le VideoWidget
        self.video_widget.set_source(self.current_camera_source, "webcam")
        self.video_widget.play()
    
    def _stop_detection(self):
        """Arrête la détection."""
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.video_widget.stop()
    
    def _capture_frame(self):
        """Capture une image."""
        frame = self.video_widget.capture_frame()
        if frame is not None:
            # TODO: Sauvegarder l'image
            pass
    
    def _toggle_recording(self):
        """Bascule l'enregistrement."""
        # TODO: Implémenter l'enregistrement
        pass
    
    def _on_frame_received(self, frame):
        """
        Callback lorsqu'une nouvelle frame est reçue.
        
        Args:
            frame: Image OpenCV
        """
        # TODO: Traiter la frame avec YOLO/MediaPipe
        # Pour l'instant, le VideoWidget gère l'affichage
        pass
    
    def _update_info(self):
        """Met à jour les informations temps réel."""
        if self.is_running:
            # Simuler des données temps réel
            import random
            self.persons_card.update_value(str(random.randint(0, 5)))
            self.fps_card.update_value(str(random.randint(25, 35)))
    
    def set_camera_source(self, source: str, source_type: str = "webcam"):
        """
        Définit la source de la caméra.
        
        Args:
            source: Source (index webcam, URL RTSP ou chemin fichier)
            source_type: Type de source ('webcam', 'rtsp', 'file')
        """
        self.current_camera_source = source
        if self.is_running:
            self.video_widget.stop()
            self.video_widget.set_source(source, source_type)
            self.video_widget.play()
