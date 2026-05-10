#!/usr/bin/env python3
"""
🇷🇺 Russian Virtual Keyboard — PyQt6  v2
Dark-mode GUI for typing Cyrillic on an English keyboard.

Novedades v2:
  • Mapeo de teclado físico — presiona Q/W/E... y escribe cirílico directamente
    (sigue el layout activo: ЙЦУКЕН o Fonético). Backtick (`) → ё
  • Historial de frases — guarda frases con 💾, recupéralas con un clic

Requisitos:
  pip install pyqt6 pynput
"""

import sys
import threading

from PyQt6.QtCore    import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui     import QKeyEvent
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel,
    QButtonGroup, QRadioButton,
    QListWidget, QListWidgetItem, QFrame,
)

# ── pynput (opcional) ─────────────────────────────────────────────────────────
try:
    from pynput.keyboard import Controller as _KbCtrl
    _kb = _KbCtrl()
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

# ── Paleta dark ───────────────────────────────────────────────────────────────
BG       = "#1a1a2e"
SURFACE  = "#16213e"
KEY      = "#0f3460"
HOVER    = "#1a4a80"
PRESSED  = "#e94560"
ACCENT   = "#e94560"
FG       = "#eaeaea"
DIM      = "#7a8599"
AREA_BG  = "#0d0d1a"
GREEN    = "#27ae60"
RED_BTN  = "#c0392b"
BLUE_BTN = "#2980b9"
HIST_BG  = "#12122a"
HIST_SEL = "#1e1e4a"

# ── Layouts ───────────────────────────────────────────────────────────────────
# Cada tecla: (minúscula, mayúscula, pista_latina)
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

ROW_INDENT = [0, 22, 44]

# ── Mapeo Qt.Key → posición en layout ─────────────────────────────────────────
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
    """Devuelve {Qt.Key → (minúscula, mayúscula)} para el layout activo."""
    mapping: dict[Qt.Key, tuple[str, str]] = {}
    for qt_row, layout_row in zip(QWERTY_ROWS, LAYOUTS[layout_name]):
        for qt_key, (lower, upper, _) in zip(qt_row, layout_row):
            mapping[qt_key] = (lower, upper)
    mapping[Qt.Key.Key_QuoteLeft] = ("ё", "Ё")   # backtick → ё
    return mapping

