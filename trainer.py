#!/usr/bin/env python3
"""
Russian Typing Trainer — PyQt6

A typing practice module for the Russian Keyboard application.
Tracks progress, highlights errors, and provides English meanings.
Includes virtual keyboard for typing.
"""

import sys
import random
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QKeyEvent, QPainter
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QFrame, QProgressBar,
    QMessageBox, QListWidget, QListWidgetItem, QSplitter
)

# Color palette matching main app
BG = "#1e1e1e"
SURFACE = "#2a2a2a"
SURFACE2 = "#333333"
KEY_BG = "#3c3c3c"
KEY_HOV = "#4a4a4a"
KEY_ACT = "#e94560"
FG = "#e8e8e8"
FG_DIM = "#909090"
GREEN = "#2ecc71"
RED = "#e74c3c"
ORANGE = "#c67c00"
BLUE = "#2980b9"
ERROR_BG = "#4a2020"
AREA_BG = "#141414"

# Training vocabulary
VOCABULARY = [
    ("привет", "hello"),
    ("спасибо", "thank you"),
    ("пожалуйста", "please / you're welcome"),
    ("да", "yes"),
    ("нет", "no"),
    ("хорошо", "good / fine"),
    ("плохо", "bad"),
    ("большой", "big"),
    ("маленький", "small"),
    ("красивый", "beautiful"),
    ("умный", "smart"),
    ("вкусный", "delicious"),
    ("вода", "water"),
    ("еда", "food"),
    ("дом", "house"),
    ("машина", "car"),
    ("работа", "work"),
    ("друг", "friend"),
    ("семья", "family"),
    ("любовь", "love"),
    ("утро", "morning"),
    ("день", "day"),
    ("ночь", "night"),
    ("книга", "book"),
]

# Keyboard layout with Latin mappings (same as main.py)
TRAINER_KEYBOARD_LAYOUT = [
    [("й","Й","Q"), ("ц","Ц","W"), ("у","У","E"), ("к","К","R"), ("е","Е","T"),
     ("н","Н","Y"), ("г","Г","U"), ("ш","Ш","I"), ("щ","Щ","O"), ("з","З","P"),
     ("х","Х","["), ("ъ","Ъ","]")],
    [("ф","Ф","A"), ("ы","Ы","S"), ("в","В","D"), ("а","А","F"), ("п","П","G"),
     ("р","Р","H"), ("о","О","J"), ("л","Л","K"), ("д","Д","L"), ("ж","Ж",";"),
     ("э","Э","'")],
    [("я","Я","Z"), ("ч","Ч","X"), ("с","С","C"), ("м","М","V"), ("и","И","B"),
     ("т","Т","N"), ("ь","Ь","M"), ("б","Б",","), ("ю","Ю",".")],
]

# QWERTY to Cyrillic mapping for physical keyboard
QWERTY_TO_CYRILLIC = {
    Qt.Key.Key_Q: "й", Qt.Key.Key_W: "ц", Qt.Key.Key_E: "у", Qt.Key.Key_R: "к",
    Qt.Key.Key_T: "е", Qt.Key.Key_Y: "н", Qt.Key.Key_U: "г", Qt.Key.Key_I: "ш",
    Qt.Key.Key_O: "щ", Qt.Key.Key_P: "з", Qt.Key.Key_BracketLeft: "х", Qt.Key.Key_BracketRight: "ъ",
    Qt.Key.Key_A: "ф", Qt.Key.Key_S: "ы", Qt.Key.Key_D: "в", Qt.Key.Key_F: "а",
    Qt.Key.Key_G: "п", Qt.Key.Key_H: "р", Qt.Key.Key_J: "о", Qt.Key.Key_K: "л",
    Qt.Key.Key_L: "д", Qt.Key.Key_Semicolon: "ж", Qt.Key.Key_Apostrophe: "э",
    Qt.Key.Key_Z: "я", Qt.Key.Key_X: "ч", Qt.Key.Key_C: "с", Qt.Key.Key_V: "м",
    Qt.Key.Key_B: "и", Qt.Key.Key_N: "т", Qt.Key.Key_M: "ь", Qt.Key.Key_Comma: "б",
    Qt.Key.Key_Period: "ю", Qt.Key.Key_QuoteLeft: "ё"
}

