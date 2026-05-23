from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QPushButton

from russian_keyboard import constants
from russian_keyboard.keyboard import build_mapping, build_american_mapping
from russian_keyboard.keyboard_tab import KeyboardTab
from russian_keyboard.trainer_tab import RussianTypingTrainerWidget
from russian_keyboard.translations import tr, set_language


class RussianKeyboard(QMainWindow):
    _INITIAL_WIDTH  = 1100
    _INITIAL_HEIGHT = 650

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("app_title"))

        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        win_width = min(self._INITIAL_WIDTH, screen_geometry.width() - 100)
        win_height = min(self._INITIAL_HEIGHT, screen_geometry.height() - 100)
        self.resize(win_width, win_height)
        self.setGeometry(
            (screen_geometry.width() - win_width) // 2,
            (screen_geometry.height() - win_height) // 2,
            win_width,
            win_height,
        )

        self._current_layout = "ЙЦУКЕН"
        self._american_mode = False
        self._rebuild_mapping()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("root")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(4, 4, 4, 0)

        self._theme_btn = QPushButton()
        self._theme_btn.setObjectName("themeBtn")
        self._theme_btn.setFixedWidth(36)
        self._theme_btn.clicked.connect(self._toggle_theme)
        header_layout.addWidget(self._theme_btn)

        es_btn = QPushButton("ES")
        es_btn.setObjectName("langBtn")
        es_btn.setFixedWidth(36)
        es_btn.setCheckable(True)
        es_btn.setChecked(True)
        es_btn.clicked.connect(lambda: self._switch_language("es", es_btn, en_btn))

        en_btn = QPushButton("EN")
        en_btn.setObjectName("langBtn")
        en_btn.setFixedWidth(36)
        en_btn.setCheckable(True)
        en_btn.clicked.connect(lambda: self._switch_language("en", en_btn, es_btn))

        header_layout.addStretch()
        header_layout.addWidget(es_btn)
        header_layout.addWidget(en_btn)
        main_layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        main_layout.addWidget(self.tabs)

        self.keyboard_tab = KeyboardTab(mapping_provider=lambda: self._mapping)
        self.keyboard_tab.layout_changed.connect(self._on_layout_changed)
        self.keyboard_tab.american_mode_changed.connect(self._on_american_mode_changed)
        self.tabs.addTab(self.keyboard_tab, tr("tab_keyboard"))

        self.trainer_widget = RussianTypingTrainerWidget()
        self.trainer_widget.set_layout(self._current_layout)
        self.keyboard_tab.layout_changed.connect(self.trainer_widget.set_layout)
        self.tabs.addTab(self.trainer_widget, tr("tab_training"))

        self._apply_theme()

    def _toggle_theme(self):
        new = "light" if constants.current_theme() == "dark" else "dark"
        constants.set_theme(new)
        self._apply_theme()

    def _apply_theme(self):
        is_dark = constants.current_theme() == "dark"
        self._theme_btn.setText("\u2601" if is_dark else "\u2600")

        self.setStyleSheet(constants.QSS + f"""
            QPushButton#langBtn {{
                background: {constants.KEY_BG}; color: {constants.FG_DIM}; border: 1px solid {constants.BORDER};
                border-radius: 4px; font-size: 12px; font-weight: bold; padding: 4px;
            }}
            QPushButton#langBtn:checked {{
                background: {constants.KEY_ACT}; color: white; border-color: {constants.KEY_ACT};
            }}
            QPushButton#langBtn:hover:!checked {{
                background: {constants.KEY_HOV}; color: {constants.FG};
            }}
            QPushButton#themeBtn {{
                background: {constants.SURFACE2}; color: {constants.FG}; border: 1px solid {constants.BORDER};
                border-radius: 4px; font-size: 14px; padding: 4px;
            }}
            QPushButton#themeBtn:hover {{
                background: {constants.KEY_HOV};
            }}
        """)

        self.keyboard_tab.apply_theme()
        self.trainer_widget.apply_theme()

    def _switch_language(self, lang: str, active_btn, other_btn):
        set_language(lang)
        active_btn.setChecked(True)
        other_btn.setChecked(False)
        self.setWindowTitle(tr("app_title"))
        self.tabs.setTabText(0, tr("tab_keyboard"))
        self.tabs.setTabText(1, tr("tab_training"))
        self.keyboard_tab.retranslate_ui()
        self.trainer_widget.retranslate_ui()

    def _rebuild_mapping(self):
        if self._american_mode:
            self._mapping = build_american_mapping(self._current_layout)
        else:
            self._mapping = build_mapping(self._current_layout)

    def _on_layout_changed(self, name: str):
        self._current_layout = name
        self._rebuild_mapping()

    def _on_american_mode_changed(self, enabled: bool):
        self._american_mode = enabled
        self._rebuild_mapping()
