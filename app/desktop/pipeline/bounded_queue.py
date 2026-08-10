"""
File d'attente bornée pour les frames vidéo.
Évite l'accumulation des traitements avec plusieurs caméras.
"""

from typing import Optional, Any, Deque, Dict
from collections import deque
from threading import Lock, Condition
from dataclasses import dataclass
from datetime import datetime
import time

from app.core.logger import get_logger


@dataclass
class QueueMetrics:
    """Métriques de la file d'attente."""
    total_enqueued: int = 0
    total_dequeued: int = 0
    total_dropped: int = 0
    current_size: int = 0
    max_size: int = 0
    avg_wait_time_ms: float = 0.0
    peak_size: int = 0


class BoundedQueue:
    """
    File d'attente bornée avec suppression automatique des anciens éléments.
    Garantit une faible latence en limitant la taille de la file.
    """
    
    def __init__(self, max_size: int = 3, drop_policy: str = "oldest"):
        """
        Initialise la file bornée.
        
        Args:
            max_size: Taille maximale de la file
            drop_policy: Politique de suppression ("oldest", "newest", "none")
        """
        self._max_size = max_size
        self._drop_policy = drop_policy
        self._queue: Deque = deque(maxlen=max_size)
        self._lock = Lock()
        self._condition = Condition(self._lock)
        self._logger = get_logger(f"BoundedQueue.{id(self)}")
        
        # Métriques
        self._metrics = QueueMetrics(max_size=max_size)
        self._enqueue_times: Deque = deque(maxlen=1000)
    
    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Ajoute un élément à la file.
        
        Args:
            item: Élément à ajouter
            block: Si True, bloque si la file est pleine
            timeout: Timeout en secondes si block=True
        
        Returns:
            True si succès, False si l'élément a été supprimé
        """
        with self._lock:
            # Vérifier si la file est pleine
            if len(self._queue) >= self._max_size:
                if self._drop_policy == "none":
                    if block:
                        # Attendre qu'une place se libère
                        self._condition.wait(timeout)
                        if len(self._queue) >= self._max_size:
                            self._metrics.total_dropped += 1
                            return False
                    else:
                        self._metrics.total_dropped += 1
                        return False
                elif self._drop_policy == "oldest":
                    # Supprimer le plus ancien
                    dropped = self._queue.popleft()
                    self._metrics.total_dropped += 1
                    self._logger.debug(f"Élément supprimé (oldest): {type(dropped)}")
                elif self._drop_policy == "newest":
                    # Ne pas ajouter le nouvel élément
                    self._metrics.total_dropped += 1
                    self._logger.debug(f"Élément supprimé (newest): {type(item)}")
                    return False
            
            # Ajouter l'éléément
            self._queue.append(item)
            self._enqueue_times.append(datetime.now())
            self._metrics.total_enqueued += 1
            self._metrics.current_size = len(self._queue)
            self._metrics.peak_size = max(self._metrics.peak_size, len(self._queue))
            
            # Notifier les consommateurs
            self._condition.notify_all()
            
            return True
    
    def get(self, block: bool = True, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Retire et retourne un élément de la file.
        
        Args:
            block: Si True, bloque si la file est vide
            timeout: Timeout en secondes si block=True
        
        Returns:
            Élément ou None si timeout
        """
        with self._lock:
            if not self._queue:
                if block:
                    self._condition.wait(timeout)
                    if not self._queue:
                        return None
                else:
                    return None
            
            # Retirer l'élément
            item = self._queue.popleft()
            
            # Calculer le temps d'attente
            if self._enqueue_times:
                enqueue_time = self._enqueue_times.popleft()
                wait_time_ms = (datetime.now() - enqueue_time).total_seconds() * 1000
                
                # Mettre à jour le temps moyen d'attente
                self._metrics.avg_wait_time_ms = (
                    (self._metrics.avg_wait_time_ms * self._metrics.total_dequeued + wait_time_ms)
                    / (self._metrics.total_dequeued + 1)
                )
            
            self._metrics.total_dequeued += 1
            self._metrics.current_size = len(self._queue)
            
            return item
    
    def peek(self) -> Optional[Any]:
        """
        Retourne le premier élément sans le retirer.
        
        Returns:
            Premier élément ou None
        """
        with self._lock:
            return self._queue[0] if self._queue else None
    
    def size(self) -> int:
        """Retourne la taille actuelle de la file."""
        with self._lock:
            return len(self._queue)
    
    def is_empty(self) -> bool:
        """Retourne True si la file est vide."""
        with self._lock:
            return len(self._queue) == 0
    
    def is_full(self) -> bool:
        """Retourne True si la file est pleine."""
        with self._lock:
            return len(self._queue) >= self._max_size
    
    def clear(self):
        """Efface tous les éléments de la file."""
        with self._lock:
            dropped_count = len(self._queue)
            self._queue.clear()
            self._enqueue_times.clear()
            self._metrics.total_dropped += dropped_count
            self._metrics.current_size = 0
            self._logger.info(f"File effacée: {dropped_count} éléments supprimés")
    
    def get_metrics(self) -> QueueMetrics:
        """Retourne les métriques de la file."""
        with self._lock:
            self._metrics.current_size = len(self._queue)
            return self._metrics
    
    def get_drop_rate(self) -> float:
        """
        Calcule le taux de suppression.
        
        Returns:
            Taux de suppression (0.0 - 1.0)
        """
        with self._lock:
            total = self._metrics.total_enqueued
            if total == 0:
                return 0.0
            return self._metrics.total_dropped / total


