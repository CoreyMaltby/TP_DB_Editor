# utils.py
import sys
import json
from pathlib import Path

# --- Paths ---
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)  # when bundled with PyInstaller
    EXEC_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent
    EXEC_DIR = BASE_DIR

DATA_DIR = EXEC_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# --- Tab files ---
TAB_FILES = {
    "config": "config.json",
    "drivers": "drivers.json",
    "teams": "teams.json",
    "engines": "engines.json",
    "sponsors": "sponsors.json",
    "staff": "staff.json",
    "events": "events.json",
}

# --- Colour Scheme ---
BG = "#393E41"
TEXT = "#D3D0CB"
ACCENT = "#B80C09"

# --- JSON Helpers ---
def read_json(path: Path):
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to read {path}: {e}")
        return []

def write_json(path: Path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to write {path}: {e}")
