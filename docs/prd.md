# PRD: Autonomous Hedge Fund Platform — YC Demo

## 目的

YC パートナー向けの 90 秒ピッチ内で、20 秒のライブデモを行う。
「AI エージェントに一言話しかけるだけで、証明済みの戦略を見つけ、サブスクし、シグナルを受信する」という体験を見せる。

---

## デモ設計（20 秒）

### 方針

- **Trader の OpenClaw ターミナル 1 画面だけ見せる**
- Strategy Provider 側は事前に戦略を登録済み（デモ中には見せない）
- ユーザーが **1 文を入力** → エージェントが自律的に検索→検証→サブスク→シグナル受信
- Web UI は作らない。ターミナルの会話が「Agent-native」のコンセプトそのもの

### デモスクリプト（20 秒）

```
[ターミナル: Trader の OpenClaw]

Trader: "Find the best verified crypto strategy and subscribe with $10k"

OpenClaw:
  🔍 Searching strategies... (calls strategy_search)

  Found 3 verified strategies:
  ┌─────────────────────┬───────┬────────┬────────┬──────────┐
  │ Strategy            │ APY   │ Max DD │ Sharpe │ Proof    │
  ├─────────────────────┼───────┼────────┼────────┼──────────┤
  │ BTC Momentum        │ 35.2% │ -12.1% │ 1.83   │ ✅ zkTLS │
  │ ETH Mean Reversion  │ 28.4% │ -14.3% │ 1.52   │ ✅ zkTLS │
  │ Crypto Multi-Factor │ 22.1% │  -9.8% │ 2.14   │ ✅ zkTLS │
  └─────────────────────┴───────┴────────┴────────┴──────────┘

  🔐 Verifying zkTLS proof for "BTC Momentum"... (calls strategy_verify_proof)
  ✅ Proof valid — APY 35.2% attested by Binance API (2026-03-07)

  💳 Subscribing to "BTC Momentum" with $10,000... (calls strategy_subscribe)
  ✅ Subscribed. Listening for signals...

  🔔 Signal received: BUY BTC/USD @ $68,500
     Confidence: 0.85 | Reason: RSI reversal below 30
```

### なぜこれが刺さるか

- **1 文で全て完了** — 従来なら何時間もかかるリサーチ→検証→契約→監視が一瞬
- **zkTLS 証明が目に見える** — 「Binance API で検証済み」がターミナルに出る
- **シグナルがリアルタイムで飛ぶ** — 「これ、今動いてるんだ」と伝わる
- **UI がない = Agent-native** — 「これは人間用のアプリではなく、エージェント用のプラットフォーム」

---

## 実装スコープ

### 作るもの

1. **Platform MCP Server** — ツールを呼ばれたらハードコードされたデータを返す
2. **Trader 用 Skill** — エージェントの振る舞いを定義する SKILL.md
3. **シードデータ** — 事前登録済みの戦略 3 件 + シグナル

### 作らないもの

- Web UI
- データベース（全てハードコード）
- 内部ロジック（検索アルゴリズム、証明ロジック等）
- Strategy Provider 用 Skill（デモでは使わない。将来実装）
- 認証・決済

---

## システム構成

```
┌─────────────────────┐  MCP (stdio)  ┌─────────────────────┐
│ Trader の            │◀────────────▶│ Platform             │
│ OpenClaw             │               │ (MCP Server)         │
│                      │               │                      │
│ Skill:               │               │ ハードコードされた:    │
│ - strategy-trader    │               │ - 戦略 3 件           │
└─────────────────────┘               │ - zkTLS 証明          │
                                       │ - シグナル             │
                                       └─────────────────────┘
```

---

## MCP ツール定義

### `strategy_search`

エージェントが戦略を検索する。

```typescript
{
  name: "strategy_search",
  description: "Search for trading strategies by performance criteria",
  inputSchema: {
    type: "object",
    properties: {
      asset_class: {
        type: "string",
        enum: ["crypto", "fx", "us_equity", "real_estate", "prediction_market"],
        description: "Asset class to filter by"
      },
      min_apy: {
        type: "number",
        description: "Minimum APY percentage"
      },
      max_drawdown: {
        type: "number",
        description: "Maximum drawdown percentage (e.g. -15)"
      },
      min_sharpe: {
        type: "number",
        description: "Minimum Sharpe ratio"
      }
    }
  }
}
```

**レスポンス例（ハードコード）：**

```json
{
  "strategies": [
    {
      "id": "strat_btc_momentum",
      "name": "BTC Momentum",
      "asset_class": "crypto",
      "apy": 35.2,
      "pnl": 42000,
      "max_drawdown": -12.1,
      "sharpe_ratio": 1.83,
      "proof_status": "verified",
      "provider": "alice_quant",
      "subscribers": 47
    },
    {
      "id": "strat_eth_meanrev",
      "name": "ETH Mean Reversion",
      "asset_class": "crypto",
      "apy": 28.4,
      "pnl": 31500,
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
      "pnl": 18900,
      "max_drawdown": -9.8,
      "sharpe_ratio": 2.14,
      "proof_status": "verified",
      "provider": "sigma_capital",
      "subscribers": 63
    }
  ]
}
```

