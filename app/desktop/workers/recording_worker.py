"""
Worker pour l'enregistrement vidéo.
Utilise QThread pour ne pas bloquer l'interface lors de l'écriture des fichiers.
"""

from PyQt6.QtCore import pyqtSignal
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np

from app.desktop.workers.base_worker import BaseWorker, WorkerStatus
from app.core.logger import get_logger
from app.core.exceptions import StorageException


class RecordingWorker(BaseWorker):
    """
    Worker pour l'enregistrement vidéo.
    Gère l'écriture des frames dans un fichier vidéo.
    """
    
    # Signaux
    recording_started = pyqtSignal(str)  # file_path
    recording_stopped = pyqtSignal(str, float)  # file_path, duration_seconds
    recording_error = pyqtSignal(str)  # error message
    frame_written = pyqtSignal(int)  # frame_count
    duration_changed = pyqtSignal(float)  # duration_seconds
    
    def __init__(
        self,
        output_path: str,
        fps: int = 30,
        resolution: Tuple[int, int] = (1920, 1080),
        codec: str = "mp4v",
        parent=None
    ):
        """
        Initialise le worker d'enregistrement.
        
        Args:
            output_path: Chemin du fichier de sortie
            fps: FPS de l'enregistrement
            resolution: Résolution (width, height)
            codec: Codec vidéo (mp4v, xvid, etc.)
        """
        super().__init__(parent)
        self.output_path = output_path
        self.fps = fps
        self.resolution = resolution
        self.codec = codec
        self._writer: Optional[cv2.VideoWriter] = None
        self._frame_count = 0
        self._start_time: Optional[datetime] = None
        self._frame_queue = []
        self._max_queue_size = 100
    
    def _run_impl(self):
        """Implémentation de l'enregistrement vidéo."""
        self._logger.info(f"Démarrage enregistrement vers {self.output_path}")
        
        # Créer le dossier si nécessaire
        output_file = Path(self.output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialiser le writer
        if not self._init_writer():
            self.recording_error.emit("Impossible d'initialiser l'enregistreur")
            return
        
        self._start_time = datetime.now()
        self.recording_started.emit(self.output_path)
        
        # Boucle d'écriture
        while not self._check_stop():
            if self._check_pause():
                continue
            
            # Traiter la queue de frames
            if self._frame_queue:
                frame = self._frame_queue.pop(0)
                self._write_frame(frame)
            
            self.msleep(10)
        
        # Finaliser l'enregistrement
        self._finalize_recording()
    
    def _init_writer(self) -> bool:
        """
        Initialise le VideoWriter.
        
        Returns:
            True si succès
        """
        try:
            fourcc = cv2.VideoWriter_fourcc(*self.codec)
            self._writer = cv2.VideoWriter(
                self.output_path,
                fourcc,
                self.fps,
                self.resolution
            )
            
            if not self._writer.isOpened():
                self._logger.error("Impossible d'ouvrir le VideoWriter")
                return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Erreur initialisation VideoWriter: {e}")
            return False
    
    def _write_frame(self, frame: np.ndarray):
        """
        Écrit un frame dans le fichier.
        
        Args:
            frame: Frame à écrire
        """
        try:
            # Redimensionner si nécessaire
            if frame.shape[:2] != (self.resolution[1], self.resolution[0]):
                frame = cv2.resize(frame, self.resolution)
            
            self._writer.write(frame)
            self._frame_count += 1
            self.frame_written.emit(self._frame_count)
            
            # Mettre à jour la durée
            if self._start_time:
                duration = (datetime.now() - self._start_time).total_seconds()
                self.duration_changed.emit(duration)
            
        except Exception as e:
            self._logger.error(f"Erreur écriture frame: {e}")
    
    def add_frame(self, frame: np.ndarray):
        """
        Ajoute un frame à la queue d'enregistrement.
        
        Args:
            frame: Frame à enregistrer
        """
        if len(self._frame_queue) < self._max_queue_size:
            self._frame_queue.append(frame.copy())
        else:
            self._logger.warning("Queue de frames pleine, frame ignoré")
    
    def _finalize_recording(self):
        """Finalise l'enregistrement et ferme le fichier."""
        if self._writer is not None:
            self._writer.release()
            self._writer = None
        
        duration = 0.0
        if self._start_time:
            duration = (datetime.now() - self._start_time).total_seconds()
        
        self.recording_stopped.emit(self.output_path, duration)
        self._logger.info(f"Enregistrement terminé: {self._frame_count} frames, {duration:.2f}s")
    
    def get_frame_count(self) -> int:
        """Retourne le nombre de frames enregistrées."""
        return self._frame_count
    
    def get_duration(self) -> float:
        """Retourne la durée de l'enregistrement."""
        if self._start_time:
            return (datetime.now() - self._start_time).total_seconds()
        return 0.0
    
    def stop(self):
        """Arrête l'enregistrement."""
        super().stop()
        self._finalize_recording()


class SnapshotWorker(BaseWorker):
    """
    Worker pour la capture de snapshots (images individuelles).
    """
    
    # Signaux
    snapshot_saved = pyqtSignal(str)  # file_path
    snapshot_error = pyqtSignal(str)  # error message
    
    def __init__(self, output_path: str, parent=None):
        """
        Initialise le worker de snapshot.
        
        Args:
            output_path: Chemin du fichier de sortie
        """
        super().__init__(parent)
        self.output_path = output_path
    
    def _run_impl(self):
        """Implémentation de la capture de snapshot."""
        # Ce worker est utilisé pour des captures uniques
        pass
    
    def save_snapshot(self, frame: np.ndarray) -> bool:
        """
        Sauvegarde un frame comme snapshot.
        
        Args:
            frame: Frame à sauvegarder
        
        Returns:
            True si succès
        """
        try:
            # Créer le dossier si nécessaire
            output_file = Path(self.output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarder l'image
            success = cv2.imwrite(self.output_path, frame)
            
            if success:
                self.snapshot_saved.emit(self.output_path)
                self._logger.info(f"Snapshot sauvegardé: {self.output_path}")
            else:
                self.snapshot_error.emit("Impossible d'écrire l'image")
            
            return success
            
        except Exception as e:
            self._logger.error(f"Erreur sauvegarde snapshot: {e}")
            self.snapshot_error.emit(str(e))
            return False


class RecordingManager:
    """
    Gestionnaire d'enregistrements multiples.
    Gère plusieurs workers d'enregistrement simultanés.
    """
    
    def __init__(self):
        self._recordings: Dict[str, RecordingWorker] = {}
        self._logger = get_logger(__name__)
    
    def start_recording(
        self,
        camera_id: str,
        output_path: str,
        fps: int = 30,
        resolution: Tuple[int, int] = (1920, 1080),
        codec: str = "mp4v"
    ) -> bool:
        """
        Démarre un enregistrement pour une caméra.
        
        Args:
            camera_id: ID de la caméra
            output_path: Chemin du fichier de sortie
            fps: FPS de l'enregistrement
            resolution: Résolution
            codec: Codec vidéo
        
        Returns:
            True si succès
        """
        if camera_id in self._recordings:
            self._logger.warning(f"Enregistrement déjà en cours pour {camera_id}")
            return False
        
        worker = RecordingWorker(output_path, fps, resolution, codec)
        worker.finished.connect(lambda: self._on_recording_finished(camera_id))
        worker.start()
        
        self._recordings[camera_id] = worker
        self._logger.info(f"Enregistrement démarré pour {camera_id}")
        return True
    
    def stop_recording(self, camera_id: str) -> bool:
        """
        Arrête un enregistrement pour une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            True si succès
        """
        if camera_id not in self._recordings:
            self._logger.warning(f"Aucun enregistrement en cours pour {camera_id}")
            return False
        
        worker = self._recordings[camera_id]
        worker.stop()
        worker.wait()
        
        del self._recordings[camera_id]
        self._logger.info(f"Enregistrement arrêté pour {camera_id}")
        return True
    
    def add_frame(self, camera_id: str, frame: np.ndarray):
        """
        Ajoute un frame à l'enregistrement d'une caméra.
        
        Args:
            camera_id: ID de la caméra
            frame: Frame à ajouter
        """
        if camera_id in self._recordings:
            self._recordings[camera_id].add_frame(frame)
    
    def is_recording(self, camera_id: str) -> bool:
        """
        Vérifie si une caméra est en cours d'enregistrement.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            True si en enregistrement
        """
        return camera_id in self._recordings
    
    def stop_all(self):
        """Arrête tous les enregistrements."""
        for camera_id in list(self._recordings.keys()):
            self.stop_recording(camera_id)
    
    def _on_recording_finished(self, camera_id: str):
        """Callback quand un enregistrement est terminé."""
        if camera_id in self._recordings:
            del self._recordings[camera_id]
            self._logger.info(f"Enregistrement terminé pour {camera_id}")
