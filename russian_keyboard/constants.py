from PyQt6.QtCore import Qt


DARK = {
    "BG": "#1e1e1e",
    "SURFACE": "#2a2a2a",
    "SURFACE2": "#333333",
    "KEY_BG": "#3c3c3c",
    "KEY_HOV": "#4a4a4a",
    "KEY_ACT": "#e94560",
    "FG": "#e8e8e8",
    "FG_DIM": "#b0b0b0",
    "AREA_BG": "#141414",
    "GREEN": "#2ecc71",
    "RED_BTN": "#c0392b",
    "BLUE_BTN": "#2980b9",
    "ORANGE": "#c67c00",
    "HIST_BG": "#1e1e1e",
    "HIST_SEL": "#383838",
    "ERROR_BG": "#4a2020",
    "RED": "#e74c3c",
    "BLUE": "#2980b9",
    "BORDER": "#404040",
    "BORDER_HOVER": "#606060",
    "BS_BG": "#4a2020",
    "BS_FG": "#ff8080",
    "BS_BORDER": "#6a3030",
    "BS_HOV_BG": "#5c2828",
    "BS_HOV_FG": "#ffaaaa",
    "BS_HOV_BORDER": "#884040",
    "GREEN_HOV": "#3dde8a",
    "ORANGE_HOV": "#e09000",
    "BLUE_HOV": "#3498db",
    "BLUE_PRESSED": "#217dbb",
}

LIGHT = {
    "BG": "#f0f0f0",
    "SURFACE": "#ffffff",
    "SURFACE2": "#dcdcdc",
    "KEY_BG": "#d0d0d0",
    "KEY_HOV": "#b8b8b8",
    "KEY_ACT": "#e94560",
    "FG": "#1a1a1a",
    "FG_DIM": "#666666",
    "AREA_BG": "#ffffff",
    "GREEN": "#27ae60",
    "RED_BTN": "#c0392b",
    "BLUE_BTN": "#2980b9",
    "ORANGE": "#c67c00",
    "HIST_BG": "#ffffff",
    "HIST_SEL": "#dcdcdc",
    "ERROR_BG": "#ffe0e0",
    "RED": "#c0392b",
    "BLUE": "#2980b9",
    "BORDER": "#c0c0c0",
    "BORDER_HOVER": "#a0a0a0",
    "BS_BG": "#e8c0c0",
    "BS_FG": "#8b3a3a",
    "BS_BORDER": "#c0a0a0",
    "BS_HOV_BG": "#dbb0b0",
    "BS_HOV_FG": "#6b2a2a",
    "BS_HOV_BORDER": "#a08080",
    "GREEN_HOV": "#3dde8a",
    "ORANGE_HOV": "#e09000",
    "BLUE_HOV": "#5dade2",
    "BLUE_PRESSED": "#217dbb",
}


_current_theme_name = "dark"
_current_theme = DARK

BG = _current_theme["BG"]
SURFACE = _current_theme["SURFACE"]
SURFACE2 = _current_theme["SURFACE2"]
KEY_BG = _current_theme["KEY_BG"]
KEY_HOV = _current_theme["KEY_HOV"]
KEY_ACT = _current_theme["KEY_ACT"]
FG = _current_theme["FG"]
FG_DIM = _current_theme["FG_DIM"]
AREA_BG = _current_theme["AREA_BG"]
GREEN = _current_theme["GREEN"]
RED_BTN = _current_theme["RED_BTN"]
BLUE_BTN = _current_theme["BLUE_BTN"]
ORANGE = _current_theme["ORANGE"]
HIST_BG = _current_theme["HIST_BG"]
HIST_SEL = _current_theme["HIST_SEL"]
ERROR_BG = _current_theme["ERROR_BG"]
RED = _current_theme["RED"]
BLUE = _current_theme["BLUE"]
BORDER = _current_theme["BORDER"]
BORDER_HOVER = _current_theme["BORDER_HOVER"]
BS_BG = _current_theme["BS_BG"]
BS_FG = _current_theme["BS_FG"]
BS_BORDER = _current_theme["BS_BORDER"]
BS_HOV_BG = _current_theme["BS_HOV_BG"]
BS_HOV_FG = _current_theme["BS_HOV_FG"]
BS_HOV_BORDER = _current_theme["BS_HOV_BORDER"]
GREEN_HOV = _current_theme["GREEN_HOV"]
ORANGE_HOV = _current_theme["ORANGE_HOV"]
BLUE_HOV = _current_theme["BLUE_HOV"]
BLUE_PRESSED = _current_theme["BLUE_PRESSED"]


