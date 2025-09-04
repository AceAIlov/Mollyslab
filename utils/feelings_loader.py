from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

# Default location: <repo>/Sphinx/logs/reflect_logs.json
LOG_PATH: Path = Path(__file__).resolve().parent.parent / "logs" / "reflect_logs.json"

__all__ = ["load_feelings", "LOG_PATH"]


def load_feelings(limit: int = 5, path: Path | None = None) -> List[Dict[str, Any]]:
    """
    Load the latest N feeling/reflection entries.

    The log file may be either:
      • a JSON array:        [ {...}, {...}, ... ]
      • JSON lines (NDJSON): {...}\n{...}\n...

    Args:
        limit: maximum number of entries to return (from the end).
        path: optional override for the log path.

    Returns:
        A list of dict entries (possibly empty).
    """
    p = path or LOG_PATH
    if not p.exists():
        return []

    try:
        text = p.read_text(encoding="utf-8").strip()
        if not text:
            return []

        # Try JSON array first
        try:
            data = json.loads(text)
            if isinstance(data, list):
                entries = data
            elif isinstance(data, dict):
                entries = [data]
            else:
                entries = []
        except json.JSONDecodeError:
            # Fallback: parse as JSON Lines
            entries = []
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    # skip malformed lines
                    continue

        # Return the most recent 'limit' entries.
        return entries[-limit:] if limit and limit > 0 else entries

    except Exception:
        # On any unexpected error, be safe and return an empty list.
        return []
