import json
import os


HISTORY_FILE = os.path.join("data", "analysis_history.json")


def _ensure_history_file():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_history_entries():
    _ensure_history_file()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return sorted(data, key=lambda row: str(row.get("analyzed_at", "")), reverse=True)
    except (json.JSONDecodeError, OSError):
        return []


def append_history_entry(entry):
    entries = load_history_entries()
    entries.append(entry)
    entries = sorted(entries, key=lambda row: str(row.get("analyzed_at", "")), reverse=True)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
