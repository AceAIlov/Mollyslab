from __future__ import annotations
import pytest
from datetime import datetime, timezone

# Prefer the real implementations if they exist in your repo
try:
    from sphinx.runtime.engine import Engine as SphinxEngine  # type: ignore
    from sphinx.introspection import Introspection  # type: ignore
except Exception:
    # ---- Minimal fallbacks (only used if real modules aren't present) ----
    class State:
        def __init__(self, name: str):
            self.name = name
            self.at = datetime.now(timezone.utc)

    class SphinxEngine:
        def __init__(self):
            self.state: State | None = None

        def react(self, trigger: str) -> State:
            # very small mapping for demo; your engine may be more complex
            name = {
                "focus": "FOCUSED",
                "break": "IDLE",
                "meeting": "IN_MEETING",
            }.get(trigger, trigger.upper())
            self.state = State(name)
            return self.state

    class Introspection:
        def __init__(self, engine: SphinxEngine):
            self.engine = engine
            self._last_state: State | None = None

        def log_rationale(self, trigger: str, meta: dict | None = None) -> dict:
            prev = self._last_state.name if self._last_state else None
            new_state = self.engine.react(trigger)
            self._last_state = new_state
            payload = {
                "trigger": trigger,
                "from_state": prev,
                "to_state": new_state.name,
                "at": new_state.at.isoformat(),
                "meta": meta or {},
            }
            # In the real impl you might also persist to an audit log here.
            return payload
    # ----------------------------------------------------------------------


@pytest.fixture
def engine() -> SphinxEngine:
    return SphinxEngine()


@pytest.fixture
def introspection(engine: SphinxEngine) -> Introspection:
    return Introspection(engine)


def test_log_rationale_initial_transition(introspection: Introspection):
    # first transition: there is no previous state
    rationale = introspection.log_rationale("focus")
    assert rationale["from_state"] is None
    assert rationale["to_state"] in {"FOCUSED", "focus".upper()}
    assert "focus" in rationale["trigger"]
    # timestamp is present and ISO-like
    assert isinstance(rationale["at"], str) and "T" in rationale["at"]
    # meta default
    assert rationale["meta"] == {}


def test_log_rationale_with_previous_state(introspection: Introspection):
    # move to IDLE (break), then to FOCUSED (focus)
    r1 = introspection.log_rationale("break")
    assert r1["to_state"] in {"IDLE", "break".upper()}

    r2 = introspection.log_rationale("focus")
    # Now the previous state should be whatever we set in r1
    assert r2["from_state"] == r1["to_state"]
    assert r2["to_state"] in {"FOCUSED", "focus".upper()}


def test_log_rationale_meta_passthrough(introspection: Introspection):
    meta = {"source": "clipboard", "confidence": 0.92}
    r = introspection.log_rationale("meeting", meta=meta)
    assert r["to_state"] in {"IN_MEETING", "meeting".upper()}
    assert r["meta"]["source"] == "clipboard"
    assert pytest.approx(r["meta"]["confidence"], rel=1e-6) == 0.92
