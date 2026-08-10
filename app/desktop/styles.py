"""
Styles CSS pour l'interface Desktop Surveillance IA.
Dark Mode inspiré de Windows 11.
Palette : Bleu (#2563EB), Gris foncé (#1E1E2F), Blanc, Rouge (#EF4444)
"""

STYLES = """
/* ===== COULEURS ===== */
--bg-primary: #1E1E2F;
--bg-secondary: #2D2D44;
--bg-tertiary: #3D3D5C;
--text-primary: #FFFFFF;
--text-secondary: #A0A0B0;
--accent-blue: #2563EB;
--accent-blue-hover: #1D4ED8;
--accent-red: #EF4444;
--accent-green: #10B981;
--accent-yellow: #F59E0B;
--border-color: #4A4A6A;
--shadow: rgba(0, 0, 0, 0.3);

/* ===== FENÊTRE PRINCIPALE ===== */
QMainWindow {
    background-color: #1E1E2F;
}

QWidget {
    background-color: transparent;
    color: #FFFFFF;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 10pt;
}

/* ===== SIDEBAR ===== */
Sidebar {
    background-color: #2D2D44;
    border-right: 1px solid #4A4A6A;
}

Sidebar QPushButton {
    background-color: transparent;
    border: none;
    padding: 12px 20px;
    text-align: left;
    color: #A0A0B0;
    border-radius: 8px;
    margin: 4px 12px;
    font-size: 10pt;
}

Sidebar QPushButton:hover {
    background-color: #3D3D5C;
    color: #FFFFFF;
}

Sidebar QPushButton:active {
    background-color: #2563EB;
    color: #FFFFFF;
}

Sidebar QPushButton.active {
    background-color: #2563EB;
    color: #FFFFFF;
    font-weight: 600;
}

/* ===== HEADER ===== */
Header {
    background-color: #2D2D44;
    border-bottom: 1px solid #4A4A6A;
}

Header QLabel {
    color: #FFFFFF;
    font-size: 11pt;
    font-weight: 600;
}

Header QPushButton {
    background-color: #3D3D5C;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    color: #FFFFFF;
}

Header QPushButton:hover {
    background-color: #4A4A6A;
}

/* ===== CARDS ===== */
QFrame {
    background-color: #2D2D44;
    border-radius: 12px;
    border: 1px solid #4A4A6A;
}

Card {
    background-color: #2D2D44;
    border-radius: 12px;
    border: 1px solid #4A4A6A;
    padding: 16px;
}

/* ===== BOUTONS ===== */
QPushButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 10pt;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1D4ED8;
}

QPushButton:pressed {
    background-color: #1E40AF;
}

QPushButton:disabled {
    background-color: #4A4A6A;
    color: #A0A0B0;
}

QPushButton.danger {
    background-color: #EF4444;
}

QPushButton.danger:hover {
    background-color: #DC2626;
}

QPushButton.success {
    background-color: #10B981;
}

QPushButton.success:hover {
    background-color: #059669;
}

QPushButton.secondary {
    background-color: #3D3D5C;
}

QPushButton.secondary:hover {
    background-color: #4A4A6A;
}

/* ===== INPUTS ===== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1E1E2F;
    border: 1px solid #4A4A6A;
    border-radius: 8px;
    padding: 10px 12px;
    color: #FFFFFF;
    font-size: 10pt;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #2563EB;
}

QLineEdit::placeholder, QTextEdit::placeholder {
    color: #A0A0B0;
}

/* ===== COMBO BOX ===== */
QComboBox {
    background-color: #1E1E2F;
    border: 1px solid #4A4A6A;
    border-radius: 8px;
    padding: 10px 12px;
    color: #FFFFFF;
    font-size: 10pt;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #2D2D44;
    border: 1px solid #4A4A6A;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}

/* ===== TABLES ===== */
QTableWidget {
    background-color: #1E1E2F;
    border: 1px solid #4A4A6A;
    border-radius: 8px;
    gridline-color: #4A4A6A;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #3D3D5C;
}

QTableWidget::item:selected {
    background-color: #2563EB;
    color: #FFFFFF;
}

QTableWidget::header {
    background-color: #2D2D44;
    border-bottom: 2px solid #4A4A6A;
    padding: 12px;
    font-weight: 600;
}

QTableWidget::header::section {
    background-color: #2D2D44;
    color: #FFFFFF;
    padding: 12px;
    border: none;
    border-right: 1px solid #4A4A6A;
}

/* ===== SCROLL BAR ===== */
QScrollBar:vertical {
    background-color: #2D2D44;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #4A4A6A;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5A5A7A;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #2D2D44;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #4A4A6A;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #5A5A7A;
}

/* ===== SLIDERS ===== */
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

QSlider::handle:horizontal:hover {
    background-color: #1D4ED8;
}

/* ===== CHECK BOX ===== */
QCheckBox {
    color: #FFFFFF;
    spacing: 8px;
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

QCheckBox::indicator:hover {
    border-color: #2563EB;
}

/* ===== SWITCH (Toggle) ===== */
Switch {
    background-color: #3D3D5C;
    border-radius: 12px;
}

Switch::indicator {
    width: 44px;
    height: 24px;
    border-radius: 12px;
    background-color: #3D3D5C;
}

Switch::indicator:checked {
    background-color: #2563EB;
}

/* ===== TABS ===== */
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
}

QTabBar::tab:selected {
    background-color: #2563EB;
    color: #FFFFFF;
}

QTabBar::tab:hover:!selected {
    background-color: #3D3D5C;
}

/* ===== PROGRESS BAR ===== */
QProgressBar {
    background-color: #3D3D5C;
    border-radius: 6px;
    border: none;
    height: 8px;
}

QProgressBar::chunk {
    background-color: #2563EB;
    border-radius: 6px;
}

QProgressBar.warning::chunk {
    background-color: #F59E0B;
}

QProgressBar.danger::chunk {
    background-color: #EF4444;
}

/* ===== BADGES ===== */
Badge {
    background-color: #2563EB;
    color: #FFFFFF;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 8pt;
    font-weight: 600;
}

Badge.success {
    background-color: #10B981;
}

Badge.warning {
    background-color: #F59E0B;
}

Badge.danger {
    background-color: #EF4444;
}

Badge.info {
    background-color: #3B82F6;
}

/* ===== VIDEO PLAYER ===== */
VideoPlayer {
    background-color: #000000;
    border-radius: 12px;
    border: 2px solid #4A4A6A;
}

/* ===== NOTIFICATIONS ===== */
Notification {
    background-color: #2D2D44;
    border: 1px solid #4A4A6A;
    border-radius: 12px;
    padding: 16px;
}

Notification.success {
    border-left: 4px solid #10B981;
}

Notification.warning {
    border-left: 4px solid #F59E0B;
}

Notification.danger {
    border-left: 4px solid #EF4444;
}

/* ===== SEPARATORS ===== */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #4A4A6A;
}

/* ===== TOOLTIP ===== */
QToolTip {
    background-color: #2D2D44;
    color: #FFFFFF;
    border: 1px solid #4A4A6A;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 9pt;
}

/* ===== GROUP BOX ===== */
QGroupBox {
    background-color: #2D2D44;
    border: 1px solid #4A4A6A;
    border-radius: 8px;
    margin-top: 12px;
    padding: 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: #A0A0B0;
}
"""


# Styles spécifiques pour les composants
BUTTON_PRIMARY = """
QPushButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 10pt;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #1D4ED8;
}
QPushButton:pressed {
    background-color: #1E40AF;
}
"""

BUTTON_DANGER = """
QPushButton {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 10pt;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #DC2626;
}
"""

CARD_STYLE = """
QFrame {
    background-color: #2D2D44;
    border-radius: 12px;
    border: 1px solid #4A4A6A;
}
"""

INPUT_STYLE = """
QLineEdit {
    background-color: #1E1E2F;
    border: 1px solid #4A4A6A;
    border-radius: 8px;
    padding: 10px 12px;
    color: #FFFFFF;
    font-size: 10pt;
}
QLineEdit:focus {
    border: 2px solid #2563EB;
}
"""
