"""
Page Caméras avec grille de cartes et gestion.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QScrollArea, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict, Optional

from app.desktop.models.camera import Camera, CameraStatus
from app.desktop.components.dialogs import CameraDialog
from app.desktop.services.notification_service import NotificationType


class CameraCard(QFrame):
    """
    Carte de caméra avec aperçu et informations.
    """
    
    # Signaux
    edit_clicked = pyqtSignal(int)  # camera_id
    delete_clicked = pyqtSignal(int)  # camera_id
    
    def __init__(self, camera: Camera, parent=None):
        super().__init__(parent)
        
        self.camera = camera
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setStyleSheet("""
            QFrame {
                background-color: #2D2D44;
                border-radius: 12px;
                border: 1px solid #4A4A6A;
            }
            QFrame:hover {
                border: 2px solid #2563EB;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Aperçu vidéo (placeholder)
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border-radius: 8px;
                border: 1px solid #3D3D5C;
            }
        """)
        preview_frame.setMinimumHeight(150)
        
        preview_layout = QVBoxLayout(preview_frame)
        preview_label = QLabel("📹")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setStyleSheet("""
            QLabel {
                color: #A0A0B0;
                font-size: 24pt;
            }
        """)
        preview_layout.addWidget(preview_label)
        
        layout.addWidget(preview_frame)
        
        # Nom de la caméra
        name_label = QLabel(self.camera.name)
        name_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 12pt;
                font-weight: 600;
            }
        """)
        layout.addWidget(name_label)
        
        # Source
        source_label = QLabel(f"{self.camera.source_type}: {self.camera.source[:30]}..." if len(self.camera.source) > 30 else self.camera.source)
        source_label.setStyleSheet("""
            QLabel {
                color: #A0A0B0;
                font-size: 9pt;
            }
        """)
        layout.addWidget(source_label)
        
        # Statut
        is_online = self.camera.status.value == "online"
        status_label = QLabel("● En ligne" if is_online else "● Hors ligne")
        status_label.setStyleSheet(f"""
            QLabel {{
                color: {"#10B981" if is_online else "#EF4444"};
                font-size: 9pt;
                font-weight: 600;
            }}
        """)
        layout.addWidget(status_label)
        
        # Boutons d'action
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        edit_btn = QPushButton("✏")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3D3D5C;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #4A4A6A;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.camera.id))
        actions_layout.addWidget(edit_btn)
        
        config_btn = QPushButton("⚙")
        config_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        actions_layout.addWidget(config_btn)
        
        delete_btn = QPushButton("🗑")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.camera.id))
        actions_layout.addWidget(delete_btn)
        
        layout.addLayout(actions_layout)


