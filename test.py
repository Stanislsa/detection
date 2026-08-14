import sys
import json
import secrets
import requests

from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QMessageBox,
)


# ============================================================
# CONFIGURATION
# ============================================================

WINDOW_WIDTH = 450
WINDOW_HEIGHT = 640

CONFIG_FILE = Path.home() / ".telegram_pyqt6_config.json"

# Intervalle de sondage (ms) pour détecter le scan du QR
POLL_INTERVAL_MS = 3000


# ============================================================
# GESTION DE CONFIGURATION
# ============================================================

class ConfigManager:
    """Gestion de la configuration locale."""

    def __init__(self, file_path=CONFIG_FILE):
        self.file_path = Path(file_path)

    def save(self, bot_token: str, chat_id: str, bot_username: str) -> bool:
        data = {
            "bot_token": bot_token,
            "chat_id": chat_id,
            "bot_username": bot_username,
        }
        try:
            with self.file_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            return True
        except OSError as error:
            print(f"Erreur sauvegarde : {error}")
            return False

    def load(self) -> dict:
        """Charge la configuration existante."""
        if not self.file_path.exists():
            return {}
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return {}


# ============================================================
# SERVICE TELEGRAM
# ============================================================

class TelegramService:
    """Communication avec l'API Telegram."""

    API_URL = "https://api.telegram.org/bot{}/{}"

    def __init__(self):
        self.bot_token = ""

    def set_token(self, token: str):
        self.bot_token = token.strip()

    def get_me(self):
        """Vérifie le Bot Token."""
        if not self.bot_token:
            return False, "Bot Token manquant."

        url = self.API_URL.format(self.bot_token, "getMe")

        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if response.ok and data.get("ok"):
                return True, data

            return False, data.get("description", "Erreur Telegram.")

        except requests.RequestException as error:
            return False, f"Erreur réseau : {error}"
        except ValueError:
            return False, "Réponse Telegram invalide."

    def send_message(self, chat_id: str, text: str, parse_mode: str = "Markdown"):
        """Envoie un message générique (utilisé pour les tests ET les alertes)."""
        if not self.bot_token:
            return False, "Bot Token manquant."

        if not str(chat_id).strip():
            return False, "Chat ID manquant."

        url = self.API_URL.format(self.bot_token, "sendMessage")

        payload = {
            "chat_id": str(chat_id).strip(),
            "text": text,
            "parse_mode": parse_mode,
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()

            if response.ok and data.get("ok"):
                return True, "Message envoyé avec succès."

            return False, data.get("description", "Telegram a refusé la requête.")

        except requests.RequestException as error:
            return False, f"Erreur réseau : {error}"
        except ValueError:
            return False, "Réponse Telegram invalide."

    def send_test_message(self, chat_id: str):
        return self.send_message(
            chat_id,
            "⚙️ Configuration PyQt6 validée !",
        )

    def get_updates(self, offset=None):
        """
        Récupère les dernières mises à jour reçues par le bot
        (utilisé pour détecter automatiquement le scan du QR Code).
        """
        if not self.bot_token:
            return False, "Bot Token manquant."

        url = self.API_URL.format(self.bot_token, "getUpdates")

        params = {"timeout": 0}
        if offset is not None:
            params["offset"] = offset

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if response.ok and data.get("ok"):
                return True, data.get("result", [])

            return False, data.get("description", "Erreur Telegram.")

        except requests.RequestException as error:
            return False, f"Erreur réseau : {error}"
        except ValueError:
            return False, "Réponse Telegram invalide."

    @staticmethod
    def find_start_chat(updates, start_token: str):
        """
        Parcourt les updates à la recherche du message
        '/start <token>' correspondant au QR Code affiché,
        et retourne les informations du chat correspondant.
        """
        expected = f"/start {start_token}"

        for update in updates:
            message = update.get("message") or update.get("channel_post")
            if not message:
                continue

            text = (message.get("text") or "").strip()

            if text == expected:
                chat = message.get("chat", {})
                return {
                    "chat_id": str(chat.get("id", "")),
                    "username": (
                        chat.get("username")
                        or chat.get("first_name")
                        or "utilisateur"
                    ),
                }

        return None


# ============================================================
# SERVICE D'AUTHENTIFICATION
# ============================================================

class TelegramAuthService:
    """Gestion du token de session et de l'URL Telegram."""

    def __init__(self):
        self.current_token = None
        self.authenticated_chat = None

    def generate_auth_token(self):
        """Crée un token aléatoire unique."""
        self.current_token = secrets.token_urlsafe(24)
        self.authenticated_chat = None
        return self.current_token

    def build_bot_url(self, bot_username: str) -> str:
        bot_username = bot_username.strip()

        if bot_username.startswith("@"):
            bot_username = bot_username[1:]

        if not bot_username:
            raise ValueError("Nom d'utilisateur du bot manquant.")

        if self.current_token is None:
            self.generate_auth_token()

        return f"https://t.me/{bot_username}?start={self.current_token}"

    def mark_authenticated(self, chat_info: dict):
        """Appelé quand le scan a été détecté et confirmé côté Telegram."""
        self.authenticated_chat = chat_info

    def is_authenticated(self) -> bool:
        return self.authenticated_chat is not None


# ============================================================
# WIDGET QR CODE
# ============================================================

class QRCodeWidget(QWidget):
    """
    Conteneur dédié au QR Code.

    Utilise un vrai layout (au lieu d'un positionnement manuel
    par .move()) pour rester cohérent sur toutes les plateformes
    et résolutions d'écran.
    """

    QR_SIZE = 220

    def __init__(self):
        super().__init__()

        self.setFixedSize(240, 240)

        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #394150;
                border-radius: 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.qr_label = QLabel(self)
        self.qr_label.setFixedSize(self.QR_SIZE, self.QR_SIZE)
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.show_placeholder()

    def show_placeholder(self):
        self.qr_label.setPixmap(QPixmap())  # vide le pixmap précédent
        self.qr_label.setText("QR CODE\n\nEn attente de\nconfiguration")

        self.qr_label.setStyleSheet("""
            QLabel {
                color: #555B66;
                background-color: #FFFFFF;
                border: none;
                font-size: 13px;
                font-weight: 600;
            }
        """)

    def display_qr(self, image: QImage):
        """
        Affiche le QR sans le déformer et sans créer d'effet
        de moiré.

        Le QR est généré en amont à une taille déjà proche de
        QR_SIZE (voir generer_qr_code_telegram), donc il n'y a
        normalement AUCUN redimensionnement à faire ici. S'il en
        faut malgré tout un léger, on utilise SmoothTransformation
        (jamais FastTransformation en réduction : le
        nearest-neighbor "saute" des modules du QR de façon
        irrégulière et produit exactement le bruit visuel observé
        avant ce correctif).
        """
        self.qr_label.setText("")  # efface le texte du placeholder

        pixmap = QPixmap.fromImage(image)

        if pixmap.width() != self.QR_SIZE or pixmap.height() != self.QR_SIZE:
            pixmap = pixmap.scaled(
                self.QR_SIZE,
                self.QR_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        self.qr_label.setPixmap(pixmap)

        self.qr_label.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: none;
            }
        """)


# ============================================================
# FENÊTRE PRINCIPALE
# ============================================================

class TelegramLoginWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # SERVICES
        self.config_manager = ConfigManager()
        self.telegram_service = TelegramService()
        self.auth_service = TelegramAuthService()

        # Sondage automatique du scan
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll_telegram_scan)
        self.last_update_id = None

        self.setup_window()
        self.setup_ui()
        self.load_configuration()
        self.generer_qr_code_telegram()

    # ========================================================
    # FENÊTRE
    # ========================================================

    def setup_window(self):
        self.setWindowTitle("Telegram Secure Login")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(self.get_stylesheet())

    # ========================================================
    # INTERFACE PRINCIPALE
    # ========================================================

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(6)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        self.app_title = QLabel("Telegram Secure")
        self.app_title.setObjectName("appTitle")
        header.addWidget(self.app_title)
        header.addStretch()

        self.settings_button = QPushButton("⚙")
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setFixedSize(38, 38)
        self.settings_button.clicked.connect(self.open_settings)
        header.addWidget(self.settings_button)

        main_layout.addLayout(header)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.login_tab = self.create_login_tab()
        self.settings_tab = self.create_settings_tab()

        self.tabs.addTab(self.login_tab, "Connexion")
        self.tabs.addTab(self.settings_tab, "Configuration")

        main_layout.addWidget(self.tabs)

    # ========================================================
    # ONGLET CONNEXION
    # ========================================================

    def create_login_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 8, 4, 4)
        layout.setSpacing(6)

        title = QLabel("Connexion Sécurisée")
        title.setObjectName("mainTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Authentifiez votre session avec Telegram")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        qr_layout = QHBoxLayout()
        qr_layout.setContentsMargins(0, 3, 0, 2)
        qr_layout.addStretch()
        self.qr_widget = QRCodeWidget()
        qr_layout.addWidget(self.qr_widget)
        qr_layout.addStretch()
        layout.addLayout(qr_layout)

        instruction = QLabel(
            "Scannez ce QR Code avec Telegram\npour valider votre identité"
        )
        instruction.setObjectName("instruction")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setWordWrap(True)
        layout.addWidget(instruction)

        self.status_label = QLabel("● En attente du scan...")
        self.status_label.setObjectName("statusWaiting")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.verify_button = QPushButton("Vérifier l'authentification")
        self.verify_button.setFixedHeight(46)
        self.verify_button.clicked.connect(self.verifier_authentification)
        layout.addWidget(self.verify_button)

        self.refresh_qr_button = QPushButton("Générer un nouveau QR Code")
        self.refresh_qr_button.setObjectName("secondaryButton")
        self.refresh_qr_button.setFixedHeight(40)
        self.refresh_qr_button.clicked.connect(self.generer_qr_code_telegram)
        layout.addWidget(self.refresh_qr_button)

        layout.addStretch()

        return widget

    # ========================================================
    # ONGLET CONFIGURATION
    # ========================================================

    def create_settings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 10, 8, 8)
        layout.setSpacing(9)

        title = QLabel("Configuration & Paramètres")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        description = QLabel(
            "Configurez votre bot Telegram. Le Chat ID est détecté "
            "automatiquement une fois le QR Code scanné."
        )
        description.setObjectName("description")
        description.setWordWrap(True)
        layout.addWidget(description)

        token_label = QLabel("Token du Bot Telegram")
        token_label.setObjectName("fieldLabel")
        layout.addWidget(token_label)

        token_layout = QHBoxLayout()
        token_layout.setSpacing(6)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("123456789:AA...")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        token_layout.addWidget(self.token_input)

        self.show_token_button = QPushButton("Afficher")
        self.show_token_button.setObjectName("smallButton")
        self.show_token_button.setFixedWidth(75)
        self.show_token_button.clicked.connect(self.toggle_token_visibility)
        token_layout.addWidget(self.show_token_button)

        layout.addLayout(token_layout)

        chat_label = QLabel("Chat ID de l'administrateur (auto-détecté)")
        chat_label.setObjectName("fieldLabel")
        layout.addWidget(chat_label)

        self.chat_id_input = QLineEdit()
        self.chat_id_input.setPlaceholderText("Détecté automatiquement après scan")
        layout.addWidget(self.chat_id_input)

        bot_label = QLabel("Nom d'utilisateur du bot")
        bot_label.setObjectName("fieldLabel")
        layout.addWidget(bot_label)

        self.bot_username_input = QLineEdit()
        self.bot_username_input.setPlaceholderText("Exemple : MonBot")
        layout.addWidget(self.bot_username_input)

        self.test_button = QPushButton("Tester la configuration")
        self.test_button.setFixedHeight(44)
        self.test_button.clicked.connect(self.test_configuration)
        layout.addWidget(self.test_button)

        self.save_button = QPushButton("Sauvegarder")
        self.save_button.setObjectName("secondaryButton")
        self.save_button.setFixedHeight(42)
        self.save_button.clicked.connect(self.save_configuration)
        layout.addWidget(self.save_button)

        layout.addStretch()

        return widget

    # ========================================================
    # GÉNÉRATION QR CODE (sans effet de moiré)
    # ========================================================

    def generer_qr_code_telegram(self):
        try:
            import qrcode
        except ImportError:
            QMessageBox.critical(
                self,
                "Bibliothèque manquante",
                "Installez qrcode avec :\n\npip install qrcode[pil]",
            )
            return

        bot_username = self.bot_username_input.text().strip()

        if not bot_username:
            self.qr_widget.show_placeholder()
            self.status_label.setText("● Configurez d'abord votre bot")
            self.status_label.setObjectName("statusError")
            self.refresh_status_style()
            return

        # Permet le sondage même si la configuration n'a pas encore
        # été explicitement sauvegardée.
        token_text = self.token_input.text().strip()
        if token_text:
            self.telegram_service.set_token(token_text)

        try:
            self.auth_service.generate_auth_token()
            telegram_url = self.auth_service.build_bot_url(bot_username)

            # ------------------------------------------------
            # Étape 1 : on construit un premier QR "logique"
            # pour connaître son nombre de modules, SANS se
            # soucier de la taille en pixels.
            # ------------------------------------------------
            probe = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=1,
                border=4,
            )
            probe.add_data(telegram_url)
            probe.make(fit=True)

            modules_count = probe.modules_count + 2 * probe.border

            # ------------------------------------------------
            # Étape 2 : on choisit un box_size qui produit une
            # image DÉJÀ proche de la taille cible (220px), pour
            # éviter tout redimensionnement destructeur ensuite.
            # C'est la vraie cause du QR "brouillé" : un QR généré
            # à ~300px puis compressé à 220px avec un algorithme
            # nearest-neighbor (FastTransformation) saute des
            # modules de façon irrégulière -> effet de moiré/bruit.
            # ------------------------------------------------
            target_size = QRCodeWidget.QR_SIZE
            box_size = max(1, target_size // modules_count)

            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=box_size,
                border=4,
            )
            qr.add_data(telegram_url)
            qr.make(fit=True)

            pil_image = qr.make_image(
                fill_color="black", back_color="white"
            ).convert("RGB")

            image_data = pil_image.tobytes("raw", "RGB")

            qimage = QImage(
                image_data,
                pil_image.width,
                pil_image.height,
                pil_image.width * 3,
                QImage.Format.Format_RGB888,
            )
            qimage = qimage.copy()  # copie indépendante du buffer PIL

            self.qr_widget.display_qr(qimage)

            self.status_label.setText("● En attente du scan...")
            self.status_label.setObjectName("statusWaiting")
            self.refresh_status_style()

            # Réinitialise le sondage pour ce nouveau QR
            self.last_update_id = None
            self.poll_timer.stop()
            if self.telegram_service.bot_token:
                self.poll_timer.start(POLL_INTERVAL_MS)

            print("QR Telegram généré :")
            print(telegram_url)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erreur QR Code",
                f"Impossible de générer le QR Code :\n\n{error}",
            )

    # ========================================================
    # SONDAGE AUTOMATIQUE DU SCAN (capture auto du chat_id)
    # ========================================================

    def poll_telegram_scan(self):
        if not self.auth_service.current_token:
            self.poll_timer.stop()
            return

        success, updates = self.telegram_service.get_updates(
            offset=self.last_update_id
        )

        if not success:
            # Ne pas spammer de popups pendant le sondage silencieux ;
            # on se contente de log en console.
            print(f"Sondage Telegram : {updates}")
            return

        if updates:
            self.last_update_id = updates[-1]["update_id"] + 1

        result = self.telegram_service.find_start_chat(
            updates, self.auth_service.current_token
        )

        if result:
            self.poll_timer.stop()

            self.chat_id_input.setText(result["chat_id"])
            self.auth_service.mark_authenticated(result)

            self.status_label.setText(
                f"● Scan détecté — @{result['username']}"
            )
            self.status_label.setObjectName("statusSuccess")
            self.refresh_status_style()

            # Sauvegarde automatique du chat_id détecté
            self.save_configuration(silent=True)

    # ========================================================
    # VALIDATION AUTHENTIFICATION
    # ========================================================

    def verifier_authentification(self):
        if not self.auth_service.current_token:
            self.status_label.setText("● Générez d'abord un QR Code")
            self.status_label.setObjectName("statusError")
            self.refresh_status_style()
            return

        if self.auth_service.is_authenticated():
            chat = self.auth_service.authenticated_chat
            self.status_label.setText(f"● Connexion réussie — @{chat['username']}")
            self.status_label.setObjectName("statusSuccess")
        else:
            self.status_label.setText(
                "● En attente du scan... (pas encore confirmé)"
            )
            self.status_label.setObjectName("statusWaiting")

        self.refresh_status_style()

    # ========================================================
    # STYLE DU STATUT
    # ========================================================

    def refresh_status_style(self):
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.status_label.update()

    # ========================================================
    # CHARGEMENT / SAUVEGARDE CONFIGURATION
    # ========================================================

    def load_configuration(self):
        config = self.config_manager.load()

        self.token_input.setText(config.get("bot_token", ""))
        self.chat_id_input.setText(config.get("chat_id", ""))
        self.bot_username_input.setText(config.get("bot_username", ""))

        self.telegram_service.set_token(config.get("bot_token", ""))

    def save_configuration(self, silent: bool = False):
        token = self.token_input.text().strip()
        chat_id = self.chat_id_input.text().strip()
        bot_username = self.bot_username_input.text().strip()

        if not silent:
            if not token:
                QMessageBox.warning(self, "Configuration", "Veuillez renseigner le Bot Token.")
                return
            if not bot_username:
                QMessageBox.warning(self, "Configuration", "Veuillez renseigner le nom d'utilisateur du bot.")
                return

        success = self.config_manager.save(token, chat_id, bot_username)

        if not success:
            if not silent:
                QMessageBox.critical(self, "Erreur", "Impossible de sauvegarder la configuration.")
            return

        self.telegram_service.set_token(token)

        if not silent:
            self.generer_qr_code_telegram()
            QMessageBox.information(self, "Configuration", "Configuration sauvegardée.")

    # ========================================================
    # TEST TELEGRAM
    # ========================================================

    def test_configuration(self):
        token = self.token_input.text().strip()
        chat_id = self.chat_id_input.text().strip()

        if not token:
            QMessageBox.warning(self, "Configuration", "Le Bot Token est obligatoire.")
            return
        if not chat_id:
            QMessageBox.warning(
                self,
                "Configuration",
                "Le Chat ID est vide. Scannez le QR Code dans l'onglet "
                "Connexion pour le détecter automatiquement, ou saisissez-le manuellement.",
            )
            return

        self.test_button.setEnabled(False)
        QApplication.processEvents()

        try:
            self.telegram_service.set_token(token)

            success, result = self.telegram_service.get_me()
            if not success:
                QMessageBox.critical(
                    self, "Erreur Telegram", f"Bot Token invalide ou inaccessible :\n\n{result}"
                )
                return

            bot_name = result.get("result", {}).get("username", "bot")

            success, message = self.telegram_service.send_test_message(chat_id)

            if success:
                QMessageBox.information(
                    self,
                    "Configuration valide",
                    f"Connexion Telegram réussie.\n\nBot : @{bot_name}\n\n{message}",
                )
            else:
                QMessageBox.critical(self, "Erreur d'envoi", message)

        finally:
            self.test_button.setEnabled(True)

    # ========================================================
    # ALERTE / NOTIFICATION (utilisable depuis le reste de l'app)
    # ========================================================

    def envoyer_alerte(self, message: str) -> bool:
        """
        Envoie une notification vers le chat_id sauvegardé, en
        utilisant la configuration déjà validée par l'utilisateur.
        À appeler depuis n'importe où dans l'application
        (ex : détection de connexion suspecte, erreur critique, etc.).
        """
        config = self.config_manager.load()

        token = config.get("bot_token", "")
        chat_id = config.get("chat_id", "")

        if not token or not chat_id:
            print("Alerte Telegram ignorée : configuration incomplète.")
            return False

        self.telegram_service.set_token(token)
        success, info = self.telegram_service.send_message(chat_id, message)

        if not success:
            print(f"Échec de l'alerte Telegram : {info}")

        return success

    # ========================================================
    # AFFICHER / MASQUER TOKEN
    # ========================================================

    def toggle_token_visibility(self):
        if self.token_input.echoMode() == QLineEdit.EchoMode.Password:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_token_button.setText("Masquer")
        else:
            self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_token_button.setText("Afficher")

    # ========================================================
    # NAVIGATION
    # ========================================================

    def open_settings(self):
        self.tabs.setCurrentIndex(1)

    def closeEvent(self, event):
        self.poll_timer.stop()
        super().closeEvent(event)

    # ========================================================
    # STYLE QSS
    # ========================================================

    @staticmethod
    def get_stylesheet():
        return """
        QMainWindow, QWidget {
            background-color: #111318;
            color: #F2F4F8;
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 13px;
        }
        #appTitle { color: #F7F8FA; font-size: 19px; font-weight: 700; }
        #mainTitle { color: #FFFFFF; font-size: 25px; font-weight: 700; padding: 0px; }
        #sectionTitle { color: #FFFFFF; font-size: 21px; font-weight: 700; }
        #subtitle { color: #8E96A3; font-size: 12px; }
        #instruction { color: #B5BCC8; font-size: 12px; }
        #description { color: #8E96A3; font-size: 12px; }
        #fieldLabel { color: #DCE0E7; font-size: 12px; font-weight: 600; }

        QTabWidget::pane { border: none; background-color: #111318; }
        QTabBar::tab {
            background-color: #181B21; color: #8E96A3; border: none;
            padding: 9px 18px; margin-right: 3px; border-radius: 7px;
        }
        QTabBar::tab:selected { background-color: #252A33; color: #FFFFFF; }
        QTabBar::tab:hover { background-color: #20242C; color: #FFFFFF; }

        QLineEdit {
            background-color: #191C22; color: #F3F4F6; border: 1px solid #303641;
            border-radius: 8px; padding: 9px 11px;
        }
        QLineEdit:focus { border: 1px solid #4D8DFF; background-color: #1C2027; }

        QPushButton {
            background-color: #3B82F6; color: white; border: none;
            border-radius: 8px; padding: 9px 14px; font-size: 13px; font-weight: 600;
        }
        QPushButton:hover { background-color: #4B8FF7; }
        QPushButton:pressed { background-color: #2563C7; }
        QPushButton:disabled { background-color: #303641; color: #727985; }

        #secondaryButton { background-color: #1D222A; border: 1px solid #343A45; color: #DDE2EA; }
        #secondaryButton:hover { background-color: #272D36; border: 1px solid #46505E; }

        #smallButton { background-color: #242A33; color: #DDE2EA; border: 1px solid #343A45; padding: 7px; }
        #smallButton:hover { background-color: #303742; }

        #settingsButton {
            background-color: #1C2027; color: #B9C0CC; border: 1px solid #303641;
            border-radius: 9px; font-size: 17px; padding: 0px;
        }
        #settingsButton:hover { background-color: #272D36; color: white; }

        #statusWaiting { color: #F0B84B; font-weight: 600; }
        #statusSuccess { color: #43D17A; font-weight: 700; }
        #statusError { color: #FF5C69; font-weight: 700; }
        """


# ============================================================
# MAIN
# ============================================================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Telegram Secure Login")
    app.setStyle("Fusion")

    window = TelegramLoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()