QWERTY_TO_CYRILLIC_SHIFT = {
    Qt.Key.Key_Q: "Й", Qt.Key.Key_W: "Ц", Qt.Key.Key_E: "У", Qt.Key.Key_R: "К",
    Qt.Key.Key_T: "Е", Qt.Key.Key_Y: "Н", Qt.Key.Key_U: "Г", Qt.Key.Key_I: "Ш",
    Qt.Key.Key_O: "Щ", Qt.Key.Key_P: "З", Qt.Key.Key_BracketLeft: "Х", Qt.Key.Key_BracketRight: "Ъ",
    Qt.Key.Key_A: "Ф", Qt.Key.Key_S: "Ы", Qt.Key.Key_D: "В", Qt.Key.Key_F: "А",
    Qt.Key.Key_G: "П", Qt.Key.Key_H: "Р", Qt.Key.Key_J: "О", Qt.Key.Key_K: "Л",
    Qt.Key.Key_L: "Д", Qt.Key.Key_Semicolon: "Ж", Qt.Key.Key_Apostrophe: "Э",
    Qt.Key.Key_Z: "Я", Qt.Key.Key_X: "Ч", Qt.Key.Key_C: "С", Qt.Key.Key_V: "М",
    Qt.Key.Key_B: "И", Qt.Key.Key_N: "Т", Qt.Key.Key_M: "Ь", Qt.Key.Key_Comma: "Б",
    Qt.Key.Key_Period: "Ю", Qt.Key.Key_QuoteLeft: "Ё"
}

ROW_INDENT = [0, 18, 36]
KEY_SPACING = 3


