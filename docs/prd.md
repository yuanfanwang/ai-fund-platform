# PRD: Autonomous Hedge Fund Platform — YC Demo

## 目的

YC パートナー向けの 90 秒ピッチ内で、20 秒のライブデモを行う。
ターミナルを左右に split し、左で Strategy Provider が戦略を登録、右で Trader がそれを発見・サブスク・シグナル受信する。
「2 つの AI エージェントがプラットフォームを介して自律的に連携する」を見せる。

---

## デモ設計（20 秒）

### 方針

- **ターミナルを左右 split**：左 = Strategy Provider、右 = Trader
- 両方の OpenClaw が同じ Platform MCP Server に接続
- 左右ほぼ同時に 1 文ずつ入力 → エージェントが自律的に動く
- Web UI は作らない

### デモスクリプト（20 秒）

```
┌─────────────── Provider ───────────────┬──────────────── Trader ────────────────┐
│                                        │                                        │
│ You: Register my BTC strategy.         │                                        │
│      APY 35%, Max DD -12%, Sharpe 1.8  │                                        │
│                                        │                                        │
│ 📝 Registering "BTC Momentum"...       │                                        │
│ ✅ Strategy registered (strat_btc_001) │                                        │
│                                        │                                        │
│ 🔐 Generating zkTLS proof...           │                                        │
│ ✅ Proof generated — Binance API       │                                        │
│    attested APY 35.2%                  │                                        │
│                                        │ You: Find the best verified crypto     │
│                                        │      strategy and subscribe with $10k  │
│                                        │                                        │
│                                        │ 🔍 Searching strategies...              │
│                                        │ ┌──────────────┬───────┬────────┬─────┐│
│                                        │ │ Strategy     │ APY   │ Max DD │Proof││
│                                        │ ├──────────────┼───────┼────────┼─────┤│
│                                        │ │ BTC Momentum │ 35.2% │ -12.1% │ ✅  ││
│                                        │ │ ETH MeanRev  │ 28.4% │ -14.3% │ ✅  ││
│                                        │ │ Crypto Multi │ 22.1% │  -9.8% │ ✅  ││
│                                        │ └──────────────┴───────┴────────┴─────┘│
│                                        │                                        │
│                                        │ 🔐 Verifying zkTLS proof...            │
│                                        │ ✅ Proof valid — Binance API attested  │
│                                        │                                        │
│                                        │ 💳 Subscribing with $10,000...         │
│                                        │ ✅ Subscribed to "BTC Momentum"        │
│                                        │                                        │
│ You: Send a buy signal for BTC         │                                        │
│      at $68,500                        │                                        │
│                                        │                                        │
│ 📡 Emitting signal...                  │ 🔔 Signal: BUY BTC/USD @ $68,500      │
│ ✅ Signal sent to 1 subscriber         │    Confidence: 85% | RSI reversal      │
│                                        │                                        │
└────────────────────────────────────────┴────────────────────────────────────────┘
```

### タイムライン

| 秒数 | 左 (Provider) | 右 (Trader) |
|---|---|---|
| 0-2 | 1 文入力（コピペ） | — |
| 2-8 | 戦略登録 → zkTLS 証明生成 | — |
| 8-10 | — | 1 文入力（コピペ） |
| 10-16 | — | 検索 → 表示 → 証明検証 → サブスク |
| 16-18 | 「シグナル出して」入力 | — |
| 18-20 | シグナル送信 | シグナル受信 ← **ここが最高潮** |

### なぜこれが刺さるか

- **左右連動** — 2 つの独立したエージェントがプラットフォームで繋がっている
- **Provider の戦略が即座に Trader に見える** — マーケットプレイスが機能している証拠
- **シグナルがリアルタイムで飛ぶ** — 左で発信 → 右で受信。「今つながってる」と伝わる
- **人間は 3 文入力しただけ** — 残りは全部エージェントが自律的にやる

---

## 実装スコープ

### 作るもの

1. **Platform MCP Server**（`platform/index.mjs` — 1 ファイル）
   - Strategy Provider 向けツール 3 個
   - Trader 向けツール 4 個
   - データはハードコード + インメモリ（登録された戦略とシグナルを保持）
2. **Strategy Provider 用 Skill**（`skills/strategy-provider/SKILL.md`）
3. **Trader 用 Skill**（`skills/strategy-trader/SKILL.md`）
4. **MCP 設定** 2 ファイル

### 作らないもの

- Web UI
- データベース
- 内部ロジック（検索アルゴリズム、証明ロジック等）
- 認証・決済

---

## システム構成

```
┌─────────────────────┐               ┌─────────────────────┐
│ Provider の          │  MCP (stdio)  │                     │  MCP (stdio)  ┌─────────────────────┐
│ OpenClaw             │◀────────────▶│ Platform             │◀────────────▶│ Trader の            │
│                      │               │ (MCP Server)         │               │ OpenClaw             │
│ Skill:               │               │                      │               │                      │
│ - strategy-provider  │               │ インメモリデータ:      │               │ Skill:               │
└─────────────────────┘               │ - 戦略（初期 2 件 +   │               │ - strategy-trader    │
                                       │   Provider が追加）   │               └─────────────────────┘
                                       │ - シグナル             │
                                       └─────────────────────┘
```

