"""
Provider d'images pour afficher les frames vidéo dans QML.
"""

from typing import Optional
from PyQt6.QtCore import QObject, QUrl, QSize
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtQuick import QQuickAsyncImageProvider, QQuickImageResponse, QQuickImageProvider
import io


class VideoImageResponse(QQuickImageResponse):
    """Réponse asynchrone pour les images vidéo."""
    
    def __init__(self, image: QImage):
        super().__init__()
        self._image = image
    
    def textureFactory(self):
        """Retourne la texture pour QML."""
        return self._image
    
    def image(self):
        """Retourne l'image."""
        return self._image


class VideoImageProvider(QQuickImageProvider):
    """Provider d'images pour les frames vidéo."""
    
    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Image)
        self._frames: dict = {}
    
    def set_frame(self, camera_id: str, image: QImage):
        """Stocke une frame pour une caméra."""
        self._frames[camera_id] = image.copy()
    
    def requestImage(self, id: str, size: QSize, requestedSize: QSize):
        """Retourne une image pour QML."""
        # id est le camera_id
        image = self._frames.get(id)
        
        if image is None:
            # Image vide si pas de frame
            image = QImage(1, 1, QImage.Format.Format_RGB32)
            image.fill(0, 0, 0)
        
        if requestedSize.isValid():
            image = image.scaled(requestedSize)
        
        return image, QSize(image.width(), image.height())
    
    def clear_camera(self, camera_id: str):
        """Nettoie les frames d'une caméra."""
        if camera_id in self._frames:
            del self._frames[camera_id]
