class EmotionEngine:
    """
    Azumi's emotional core: detects user sentiment and updates internal mood.
    """
    def __init__(self):
        self.mood = "neutral"
        self.bias = 0.0  # empathy bias from -1 (cold) to +1 (warm)

    def analyze(self, text: str):
        lower = text.lower()
        if any(x in lower for x in ["sad", "tired", "lonely"]):
            self.mood, self.bias = "empathetic", 0.7
        elif any(x in lower for x in ["angry", "frustrated"]):
            self.mood, self.bias = "soothing", 0.5
        elif any(x in lower for x in ["love", "happy", "grateful"]):
            self.mood, self.bias = "warm", 1.0
        else:
            self.mood, self.bias = "neutral", 0.3
        return self.mood
