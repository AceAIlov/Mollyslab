import json
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "logs" / "reflect_logs.json"

def load_feelings(limit: int = 5):
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH, encoding="utf-8") as f:
        entries = json.load(f)
    return entries[-limit:]
