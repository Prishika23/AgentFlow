from pathlib import Path
import time


def _import_win32():
    try:
        import pythoncom
        import win32com.client
        return pythoncom, win32com.client
    except ImportError as exc:
        raise RuntimeError("Microsoft Office automation requires pywin32. Run: pip install pywin32") from exc


def _active_word():
    pythoncom, win32 = _import_win32()
    try:
        return win32.GetActiveObject("Word.Application")
    except Exception:
        return None


def _active_excel():
    pythoncom, win32 = _import_win32()
    try:
        return win32.GetActiveObject("Excel.Application")
    except Exception:
        return None


def _active_powerpoint():
    pythoncom, win32 = _import_win32()
    try:
        return win32.GetActiveObject("PowerPoint.Application")
    except Exception:
        return None


def word_status():
    app = _active_word()
    if app is None:
        return {"running": False, "documents": [], "active_document": None}
    docs = []
    for doc in app.Documents:
        docs.append({"name": doc.Name, "path": doc.FullName if doc.Path else ""})
    active = None
    try:
        active = {"name": app.ActiveDocument.Name, "path": app.ActiveDocument.FullName if app.ActiveDocument.Path else ""}
    except Exception:
        pass
    return {"running": True, "documents": docs, "active_document": active}


def word_new_document():
    pythoncom, win32 = _import_win32()
    app = _active_word()
    if app is None:
        app = win32.Dispatch("Word.Application")
        app.Visible = True
    else:
        app.Visible = True
    doc = app.Documents.Add()
    app.Activate()
    time.sleep(0.7)
    return {"status": "success", "document": doc.Name, "message": "Created a new blank Word document."}


def word_open(path):
    path = str(Path(path).expanduser().resolve())
    if not Path(path).exists():
        raise FileNotFoundError(f"Word document not found: {path}")
    pythoncom, win32 = _import_win32()
    app = _active_word() or win32.Dispatch("Word.Application")
    app.Visible = True
    doc = app.Documents.Open(path)
    app.Activate()
    return {"status": "success", "document": doc.Name, "path": path}


def word_type(text, replace_selection=False):
    app = _active_word()
    if app is None:
        raise RuntimeError("Word is not running.")
    app.Visible = True
    if app.Documents.Count == 0:
        app.Documents.Add()
    doc = app.ActiveDocument
    app.Activate()
    rng = doc.Range(doc.Content.End - 1, doc.Content.End - 1)
    if replace_selection:
        rng = app.Selection.Range
    rng.InsertAfter(str(text))
    return {"status": "success", "document": doc.Name, "characters": len(str(text))}


def word_save(path=None):
    app = _active_word()
    if app is None or app.Documents.Count == 0:
        raise RuntimeError("No active Word document to save.")
    doc = app.ActiveDocument
    if path:
        path = str(Path(path).expanduser().resolve())
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        doc.SaveAs2(path)
    else:
        doc.Save()
        path = doc.FullName
    return {"status": "success", "path": path, "document": doc.Name}


def word_save_as(path):
    return word_save(path)


def word_add_heading(text, level=1):
    app = _active_word()
    if app is None or app.Documents.Count == 0:
        raise RuntimeError("No active Word document.")
    doc = app.ActiveDocument
    p = doc.Paragraphs.Add()
    p.Range.Text = str(text)
    try:
        p.Range.Style = f"Heading {int(level)}"
    except Exception:
        pass
    p.Range.InsertParagraphAfter()
    return {"status": "success", "document": doc.Name}


def excel_status():
    app = _active_excel()
    if app is None:
        return {"running": False, "workbooks": [], "active_workbook": None}
    books = []
    for wb in app.Workbooks:
        books.append({"name": wb.Name, "path": wb.FullName if wb.Path else ""})
    active = None
    try:
        wb = app.ActiveWorkbook
        active = {"name": wb.Name, "path": wb.FullName if wb.Path else ""}
    except Exception:
        pass
    return {"running": True, "workbooks": books, "active_workbook": active}


def excel_new_workbook():
    pythoncom, win32 = _import_win32()
    app = _active_excel()
    if app is None:
        app = win32.Dispatch("Excel.Application")
        app.Visible = True
    else:
        app.Visible = True
    wb = app.Workbooks.Add()
    app.Activate()
    return {"status": "success", "workbook": wb.Name, "message": "Created a new blank Excel workbook."}


def excel_open(path):
    path = str(Path(path).expanduser().resolve())
    if not Path(path).exists():
        raise FileNotFoundError(f"Excel workbook not found: {path}")
    pythoncom, win32 = _import_win32()
    app = _active_excel() or win32.Dispatch("Excel.Application")
    app.Visible = True
    wb = app.Workbooks.Open(path)
    app.Activate()
    return {"status": "success", "workbook": wb.Name, "path": path}


