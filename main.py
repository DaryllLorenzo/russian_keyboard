#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication
from russian_keyboard.main_window import RussianKeyboard

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = RussianKeyboard()
    win.show()
    sys.exit(app.exec())