class TrainerCharKey(QPushButton):
    """Character key for the trainer keyboard - same as main.py CharKey"""
    
    char_clicked = pyqtSignal(str)
    
    def __init__(self, lower: str, upper: str, latin: str, parent=None):
        super().__init__(parent)
        self.lower = lower
        self.upper = upper
        self.latin = latin
        self._pressed = False
        self._shift_active = False
        self.setObjectName("trainerCharKey")
        self.setMinimumSize(45, 52)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.refresh()
        
    def set_shift(self, active: bool):
        self._shift_active = active
        self.refresh()
        
    def refresh(self):
        self.setText(self.upper if self._shift_active else self.lower)
        self.setToolTip(f"{self.upper if self._shift_active else self.lower}  [{self.latin}]")
        self.update()
        
    def mousePressEvent(self, event):
        self._pressed = True
        self.update()
        # Emit the character on press
        char = self.upper if self._shift_active else self.lower
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
        
        # Main Cyrillic text
        main_text = self.upper if self._shift_active else self.lower
        font_main = QFont("Consolas", 0, QFont.Weight.Black)
        key_h = self.height()
        fs = max(14, min(22, key_h // 2 - 4))
        font_main.setPixelSize(fs)
        painter.setFont(font_main)
        painter.setPen(QColor(FG if not self._pressed else "#ffffff"))
        painter.drawText(event.rect(), Qt.AlignmentFlag.AlignCenter, main_text)
        
        # Latin hint text
        font_h = QFont("Consolas", 0, QFont.Weight.Normal)
        hs = max(7, min(10, key_h // 6))
        font_h.setPixelSize(hs)
        painter.setFont(font_h)
        painter.setPen(QColor(FG_DIM))
        r = event.rect()
        painter.drawText(r.adjusted(0, 0, -3, -2), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom, self.latin)
        painter.end()


class TypingLine(QTextEdit):
    """Custom text edit that highlights characters incrementally"""
    
    word_completed = pyqtSignal(bool)
    error_made = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_text = ""
        self.current_pos = 0
        self.setPlaceholderText("Type the word here...")
        self.setMaximumHeight(70)
        self._shift_pressed = False
        
    def set_target(self, text: str):
        self.target_text = text
        self.current_pos = 0
        self.clear()
        self.setPlainText("")
        self.update_highlighting()
        
    def insert_char(self, char: str):
        """Insert a character (called from virtual keyboard or physical keyboard mapping)"""
        if self.current_pos < len(self.target_text):
            expected = self.target_text[self.current_pos]
            
            if char == expected:
                # Correct character
                # Mover cursor al final antes de insertar
                cursor = self.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                self.setTextCursor(cursor)
                self.insertPlainText(char)
                self.current_pos += 1
                self.update_highlighting()
                
                # Check if word is complete
                if self.current_pos == len(self.target_text):
                    self.word_completed.emit(True)
            else:
                self.error_made.emit()
                
    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()
        
        # Handle backspace
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
        
        # Handle shift key state
        if key == Qt.Key.Key_Shift:
            self._shift_pressed = True
            event.accept()
            return
            
        # Map QWERTY to Cyrillic
        cyrillic_char = None
        shift = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
        
        if key in QWERTY_TO_CYRILLIC:
            cyrillic_char = QWERTY_TO_CYRILLIC_SHIFT[key] if shift else QWERTY_TO_CYRILLIC[key]
        
        if cyrillic_char and self.current_pos < len(self.target_text):
            expected = self.target_text[self.current_pos]
            
            if cyrillic_char == expected:
                # Correct character
                # Mover cursor al final antes de insertar
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
            # For other keys (Space, etc.), let the default handler work
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


class TrainingSession:
    def __init__(self, vocabulary, words_per_session=10):
        self.vocabulary = vocabulary[:]
        self.words_per_session = min(words_per_session, len(vocabulary))
        self.words_to_practice = []
        self.current_index = 0
        self.correct_count = 0
        self.mistakes = []
        
    def generate_session(self):
        self.words_to_practice = random.sample(self.vocabulary, self.words_per_session)
        self.current_index = 0
        self.correct_count = 0
        self.mistakes = []
        
    def current_word(self):
        if self.current_index < len(self.words_to_practice):
            return self.words_to_practice[self.current_index]
        return None
        
    def advance(self, was_correct):
        if was_correct:
            self.correct_count += 1
        else:
            current = self.current_word()
            if current:
                self.mistakes.append(current)
        self.current_index += 1
        return self.current_index >= len(self.words_to_practice)
        
    def get_progress(self):
        return (self.current_index, len(self.words_to_practice))
        
    def get_score(self):
        if self.words_per_session == 0:
            return 0
        return (self.correct_count / self.words_per_session) * 100


class RussianTypingTrainerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("trainerRoot")
        
        self.session = TrainingSession(VOCABULARY, words_per_session=10)
        self.error_timer = QTimer()
        self.error_timer.setSingleShot(True)
        self.error_timer.timeout.connect(self.clear_error_indicator)
        self._shift_active = False
        self._char_keys = []
        
        self.setup_ui()
        self.start_new_session()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(10)
        
        # LEFT PANEL - Training Area
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # Title
        title = QLabel("🎯 Russian Typing Trainer")
        title.setObjectName("title")
        left_layout.addWidget(title)
        
        # Current word display
        self.word_display = QLabel()
        self.word_display.setObjectName("currentWord")
        self.word_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.word_display)
        
        # Meaning display
        self.meaning_display = QLabel()
        self.meaning_display.setObjectName("meaning")
        self.meaning_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.meaning_display)
        
        # Typing area
        self.typing_area = TypingLine(self)
        self.typing_area.word_completed.connect(self.on_word_complete)
        self.typing_area.error_made.connect(self.on_error)
        left_layout.addWidget(self.typing_area)
        
        # Error indicator
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.error_label)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setMaximum(100)
        left_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel()
        self.progress_label.setObjectName("progressLabel")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.progress_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)
        
        self.new_session_btn = QPushButton("New Session")
        self.new_session_btn.setObjectName("actionGreen")
        self.new_session_btn.clicked.connect(self.start_new_session)
        btn_layout.addWidget(self.new_session_btn)
        
        self.reset_btn = QPushButton("Reset Word")
        self.reset_btn.setObjectName("actionOrange")
        self.reset_btn.clicked.connect(self.reset_current_word)
        btn_layout.addWidget(self.reset_btn)
        
        left_layout.addLayout(btn_layout)
        
        # RIGHT PANEL - Keyboard and Stats
        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # Stats panel
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setSpacing(4)
        
        stats_title = QLabel("Statistics")
        stats_title.setObjectName("statsTitle")
        stats_layout.addWidget(stats_title)
        
        self.correct_count_label = QLabel("✅ Correct: 0")
        self.correct_count_label.setObjectName("statsText")
        stats_layout.addWidget(self.correct_count_label)
        
        self.total_count_label = QLabel("📝 Total: 0")
        self.total_count_label.setObjectName("statsText")
        stats_layout.addWidget(self.total_count_label)
        
        self.score_label = QLabel("📈 Score: 0%")
        self.score_label.setObjectName("statsScore")
        stats_layout.addWidget(self.score_label)
        
        self.error_count_label = QLabel("❌ Mistakes: 0")
        self.error_count_label.setObjectName("statsText")
        stats_layout.addWidget(self.error_count_label)
        
        right_layout.addWidget(stats_frame)
        
        # Mistakes list
        mistakes_title = QLabel("Words to Review")
        mistakes_title.setObjectName("mistakesTitle")
        right_layout.addWidget(mistakes_title)
        
        self.mistakes_list = QListWidget()
        self.mistakes_list.setObjectName("mistakesList")
        self.mistakes_list.setMaximumHeight(120)
        self.mistakes_list.itemDoubleClicked.connect(self.practice_mistake)
        right_layout.addWidget(self.mistakes_list)
        
        # Virtual keyboard section
        kb_frame = QFrame()
        kb_frame.setObjectName("kbFrame")
        kb_layout = QVBoxLayout(kb_frame)
        kb_layout.setSpacing(5)
        
        kb_header = QHBoxLayout()
        kb_title = QLabel("Virtual Keyboard")
        kb_title.setObjectName("kbTitle")
        kb_header.addWidget(kb_title)
        kb_header.addStretch()
        
        self.vk_shift_btn = QPushButton("⇧ Shift")
        self.vk_shift_btn.setObjectName("shiftKey")
        self.vk_shift_btn.setFixedWidth(70)
        self.vk_shift_btn.clicked.connect(self.toggle_vk_shift)
        kb_header.addWidget(self.vk_shift_btn)
        
        kb_layout.addLayout(kb_header)
        
        # Keyboard rows
        self.keyboard_widget = QWidget()
        self.keyboard_layout = QVBoxLayout(self.keyboard_widget)
        self.keyboard_layout.setSpacing(KEY_SPACING)
        self.keyboard_layout.setContentsMargins(0, 0, 0, 0)
        
        self.build_virtual_keyboard()
        kb_layout.addWidget(self.keyboard_widget)
        
        # Bottom row
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()
        
        self.space_btn = QPushButton("⎵ Space")
        self.space_btn.setObjectName("wideKey")
        self.space_btn.setFixedWidth(160)
        self.space_btn.clicked.connect(lambda: self.typing_area.insert_char(" "))
        bottom_row.addWidget(self.space_btn)
        
        self.backspace_btn = QPushButton("⌫")
        self.backspace_btn.setObjectName("bsKey")
        self.backspace_btn.setFixedWidth(80)
        self.backspace_btn.clicked.connect(self.simulate_backspace)
        bottom_row.addWidget(self.backspace_btn)
        
        bottom_row.addStretch()
        kb_layout.addLayout(bottom_row)
        
        right_layout.addWidget(kb_frame)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        
        self.setup_stylesheet()
        
    def setup_stylesheet(self):
        self.setStyleSheet(f"""
            QWidget#trainerRoot {{
                background: {BG};
            }}
            
            QWidget#leftPanel, QWidget#rightPanel {{
                background: transparent;
            }}
            
            QLabel#title {{
                color: {FG};
                font-size: 18px;
                font-weight: 800;
                font-family: Consolas, "Courier New", monospace;
                padding: 3px 0;
            }}
            
            QLabel#currentWord {{
                color: {KEY_ACT};
                font-size: 42px;
                font-weight: 700;
                font-family: Consolas, "Courier New", monospace;
                background: {SURFACE2};
                padding: 20px;
                border-radius: 8px;
            }}
            
            QLabel#meaning {{
                color: {GREEN};
                font-size: 14px;
                font-family: Consolas, "Courier New", monospace;
                padding: 4px;
            }}
            
            QTextEdit {{
                background: {AREA_BG};
                color: {FG};
                border: 1px solid #404040;
                border-radius: 4px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 14px;
                padding: 6px;
            }}
            QTextEdit:focus {{
                border-color: {KEY_ACT};
            }}
            
            QLabel#errorLabel {{
                color: {RED};
                font-size: 10px;
                font-weight: bold;
                padding: 2px;
            }}
            
            QProgressBar {{
                background: {SURFACE2};
                border: none;
                border-radius: 4px;
                text-align: center;
                color: {FG};
                font-size: 10px;
                height: 18px;
            }}
            QProgressBar::chunk {{
                background: {KEY_ACT};
                border-radius: 4px;
            }}
            
            QLabel#progressLabel {{
                color: {FG_DIM};
                font-size: 10px;
                font-family: Consolas, "Courier New", monospace;
            }}
            
            QPushButton#actionGreen {{
                background: {GREEN};
                color: #1e1e1e;
                border: none;
                border-radius: 4px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 10px;
                font-weight: bold;
                padding: 6px 12px;
            }}
            QPushButton#actionGreen:hover {{ background: #3dde8a; }}
            
            QPushButton#actionOrange {{
                background: {ORANGE};
                color: white;
                border: none;
                border-radius: 4px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 10px;
                font-weight: bold;
                padding: 6px 12px;
            }}
            QPushButton#actionOrange:hover {{ background: #e09000; }}
            
            QFrame#statsFrame {{
                background: {SURFACE2};
                border-radius: 6px;
                padding: 8px;
            }}
            
            QLabel#statsTitle {{
                color: {FG};
                font-size: 13px;
                font-weight: bold;
                font-family: Consolas, "Courier New", monospace;
                padding-bottom: 4px;
            }}
            
            QLabel#statsText {{
                color: {FG_DIM};
                font-size: 11px;
                font-family: Consolas, "Courier New", monospace;
                padding: 2px 0;
            }}
            
            QLabel#statsScore {{
                color: {KEY_ACT};
                font-size: 14px;
                font-weight: bold;
                font-family: Consolas, "Courier New", monospace;
                padding: 4px 0;
            }}
            
            QLabel#mistakesTitle {{
                color: {FG};
                font-size: 11px;
                font-weight: bold;
                font-family: Consolas, "Courier New", monospace;
                padding: 4px 0 2px 0;
            }}
            
            QListWidget#mistakesList {{
                background: {SURFACE};
                color: {FG};
                border: 1px solid {SURFACE2};
                border-radius: 4px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 10px;
            }}
            QListWidget#mistakesList::item {{
                padding: 4px;
                border-bottom: 1px solid {SURFACE2};
            }}
            QListWidget#mistakesList::item:hover {{
                background: {KEY_HOV};
            }}
            QListWidget#mistakesList::item:selected {{
                background: {KEY_ACT};
            }}
            
            QFrame#kbFrame {{
                background: {SURFACE};
                border-radius: 6px;
                padding: 8px;
            }}
            
            QLabel#kbTitle {{
                color: {FG};
                font-size: 11px;
                font-weight: bold;
                font-family: Consolas, "Courier New", monospace;
            }}
            
            QPushButton#shiftKey {{
                background: {BLUE};
                color: white;
                border: none;
                border-radius: 4px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 10px;
                font-weight: bold;
                padding: 4px;
            }}
            QPushButton#shiftKey:hover {{ background: #3498db; }}
            
            QPushButton#wideKey {{
                background: {SURFACE2};
                color: {FG};
                border: 1px solid #484848;
                border-radius: 5px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 11px;
                font-weight: 600;
                padding: 6px;
            }}
            QPushButton#wideKey:hover {{ background: {KEY_HOV}; }}
            
            QPushButton#bsKey {{
                background: #4a2020;
                color: #ff8080;
                border: 1px solid #6a3030;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 6px;
            }}
            QPushButton#bsKey:hover {{ background: #5c2828; }}
            
            QPushButton#trainerCharKey {{
                background: {KEY_BG};
                color: {FG};
                border: none;
                border-radius: 5px;
                font-family: Consolas, "Courier New", monospace;
                font-weight: bold;
            }}
            QPushButton#trainerCharKey:hover {{ background: {KEY_HOV}; }}
        """)
        
    def build_virtual_keyboard(self):
        # Clear existing keys
        for i in reversed(range(self.keyboard_layout.count())):
            widget = self.keyboard_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self._char_keys.clear()
        
        # Add keyboard rows
        for ri, row_data in enumerate(TRAINER_KEYBOARD_LAYOUT):
            row_widget = QWidget()
            row_h = QHBoxLayout(row_widget)
            indent = ROW_INDENT[ri] if ri < len(ROW_INDENT) else 0
            row_h.setContentsMargins(0, 0, 0, 0)
            row_h.setSpacing(KEY_SPACING)
            row_h.addSpacing(indent)
            row_h.addStretch()
            
            for lower, upper, latin in row_data:
                key = TrainerCharKey(lower, upper, latin)
                key.char_clicked.connect(self.on_virtual_key_press)
                key.set_shift(self._shift_active)
                row_h.addWidget(key)
                self._char_keys.append(key)
                
            row_h.addStretch()
            self.keyboard_layout.addWidget(row_widget)
        
        # Add Ë key row (like main.py)
        extra_row = QWidget()
        extra_h = QHBoxLayout(extra_row)
        extra_h.addStretch()
        
        yo_key = TrainerCharKey("ё", "Ё", "`")
        yo_key.char_clicked.connect(self.on_virtual_key_press)
        yo_key.set_shift(self._shift_active)
        extra_h.addWidget(yo_key)
        self._char_keys.append(yo_key)
        
        extra_h.addStretch()
        self.keyboard_layout.addWidget(extra_row)
        
    def on_virtual_key_press(self, char: str):
        """Handle virtual key press"""
        self.typing_area.insert_char(char)
        # Auto-release shift after key press
        if self._shift_active:
            self.toggle_vk_shift()
            
    def toggle_vk_shift(self):
        self._shift_active = not self._shift_active
        self.vk_shift_btn.setStyleSheet(f"background: {KEY_ACT if self._shift_active else BLUE};")
        for key in self._char_keys:
            key.set_shift(self._shift_active)
            
    def simulate_backspace(self):
        cursor = self.typing_area.textCursor()
        if not cursor.atStart():
            cursor.deletePreviousChar()
            if self.typing_area.current_pos > 0:
                self.typing_area.current_pos -= 1
                self.typing_area.update_highlighting()
        
    def start_new_session(self):
        self.session.generate_session()
        self.update_stats_display()
        self.load_current_word()
        self.typing_area.setFocus()
        self.error_label.setText("")
        self.mistakes_list.clear()
        
    def load_current_word(self):
        current = self.session.current_word()
        if current:
            russian, meaning = current
            self.word_display.setText(russian)
            self.meaning_display.setText(f"📖 {meaning}")
            self.typing_area.set_target(russian)
            self.update_progress()
        else:
            self.on_session_complete()
            
    def update_progress(self):
        completed, total = self.session.get_progress()
        progress_percent = (completed / total) * 100 if total > 0 else 0
        self.progress_bar.setValue(int(progress_percent))
        self.progress_label.setText(f"{completed}/{total} words")
        
    def update_stats_display(self):
        self.correct_count_label.setText(f"✅ Correct: {self.session.correct_count}")
        self.total_count_label.setText(f"📝 Total: {self.session.words_per_session}")
        self.score_label.setText(f"📈 Score: {self.session.get_score():.0f}%")
        self.error_count_label.setText(f"❌ Mistakes: {len(self.session.mistakes)}")
        
        self.mistakes_list.clear()
        for word, meaning in self.session.mistakes:
            item = QListWidgetItem(f"{word} - {meaning}")
            item.setData(Qt.ItemDataRole.UserRole, (word, meaning))
            self.mistakes_list.addItem(item)
            
    def on_word_complete(self, was_correct):
        is_done = self.session.advance(True)
        self.update_stats_display()
        
        if is_done:
            self.on_session_complete()
        else:
            self.load_current_word()
            
    def on_error(self):
        self.error_label.setText("❌ Wrong character! Delete and try again.")
        self.error_timer.start(2000)
        
        original_style = self.typing_area.styleSheet()
        self.typing_area.setStyleSheet(f"background: {ERROR_BG}; border: 2px solid {RED};")
        QTimer.singleShot(500, lambda: self.typing_area.setStyleSheet(original_style))
        
    def clear_error_indicator(self):
        self.error_label.setText("")
        
    def reset_current_word(self):
        current = self.session.current_word()
        if current:
            self.typing_area.set_target(current[0])
            self.typing_area.setFocus()
            self.error_label.setText("Word reset - try again!")
            self.error_label.setStyleSheet(f"color: {BLUE};")
            QTimer.singleShot(2000, self.clear_error_indicator)
            
    def practice_mistake(self, item):
        word, meaning = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "Practice Word",
            f"Practice: {word} - {meaning}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            temp_session = TrainingSession([(word, meaning)], words_per_session=1)
            self.session = temp_session
            self.update_stats_display()
            self.load_current_word()
            self.typing_area.setFocus()
            
    def on_session_complete(self):
        score = self.session.get_score()
        mistakes_count = len(self.session.mistakes)
        
        message = f"Session Complete!\n\nScore: {score:.0f}%\nCorrect: {self.session.correct_count}/{self.session.words_per_session}"
        
        if mistakes_count > 0:
            message += f"\n\nWords to review: {mistakes_count}"
            icon = QMessageBox.Icon.Warning
        else:
            message += "\n\nPerfect! No mistakes! 🌟"
            icon = QMessageBox.Icon.Information
            
        reply = QMessageBox.question(
            self,
            "Training Complete",
            message + "\n\nStart a new session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            icon=icon
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.start_new_session()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    widget = RussianTypingTrainerWidget()
    widget.setWindowTitle("Russian Typing Trainer")
    widget.resize(1050, 650)
    widget.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()