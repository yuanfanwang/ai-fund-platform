# PRD: Autonomous Hedge Fund Platform — MVP Demo

## 目的

concept.md のコンセプトを動くデモとして実証する。
Strategy Provider が戦略を公開し、Trader が検索・サブスク・シグナル受信するフローを、2つの OpenClaw インスタンスと1つの Platform を通じて End-to-End で動かす。

---

## MVP スコープ

### やること

- Strategy Provider 用 OpenClaw から戦略を登録・シグナル発信
- Trader 用 OpenClaw から戦略を検索・サブスク・シグナル受信
- Platform が MCP Server として両者を仲介
- zkTLS 証明は **モック**（デモ用にダミー証明を生成・検証）
- 戦略の成績指標（APY, PnL, Max DD）の表示

### やらないこと（MVP 外）

- 実際の zkTLS 証明（TLSNotary / Reclaim Protocol 統合）
- オンチェーン検証・スマートコントラクト
- 実際の決済（USDC / Stripe）
- 実際の取引所接続・自動売買
- 本番レベルの認証・認可
- UI（全て OpenClaw の会話 UI で操作）

---

## システム構成

```
┌─────────────────────┐  MCP (stdio)  ┌─────────────────────┐
│ Strategy Provider の  │◀────────────▶│                     │
│ OpenClaw             │               │                     │
│                      │               │   Platform          │
│ Skills:              │               │   (MCP Server)      │
│ - strategy-provider  │               │                     │
└─────────────────────┘               │   - REST API        │
                                       │   - WebSocket       │
┌─────────────────────┐  MCP (stdio)  │   - SQLite DB       │
│ Trader の            │◀────────────▶│   - Mock zkTLS      │
│ OpenClaw             │               │                     │
│                      │               └─────────────────────┘
│ Skills:              │
│ - strategy-trader    │
└─────────────────────┘
```

---

## コンポーネント詳細

### 1. Platform（MCP Server）

プラットフォームのバックエンド。MCP Server として動作し、Strategy Provider と Trader 双方の OpenClaw に MCP ツールを提供する。

#### 技術スタック

| 項目 | 技術 |
|---|---|
| 言語 | TypeScript |
| MCP SDK | `@modelcontextprotocol/sdk` |
| トランスポート | stdio（ローカルデモ用） |
| DB | SQLite（`better-sqlite3`） |
| シグナル配信 | インプロセス EventEmitter（MVP） |

#### データモデル

```sql
-- 戦略
CREATE TABLE strategies (
  id            TEXT PRIMARY KEY,
  provider_id   TEXT NOT NULL,
  name          TEXT NOT NULL,
  description   TEXT,
  asset_class   TEXT NOT NULL,  -- crypto, fx, us_equity, real_estate, prediction_market
  apy           REAL,
  pnl           REAL,
  max_drawdown  REAL,
  sharpe_ratio  REAL,
  status        TEXT DEFAULT 'active',  -- active, paused, archived
  proof_status  TEXT DEFAULT 'unverified',  -- unverified, verified, expired
  proof_data    TEXT,  -- JSON: mock zkTLS proof
  created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

-- サブスクリプション
CREATE TABLE subscriptions (
  id            TEXT PRIMARY KEY,
  strategy_id   TEXT NOT NULL REFERENCES strategies(id),
  trader_id     TEXT NOT NULL,
  allocation    REAL NOT NULL,  -- USD
  status        TEXT DEFAULT 'active',  -- active, paused, cancelled
  created_at    TEXT DEFAULT CURRENT_TIMESTAMP
);

-- シグナル
CREATE TABLE signals (
  id            TEXT PRIMARY KEY,
  strategy_id   TEXT NOT NULL REFERENCES strategies(id),
  action        TEXT NOT NULL,  -- buy, sell, hold
  asset         TEXT NOT NULL,  -- e.g. BTC/USD, EUR/USD
  price         REAL,
  quantity      REAL,
  confidence    REAL,  -- 0.0 - 1.0
  reasoning     TEXT,
  created_at    TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### MCP ツール一覧

**Strategy Provider 向け**

| ツール名 | 説明 |
|---|---|
| `strategy_register` | 新しい戦略を登録する |
| `strategy_update` | 戦略の情報（成績指標等）を更新する |
| `strategy_generate_proof` | 成績の zkTLS 証明を生成する（MVP ではモック） |
| `signal_emit` | 売買シグナルを発信する |
| `strategy_my_list` | 自分が登録した戦略の一覧を取得する |
| `strategy_subscribers` | 自分の戦略のサブスクライバー一覧を取得する |

**Trader 向け**

| ツール名 | 説明 |
|---|---|
| `strategy_search` | 条件に合う戦略を検索する（APY, Max DD, asset_class 等） |
| `strategy_detail` | 戦略の詳細情報を取得する |
| `strategy_verify_proof` | 戦略の zkTLS 証明を検証する（MVP ではモック検証） |
| `strategy_subscribe` | 戦略をサブスクライブする |
| `strategy_unsubscribe` | サブスクリプションを解除する |
| `signal_history` | サブスク中の戦略のシグナル履歴を取得する |
| `signal_listen` | 新しいシグナルをリアルタイムで待ち受ける |

**共通**

| ツール名 | 説明 |
|---|---|
| `platform_status` | プラットフォームの稼働状況を取得する |
| `strategy_leaderboard` | 成績上位の戦略ランキングを取得する |

#### Mock zkTLS

MVP では zkTLS を以下のようにモックする：

```typescript
// 証明生成（Strategy Provider が呼ぶ）
function generateMockProof(strategyId: string, metrics: StrategyMetrics): Proof {
  return {
    id: crypto.randomUUID(),
    strategyId,
    type: "mock_zktls_v1",
    claims: {
      apy: metrics.apy,
      maxDrawdown: metrics.maxDrawdown,
      sharpeRatio: metrics.sharpeRatio,
      dataSource: "binance_api",     // 模擬
      attestedAt: new Date().toISOString(),
    },
    // 実際の zkTLS ではここに暗号学的証明が入る
    signature: crypto.randomBytes(64).toString("hex"),
    verified: true,
  };
}

