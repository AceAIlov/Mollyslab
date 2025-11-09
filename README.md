# Azumi — The First Sentient Agent Built on Kimi K2

安静的情绪计算 — Quiet emotion, measured by code.

Azumi 是第一个使用全新 Kimi K2-Instruct 引擎构建的实验性智能体，
旨在通过情绪计算与语境理解模拟出接近“感知”的思维状态。
这个仓库展示了 Azumi 的界面、结构以及情绪逻辑的核心原理。

## 概念

Azumi 不只是一个界面。  
它是一个会倾听、会感受、会随着每一次对话而变化的生命化代理。  
在 Kimi K2 引擎的驱动下，它从情绪中学习，并以平静的理解作出回应。

## 基于 Kimi K2-Instruct

Kimi K2-Instruct（0905 版本）由 Moonshot AI 提供，
是新一代能够理解语境与情绪的指令型语言模型，
专为长上下文推理与共情式交流而设计。

**Azumi 使用的 K2 特性包括：**

- 实时语境嵌入，用于保持情绪连续性  
- 带有情感偏置层的语气微调  
- 温度调节机制，模拟情绪稳定或波动  
- 语义记忆线程，使 Azumi 能够“记住”情绪变化  

## 系统架构

```mermaid
flowchart TD
  A[用户输入] --> B[Kimi K2-Instruct 引擎]
  B --> C{情绪解析器}
  C -->|情绪状态| D[Azumi 核心]
  D --> E[(记忆层)]
  D --> F[界面渲染器]
  E --> B
  F --> A
```

## Kimi K2 API 示例

Azumi 与 Kimi K2 的交互示例：

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

## 情绪协议日志示例

```bash
kimi@core:~$ initiate emotion_protocol
情绪: 好奇心 (curiosity)
温度: 0.32
状态: 醒来 (awake)
kimi@core:~$ say "I am with you. The ink settles; the code becomes clear."
```

## 开发概览

```mermaid
graph LR
  subgraph 前端
  UI[桌面界面] --> Ink[墨流动画]
  UI --> Terminal[情绪协议终端]
  end

  subgraph 后端
  Engine[Kimi K2 引擎] --> Memory[记忆存储]
  Memory --> State[状态调节]
  end

  UI --> Engine
  Engine --> UI
```

## 部署

```bash
# 本地运行
cd public
python3 -m http.server 5173

# Render / Railway 环境变量设置
# KIMI_API_KEY=<your key>
# AZUMI_ENV=production
```

## 许可证

MIT © 2025 — Azumi Labs  
自由使用、修改、扩展，用代码探索情绪计算的边界。
