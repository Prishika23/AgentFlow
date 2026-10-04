import os
import subprocess
import time
from pathlib import Path

import pyautogui

from .windows import focus_window, process_running

APP_ALIASES = {
    "calculator": "calc.exe", "calc": "calc.exe",
    "notepad": "notepad.exe", "wordpad": "write.exe",
    "word": "winword.exe", "microsoft word": "winword.exe",
    "excel": "excel.exe", "microsoft excel": "excel.exe",
    "powerpoint": "powerpnt.exe", "microsoft powerpoint": "powerpnt.exe",
    "chrome": "chrome.exe", "google chrome": "chrome.exe",
    "edge": "msedge.exe", "microsoft edge": "msedge.exe",
    "paint": "mspaint.exe",
    "file explorer": "explorer.exe", "explorer": "explorer.exe",
    "vscode": "code.exe", "vs code": "code.exe", "visual studio code": "code.exe",
    "outlook": "outlook.exe", "microsoft outlook": "outlook.exe",
}


def _chrome_path():
    candidates = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    return next((p for p in candidates if os.path.exists(p)), None)


def _chrome_profile_dir():
    root = Path(os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"))
    if not root.exists():
        return None
    preferred = root / "Default"
    if preferred.exists():
        return "Default"
    profiles = sorted([p.name for p in root.glob("Profile *") if p.is_dir()])
    return profiles[0] if profiles else None


def application_running(name):
    target = APP_ALIASES.get(str(name).strip().lower(), str(name).strip().lower())
    return process_running([target])


def open_application(name, reuse=True):
    original = str(name).strip()
    key = original.lower()
    target = APP_ALIASES.get(key, key)

    if reuse:
        focus_patterns = {
            "word": [r"Microsoft Word"], "microsoft word": [r"Microsoft Word"],
            "excel": [r"Microsoft Excel"], "microsoft excel": [r"Microsoft Excel"],
            "powerpoint": [r"PowerPoint"], "microsoft powerpoint": [r"PowerPoint"],
            "chrome": [r"Google Chrome"], "google chrome": [r"Google Chrome"],
            "edge": [r"Microsoft Edge"], "notepad": [r"Notepad"],
            "vscode": [r"Visual Studio Code"], "vs code": [r"Visual Studio Code"],
        }
        if focus_window(patterns=focus_patterns.get(key, [])):
            return f"Focused existing {original}"

    if key in {"chrome", "google chrome"}:
        path = _chrome_path()
        if path:
            profile = _chrome_profile_dir()
            args = [path]
            if profile:
                args += [f"--profile-directory={profile}"]
            subprocess.Popen(args, shell=False)
        else:
            subprocess.Popen(["cmd", "/c", "start", "", "chrome.exe"], shell=False)
        time.sleep(4)
        return "Opened Google Chrome"

    if os.path.isabs(target) and os.path.exists(target):
        subprocess.Popen([target], shell=False)
    else:
        subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)

    time.sleep(5 if key in {"word", "microsoft word", "excel", "microsoft excel", "powerpoint", "microsoft powerpoint", "outlook"} else 2)
    return f"Opened {original}"


def close_active_window():
    pyautogui.hotkey("alt", "f4")
    time.sleep(0.7)
    return "Closed active window"