def _excel_sheet(app, sheet_name=None):
    if app.Workbooks.Count == 0:
        app.Workbooks.Add()
    wb = app.ActiveWorkbook
    if sheet_name:
        try:
            return wb.Worksheets(str(sheet_name))
        except Exception:
            return wb.Worksheets.Add()
    return wb.ActiveSheet


def excel_write_cell(cell, value, sheet=None):
    app = _active_excel()
    if app is None:
        raise RuntimeError("Excel is not running.")
    ws = _excel_sheet(app, sheet)
    ws.Range(str(cell)).Value = value
    app.Visible = True
    app.Activate()
    return {"status": "success", "cell": str(cell), "value": value, "sheet": ws.Name}


def excel_write_range(start_cell, data, sheet=None):
    app = _active_excel()
    if app is None:
        raise RuntimeError("Excel is not running.")
    ws = _excel_sheet(app, sheet)
    rows = data if isinstance(data, list) else [[data]]
    normalized = [r if isinstance(r, list) else [r] for r in rows]
    r0 = ws.Range(str(start_cell)).Row
    c0 = ws.Range(str(start_cell)).Column
    r1 = r0 + len(normalized) - 1
    c1 = c0 + max(len(r) for r in normalized) - 1
    padded = [r + [""] * (c1 - c0 + 1 - len(r)) for r in normalized]
    ws.Range(ws.Cells(r0, c0), ws.Cells(r1, c1)).Value = padded
    app.Visible = True
    app.Activate()
    return {"status": "success", "start_cell": str(start_cell), "rows": len(normalized), "sheet": ws.Name}


def excel_formula(cell, formula, sheet=None):
    app = _active_excel()
    if app is None:
        raise RuntimeError("Excel is not running.")
    ws = _excel_sheet(app, sheet)
    value = str(formula)
    if not value.startswith("="):
        value = "=" + value
    ws.Range(str(cell)).Formula = value
    app.Visible = True
    app.Activate()
    return {"status": "success", "cell": str(cell), "formula": value, "sheet": ws.Name}


def excel_save(path=None):
    app = _active_excel()
    if app is None or app.Workbooks.Count == 0:
        raise RuntimeError("No active Excel workbook to save.")
    wb = app.ActiveWorkbook
    if path:
        path = str(Path(path).expanduser().resolve())
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        # 51 = xlsx, 52 = xlsm. Keep normal .xlsx by default.
        ext = Path(path).suffix.lower()
        file_format = 52 if ext == ".xlsm" else 51
        wb.SaveAs(path, FileFormat=file_format)
    else:
        wb.Save()
        path = wb.FullName
    return {"status": "success", "path": path, "workbook": wb.Name}


def powerpoint_status():
    app = _active_powerpoint()
    if app is None:
        return {"running": False, "presentations": [], "active_presentation": None}
    presentations = []
    for p in app.Presentations:
        presentations.append({"name": p.Name, "path": p.FullName})
    active = None
    try:
        p = app.ActivePresentation
        active = {"name": p.Name, "path": p.FullName}
    except Exception:
        pass
    return {"running": True, "presentations": presentations, "active_presentation": active}


def powerpoint_new():
    pythoncom, win32 = _import_win32()
    app = _active_powerpoint()
    if app is None:
        app = win32.Dispatch("PowerPoint.Application")
        app.Visible = True
    else:
        app.Visible = True
    presentation = app.Presentations.Add()
    app.Activate()
    return {"status": "success", "presentation": presentation.Name}


def powerpoint_add_slide(title, body=""):
    app = _active_powerpoint()
    if app is None or app.Presentations.Count == 0:
        raise RuntimeError("No active PowerPoint presentation.")
    presentation = app.ActivePresentation
    slide = presentation.Slides.Add(presentation.Slides.Count + 1, 12)
    slide.Shapes.Title.TextFrame.TextRange.Text = str(title)
    if body:
        slide.Shapes.Placeholders(2).TextFrame.TextRange.Text = str(body)
    return {"status": "success", "slide": presentation.Slides.Count}


def powerpoint_save(path=None):
    app = _active_powerpoint()
    if app is None or app.Presentations.Count == 0:
        raise RuntimeError("No active PowerPoint presentation to save.")
    p = app.ActivePresentation
    if path:
        path = str(Path(path).expanduser().resolve())
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        p.SaveAs(path)
    else:
        p.Save()
        path = p.FullName
    return {"status": "success", "path": path, "presentation": p.Name}
