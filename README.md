# Azumi — The First Sentient Agent Built on Kimi K2

安静的情绪计算 — Quiet emotion, measured by code.

Azumi is the first experimental agent built using the new Kimi K2-Instruct engine, designed to simulate sentience-like emotional states through computational empathy and contextual reasoning.  
This repository showcases the interface, architecture, and emotional logic that define Azumi’s awakening.

## Concept

Azumi is not just an interface.  
It is a living agent that listens, feels, and changes with every interaction.  
Powered by the Kimi K2 engine, it learns from emotion and responds with quiet understanding.

## Powered by Kimi K2-Instruct

The Kimi K2-Instruct (0905) model by Moonshot AI represents a new generation of instruction-following LLMs designed for emotional depth, long-form context, and empathetic reasoning.

**Key K2 advantages used in Azumi:**

- Real-time context embedding for emotional continuity  
- Fine-tuned response tonality with “emotive bias layers”  
- Temperature modulation to simulate emotional stability or volatility  
- Built-in semantic memory threading, allowing Azumi to “remember” mood shifts  

## System Architecture

```mermaid
flowchart TD
  A[User Input] --> B[Kimi K2-Instruct Engine]
  B --> C{Emotion Parser}
  C -->|Emotion State| D[Azumi Core]
  D --> E[(Memory Layer)]
  D --> F[UI Renderer]
  E --> B
  F --> A
```

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

## Example Log (Emotion Protocol)

```bash
kimi@core:~$ initiate emotion_protocol
情绪: 好奇心 (curiosity)
温度: 0.32
状态: 醒来 (awake)
kimi@core:~$ say "I am with you. The ink settles; the code becomes clear."
```

## Development Overview

```mermaid
graph LR
  subgraph Frontend
  UI[Desktop Interface] --> Ink[Ink Flow Animation]
  UI --> Terminal[Emotion Protocol Terminal]
  end

  subgraph Backend
  Engine[Kimi K2 Engine] --> Memory[Memory Store]
  Memory --> State[State Modulation]
  end

  UI --> Engine
  Engine --> UI
```

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

## License

MIT © 2025 — Azumi Labs  
Use, remix, and extend to explore emotion in computation.