class FrameQueue(BoundedQueue):
    """
    File d'attente spécialisée pour les frames vidéo.
    Inclut des métadonnées spécifiques aux frames.
    """
    
    def __init__(self, max_size: int = 3, drop_policy: str = "oldest"):
        """
        Initialise la file de frames.
        
        Args:
            max_size: Taille maximale de la file
            drop_policy: Politique de suppression
        """
        super().__init__(max_size, drop_policy)
        self._frame_counter = 0
    
    def put_frame(self, frame, frame_number: int = None, timestamp: datetime = None) -> bool:
        """
        Ajoute une frame à la file.
        
        Args:
            frame: Frame à ajouter
            frame_number: Numéro de frame (auto-incrémenté si None)
            timestamp: Timestamp de la frame (maintenant si None)
        
        Returns:
            True si succès
        """
        if frame_number is None:
            frame_number = self._frame_counter
            self._frame_counter += 1
        
        if timestamp is None:
            timestamp = datetime.now()
        
        frame_data = {
            "frame": frame,
            "frame_number": frame_number,
            "timestamp": timestamp
        }
        
        return self.put(frame_data)
    
    def get_frame(self, block: bool = True, timeout: Optional[float] = None) -> Optional[dict]:
        """
        Retire et retourne une frame de la file.
        
        Args:
            block: Si True, bloque si la file est vide
            timeout: Timeout en secondes
        
        Returns:
            Dictionnaire frame_data ou None
        """
        return self.get(block, timeout)
    
    def get_frame_count(self) -> int:
        """Retourne le nombre de frames dans la file."""
        return self.size()


class MultiQueueManager:
    """
    Gestionnaire de files d'attente multiples.
    Gère les files pour plusieurs caméras.
    """
    
    def __init__(self, default_max_size: int = 3, default_drop_policy: str = "oldest"):
        """
        Initialise le gestionnaire.
        
        Args:
            default_max_size: Taille maximale par défaut
            default_drop_policy: Politique de suppression par défaut
        """
        self._default_max_size = default_max_size
        self._default_drop_policy = default_drop_policy
        self._queues: Dict[str, FrameQueue] = {}
        self._lock = Lock()
        self._logger = get_logger("MultiQueueManager")
    
    def create_queue(self, camera_id: str, max_size: int = None, drop_policy: str = None) -> FrameQueue:
        """
        Crée une file pour une caméra.
        
        Args:
            camera_id: ID de la caméra
            max_size: Taille maximale (utilise le défaut si None)
            drop_policy: Politique de suppression (utilise le défaut si None)
        
        Returns:
            File créée
        """
        with self._lock:
            if camera_id in self._queues:
                self._logger.warning(f"File déjà existante pour {camera_id}")
                return self._queues[camera_id]
            
            queue = FrameQueue(
                max_size=max_size or self._default_max_size,
                drop_policy=drop_policy or self._default_drop_policy
            )
            self._queues[camera_id] = queue
            self._logger.info(f"File créée pour {camera_id} (max_size={queue._max_size})")
            return queue
    
    def get_queue(self, camera_id: str) -> Optional[FrameQueue]:
        """
        Retourne la file d'une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            File ou None
        """
        with self._lock:
            return self._queues.get(camera_id)
    
    def remove_queue(self, camera_id: str) -> bool:
        """
        Supprime la file d'une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            True si succès
        """
        with self._lock:
            if camera_id in self._queues:
                self._queues[camera_id].clear()
                del self._queues[camera_id]
                self._logger.info(f"File supprimée pour {camera_id}")
                return True
            return False
    
    def get_all_metrics(self) -> Dict[str, QueueMetrics]:
        """Retourne les métriques de toutes les files."""
        with self._lock:
            return {camera_id: queue.get_metrics() for camera_id, queue in self._queues.items()}
    
    def get_total_drop_rate(self) -> float:
        """
        Calcule le taux de suppression global.
        
        Returns:
            Taux de suppression (0.0 - 1.0)
        """
        metrics = self.get_all_metrics()
        
        total_enqueued = sum(m.total_enqueued for m in metrics.values())
        total_dropped = sum(m.total_dropped for m in metrics.values())
        
        if total_enqueued == 0:
            return 0.0
        
        return total_dropped / total_enqueued
    
    def clear_all(self):
        """Efface toutes les files."""
        with self._lock:
            for queue in self._queues.values():
                queue.clear()
            self._logger.info("Toutes les files effacées")
