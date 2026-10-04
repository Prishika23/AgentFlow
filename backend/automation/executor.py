import time

from .applications import open_application, close_active_window
from .keyboard import type_text, press_key, hotkey
from .mouse import click, double_click
from .files import create_folder, create_file, rename_file, move_file
from .browser import open_url, search_web, open_chrome
from .windows import active_window
from .state_detector import detect_application, detect_system_state
from .verifier import verify_action
from .office import (
    word_status, word_new_document, word_open, word_type, word_save, word_save_as, word_add_heading,
    excel_status, excel_new_workbook, excel_open, excel_write_cell, excel_write_range, excel_formula, excel_save,
    powerpoint_status, powerpoint_new, powerpoint_add_slide, powerpoint_save,
)
from .email import send_email
from .reminders import set_reminder


def execute_action(action):
    if not isinstance(action, dict):
        raise ValueError(f"Invalid action: expected object, got {type(action).__name__}")
    t = action.get("type")
    if not isinstance(t, str) or not t.strip():
        raise ValueError("Invalid action: missing action type")
    a = action.get("args")
    if not isinstance(a, dict):
        a = {}

    if t == "OPEN_APPLICATION": return open_application(a["application"], reuse=a.get("reuse", True))
    if t == "CLOSE_ACTIVE_WINDOW": return close_active_window()
    if t == "TYPE": return type_text(a["text"])
    if t == "KEY_PRESS": return press_key(a["key"])
    if t == "HOTKEY": return hotkey(a["keys"])
    if t == "CLICK": return click(a.get("x"), a.get("y"), a.get("button", "left"))
    if t == "DOUBLE_CLICK": return double_click(a.get("x"), a.get("y"))
    if t == "WAIT":
        time.sleep(float(a.get("seconds", 1))); return "Wait completed"
    if t == "CREATE_FOLDER": return create_folder(a["path"])
    if t == "CREATE_FILE": return create_file(a["path"], a.get("content", ""))
    if t == "RENAME_FILE": return rename_file(a["source"], a["destination"])
    if t == "MOVE_FILE": return move_file(a["source"], a["destination"])
    if t == "OPEN_URL": return open_url(a["url"])
    if t == "SEARCH_WEB": return search_web(a["query"])
    if t == "GET_ACTIVE_WINDOW": return active_window()
    if t == "OBSERVE_SYSTEM": return detect_system_state()
    if t == "OBSERVE_APPLICATION": return detect_application(a["application"])
    if t == "VERIFY": return verify_action(a.get("action", {}), a.get("result"))
    if t == "BROWSER_OPEN": return open_chrome()
    if t == "BROWSER_OPEN_URL": return open_url(a["url"])
    if t == "BROWSER_SEARCH": return search_web(a["query"])
    if t == "WORD_STATUS": return word_status()
    if t == "WORD_NEW_DOCUMENT": return word_new_document()
    if t == "WORD_OPEN": return word_open(a["path"])
    if t == "WORD_TYPE": return word_type(a["text"], a.get("replace_selection", False))
    if t == "WORD_ADD_HEADING": return word_add_heading(a["text"], a.get("level", 1))
    if t == "WORD_SAVE": return word_save(a.get("path"))
    if t == "WORD_SAVE_AS": return word_save_as(a["path"])
    if t == "EXCEL_STATUS": return excel_status()
    if t == "EXCEL_NEW_WORKBOOK": return excel_new_workbook()
    if t == "EXCEL_OPEN": return excel_open(a["path"])
    if t == "EXCEL_WRITE_CELL": return excel_write_cell(a["cell"], a.get("value", ""), a.get("sheet"))
    if t == "EXCEL_WRITE_RANGE": return excel_write_range(a["start_cell"], a["data"], a.get("sheet"))
    if t == "EXCEL_FORMULA": return excel_formula(a["cell"], a["formula"], a.get("sheet"))
    if t == "EXCEL_SAVE": return excel_save(a.get("path"))
    if t == "POWERPOINT_STATUS": return powerpoint_status()
    if t == "POWERPOINT_NEW": return powerpoint_new()
    if t == "POWERPOINT_ADD_SLIDE": return powerpoint_add_slide(a["title"], a.get("body", ""))
    if t == "POWERPOINT_SAVE": return powerpoint_save(a.get("path"))
    if t == "SEND_EMAIL": return send_email(a["to"], a.get("subject", ""), a.get("body", ""))
    if t == "SET_REMINDER": return set_reminder(a["title"], a["datetime"])
    raise ValueError(f"Unsupported action: {t}")