# ── Stylesheet ────────────────────────────────────────────────────────────────
QSS = f"""
QMainWindow, QWidget#root {{ background: {BG}; }}

QTextEdit {{
    background: {AREA_BG}; color: {FG};
    border: 1px solid {ACCENT}; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 14px; padding: 8px;
    selection-background-color: {ACCENT};
}}
QLabel#status {{
    color: {DIM}; font-size: 11px; padding: 2px 0 4px 0;
}}
QLabel#title {{
    color: {FG}; font-size: 14px; font-weight: bold;
    font-family: Consolas, "Courier New", monospace;
}}
QLabel#histTitle {{
    color: {FG}; font-size: 12px; font-weight: bold;
    font-family: Consolas, "Courier New", monospace;
    padding: 4px 0 2px 0;
}}
QLabel#kbHint {{
    color: {DIM}; font-size: 10px;
    font-family: Consolas, "Courier New", monospace;
    padding: 0 0 2px 0;
}}
QRadioButton {{
    color: {FG};
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px; spacing: 6px;
}}
QRadioButton::indicator {{
    width: 14px; height: 14px; border-radius: 7px;
    border: 2px solid {DIM}; background: {SURFACE};
}}
QRadioButton::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}

QPushButton#charKey {{
    background: {KEY}; color: {FG}; border: none; border-radius: 6px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px; min-width: 44px; min-height: 48px; padding: 2px;
}}
QPushButton#charKey:hover   {{ background: {HOVER}; }}
QPushButton#charKey:pressed {{ background: {PRESSED}; color: white; }}

QPushButton#shiftKey {{
    background: {KEY}; color: {FG}; border: none; border-radius: 6px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px; font-weight: bold;
    min-width: 80px; min-height: 44px; padding: 0 12px;
}}
QPushButton#shiftKey:hover {{ background: {HOVER}; }}
QPushButton#shiftKey[active="true"] {{ background: {ACCENT}; color: white; }}

QPushButton#wideKey {{
    background: {KEY}; color: {DIM}; border: none; border-radius: 6px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px; min-width: 140px; min-height: 44px;
}}
QPushButton#wideKey:hover   {{ background: {HOVER}; color: {FG}; }}
QPushButton#wideKey:pressed {{ background: {PRESSED}; color: white; }}

QPushButton#bsKey {{
    background: {KEY}; color: {FG}; border: none; border-radius: 6px;
    font-size: 16px; min-width: 52px; min-height: 44px;
}}
QPushButton#bsKey:hover   {{ background: {HOVER}; }}
QPushButton#bsKey:pressed {{ background: {PRESSED}; color: white; }}

QPushButton#actionGreen {{
    background: {GREEN}; color: white; border: none; border-radius: 5px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px; font-weight: bold; padding: 7px 14px;
}}
QPushButton#actionGreen:hover {{ background: #2ecc71; }}

QPushButton#actionRed {{
    background: {RED_BTN}; color: white; border: none; border-radius: 5px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px; font-weight: bold; padding: 7px 14px;
}}
QPushButton#actionRed:hover {{ background: #e74c3c; }}

QPushButton#actionBlue {{
    background: {BLUE_BTN}; color: white; border: none; border-radius: 5px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px; font-weight: bold; padding: 7px 14px;
}}
QPushButton#actionBlue:hover {{ background: #3498db; }}

QPushButton#actionOrange {{
    background: #c67c00; color: white; border: none; border-radius: 5px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px; font-weight: bold; padding: 7px 14px;
}}
QPushButton#actionOrange:hover {{ background: #e09000; }}

QPushButton#histSmall {{
    background: {SURFACE}; color: {DIM}; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 10px; padding: 4px 8px;
}}
QPushButton#histSmall:hover {{ background: {KEY}; color: {FG}; }}

QListWidget {{
    background: {HIST_BG}; color: {FG}; border: 1px solid {SURFACE};
    border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px;
    outline: 0;
}}
QListWidget::item {{
    padding: 6px 8px; border-bottom: 1px solid {SURFACE};
}}
QListWidget::item:hover    {{ background: {HIST_SEL}; }}
QListWidget::item:selected {{ background: {KEY}; color: {FG}; }}

QFrame#divider {{ background: {SURFACE}; }}
"""


# ── Signal bridge ─────────────────────────────────────────────────────────────
class _Bridge(QObject):
    status_signal = pyqtSignal(str)


# ── Tecla de carácter ─────────────────────────────────────────────────────────
class CharKey(QPushButton):
    def __init__(self, lower: str, upper: str, latin: str, parent=None):
        super().__init__(parent)
        self.lower = lower
        self.upper = upper
        self.latin = latin
        self.setObjectName("charKey")
        self.refresh(shift=False)

    def refresh(self, shift: bool):
        self.setText(f"{self.upper if shift else self.lower}\n{self.latin}")


# ── Text area con mapeo de teclado físico ─────────────────────────────────────
class RussianTextEdit(QTextEdit):
    """QTextEdit que intercepta teclas físicas y las convierte a cirílico."""

    def __init__(self, get_mapping, parent=None):
        super().__init__(parent)
        self._get_mapping = get_mapping   # callable → dict activo

    def keyPressEvent(self, event: QKeyEvent):
        mods = event.modifiers()
        key  = event.key()

        # Ctrl/Alt shortcuts pasan sin cambio (Ctrl+C, Ctrl+V, etc.)
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
            super().keyPressEvent(event)   # backspace, flechas, enter, etc.


