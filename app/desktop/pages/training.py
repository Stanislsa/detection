"""
Page d'entraînement YOLO.
Interface pour la configuration, le suivi et l'export des modèles.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QDoubleSpinBox, QComboBox,
    QProgressBar, QTextEdit, QGroupBox, QFileDialog,
    QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
from typing import List

from app.ai.training_service import (
    get_training_service,
    TrainingConfig,
    TrainingMetrics
)
from app.core.logger import get_logger


class TrainingPage(QWidget):
    """
    Page d'entraînement YOLO.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.training_service = get_training_service()
        self._logger = get_logger(__name__)
        
        # Métriques
        self.metrics_history: List[TrainingMetrics] = []
        
        # Configuration callbacks
        self.training_service.set_callbacks(
            progress_callback=self._on_progress,
            metrics_callback=self._on_metrics,
            log_callback=self._on_log
        )
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("Entraînement YOLO")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_config_tab(), "Configuration")
        self.tabs.addTab(self._create_training_tab(), "Entraînement")
        self.tabs.addTab(self._create_metrics_tab(), "Métriques")
        self.tabs.addTab(self._create_export_tab(), "Export")
        layout.addWidget(self.tabs)
        
        self.setLayout(layout)
    
    def _create_config_tab(self) -> QWidget:
        """Crée l'onglet de configuration."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Dataset
        dataset_group = QGroupBox("Dataset")
        dataset_layout = QFormLayout()
        
        self.dataset_path_edit = QLineEdit()
        self.dataset_path_edit.setPlaceholderText("Chemin vers le dataset")
        dataset_browse_btn = QPushButton("Parcourir...")
        dataset_browse_btn.clicked.connect(self._browse_dataset)
        
        dataset_path_layout = QHBoxLayout()
        dataset_path_layout.addWidget(self.dataset_path_edit)
        dataset_path_layout.addWidget(dataset_browse_btn)
        
        dataset_layout.addRow("Chemin:", dataset_path_layout)
        
        self.data_yaml_edit = QLineEdit()
        self.data_yaml_edit.setPlaceholderText("data.yaml")
        dataset_layout.addRow("data.yaml:", self.data_yaml_edit)
        
        validate_btn = QPushButton("Valider le dataset")
        validate_btn.clicked.connect(self._validate_dataset)
        dataset_layout.addRow(validate_btn)
        
        self.dataset_validation_label = QLabel("")
        dataset_layout.addRow(self.dataset_validation_label)
        
        dataset_group.setLayout(dataset_layout)
        layout.addWidget(dataset_group)
        
        # Modèle
        model_group = QGroupBox("Modèle")
        model_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.training_service.get_available_models())
        model_layout.addRow("Modèle:", self.model_combo)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Hyperparamètres
        hyper_group = QGroupBox("Hyperparamètres")
        hyper_layout = QFormLayout()
        
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 1000)
        self.epochs_spin.setValue(100)
        hyper_layout.addRow("Epochs:", self.epochs_spin)
        
        self.imgsz_spin = QSpinBox()
        self.imgsz_spin.setRange(320, 1280)
        self.imgsz_spin.setValue(640)
        self.imgsz_spin.setSingleStep(32)
        hyper_layout.addRow("Taille image:", self.imgsz_spin)
        
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(1, 64)
        self.batch_spin.setValue(16)
        hyper_layout.addRow("Batch size:", self.batch_spin)
        
        self.lr_spin = QDoubleSpinBox()
        self.lr_spin.setRange(0.0001, 0.1)
        self.lr_spin.setValue(0.001)
        self.lr_spin.setSingleStep(0.0001)
        self.lr_spin.setDecimals(4)
        hyper_layout.addRow("Learning rate:", self.lr_spin)
        
        self.patience_spin = QSpinBox()
        self.patience_spin.setRange(0, 100)
        self.patience_spin.setValue(10)
        hyper_layout.addRow("Patience:", self.patience_spin)
        
        self.optimizer_combo = QComboBox()
        self.optimizer_combo.addItems(["Adam", "SGD", "AdamW"])
        hyper_layout.addRow("Optimiseur:", self.optimizer_combo)
        
        self.device_combo = QComboBox()
        self.device_combo.addItems(["cpu", "cuda", "mps"])
        hyper_layout.addRow("Device:", self.device_combo)
        
        hyper_group.setLayout(hyper_layout)
        layout.addWidget(hyper_group)
        
        # Bouton démarrer
        start_btn = QPushButton("Démarrer l'entraînement")
        start_btn.clicked.connect(self._start_training)
        layout.addWidget(start_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_training_tab(self) -> QWidget:
        """Crée l'onglet d'entraînement."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Progression
        progress_group = QGroupBox("Progression")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("En attente...")
        progress_layout.addWidget(self.progress_label)
        
        stop_btn = QPushButton("Arrêter l'entraînement")
        stop_btn.clicked.connect(self._stop_training)
        progress_layout.addWidget(stop_btn)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Logs
        logs_group = QGroupBox("Logs")
        logs_layout = QVBoxLayout()
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        logs_layout.addWidget(self.logs_text)
        
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)
        
        widget.setLayout(layout)
        return widget
    
    def _create_metrics_tab(self) -> QWidget:
        """Crée l'onglet des métriques."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tableau des métriques
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(7)
        self.metrics_table.setHorizontalHeaderLabels([
            "Epoch", "Loss", "mAP50", "mAP50-95", "Precision", "Recall", "LR"
        ])
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.metrics_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_export_tab(self) -> QWidget:
        """Crée l'onglet d'export."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Sélection du modèle
        model_group = QGroupBox("Modèle à exporter")
        model_layout = QFormLayout()
        
        self.export_model_path_edit = QLineEdit()
        self.export_model_path_edit.setPlaceholderText("Chemin vers le modèle entraîné")
        export_browse_btn = QPushButton("Parcourir...")
        export_browse_btn.clicked.connect(self._browse_export_model)
        
        export_path_layout = QHBoxLayout()
        export_path_layout.addWidget(self.export_model_path_edit)
        export_path_layout.addWidget(export_browse_btn)
        
        model_layout.addRow("Chemin:", export_path_layout)
        
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["onnx", "openvino", "torchscript"])
        model_layout.addRow("Format:", self.export_format_combo)
        
        export_btn = QPushButton("Exporter")
        export_btn.clicked.connect(self._export_model)
        model_layout.addRow(export_btn)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _browse_dataset(self):
        """Parcourt pour sélectionner le dataset."""
        path = QFileDialog.getExistingDirectory(self, "Sélectionner le dataset")
        if path:
            self.dataset_path_edit.setText(path)
            
            # Définir automatiquement data.yaml
            data_yaml = Path(path) / "data.yaml"
            if data_yaml.exists():
                self.data_yaml_edit.setText(str(data_yaml))
    
    def _browse_export_model(self):
        """Parcourt pour sélectionner le modèle à exporter."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le modèle",
            "",
            "Fichiers YOLO (*.pt);;Tous les fichiers (*.*)"
        )
        if path:
            self.export_model_path_edit.setText(path)
    
    def _validate_dataset(self):
        """Valide la structure du dataset."""
        dataset_path = self.dataset_path_edit.text()
        
        if not dataset_path:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un dataset")
            return
        
        result = self.training_service.validate_dataset(dataset_path)
        
        if result["valid"]:
            self.dataset_validation_label.setText("✓ Dataset valide")
            self.dataset_validation_label.setStyleSheet("color: green")
            
            info = f"Images train: {result.get('train_images', 0)}\n"
            info += f"Images valid: {result.get('valid_images', 0)}\n"
            if "test_images" in result:
                info += f"Images test: {result['test_images']}\n"
            
            if result["warnings"]:
                info += "\nWarnings:\n" + "\n".join(result["warnings"])
            
            QMessageBox.information(self, "Validation", info)
        else:
            self.dataset_validation_label.setText("✗ Dataset invalide")
            self.dataset_validation_label.setStyleSheet("color: red")
            
            error_msg = "Erreurs:\n" + "\n".join(result["errors"])
            QMessageBox.critical(self, "Erreur", error_msg)
    
    def _start_training(self):
        """Démarre l'entraînement."""
        dataset_path = self.dataset_path_edit.text()
        data_yaml = self.data_yaml_edit.text()
        
        if not dataset_path or not data_yaml:
            QMessageBox.warning(self, "Erreur", "Veuillez configurer le dataset")
            return
        
        # Créer la configuration
        config = TrainingConfig(
            dataset_path=dataset_path,
            data_yaml=data_yaml,
            model_name=self.model_combo.currentText(),
            epochs=self.epochs_spin.value(),
            imgsz=self.imgsz_spin.value(),
            batch=self.batch_spin.value(),
            optimizer=self.optimizer_combo.currentText(),
            lr0=self.lr_spin.value(),
            patience=self.patience_spin.value(),
            device=self.device_combo.currentText(),
            name="trained_model"
        )
        
        # Démarrer l'entraînement
        if self.training_service.start_training(config):
            self.tabs.setCurrentIndex(1)  # Onglet entraînement
            self._log("Entraînement démarré")
        else:
            QMessageBox.critical(self, "Erreur", "Impossible de démarrer l'entraînement")
    
    def _stop_training(self):
        """Arrête l'entraînement."""
        self.training_service.stop_training()
        self._log("Entraînement arrêté")
    
    def _export_model(self):
        """Exporte le modèle."""
        model_path = self.export_model_path_edit.text()
        format = self.export_format_combo.currentText()
        
        if not model_path:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un modèle")
            return
        
        if self.training_service.export_model(model_path, format):
            QMessageBox.information(self, "Succès", f"Export {format} réussi")
        else:
            QMessageBox.critical(self, "Erreur", "Échec de l'export")
    
    def _on_progress(self, current: int, total: int):
        """Callback de progression."""
        progress = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Epoch {current}/{total}")
    
    def _on_metrics(self, metrics: TrainingMetrics):
        """Callback de métriques."""
        self.metrics_history.append(metrics)
        
        # Ajouter au tableau
        row = self.metrics_table.rowCount()
        self.metrics_table.insertRow(row)
        
        self.metrics_table.setItem(row, 0, QTableWidgetItem(str(metrics.epoch)))
        self.metrics_table.setItem(row, 1, QTableWidgetItem(f"{metrics.loss:.4f}"))
        self.metrics_table.setItem(row, 2, QTableWidgetItem(f"{metrics.mAP50:.4f}"))
        self.metrics_table.setItem(row, 3, QTableWidgetItem(f"{metrics.mAP50_95:.4f}"))
        self.metrics_table.setItem(row, 4, QTableWidgetItem(f"{metrics.precision:.4f}"))
        self.metrics_table.setItem(row, 5, QTableWidgetItem(f"{metrics.recall:.4f}"))
        self.metrics_table.setItem(row, 6, QTableWidgetItem(f"{metrics.learning_rate:.6f}"))
        
        # Scroller vers le bas
        self.metrics_table.scrollToBottom()
    
    def _on_log(self, message: str):
        """Callback de log."""
        self._log(message)
    
    def _log(self, message: str):
        """Ajoute un message aux logs."""
        self.logs_text.append(message)
        self._logger.info(message)