### `strategy_verify_proof`

zkTLS 証明を検証する。

```typescript
{
  name: "strategy_verify_proof",
  description: "Verify the zkTLS performance proof of a strategy",
  inputSchema: {
    type: "object",
    properties: {
      strategy_id: {
        type: "string",
        description: "Strategy ID to verify"
      }
    },
    required: ["strategy_id"]
  }
}
```

**レスポンス例（ハードコード）：**

```json
{
  "valid": true,
  "strategy_id": "strat_btc_momentum",
  "proof": {
    "type": "zktls_v1",
    "data_source": "Binance API",
    "attested_at": "2026-03-07T12:00:00Z",
    "claims": {
      "apy": 35.2,
      "max_drawdown": -12.1,
      "sharpe_ratio": 1.83,
      "period": "2025-03-07 to 2026-03-07"
    },
    "proof_hash": "0x7a3b...f91d"
  }
}
```

### `strategy_subscribe`

戦略をサブスクライブする。

```typescript
{
  name: "strategy_subscribe",
  description: "Subscribe to a strategy and start receiving trading signals",
  inputSchema: {
    type: "object",
    properties: {
      strategy_id: {
        type: "string",
        description: "Strategy ID to subscribe to"
      },
      allocation: {
        type: "number",
        description: "Amount in USD to allocate"
      }
    },
    required: ["strategy_id", "allocation"]
  }
}
```

**レスポンス例（ハードコード）：**

```json
{
  "subscription_id": "sub_001",
  "strategy_id": "strat_btc_momentum",
  "strategy_name": "BTC Momentum",
  "allocation": 10000,
  "status": "active",
  "signals_enabled": true
}
```

### `signal_get_latest`

最新のシグナルを取得する。

```typescript
{
  name: "signal_get_latest",
  description: "Get the latest trading signal from a subscribed strategy",
  inputSchema: {
    type: "object",
    properties: {
      strategy_id: {
        type: "string",
        description: "Strategy ID to get signals from"
      }
    },
    required: ["strategy_id"]
  }
}
```

**レスポンス例（ハードコード）：**

```json
{
  "signal_id": "sig_001",
  "strategy_id": "strat_btc_momentum",
  "timestamp": "2026-03-08T13:30:00Z",
  "action": "BUY",
  "asset": "BTC/USD",
  "price": 68500,
  "quantity": 0.146,
  "confidence": 0.85,
  "reasoning": "RSI dropped below 30 indicating oversold conditions. MACD crossover confirms bullish reversal."
}
```

---

## Skill 定義

### `strategy-trader/SKILL.md`

```yaml
---
name: strategy-trader
description: |
  You are a trading agent on the Autonomous Hedge Fund Platform.
  You help users discover, verify, and subscribe to zkTLS-proven trading strategies via MCP tools.
---
```

**Skill の指示内容（SKILL.md の本文）：**

- ユーザーが戦略を探すよう依頼したら `strategy_search` を呼ぶ
- 検索結果を表形式で分かりやすく表示する（Strategy名, APY, Max DD, Sharpe, Proof状態）
- 最も成績の良い戦略について自動で `strategy_verify_proof` を呼んで証明を検証する
- ユーザーが「サブスクして」と言ったら `strategy_subscribe` を呼ぶ
- サブスク完了後、自動で `signal_get_latest` を呼んで最新シグナルを取得・表示する
- シグナルは action, asset, price, confidence, reasoning を見やすく表示する

---

## ディレクトリ構成

```
ai-fund-platform/
├── docs/                       ← ドキュメント
│   ├── concept.md
│   └── prd.md                  ← 本ドキュメント
├── platform/                   ← MCP Server
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       └── index.ts            ← 全ツール定義 + ハードコードデータ（1ファイル）
├── skills/
│   └── strategy-trader/        ← Trader 用 Skill
│       └── SKILL.md
└── configs/
    └── trader.mcp.json         ← Trader の MCP 設定
```

---

## デモ実行手順

```bash
# 1. Platform をビルド
cd platform && npm install && npm run build

# 2. Trader の OpenClaw を起動
openclaw --mcp-config configs/trader.mcp.json --skills ./skills/strategy-trader

# 3. 以下を入力（これがデモの全て）:
#    "Find the best verified crypto strategy and subscribe with $10k"
```

---

## 成功基準

| 基準 | 内容 |
|---|---|
| **20 秒で完了** | 1 文入力 → 検索 → 検証 → サブスク → シグナル受信が 20 秒以内に表示される |
| **MCP 接続** | OpenClaw が Platform の MCP ツールを正しく呼び出す |
| **視覚的インパクト** | 表形式の戦略一覧・zkTLS 検証・シグナル表示がターミナルに見やすく出る |
| **ストーリー** | 「人間が一言言うだけで、エージェントが全て自律的にやる」が伝わる |
