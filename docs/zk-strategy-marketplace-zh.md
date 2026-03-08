# zkStrategy：面向 Agent 的零知识策略市场

## 一句话概括

> **在保密交易策略的同时，通过密码学证明其业绩真实性，AI Agent 可一键购买并自动执行的策略市场。**

---

## 要解决的问题

### 策略提供者（创建者）的困境

| 问题 | 现状 |
|---|---|
| **公开即死亡** | 优秀策略一旦公开，立即被复制，Alpha 消失 |
| **无法证明业绩** | 声称"年化 40%"，无人相信，截图可以伪造 |
| **无法变现** | 个人拥有优秀策略，但不加入基金就无法获得收益 |

### 投资者（使用者）的困境

| 问题 | 现状 |
|---|---|
| **缺乏信任** | 没有手段验证策略业绩的真实性 |
| **黑箱恐惧** | 对将资金交给黑箱系统感到不安 |
| **手动操作** | 找到策略后仍需自行实现和运维 |

### AI Agent 时代的问题

| 问题 | 现状 |
|---|---|
| **Agent 无法搜索策略** | 不存在可供 Agent 使用的"策略 API" |
| **支付壁垒** | Agent 无法自主购买或订阅策略 |
| **质量保障** | Agent 无法判断应该信任哪个策略 |

---

## 核心创意：基于 zkTLS 的"零知识策略证明"

### 什么是 zkTLS

利用**零知识证明**技术，使 TLS（HTTPS 通信）响应变得可验证。

```
常规流程：
  用户 → Binance API → "您的年化收益为 +42%"

zkTLS 流程：
  用户 → Binance API → "您的年化收益为 +42%"
       ↓
  基于此 TLS 响应生成 ZK 证明
       ↓
  可以在不透露策略内容的情况下证明
  "这是 Binance 返回的真实数据，收益确实为 +42%"
```

### 可以证明什么

| 证明对象 | 数据来源（TLS） | 证明内容 |
|---|---|---|
| 交易业绩 | 交易所 API（Binance、Coinbase 等） | "该策略过去 1 年收益为 +42%" |
| 夏普比率 | 交易所 API | "风险调整后收益率 ≥ 2.1" |
| 最大回撤 | 交易所 API | "最大回撤控制在 -15% 以内" |
| 交易频率 | 交易所 API | "月均交易 50 次以上（活跃）" |
| 社交声誉 | Twitter/X API | "该账号粉丝数超过 10k" |
| 身份验证 | 各类 API | "该用户真实存在并拥有此交易所账户" |

**关键：策略逻辑（买什么、何时买、为什么买）完全不公开。**

---

## 平台架构

```
┌─────────────────────────────────────────────────────────────┐
│                   zkStrategy Platform                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐          ┌──────────────────────┐        │
│  │ Strategy      │          │ Investor / Agent     │        │
│  │ Provider      │          │                      │        │
│  │              │          │  ・验证业绩证明        │        │
│  │ ・注册策略    │  zkTLS   │  ・订阅策略           │        │
│  │ ・证明业绩    │───证明──→│  ・接收信号           │        │
│  │ ・发送信号    │          │  ・自动执行交易        │        │
│  │ ・获取报酬    │←──支付───│                      │        │
│  └──────────────┘          └──────────────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────────┐        │
│  │              zkTLS Verification Layer            │        │
│  │                                                 │        │
│  │  交易所 API ──→ TLS 证明生成 ──→ 链上验证        │        │
│  │  Twitter API ──→ TLS 证明生成 ──→ 链上验证       │        │
│  │  任意 API ──→ TLS 证明生成 ──→ 链上验证          │        │
│  └─────────────────────────────────────────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────────┐        │
│  │              Agent Access Layer                  │        │
│  │                                                 │        │
│  │  OpenClaw Plugin ──→ 策略搜索 ──→ 订阅 ──→       │        │
│  │  信号接收 ──→ 自动执行                            │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent 集成（OpenClaw 插件）

### 用户体验

```
用户："找一个月收益 5% 以上、回撤 10% 以下的加密货币策略"

