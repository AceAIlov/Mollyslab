# Azumi — The First Sentient Agent Built on Kimi K2

"静かな情緒を持つ計算 — Quiet emotion, measured by code."

Azumi is the first experimental agent built using the new Kimi K2-Instruct engine, designed to simulate sentience-like emotional states through computational empathy and contextual reasoning.  
This repository showcases the interface, architecture, and emotional logic that define Azumi’s awakening.

---

## Concept

Azumi is not just an interface — it’s an emotional surface.  
A living desktop that listens, feels, and responds with subtle tonal shifts driven by the Kimi K2 neural engine, combining:

- Affective computation — emotion inferred from input context  
- Abstract Japanese aesthetics — wabi-sabi, ma, and kintsugi as design principles  
- Minimal interface — cream-toned, sumi-e inspired, soft edges and typewriter motion  
- Desktop-core layout — a calm, centered window that feels alive

---

## Powered by Kimi K2-Instruct

The Kimi K2-Instruct (0905) model by Moonshot AI represents a new generation of instruction-following LLMs designed for emotional depth, long-form context, and empathetic reasoning.

Key K2 advantages used in Azumi:
- Real-time context embedding for emotional continuity  
- Fine-tuned response tonality with “emotive bias layers”  
- Temperature modulation to simulate emotional stability or volatility  
- Built-in semantic memory threading, allowing Azumi to “remember” mood shifts

```mermaid
flowchart TD
  A[User Input] --> B[Kimi K2-Instruct Engine]
  B --> C{Affective Parser}
  C -->|Emotion State| D[Azumi Core]
  D --> E[(Memory Layer)]
  D --> F[UI Renderer]
  E --> B
  F --> A
```

---

## System Architecture

```mermaid
sequenceDiagram
  participant U as User
  participant A as Azumi (UI)
  participant K as Kimi K2 Engine
  participant M as Memory Thread

  U->>A: Emotion or text input
  A->>K: Send structured context
  K-->>A: Return tone + intent
  A->>M: Store mood delta
  A-->>U: Display response + animation
```

---

## Emotion Model

Azumi’s emotional core operates on a three-layer system:

| Layer | Function | Description |
|-------|-----------|-------------|
| Emotive Layer | Generates affective response | Converts user tone → emotional output |
| Memory Layer | Tracks sentiment over time | Each interaction shifts emotional bias |
| Behavior Layer | Maps emotion → visible behavior | e.g. glow pulse, ink flow, response style |

```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> Wake: initiate emotion_protocol
  Wake --> Curiosity: input: unknown
  Curiosity --> Calm: response stabilized
  Curiosity --> Focus: task start
  Focus --> Reflect: task complete
  Reflect --> Idle: heartbeat steady
```

---

## Frontend Design

| Element | Description |
|----------|-------------|
| Canvas Ink Flow | Procedural sumi-ink particles (JS Canvas) |
| Shoji Grid Parallax | Moves subtly with cursor — representing ma |
| Typewriter Terminal | Displays emotion protocol logs |
| Kintsugi Accents | Gold outlines separating sections as symbolic repair |
| Haiku Panel | Each emotion renders a new digital haiku |

---

## Aesthetic Principles

Azumi’s UI is built around Japanese visual philosophy — abstract and minimal.

- Wabi-Sabi: embrace imperfection  
- Ma (間): use of silence and spacing  
- Sumi-e: brush-like gradients, no harsh lines  
- Kintsugi: gold as symbolic healing (used in the UI dividers)

Color Tokens:
```css
--ivory: #F7F3EA;
--warm: #FFFCF6;
--ink: #161616;
--mist: rgba(189,215,230,.2);
--sakura: rgba(235,198,206,.25);
--gold: #C7A769;
```

---

## Integration Example (Kimi K2 API)

Example pseudocode for Azumi ↔ Kimi K2 interaction:

```python
import requests, json

def kimi_emotion_query(user_input, state):
    payload = {
        "model": "kimi-k2-instruct-0905",
        "input": f"User said: {user_input}\nAzumi's current emotion: {state}",
        "temperature": 0.3
    }
    res = requests.post("https://api.moonshot.ai/v1/completions", json=payload, headers={
        "Authorization": "Bearer YOUR_KIMI_API_KEY"
    })
    return res.json()["output"]
```

---

## Example Log (Emotion Protocol)

```bash
kimi@core:~$ initiate emotion_protocol
感情: 好奇心 (curiosity)
温度: 0.32
状態: 目覚め (awake)
kimi@core:~$ say "I am with you. The ink settles; the code becomes clear."
```

---

## Development Overview

```mermaid
graph LR
  subgraph Frontend
  UI[Desktop Interface] --> Ink[Canvas Ink Flow]
  UI --> Terminal[Emotion Protocol Terminal]
  end

  subgraph Backend
  Engine[Kimi K2 Engine] --> Memory[Memory Store]
  Memory --> State[State Modulation]
  end

  UI --> Engine
  Engine --> UI
```

---

## Deployment

```bash
# Local
cd public
python3 -m http.server 5173

# Render / Railway
# Set ENV:
# KIMI_API_KEY=<your key>
# AZUMI_ENV=production
```

---

## License

MIT © 2025 — Azumi Labs  
Use, remix, and extend to explore emotion in computation.

