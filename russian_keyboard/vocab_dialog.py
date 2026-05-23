import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QLineEdit, QFormLayout,
    QDialogButtonBox, QMessageBox, QFileDialog,
)

from russian_keyboard import constants
from russian_keyboard.translations import tr


class VocabularyDialog(QDialog):
    def __init__(self, vocabulary: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("vocab_dialog_title"))
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)

        self._vocab = vocabulary[:]

        self._setup_ui()
        self._populate_list()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self._list_widget = QListWidget()
        layout.addWidget(self._list_widget, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self._add_btn = QPushButton(tr("vocab_add"))
        self._add_btn.clicked.connect(self._add_word)
        btn_row.addWidget(self._add_btn)

        self._remove_btn = QPushButton(tr("vocab_remove"))
        self._remove_btn.clicked.connect(self._remove_word)
        btn_row.addWidget(self._remove_btn)

        btn_row.addStretch()

        self._import_btn = QPushButton(tr("vocab_import"))
        self._import_btn.clicked.connect(self._import_vocab)
        btn_row.addWidget(self._import_btn)

        self._export_btn = QPushButton(tr("vocab_export"))
        self._export_btn.clicked.connect(self._export_vocab)
        btn_row.addWidget(self._export_btn)

        layout.addLayout(btn_row)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(f"""
            QDialog {{
                background: {constants.BG};
            }}
            QLabel {{
                color: {constants.FG};
                font-family: Consolas, "Courier New", monospace;
            }}
            QListWidget {{
                background: {constants.SURFACE};
                color: {constants.FG};
                border: 1px solid {constants.BORDER};
                border-radius: 4px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 4px 6px;
                border-bottom: 1px solid {constants.SURFACE2};
            }}
            QListWidget::item:hover {{
                background: {constants.KEY_HOV};
            }}
            QListWidget::item:selected {{
                background: {constants.KEY_ACT};
                color: white;
            }}
            QPushButton {{
                background: {constants.SURFACE2};
                color: {constants.FG};
                border: 1px solid {constants.BORDER};
                border-radius: 4px;
                padding: 6px 12px;
                font-family: Consolas, "Courier New", monospace;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {constants.KEY_HOV};
            }}
            QLineEdit {{
                background: {constants.AREA_BG};
                color: {constants.FG};
                border: 1px solid {constants.BORDER};
                border-radius: 4px;
                padding: 4px;
                font-family: Consolas, "Courier New", monospace;
            }}
        """)

    def _populate_list(self):
        self._list_widget.clear()
        for russian, meaning in self._vocab:
            item = QListWidgetItem(f"{russian} — {meaning}")
            item.setData(Qt.ItemDataRole.UserRole, (russian, meaning))
            self._list_widget.addItem(item)

    def _add_word(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("vocab_add"))
        dialog.setMinimumWidth(300)
        dialog.setStyleSheet(self.styleSheet())

        form = QFormLayout(dialog)
        russian_input = QLineEdit()
        meaning_input = QLineEdit()
        form.addRow(tr("vocab_russian"), russian_input)
        form.addRow(tr("vocab_meaning"), meaning_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            russian = russian_input.text().strip()
            meaning = meaning_input.text().strip()
            if russian and meaning:
                self._vocab.append((russian, meaning))
                item = QListWidgetItem(f"{russian} — {meaning}")
                item.setData(Qt.ItemDataRole.UserRole, (russian, meaning))
                self._list_widget.addItem(item)

    def _remove_word(self):
        current = self._list_widget.currentItem()
        if current is None:
            return
        idx = self._list_widget.row(current)
        self._list_widget.takeItem(idx)
        self._vocab.pop(idx)

    def _export_vocab(self):
        path, _ = QFileDialog.getSaveFileName(
            self, tr("vocab_export"), "", "JSON (*.json)"
        )
        if not path:
            return
        data = [[r, m] for r, m in self._vocab]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "", tr("vocab_export_success", n=len(self._vocab)))

    def _import_vocab(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("vocab_import"), "", "JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            imported = [(str(item[0]), str(item[1])) for item in data]
        except Exception:
            QMessageBox.warning(self, "", tr("vocab_import_error"))
            return

        if self._vocab:
            reply = QMessageBox.question(
                self, "", tr("vocab_import_confirm"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._vocab = imported
        self._populate_list()
        QMessageBox.information(self, "", tr("vocab_import_success", n=len(self._vocab)))

    def get_vocabulary(self) -> list[tuple[str, str]]:
        return self._vocab[:]
