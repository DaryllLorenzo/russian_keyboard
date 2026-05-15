from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

from russian_keyboard.constants import QSS
from russian_keyboard.keyboard import build_mapping
from russian_keyboard.keyboard_tab import KeyboardTab
from russian_keyboard.trainer_tab import RussianTypingTrainerWidget


class RussianKeyboard(QMainWindow):
    _INITIAL_WIDTH  = 1100
    _INITIAL_HEIGHT = 650

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Russian Keyboard")

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
        self._mapping = build_mapping(self._current_layout)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.setCentralWidget(self.tabs)

        self.keyboard_tab = KeyboardTab(mapping_provider=lambda: self._mapping)
        self.keyboard_tab.layout_changed.connect(self._on_layout_changed)
        self.tabs.addTab(self.keyboard_tab, "Keyboard")

        self.trainer_widget = RussianTypingTrainerWidget()
        self.tabs.addTab(self.trainer_widget, "Training")

        self.setStyleSheet(QSS)

    def _on_layout_changed(self, name: str):
        self._current_layout = name
        self._mapping = build_mapping(name)
