introspection.py — Sphinx Introspection Module

This module generates human-readable rationale for state transitions coming
from the EmotionEngine (system modes). It explains why the engine moved
from the previous state to the new one, adds a UTC timestamp, and estimates
an intensity score in [0, 1]. It also returns a concise "felt" sentence.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Optional

# Prefer the Sphinx engine's Emotion alias (maps to SphinxMode: CALM/FOCUSED/IDLE/IN_MEETING)
try:
    from Sphinx.agent.emotion_engine import Emotion  # alias to SphinxMode
except Exception:
    # Fallback enum (used only if the real module is unavailable)
    from enum import Enum

    class Emotion(Enum):
        CALM = "CALM"
        FOCUSED = "FOCUSED"
        IDLE = "IDLE"
        IN_MEETING = "IN_MEETING"


class Introspection:
    def __init__(self, engine):
        """
        Args:
            engine: An object exposing:
              • .state -> current Emotion
              • .history -> sequence of Emotion states (most recent last)
        """
        self.engine = engine

    # ----------------------------- internals -----------------------------

    def _compute_intensity(
        self, from_state: Optional[Emotion], to_state: Emotion
    ) -> float:
        """
        Rough intensity model tuned for Sphinx modes.

        Heuristics:
          - same-state                   -> low (0.2)
          - CALM -> FOCUSED/IN_MEETING  -> high (0.85)
          - any  -> IN_MEETING          -> med-high (0.7)
          - FOCUSED <-> IDLE            -> medium (0.6)
          - otherwise                   -> moderate (0.5)

        A small random jitter simulates natural fluctuation.
        """
        if from_state == to_state:
            base = 0.20
        elif from_state is None:
            # First observation often feels moderate unless it's a big jump
            base = 0.50
            if to_state in (Emotion.FOCUSED, Emotion.IN_MEETING):
                base = 0.70 if to_state is Emotion.IN_MEETING else 0.85
        else:
            pair = {from_state, to_state}
            if from_state is Emotion.CALM and to_state in (Emotion.FOCUSED, Emotion.IN_MEETING):
                base = 0.85 if to_state is Emotion.FOCUSED else 0.70
            elif pair == {Emotion.FOCUSED, Emotion.IDLE}:
                base = 0.60
            elif to_state is Emotion.IN_MEETING:
                base = 0.70
            else:
                base = 0.50

        # Add bounded noise and clamp
        jitter = random.uniform(-0.10, 0.10)
        val = max(0.0, min(1.0, base + jitter))
        return round(val, 2)

    def _generate_felt(self, state: Emotion, intensity: float) -> str:
        """
        Return a short sentence describing how the state felt.
        """
        templates = {
            Emotion.FOCUSED: "Felt sharply focused at {:.0%} intensity.",
            Emotion.IDLE: "Energy dipped (idle) at {:.0%} intensity.",
            Emotion.IN_MEETING: "Attention shifted to collaboration at {:.0%} intensity.",
            Emotion.CALM: "Returned to calm at {:.0%} ease.",
        }
        # Fallback if an unknown state appears
        tmpl = templates.get(state, "State changed at {:.0%} intensity.")
        return tmpl.format(intensity)

    # ------------------------------ public -------------------------------

    def log_rationale(self, trigger: str) -> dict:
        """
        Produce a rationale for the latest transition.

        Notes:
          • This function does not mutate engine state.
          • It expects the engine to have already reacted and appended to history.
        """
        # Resolve current / previous from the engine's history if available.
        prev_state = None
        curr_state = getattr(self.engine, "state", None)

        hist = getattr(self.engine, "history", None)
        if hist:
            try:
                # history may be a deque or list of Emotion
                if len(hist) >= 1:
                    curr_state = hist[-1]
                if len(hist) >= 2:
                    prev_state = hist[-2]
            except Exception:
                # fall back to .state
                pass

        if curr_state is None:
            curr_state = Emotion.CALM  # safe default

        intensity = self._compute_intensity(prev_state, curr_state)
        felt = self._generate_felt(curr_state, intensity)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trigger": trigger,
            "from_state": prev_state.name if prev_state else None,
            "to_state": curr_state.name,
            "intensity": intensity,
            "reasoning": f"Transitioned due to input '{trigger}'.",
            "felt": felt,
        }