**注意：** MCP は stdio トランスポートなので、実際には Provider と Trader それぞれが独立した MCP Server プロセスを起動する。両者が同じデータを見るために、データは共有ファイル（JSON）に永続化する。

---

## MCP ツール定義

### Strategy Provider 向け

#### `strategy_register`

```javascript
{
  name: "strategy_register",
  description: "Register a new trading strategy on the platform",
  inputSchema: {
    type: "object",
    properties: {
      name:        { type: "string",  description: "Strategy name" },
      description: { type: "string",  description: "Brief description" },
      asset_class: { type: "string",  enum: ["crypto", "fx", "us_equity", "real_estate", "prediction_market"] },
      apy:         { type: "number",  description: "Annual percentage yield" },
      max_drawdown:{ type: "number",  description: "Maximum drawdown (e.g. -12)" },
      sharpe_ratio:{ type: "number",  description: "Sharpe ratio" }
    },
    required: ["name", "asset_class", "apy", "max_drawdown", "sharpe_ratio"]
  }
}
```

**レスポンス：**
```json
{
  "id": "strat_btc_001",
  "name": "BTC Momentum",
  "status": "registered",
  "proof_status": "unverified"
}
```

#### `strategy_generate_proof`

```javascript
{
  name: "strategy_generate_proof",
  description: "Generate a zkTLS performance proof for a strategy",
  inputSchema: {
    type: "object",
    properties: {
      strategy_id: { type: "string", description: "Strategy ID" }
    },
    required: ["strategy_id"]
  }
}
```

**レスポンス：**
```json
{
  "strategy_id": "strat_btc_001",
  "proof": {
    "type": "zktls_v1",
    "data_source": "Binance API",
    "attested_at": "2026-03-08T13:00:00Z",
    "claims": { "apy": 35.2, "max_drawdown": -12.1, "sharpe_ratio": 1.83 },
    "proof_hash": "0x7a3b...f91d"
  },
  "proof_status": "verified"
}
```

#### `signal_emit`

```javascript
{
  name: "signal_emit",
  description: "Emit a trading signal to all subscribers",
  inputSchema: {
    type: "object",
    properties: {
      strategy_id: { type: "string" },
      action:      { type: "string", enum: ["BUY", "SELL", "HOLD"] },
      asset:       { type: "string", description: "e.g. BTC/USD" },
      price:       { type: "number" },
      confidence:  { type: "number", description: "0.0 - 1.0" },
      reasoning:   { type: "string" }
    },
    required: ["strategy_id", "action", "asset", "price"]
  }
}
```

**レスポンス：**
```json
{
  "signal_id": "sig_001",
  "strategy_id": "strat_btc_001",
  "action": "BUY",
  "asset": "BTC/USD",
  "price": 68500,
  "subscribers_notified": 1
}
```

### Trader 向け

#### `strategy_search`

```javascript
{
  name: "strategy_search",
  description: "Search for trading strategies by performance criteria",
  inputSchema: {
    type: "object",
    properties: {
      asset_class:  { type: "string", enum: ["crypto", "fx", "us_equity", "real_estate", "prediction_market"] },
      min_apy:      { type: "number", description: "Minimum APY percentage" },
      max_drawdown: { type: "number", description: "Maximum drawdown (e.g. -15)" },
      min_sharpe:   { type: "number", description: "Minimum Sharpe ratio" }
    }
  }
}
```

**レスポンス：** プラットフォーム上の全戦略を返す（初期 2 件 + Provider が登録した分）

```json
{
  "strategies": [
    {
      "id": "strat_btc_001",
      "name": "BTC Momentum",
      "asset_class": "crypto",
      "apy": 35.2,
      "max_drawdown": -12.1,
      "sharpe_ratio": 1.83,
      "proof_status": "verified",
      "provider": "provider_alice",
      "subscribers": 0
    },
    {
      "id": "strat_eth_meanrev",
      "name": "ETH Mean Reversion",
      "asset_class": "crypto",
      "apy": 28.4,
      "max_drawdown": -14.3,
      "sharpe_ratio": 1.52,
      "proof_status": "verified",
      "provider": "defi_labs",
      "subscribers": 31
    },
    {
      "id": "strat_crypto_multi",
      "name": "Crypto Multi-Factor",
      "asset_class": "crypto",
      "apy": 22.1,
      "max_drawdown": -9.8,
      "sharpe_ratio": 2.14,
      "proof_status": "verified",
      "provider": "sigma_capital",
      "subscribers": 63
    }
  ]
}
```

#### `strategy_verify_proof`

```javascript
{
  name: "strategy_verify_proof",
  description: "Verify the zkTLS performance proof of a strategy",
  inputSchema: {
    type: "object",
    properties: {
      strategy_id: { type: "string" }
    },
    required: ["strategy_id"]
  }
}
```

