from pathlib import Path
import shutil


def create_folder(path):
    path = Path(path).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return f"Created folder {path}"


def create_file(path, content=""):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(content), encoding="utf-8")
    return f"Created file {path}"


def rename_file(source, destination):
    source = Path(source).expanduser()
    destination = Path(destination).expanduser()
    if not source.exists():
        raise FileNotFoundError(f"File not found: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    source.rename(destination)
    return f"Renamed to {destination}"


def move_file(source, destination):
    source = Path(source).expanduser()
    destination = Path(destination).expanduser()
    if not source.exists():
        raise FileNotFoundError(f"File not found: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))
    return f"Moved {source} to {destination}"