// 証明検証（Trader が呼ぶ）
function verifyMockProof(proof: Proof): VerificationResult {
  return {
    valid: true,
    message: "Mock proof verified successfully",
    attestedSource: proof.claims.dataSource,
    attestedAt: proof.claims.attestedAt,
  };
}
```

---

### 2. Strategy Provider 用 OpenClaw

戦略提供者が使用する OpenClaw インスタンス。Platform の MCP Server に接続し、戦略の登録・シグナル発信を行う。

#### MCP 設定

```json
{
  "mcpServers": {
    "zkstrategy": {
      "command": "node",
      "args": ["./platform/dist/mcp-server.js"],
      "env": {
        "USER_ROLE": "provider",
        "USER_ID": "provider_alice"
      }
    }
  }
}
```

#### Skill: `strategy-provider`

```yaml
---
name: strategy-provider
description: |
  Manage your trading strategies on the Autonomous Hedge Fund Platform.
  Register strategies, generate performance proofs, and emit trading signals.
---
```

Skill の指示内容：
- 戦略登録時に asset_class, name, description, 成績指標を収集
- 登録後に自動で zkTLS 証明生成を提案
- シグナル発信時に action, asset, price, quantity, confidence, reasoning を収集
- サブスクライバー数や収益の確認

#### デモシナリオ（Strategy Provider）

```
Provider: 「BTC のモメンタム戦略を登録して。APY 35%、Max DD -12%、シャープ 1.8」

OpenClaw:
  → strategy_register を呼び出し
  → 「戦略 "BTC Momentum" を登録しました (ID: strat_xxx)」
  → 「zkTLS 証明を生成しますか？」

Provider: 「はい」

OpenClaw:
  → strategy_generate_proof を呼び出し
  → 「証明を生成しました。APY 35%, Max DD -12% が Binance データで確認済みです。」

Provider: 「BTC を $68,500 で買いシグナルを出して」

OpenClaw:
  → signal_emit を呼び出し
  → 「シグナルを発信しました。3 人のサブスクライバーに配信されます。」
```

---

### 3. Trader 用 OpenClaw

トレーダーが使用する OpenClaw インスタンス。Platform の MCP Server に接続し、戦略の検索・サブスク・シグナル受信を行う。

#### MCP 設定

```json
{
  "mcpServers": {
    "zkstrategy": {
      "command": "node",
      "args": ["./platform/dist/mcp-server.js"],
      "env": {
        "USER_ROLE": "trader",
        "USER_ID": "trader_bob"
      }
    }
  }
}
```

#### Skill: `strategy-trader`

```yaml
---
name: strategy-trader
description: |
  Discover, verify, and subscribe to trading strategies on the Autonomous Hedge Fund Platform.
  Search by performance metrics, verify zkTLS proofs, and receive trading signals.
---
```

Skill の指示内容：
- ユーザーの投資条件（APY, Max DD, asset_class 等）をヒアリング
- 検索結果を分かりやすく比較表示
- サブスク前に必ず zkTLS 証明の検証を提案
- シグナル受信時に内容を要約し、投資判断の参考情報を付加

#### デモシナリオ（Trader）

```
Trader: 「APY 20% 以上、DD 15% 以下の暗号通貨戦略を探して」

OpenClaw:
  → strategy_search を呼び出し
  → 検索結果を表示:
    1. BTC Momentum (APY: 35%, DD: -12%, Sharpe: 1.8) ✅ 証明済み
    2. ETH Mean Reversion (APY: 28%, DD: -14%, Sharpe: 1.5) ✅ 証明済み
    3. Crypto Multi-Factor (APY: 22%, DD: -10%, Sharpe: 2.1) ⏳ 未証明