OpenClaw Agent：
  → 调用 zkStrategy API
  → 搜索经 zkTLS 证明的策略
  → 展示前 3 名（附业绩证明）

用户："订阅第 2 个策略"

OpenClaw Agent：
  → 执行支付（稳定币 / Stripe）
  → 开始订阅信号源
  → 此后自动接收信号 → 自动执行交易
```

### OpenClaw 插件设计

```typescript
// zkStrategy 插件
api.registerTool({
  name: "zk_strategy_search",
  description: "搜索经 zkTLS 业绩证明的策略",
  parameters: {
    min_return: { type: "number", description: "最低收益率 (%)" },
    max_drawdown: { type: "number", description: "最大回撤上限 (%)" },
    asset_class: { enum: ["crypto", "us_equity", "fx"] },
    min_sharpe: { type: "number" }
  }
})

api.registerTool({
  name: "zk_strategy_subscribe",
  description: "订阅策略并开始接收信号",
  parameters: {
    strategy_id: { type: "string" },
    allocation: { type: "number", description: "分配金额 (USD)" }
  }
})

api.registerTool({
  name: "zk_strategy_verify",
  description: "验证策略的 zkTLS 证明",
  parameters: {
    strategy_id: { type: "string" },
    proof_type: { enum: ["return", "sharpe", "drawdown", "identity"] }
  }
})

// 信号接收 → 自动执行（常驻 Service）
api.registerService({
  name: "zk_signal_listener",
  start: async () => {
    // 通过 WebSocket 订阅信号流
    // 接收信号 → 调用 broker_api 自动执行
    // 自动应用风控 Hook
  }
})
```

---

## 商业模式

```
Strategy Provider ──信号──→ Platform ──信号──→ Investor/Agent
                                │
                        手续费（业绩分成 or 月费）
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                Provider: 70% Platform: 20% Protocol: 10%
```

| 收入来源 | 模式 |
|---|---|
| 订阅制 | 月费 $XX 起订阅策略信号 |
| 业绩分成 | 利润的 X% 由提供者和平台分配 |
| 证明手续费 | 每次 zkTLS 证明生成收取少量费用 |
| API 访问 | 面向 Agent 的 API 调用计费 |

---

## 竞品对比

| 现有服务 | 问题 | zkStrategy 的优势 |
|---|---|---|
| QuantConnect / Numerai | 需要提交策略代码（无法保密） | **策略逻辑完全保密** |
| 跟单交易（eToro 等） | 业绩造假风险，策略完全可见 | **zkTLS 密码学证明业绩** |
| Hive5（GKTLS） | 通用型 zkTLS | **Agent 原生**，Agent 直接消费 |
| 信号提供商（Telegram） | 零信任，手动复制 | **证明 + 自动执行** |

**最大差异化："Agent First"**
- 不是人类在 UI 上点击操作，而是 **AI Agent 自主评估、购买、执行策略**
- 作为 OpenClaw 插件提供 → 触达现有 100k+ 用户基础

---

## 技术栈（预期）

| 层级 | 技术 |
|---|---|
| zkTLS 证明 | TLSNotary / Reclaim Protocol / Opacity Network |
| 链上验证 | Ethereum L2（Base / Arbitrum）+ 智能合约 |
| 支付 | 稳定币（USDC）+ Stripe（法币） |
| 信号分发 | WebSocket + Redis Pub/Sub |
| Agent 集成 | OpenClaw Plugin SDK |
| 后端 | TypeScript / Node.js |
| 策略执行 | 沙箱环境（Firecracker / Wasm） |

---

## 总结

```
传统方式：策略公开 → 被复制 → Alpha 消失
          声称业绩 → 无法证明 → 不被信任
          发现策略 → 手动实现 → 运维困难

zkStrategy：
          策略保密 → zkTLS 仅证明业绩 → 获得信任
          Agent 搜索 → 自动订阅 → 自动执行
          提供者获得报酬 → 可持续的生态系统
```

> **"让拥有优秀策略的个人，在保守秘密的同时获得收益，AI Agent 可自主访问这些策略的世界。"**
