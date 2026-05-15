from PyQt6.QtCore import Qt

BG       = "#1e1e1e"
SURFACE  = "#2a2a2a"
SURFACE2 = "#333333"
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
ERROR_BG = "#4a2020"
RED      = "#e74c3c"
BLUE     = "#2980b9"

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

QSS = QSS.strip()
