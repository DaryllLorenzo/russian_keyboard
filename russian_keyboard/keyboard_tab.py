from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QButtonGroup, QRadioButton, QListWidget, QListWidgetItem,
    QFrame, QSlider, QSpinBox, QApplication,
)

from russian_keyboard.constants import (
    BG, SURFACE, SURFACE2, KEY_BG, KEY_HOV, KEY_ACT,
    FG, FG_DIM, BLUE_BTN, GREEN, RED_BTN, ORANGE,
    HIST_BG, HIST_SEL,
)
from russian_keyboard.keyboard import LAYOUTS
from russian_keyboard.widgets import CharKey, RussianTextEdit


class KeyboardTab(QWidget):
    layout_changed = pyqtSignal(str)

    _KEY_W          = 45
    _KEY_H          = 52
    _KEY_SPACING    = 3
    _ROW_INDENT     = [0, 15, 30]
    _HIST_PANEL_W   = 180
    _DEFAULT_FONT_SIZE = 14

    def __init__(self, mapping_provider, parent=None):
        super().__init__(parent)
        self.setObjectName("root")
        self._mapping_provider = mapping_provider
        self._shift_active   = False
        self._current_layout = "ЙЦУКЕН"
        self._char_keys: list[CharKey] = []
        self._yo_key: CharKey | None = None
        self._history: list[str] = []
        self._setup_ui()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_shift(self, active: bool):
        self._shift_active = active
        self._shift_btn.setProperty("active", "true" if active else "false")
        self._shift_btn.style().unpolish(self._shift_btn)
        self._shift_btn.style().polish(self._shift_btn)
        self._refresh_all_keys()

    def set_layout(self, name: str):
        self._current_layout = name
        self._draw_keyboard()

    def focus_text_area(self):
        self._ta.setFocus()

    # ── UI setup ──────────────────────────────────────────────────────────────

    def _setup_ui(self):
        root_h = QHBoxLayout(self)
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
                lambda checked, n=name: self._on_layout_selected(n) if checked else None
            )
            self._layout_group.addButton(rb)
            row.addWidget(rb)
            row.addSpacing(6)

        self._vbox.addLayout(row)

        kb_hint = QLabel("Escribe con teclado físico. Q W E... → cirílico. ` → ё")
        kb_hint.setObjectName("kbHint")
        self._vbox.addWidget(kb_hint)

    def _on_layout_selected(self, name: str):
        self._current_layout = name
        self._draw_keyboard()
        self.layout_changed.emit(name)

    def _build_textarea(self):
        self._ta = RussianTextEdit(self._mapping_provider)
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
        self._yo_key.char_clicked.connect(lambda c: self._insert_char(c))
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

    # ── Keyboard drawing ──────────────────────────────────────────────────────

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
                key.char_clicked.connect(self._on_key_clicked)
                row_h.addWidget(key)
                self._char_keys.append(key)
            row_h.addStretch()
            self._kb_layout.addWidget(row_widget)

        self._refresh_all_keys()
        self._update_key_sizes()

    def _on_key_clicked(self, char: str):
        self._insert_char(char)
        if self._shift_active:
            self._toggle_shift()

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

    # ── Actions ───────────────────────────────────────────────────────────────

    def _toggle_shift(self):
        self.set_shift(not self._shift_active)

    def _refresh_all_keys(self):
        for k in self._char_keys:
            k.set_shift(self._shift_active)
        if self._yo_key:
            self._yo_key.set_shift(self._shift_active)

    def _insert_char(self, char: str):
        self._ta.insertPlainText(char)
        self._ta.setFocus()

    def _backspace(self):
        self._ta.textCursor().deletePreviousChar()
        self._ta.setFocus()

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

    def _set_status(self, msg: str):
        self._status_lbl.setText(msg)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_key_sizes)
