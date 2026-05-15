from PyQt6.QtCore import Qt

LAYOUTS: dict[str, list[list[tuple[str, str, str]]]] = {
    "ЙЦУКЕН": [
        [("й","Й","Q"),("ц","Ц","W"),("у","У","E"),("к","К","R"),("е","Е","T"),
         ("н","Н","Y"),("г","Г","U"),("ш","Ш","I"),("щ","Щ","O"),("з","З","P"),
         ("х","Х","["),("ъ","Ъ","]")],
        [("ф","Ф","A"),("ы","Ы","S"),("в","В","D"),("а","А","F"),("п","П","G"),
         ("р","Р","H"),("о","О","J"),("л","Л","K"),("д","Д","L"),("ж","Ж",";"),
         ("э","Э","'")],
        [("я","Я","Z"),("ч","Ч","X"),("с","С","C"),("м","М","V"),("и","И","B"),
         ("т","Т","N"),("ь","Ь","M"),("б","Б",","),("ю","Ю",".")],
    ],
    "Fonético": [
        [("я","Я","Q"),("в","В","W"),("е","Е","E"),("р","Р","R"),("т","Т","T"),
         ("ы","Ы","Y"),("у","У","U"),("и","И","I"),("о","О","O"),("п","П","P"),
         ("ш","Ш","["),("щ","Щ","]")],
        [("а","А","A"),("с","С","S"),("д","Д","D"),("ф","Ф","F"),("г","Г","G"),
         ("х","Х","H"),("й","Й","J"),("к","К","K"),("л","Л","L"),("э","Э",";"),
         ("ъ","Ъ","'")],
        [("з","З","Z"),("ж","Ж","X"),("ц","Ц","C"),("ч","Ч","V"),("б","Б","B"),
         ("н","Н","N"),("м","М","M"),("ь","Ь",","),("ю","Ю",".")],
    ],
}

QWERTY_ROWS: list[list[Qt.Key]] = [
    [Qt.Key.Key_Q, Qt.Key.Key_W, Qt.Key.Key_E, Qt.Key.Key_R, Qt.Key.Key_T,
     Qt.Key.Key_Y, Qt.Key.Key_U, Qt.Key.Key_I, Qt.Key.Key_O, Qt.Key.Key_P,
     Qt.Key.Key_BracketLeft, Qt.Key.Key_BracketRight],
    [Qt.Key.Key_A, Qt.Key.Key_S, Qt.Key.Key_D, Qt.Key.Key_F, Qt.Key.Key_G,
     Qt.Key.Key_H, Qt.Key.Key_J, Qt.Key.Key_K, Qt.Key.Key_L,
     Qt.Key.Key_Semicolon, Qt.Key.Key_Apostrophe],
    [Qt.Key.Key_Z, Qt.Key.Key_X, Qt.Key.Key_C, Qt.Key.Key_V, Qt.Key.Key_B,
     Qt.Key.Key_N, Qt.Key.Key_M, Qt.Key.Key_Comma, Qt.Key.Key_Period],
]

ROW_INDENT = [0, 18, 36]
KEY_SPACING = 3


def build_mapping(layout_name: str) -> dict[Qt.Key, tuple[str, str]]:
    mapping: dict[Qt.Key, tuple[str, str]] = {}
    for qt_row, layout_row in zip(QWERTY_ROWS, LAYOUTS[layout_name]):
        for qt_key, (lower, upper, _) in zip(qt_row, layout_row):
            mapping[qt_key] = (lower, upper)
    mapping[Qt.Key.Key_QuoteLeft] = ("ё", "Ё")
    return mapping
