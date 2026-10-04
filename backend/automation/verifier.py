from pathlib import Path
import time

from .state_detector import detect_application
from .windows import active_window


def verify_action(action, result):
    if not isinstance(action, dict):
        return {"verified": False, "observation": "Invalid action object"}
    t = action.get("type")
    a = action.get("args") if isinstance(action.get("args"), dict) else {}

    if t == "OPEN_APPLICATION":
        state = detect_application(a.get("application", ""))
        return {"verified": bool(state.get("running") or state.get("active")), "observation": state}

    if t in {"CREATE_FILE", "WORD_SAVE", "EXCEL_SAVE", "POWERPOINT_SAVE"}:
        path = a.get("path") or a.get("filename")
        if not path and isinstance(result, dict):
            path = result.get("path")
        if path:
            return {"verified": Path(str(path)).expanduser().exists(), "observation": {"path": str(path)}}

    if t == "CREATE_FOLDER":
        path = a.get("path")
        return {"verified": bool(path and Path(str(path)).expanduser().is_dir()), "observation": {"path": str(path)}}

    if t in {"WORD_NEW_DOCUMENT", "WORD_OPEN", "WORD_TYPE", "WORD_ADD_HEADING", "EXCEL_NEW_WORKBOOK", "EXCEL_OPEN", "EXCEL_WRITE_CELL", "EXCEL_WRITE_RANGE", "EXCEL_FORMULA"}:
        return {"verified": True, "observation": {"result": result}}

    if t in {"OPEN_URL", "SEARCH_WEB", "BROWSER_OPEN_URL", "BROWSER_SEARCH"}:
        time.sleep(0.5)
        return {"verified": True, "observation": active_window()}

    return {"verified": True, "observation": {"result": result}}
