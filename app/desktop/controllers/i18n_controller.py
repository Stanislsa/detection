"""
Internationalisation — catalogues JSON (fr / en).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt6.QtCore import QObject, QSettings, pyqtSignal, pyqtProperty, pyqtSlot


I18N_DIR = Path(__file__).resolve().parent.parent / "i18n"
SUPPORTED = ("fr", "en")
DEFAULT_LANG = "fr"


class I18nController(QObject):
    """Expose t(key) et changement de langue à QML."""

    languageChanged = pyqtSignal()
    catalogChanged = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None, language: str = DEFAULT_LANG):
        super().__init__(parent)
        self._settings = QSettings("SentinelAI", "Desktop")
        saved = self._settings.value("i18n/language", language)
        self._language = saved if saved in SUPPORTED else language
        self._catalogs: Dict[str, Dict[str, str]] = {}
        self._load_all()

    def _load_all(self) -> None:
        for lang in SUPPORTED:
            path = I18N_DIR / f"{lang}.json"
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._catalogs[lang] = {str(k): str(v) for k, v in data.items()}
            except Exception as exc:
                print(f"[i18n] failed to load {path}: {exc}")
                self._catalogs[lang] = {}

    def _cat(self) -> Dict[str, str]:
        return self._catalogs.get(self._language) or self._catalogs.get("en") or {}

    @pyqtProperty(str, notify=languageChanged)
    def language(self) -> str:
        return self._language

    @pyqtProperty(str, notify=languageChanged)
    def languageLabel(self) -> str:
        return "Français" if self._language == "fr" else "English"

    @pyqtProperty("QStringList", constant=True)
    def availableLanguages(self):
        return list(SUPPORTED)

    @pyqtSlot(str)
    def setLanguage(self, lang: str) -> None:
        if lang not in SUPPORTED:
            return
        if lang == self._language:
            return
        self._language = lang
        self._settings.setValue("i18n/language", lang)
        self._settings.sync()
        self.languageChanged.emit()
        self.catalogChanged.emit()

    @pyqtSlot(str, result=str)
    def t(self, key: str) -> str:
        """Traduit une clé. Fallback: en → clé brute."""
        if not key:
            return ""
        cat = self._cat()
        if key in cat:
            return cat[key]
        en = self._catalogs.get("en") or {}
        if key in en:
            return en[key]
        return key

    @pyqtSlot(str, str, result=str)
    def tf(self, key: str, **kwargs) -> str:
        """Non utilisable facilement depuis QML pour kwargs — voir format()."""
        return self.t(key)

    @pyqtSlot(str, str, str, result=str)
    def format(self, key: str, placeholder: str, value: str) -> str:
        """Remplace {placeholder} dans la chaîne traduite."""
        text = self.t(key)
        return text.replace("{" + placeholder + "}", value)

    @pyqtSlot(result="QVariantMap")
    def catalog(self) -> Dict[str, Any]:
        return dict(self._cat())

    # Raccourcis fréquents pour binding QML simple (réactifs via languageChanged)
    @pyqtProperty(str, notify=languageChanged)
    def navDashboard(self): return self.t("nav.dashboard")
    @pyqtProperty(str, notify=languageChanged)
    def navCameras(self): return self.t("nav.cameras")
    @pyqtProperty(str, notify=languageChanged)
    def navAlerts(self): return self.t("nav.alerts")
    @pyqtProperty(str, notify=languageChanged)
    def navEvents(self): return self.t("nav.events")
    @pyqtProperty(str, notify=languageChanged)
    def navUsers(self): return self.t("nav.users")
    @pyqtProperty(str, notify=languageChanged)
    def navAiTraining(self): return self.t("nav.ai_training")
    @pyqtProperty(str, notify=languageChanged)
    def navObservability(self): return self.t("nav.observability")
    @pyqtProperty(str, notify=languageChanged)
    def navSystemHealth(self): return self.t("nav.system_health")
    @pyqtProperty(str, notify=languageChanged)
    def navSettings(self): return self.t("nav.settings")
    @pyqtProperty(str, notify=languageChanged)
    def searchPlaceholder(self): return self.t("header.search_placeholder")