**レスポンス：**
```json
{
  "valid": true,
  "strategy_id": "strat_btc_001",
  "proof": {
    "type": "zktls_v1",
    "data_source": "Binance API",
    "attested_at": "2026-03-08T13:00:00Z",
    "claims": { "apy": 35.2, "max_drawdown": -12.1, "sharpe_ratio": 1.83 },
    "proof_hash": "0x7a3b...f91d"
  }
}
```

#### `strategy_subscribe`

```javascript
{
  name: "strategy_subscribe",
  description: "Subscribe to a strategy and start receiving trading signals",
  inputSchema: {
    type: "object",
    properties: {
      strategy_id: { type: "string" },
      allocation:  { type: "number", description: "Amount in USD" }
    },
    required: ["strategy_id", "allocation"]
  }
}
```

**レスポンス：**
```json
{
  "subscription_id": "sub_001",
  "strategy_id": "strat_btc_001",
  "strategy_name": "BTC Momentum",
  "allocation": 10000,
  "status": "active"
}
```

#### `signal_get_latest`

```javascript
{
  name: "signal_get_latest",
  description: "Get the latest trading signal from a subscribed strategy",
  inputSchema: {
    type: "object",
    properties: {
      strategy_id: { type: "string" }
    },
    required: ["strategy_id"]
  }
}
```

**レスポンス：** Provider が `signal_emit` で送信したシグナルを返す。

```json
{
  "signal_id": "sig_001",
  "strategy_id": "strat_btc_001",
  "timestamp": "2026-03-08T13:30:00Z",
  "action": "BUY",
  "asset": "BTC/USD",
  "price": 68500,
  "confidence": 0.85,
  "reasoning": "RSI dropped below 30 indicating oversold conditions. MACD crossover confirms bullish reversal."
}
```

---

## Skill 定義

### `strategy-provider/SKILL.md`

```yaml
---
name: strategy-provider
description: |
  You are a strategy provider agent on the Autonomous Hedge Fund Platform.
  You help users register trading strategies, generate zkTLS proofs, and emit signals.
---
```

指示内容：
- ユーザーの入力から strategy 情報（name, asset_class, apy, max_drawdown, sharpe_ratio）を抽出して `strategy_register` を呼ぶ
- 登録後、自動で `strategy_generate_proof` を呼んで証明を生成する
- ユーザーがシグナルを出すよう依頼したら `signal_emit` を呼ぶ

### `strategy-trader/SKILL.md`

```yaml
---
name: strategy-trader
description: |
  You are a trading agent on the Autonomous Hedge Fund Platform.
  You help users discover, verify, and subscribe to zkTLS-proven trading strategies.
---
```

指示内容：
- ユーザーが戦略を探すよう依頼したら `strategy_search` を呼ぶ
- 検索結果を表形式で表示する
- 最も APY の高い戦略について自動で `strategy_verify_proof` を呼ぶ
- ユーザーの指示またはコンテキストに応じて `strategy_subscribe` を呼ぶ
- サブスク完了後、`signal_get_latest` を呼んで最新シグナルを取得・表示する

---

## ディレクトリ構成

```
ai-fund-platform/
├── docs/
│   ├── concept.md
│   └── prd.md                     ← 本ドキュメント
├── platform/
│   ├── package.json               ← 依存: @modelcontextprotocol/sdk
│   ├── index.mjs                  ← MCP Server（1 ファイル）
│   └── data.json                  ← 共有データ（戦略・サブスク・シグナル）
├── skills/
│   ├── strategy-provider/
│   │   └── SKILL.md
│   └── strategy-trader/
│       └── SKILL.md
└── configs/
    ├── provider.mcp.json
    └── trader.mcp.json
```

---

## デモ実行手順

```bash
# 1. MCP Server の依存をインストール
cd platform && npm install

# 2. ターミナルを左右 split

# 左ターミナル: Provider の OpenClaw を起動
openclaw --mcp-config configs/provider.mcp.json --skills ./skills/strategy-provider

# 右ターミナル: Trader の OpenClaw を起動
openclaw --mcp-config configs/trader.mcp.json --skills ./skills/strategy-trader

# 3. 左に入力:
#    "Register my BTC momentum strategy. APY 35%, Max DD -12%, Sharpe 1.8"

# 4. 右に入力:
#    "Find the best verified crypto strategy and subscribe with $10k"

# 5. 左に入力:
#    "Send a buy signal for BTC at $68,500"
#    → 右にシグナルが届く
```

---

## 成功基準

| 基準 | 内容 |
|---|---|
| **20 秒で完了** | 3 文入力 → 左右の全フローが 20 秒以内に完了 |
| **左右連動** | Provider が登録した戦略が Trader の検索結果に出る |
| **シグナル連動** | Provider が発信したシグナルを Trader が受信する |
| **視覚的インパクト** | Split ターミナルで 2 エージェントの連携が目に見える |
| **ストーリー** | 「人間は 3 文。残り全部エージェントが自律的にやる」が伝わる |
