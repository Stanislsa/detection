"""
Gestionnaire centralisé du stockage.
Gère l'organisation, le nettoyage et l'accès aux fichiers stockés.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import shutil
import os

from app.core.constants import (
    STORAGE_DIR_NAME,
    SNAPSHOTS_DIR,
    RECORDINGS_DIR,
    REPORTS_DIR,
    EXPORTS_DIR,
    CACHE_DIR
)
from app.core.logger import get_logger
from app.core.exceptions import StorageException


class RetentionPolicy(Enum):
    """Politiques de rétention des fichiers."""
    NEVER = "never"  # Ne jamais supprimer
    DAYS = "days"  # Supprimer après X jours
    SIZE = "size"  # Supprimer si taille > X GB
    COUNT = "count"  # Garder seulement X fichiers


@dataclass
class StoragePolicy:
    """Politique de stockage."""
    # Snapshots
    snapshots_retention_days: int = 7
    snapshots_max_count: int = 1000
    snapshots_max_size_gb: float = 5.0
    
    # Recordings
    recordings_retention_days: int = 30
    recordings_max_count: int = 100
    recordings_max_size_gb: float = 50.0
    recordings_rotation_enabled: bool = True
    
    # Reports
    reports_retention_days: int = 90
    reports_max_count: int = 50
    reports_max_size_gb: float = 1.0
    
    # Exports
    exports_retention_days: int = 30
    exports_max_count: int = 20
    exports_max_size_gb: float = 2.0
    
    # Cache
    cache_ttl_hours: int = 24
    cache_max_size_gb: float = 1.0
    
    # Global
    global_max_size_gb: float = 100.0
    auto_cleanup_enabled: bool = True
    cleanup_interval_hours: int = 24


@dataclass
class CameraQuota:
    """Quota de stockage par caméra."""
    camera_id: str
    max_recordings: int = 50
    max_recordings_size_gb: float = 10.0
    max_snapshots: int = 500
    max_snapshots_size_gb: float = 2.0


class StorageManager:
    """
    Gestionnaire de stockage avec organisation automatique et nettoyage.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._base_dir = Path.home() / STORAGE_DIR_NAME
            self._snapshots_dir = self._base_dir / SNAPSHOTS_DIR
            self._recordings_dir = self._base_dir / RECORDINGS_DIR
            self._reports_dir = self._base_dir / REPORTS_DIR
            self._exports_dir = self._base_dir / EXPORTS_DIR
            self._cache_dir = self._base_dir / CACHE_DIR
            self._logger = get_logger(__name__)
            
            # Politique de stockage
            self._policy = StoragePolicy()
            self._camera_quotas: Dict[str, CameraQuota] = {}
            
            self._initialized = True
            self._ensure_directories()
    
    def _ensure_directories(self):
        """Crée les répertoires de stockage s'ils n'existent pas."""
        directories = [
            self._base_dir,
            self._snapshots_dir,
            self._recordings_dir,
            self._reports_dir,
            self._exports_dir,
            self._cache_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        self._logger.info("Répertoires de stockage vérifiés")
    
    # ===== SNAPSHOTS =====
    
    def save_snapshot(self, camera_id: str, image_data: bytes, timestamp: Optional[datetime] = None) -> str:
        """
        Sauvegarde un snapshot.
        
        Args:
            camera_id: ID de la caméra
            image_data: Données de l'image
            timestamp: Timestamp du snapshot (utilise maintenant si None)
        
        Returns:
            Chemin du fichier sauvegardé
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Nom du fichier: camera_id_timestamp.jpg
        filename = f"{camera_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = self._snapshots_dir / filename
        
        try:
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            self._logger.info(f"Snapshot sauvegardé: {filepath}")
            return str(filepath)
            
        except IOError as e:
            self._logger.error(f"Erreur sauvegarde snapshot: {e}")
            raise StorageException(f"Erreur sauvegarde snapshot: {e}")
    
    def get_snapshot(self, filename: str) -> Optional[bytes]:
        """
        Récupère un snapshot.
        
        Args:
            filename: Nom du fichier
        
        Returns:
            Données de l'image ou None
        """
        filepath = self._snapshots_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except IOError as e:
            self._logger.error(f"Erreur lecture snapshot: {e}")
            return None
    
    def list_snapshots(self, camera_id: Optional[str] = None, limit: int = 100) -> List[str]:
        """
        Liste les snapshots.
        
        Args:
            camera_id: Filtrer par caméra (optionnel)
            limit: Nombre maximum de résultats
        
        Returns:
            Liste des chemins de fichiers
        """
        pattern = f"{camera_id}_*" if camera_id else "*.jpg"
        snapshots = sorted(self._snapshots_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        return [str(s) for s in snapshots[:limit]]
    
    def delete_snapshot(self, filename: str) -> bool:
        """
        Supprime un snapshot.
        
        Args:
            filename: Nom du fichier
        
        Returns:
            True si succès
        """
        filepath = self._snapshots_dir / filename
        
        if filepath.exists():
            try:
                filepath.unlink()
                self._logger.info(f"Snapshot supprimé: {filename}")
                return True
            except IOError as e:
                self._logger.error(f"Erreur suppression snapshot: {e}")
                return False
        
        return False
    
    # ===== RECORDINGS =====
    
    def save_recording(self, camera_id: str, video_data: bytes, timestamp: Optional[datetime] = None) -> str:
        """
        Sauvegarde un enregistrement vidéo.
        
        Args:
            camera_id: ID de la caméra
            video_data: Données vidéo
            timestamp: Timestamp de l'enregistrement
        
        Returns:
            Chemin du fichier sauvegardé
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Nom du fichier: camera_id_timestamp.mp4
        filename = f"{camera_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.mp4"
        filepath = self._recordings_dir / filename
        
        try:
            with open(filepath, 'wb') as f:
                f.write(video_data)
            
            self._logger.info(f"Enregistrement sauvegardé: {filepath}")
            return str(filepath)
            
        except IOError as e:
            self._logger.error(f"Erreur sauvegarde enregistrement: {e}")
            raise StorageException(f"Erreur sauvegarde enregistrement: {e}")
    
    def get_recording(self, filename: str) -> Optional[bytes]:
        """
        Récupère un enregistrement.
        
        Args:
            filename: Nom du fichier
        
        Returns:
            Données vidéo ou None
        """
        filepath = self._recordings_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except IOError as e:
            self._logger.error(f"Erreur lecture enregistrement: {e}")
            return None
    
    def list_recordings(self, camera_id: Optional[str] = None, limit: int = 50) -> List[str]:
        """
        Liste les enregistrements.
        
        Args:
            camera_id: Filtrer par caméra (optionnel)
            limit: Nombre maximum de résultats
        
        Returns:
            Liste des chemins de fichiers
        """
        pattern = f"{camera_id}_*" if camera_id else "*.mp4"
        recordings = sorted(self._recordings_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        return [str(r) for r in recordings[:limit]]
    
    def delete_recording(self, filename: str) -> bool:
        """
        Supprime un enregistrement.
        
        Args:
            filename: Nom du fichier
        
        Returns:
            True si succès
        """
        filepath = self._recordings_dir / filename
        
        if filepath.exists():
            try:
                filepath.unlink()
                self._logger.info(f"Enregistrement supprimé: {filename}")
                return True
            except IOError as e:
                self._logger.error(f"Erreur suppression enregistrement: {e}")
                return False
        
        return False
    
    # ===== REPORTS =====
    
    def save_report(self, report_name: str, report_data: str, format: str = "txt") -> str:
        """
        Sauvegarde un rapport.
        
        Args:
            report_name: Nom du rapport
            report_data: Contenu du rapport
            format: Format du fichier (txt, csv, json, pdf)
        
        Returns:
            Chemin du fichier sauvegardé
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{report_name}_{timestamp}.{format}"
        filepath = self._reports_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_data)
            
            self._logger.info(f"Rapport sauvegardé: {filepath}")
            return str(filepath)
            
        except IOError as e:
            self._logger.error(f"Erreur sauvegarde rapport: {e}")
            raise StorageException(f"Erreur sauvegarde rapport: {e}")
    
    def list_reports(self, limit: int = 50) -> List[str]:
        """
        Liste les rapports.
        
        Args:
            limit: Nombre maximum de résultats
        
        Returns:
            Liste des chemins de fichiers
        """
        reports = sorted(self._reports_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        return [str(r) for r in reports[:limit]]
    
    # ===== EXPORTS =====
    
    def save_export(self, export_name: str, export_data: bytes, format: str = "csv") -> str:
        """
        Sauvegarde un export.
        
        Args:
            export_name: Nom de l'export
            export_data: Données de l'export
            format: Format du fichier
        
        Returns:
            Chemin du fichier sauvegardé
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{export_name}_{timestamp}.{format}"
        filepath = self._exports_dir / filename
        
        try:
            with open(filepath, 'wb') as f:
                f.write(export_data)
            
            self._logger.info(f"Export sauvegardé: {filepath}")
            return str(filepath)
            
        except IOError as e:
            self._logger.error(f"Erreur sauvegarde export: {e}")
            raise StorageException(f"Erreur sauvegarde export: {e}")
    
    # ===== CACHE =====
    
    def save_cache(self, key: str, data: bytes, ttl_hours: int = 24) -> str:
        """
        Sauvegarde des données dans le cache.
        
        Args:
            key: Clé du cache
            data: Données à mettre en cache
            ttl_hours: Durée de vie en heures
        
        Returns:
            Chemin du fichier
        """
        filename = f"{key}.cache"
        filepath = self._cache_dir / filename
        
        try:
            with open(filepath, 'wb') as f:
                f.write(data)
            
            # Stocker la TTL dans un fichier séparé
            ttl_file = self._cache_dir / f"{key}.ttl"
            expiry = datetime.now() + timedelta(hours=ttl_hours)
            with open(ttl_file, 'w') as f:
                f.write(expiry.isoformat())
            
            return str(filepath)
            
        except IOError as e:
            self._logger.error(f"Erreur sauvegarde cache: {e}")
            raise StorageException(f"Erreur sauvegarde cache: {e}")
    
    def get_cache(self, key: str) -> Optional[bytes]:
        """
        Récupère des données du cache.
        
        Args:
            key: Clé du cache
        
        Returns:
            Données ou None si expiré/inexistant
        """
        filepath = self._cache_dir / f"{key}.cache"
        ttl_file = self._cache_dir / f"{key}.ttl"
        
        if not filepath.exists() or not ttl_file.exists():
            return None
        
        # Vérifier la TTL
        try:
            with open(ttl_file, 'r') as f:
                expiry = datetime.fromisoformat(f.read())
            
            if datetime.now() > expiry:
                # Cache expiré
                self.delete_cache(key)
                return None
            
            with open(filepath, 'rb') as f:
                return f.read()
                
        except (IOError, ValueError) as e:
            self._logger.error(f"Erreur lecture cache: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """
        Supprime une entrée du cache.
        
        Args:
            key: Clé du cache
        
        Returns:
            True si succès
        """
        filepath = self._cache_dir / f"{key}.cache"
        ttl_file = self._cache_dir / f"{key}.ttl"
        
        success = True
        if filepath.exists():
            try:
                filepath.unlink()
            except IOError:
                success = False
        
        if ttl_file.exists():
            try:
                ttl_file.unlink()
            except IOError:
                success = False
        
        return success
    
    # ===== NETTOYAGE =====
    
    def set_storage_policy(self, policy: StoragePolicy):
        """
        Définit la politique de stockage.
        
        Args:
            policy: Nouvelle politique de stockage
        """
        self._policy = policy
        self._logger.info("Politique de stockage mise à jour")
    
    def get_storage_policy(self) -> StoragePolicy:
        """Retourne la politique de stockage actuelle."""
        return self._policy
    
    def set_camera_quota(self, camera_id: str, quota: CameraQuota):
        """
        Définit le quota de stockage pour une caméra.
        
        Args:
            camera_id: ID de la caméra
            quota: Quota de stockage
        """
        self._camera_quotas[camera_id] = quota
        self._logger.info(f"Quota défini pour la caméra {camera_id}")
    
    def get_camera_quota(self, camera_id: str) -> Optional[CameraQuota]:
        """
        Retourne le quota d'une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            Quota ou None
        """
        return self._camera_quotas.get(camera_id)
    
    def cleanup_by_policy(self) -> Dict[str, int]:
        """
        Nettoie les fichiers selon la politique de stockage.
        
        Returns:
            Dictionnaire avec le nombre de fichiers supprimés par type
        """
        if not self._policy.auto_cleanup_enabled:
            self._logger.info("Nettoyage automatique désactivé")
            return {}
        
        results = {
            "snapshots": 0,
            "recordings": 0,
            "reports": 0,
            "exports": 0,
            "cache": 0
        }
        
        # Nettoyer les snapshots selon la politique
        results["snapshots"] = self._cleanup_snapshots_by_policy()
        
        # Nettoyer les enregistrements selon la politique
        results["recordings"] = self._cleanup_recordings_by_policy()
        
        # Nettoyer les rapports selon la politique
        results["reports"] = self._cleanup_reports_by_policy()
        
        # Nettoyer les exports selon la politique
        results["exports"] = self._cleanup_exports_by_policy()
        
        # Nettoyer le cache selon la politique
        results["cache"] = self._cleanup_cache_by_policy()
        
        # Vérifier la taille globale
        total_size = self._get_total_size_gb()
        if total_size > self._policy.global_max_size_gb:
            self._logger.warning(f"Taille globale dépassée: {total_size:.2f}GB / {self._policy.global_max_size_gb}GB")
            self._cleanup_by_global_size(results)
        
        self._logger.info(f"Nettoyage par politique terminé: {results}")
        return results
    
    def _cleanup_snapshots_by_policy(self) -> int:
        """Nettoie les snapshots selon la politique."""
        deleted = 0
        
        # Par âge
        if self._policy.snapshots_retention_days > 0:
            cutoff_date = datetime.now() - timedelta(days=self._policy.snapshots_retention_days)
            for filepath in self._snapshots_dir.glob("*.jpg"):
                if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_date:
                    try:
                        filepath.unlink()
                        deleted += 1
                    except IOError:
                        pass
        
        # Par nombre
        if self._policy.snapshots_max_count > 0:
            snapshots = sorted(self._snapshots_dir.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)
            for filepath in snapshots[self._policy.snapshots_max_count:]:
                try:
                    filepath.unlink()
                    deleted += 1
                except IOError:
                    pass
        
        # Par taille
        if self._policy.snapshots_max_size_gb > 0:
            size_gb = self._get_dir_size_gb(self._snapshots_dir)
            if size_gb > self._policy.snapshots_max_size_gb:
                snapshots = sorted(self._snapshots_dir.glob("*.jpg"), key=lambda p: p.stat().st_mtime)
                for filepath in snapshots:
                    if self._get_dir_size_gb(self._snapshots_dir) <= self._policy.snapshots_max_size_gb:
                        break
                    try:
                        filepath.unlink()
                        deleted += 1
                    except IOError:
                        pass
        
        return deleted
    
    def _cleanup_recordings_by_policy(self) -> int:
        """Nettoie les enregistrements selon la politique."""
        deleted = 0
        
        # Par âge
        if self._policy.recordings_retention_days > 0:
            cutoff_date = datetime.now() - timedelta(days=self._policy.recordings_retention_days)
            for filepath in self._recordings_dir.glob("*.mp4"):
                if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_date:
                    try:
                        filepath.unlink()
                        deleted += 1
                    except IOError:
                        pass
        
        # Par nombre
        if self._policy.recordings_max_count > 0:
            recordings = sorted(self._recordings_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
            for filepath in recordings[self._policy.recordings_max_count:]:
                try:
                    filepath.unlink()
                    deleted += 1
                except IOError:
                    pass
        
        # Par taille
        if self._policy.recordings_max_size_gb > 0:
            size_gb = self._get_dir_size_gb(self._recordings_dir)
            if size_gb > self._policy.recordings_max_size_gb:
                recordings = sorted(self._recordings_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
                for filepath in recordings:
                    if self._get_dir_size_gb(self._recordings_dir) <= self._policy.recordings_max_size_gb:
                        break
                    try:
                        filepath.unlink()
                        deleted += 1
                    except IOError:
                        pass
        
        return deleted
    
    def _cleanup_reports_by_policy(self) -> int:
        """Nettoie les rapports selon la politique."""
        deleted = 0
        
        if self._policy.reports_retention_days > 0:
            cutoff_date = datetime.now() - timedelta(days=self._policy.reports_retention_days)
            for filepath in self._reports_dir.glob("*"):
                if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_date:
                    try:
                        filepath.unlink()
                        deleted += 1
                    except IOError:
                        pass
        
        return deleted
    
    def _cleanup_exports_by_policy(self) -> int:
        """Nettoie les exports selon la politique."""
        deleted = 0
        
        if self._policy.exports_retention_days > 0:
            cutoff_date = datetime.now() - timedelta(days=self._policy.exports_retention_days)
            for filepath in self._exports_dir.glob("*"):
                if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_date:
                    try:
                        filepath.unlink()
                        deleted += 1
                    except IOError:
                        pass
        
        return deleted
    
    def _cleanup_cache_by_policy(self) -> int:
        """Nettoie le cache selon la politique."""
        deleted = 0
        
        # Par TTL
        now = datetime.now()
        for filepath in self._cache_dir.glob("*.ttl"):
            try:
                with open(filepath, 'r') as f:
                    expiry = datetime.fromisoformat(f.read())
                if now > expiry:
                    # Supprimer le cache et le TTL
                    cache_file = filepath.with_suffix('.cache')
                    if cache_file.exists():
                        cache_file.unlink()
                        deleted += 1
                    filepath.unlink()
            except (IOError, ValueError):
                pass
        
        # Par taille
        if self._policy.cache_max_size_gb > 0:
            size_gb = self._get_dir_size_gb(self._cache_dir)
            if size_gb > self._policy.cache_max_size_gb:
                for filepath in self._cache_dir.glob("*"):
                    if self._get_dir_size_gb(self._cache_dir) <= self._policy.cache_max_size_gb:
                        break
                    try:
                        filepath.unlink()
                        deleted += 1
                    except IOError:
                        pass
        
        return deleted
    
    def _cleanup_by_global_size(self, results: Dict[str, int]):
        """
        Nettoie les fichiers pour respecter la taille globale maximale.
        
        Args:
            results: Dictionnaire de résultats à mettre à jour
        """
        # Priorité: cache → exports → rapports → snapshots → enregistrements
        directories = [
            (self._cache_dir, "cache"),
            (self._exports_dir, "exports"),
            (self._reports_dir, "reports"),
            (self._snapshots_dir, "snapshots"),
            (self._recordings_dir, "recordings")
        ]
        
        for directory, key in directories:
            if self._get_total_size_gb() <= self._policy.global_max_size_gb:
                break
            
            files = sorted(directory.glob("*"), key=lambda p: p.stat().st_mtime)
            for filepath in files:
                if self._get_total_size_gb() <= self._policy.global_max_size_gb:
                    break
                try:
                    filepath.unlink()
                    results[key] += 1
                except IOError:
                    pass
    
    def cleanup_camera_quota(self, camera_id: str) -> Dict[str, int]:
        """
        Nettoie les fichiers d'une caméra selon son quota.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            Dictionnaire avec le nombre de fichiers supprimés par type
        """
        quota = self._camera_quotas.get(camera_id)
        if not quota:
            return {}
        
        results = {
            "recordings": 0,
            "snapshots": 0
        }
        
        # Nettoyer les enregistrements de la caméra
        pattern = f"{camera_id}_*.mp4"
        recordings = sorted(self._recordings_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        
        # Par nombre
        for filepath in recordings[quota.max_recordings:]:
            try:
                filepath.unlink()
                results["recordings"] += 1
            except IOError:
                pass
        
        # Par taille
        cam_recordings_size = sum(f.stat().st_size for f in self._recordings_dir.glob(pattern)) / (1024 ** 3)
        if cam_recordings_size > quota.max_recordings_size_gb:
            recordings = sorted(self._recordings_dir.glob(pattern), key=lambda p: p.stat().st_mtime)
            for filepath in recordings:
                cam_recordings_size = sum(f.stat().st_size for f in self._recordings_dir.glob(pattern)) / (1024 ** 3)
                if cam_recordings_size <= quota.max_recordings_size_gb:
                    break
                try:
                    filepath.unlink()
                    results["recordings"] += 1
                except IOError:
                    pass
        
        # Nettoyer les snapshots de la caméra
        pattern = f"{camera_id}_*.jpg"
        snapshots = sorted(self._snapshots_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        
        # Par nombre
        for filepath in snapshots[quota.max_snapshots:]:
            try:
                filepath.unlink()
                results["snapshots"] += 1
            except IOError:
                pass
        
        # Par taille
        cam_snapshots_size = sum(f.stat().st_size for f in self._snapshots_dir.glob(pattern)) / (1024 ** 3)
        if cam_snapshots_size > quota.max_snapshots_size_gb:
            snapshots = sorted(self._snapshots_dir.glob(pattern), key=lambda p: p.stat().st_mtime)
            for filepath in snapshots:
                cam_snapshots_size = sum(f.stat().st_size for f in self._snapshots_dir.glob(pattern)) / (1024 ** 3)
                if cam_snapshots_size <= quota.max_snapshots_size_gb:
                    break
                try:
                    filepath.unlink()
                    results["snapshots"] += 1
                except IOError:
                    pass
        
        self._logger.info(f"Nettoyage quota caméra {camera_id}: {results}")
        return results
    
    def _get_dir_size_gb(self, directory: Path) -> float:
        """
        Calcule la taille d'un répertoire en GB.
        
        Args:
            directory: Répertoire
        
        Returns:
            Taille en GB
        """
        total_bytes = 0
        for filepath in directory.rglob("*"):
            if filepath.is_file():
                total_bytes += filepath.stat().st_size
        return total_bytes / (1024 ** 3)
    
    def cleanup_old_files(self, days: int = 30, max_size_gb: int = 100) -> Dict[str, int]:
        """
        Nettoie les anciens fichiers (méthode legacy).
        
        Args:
            days: Âge maximum des fichiers en jours
            max_size_gb: Taille maximum en GB
        
        Returns:
            Dictionnaire avec le nombre de fichiers supprimés par type
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        results = {
            "snapshots": 0,
            "recordings": 0,
            "reports": 0,
            "exports": 0,
            "cache": 0
        }
        
        # Nettoyer les snapshots
        for filepath in self._snapshots_dir.glob("*.jpg"):
            if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_date:
                try:
                    filepath.unlink()
                    results["snapshots"] += 1
                except IOError:
                    pass
        
        # Nettoyer les enregistrements
        for filepath in self._recordings_dir.glob("*.mp4"):
            if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_date:
                try:
                    filepath.unlink()
                    results["recordings"] += 1
                except IOError:
                    pass
        
        # Nettoyer les rapports
        for filepath in self._reports_dir.glob("*"):
            if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_date:
                try:
                    filepath.unlink()
                    results["reports"] += 1
                except IOError:
                    pass
        
        # Nettoyer les exports
        for filepath in self._exports_dir.glob("*"):
            if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff_date:
                try:
                    filepath.unlink()
                    results["exports"] += 1
                except IOError:
                    pass
        
        # Nettoyer le cache (tous les fichiers)
        for filepath in self._cache_dir.glob("*"):
            try:
                filepath.unlink()
                results["cache"] += 1
            except IOError:
                pass
        
        # Vérifier la taille totale
        total_size = self._get_total_size_gb()
        if total_size > max_size_gb:
            self._logger.warning(f"Taille de stockage dépassée: {total_size:.2f}GB / {max_size_gb}GB")
            # Nettoyage supplémentaire si nécessaire
            self._cleanup_by_size(max_size_gb, results)
        
        self._logger.info(f"Nettoyage terminé: {results}")
        return results
    
    def _cleanup_by_size(self, max_size_gb: int, results: Dict[str, int]):
        """
        Nettoie les fichiers par taille.
        
        Args:
            max_size_gb: Taille maximum en GB
            results: Dictionnaire de résultats à mettre à jour
        """
        # Supprimer les enregistrements les plus anciens d'abord
        recordings = sorted(self._recordings_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
        
        for filepath in recordings:
            if self._get_total_size_gb() <= max_size_gb:
                break
            try:
                filepath.unlink()
                results["recordings"] += 1
            except IOError:
                pass
    
    def _get_total_size_gb(self) -> float:
        """
        Calcule la taille totale du stockage en GB.
        
        Returns:
            Taille en GB
        """
        total_bytes = 0
        
        for directory in [self._snapshots_dir, self._recordings_dir, self._reports_dir, self._exports_dir, self._cache_dir]:
            for filepath in directory.rglob("*"):
                if filepath.is_file():
                    total_bytes += filepath.stat().st_size
        
        return total_bytes / (1024 ** 3)
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le stockage.
        
        Returns:
            Dictionnaire d'informations
        """
        return {
            "base_dir": str(self._base_dir),
            "total_size_gb": self._get_total_size_gb(),
            "snapshots_count": len(list(self._snapshots_dir.glob("*.jpg"))),
            "recordings_count": len(list(self._recordings_dir.glob("*.mp4"))),
            "reports_count": len(list(self._reports_dir.glob("*"))),
            "exports_count": len(list(self._exports_dir.glob("*"))),
            "cache_count": len(list(self._cache_dir.glob("*")))
        }


def get_storage_manager() -> StorageManager:
    """
    Fonction utilitaire pour récupérer le StorageManager.
    
    Returns:
        Instance singleton du StorageManager
    """
    return StorageManager()
