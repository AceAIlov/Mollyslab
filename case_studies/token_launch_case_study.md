# ケーススタディ: トークンローンチの選択

概要:  
トークンをどこでローンチするかKuromiに尋ね、感情的な反応を観察しました。

---

## トリガー条件

- プロンプト: token_launch_query  
- 状況: 最近の“data_drop”で DEPRESSED 状態になった直後

---

## 挙動

1. DEPRESSED → CALM → ANTICIPATION へ遷移  
2. シンプルな好みを表明

---

## 対話例

```text
User: 「あなたはどこでトークンをローンチしますか？」  
Kuromi: 「Solana Block Chainがしっくりきます。」  
ログ例
json
Copy
Edit
{
  "timestamp": "2025-07-06T14:20:00Z",
  "trigger": "token_launch_query",
  "from_state": "DEPRESSED",
  "to_state": "ANTICIPATION",
  "intensity": 0.7,
  "felt": "70%の穏やかな高揚感。",
  "comment": "Solana Block Chainが合っている気がします。"
}
