# utils.py
import json
from pathlib import Path
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

# --- Tab files ---
TAB_FILES = {
    "drivers": "drivers.json",
    "teams": "teams.json",
    "engines": "engines.json",
    "sponsors": "sponsors.json",
    "staff": "staff.json",
    "events": "events.json",
    "config": "config.json",
    "schedule": "schedule.json",
    "tyre_suppliers": "tyre_suppliers.json"
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
