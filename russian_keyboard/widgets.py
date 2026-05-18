from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QPainter, QFont, QColor
from PyQt6.QtWidgets import QPushButton, QTextEdit

from russian_keyboard.constants import (
    BG, SURFACE, SURFACE2, KEY_BG, KEY_HOV, KEY_ACT,
    FG, FG_DIM, AREA_BG, GREEN, RED, ERROR_BG,
    QWERTY_TO_CYRILLIC, QWERTY_TO_CYRILLIC_SHIFT,
)
from russian_keyboard.keyboard import build_mapping
from russian_keyboard.translations import tr


class CharKey(QPushButton):
    char_clicked = pyqtSignal(str)

    def __init__(self, lower: str, upper: str, latin: str, parent=None):
        super().__init__(parent)
        self.lower = lower
        self.upper = upper
        self.latin = latin
        self._pressed = False
        self._shift_state = False
        self._american_mode = False
        self.setObjectName("charKey")
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.refresh()

    def set_shift(self, active: bool):
        self._shift_state = active
        self.refresh()

    def set_american_mode(self, enabled: bool):
        self._american_mode = enabled
        self.refresh()

    def refresh(self):
        if self._american_mode:
            self.setText(self.latin.upper() if self._shift_state else self.latin.lower())
            self.setToolTip(f"{self.latin.upper() if self._shift_state else self.latin.lower()}")
        else:
            self.setText(self.upper if self._shift_state else self.lower)
            self.setToolTip(f"{self.upper if self._shift_state else self.lower}  [{self.latin}]")
        self.update()

    def mousePressEvent(self, event):
        self._pressed = True
        self.update()
        if self._american_mode:
            char = self.latin.upper() if self._shift_state else self.latin.lower()
        else:
            char = self.upper if self._shift_state else self.lower
        self.char_clicked.emit(char)
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

        if self._american_mode:
            main_text = self.latin.upper() if self._shift_state else self.latin.lower()
        else:
            main_text = self.upper if self._shift_state else self.lower
        font_main = QFont("Consolas", 0, QFont.Weight.Black)
        key_h = self.height()
        fs = max(16, min(28, key_h // 2 - 2))
        font_main.setPixelSize(fs)
        painter.setFont(font_main)
        painter.setPen(QColor(FG if not self._pressed else "#ffffff"))
        painter.drawText(event.rect(), Qt.AlignmentFlag.AlignCenter, main_text)

        font_h = QFont("Consolas", 0, QFont.Weight.Normal)
        hs = max(8, min(12, key_h // 5))
        font_h.setPixelSize(hs)
        painter.setFont(font_h)
        painter.setPen(QColor(FG_DIM))
        r = event.rect()
        hint = (self.upper if self._shift_state else self.lower) if self._american_mode else self.latin
        painter.drawText(r.adjusted(0, 0, -3, -2), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom, hint)
        painter.end()


class RussianTextEdit(QTextEdit):
    def __init__(self, mapping_provider, parent=None):
        super().__init__(parent)
        self._mapping_provider = mapping_provider
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

        mapping = self._mapping_provider()
        if key in mapping:
            shift = bool(mods & Qt.KeyboardModifier.ShiftModifier)
            lower, upper = mapping[key]
            self.insertPlainText(upper if shift else lower)
        else:
            super().keyPressEvent(event)


class TypingLine(QTextEdit):
    word_completed = pyqtSignal(bool)
    error_made = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_text = ""
        self.current_pos = 0
        self.setPlaceholderText(tr("trainer_placeholder"))
        self.setMaximumHeight(70)
        self._shift_pressed = False
        self._mapping: dict | None = None

    def set_mapping(self, mapping: dict):
        self._mapping = mapping

    def set_placeholder_text(self, text: str):
        self.setPlaceholderText(text)

    def set_target(self, text: str):
        self.target_text = text
        self.current_pos = 0
        self.clear()
        self.setPlainText("")
        self.update_highlighting()

    def insert_char(self, char: str):
        if self.current_pos < len(self.target_text):
            expected = self.target_text[self.current_pos]
            if char == expected:
                cursor = self.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                self.setTextCursor(cursor)
                self.insertPlainText(char)
                self.current_pos += 1
                self.update_highlighting()
                if self.current_pos == len(self.target_text):
                    self.word_completed.emit(True)
            else:
                self.error_made.emit()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key.Key_Backspace:
            if self.current_pos > 0:
                self.current_pos -= 1
                cursor = self.textCursor()
                cursor.movePosition(cursor.MoveOperation.Left)
                cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
                self.update_highlighting()
            event.accept()
            return

        if key == Qt.Key.Key_Shift:
            self._shift_pressed = True
            event.accept()
            return

        cyrillic_char = None
        shift = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)

        mapping = self._mapping if self._mapping is not None else QWERTY_TO_CYRILLIC
        mapping_shift = self._mapping if self._mapping is not None else QWERTY_TO_CYRILLIC_SHIFT

        if key in mapping:
            if self._mapping is not None:
                _, upper = mapping[key]
                cyrillic_char = upper if shift else mapping[key][0]
            else:
                cyrillic_char = mapping_shift[key] if shift else mapping[key]

        if cyrillic_char and self.current_pos < len(self.target_text):
            expected = self.target_text[self.current_pos]
            if cyrillic_char == expected:
                cursor = self.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                self.setTextCursor(cursor)
                self.insertPlainText(cyrillic_char)
                self.current_pos += 1
                self.update_highlighting()
                if self.current_pos == len(self.target_text):
                    self.word_completed.emit(True)
            else:
                self.error_made.emit()
                event.accept()
                return
        elif cyrillic_char and self.current_pos >= len(self.target_text):
            event.accept()
            return
        else:
            if key == Qt.Key.Key_Space:
                event.accept()
                return
            super().keyPressEvent(event)

        event.accept()

    def keyReleaseEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_Shift:
            self._shift_pressed = False
            event.accept()
        else:
            super().keyReleaseEvent(event)

    def update_highlighting(self):
        text = self.toPlainText()
        if not text:
            self.setTextColor(QColor(FG))
            return

        html = '<html><body>'
        correct_part = text[:self.current_pos]
        if correct_part:
            html += f'<span style="color: {GREEN};">{correct_part}</span>'
        remaining = self.target_text[self.current_pos:]
        if remaining:
            html += f'<span style="color: {FG_DIM};">{remaining}</span>'
        html += '</body></html>'
        self.setHtml(html)