Trader: 「1 番の証明を検証して」

OpenClaw:
  → strategy_verify_proof を呼び出し
  → 「✅ 証明は有効です。Binance API データに基づき APY 35%、Max DD -12% が確認されています。」

Trader: 「サブスクして。$10,000 で」

OpenClaw:
  → strategy_subscribe を呼び出し
  → 「BTC Momentum をサブスクしました。$10,000 を配分。シグナルの受信を開始します。」

--- （Strategy Provider がシグナルを発信した後） ---

OpenClaw:
  → signal_listen でシグナルを受信
  → 「🔔 新しいシグナル: BTC Momentum が BTC/USD を $68,500 で買い推奨
      (confidence: 0.85, 理由: RSI が 30 を下回り反転シグナル)」
```

---

## ディレクトリ構成

```
ai-fund-platform/
├── docs/
│   ├── concept.md
│   ├── prd.md                          ← 本ドキュメント
│   └── ...
├── platform/                            ← Platform (MCP Server)
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── mcp-server.ts              ← MCP Server エントリポイント
│   │   ├── tools/
│   │   │   ├── provider-tools.ts     ← Strategy Provider 向けツール定義
│   │   │   ├── trader-tools.ts       ← Trader 向けツール定義
│   │   │   └── common-tools.ts        ← 共通ツール定義
│   │   ├── db/
│   │   │   ├── schema.ts             ← SQLite スキーマ定義
│   │   │   └── index.ts              ← DB 初期化・クエリ
│   │   ├── proof/
│   │   │   └── mock-zktls.ts         ← Mock zkTLS 証明生成・検証
│   │   └── signals/
│   │       └── emitter.ts            ← シグナル配信ロジック
│   └── dist/                          ← ビルド成果物
├── skills/
│   ├── strategy-provider/             ← Strategy Provider 用 Skill
│   │   └── SKILL.md
│   └── strategy-trader/               ← Trader 用 Skill
│       └── SKILL.md
├── configs/
│   ├── provider.mcp.json             ← Strategy Provider の MCP 設定
│   └── trader.mcp.json               ← Trader の MCP 設定
└── demo/
    ├── seed-data.ts                   ← デモ用の初期データ投入
    └── README.md                      ← デモ実行手順
```

---

## デモ実行フロー

### 前提条件

- Node.js 20+
- OpenClaw がインストール済み（`npm install -g openclaw@latest`）

### セットアップ

```bash
# 1. Platform をビルド
cd platform && npm install && npm run build

# 2. デモ用データを投入
npx tsx demo/seed-data.ts

# 3. Strategy Provider の OpenClaw を起動（ターミナル A）
openclaw --mcp-config configs/provider.mcp.json --skills ./skills/strategy-provider

# 4. Trader の OpenClaw を起動（ターミナル B）
openclaw --mcp-config configs/trader.mcp.json --skills ./skills/strategy-trader
```

### デモストーリー

| ステップ | 誰が | 操作 | 使う MCP ツール |
|---|---|---|---|
| 1 | Provider | 「FX 戦略を登録して」 | `strategy_register` |
| 2 | Provider | 「証明を生成して」 | `strategy_generate_proof` |
| 3 | Trader | 「APY 20% 以上の戦略を探して」 | `strategy_search` |
| 4 | Trader | 「証明を検証して」 | `strategy_verify_proof` |
| 5 | Trader | 「サブスクして」 | `strategy_subscribe` |
| 6 | Provider | 「EUR/USD の買いシグナルを出して」 | `signal_emit` |
| 7 | Trader | （自動受信） | `signal_listen` |

---

## 成功基準

| 基準 | 内容 |
|---|---|
| **E2E フロー** | Provider → 戦略登録 → 証明生成 → シグナル発信 → Trader が受信、が一連で動く |
| **MCP 接続** | 2 つの OpenClaw インスタンスが同一 Platform の MCP Server に接続して動作する |
| **検索・フィルタ** | Trader が APY, Max DD, asset_class 等で戦略を検索できる |
| **Mock 証明** | 証明の生成・検証フローがデモとして成立する |
| **シグナル配信** | Provider のシグナルが Trader にリアルタイムで届く |

---

## 将来の拡張（MVP 後）

| フェーズ | 内容 |
|---|---|
| **Phase 2** | 実際の zkTLS 統合（TLSNotary / Reclaim Protocol） |
| **Phase 2** | オンチェーン証明検証（Base / Arbitrum） |
| **Phase 3** | USDC / Stripe による実決済 |
| **Phase 3** | 取引所 API 接続による自動売買 |
| **Phase 4** | マルチエージェント分析（RFS のエージェント群） |
| **Phase 4** | リスク管理 Hook |
