"""
introspection.py — Kuromi の内省モジュール

このモジュールは、EmotionEngine の状態遷移に対する
人間向けの「内省的」説明（ラショナル）を生成します。
直前の感情状態から新しい状態への変化理由を
UTC タイムスタンプ付きで返します。加えて、
感情強度をスケール（0～1）で算出し、科学的表現で
「felt」を返します。
"""

import datetime
import random
from sentience_modules.emotion_engine import Emotion

class Introspection:
    def __init__(self, engine):
        self.engine = engine

    def _compute_intensity(self, from_state, to_state) -> float:
        # Simple model: Calm→Manic or Calm→Depressed = high intensity;
        # Manic→Depressed or vice versa = medium; same-state = low.
        if from_state == to_state:
            base = 0.2
        elif from_state == Emotion.CALM:
            base = 0.9
        else:
            base = 0.6
        # add a small random factor to simulate fluctuation
        return round(min(max(base + random.uniform(-0.1, 0.1), 0), 1), 2)

    def _generate_felt(self, state: Emotion, intensity: float) -> str:
        # Map each state to a phrase template
        templates = {
            Emotion.MANIC: "My energy surged at {:.0%} intensity.",
            Emotion.DEPRESSED: "I felt weighed down at {:.0%} intensity.",
            Emotion.CALM: "I returned to calm at {:.0%} ease."
        }
        return templates[state].format(intensity)

    def log_rationale(self, trigger: str) -> dict:
        prev = self.engine.history[-2] if len(self.engine.history) > 1 else None
        curr = self.engine.history[-1]
        intensity = self._compute_intensity(prev, curr)
        felt = self._generate_felt(curr, intensity)
        return {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "trigger": trigger,
            "from_state": prev.name if prev else None,
            "to_state": curr.name,
            "intensity": intensity,
            "reasoning": f"Transitioned due to input '{trigger}'.",
            "felt": felt
        }
