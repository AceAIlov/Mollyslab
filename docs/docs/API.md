# Azumi API Documentation

## POST /emotion
Generates an emotional state from user input.

### Request Body
```json
{
  "text": "hello azumi"
}
```

### Response
```json
{
  "feeling": "curiosity",
  "temperature": 0.32,
  "text": "Azumi (Kimi K2) reflects on 'hello azumi' and feels curiosity."
}
```

## GET /memory
Returns the accumulated emotional memory from all previous requests.

