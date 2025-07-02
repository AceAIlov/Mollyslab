from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import json

from sentience_modules.emotion_engine import EmotionEngine
from sentience_modules.self_discovery import generate_new_emotion_tag
from sentience_modules.vision_processor import VisionProcessor
from sentience_modules.introspection import Introspection
from utils.feelings_loader import load_feelings, LOG_PATH

app = FastAPI(title="Kuromi Agent")

agent = EmotionEngine()
vision = VisionProcessor()
introspector = Introspection(agent)

@app.get("/status")
async def status():
    return {"state": agent.state.name}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    async for msg in ws.iter_text():
        if msg.startswith("IMAGE:"):
            raw = await ws.receive_bytes()
            label = vision.classify_image(raw)
            agent.react(label)
        else:
            agent.react(msg)
        new_tag = generate_new_emotion_tag()
        await ws.send_text(f"State: {agent.state.name}, NewEmotion: {new_tag}")

@app.get("/reflect")
async def reflect(trigger: str):
    agent.react(trigger)
    rationale = introspector.log_rationale(trigger)
    # persist to log
    LOG_PATH.parent.mkdir(exist_ok=True)
    logs = json.load(open(LOG_PATH, encoding="utf-8")) if LOG_PATH.exists() else []
    logs.append(rationale)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    return rationale

@app.get("/feelings")
async def feelings(limit: int = 5):
    entries = load_feelings(limit)
    if not entries:
        return JSONResponse(status_code=204, content=[])
    return entries