class CamerasPage(QWidget):
    """
    Page Caméras avec grille de cartes.
    """
    
    def __init__(self, camera_service=None, notification_service=None, parent=None):
        super().__init__(parent)
        
        self.camera_service = camera_service
        self.notification_service = notification_service
        self.cameras: List[Camera] = []
        self._init_ui()
        self._load_cameras()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Titre de la page et boutons
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Caméras")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 20pt;
                font-weight: 700;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Boutons d'action
        add_btn = QPushButton("+ Ajouter une caméra")
        add_btn.setStyleSheet("""
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
        add_btn.clicked.connect(self._add_camera)
        header_layout.addWidget(add_btn)
        
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3D3D5C;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #4A4A6A;
            }
        """)
        refresh_btn.clicked.connect(self._load_cameras)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Zone de défilement pour la grille
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2D2D44;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4A4A6A;
                border-radius: 6px;
                min-height: 30px;
            }
        """)
        
        # Container pour la grille
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.grid_container)
        layout.addWidget(scroll_area)
    
    def _load_cameras(self):
        """Charge les caméras depuis le service ou utilise des données d'exemple."""
        if self.camera_service:
            self.cameras = self.camera_service.get_cameras()
        else:
            # Données d'exemple si pas de service
            self.cameras = [
                Camera(
                    id=1,
                    name="Caméra Salon",
                    source="rtsp://192.168.1.50/stream",
                    source_type="rtsp",
                    room="Salon",
                    is_active=True,
                    fps=30,
                    resolution_width=1920,
                    resolution_height=1080,
                    status=CameraStatus.ONLINE
                ),
                Camera(
                    id=2,
                    name="Caméra Cuisine",
                    source="rtsp://192.168.1.51/stream",
                    source_type="rtsp",
                    room="Cuisine",
                    is_active=True,
                    fps=30,
                    resolution_width=1920,
                    resolution_height=1080,
                    status=CameraStatus.ONLINE
                ),
                Camera(
                    id=3,
                    name="Webcam Locale",
                    source="0",
                    source_type="webcam",
                    room="Bureau",
                    is_active=True,
                    fps=30,
                    resolution_width=640,
                    resolution_height=480,
                    status=CameraStatus.OFFLINE
                ),
            ]
        
        self._populate_grid()
    
    def _populate_grid(self):
        """Remplit la grille avec les caméras."""
        # Nettoyer la grille existante
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Ajouter les cartes
        row, col = 0, 0
        max_cols = 3
        
        for camera in self.cameras:
            card = CameraCard(camera)
            card.edit_clicked.connect(self._edit_camera)
            card.delete_clicked.connect(self._delete_camera)
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def _add_camera(self):
        """Ajoute une nouvelle caméra."""
        dialog = CameraDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            camera_data = dialog.get_data()
            
            if self.camera_service:
                new_camera = self.camera_service.create_camera(camera_data)
                if new_camera:
                    self.cameras.append(new_camera)
                    self._populate_grid()
                    if self.notification_service:
                        self.notification_service.add_notification(
                            "Caméra ajoutée",
                            f"La caméra {new_camera.name} a été ajoutée avec succès",
                            NotificationType.SUCCESS
                        )
            else:
                # Mode hors ligne - ajouter localement
                new_camera = Camera(
                    id=len(self.cameras) + 1,
                    name=camera_data["name"],
                    source=camera_data["source"],
                    source_type=camera_data["source_type"],
                    is_active=camera_data["active"],
                    fps=camera_data["fps"],
                    resolution_width=int(camera_data["resolution"].split("x")[0]),
                    resolution_height=int(camera_data["resolution"].split("x")[1]),
                    status=CameraStatus.OFFLINE
                )
                self.cameras.append(new_camera)
                self._populate_grid()
    
    def _edit_camera(self, camera_id: int):
        """
        Modifie une caméra.
        
        Args:
            camera_id: ID de la caméra
        """
        camera = next((c for c in self.cameras if c.id == camera_id), None)
        if camera:
            camera_data = camera.to_dict()
            dialog = CameraDialog(camera_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                
                if self.camera_service:
                    updated_camera = self.camera_service.update_camera(camera_id, new_data)
                    if updated_camera:
                        # Mettre à jour la liste locale
                        idx = next(i for i, c in enumerate(self.cameras) if c.id == camera_id)
                        self.cameras[idx] = updated_camera
                        self._populate_grid()
                        if self.notification_service:
                            self.notification_service.add_notification(
                                "Caméra modifiée",
                                f"La caméra {updated_camera.name} a été modifiée",
                                NotificationType.SUCCESS
                            )
    
    def _delete_camera(self, camera_id: int):
        """
        Supprime une caméra.
        
        Args:
            camera_id: ID de la caméra
        """
        from app.desktop.components.dialogs import ConfirmDialog
        
        camera = next((c for c in self.cameras if c.id == camera_id), None)
        if camera:
            dialog = ConfirmDialog(
                "Supprimer la caméra",
                f"Êtes-vous sûr de vouloir supprimer la caméra {camera.name} ?",
                self
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if self.camera_service:
                    success = self.camera_service.delete_camera(camera_id)
                    if success:
                        self.cameras = [c for c in self.cameras if c.id != camera_id]
                        self._populate_grid()
                        if self.notification_service:
                            self.notification_service.add_notification(
                                "Caméra supprimée",
                                f"La caméra {camera.name} a été supprimée",
                                NotificationType.SUCCESS
                            )
                else:
                    # Mode hors ligne
                    self.cameras = [c for c in self.cameras if c.id != camera_id]
                    self._populate_grid()
