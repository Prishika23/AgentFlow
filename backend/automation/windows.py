import re
import time

import psutil
import pygetwindow as gw


def active_window():
    try:
        w = gw.getActiveWindow()
        return {
            "title": w.title if w else None,
            "active": bool(w),
        }
    except Exception:
        return {"title": None, "active": False}


def list_windows():
    result = []
    try:
        for w in gw.getAllWindows():
            title = (w.title or "").strip()
            if title:
                result.append({"title": title, "visible": bool(w.visible)})
    except Exception:
        pass
    return result


def find_window(title_contains=None, patterns=None):
    title_contains = str(title_contains or "").lower().strip()
    patterns = patterns or []
    for w in gw.getAllWindows():
        title = (w.title or "").strip()
        lower = title.lower()
        if not title:
            continue
        if title_contains and title_contains in lower:
            return w
        if any(re.search(p, title, re.I) for p in patterns):
            return w
    return None


def focus_window(title_contains=None, patterns=None):
    w = find_window(title_contains, patterns)
    if not w:
        return False
    try:
        if w.isMinimized:
            w.restore()
        w.activate()
        time.sleep(0.5)
        return True
    except Exception:
        return False


def process_running(names):
    names = {str(n).lower() for n in names}
    try:
        return any((p.info.get("name") or "").lower() in names for p in psutil.process_iter(["name"]))
    except Exception:
        return False
