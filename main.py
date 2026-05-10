#!/usr/bin/env python3
"""
Russian Virtual Keyboard — PyQt6

A dark-mode GUI for typing Cyrillic using an English keyboard layout.
Supports two layouts: ЙЦУКЕН (standard) and Fonetico (QWERTY-based phonetic).
Physical keyboard input is intercepted and converted on the fly.

Requirements:
  pip install pyqt6
"""

import sys
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QKeyEvent, QPainter, QFont, QColor, QPalette, QScreen
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel,
    QButtonGroup, QRadioButton,
    QListWidget, QListWidgetItem, QFrame,
    QSizePolicy, QSpacerItem,
    QSlider, QSpinBox, QStackedWidget, QTabWidget,
)

# Import the trainer module
from trainer import RussianTypingTrainerWidget

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = "#1e1e1e"
SURFACE  = "#2a2a2a"
SURFACE2  = "#333333"
KEY_BG   = "#3c3c3c"
KEY_HOV  = "#4a4a4a"
KEY_ACT  = "#e94560"
FG       = "#e8e8e8"
FG_DIM   = "#909090"
AREA_BG  = "#141414"
GREEN    = "#2ecc71"
RED_BTN  = "#c0392b"
BLUE_BTN = "#2980b9"
ORANGE   = "#c67c00"
HIST_BG  = "#1e1e1e"
HIST_SEL = "#383838"

# ── Layouts ───────────────────────────────────────────────────────────────────
LAYOUTS: dict[str, list[list[tuple[str, str, str]]]] = {
    "ЙЦУКЕН": [
        [("й","Й","Q"),("ц","Ц","W"),("у","У","E"),("к","К","R"),("е","Е","T"),
         ("н","Н","Y"),("г","Г","U"),("ш","Ш","I"),("щ","Щ","O"),("з","З","P"),
         ("х","Х","["),("ъ","Ъ","]")],
        [("ф","Ф","A"),("ы","Ы","S"),("в","В","D"),("а","А","F"),("п","П","G"),
         ("р","Р","H"),("о","О","J"),("л","Л","K"),("д","Д","L"),("ж","Ж",";"),
         ("э","Э","'")],
        [("я","Я","Z"),("ч","Ч","X"),("с","С","C"),("м","М","V"),("и","И","B"),
         ("т","Т","N"),("ь","Ь","M"),("б","Б",","),("ю","Ю",".")],
    ],
    "Fonético": [
        [("я","Я","Q"),("в","В","W"),("е","Е","E"),("р","Р","R"),("т","Т","T"),
         ("ы","Ы","Y"),("у","У","U"),("и","И","I"),("о","О","O"),("п","П","P"),
         ("ш","Ш","["),("щ","Щ","]")],
        [("а","А","A"),("с","С","S"),("д","Д","D"),("ф","Ф","F"),("г","Г","G"),
         ("х","Х","H"),("й","Й","J"),("к","К","K"),("л","Л","L"),("э","Э",";"),
         ("ъ","Ъ","'")],
        [("з","З","Z"),("ж","Ж","X"),("ц","Ц","C"),("ч","Ч","V"),("б","Б","B"),
         ("н","Н","N"),("м","М","M"),("ь","Ь",","),("ю","Ю",".")],
    ],
}

ROW_INDENT = [0, 18, 36]

# ── QWERTY physical key mapping ────────────────────────────────────────────────
QWERTY_ROWS: list[list[Qt.Key]] = [
    [Qt.Key.Key_Q, Qt.Key.Key_W, Qt.Key.Key_E, Qt.Key.Key_R, Qt.Key.Key_T,
     Qt.Key.Key_Y, Qt.Key.Key_U, Qt.Key.Key_I, Qt.Key.Key_O, Qt.Key.Key_P,
     Qt.Key.Key_BracketLeft, Qt.Key.Key_BracketRight],
    [Qt.Key.Key_A, Qt.Key.Key_S, Qt.Key.Key_D, Qt.Key.Key_F, Qt.Key.Key_G,
     Qt.Key.Key_H, Qt.Key.Key_J, Qt.Key.Key_K, Qt.Key.Key_L,
     Qt.Key.Key_Semicolon, Qt.Key.Key_Apostrophe],
    [Qt.Key.Key_Z, Qt.Key.Key_X, Qt.Key.Key_C, Qt.Key.Key_V, Qt.Key.Key_B,
     Qt.Key.Key_N, Qt.Key.Key_M, Qt.Key.Key_Comma, Qt.Key.Key_Period],
]

