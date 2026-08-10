"""
Worker de base pour les tâches asynchrones.
Utilise QThread pour éviter de bloquer l'interface PyQt6.
"""

from PyQt6.QtCore import QThread, pyqtSignal, QObject
from typing import Optional, Any
from enum import Enum

from app.core.logger import get_logger


class WorkerStatus(Enum):
    """Statut du worker."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class BaseWorker(QThread):
    """
    Worker de base avec gestion du cycle de vie et des signaux.
    """
    
    # Signaux
    started = pyqtSignal()
    finished = pyqtSignal()
    error = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    progress = pyqtSignal(int, str)  # percentage, message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._status = WorkerStatus.IDLE
        self._should_stop = False
        self._should_pause = False
        self._logger = get_logger(self.__class__.__name__)
    
    @property
    def status(self) -> WorkerStatus:
        """Retourne le statut actuel."""
        return self._status
    
    def set_status(self, status: WorkerStatus):
        """
        Définit le statut et émet le signal.
        
        Args:
            status: Nouveau statut
        """
        self._status = status
        self.status_changed.emit(status.value)
    
    def stop(self):
        """Demande l'arrêt du worker."""
        self._should_stop = True
        self._logger.info("Arrêt demandé")
    
    def pause(self):
        """Demande la pause du worker."""
        self._should_pause = True
        self.set_status(WorkerStatus.PAUSED)
        self._logger.info("Pause demandée")
    
    def resume(self):
        """Demande la reprise du worker."""
        self._should_pause = False
        self.set_status(WorkerStatus.RUNNING)
        self._logger.info("Reprise demandée")
    
    def is_running(self) -> bool:
        """Vérifie si le worker est en cours d'exécution."""
        return self._status == WorkerStatus.RUNNING
    
    def is_stopped(self) -> bool:
        """Vérifie si le worker est arrêté."""
        return self._status == WorkerStatus.STOPPED or self._should_stop
    
    def _check_stop(self) -> bool:
        """
        Vérifie si le worker doit s'arrêter.
        
        Returns:
            True si doit s'arrêter
        """
        if self._should_stop:
            self.set_status(WorkerStatus.STOPPED)
            return True
        return False
    
    def _check_pause(self) -> bool:
        """
        Vérifie si le worker est en pause et attend.
        
        Returns:
            True si en pause
        """
        while self._should_pause and not self._should_stop:
            self.msleep(100)
        return self._should_pause
    
    def run(self):
        """Méthode principale à surcharger."""
        self.set_status(WorkerStatus.RUNNING)
        self.started.emit()
        
        try:
            self._run_impl()
        except Exception as e:
            self._logger.error(f"Erreur dans le worker: {e}")
            self.error.emit(str(e))
            self.set_status(WorkerStatus.ERROR)
        finally:
            if not self._should_stop:
                self.set_status(WorkerStatus.IDLE)
            self.finished.emit()
    
    def _run_impl(self):
        """Implémentation à surcharger par les sous-classes."""
        raise NotImplementedError("Subclasses must implement _run_impl")