# ── Ventana principal ─────────────────────────────────────────────────────────
class RussianKeyboard(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🇷🇺  Russian Virtual Keyboard")

        self._shift_active    = False
        self._current_layout  = "ЙЦУКЕН"
        self._char_keys: list[CharKey] = []
        self._yo_key: CharKey | None   = None
        self._mapping: dict            = build_mapping(self._current_layout)
        self._history: list[str]       = []

        self._bridge = _Bridge()
        self._bridge.status_signal.connect(self._set_status)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        # Layout raíz: teclado (izquierda) | historial (derecha)
        root_h = QHBoxLayout(root)
        root_h.setContentsMargins(0, 0, 0, 0)
        root_h.setSpacing(0)

        # Panel izquierdo
        left = QWidget()
        left.setObjectName("root")
        self._vbox = QVBoxLayout(left)
        self._vbox.setContentsMargins(16, 14, 16, 6)
        self._vbox.setSpacing(8)
        root_h.addWidget(left)

        # Divisor
        div = QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QFrame.Shape.VLine)
        div.setFixedWidth(1)
        root_h.addWidget(div)

        # Panel historial (derecha)
        self._hist_panel = self._build_history_panel()
        root_h.addWidget(self._hist_panel)

        self._build_header()
        self._build_textarea()
        self._build_actions()
        self._build_keyboard_area()
        self._build_bottom_bar()
        self._build_status()

        self.setStyleSheet(QSS)
        self._draw_keyboard()
        self.setFixedWidth(920)

    # ── Historial ─────────────────────────────────────────────────────────────

    def _build_history_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("root")
        panel.setFixedWidth(200)
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(10, 14, 12, 10)
        vbox.setSpacing(6)

        title = QLabel("📖  Historial")
        title.setObjectName("histTitle")
        vbox.addWidget(title)

        hint = QLabel("Clic → cargar al editor")
        hint.setObjectName("kbHint")
        vbox.addWidget(hint)

        self._hist_list = QListWidget()
        self._hist_list.setWordWrap(True)
        self._hist_list.itemClicked.connect(self._load_from_history)
        vbox.addWidget(self._hist_list)

        clear_hist = QPushButton("🗑  Limpiar historial")
        clear_hist.setObjectName("histSmall")
        clear_hist.clicked.connect(self._clear_history)
        vbox.addWidget(clear_hist)

        return panel

    def _save_to_history(self):
        text = self._ta.toPlainText().strip()
        if not text:
            self._set_status("⚠  Nada que guardar")
            return
        if text in self._history:
            self._set_status("ℹ  Ya está en el historial")
            return
        self._history.insert(0, text)
        preview = text if len(text) <= 30 else text[:28] + "…"
        item = QListWidgetItem(preview)
        item.setData(Qt.ItemDataRole.UserRole, text)   # guarda texto completo
        item.setToolTip(text)
        self._hist_list.insertItem(0, item)
        self._set_status(f"💾  Guardado en historial")

    def _load_from_history(self, item: QListWidgetItem):
        full_text = item.data(Qt.ItemDataRole.UserRole)
        self._ta.setPlainText(full_text)
        self._ta.setFocus()
        self._set_status("📖  Frase cargada desde historial")

    def _clear_history(self):
        self._history.clear()
        self._hist_list.clear()
        self._set_status("Historial limpiado")

    # ── UI sections ───────────────────────────────────────────────────────────

    def _build_header(self):
        row = QHBoxLayout()

        title = QLabel("🇷🇺  Russian Virtual Keyboard")
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
            row.addSpacing(8)

        self._vbox.addLayout(row)

        # Pista del teclado físico
        kb_hint = QLabel("⌨️  Escribe directo con tu teclado — las teclas Q W E … escriben cirílico automáticamente  •  ` → ё")
        kb_hint.setObjectName("kbHint")
        self._vbox.addWidget(kb_hint)

    def _build_textarea(self):
        self._ta = RussianTextEdit(lambda: self._mapping)
        self._ta.setFixedHeight(100)
        self._ta.setPlaceholderText("Escribe aquí con el teclado virtual o con tu teclado físico…")
        self._vbox.addWidget(self._ta)

    def _build_actions(self):
        row = QHBoxLayout()
        row.setSpacing(8)

        copy_btn = QPushButton("📋  Copiar")
        copy_btn.setObjectName("actionBlue")
        copy_btn.clicked.connect(self._copy)

        save_btn = QPushButton("💾  Guardar")
        save_btn.setObjectName("actionOrange")
        save_btn.clicked.connect(self._save_to_history)

        type_btn = QPushButton("⌨️  Type to App")
        type_btn.setObjectName("actionGreen")
        type_btn.clicked.connect(self._type_app)

        clear_btn = QPushButton("🗑  Limpiar")
        clear_btn.setObjectName("actionRed")
        clear_btn.clicked.connect(self._clear)

        row.addWidget(copy_btn)
        row.addWidget(save_btn)
        row.addWidget(type_btn)
        row.addStretch()
        row.addWidget(clear_btn)
        self._vbox.addLayout(row)

    def _build_keyboard_area(self):
        self._kb_widget = QWidget()
        self._kb_layout = QVBoxLayout(self._kb_widget)
        self._kb_layout.setContentsMargins(0, 0, 0, 0)
        self._kb_layout.setSpacing(4)
        self._vbox.addWidget(self._kb_widget)

    def _build_bottom_bar(self):
        row = QHBoxLayout()
        row.setSpacing(6)

        self._shift_btn = QPushButton("⇧  Shift")
        self._shift_btn.setObjectName("shiftKey")
        self._shift_btn.setProperty("active", "false")
        self._shift_btn.clicked.connect(self._toggle_shift)
        row.addWidget(self._shift_btn)

        self._yo_key = CharKey("ё", "Ё", "Ё / `")
        self._yo_key.clicked.connect(lambda: self._emit_char(self._yo_key))
        row.addWidget(self._yo_key)

        space_btn = QPushButton("Space")
        space_btn.setObjectName("wideKey")
        space_btn.clicked.connect(lambda: self._insert_char(" "))
        row.addWidget(space_btn)

        bs_btn = QPushButton("⌫")
        bs_btn.setObjectName("bsKey")
        bs_btn.clicked.connect(self._backspace)
        row.addWidget(bs_btn)

        row.addStretch()
        self._vbox.addLayout(row)

    def _build_status(self):
        self._status_lbl = QLabel(
            "Listo  •  haz clic en una tecla o escribe con tu teclado físico"
        )
        self._status_lbl.setObjectName("status")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._vbox.addWidget(self._status_lbl)

    # ── Teclado visual ────────────────────────────────────────────────────────

    def _draw_keyboard(self):
        while self._kb_layout.count():
            item = self._kb_layout.takeAt(0)
            if w := item.widget():
                w.deleteLater()
        self._char_keys.clear()

        for ri, row_data in enumerate(LAYOUTS[self._current_layout]):
            row_widget = QWidget()
            row_h = QHBoxLayout(row_widget)
            indent = ROW_INDENT[ri] if ri < len(ROW_INDENT) else 0
            row_h.setContentsMargins(indent, 0, 0, 0)
            row_h.setSpacing(4)
            for lower, upper, latin in row_data:
                key = CharKey(lower, upper, latin)
                key.clicked.connect(lambda _, k=key: self._emit_char(k))
                row_h.addWidget(key)
                self._char_keys.append(key)
            row_h.addStretch()
            self._kb_layout.addWidget(row_widget)

        self._refresh_all_keys()

    # ── Shift ─────────────────────────────────────────────────────────────────

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

    # ── Interacción con teclas ────────────────────────────────────────────────

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

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _clear(self):
        self._ta.clear()
        self._set_status("Texto limpiado")

    def _copy(self):
        text = self._ta.toPlainText().strip()
        if not text:
            self._set_status("⚠  Nada que copiar")
            return
        QApplication.clipboard().setText(text)
        self._set_status(f"✓  Copiado — {len(text)} caracteres en el portapapeles")

    def _type_app(self):
        if not HAS_PYNPUT:
            self._set_status("⚠  pynput no instalado — ejecuta: pip install pynput")
            return
        text = self._ta.toPlainText().strip()
        if not text:
            self._set_status("⚠  Nada que escribir")
            return
        self._countdown(3, text)

    def _countdown(self, n: int, text: str):
        if n > 0:
            self._set_status(f"⚠  Cambia a la ventana destino — escribiendo en {n}s…")
            QTimer.singleShot(1000, lambda: self._countdown(n - 1, text))
        else:
            self._set_status("⌨️  Escribiendo…")
            def _do():
                _kb.type(text)
                self._bridge.status_signal.emit(
                    f"✓  Escritos {len(text)} caracteres en la ventana activa"
                )
            threading.Thread(target=_do, daemon=True).start()

    def _set_status(self, msg: str):
        self._status_lbl.setText(msg)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = RussianKeyboard()
    win.show()
    sys.exit(app.exec())