def build_mapping(layout_name: str) -> dict[Qt.Key, tuple[str, str]]:
    mapping: dict[Qt.Key, tuple[str, str]] = {}
    for qt_row, layout_row in zip(QWERTY_ROWS, LAYOUTS[layout_name]):
        for qt_key, (lower, upper, _) in zip(qt_row, layout_row):
            mapping[qt_key] = (lower, upper)
    mapping[Qt.Key.Key_QuoteLeft] = ("ё", "Ё")
    return mapping

# ── Stylesheet ─────────────────────────────────────────────────────────────────
QSS = f"""
QMainWindow, QWidget#root {{ background: {BG}; }}

QTabWidget::pane {{
    background: {BG}; border: none;
}}

QTabBar::tab {{
    background: {SURFACE2}; color: {FG_DIM};
    padding: 6px 14px; margin: 2px;
    border-top-left-radius: 4px; border-top-right-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-weight: bold;
    font-size: 12px;
}}
QTabBar::tab:selected {{
    background: {KEY_ACT}; color: white;
}}
QTabBar::tab:hover:!selected {{
    background: {KEY_HOV}; color: {FG};
}}

QTextEdit {{
    background: {AREA_BG}; color: {FG};
    border: 1px solid #404040; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    padding: 8px;
    selection-background-color: {KEY_ACT};
}}
QLabel#status {{
    color: {FG_DIM}; font-size: 10px; padding: 2px 0 4px 0;
}}
QLabel#title {{
    color: {FG}; font-size: 18px; font-weight: 800;
    font-family: Consolas, "Courier New", monospace;
}}
QLabel#histTitle {{
    color: {FG}; font-size: 16px; font-weight: 700;
    font-family: Consolas, "Courier New", monospace;
    padding: 4px 0 2px 0;
}}
QLabel#kbHint {{
    color: {FG_DIM}; font-size: 9px;
    font-family: Consolas, "Courier New", monospace;
    padding: 0 0 2px 0;
}}
QRadioButton {{
    color: {FG};
    font-family: Consolas, "Courier New", monospace;
    font-size: 10px; spacing: 5px;
}}
QRadioButton::indicator {{
    width: 12px; height: 12px; border-radius: 6px;
    border: 2px solid {FG_DIM}; background: {SURFACE};
}}
QRadioButton::indicator:checked {{ background: {KEY_ACT}; border-color: {KEY_ACT}; }}

QPushButton#charKey {{
    background: {KEY_BG};
}}
QPushButton#charKey:hover   {{ background: {KEY_HOV}; }}
QPushButton#charKey:pressed {{ background: {KEY_ACT}; }}

QPushButton#wideKey {{
    background: {SURFACE2}; color: {FG}; border: 1px solid #484848;
    border-radius: 5px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px; font-weight: 600;
    letter-spacing: 1px;
}}
QPushButton#wideKey:hover   {{ background: {KEY_HOV}; color: white; border-color: #606060; }}
QPushButton#wideKey:pressed {{ background: {KEY_ACT}; color: white; border-color: {KEY_ACT}; }}

QPushButton#bsKey {{
    background: #4a2020; color: #ff8080; border: 1px solid #6a3030;
    border-radius: 5px;
    font-size: 16px; font-weight: bold;
}}
QPushButton#bsKey:hover   {{ background: #5c2828; color: #ffaaaa; border-color: #884040; }}
QPushButton#bsKey:pressed {{ background: {KEY_ACT}; color: white; border-color: {KEY_ACT}; }}

QPushButton#shiftKey {{
    background: {BLUE_BTN}; color: white; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px; font-weight: bold;
}}
QPushButton#shiftKey:hover {{ background: #3498db; }}
QPushButton#shiftKey:pressed {{ background: #217dbb; }}
QPushButton#shiftKey[active="true"] {{
    background: {KEY_ACT}; color: white;
}}

QPushButton#actionGreen {{
    background: {GREEN}; color: white; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 10px; font-weight: bold; padding: 5px 12px;
}}
QPushButton#actionGreen:hover {{ background: #3dde8a; }}

QPushButton#actionRed {{
    background: {RED_BTN}; color: white; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 10px; font-weight: bold; padding: 5px 12px;
}}
QPushButton#actionRed:hover {{ background: #e74c3c; }}

QPushButton#actionBlue {{
    background: {BLUE_BTN}; color: white; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 10px; font-weight: bold; padding: 5px 12px;
}}
QPushButton#actionBlue:hover {{ background: #3498db; }}

QPushButton#actionOrange {{
    background: {ORANGE}; color: white; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 10px; font-weight: bold; padding: 5px 12px;
}}
QPushButton#actionOrange:hover {{ background: #e09000; }}

QPushButton#histSmall {{
    background: {SURFACE2}; color: {FG_DIM}; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 9px; padding: 3px 6px;
}}
QPushButton#histSmall:hover {{ background: {KEY_HOV}; color: {FG}; }}

QListWidget {{
    background: {HIST_BG}; color: {FG}; border: 1px solid {SURFACE};
    border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px;
    outline: 0;
}}
QListWidget::item {{
    padding: 4px 6px; border-bottom: 1px solid {SURFACE};
}}
QListWidget::item:hover    {{ background: {HIST_SEL}; }}
QListWidget::item:selected {{ background: {KEY_BG}; color: {FG}; }}

QFrame#divider {{ background: {SURFACE}; }}
"""


