from fastapi import FastAPI
from pydantic import BaseModel
from azumi.core.emotion_engine import EmotionEngine
from azumi.core.memory import EmotionalMemory
from azumi.core.response import ResponseGenerator

app = FastAPI(title="Azumi Emotional AI")

engine = EmotionEngine()
memory = EmotionalMemory()
responder = ResponseGenerator()

class Input(BaseModel):
    user: str
    message: str

@app.post("/azumi")
def chat(input: Input):
    mood = engine.analyze(input.message)
    memory.record(input.user, input.message, mood)
    reply = responder.generate(mood)
    return {"reply": reply, "mood": mood, "memory_count": len(memory.entries)}