def _build_qss() -> str:
    return f"""
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
    font-size: 13px;
}}
QTabBar::tab:selected {{
    background: {KEY_ACT}; color: white;
}}
QTabBar::tab:hover:!selected {{
    background: {KEY_HOV}; color: {FG};
}}

QTextEdit {{
    background: {AREA_BG}; color: {FG};
    border: 1px solid {BORDER}; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    padding: 8px;
    selection-background-color: {KEY_ACT};
}}
QLabel#status {{
    color: {FG_DIM}; font-size: 13px; padding: 2px 0 4px 0;
}}
QLabel#title {{
    color: {FG}; font-size: 20px; font-weight: 800;
    font-family: Consolas, "Courier New", monospace;
}}
QLabel#histTitle {{
    color: {FG}; font-size: 18px; font-weight: 700;
    font-family: Consolas, "Courier New", monospace;
    padding: 4px 0 2px 0;
}}
QLabel#kbHint {{
    color: {FG_DIM}; font-size: 13px;
    font-family: Consolas, "Courier New", monospace;
    padding: 0 0 2px 0;
}}
QRadioButton {{
    color: {FG};
    font-family: Consolas, "Courier New", monospace;
    font-size: 14px; spacing: 6px;
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
    background: {SURFACE2}; color: {FG}; border: 1px solid {BORDER};
    border-radius: 5px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 13px; font-weight: 600;
    letter-spacing: 1px;
}}
QPushButton#wideKey:hover   {{ background: {KEY_HOV}; color: {FG}; border-color: {BORDER_HOVER}; }}
QPushButton#wideKey:pressed {{ background: {KEY_ACT}; color: white; border-color: {KEY_ACT}; }}

QPushButton#bsKey {{
    background: {BS_BG}; color: {BS_FG}; border: 1px solid {BS_BORDER};
    border-radius: 5px;
    font-size: 18px; font-weight: bold;
}}
QPushButton#bsKey:hover   {{ background: {BS_HOV_BG}; color: {BS_HOV_FG}; border-color: {BS_HOV_BORDER}; }}
QPushButton#bsKey:pressed {{ background: {KEY_ACT}; color: white; border-color: {KEY_ACT}; }}

QPushButton#shiftKey {{
    background: {BLUE_BTN}; color: white; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 13px; font-weight: bold;
}}
QPushButton#shiftKey:hover {{ background: {BLUE_HOV}; }}
QPushButton#shiftKey:pressed {{ background: {BLUE_PRESSED}; }}
QPushButton#shiftKey[active="true"] {{
    background: {KEY_ACT}; color: white;
}}

QPushButton#actionGreen {{
    background: {GREEN}; color: white; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px; font-weight: bold; padding: 6px 14px;
}}
QPushButton#actionGreen:hover {{ background: {GREEN_HOV}; }}

QPushButton#actionRed {{
    background: {RED_BTN}; color: white; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px; font-weight: bold; padding: 6px 14px;
}}
QPushButton#actionRed:hover {{ background: {RED}; }}

QPushButton#actionBlue {{
    background: {BLUE_BTN}; color: white; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px; font-weight: bold; padding: 6px 14px;
}}
QPushButton#actionBlue:hover {{ background: {BLUE_HOV}; }}

QPushButton#actionOrange {{
    background: {ORANGE}; color: white; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px; font-weight: bold; padding: 6px 14px;
}}
QPushButton#actionOrange:hover {{ background: {ORANGE_HOV}; }}

QPushButton#histSmall {{
    background: {SURFACE2}; color: {FG_DIM}; border: none; border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px; padding: 4px 8px;
}}
QPushButton#histSmall:hover {{ background: {KEY_HOV}; color: {FG}; }}

QListWidget {{
    background: {HIST_BG}; color: {FG}; border: 1px solid {SURFACE};
    border-radius: 4px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px;
    outline: 0;
}}
QListWidget::item {{
    padding: 4px 6px; border-bottom: 1px solid {SURFACE};
}}
QListWidget::item:hover    {{ background: {HIST_SEL}; }}
QListWidget::item:selected {{ background: {KEY_BG}; color: {FG}; }}

QFrame#divider {{ background: {SURFACE}; }}
"""


QSS = _build_qss()


def set_theme(name: str):
    global _current_theme_name, _current_theme
    global BG, SURFACE, SURFACE2, KEY_BG, KEY_HOV, KEY_ACT
    global FG, FG_DIM, AREA_BG, GREEN, RED_BTN, BLUE_BTN, ORANGE
    global HIST_BG, HIST_SEL, ERROR_BG, RED, BLUE
    global BORDER, BORDER_HOVER
    global BS_BG, BS_FG, BS_BORDER, BS_HOV_BG, BS_HOV_FG, BS_HOV_BORDER
    global GREEN_HOV, ORANGE_HOV, BLUE_HOV, BLUE_PRESSED
    global QSS

    if name == "dark":
        _current_theme = DARK
    else:
        _current_theme = LIGHT
    _current_theme_name = name

    BG = _current_theme["BG"]
    SURFACE = _current_theme["SURFACE"]
    SURFACE2 = _current_theme["SURFACE2"]
    KEY_BG = _current_theme["KEY_BG"]
    KEY_HOV = _current_theme["KEY_HOV"]
    KEY_ACT = _current_theme["KEY_ACT"]
    FG = _current_theme["FG"]
    FG_DIM = _current_theme["FG_DIM"]
    AREA_BG = _current_theme["AREA_BG"]
    GREEN = _current_theme["GREEN"]
    RED_BTN = _current_theme["RED_BTN"]
    BLUE_BTN = _current_theme["BLUE_BTN"]
    ORANGE = _current_theme["ORANGE"]
    HIST_BG = _current_theme["HIST_BG"]
    HIST_SEL = _current_theme["HIST_SEL"]
    ERROR_BG = _current_theme["ERROR_BG"]
    RED = _current_theme["RED"]
    BLUE = _current_theme["BLUE"]
    BORDER = _current_theme["BORDER"]
    BORDER_HOVER = _current_theme["BORDER_HOVER"]
    BS_BG = _current_theme["BS_BG"]
    BS_FG = _current_theme["BS_FG"]
    BS_BORDER = _current_theme["BS_BORDER"]
    BS_HOV_BG = _current_theme["BS_HOV_BG"]
    BS_HOV_FG = _current_theme["BS_HOV_FG"]
    BS_HOV_BORDER = _current_theme["BS_HOV_BORDER"]
    GREEN_HOV = _current_theme["GREEN_HOV"]
    ORANGE_HOV = _current_theme["ORANGE_HOV"]
    BLUE_HOV = _current_theme["BLUE_HOV"]
    BLUE_PRESSED = _current_theme["BLUE_PRESSED"]

    QSS = _build_qss()


def current_theme() -> str:
    return _current_theme_name


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