# ── Character key ─────────────────────────────────────────────────────────────
class CharKey(QPushButton):
    def __init__(self, lower: str, upper: str, latin: str, parent=None):
        super().__init__(parent)
        self.lower = lower
        self.upper = upper
        self.latin = latin
        self._pressed = False
        self.setObjectName("charKey")
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.refresh(shift=False)

    def refresh(self, shift: bool):
        self.setText(self.upper if shift else self.lower)
        self.setToolTip(f"{self.upper if shift else self.lower}  [{self.latin}]")
        self.update()

    def mousePressEvent(self, event):
        self._pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.eraseRect(event.rect())

        is_hovered = self.testAttribute(Qt.WidgetAttribute.WA_Hover)
        bg_color = KEY_ACT if self._pressed else (KEY_HOV if is_hovered else KEY_BG)
        painter.fillRect(event.rect(), QColor(bg_color))

        main_text = self.upper if self._shift_state() else self.lower
        font_main = QFont("Consolas", 0, QFont.Weight.Black)
        key_h = self.height()
        fs = max(14, min(22, key_h // 2 - 4))
        font_main.setPixelSize(fs)
        painter.setFont(font_main)
        painter.setPen(QColor(FG if not self._pressed else "#ffffff"))
        painter.drawText(event.rect(), Qt.AlignmentFlag.AlignCenter, main_text)

        font_h = QFont("Consolas", 0, QFont.Weight.Normal)
        hs = max(7, min(10, key_h // 6))
        font_h.setPixelSize(hs)
        painter.setFont(font_h)
        painter.setPen(QColor(FG_DIM))
        r = event.rect()
        painter.drawText(r.adjusted(0, 0, -3, -2), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom, self.latin)
        painter.end()

    def _shift_state(self) -> bool:
        try:
            return self.window()._shift_active
        except AttributeError:
            return False


# ── Text area with physical keyboard mapping ───────────────────────────────────
class RussianTextEdit(QTextEdit):
    def __init__(self, get_mapping, parent=None):
        super().__init__(parent)
        self._get_mapping = get_mapping
        self._font_size = 14

    def set_font_size(self, size: int):
        self._font_size = size
        font = QFont("Consolas", size)
        font.setPixelSize(size)
        self.setFont(font)
        self.viewport().update()

    def keyPressEvent(self, event: QKeyEvent):
        mods = event.modifiers()
        key  = event.key()

        if mods & (Qt.KeyboardModifier.ControlModifier |
                   Qt.KeyboardModifier.AltModifier):
            super().keyPressEvent(event)
            return

        mapping = self._get_mapping()
        if key in mapping:
            shift = bool(mods & Qt.KeyboardModifier.ShiftModifier)
            lower, upper = mapping[key]
            self.insertPlainText(upper if shift else lower)
        else:
            super().keyPressEvent(event)


# ── Main window with tabs ─────────────────────────────────────────────────────
class RussianKeyboard(QMainWindow):

    _INITIAL_WIDTH  = 1100
    _INITIAL_HEIGHT = 650
    _HIST_PANEL_W   = 180
    _KEY_W          = 45
    _KEY_H          = 52
    _KEY_SPACING    = 3
    _ROW_INDENT     = [0, 15, 30]
    _KEY_LATIN_SIZE = 8
    _DEFAULT_FONT_SIZE = 14

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Russian Keyboard")
        
        # Get screen size and adjust window size if needed
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        win_width = min(self._INITIAL_WIDTH, screen_geometry.width() - 100)
        win_height = min(self._INITIAL_HEIGHT, screen_geometry.height() - 100)
        self.resize(win_width, win_height)
        
        # Center window
        self.setGeometry(
            (screen_geometry.width() - win_width) // 2,
            (screen_geometry.height() - win_height) // 2,
            win_width,
            win_height
        )

        self._shift_active   = False
        self._current_layout = "ЙЦУКЕН"
        self._char_keys: list[CharKey] = []
        self._yo_key: CharKey | None = None
        self._mapping: dict = build_mapping(self._current_layout)
        self._history: list[str] = []

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.setCentralWidget(self.tabs)

        # Tab 1: Keyboard
        self.keyboard_tab = QWidget()
        self.tabs.addTab(self.keyboard_tab, "⌨️ Keyboard")
        self.setup_keyboard_tab()

        # Tab 2: Trainer
        self.trainer_widget = RussianTypingTrainerWidget()
        self.tabs.addTab(self.trainer_widget, "🎯 Training")

        self.setStyleSheet(QSS)

    def setup_keyboard_tab(self):
        """Setup the original keyboard interface"""
        root = self.keyboard_tab
        root.setObjectName("root")
        
        root_h = QHBoxLayout(root)
        root_h.setContentsMargins(8, 8, 8, 8)
        root_h.setSpacing(8)

        self._left_panel = QWidget()
        self._left_panel.setObjectName("root")
        self._vbox = QVBoxLayout(self._left_panel)
        self._vbox.setContentsMargins(8, 8, 8, 6)
        self._vbox.setSpacing(6)
        root_h.addWidget(self._left_panel, 1)

        div = QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QFrame.Shape.VLine)
        div.setFixedWidth(1)
        root_h.addWidget(div)

        self._hist_panel = self._build_history_panel()
        root_h.addWidget(self._hist_panel)

        self._build_header()
        self._build_textarea()
        self._build_actions()
        self._build_keyboard_area()
        self._build_bottom_bar()
        self._build_status()

        self._draw_keyboard()

    def _on_font_size_changed(self, size: int):
        self._font_slider.blockSignals(True)
        self._font_spin.blockSignals(True)
        
        if self._font_slider.value() != size:
            self._font_slider.setValue(size)
        if self._font_spin.value() != size:
            self._font_spin.setValue(size)
        
        self._font_slider.blockSignals(False)
        self._font_spin.blockSignals(False)
        
        self._ta.set_font_size(size)
        self._ta.setFocus()

    def _build_history_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("root")
        panel.setFixedWidth(self._HIST_PANEL_W)
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(8, 10, 8, 8)
        vbox.setSpacing(5)

        title = QLabel("Historial")
        title.setObjectName("histTitle")
        vbox.addWidget(title)

        hint = QLabel("Clic para cargar")
        hint.setObjectName("kbHint")
        vbox.addWidget(hint)

        self._hist_list = QListWidget()
        self._hist_list.setWordWrap(True)
        self._hist_list.itemClicked.connect(self._load_from_history)
        vbox.addWidget(self._hist_list)

        clear_hist = QPushButton("Limpiar")
        clear_hist.setObjectName("histSmall")
        clear_hist.clicked.connect(self._clear_history)
        vbox.addWidget(clear_hist)

        return panel

    def _save_to_history(self):
        text = self._ta.toPlainText().strip()
        if not text:
            self._set_status("Nada que guardar")
            return
        if text in self._history:
            self._set_status("Ya esta en el historial")
            return
        self._history.insert(0, text)
        preview = text if len(text) <= 30 else text[:28] + "..."
        item = QListWidgetItem(preview)
        item.setData(Qt.ItemDataRole.UserRole, text)
        item.setToolTip(text)
        self._hist_list.insertItem(0, item)
        self._set_status("Guardado en historial")

    def _load_from_history(self, item: QListWidgetItem):
        full_text = item.data(Qt.ItemDataRole.UserRole)
        self._ta.setPlainText(full_text)
        self._ta.setFocus()
        self._set_status("Frase cargada desde historial")

    def _clear_history(self):
        self._history.clear()
        self._hist_list.clear()
        self._set_status("Historial limpiado")

    def _build_header(self):
        row = QHBoxLayout()
        row.setSpacing(8)

        title = QLabel("Russian Keyboard")
        title.setObjectName("title")
        row.addWidget(title)
        row.addStretch()

        self._layout_group = QButtonGroup(self)
        for name in LAYOUTS:
            rb = QRadioButton(name)
            rb.setChecked(name == self._current_layout)
            rb.toggled.connect(
                lambda checked, n=name: self._switch_layout(n) if checked else None
            )
            self._layout_group.addButton(rb)
            row.addWidget(rb)
            row.addSpacing(6)

        self._vbox.addLayout(row)

        kb_hint = QLabel("Escribe con teclado físico. Q W E... → cirílico. ` → ё")
        kb_hint.setObjectName("kbHint")
        self._vbox.addWidget(kb_hint)

    def _build_textarea(self):
        self._ta = RussianTextEdit(lambda: self._mapping)
        self._ta.setPlaceholderText("Escribe aquí...")
        self._vbox.addWidget(self._ta, 1)
        self._ta.set_font_size(self._DEFAULT_FONT_SIZE)

    def _build_actions(self):
        row = QHBoxLayout()
        row.setSpacing(6)

        copy_btn = QPushButton("Copiar")
        copy_btn.setObjectName("actionBlue")
        copy_btn.clicked.connect(self._copy)

        save_btn = QPushButton("Guardar")
        save_btn.setObjectName("actionOrange")
        save_btn.clicked.connect(self._save_to_history)

        clear_btn = QPushButton("Limpiar")
        clear_btn.setObjectName("actionRed")
        clear_btn.clicked.connect(self._clear)

        row.addWidget(copy_btn)
        row.addWidget(save_btn)

        row.addSpacing(12)
        fs_label = QLabel("Tamaño:")
        fs_label.setObjectName("kbHint")
        row.addWidget(fs_label)

        self._font_slider = QSlider(Qt.Orientation.Horizontal)
        self._font_slider.setObjectName("histSmall")
        self._font_slider.setRange(10, 36)
        self._font_slider.setValue(self._DEFAULT_FONT_SIZE)
        self._font_slider.setFixedWidth(120)
        self._font_slider.valueChanged.connect(self._on_font_size_changed)
        row.addWidget(self._font_slider)

        self._font_spin = QSpinBox()
        self._font_spin.setRange(10, 36)
        self._font_spin.setValue(self._DEFAULT_FONT_SIZE)
        self._font_spin.setFixedWidth(50)
        self._font_spin.valueChanged.connect(self._on_font_size_changed)
        row.addWidget(self._font_spin)

        row.addStretch()
        row.addWidget(clear_btn)
        self._vbox.addLayout(row)

    def _build_keyboard_area(self):
        self._kb_widget = QWidget()
        self._kb_layout = QVBoxLayout(self._kb_widget)
        self._kb_layout.setContentsMargins(0, 0, 0, 0)
        self._kb_layout.setSpacing(self._KEY_SPACING)
        self._vbox.addWidget(self._kb_widget, 1)

    def _build_bottom_bar(self):
        row = QHBoxLayout()
        row.setSpacing(self._KEY_SPACING)

        row.addStretch()

        self._shift_btn = QPushButton("⇧ Shift")
        self._shift_btn.setObjectName("shiftKey")
        self._shift_btn.setProperty("active", "false")
        self._shift_btn.clicked.connect(self._toggle_shift)
        row.addWidget(self._shift_btn)

        row.addSpacing(3)

        self._yo_key = CharKey("ё", "Ё", "`")
        self._yo_key.clicked.connect(lambda: self._emit_char(self._yo_key))
        row.addWidget(self._yo_key)

        row.addSpacing(3)

        self._space_btn = QPushButton("⎵ Пробел")
        self._space_btn.setObjectName("wideKey")
        self._space_btn.setFixedHeight(self._KEY_H)
        self._space_btn.setMinimumWidth(180)
        self._space_btn.clicked.connect(lambda: self._insert_char(" "))
        row.addWidget(self._space_btn)

        row.addSpacing(3)

        self._bs_btn = QPushButton("⌫")
        self._bs_btn.setObjectName("bsKey")
        self._bs_btn.setFixedHeight(self._KEY_H)
        self._bs_btn.setMinimumWidth(55)
        self._bs_btn.setToolTip("Borrar")
        self._bs_btn.clicked.connect(self._backspace)
        row.addWidget(self._bs_btn)

        row.addStretch()
        self._vbox.addLayout(row)

    def _build_status(self):
        self._status_lbl = QLabel("Listo")
        self._status_lbl.setObjectName("status")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._vbox.addWidget(self._status_lbl)

    def _draw_keyboard(self):
        while self._kb_layout.count():
            item = self._kb_layout.takeAt(0)
            if w := item.widget():
                w.deleteLater()
        self._char_keys.clear()

        for ri, row_data in enumerate(LAYOUTS[self._current_layout]):
            row_widget = QWidget()
            row_h = QHBoxLayout(row_widget)
            indent = self._ROW_INDENT[ri] if ri < len(self._ROW_INDENT) else 0
            row_h.setContentsMargins(0, 0, 0, 0)
            row_h.setSpacing(self._KEY_SPACING)
            row_h.addSpacing(indent)
            row_h.addStretch()
            for lower, upper, latin in row_data:
                key = CharKey(lower, upper, latin)
                key.clicked.connect(lambda _, k=key: self._emit_char(k))
                row_h.addWidget(key)
                self._char_keys.append(key)
            row_h.addStretch()
            self._kb_layout.addWidget(row_widget)

        self._refresh_all_keys()
        self._update_key_sizes()

    def _update_key_sizes(self):
        if not hasattr(self, '_left_panel') or not hasattr(self, '_kb_widget'):
            return
        total_keys = len(LAYOUTS[self._current_layout][0])
        available_w = self._left_panel.width() - 40
        key_w = max(38, min(65, (available_w - self._ROW_INDENT[-1] - (total_keys - 1) * self._KEY_SPACING) // total_keys))
        key_h = max(42, min(65, int(self._kb_widget.height() * 0.3)))

        for key in self._char_keys:
            key.setMinimumSize(key_w, key_h)
            key.setMaximumSize(key_w, key_h)

        if self._yo_key:
            self._yo_key.setMinimumSize(key_w, key_h)
            self._yo_key.setMaximumSize(key_w, key_h)

        if hasattr(self, '_shift_btn') and self._shift_btn:
            self._shift_btn.setMinimumSize(max(60, int(key_w * 1.5)), key_h)
            self._shift_btn.setMaximumSize(max(60, int(key_w * 1.5)), key_h)

        if hasattr(self, '_space_btn') and self._space_btn:
            self._space_btn.setFixedHeight(key_h)

        if hasattr(self, '_bs_btn') and self._bs_btn:
            self._bs_btn.setFixedHeight(key_h)
            self._bs_btn.setMinimumWidth(max(48, key_w))

    def _toggle_shift(self):
        self._shift_active = not self._shift_active
        self._shift_btn.setProperty("active", "true" if self._shift_active else "false")
        self._shift_btn.style().unpolish(self._shift_btn)
        self._shift_btn.style().polish(self._shift_btn)
        self._refresh_all_keys()

    def _refresh_all_keys(self):
        for k in self._char_keys:
            k.refresh(self._shift_active)
        if self._yo_key:
            self._yo_key.refresh(self._shift_active)

    def _emit_char(self, key: CharKey):
        self._insert_char(key.upper if self._shift_active else key.lower)
        if self._shift_active:
            self._toggle_shift()

    def _insert_char(self, char: str):
        self._ta.insertPlainText(char)
        self._ta.setFocus()

    def _backspace(self):
        self._ta.textCursor().deletePreviousChar()
        self._ta.setFocus()

    def _switch_layout(self, name: str):
        self._current_layout = name
        self._mapping = build_mapping(name)
        self._draw_keyboard()

    def _clear(self):
        self._ta.clear()
        self._set_status("Texto limpiado")

    def _copy(self):
        text = self._ta.toPlainText().strip()
        if not text:
            self._set_status("Nada que copiar")
            return
        QApplication.clipboard().setText(text)
        self._set_status(f"Copiado - {len(text)} caracteres")

    def _set_status(self, msg: str):
        self._status_lbl.setText(msg)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_key_sizes)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = RussianKeyboard()
    win.show()
    sys.exit(app.exec())