from azumi.core.emotion_engine import EmotionEngine

def test_emotion_detection():
    e = EmotionEngine()
    assert e.analyze("I feel sad") == "empathetic"
    assert e.analyze("I'm angry") == "soothing"
    assert e.analyze("I love today") == "warm"
