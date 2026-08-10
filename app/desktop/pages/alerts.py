"""
Page Alertes avec tableau moderne, filtres et export.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QFrame, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict, Optional
from datetime import datetime

from app.desktop.models.alert import Alert, AlertSeverity, AlertStatus, AlertType
from app.desktop.components.badge import Badge
from app.desktop.components.dialogs import AlertDetailDialog


class AlertsPage(QWidget):
    """
    Page Alertes avec tableau et filtres.
    """
    
    def __init__(self, detection_service=None, notification_service=None, parent=None):
        super().__init__(parent)
        
        self.detection_service = detection_service
        self.notification_service = notification_service
        self.alerts: List[Alert] = []
        self._init_ui()
        self._load_alerts()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Titre de la page
        title_label = QLabel("Alertes")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 20pt;
                font-weight: 700;
            }
        """)
        layout.addWidget(title_label)
        
        # Barre de recherche et filtres
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)
        
        # Recherche
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Rechercher...")
        search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
                min-width: 300px;
            }
        """)
        filter_layout.addWidget(search_input)
        
        # Filtre caméra
        camera_filter = QComboBox()
        camera_filter.addItem("Toutes les caméras")
        camera_filter.setStyleSheet("""
            QComboBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
                min-width: 150px;
            }
        """)
        filter_layout.addWidget(camera_filter)
        
        # Filtre gravité
        severity_filter = QComboBox()
        severity_filter.addItem("Toutes les gravités")
        severity_filter.addItem("Critique")
        severity_filter.addItem("Élevée")
        severity_filter.addItem("Moyenne")
        severity_filter.addItem("Faible")
        severity_filter.setStyleSheet("""
            QComboBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
                min-width: 150px;
            }
        """)
        filter_layout.addWidget(severity_filter)
        
        # Filtre statut
        status_filter = QComboBox()
        status_filter.addItem("Tous les statuts")
        status_filter.addItem("Nouveau")
        status_filter.addItem("En cours")
        status_filter.addItem("Résolu")
        status_filter.addItem("Faux positif")
        status_filter.setStyleSheet("""
            QComboBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
                min-width: 150px;
            }
        """)
        filter_layout.addWidget(status_filter)
        
        filter_layout.addStretch()
        
        # Boutons d'export
        export_pdf_btn = QPushButton("📄 Export PDF")
        export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #3D3D5C;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #4A4A6A;
            }
        """)
        filter_layout.addWidget(export_pdf_btn)
        
        export_excel_btn = QPushButton("📊 Export Excel")
        export_excel_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        filter_layout.addWidget(export_excel_btn)
        
        layout.addLayout(filter_layout)
        
        # Tableau des alertes
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(7)
        self.alerts_table.setHorizontalHeaderLabels([
            "Date", "Heure", "Caméra", "Type d'alerte", "Gravité", "Statut", "Actions"
        ])
        
        self.alerts_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                gridline-color: #4A4A6A;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3D3D5C;
                color: #FFFFFF;
            }
            QTableWidget::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
            }
            QTableWidget::header {
                background-color: #2D2D44;
                border-bottom: 2px solid #4A4A6A;
                padding: 12px;
                font-weight: 600;
            }
            QTableWidget::header::section {
                background-color: #2D2D44;
                color: #FFFFFF;
                padding: 12px;
                border: none;
                border-right: 1px solid #4A4A6A;
                font-weight: 600;
            }
        """)
        
        # Configuration des colonnes
        header = self.alerts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Heure
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Caméra
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Gravité
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Statut
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Actions
        
        self.alerts_table.setAlternatingRowColors(True)
        self.alerts_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.alerts_table)
    
    def _load_alerts(self):
        """Charge les alertes depuis le service ou utilise des données d'exemple."""
        if self.detection_service:
            self.alerts = self.detection_service.get_detections()
        else:
            # Données d'exemple si pas de service
            self.alerts = [
                Alert(
                    id=1,
                    camera_id=1,
                    camera_name="Salon",
                    alert_type=AlertType.FALL,
                    severity=AlertSeverity.CRITICAL,
                    status=AlertStatus.NEW,
                    detected_at=datetime.now(),
                    confidence=0.95,
                    bbox=(100, 100, 300, 400)
                ),
                Alert(
                    id=2,
                    camera_id=2,
                    camera_name="Cuisine",
                    alert_type=AlertType.MOVEMENT,
                    severity=AlertSeverity.HIGH,
                    status=AlertStatus.IN_PROGRESS,
                    detected_at=datetime.now(),
                    confidence=0.82,
                    bbox=(50, 50, 200, 300)
                ),
            ]
        
        self._populate_table()
    
    def _populate_table(self):
        """Remplit le tableau avec les alertes."""
        self.alerts_table.setRowCount(len(self.alerts))
        
        for row, alert in enumerate(self.alerts):
            # Date
            from app.desktop.utils.formatters import format_date
            self.alerts_table.setItem(row, 0, QTableWidgetItem(format_date(alert.detected_at)))
            
            # Heure
            from app.desktop.utils.formatters import format_time
            self.alerts_table.setItem(row, 1, QTableWidgetItem(format_time(alert.detected_at)))
            
            # Caméra
            self.alerts_table.setItem(row, 2, QTableWidgetItem(alert.camera_name))
            
            # Type d'alerte
            type_names = {
                AlertType.FALL: "Chute détectée",
                AlertType.INTRUSION: "Intrusion",
                AlertType.MOVEMENT: "Mouvement suspect",
                AlertType.ABNORMAL_ACTIVITY: "Activité anormale",
                AlertType.SYSTEM: "Système"
            }
            self.alerts_table.setItem(row, 3, QTableWidgetItem(type_names.get(alert.alert_type, alert.alert_type.value)))
            
            # Gravité (badge)
            severity_widget = QWidget()
            severity_layout = QHBoxLayout(severity_widget)
            severity_layout.setContentsMargins(8, 4, 8, 4)
            
            severity_colors = {
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.HIGH: "warning",
                AlertSeverity.MEDIUM: "info",
                AlertSeverity.LOW: "success"
            }
            severity_names = {
                AlertSeverity.CRITICAL: "Critique",
                AlertSeverity.HIGH: "Élevée",
                AlertSeverity.MEDIUM: "Moyenne",
                AlertSeverity.LOW: "Faible"
            }
            badge = Badge(
                severity_names.get(alert.severity, alert.severity.value),
                severity_colors.get(alert.severity, "default")
            )
            severity_layout.addWidget(badge)
            severity_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.alerts_table.setCellWidget(row, 4, severity_widget)
            
            # Statut (badge)
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(8, 4, 8, 4)
            
            status_colors = {
                AlertStatus.NEW: "danger",
                AlertStatus.IN_PROGRESS: "warning",
                AlertStatus.RESOLVED: "success",
                AlertStatus.FALSE_POSITIVE: "default"
            }
            status_names = {
                AlertStatus.NEW: "Nouveau",
                AlertStatus.IN_PROGRESS: "En cours",
                AlertStatus.RESOLVED: "Résolu",
                AlertStatus.FALSE_POSITIVE: "Faux positif"
            }
            status_badge = Badge(
                status_names.get(alert.status, alert.status.value),
                status_colors.get(alert.status, "default")
            )
            status_layout.addWidget(status_badge)
            status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.alerts_table.setCellWidget(row, 5, status_widget)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(8, 4, 8, 4)
            
            view_btn = QPushButton("👁")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            view_btn.clicked.connect(lambda _, a=alert: self._view_alert_details(a))
            actions_layout.addWidget(view_btn)
            
            delete_btn = QPushButton("🗑")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                }
            """)
            actions_layout.addWidget(delete_btn)
            
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.alerts_table.setCellWidget(row, 6, actions_widget)
    
    def _view_alert_details(self, alert: Alert):
        """
        Affiche les détails d'une alerte.
        
        Args:
            alert: Alerte à afficher
        """
        alert_data = {
            "date": alert.detected_at.strftime("%d/%m/%Y"),
            "time": alert.detected_at.strftime("%H:%M:%S"),
            "camera": alert.camera_name,
            "type": alert.alert_type.value,
            "severity": alert.severity.value,
            "description": f"Confidence: {alert.confidence:.2f}\nBBox: {alert.bbox}"
        }
        
        dialog = AlertDetailDialog(alert_data, self)
        dialog.exec()
