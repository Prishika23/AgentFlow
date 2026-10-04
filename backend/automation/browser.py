import os
import subprocess
import time
from pathlib import Path
from urllib.parse import quote_plus

from .applications import _chrome_path, _chrome_profile_dir
from .windows import focus_window


def _chrome_ready():
    return focus_window(patterns=[r"Google Chrome"])


def open_chrome(url=None):
    if _chrome_ready():
        if url:
            return open_url(url)
        return "Focused existing Google Chrome"
    path = _chrome_path()
    if path:
        args = [path]
        profile = _chrome_profile_dir()
        if profile:
            args.append(f"--profile-directory={profile}")
        if url:
            args.append(url)
        subprocess.Popen(args, shell=False)
    else:
        command = ["cmd", "/c", "start", "", "chrome.exe"]
        if url:
            command.append(url)
        subprocess.Popen(command, shell=False)
    time.sleep(4)
    return "Opened Google Chrome"


def open_url(url):
    url = str(url).strip()
    if not url:
        raise ValueError("URL is required.")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    if _chrome_ready():
        # Ctrl+L makes navigation reliable in the currently focused browser.
        import pyautogui
        pyautogui.hotkey("ctrl", "l")
        pyautogui.write(url, interval=0.001)
        pyautogui.press("enter")
    else:
        open_chrome(url)
    time.sleep(2)
    return f"Opened {url} in Chrome"


def search_web(query):
    query = str(query).strip()
    if not query:
        raise ValueError("Search query is required.")
    url = "https://www.google.com/search?q=" + quote_plus(query)
    return open_url(url)
