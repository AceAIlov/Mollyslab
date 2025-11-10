import random

class ResponseGenerator:
    TEMPLATES = {
        "empathetic": [
            "I hear you. That sounds difficult.",
            "I'm here with you through this.",
            "You’re not alone in that feeling."
        ],
        "soothing": [
            "Take a breath. It’s okay to slow down.",
            "Let’s find calm together.",
            "Your feelings are valid — we can steady them."
        ],
        "warm": [
            "That’s wonderful to hear.",
            "Your warmth is contagious.",
            "It’s moments like these that define you."
        ],
        "neutral": [
            "I’m listening.",
            "Go on, I’m following.",
            "Tell me more."
        ]
    }

    def generate(self, mood: str) -> str:
        return random.choice(self.TEMPLATES.get(mood, self.TEMPLATES["neutral"]))
