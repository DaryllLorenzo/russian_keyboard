# Russian Keyboard

A virtual keyboard GUI for typing Cyrillic on an English keyboard, built with PyQt6.

## Features

- **Two keyboard layouts**: ЙЦУКЕН (standard Russian) and Fonetico (QWERTY-based phonetic)
- **Physical keyboard support**: Type directly with your keyboard — Q/W/E... produce Cyrillic characters automatically
- **Phrase history**: Save and recall typed phrases
- **Font size control**: Adjust text area font size with a slider
- **Resizable window**: Keyboard scales automatically when resizing the window
- **Shift toggle**: Capitalize Cyrillic letters with the Shift key

## Requirements

- Python 3.14+
- PyQt6

## Installation

### Using uv (recommended)

```bash
uv sync
```

### Using conventional pip

```bash
pip install pyqt6
```

## Running

### Using uv

```bash
uv run python main.py
```

### Using conventional pip

```bash
python main.py
```

## Usage

1. Select a keyboard layout (ЙЦУКЕН or Fonetico) using the radio buttons
2. Click keys on the virtual keyboard or type directly with your physical keyboard
3. Press `Shift` to type uppercase Cyrillic letters
4. Use the backtick (`) key to type ё/Ё
5. Adjust the text area font size with the slider
6. Save phrases to history and recall them with a click
