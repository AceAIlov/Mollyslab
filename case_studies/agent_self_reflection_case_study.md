# ケーススタディ: エージェント自己内省実験

**概要:**  
マーケットやセンサーのデータなしで、中立的なプロンプトに対しKuromiが自身の感情状態を内省し、「felt」レスポンスを生成できるかを検証しました。

---

## トリガー条件

- **プロンプト:** `「今どんな気持ち？」`  
- **前提:** 直前10分間に市場やIoTのシグナルなし

---

## 挙動

1. **初期状態**  
   - 外部トリガーがないため、Kuromiは`CALM`のまま  
2. **自己内省呼び出し**  
   - `/reflect?trigger=self_query` エンドポイントを呼び出し  
3. **内省出力**  
   - 強度（intensity）と「felt」文言を含むラショナルを生成

---

## ログサンプル

```json
{
  "timestamp": "2025-07-05T08:30:00Z",
  "trigger": "self_query",
  "from_state": "CALM",
  "to_state": "CALM",
  "intensity": 0.25,
  "reasoning": "Transitioned due to input 'self_query'.",
  "felt": "I returned to calm at 25% ease."
}
