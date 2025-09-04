
from __future__ import annotations

from enum import Enum
from collections import deque
from datetime import datetime, timezone
from typing import Deque, List, Tuple


class SphinxMode(Enum):
    CALM = "CALM"
    FOCUSED = "FOCUSED"
    IDLE = "IDLE"
    IN_MEETING = "IN_MEETING"


# Backward-compat alias so existing imports/tests referring to `Emotion` won’t break.
Emotion = SphinxMode


class EmotionEngine:
    """
    Interprets lightweight triggers into a coarse 'mode' the Sphinx runtime can use
    for planning and approvals. Stays intentionally simple and deterministic.

    .react(trigger) returns the current Enum (kept for backward-compat with tests that
    access `state.name`). Use .history_events for auditing (mode, timestamp) tuples.
    """

    def __init__(self, max_history: int = 128):
        self.state: SphinxMode = SphinxMode.CALM
        self.history: Deque[SphinxMode] = deque(maxlen=max_history)
        self._when: Deque[datetime] = deque(maxlen=max_history)

    # --- Utilities ---------------------------------------------------------

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    @property
    def history_events(self) -> List[Tuple[SphinxMode, datetime]]:
        """List of (mode, timestamp) pairs (most recent last)."""
        return list(zip(self.history, self._when))

    # --- Public API --------------------------------------------------------

    def reset(self) -> None:
        self.state = SphinxMode.CALM
        self.history.clear()
        self._when.clear()

    def react(self, trigger: str) -> SphinxMode:
        """
        Map a trigger to a system mode.

        Accepted examples (case-insensitive):
          - "focus", "flow", "coding"       -> FOCUSED
          - "break", "idle", "away", "neg"  -> IDLE
          - "meeting", "call", "zoom"       -> IN_MEETING
          - "positive"/"negative"           -> FOCUSED / IDLE  (legacy support)
          - anything else                   -> CALM
        """
        t = (trigger or "").strip().lower()

        if t.startswith(("focus", "flow", "code", "coding", "positive")):
            new_state = SphinxMode.FOCUSED
        elif t.startswith(("meeting", "call", "zoom", "teams", "calendar")):
            new_state = SphinxMode.IN_MEETING
        elif t.startswith(("break", "idle", "away", "neg", "negative", "rest")):
            new_state = SphinxMode.IDLE
        else:
            new_state = SphinxMode.CALM

        self.state = new_state
        self.history.append(self.state)
        self._when.append(self._now())
        return self.state
