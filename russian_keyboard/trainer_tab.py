from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QProgressBar, QMessageBox, QListWidget, QListWidgetItem,
)

from russian_keyboard.constants import (
    BG, SURFACE, SURFACE2, KEY_BG, KEY_HOV, KEY_ACT,
    FG, FG_DIM, AREA_BG, GREEN, RED, ORANGE, BLUE, ERROR_BG,
    VOCABULARY,
)
from russian_keyboard.keyboard import LAYOUTS, ROW_INDENT, KEY_SPACING
from russian_keyboard.translations import tr
from russian_keyboard.widgets import CharKey, TypingLine
from russian_keyboard.trainer_session import TrainingSession


class RussianTypingTrainerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("trainerRoot")

        self.session = TrainingSession(VOCABULARY, words_per_session=10)
        self.error_timer = QTimer()
        self.error_timer.setSingleShot(True)
        self.error_timer.timeout.connect(self.clear_error_indicator)
        self._shift_active = False
        self._char_keys: list[CharKey] = []

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

        self._trainer_title = QLabel(tr("title_trainer"))
        self._trainer_title.setObjectName("title")
        left_layout.addWidget(self._trainer_title)

        self.word_display = QLabel()
        self.word_display.setObjectName("currentWord")
        self.word_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.word_display)

        self.meaning_display = QLabel()
        self.meaning_display.setObjectName("meaning")
        self.meaning_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.meaning_display)

        self.typing_area = TypingLine(self)
        self.typing_area.word_completed.connect(self.on_word_complete)
        self.typing_area.error_made.connect(self.on_error)
        left_layout.addWidget(self.typing_area)

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.error_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setMaximum(100)
        left_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel()
        self.progress_label.setObjectName("progressLabel")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.progress_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        self.new_session_btn = QPushButton(tr("trainer_new_session"))
        self.new_session_btn.setObjectName("actionGreen")
        self.new_session_btn.clicked.connect(self.start_new_session)
        btn_layout.addWidget(self.new_session_btn)

        self.reset_btn = QPushButton(tr("trainer_reset_word"))
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

        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setSpacing(4)

        self._stats_title = QLabel(tr("trainer_stats_title"))
        self._stats_title.setObjectName("statsTitle")
        stats_layout.addWidget(self._stats_title)

        self.correct_count_label = QLabel("Correct: 0")
        self.correct_count_label.setObjectName("statsText")
        stats_layout.addWidget(self.correct_count_label)

        self.total_count_label = QLabel("Total: 0")
        self.total_count_label.setObjectName("statsText")
        stats_layout.addWidget(self.total_count_label)

        self.score_label = QLabel("Score: 0%")
        self.score_label.setObjectName("statsScore")
        stats_layout.addWidget(self.score_label)

        self.error_count_label = QLabel("Mistakes: 0")
        self.error_count_label.setObjectName("statsText")
        stats_layout.addWidget(self.error_count_label)

        right_layout.addWidget(stats_frame)

        self._mistakes_title = QLabel(tr("trainer_review_title"))
        self._mistakes_title.setObjectName("mistakesTitle")
        right_layout.addWidget(self._mistakes_title)

        self.mistakes_list = QListWidget()
        self.mistakes_list.setObjectName("mistakesList")
        self.mistakes_list.setMaximumHeight(120)
        self.mistakes_list.itemDoubleClicked.connect(self.practice_mistake)
        right_layout.addWidget(self.mistakes_list)

        kb_frame = QFrame()
        kb_frame.setObjectName("kbFrame")
        kb_layout = QVBoxLayout(kb_frame)
        kb_layout.setSpacing(5)

        kb_header = QHBoxLayout()
        self._kb_title = QLabel(tr("trainer_kb_title"))
        self._kb_title.setObjectName("kbTitle")
        kb_header.addWidget(self._kb_title)
        kb_header.addStretch()

        self.vk_shift_btn = QPushButton(tr("btn_shift"))
        self.vk_shift_btn.setObjectName("shiftKey")
        self.vk_shift_btn.setFixedWidth(70)
        self.vk_shift_btn.clicked.connect(self.toggle_vk_shift)
        kb_header.addWidget(self.vk_shift_btn)

        kb_layout.addLayout(kb_header)

        self.keyboard_widget = QWidget()
        self.keyboard_layout = QVBoxLayout(self.keyboard_widget)
        self.keyboard_layout.setSpacing(KEY_SPACING)
        self.keyboard_layout.setContentsMargins(0, 0, 0, 0)

        self.build_virtual_keyboard()
        kb_layout.addWidget(self.keyboard_widget)

        bottom_row = QHBoxLayout()
        bottom_row.addStretch()

        self.space_btn = QPushButton(tr("btn_space"))
        self.space_btn.setObjectName("wideKey")
        self.space_btn.setFixedWidth(160)
        self.space_btn.clicked.connect(lambda: self.typing_area.insert_char(" "))
        bottom_row.addWidget(self.space_btn)

        self.backspace_btn = QPushButton(tr("btn_backspace"))
        self.backspace_btn.setObjectName("bsKey")
        self.backspace_btn.setFixedWidth(80)
        self.backspace_btn.clicked.connect(self.simulate_backspace)
        bottom_row.addWidget(self.backspace_btn)

        bottom_row.addStretch()
        kb_layout.addLayout(bottom_row)

        right_layout.addWidget(kb_frame)

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
                font-size: 20px;
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
                font-size: 16px;
                font-family: Consolas, "Courier New", monospace;
                padding: 4px;
            }}

            QTextEdit {{
                background: {AREA_BG};
                color: {FG};
                border: 1px solid #404040;
                border-radius: 4px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 16px;
                padding: 6px;
            }}
            QTextEdit:focus {{
                border-color: {KEY_ACT};
            }}

            QLabel#errorLabel {{
                color: {RED};
                font-size: 13px;
                font-weight: bold;
                padding: 2px;
            }}

            QProgressBar {{
                background: {SURFACE2};
                border: none;
                border-radius: 4px;
                text-align: center;
                color: {FG};
                font-size: 11px;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: {KEY_ACT};
                border-radius: 4px;
            }}

            QLabel#progressLabel {{
                color: {FG_DIM};
                font-size: 13px;
                font-family: Consolas, "Courier New", monospace;
            }}

            QPushButton#actionGreen {{
                background: {GREEN};
                color: #1e1e1e;
                border: none;
                border-radius: 4px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton#actionGreen:hover {{ background: #3dde8a; }}

            QPushButton#actionOrange {{
                background: {ORANGE};
                color: white;
                border: none;
                border-radius: 4px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton#actionOrange:hover {{ background: #e09000; }}

            QFrame#statsFrame {{
                background: {SURFACE2};
                border-radius: 6px;
                padding: 8px;
            }}

            QLabel#statsTitle {{
                color: {FG};
                font-size: 15px;
                font-weight: bold;
                font-family: Consolas, "Courier New", monospace;
                padding-bottom: 4px;
            }}

            QLabel#statsText {{
                color: {FG_DIM};
                font-size: 13px;
                font-family: Consolas, "Courier New", monospace;
                padding: 2px 0;
            }}

            QLabel#statsScore {{
                color: {KEY_ACT};
                font-size: 18px;
                font-weight: bold;
                font-family: Consolas, "Courier New", monospace;
                padding: 4px 0;
            }}

            QLabel#mistakesTitle {{
                color: {FG};
                font-size: 13px;
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
                font-size: 12px;
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
                font-size: 13px;
                font-weight: bold;
                font-family: Consolas, "Courier New", monospace;
            }}

            QPushButton#shiftKey {{
                background: {BLUE};
                color: white;
                border: none;
                border-radius: 4px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 13px;
                font-weight: bold;
                padding: 5px;
            }}
            QPushButton#shiftKey:hover {{ background: #3498db; }}

            QPushButton#wideKey {{
                background: {SURFACE2};
                color: {FG};
                border: 1px solid #484848;
                border-radius: 5px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 13px;
                font-weight: 600;
                padding: 6px;
            }}
            QPushButton#wideKey:hover {{ background: {KEY_HOV}; }}

            QPushButton#bsKey {{
                background: #4a2020;
                color: #ff8080;
                border: 1px solid #6a3030;
                border-radius: 5px;
                font-size: 17px;
                font-weight: bold;
                padding: 6px;
            }}
            QPushButton#bsKey:hover {{ background: #5c2828; }}

            QPushButton#charKey {{
                background: {KEY_BG};
                color: {FG};
                border: none;
                border-radius: 5px;
                font-family: Consolas, "Courier New", monospace;
                font-weight: bold;
            }}
            QPushButton#charKey:hover {{ background: {KEY_HOV}; }}
        """)

    def build_virtual_keyboard(self):
        for i in reversed(range(self.keyboard_layout.count())):
            widget = self.keyboard_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self._char_keys.clear()

        layout_data = LAYOUTS["ЙЦУКЕН"]
        for ri, row_data in enumerate(layout_data):
            row_widget = QWidget()
            row_h = QHBoxLayout(row_widget)
            indent = ROW_INDENT[ri] if ri < len(ROW_INDENT) else 0
            row_h.setContentsMargins(0, 0, 0, 0)
            row_h.setSpacing(KEY_SPACING)
            row_h.addSpacing(indent)
            row_h.addStretch()

            for lower, upper, latin in row_data:
                key = CharKey(lower, upper, latin)
                key.char_clicked.connect(self.on_virtual_key_press)
                key.set_shift(self._shift_active)
                row_h.addWidget(key)
                self._char_keys.append(key)

            row_h.addStretch()
            self.keyboard_layout.addWidget(row_widget)

        extra_row = QWidget()
        extra_h = QHBoxLayout(extra_row)
        extra_h.addStretch()

        yo_key = CharKey("ё", "Ё", "`")
        yo_key.char_clicked.connect(self.on_virtual_key_press)
        yo_key.set_shift(self._shift_active)
        extra_h.addWidget(yo_key)
        self._char_keys.append(yo_key)

        extra_h.addStretch()
        self.keyboard_layout.addWidget(extra_row)

    def on_virtual_key_press(self, char: str):
        self.typing_area.insert_char(char)
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

    def retranslate_ui(self):
        self._trainer_title.setText(tr("title_trainer"))
        self.new_session_btn.setText(tr("trainer_new_session"))
        self.reset_btn.setText(tr("trainer_reset_word"))
        self._stats_title.setText(tr("trainer_stats_title"))
        self._mistakes_title.setText(tr("trainer_review_title"))
        self._kb_title.setText(tr("trainer_kb_title"))
        self.vk_shift_btn.setText(tr("btn_shift"))
        self.space_btn.setText(tr("btn_space"))
        self.backspace_btn.setText(tr("btn_backspace"))
        self.typing_area.set_placeholder_text(tr("trainer_placeholder"))
        self.update_stats_display()
        self.update_progress()

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
            self.meaning_display.setText(meaning)
            self.typing_area.set_target(russian)
            self.update_progress()
        else:
            self.on_session_complete()

    def update_progress(self):
        completed, total = self.session.get_progress()
        progress_percent = (completed / total) * 100 if total > 0 else 0
        self.progress_bar.setValue(int(progress_percent))
        self.progress_label.setText(tr("trainer_progress", n=completed, total=total))

    def update_stats_display(self):
        self.correct_count_label.setText(tr("trainer_correct", n=self.session.correct_count))
        self.total_count_label.setText(tr("trainer_total", n=self.session.words_per_session))
        self.score_label.setText(tr("trainer_score", n=self.session.get_score()))
        self.error_count_label.setText(tr("trainer_mistakes", n=len(self.session.mistakes)))

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
        self.error_label.setText(tr("trainer_error_wrong"))
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
            self.error_label.setText(tr("trainer_error_reset"))
            self.error_label.setStyleSheet(f"color: {BLUE};")
            QTimer.singleShot(2000, self.clear_error_indicator)

    def practice_mistake(self, item):
        word, meaning = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            tr("trainer_dialog_practice_title"),
            tr("trainer_dialog_practice_body", word=word, meaning=meaning),
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

        message = tr("trainer_complete_body", score=score, correct=self.session.correct_count, total=self.session.words_per_session)

        if mistakes_count > 0:
            message += tr("trainer_review_count", n=mistakes_count)
            icon = QMessageBox.Icon.Warning
        else:
            message += tr("trainer_perfect")
            icon = QMessageBox.Icon.Information

        reply = QMessageBox.question(
            self,
            tr("trainer_complete_title"),
            message + tr("trainer_new_session_prompt"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            icon=icon
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.start_new_session()
