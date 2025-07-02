# File: tests/test_introspection.py

import pytest
from agent.emotion_engine import EmotionEngine
from agent.introspection import Introspection

@pytest.fixture
def engine():
    return EmotionEngine()

@pytest.fixture
def introspection(engine):
    return Introspection(engine)

def test_log_rationale(introspection):
    # initial
    state = introspection.engine.react("positive")
    rationale = introspection.log_rationale("positive")
    assert rationale["from_state"] is None
    assert rationale["to_state"] == state.name
    assert "positive" in rationale["trigger"]
