"""
Page Paramètres avec sections de configuration.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QTabWidget, QLineEdit, QComboBox, QSlider, QCheckBox,
    QSpinBox, QDoubleSpinBox, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SettingsSection(QFrame):
    """
    Section de paramètres générique.
    """
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        
        self.title = title
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        self.setStyleSheet("""
            QFrame {
                background-color: #2D2D44;
                border-radius: 12px;
                border: 1px solid #4A4A6A;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14pt;
                font-weight: 600;
                margin-bottom: 16px;
            }
        """)
        layout.addWidget(title_label)


class SettingsPage(QWidget):
    """
    Page Paramètres avec onglets et sections.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Titre de la page
        title_label = QLabel("Paramètres")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 20pt;
                font-weight: 700;
            }
        """)
        layout.addWidget(title_label)
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                background-color: #1E1E2F;
            }
            QTabBar::tab {
                background-color: #2D2D44;
                color: #A0A0B0;
                padding: 12px 24px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                font-size: 10pt;
            }
            QTabBar::tab:selected {
                background-color: #2563EB;
                color: #FFFFFF;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3D3D5C;
            }
        """)
        
        # Créer les onglets
        self._create_general_tab()
        self._create_ai_tab()
        self._create_cameras_tab()
        self._create_notifications_tab()
        self._create_security_tab()
        self._create_database_tab()
        
        layout.addWidget(self.tabs)
    
    def _create_general_tab(self):
        """Crée l'onglet Général."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        # Section Thème
        theme_section = SettingsSection("Thème")
        theme_layout = QVBoxLayout()
        
        # Thème clair/sombre
        theme_label = QLabel("Mode sombre")
        theme_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        theme_layout.addWidget(theme_label)
        
        theme_switch = QCheckBox("Activer le mode sombre")
        theme_switch.setChecked(True)
        theme_switch.setStyleSheet("""
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #4A4A6A;
                border-radius: 4px;
                background-color: #1E1E2F;
            }
            QCheckBox::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        theme_layout.addWidget(theme_switch)
        
        theme_section.layout().addLayout(theme_layout)
        layout.addWidget(theme_section)
        
        # Section Langue
        language_section = SettingsSection("Langue")
        language_layout = QVBoxLayout()
        
        language_label = QLabel("Langue de l'interface")
        language_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        language_layout.addWidget(language_label)
        
        language_combo = QComboBox()
        language_combo.addItems(["Français", "English", "Español", "Deutsch"])
        language_combo.setCurrentIndex(0)
        language_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        language_layout.addWidget(language_combo)
        
        language_section.layout().addLayout(language_layout)
        layout.addWidget(language_section)
        
        layout.addStretch()
        scroll.setWidget(container)
        self.tabs.addTab(scroll, "Général")
    
    def _create_ai_tab(self):
        """Crée l'onglet IA."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        # Section Modèle
        model_section = SettingsSection("Modèle IA")
        model_layout = QVBoxLayout()
        
        # Seuil de confiance
        confidence_label = QLabel("Seuil de confiance")
        confidence_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        model_layout.addWidget(confidence_label)
        
        confidence_slider = QSlider(Qt.Orientation.Horizontal)
        confidence_slider.setRange(0, 100)
        confidence_slider.setValue(75)
        confidence_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background-color: #3D3D5C;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background-color: #2563EB;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }
        """)
        model_layout.addWidget(confidence_slider)
        
        confidence_value = QLabel("75%")
        confidence_value.setStyleSheet("color: #2563EB; font-size: 10pt; font-weight: 600;")
        model_layout.addWidget(confidence_value)
        
        model_section.layout().addLayout(model_layout)
        layout.addWidget(model_section)
        
        # Section Performance
        performance_section = SettingsSection("Performance")
        performance_layout = QVBoxLayout()
        
        # Résolution vidéo
        resolution_label = QLabel("Résolution vidéo")
        resolution_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        performance_layout.addWidget(resolution_label)
        
        resolution_combo = QComboBox()
        resolution_combo.addItems(["640x480", "1280x720 (HD)", "1920x1080 (Full HD)"])
        resolution_combo.setCurrentIndex(0)
        resolution_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        performance_layout.addWidget(resolution_combo)
        
        # Frame skipping
        skip_label = QLabel("Frame skipping (1 sur N frames)")
        skip_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        performance_layout.addWidget(skip_label)
        
        skip_spin = QSpinBox()
        skip_spin.setRange(1, 10)
        skip_spin.setValue(3)
        skip_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        performance_layout.addWidget(skip_spin)
        
        performance_section.layout().addLayout(performance_layout)
        layout.addWidget(performance_section)
        
        # Section OpenVINO
        openvino_section = SettingsSection("Optimisation OpenVINO")
        openvino_layout = QVBoxLayout()
        
        openvino_check = QCheckBox("Activer OpenVINO (accélération Intel CPU)")
        openvino_check.setChecked(True)
        openvino_check.setStyleSheet("""
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #4A4A6A;
                border-radius: 4px;
                background-color: #1E1E2F;
            }
            QCheckBox::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        openvino_layout.addWidget(openvino_check)
        
        openvino_section.layout().addLayout(openvino_layout)
        layout.addWidget(openvino_section)
        
        layout.addStretch()
        scroll.setWidget(container)
        self.tabs.addTab(scroll, "IA")
    
    def _create_cameras_tab(self):
        """Crée l'onglet Caméras."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        # Section Multi-caméra
        multi_section = SettingsSection("Multi-caméra")
        multi_layout = QVBoxLayout()
        
        multi_check = QCheckBox("Activer le mode multi-caméra")
        multi_check.setChecked(True)
        multi_check.setStyleSheet("""
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #4A4A6A;
                border-radius: 4px;
                background-color: #1E1E2F;
            }
            QCheckBox::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        multi_layout.addWidget(multi_check)
        
        # Nombre max de caméras
        max_cam_label = QLabel("Nombre maximum de caméras simultanées")
        max_cam_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        multi_layout.addWidget(max_cam_label)
        
        max_cam_spin = QSpinBox()
        max_cam_spin.setRange(1, 10)
        max_cam_spin.setValue(3)
        max_cam_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        multi_layout.addWidget(max_cam_spin)
        
        multi_section.layout().addLayout(multi_layout)
        layout.addWidget(multi_section)
        
        # Section RTSP
        rtsp_section = SettingsSection("Configuration RTSP")
        rtsp_layout = QVBoxLayout()
        
        timeout_label = QLabel("Timeout de connexion (secondes)")
        timeout_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        rtsp_layout.addWidget(timeout_label)
        
        timeout_spin = QSpinBox()
        timeout_spin.setRange(5, 60)
        timeout_spin.setValue(10)
        timeout_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        rtsp_layout.addWidget(timeout_spin)
        
        rtsp_section.layout().addLayout(rtsp_layout)
        layout.addWidget(rtsp_section)
        
        layout.addStretch()
        scroll.setWidget(container)
        self.tabs.addTab(scroll, "Caméras")
    
    def _create_notifications_tab(self):
        """Crée l'onglet Notifications."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        # Section Telegram
        telegram_section = SettingsSection("Telegram")
        telegram_layout = QVBoxLayout()
        
        telegram_check = QCheckBox("Activer les notifications Telegram")
        telegram_check.setChecked(False)
        telegram_check.setStyleSheet("""
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #4A4A6A;
                border-radius: 4px;
                background-color: #1E1E2F;
            }
            QCheckBox::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        telegram_layout.addWidget(telegram_check)
        
        bot_token_label = QLabel("Token du bot")
        bot_token_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        telegram_layout.addWidget(bot_token_label)
        
        bot_token_input = QLineEdit()
        bot_token_input.setPlaceholderText("Entrez le token du bot Telegram")
        bot_token_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        telegram_layout.addWidget(bot_token_input)
        
        chat_id_label = QLabel("Chat ID")
        chat_id_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        telegram_layout.addWidget(chat_id_label)
        
        chat_id_input = QLineEdit()
        chat_id_input.setPlaceholderText("Entrez le Chat ID")
        chat_id_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        telegram_layout.addWidget(chat_id_input)
        
        telegram_section.layout().addLayout(telegram_layout)
        layout.addWidget(telegram_section)
        
        # Section Email
        email_section = SettingsSection("Email")
        email_layout = QVBoxLayout()
        
        email_check = QCheckBox("Activer les notifications par email")
        email_check.setChecked(True)
        email_check.setStyleSheet("""
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #4A4A6A;
                border-radius: 4px;
                background-color: #1E1E2F;
            }
            QCheckBox::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        email_layout.addWidget(email_check)
        
        smtp_label = QLabel("Serveur SMTP")
        smtp_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        email_layout.addWidget(smtp_label)
        
        smtp_input = QLineEdit()
        smtp_input.setPlaceholderText("smtp.example.com")
        smtp_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        email_layout.addWidget(smtp_input)
        
        email_section.layout().addLayout(email_layout)
        layout.addWidget(email_section)
        
        layout.addStretch()
        scroll.setWidget(container)
        self.tabs.addTab(scroll, "Notifications")
    
    def _create_security_tab(self):
        """Crée l'onglet Sécurité."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        # Section MFA
        mfa_section = SettingsSection("Authentification à deux facteurs")
        mfa_layout = QVBoxLayout()
        
        mfa_check = QCheckBox("Activer MFA (TOTP)")
        mfa_check.setChecked(True)
        mfa_check.setStyleSheet("""
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #4A4A6A;
                border-radius: 4px;
                background-color: #1E1E2F;
            }
            QCheckBox::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        mfa_layout.addWidget(mfa_check)
        
        mfa_section.layout().addLayout(mfa_layout)
        layout.addWidget(mfa_section)
        
        # Section Lockout
        lockout_section = SettingsSection("Verrouillage de compte")
        lockout_layout = QVBoxLayout()
        
        attempts_label = QLabel("Nombre de tentatives avant verrouillage")
        attempts_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        lockout_layout.addWidget(attempts_label)
        
        attempts_spin = QSpinBox()
        attempts_spin.setRange(3, 10)
        attempts_spin.setValue(5)
        attempts_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        lockout_layout.addWidget(attempts_spin)
        
        duration_label = QLabel("Durée du verrouillage (minutes)")
        duration_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        lockout_layout.addWidget(duration_label)
        
        duration_spin = QSpinBox()
        duration_spin.setRange(5, 60)
        duration_spin.setValue(15)
        duration_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        lockout_layout.addWidget(duration_spin)
        
        lockout_section.layout().addLayout(lockout_layout)
        layout.addWidget(lockout_section)
        
        layout.addStretch()
        scroll.setWidget(container)
        self.tabs.addTab(scroll, "Sécurité")
    
    def _create_database_tab(self):
        """Crée l'onglet Base de données."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        # Section Sauvegarde
        backup_section = SettingsSection("Sauvegarde automatique")
        backup_layout = QVBoxLayout()
        
        backup_check = QCheckBox("Activer la sauvegarde automatique")
        backup_check.setChecked(True)
        backup_check.setStyleSheet("""
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #4A4A6A;
                border-radius: 4px;
                background-color: #1E1E2F;
            }
            QCheckBox::indicator:checked {
                background-color: #2563EB;
                border-color: #2563EB;
            }
        """)
        backup_layout.addWidget(backup_check)
        
        interval_label = QLabel("Intervalle de sauvegarde (heures)")
        interval_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        backup_layout.addWidget(interval_label)
        
        interval_spin = QSpinBox()
        interval_spin.setRange(1, 24)
        interval_spin.setValue(6)
        interval_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        backup_layout.addWidget(interval_spin)
        
        backup_section.layout().addLayout(backup_layout)
        layout.addWidget(backup_section)
        
        # Section Rétention
        retention_section = SettingsSection("Rétention des données")
        retention_layout = QVBoxLayout()
        
        retention_label = QLabel("Durée de rétention des logs (jours)")
        retention_label.setStyleSheet("color: #A0A0B0; font-size: 10pt;")
        retention_layout.addWidget(retention_label)
        
        retention_spin = QSpinBox()
        retention_spin.setRange(7, 365)
        retention_spin.setValue(30)
        retention_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1E1E2F;
                border: 1px solid #4A4A6A;
                border-radius: 8px;
                padding: 10px 12px;
                color: #FFFFFF;
                font-size: 10pt;
            }
        """)
        retention_layout.addWidget(retention_spin)
        
        retention_section.layout().addLayout(retention_layout)
        layout.addWidget(retention_section)
        
        # Bouton de sauvegarde manuelle
        backup_btn = QPushButton("💾 Sauvegarder maintenant")
        backup_btn.setStyleSheet("""
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
        layout.addWidget(backup_btn)
        
        layout.addStretch()
        scroll.setWidget(container)
        self.tabs.addTab(scroll, "Base de données")
