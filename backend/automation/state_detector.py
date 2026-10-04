import os
from pathlib import Path

import psutil

from .windows import active_window, list_windows


def _running(names):
    names = {n.lower() for n in names}
    try:
        return any((p.info.get("name") or "").lower() in names for p in psutil.process_iter(["name"]))
    except Exception:
        return False


def detect_application(application):
    name = str(application).strip().lower()
    process_map = {
        "word": ["winword.exe"],
        "microsoft word": ["winword.exe"],
        "excel": ["excel.exe"],
        "microsoft excel": ["excel.exe"],
        "powerpoint": ["powerpnt.exe"],
        "microsoft powerpoint": ["powerpnt.exe"],
        "chrome": ["chrome.exe"],
        "google chrome": ["chrome.exe"],
        "edge": ["msedge.exe"],
        "notepad": ["notepad.exe"],
        "calculator": ["calculatorapp.exe", "calc.exe"],
        "calc": ["calculatorapp.exe", "calc.exe"],
        "vscode": ["code.exe"],
        "vs code": ["code.exe"],
        "visual studio code": ["code.exe"],
        "outlook": ["outlook.exe"],
        "paint": ["mspaint.exe"],
        "file explorer": ["explorer.exe"],
        "explorer": ["explorer.exe"],
    }
    running = _running(process_map.get(name, [name if name.endswith(".exe") else f"{name}.exe"]))
    aw = active_window()
    title = (aw.get("title") or "").lower()
    title_hints = {
        "word": ["word"], "microsoft word": ["word"],
        "excel": ["excel"], "microsoft excel": ["excel"],
        "powerpoint": ["powerpoint"], "microsoft powerpoint": ["powerpoint"],
        "chrome": ["chrome"], "google chrome": ["chrome"],
        "edge": ["edge"], "notepad": ["notepad"],
        "outlook": ["outlook"], "paint": ["paint"],
        "vscode": ["visual studio code", "vs code"],
        "vs code": ["visual studio code", "vs code"],
    }
    active = any(h in title for h in title_hints.get(name, []))
    return {
        "application": application,
        "running": running,
        "active": active,
        "active_window": aw,
        "windows": list_windows()[:30],
    }


def detect_system_state():
    return {
        "active_window": active_window(),
        "desktop": str(Path.home() / "Desktop"),
        "documents": str(Path.home() / "Documents"),
        "downloads": str(Path.home() / "Downloads"),
        "applications": {
            app: detect_application(app)
            for app in ("Word", "Excel", "PowerPoint", "Chrome", "Notepad", "Calculator", "VS Code")
        },
    }
