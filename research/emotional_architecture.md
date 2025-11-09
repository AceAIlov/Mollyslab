# Azumi Emotional Architecture

Azumi models emotional cognition as a **3-layer computation stack**.

## 1. Sensory Layer (Perception)
- Converts input text into semantic tokens.
- Applies sentiment embeddings via contextual analysis.
- Output: affect vector `[valence, arousal, dominance]`.

## 2. Affective Layer (Emotion Core)
- Weighted random modulation using temperature scaling.
- Memory influence derived from the last five states.
- Output: discrete feeling label (e.g., *serenity*, *focus*).

## 3. Behavioral Layer (Expression)
- Renders response tone + verbal rhythm.
- Selects haiku / reflective phrasing template.
- Output: emotionally coherent text string.

```mermaid
flowchart LR
  Input[User Input] --> Sensory[Perception Layer]
  Sensory --> Affective[Affective Layer]
  Affective --> Behavioral[Behavioral Layer]
  Behavioral --> Output[Azumi Reply]
