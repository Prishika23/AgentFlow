import time
import pyautogui
import pyperclip

SPECIAL_KEYS = {
    "ENTER": "enter", "TAB": "tab", "ESC": "esc", "ESCAPE": "esc",
    "SPACE": "space", "BACKSPACE": "backspace", "DELETE": "delete",
    "HOME": "home", "END": "end", "UP": "up", "DOWN": "down",
    "LEFT": "left", "RIGHT": "right", "PAGEUP": "pageup", "PAGEDOWN": "pagedown",
}


def type_text(text):
    text = str(text)
    try:
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
    except Exception:
        pyautogui.write(text, interval=0.01)
    time.sleep(0.4)
    return "Typed text"


def press_key(key):
    key = str(key).upper()
    pyautogui.press(SPECIAL_KEYS.get(key, key.lower()))
    time.sleep(0.2)
    return f"Pressed {key}"


def hotkey(keys):
    if isinstance(keys, str):
        keys = [x.strip() for x in keys.split("+")]
    keys = [str(x).lower() for x in keys]
    pyautogui.hotkey(*keys)
    time.sleep(0.3)
    return f"Pressed {'+'.join(keys)}"
