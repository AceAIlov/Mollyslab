from datetime import datetime

class EmotionalMemory:
    def __init__(self):
        self.entries = []

    def record(self, user: str, message: str, mood: str):
        self.entries.append({
            "timestamp": datetime.utcnow().isoformat(),
            "user": user,
            "message": message,
            "mood": mood
        })
        if len(self.entries) > 100:
            self.entries.pop(0)  # trim oldest
        return self.entries[-1]
