import pyautogui


def click(x=None, y=None, button="left"):
    if x is None or y is None:
        pyautogui.click(button=button)
    else:
        pyautogui.click(int(x), int(y), button=button)
    return "Clicked"


def double_click(x=None, y=None):
    if x is None or y is None:
        pyautogui.doubleClick()
    else:
        pyautogui.doubleClick(int(x), int(y))
    return "Double-clicked"
