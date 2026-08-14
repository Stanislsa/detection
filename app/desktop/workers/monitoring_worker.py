"""
Worker pour le monitoring système.
Collecte les métriques système en arrière-plan.
"""

from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QMutex, QMutexLocker, QWaitCondition
from datetime import datetime

from app.desktop.services.health_service import HealthService


class MonitoringWorker(QThread):
    """Worker pour le monitoring système."""
    
    # Signaux
    metricsUpdated = pyqtSignal()
    healthStatusChanged = pyqtSignal(str, str)  # component_type, status
    
    def __init__(self, health_service: HealthService, update_interval: int = 1000):
        super().__init__()
        self._health_service = health_service
        self._update_interval = update_interval  # ms
        self._mutex = QMutex()
        self._condition = QWaitCondition()
        self._running = False
    
    def run(self):
        """Boucle principale du worker."""
        self._running = True
        
        while self._running:
            # Mettre à jour les métriques
            self._health_service.update_all_metrics()
            
            # Émettre le signal de mise à jour
            self.metricsUpdated.emit()
            
            # Attendre l'intervalle de mise à jour
            self.msleep(self._update_interval)
    
    def stop(self):
        """Arrête le worker."""
        self._running = False
        self.wait()
